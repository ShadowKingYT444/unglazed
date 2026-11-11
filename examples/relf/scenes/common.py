"""Shared setup for the technical ReLF scenes."""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from unglazed.kit import *  # noqa: E402,F401,F403
from unglazed import sims  # noqa: E402,F401
import world  # noqa: E402

W = world.load()
LANG = W.lang
T4, T4_PI, T4_E = W.T4, W.T4_PI, W.T4_E

TRAIN = [
    "x1 = E[w]                        # (L, d)",
    "x0 = randn_like(x1);  t = sample_time()",
    "xt = t * x1 + (1 - t) * x0",
    "C  = k * stopgrad(soft(net(xt, t, 0, om)))",
    "logits = singular(xt, t) + net(xt, t, C, om)",
    "loss = cross_entropy(logits - delta, w)",
]
SAMPLE = [
    "z = randn(L, d);  C = 0",
    "for i in range(N):",
    "    p = softmax(singular(z, t[i]) + net(z, t[i], C, om))",
    "    xhat = p @ E",
    "    if i == N - 1: return argmax(p)",
    "    z = renoise(z, xhat, t[i])",
    "    z = z + (t[i+1] - t[i]) / (1 - t[i]) * (xhat - z)",
    "    C = xhat",
]


def spine(which, lit, size=0.17, corner=UR, dim=0.22):
    """The small code panel in a corner that shows which line of the two loops a scene is about."""
    p = CodePanel(TRAIN if which == "train" else SAMPLE, size=size, line_gap=0.12)
    for i, ln in enumerate(p.lines):
        ln.set_opacity(1.0 if i in lit else dim)
    p.to_corner(corner, buff=0.3)
    return p


class Plane2:
    """Data coordinates -> screen for a frameless 2D scatter."""

    def __init__(self, center=ORIGIN, unit=1.5):
        self.c, self.u = np.array(center, float), unit

    def p(self, xy):
        xy = np.asarray(xy, float)
        out = np.zeros(xy.shape[:-1] + (3,))
        out[..., :2] = xy * self.u
        return out + self.c


def token_dots(pl, E, names, size=0.3, color=DATA, radius=0.07, side=None):
    dots = VGroup(*[Dot(pl.p(e), radius=radius).set_fill(color, 1).set_stroke(width=0) for e in E])
    labs = VGroup()
    for i, (n, e) in enumerate(zip(names, E)):
        d = (side[i] if side else (RIGHT if e[0] >= 0 else LEFT))
        labs.add(Tx(n, size, FG).next_to(pl.p(e), d, buff=0.12))
    return dots, labs
