"""The toy world of the technical ReLF video: a small language, the paper's embedding recipe run on it,
and the exact denoiser, so every number on screen is computed with the paper's own formulas.

Paper: Rectified Language Flow (Su, Liao, Chen, Liu), arXiv 2610.33811. Convention: t = 0 noise, t = 1 data.
"""
from __future__ import annotations

import pickle
from types import SimpleNamespace

import numpy as np

SENTENCES = [
    "the cat sat on the mat", "the cat slept on the rug", "a cat ran to the door", "the cat sat by the door",
    "the dog sat on the rug", "a dog ran to the park", "a dog slept by the door", "the dog ran to the door",
    "a bird sang in the tree", "the bird sat in the tree", "a bird sang by the door", "the bird slept in the tree",
]
D = 2
EPS_SMOOTH = 0.02      # the data distribution is (1 - eps) * sentences + eps * unigram product, so kappa is finite


def hellinger_svd(sents, d=D, tau=1.0):
    """The paper's embedding recipe (Sec. 3.2, App. A.4) on a toy corpus.

    1. For each token a, count the tokens right before and right after it: a context distribution Q_a over 2V contexts.
    2. Smooth Q_a toward the overall context frequency (strength tau).
    3. H = sqrt(Q): rows are unit vectors and |H_a - H_b|^2 = 2 * Hellinger^2(Q_a, Q_b)   (Eq. 7).
    4. Frequency-weighted centering, then keep the top d right singular vectors.
    5. Rescale so that sum_w pi(w) E(w) = 0 and sum_w pi(w) |E(w)|^2 = d.
    """
    toks = [["<s>"] + s.split() + ["</s>"] for s in sents]
    vocab = sorted({w for s in sents for w in s.split()})
    V = len(vocab)
    ctx = ["<s>"] + vocab + ["</s>"]
    C = len(ctx)
    counts = np.zeros((V, 2 * C))
    uni = np.zeros(V)
    for s in toks:
        for i in range(1, len(s) - 1):
            a = vocab.index(s[i])
            uni[a] += 1
            counts[a, ctx.index(s[i - 1])] += 1
            counts[a, C + ctx.index(s[i + 1])] += 1
    pi = uni / uni.sum()
    Qraw = counts / counts.sum(1, keepdims=True)
    back = counts.sum(0) / counts.sum()
    Q = (counts + tau * back[None]) / (counts.sum(1, keepdims=True) + tau)
    H = np.sqrt(Q)
    Hbar = (pi[:, None] * H).sum(0)
    A = np.sqrt(pi)[:, None] * (H - Hbar)
    _U, S, Vt = np.linalg.svd(A, full_matrices=False)
    E = (H - Hbar) @ Vt[:d].T
    E = E - (pi[:, None] * E).sum(0)
    E = E * np.sqrt(d / (pi * (E ** 2).sum(1)).sum())
    return SimpleNamespace(vocab=vocab, pi=pi, counts=counts, Qraw=Qraw, Q=Q, H=H, S=S, E=E, ctx=ctx)


