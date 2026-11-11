"""Exact flow-matching math for small worlds (numpy only).

Everything a scene shows should come from a real computation, not a drawing.
For a finite data set X (N points) and Gaussian noise, flow matching has a
closed form, so no network has to be trained to show the true behaviour:

    x_t = t * x1 + (1 - t) * s * eps                  (t = 0 noise, t = 1 data)
    q_t(i | z) = softmax_i( log pi_i - |z - t X_i|^2 / (2 s^2 (1 - t)^2) )
    guess(z, t) = sum_i q_t(i | z) X_i                (the denoiser, E[x1 | x_t = z])
    v(z, t) = (guess - z) / (1 - t)                   (the marginal velocity)

`s` is the noise scale (1 by default).
"""
from __future__ import annotations

import numpy as np


def posterior(z, t, X, logpi=None, s=1.0):
    """q_t(i | z) for each row of z. z: (M, d), X: (N, d) -> (M, N)."""
    z = np.atleast_2d(z)
    d2 = ((z[:, None, :] - t * X[None, :, :]) ** 2).sum(-1)
    lg = -d2 / (2 * (s * max(1 - t, 1e-6)) ** 2)
    if logpi is not None:
        lg = lg + logpi[None, :]
    lg -= lg.max(1, keepdims=True)
    p = np.exp(lg)
    return p / p.sum(1, keepdims=True)


def guess(z, t, X, logpi=None, s=1.0):
    return posterior(z, t, X, logpi, s) @ X


def velocity(z, t, X, logpi=None, s=1.0):
    return (guess(z, t, X, logpi, s) - np.atleast_2d(z)) / max(1 - t, 1e-6)


def integrate(z0, X, steps=200, logpi=None, s=1.0, t0=0.0, t1=1.0, return_guess=False):
    """Euler steps in the 'move a fraction toward the guess' form.

    Returns ts (steps+1,), traj (steps+1, M, d) and, if asked, the guess at each step.
    The last step to t1 = 1 lands exactly on the guess.
    """
    ts = np.linspace(t0, t1, steps + 1)
    z = np.array(z0, dtype=float)
    traj, gs = [z.copy()], []
    for k in range(steps):
        t, h = ts[k], ts[k + 1] - ts[k]
        g = guess(z, t, X, logpi, s)
        gs.append(g)
        z = z + (h / max(1 - t, 1e-9)) * (g - z)
        traj.append(z.copy())
    gs.append(guess(z, min(t1, 1 - 1e-6), X, logpi, s))
    out = (ts, np.stack(traj))
    return out + (np.stack(gs),) if return_guess else out


def density(grid_xy, t, X, logpi=None, s=1.0):
    """Marginal density p_t on grid points (G, d): a mixture of Gaussians at t X_i."""
    d = X.shape[1]
    sd = s * max(1 - t, 1e-3)
    d2 = ((grid_xy[:, None, :] - t * X[None, :, :]) ** 2).sum(-1)
    w = np.full(len(X), 1 / len(X)) if logpi is None else np.exp(logpi - np.logaddexp.reduce(logpi))
    return (np.exp(-d2 / (2 * sd * sd)) * w[None, :]).sum(1) / ((2 * np.pi) ** (d / 2) * sd ** d)


# ---------------------------------------------------------------- reflow (kernel version)
class PairFlow:
    """Flow matching on a fixed list of pairs (z0_i, z1_i), e.g. the pairs made by a first flow.

    v(z, t) = E[z1 - z0 | t z1 + (1 - t) z0 = z], estimated with a small Gaussian kernel
    of width `bw` around each pair's point on its line.
    """

    def __init__(self, z0, z1, bw=0.12):
        self.z0, self.z1, self.bw = np.asarray(z0, float), np.asarray(z1, float), bw

    def velocity(self, z, t):
        z = np.atleast_2d(z)
        xt = t * self.z1 + (1 - t) * self.z0
        d2 = ((z[:, None, :] - xt[None, :, :]) ** 2).sum(-1)
        lg = -d2 / (2 * self.bw ** 2)
        lg -= lg.max(1, keepdims=True)
        w = np.exp(lg)
        w /= w.sum(1, keepdims=True)
        return w @ (self.z1 - self.z0)

    def integrate(self, z0, steps=200):
        ts = np.linspace(0, 1, steps + 1)
        z = np.array(z0, float)
        traj = [z.copy()]
        for k in range(steps):
            z = z + (ts[k + 1] - ts[k]) * self.velocity(z, ts[k])
            traj.append(z.copy())
        return ts, np.stack(traj)


# ---------------------------------------------------------------- toy worlds
def islands(rng, centers, n_each=40, spread=0.18, shapes=None):
    """Data that lives on a few small islands. shapes: per-island 2x2 stretch matrices."""
    pts = []
    for k, c in enumerate(centers):
        p = rng.normal(size=(n_each, 2)) * spread
        if shapes is not None:
            p = p @ np.asarray(shapes[k]).T
        pts.append(p + np.asarray(c))
    return np.concatenate(pts)


def straightness(ts, traj):
    """Mean squared gap between each path's velocity and its total displacement (0 = straight)."""
    disp = traj[-1] - traj[0]
    v = np.diff(traj, axis=0) / np.diff(ts)[:, None, None]
    return float(((v - disp[None]) ** 2).sum(-1).mean())


# ---------------------------------------------------------------- toy language
class ToyLanguage:
    """A tiny corpus with word embeddings; the exact 'denoiser' over whole sentences.

    The posterior over sentences given a whole noisy row Z (L, d) at time t is
        q(s | Z) ∝ pi_s * prod_i N(Z_i ; t E(s_i), (1 - t)^2)
    and the per-position word probabilities are its marginals. This is what a perfect
    bidirectional network would output, so the sampler here is the real ReLF loop in a
    world small enough to compute exactly.
    """

    def __init__(self, sentences, emb: dict, s=1.0):
        self.sent = [x.split() for x in sentences]
        self.L = len(self.sent[0])
        assert all(len(x) == self.L for x in self.sent)
        self.vocab = list(emb.keys())
        self.E = np.array([emb[w] for w in self.vocab], float)
        self.idx = np.array([[self.vocab.index(w) for w in x] for x in self.sent])  # (S, L)
        self.X = self.E[self.idx]  # (S, L, d)
        self.s = s

    def sentence_posterior(self, Z, t):
        d2 = ((Z[None] - t * self.X) ** 2).sum((1, 2))
        lg = -d2 / (2 * (self.s * max(1 - t, 1e-6)) ** 2)
        lg -= lg.max()
        p = np.exp(lg)
        return p / p.sum()

    def word_probs(self, Z, t):
        """(L, V) per-position word probabilities."""
        ps = self.sentence_posterior(Z, t)
        P = np.zeros((self.L, len(self.vocab)))
        for s_i, p in enumerate(ps):
            P[np.arange(self.L), self.idx[s_i]] += p
        return P

    def sample(self, Z0, steps=16):
        ts = np.linspace(0, 1, steps + 1)
        Z = np.array(Z0, float)
        traj, probs = [Z.copy()], []
        for k in range(steps):
            t, h = ts[k], ts[k + 1] - ts[k]
            P = self.word_probs(Z, t)
            probs.append(P)
            G = P @ self.E
            Z = Z + (h / (1 - t)) * (G - Z)
            traj.append(Z.copy())
        probs.append(self.word_probs(Z, 1 - 1e-6))
        return ts, np.stack(traj), np.stack(probs)
