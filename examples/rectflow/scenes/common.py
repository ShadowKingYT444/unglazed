"""Shared setup for "Rectified flow, from scratch"."""
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
GREY = "#bdbdbd"

HEAD = (0.0, 3.2, 12.6, 1.2)          # a formula above the main picture (taller than Stage.title)
FM_CODE = [
    "x0, x1 = randn(), sample_data()",
    "t  = rand()",
    "xt = t * x1 + (1 - t) * x0",
    "loss = (net(xt, t) - x1) ** 2",
]
LOOP_CODE = [
    "z = randn(L, d)",
    "for i in range(N):",
    "    p = softmax(net(z, t[i]))          # bars for every slot",
    "    guess = p @ E                      # soft tokens",
    "    if i == N - 1: return argmax(p)",
    "    z = z + (t[i+1] - t[i]) / (1 - t[i]) * (guess - z)",
]
TRAIN_FULL = [
    "x1 = E[w]                                # words -> locations",
    "x0 = randn_like(x1);  t = sample_time()",
    "xt = t * x1 + (1 - t) * x0               # the straight line",
    "C  = coin * stopgrad(soft(net(xt, t, 0)))   # previous guess",
    "logits = closeness(xt, t) + net(xt, t, C)   # formula + learned",
    "loss = cross_entropy(logits, w)",
]
SAMPLE_FULL = [
    "z = randn(L, d);  C = 0",
    "for i in range(N):",
    "    p = softmax(closeness(z, t[i]) + net(z, t[i], C))",
    "    guess = p @ E",
    "    if i == N - 1: return argmax(p)",
    "    z = z + (t[i+1] - t[i]) / (1 - t[i]) * (guess - z)",
    "    C = guess",
]


class XT:
    """The picture of the two-number world: time runs left to right (0 = noise, 1 = data), the value runs up."""

    def __init__(self, zone=Stage.main, xlim=3.0, pad=1.7, vfill=0.86):
        cx, cy, w, h = zone
        self.a, self.b = cx - w / 2 + pad, cx + w / 2 - pad          # screen x of t = 0 and t = 1
        self.cy, self.half, self.xlim = cy, h * vfill / 2, xlim

    def p(self, t, x):
        return np.array([self.a + t * (self.b - self.a), self.cy + x / self.xlim * self.half, 0.0])

    def P(self, ts, xs):
        ts, xs = np.broadcast_arrays(np.asarray(ts, float), np.asarray(xs, float))
        out = np.zeros(ts.shape + (3,))
        out[..., 0] = self.a + ts * (self.b - self.a)
        out[..., 1] = self.cy + xs / self.xlim * self.half
        return out

    def axes(self, data=True):
        g = VGroup()
        left = Line(self.p(0, -self.xlim), self.p(0, self.xlim)).set_stroke(DIM, 2)
        right = Line(self.p(1, -self.xlim), self.p(1, self.xlim)).set_stroke(DIM, 2)
        base = Line(self.p(0, -self.xlim), self.p(1, -self.xlim)).set_stroke(FAINT, 1.5)
        l0 = VGroup(Tx("noise", 0.32, NOISE), Tx("time 0", 0.25, DIM)).arrange(DOWN, buff=0.08).next_to(self.p(0, -self.xlim), DOWN, buff=0.15)
        l1 = VGroup(Tx("data", 0.32, DATA), Tx("time 1", 0.25, DIM)).arrange(DOWN, buff=0.08).next_to(self.p(1, -self.xlim), DOWN, buff=0.15)
        g.add(left, right, base, l0, l1)
        g.left, g.right, g.base, g.l0, g.l1 = left, right, base, l0, l1
        if data:
            g.marks = self.data_marks()
            g.add(g.marks)
        return g

    def data_marks(self):
        g = VGroup()
        for v, lab in ((1, "+1"), (-1, "−1")):
            g.add(Dot(self.p(1, v), radius=0.09).set_fill(DATA, 1).set_stroke(width=0))
            g.add(Tx(lab, 0.34, DATA).next_to(self.p(1, v), UR, buff=0.13))
        return g

    def lines(self, ts, X, color=FG, width=1.5, opacity=0.5):
        """One polyline per column of X (T, N)."""
        g = VGroup()
        for j in range(X.shape[1]):
            g.add(VMobject().set_points_as_corners(self.P(ts, X[:, j])).set_stroke(color, width, opacity))
        return g

    def jitter(self, n, width=0.16, seed=0):
        """Small fixed sideways offsets, so a crowd at one time reads as a crowd and not as a line."""
        out = np.zeros((n, 3))
        out[:, 0] = np.random.default_rng(seed).uniform(-width, width, n)
        return out

    def crowd(self, xs, t=0.0, color=NOISE, radius=0.04, opacity=0.9, jitter=0.16):
        return DotCloud(self.P(np.full(len(xs), t), xs) + self.jitter(len(xs), jitter), color=color, radius=radius, opacity=opacity)

    def hist(self, xs, t, direction=1, scale=1.6, bins=48, color=NOISE, opacity=0.85):
        """A sideways histogram of the crowd, standing on the vertical line at time t."""
        edges = np.linspace(-self.xlim, self.xlim, bins + 1)
        h, _ = np.histogram(np.clip(xs, -self.xlim + 1e-6, self.xlim - 1e-6), bins=edges)
        h = h / max(h.max(), 1) if False else h / len(xs) * bins / 6.0
        g = VGroup()
        bh = (self.p(0, edges[1])[1] - self.p(0, edges[0])[1]) * 0.9
        for k in range(bins):
            wd = max(1e-3, min(float(h[k]), 1.6) * scale)
            r = Rectangle(wd, bh).set_stroke(width=0).set_fill(color, opacity)
            c = self.p(t, (edges[k] + edges[k + 1]) / 2)
            r.move_to(c + RIGHT * direction * wd / 2)
            g.add(r)
        return g