class Lang:
    """Exact posteriors for the toy language with Gaussian noise (the perfect bidirectional network)."""

    def __init__(self, sents, emb, eps=EPS_SMOOTH):
        self.vocab, self.pi, self.E = emb.vocab, emb.pi, emb.E
        self.V, self.d = len(self.vocab), self.E.shape[1]
        self.sent = [s.split() for s in sents]
        self.L = len(self.sent[0])
        self.idx = np.array([[self.vocab.index(w) for w in s] for s in self.sent])
        self.X = self.E[self.idx]                      # (S, L, d)
        self.eps = eps
        self.logpi = np.log(self.pi)

    # ---- one position, reference (unigram) posterior: the singular logits, Eq. (6)
    def singular_logits(self, Z, t):
        """log r1(w) - |z - t E(w)|^2 / (2 (1 - t)^2) for each position: (L, V), unnormalised."""
        d2 = ((Z[:, None, :] - t * self.E[None]) ** 2).sum(-1)
        return self.logpi[None] - d2 / (2 * max(1 - t, 1e-9) ** 2)

    def ref_logpost(self, Z, t):
        lg = self.singular_logits(Z, t)
        return lg - np.logaddexp.reduce(lg, 1, keepdims=True)

    # ---- the true per-position log posterior log q_t(w | Z) under the smoothed data distribution
    def true_logpost(self, Z, t):
        b = max(1 - t, 1e-9)
        ll = -((Z[:, None, :] - t * self.E[None]) ** 2).sum(-1) / (2 * b * b)          # (L, V) log likelihood per token
        # component 1: the sentences
        ls = ll[np.arange(self.L)[None], self.idx].sum(1) - np.log(len(self.sent))       # (S,)
        # component 2: unigram product (factorised): log prod_l sum_u pi(u) L(z_l | u)
        lu_pos = np.logaddexp.reduce(self.logpi[None] + ll, 1)                           # (L,)
        l1 = np.log(1 - self.eps) + np.logaddexp.reduce(ls)
        l2 = np.log(self.eps) + lu_pos.sum()
        lz = np.logaddexp(l1, l2)
        out = np.full((self.L, self.V), -np.inf)
        # sentences contribute to their own token at each position
        for s in range(len(self.sent)):
            for l in range(self.L):
                out[l, self.idx[s, l]] = np.logaddexp(out[l, self.idx[s, l]], np.log(1 - self.eps) + ls[s])
        # unigram product: token w at position l, the other positions marginalised
        other = lu_pos.sum() - lu_pos                                                    # (L,)
        out = np.logaddexp(out, np.log(self.eps) + self.logpi[None] + ll + other[:, None])
        return out - lz

    def probs(self, Z, t):
        return np.exp(self.true_logpost(Z, t))

    def kappa(self):
        """Smallest kappa with 1/kappa <= q1(w)/r1(w) <= kappa over all sequences (Theorem 3.1's assumption)."""
        r_sent = np.exp(self.logpi[self.idx].sum(1))
        hi = ((1 - self.eps) / len(self.sent) + self.eps * r_sent) / r_sent
        return float(max(hi.max(), 1 / self.eps))

    # ---- samplers
    def euler(self, Z0, ts, logit_cap=None, use_singular=True, sigma=0.0, rng=None):
        """Eq. (4) (and Eq. (18) when sigma > 0). ts: grid of N evaluation times, last one < 1.

        logit_cap: a 'bounded network'. With use_singular=True the cap applies to the residual f only
        (the paper's parameterisation, Eq. 5); with False it applies to the whole log posterior.
        Returns states (N, L, d), probs (N, L, V), guesses (N, L, d).
        """
        Z = np.array(Z0, float)
        states, probs, guesses = [], [], []
        for i, t in enumerate(ts):
            lq = self.true_logpost(Z, t)
            if logit_cap is not None:
                if use_singular:
                    lr = self.ref_logpost(Z, t)
                    f = np.clip(lq - lr, -logit_cap, logit_cap)
                    lg = lr + f
                else:
                    lg = np.clip(lq - lq.max(1, keepdims=True), -logit_cap, 0.0)
                lq = lg - np.logaddexp.reduce(lg, 1, keepdims=True)
            P = np.exp(lq)
            G = P @ self.E
            states.append(Z.copy()), probs.append(P), guesses.append(G)
            if i + 1 < len(ts):
                h, b = ts[i + 1] - t, 1 - t
                if sigma > 0:
                    eps_hat = (Z - t * G) / b
                    delta = min(sigma * h * b, b)
                    Z = Z - delta * eps_hat + np.sqrt(b * b - (b - delta) ** 2) * rng.normal(size=Z.shape)
                Z = Z + (h / b) * (G - Z)
        return np.stack(states), np.stack(probs), np.stack(guesses)


# the four-token teaching vocabulary for one-position pictures (illustrative positions, normalised like the paper's)
T4 = ["the", "sat", "cat", "dog"]
T4_PI = np.array([0.4, 0.2, 0.2, 0.2])
_raw = np.array([[-1.5, 0.2], [0.1, -1.6], [1.1, 0.9], [1.4, 0.2]])
_c = _raw - (T4_PI[:, None] * _raw).sum(0)
T4_E = _c * np.sqrt(2 / (T4_PI * (_c ** 2).sum(1)).sum())


def post4(z, t):
    """One-position posterior over the four teaching tokens (Eq. 6 with the prior T4_PI)."""
    z = np.atleast_2d(z)
    lg = np.log(T4_PI)[None] - ((z[:, None] - t * T4_E[None]) ** 2).sum(-1) / (2 * max(1 - t, 1e-9) ** 2)
    lg -= lg.max(1, keepdims=True)
    p = np.exp(lg)
    return p / p.sum(1, keepdims=True)


