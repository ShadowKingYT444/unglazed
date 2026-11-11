"""The world: the numbers every scene draws from, computed with the source's own formulas (no manim imports here).

Keep it small enough to compute exactly, so nothing on screen is a sketch. `load()` caches it in build/<video>/.
"""
from __future__ import annotations

import pickle
from types import SimpleNamespace

from unglazed.paths import build_dir


def build():
    W = SimpleNamespace()
    W.x0, W.x1 = -1.6, 2.0          # one noise value and one data value
    W.t, W.h = 0.5, 0.125
    W.xt = W.t * W.x1 + (1 - W.t) * W.x0
    W.fraction = W.h / (1 - W.t)
    W.x_next = W.xt + W.fraction * (W.x1 - W.xt)
    return W


def load(rebuild=False):
    f = build_dir() / "world.pkl"
    if f.exists() and not rebuild:
        return pickle.loads(f.read_bytes())
    W = build()
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_bytes(pickle.dumps(W))
    return W