def live_hist(xt, fn, direction=1, scale=1.6, bins=40, color=NOISE, opacity=0.85):
    """A sideways histogram that follows fn() -> (values, time) on every frame."""
    kw = dict(direction=direction, scale=scale, bins=bins, color=color, opacity=opacity)
    g = xt.hist(*fn(), **kw)
    g.add_updater(lambda m: m.become(xt.hist(*fn(), **kw)))
    return g


def picture(n=96):
    """A small procedural painting (sky, sun, hills), so the hook can show an image made from static."""
    y, x = np.mgrid[0:n, 0:n] / (n - 1)
    sky = np.stack([0.95 - 0.55 * y, 0.55 + 0.1 * y, 0.35 + 0.5 * (1 - y)], -1) * 0.9
    img = sky.copy()
    sun = ((x - 0.7) ** 2 + (y - 0.32) ** 2) < 0.012
    img[sun] = [1.0, 0.93, 0.6]
    h1 = y > 0.66 + 0.08 * np.sin(6 * x + 0.5)
    img[h1] = [0.18, 0.42, 0.33]
    h2 = y > 0.78 + 0.06 * np.sin(9 * x + 2.0)
    img[h2] = [0.1, 0.27, 0.24]
    return np.clip(img, 0, 1)


def guess_plot(zone, clock, xlim=3.0):
    """The guess as a curve: along the bottom where you are, up the side what to guess; it follows the clock."""
    cx, cy, w, h = zone
    pl = Plot(xr=(-xlim, xlim), yr=(-1.25, 1.25), w=w * 0.8, h=h * 0.55)
    pl.move_to(np.array([cx, cy, 0]))
    mid = Line(pl.p(-xlim, 0), pl.p(xlim, 0)).set_stroke(FAINT, 1.5)
    vax = Line(pl.p(0, -1.25), pl.p(0, 1.25)).set_stroke(FAINT, 1.5)
    xs = np.linspace(-xlim, xlim, 160)
    curve = VMobject().set_stroke(BLUE, 4)

    def upd(m):
        t = float(np.clip(clock.get_value(), 0.0, 0.995))
        m.set_points_as_corners(np.stack([pl.p(x, world.guess1(x, t)) for x in xs]))

    upd(curve)
    curve.add_updater(upd)
    lx = Tx("where you are", 0.28, DIM).next_to(pl.xax, DOWN, buff=0.2)
    ly = Tx("what to guess", 0.28, BLUE).next_to(pl.p(-xlim, 1.25), UP, buff=0.15).shift(RIGHT * 0.6)
    ticks = VGroup(Tx("+1", 0.28, DIM).next_to(pl.p(-xlim, 1), LEFT, buff=0.1), Tx("−1", 0.28, DIM).next_to(pl.p(-xlim, -1), LEFT, buff=0.1),
                   Tx("0", 0.28, DIM).next_to(pl.p(-xlim, 0), LEFT, buff=0.1))
    g = VGroup(pl.xax, pl.yax, mid, vax, lx, ly, ticks, curve)
    g.plot, g.curve = pl, curve
    return g