def build():
    emb = hellinger_svd(SENTENCES)
    lang = Lang(SENTENCES, emb)
    W = SimpleNamespace(emb=emb, lang=lang, sentences=SENTENCES, T4=T4, T4_PI=T4_PI, T4_E=T4_E)
    rng = np.random.default_rng(0)
    # demo run for the sampling scene: 16 evaluations; pick a start whose positions commit at different times
    ts16 = np.linspace(0, 1, 17)[:-1]
    best = None
    for k in range(60):
        Z0 = rng.normal(size=(lang.L, lang.d))
        S_, P_, G_ = lang.euler(Z0, ts16)
        sent = " ".join(lang.vocab[v] for v in P_[-1].argmax(1))
        first = (P_.max(-1) > 0.9).argmax(0)
        score = first.std() if sent in SENTENCES else -1
        if best is None or score > best[0]:
            best = (score, Z0, S_, P_, G_, sent)
    _, W.demo_Z0, W.demo_S, W.demo_P, W.demo_G, W.demo_sent = best
    W.ts16 = ts16
    # fine trajectory for the gap / residual plots
    tf = np.concatenate([np.linspace(0, 0.9, 46), np.linspace(0.91, 0.995, 40)])
    stats = dict(t=tf, gap=[], fmax=[])
    runs = [lang.euler(rng.normal(size=(lang.L, lang.d)), tf)[0] for _ in range(30)]
    for i, t in enumerate(tf):
        g, f = [], []
        for S_ in runs:
            sg = np.sort(lang.singular_logits(S_[i], t), 1)
            g.append((sg[:, -1] - sg[:, -2]).mean())
            f.append(np.abs(lang.true_logpost(S_[i], t) - lang.ref_logpost(S_[i], t)).max())
        stats["gap"].append(np.mean(g)), stats["fmax"].append(np.max(f))
    stats["gap"], stats["fmax"] = np.array(stats["gap"]), np.array(stats["fmax"])
    W.stats, W.kappa, W.bound = stats, lang.kappa(), 2 * np.log(lang.kappa())
    # bounded-network experiment: 64 evaluations up to t = 0.999, then read where the state would land
    ts64 = 1 - (1 - np.linspace(0, 1, 65)[:-1]) ** 1.0
    ts64 = np.concatenate([ts64, [0.999]])
    cap = dict()
    for name, kw in [("exact", {}), ("capped", dict(logit_cap=6, use_singular=False)), ("split", dict(logit_cap=6, use_singular=True))]:
        r = np.random.default_rng(1)
        miss, ptop, ex = [], [], None
        for k in range(200):
            Z0 = r.normal(size=(lang.L, lang.d))
            S_, P_, G_ = lang.euler(Z0, ts64, **kw)
            end = G_[-1]                                   # the last full step lands exactly on the last guess
            tok = lang.E[P_[-1].argmax(1)]
            miss.append(np.linalg.norm(end - tok, axis=1).mean())
            ptop.append(P_[-1].max(1).mean())
            if k == 0:
                ex = (S_, P_, G_)
        cap[name] = dict(miss=float(np.mean(miss)), ptop=float(np.mean(ptop)), ex=ex)
    W.cap, W.ts64 = cap, ts64
    return W


def load(rebuild=False):
    from unglazed.paths import build_dir
    f = build_dir() / "world.pkl"
    if f.exists() and not rebuild:
        return pickle.loads(f.read_bytes())
    W = build()
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_bytes(pickle.dumps(W))
    return W


if __name__ == "__main__":
    import world as _world      # so the pickle refers to world.Lang, not __main__.Lang
    W = _world.load(rebuild=True)
    e, lang = W.emb, W.lang
    np.set_printoptions(precision=2, suppress=True)
    print("E4", W.T4_E.round(2).tolist(), "check", (W.T4_PI[:, None] * W.T4_E).sum(0).round(3), (W.T4_PI * (W.T4_E ** 2).sum(1)).sum().round(3))
    print("demo sentence:", W.demo_sent)
    for k in range(0, 16, 3):
        print(k, " ".join(f"{lang.vocab[i]}:{p:.2f}" for i, p in zip(W.demo_P[k].argmax(1), W.demo_P[k].max(1))))
    st = W.stats
    for i in [0, 15, 25, 35, 45, 60, 75, 85]:
        print(f"t={st['t'][i]:.3f} gap={st['gap'][i]:8.1f} max|f*|={st['fmax'][i]:5.1f}")
    print("kappa %.3g bound %.1f max residual over all %.1f" % (W.kappa, W.bound, st["fmax"].max()))
    for k, v in W.cap.items():
        print(f"{k:7s} miss {v['miss']:.4f}  top prob {v['ptop']:.4f}")
