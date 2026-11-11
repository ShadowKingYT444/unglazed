import numpy as np

from unglazed import sims


def world():
    rng = np.random.default_rng(0)
    X = sims.islands(rng, [(-1.5, 1.0), (1.5, -1.0)], n_each=20, spread=0.1)
    return rng, X


def test_posterior_is_a_distribution_and_sharpens():
    rng, X = world()
    z = rng.normal(size=(5, 2))
    early, late = sims.posterior(z, 0.05, X), sims.posterior(0.99 * X[:5], 0.99, X)
    assert np.allclose(early.sum(1), 1) and np.allclose(late.sum(1), 1)
    assert early.max() < 0.2            # near t = 0 the point says almost nothing
    assert np.allclose(late.argmax(1), np.arange(5))   # near t = 1 the nearest data point wins


def test_guess_at_time_zero_is_the_data_mean():
    rng, X = world()
    g = sims.guess(rng.normal(size=(4, 2)), 0.0, X)
    assert np.allclose(g, X.mean(0), atol=1e-6)


def test_velocity_is_guess_minus_point_over_time_left():
    rng, X = world()
    z, t = rng.normal(size=(3, 2)), 0.4
    assert np.allclose(sims.velocity(z, t, X), (sims.guess(z, t, X) - z) / (1 - t))


def test_flow_lands_on_data_and_one_step_lands_on_the_mean():
    rng, X = world()
    z0 = rng.normal(size=(50, 2))
    _, fine = sims.integrate(z0, X, steps=200)
    dist = np.sqrt(((fine[-1][:, None] - X[None]) ** 2).sum(-1)).min(1)
    assert dist.mean() < 0.01 and dist.max() < 0.1
    _, one = sims.integrate(z0, X, steps=1)
    assert np.allclose(one[-1], X.mean(0), atol=1e-6)


def test_reflow_makes_paths_straighter():
    rng, X = world()
    z0 = rng.normal(size=(300, 2))
    ts, tr = sims.integrate(z0, X, steps=100)
    pf = sims.PairFlow(z0, tr[-1], bw=0.1)
    ts2, tr2 = pf.integrate(z0[:60], steps=60)
    assert sims.straightness(ts2, tr2) < 0.2 * sims.straightness(ts, tr[:, :60])