# ---------------------------------------------------------------- rung 2: one word on a plane
class Plane2:
    """Data coordinates -> screen for a frameless 2D scatter."""

    def __init__(self, center=ORIGIN, unit=1.5):
        self.c, self.u = np.array(center, float), unit

    def p(self, xy):
        xy = np.asarray(xy, float)
        out = np.zeros(xy.shape[:-1] + (3,))
        out[..., :2] = xy * self.u
        return out + self.c


T4_SIDE = [LEFT, DOWN, UP, RIGHT]           # where each word's label sits: the, sat, cat, dog


def token_dots(pl, E=None, names=None, size=0.36, color=DATA, radius=0.09, side=None):
    E = T4_E if E is None else E
    names = T4 if names is None else names
    side = side or T4_SIDE
    dots = VGroup(*[Dot(pl.p(e), radius=radius).set_fill(color, 1).set_stroke(width=0) for e in E])
    labs = VGroup(*[Tx(n, size, FG).next_to(pl.p(e), side[i], buff=0.16) for i, (n, e) in enumerate(zip(names, E))])
    return dots, labs


def path4(z0, n=200):
    """One point of the one-word world following its guess: states (n+1, 2), bars (n+1, 4), guesses (n+1, 2)."""
    z = np.array(z0, float)
    tt = np.linspace(0, 1, n + 1)
    S, P, G = [], [], []
    for a, b in zip(tt[:-1], tt[1:]):
        p = world.post4(z, min(a, 0.999))[0]
        g = p @ T4_E
        S.append(z.copy()), P.append(p), G.append(g)
        z = z + (b - a) / (1 - a) * (g - z)
    p = world.post4(z, 0.999)[0]
    S.append(z.copy()), P.append(p), G.append(p @ T4_E)
    return np.array(S), np.array(P), np.array(G)


def card(scene, numeral, title, hold=2.3):
    """A short chapter card, for scenes whose first beat goes on after the chapter is announced."""
    n, t = Tx(numeral + ".", 0.5).move_to(UP * 0.75), Tx(title, 0.62).move_to(DOWN * 0.45)
    scene.play(FadeIn(n), FadeIn(t), run_time=0.8)
    scene.wait(hold)
    scene.play(FadeOut(n), FadeOut(t), run_time=0.6)


def live_bars(bars, fn):
    bars.add_updater(lambda m: m.set_values(fn()))
    return bars


# ---------------------------------------------------------------- rung 3: a sentence
VOCAB_ORDER = ["the", "a", "cat", "dog", "bird", "tree", "door", "rug", "mat", "park", "sat", "slept", "ran", "sang", "on", "in", "by", "to"]
VIDX = [LANG.vocab.index(w) for w in VOCAB_ORDER]


class ProbGrid(VGroup):
    """One column of bars-as-shades per slot: rows are the words, a cell's brightness is that word's probability."""

    def __init__(self, P, col_w=1.15, row_h=0.26, gap_x=0.12, gap_y=0.035, color=BLUE, size=0.25):
        super().__init__()
        self.L, self.color_ = P.shape[0], color
        self.cells = [[None] * self.L for _ in VIDX]
        for r in range(len(VIDX)):
            for c in range(self.L):
                q = Rectangle(col_w, row_h).set_stroke(FAINT, 1)
                q.move_to(np.array([c * (col_w + gap_x), -r * (row_h + gap_y), 0]))
                self.cells[r][c] = q
                self.add(q)
        self.labels = VGroup(*[Tx(w, size, DIM).move_to(np.array([-col_w / 2 - 0.15, -r * (row_h + gap_y), 0]), aligned_edge=RIGHT) for r, w in enumerate(VOCAB_ORDER)])
        self.add(self.labels)
        self.set_values(P)

    def set_values(self, P):
        for r, v in enumerate(VIDX):
            for c in range(self.L):
                self.cells[r][c].set_fill(self.color_, float(np.clip(P[c, v], 0, 1)) ** 0.7)
        return self

    def col_x(self, c):
        return self.cells[0][c].get_center()[0]

    def column(self, c):
        return VGroup(*[self.cells[r][c] for r in range(len(VIDX))])
