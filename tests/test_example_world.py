"""The demo video's toy world: the paper's formulas must hold on it, because the video shows these numbers."""
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "examples" / "relf"))
import world  # noqa: E402


@pytest.fixture(scope="module")
def emb():
    return world.hellinger_svd(world.SENTENCES)


def test_embedding_is_normalised_like_the_paper(emb):
    assert np.allclose((emb.pi[:, None] * emb.E).sum(0), 0, atol=1e-9)           # sum_w pi(w) E(w) = 0
    assert np.isclose((emb.pi * (emb.E ** 2).sum(1)).sum(), emb.E.shape[1])      # sum_w pi(w) |E(w)|^2 = d


def test_rows_of_H_are_unit_vectors_and_eq7_holds(emb):
    assert np.allclose((emb.H ** 2).sum(1), 1)
    a, b = emb.vocab.index("cat"), emb.vocab.index("dog")
    hel2 = 0.5 * ((np.sqrt(emb.Q[a]) - np.sqrt(emb.Q[b])) ** 2).sum()
    assert np.isclose(((emb.H[a] - emb.H[b]) ** 2).sum(), 2 * hel2)             # Eq. 7


def test_posteriors_are_distributions_and_the_residual_obeys_the_bound(emb):
    lang = world.Lang(world.SENTENCES, emb)
    rng = np.random.default_rng(0)
    bound = 2 * np.log(lang.kappa())                                             # Theorem 3.1
    for t in (0.1, 0.5, 0.9, 0.99):
        s = rng.integers(len(world.SENTENCES))
        Z = t * lang.X[s] + (1 - t) * rng.normal(size=lang.X[s].shape)
        q, r = lang.true_logpost(Z, t), lang.ref_logpost(Z, t)
        assert np.allclose(np.exp(q).sum(1), 1) and np.allclose(np.exp(r).sum(1), 1)
        assert np.abs(q - r).max() <= bound + 1e-6


def test_capping_the_whole_logits_misses_the_token_but_capping_the_residual_does_not(emb):
    lang = world.Lang(world.SENTENCES, emb)
    ts = np.concatenate([np.linspace(0, 1, 65)[:-1], [0.999]])
    rng = np.random.default_rng(1)
    miss = {}
    for name, kw in [("capped", dict(logit_cap=6, use_singular=False)), ("split", dict(logit_cap=6, use_singular=True))]:
        out = []
        for _ in range(5):
            _S, P, G = lang.euler(rng.normal(size=(lang.L, lang.d)), ts, **kw)
            out.append(np.linalg.norm(G[-1] - lang.E[P[-1].argmax(1)], axis=1).mean())
        miss[name] = float(np.mean(out))
    assert miss["capped"] > 0.02 and miss["split"] < 0.005
