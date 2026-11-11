"""Part 4: the embedding table. Why geometry matters, Hellinger distance, SVD and normalisation, the time schedule."""
from common import *

CLASSES = {
    "article": (["the", "a"], FG),
    "animal": (["cat", "dog", "bird"], DATA),
    "verb": (["sat", "ran", "slept", "sang"], HOT),
    "preposition": (["on", "to", "in", "by"], BLUE),
    "place": (["mat", "rug", "door", "park", "tree"], NOISE),
}
CLS_OF = {w: c for c, (ws, _col) in CLASSES.items() for w in ws}
COL_OF = {w: col for c, (ws, col) in CLASSES.items() for w in ws}
E = W.emb


def normalise(tab, pi):
    tab = tab - (pi[:, None] * tab).sum(0)
    return tab * np.sqrt(tab.shape[1] / (pi * (tab ** 2).sum(1)).sum())


def class_mass(tab, z, t):
    lg = np.log(E.pi) - ((z[None] - t * tab) ** 2).sum(1) / (2 * (1 - t) ** 2)
    p = np.exp(lg - lg.max())
    p /= p.sum()
    return np.array([sum(p[E.vocab.index(w)] for w in ws) for ws, _c in CLASSES.values()])


def class_scatter(pl, tab, radius=0.07):
    return VGroup(*[Dot(pl.p(e), radius=radius).set_fill(COL_OF[w], 1).set_stroke(width=0) for w, e in zip(E.vocab, tab)])


def legend():
    g = VGroup()
    for c, (_ws, col) in CLASSES.items():
        g.add(VGroup(Dot(radius=0.06).set_fill(col, 1).set_stroke(width=0), Tx(c, 0.22, col)).arrange(RIGHT, buff=0.1))
    return g.arrange(RIGHT, buff=0.4)


class S13(BeatScene):
    SID = "s13"

    def construct(self):
        rng = np.random.default_rng(13)
        rand_tab = normalise(rng.normal(size=E.E.shape), E.pi)
        L = Plane2(center=LEFT * 3.5 + UP * 1.0, unit=1.05)
        R = Plane2(center=RIGHT * 3.5 + UP * 1.0, unit=1.05)
        dl, dr = class_scatter(L, rand_tab), class_scatter(R, E.E)
        tl = Tx("a random table", 0.27, DIM).move_to(LEFT * 3.5 + UP * 3.4)
        trr = Tx("tokens used alike sit together", 0.27, DIM).move_to(RIGHT * 3.5 + UP * 3.4)
        leg = legend().move_to(DOWN * 3.5)
        fit(leg, 9.0)

        # b0: any table works in theory; in practice it decides how hard the job is
        self.at(0)
        self.wait(self.dur(0) * 0.3)
        self.play(FadeIn(dl), FadeIn(tl), FadeIn(leg), run_time=0.9)
        self.wait(max(0.1, self.dur(0) * 0.65 - 1.0))
        self.play(FadeIn(dr), FadeIn(trr), run_time=0.9)

        # b1: noise blurs nearby tokens together first
        self.at(1)
        t = 0.5
        cat = E.vocab.index("cat")
        eps = np.array([0.35, -0.25])
        zl, zr = t * rand_tab[cat] + (1 - t) * eps, t * E.E[cat] + (1 - t) * eps
        hl = halo(L.p(zl / t), (1 - t) / t * L.u, color=NOISE, fill=0.1)
        hr = halo(R.p(zr / t), (1 - t) / t * R.u, color=NOISE, fill=0.1)
        self.play(FadeIn(hl), FadeIn(hr), run_time=1.0)
        hn = Tx("circle: the tokens a half-noisy point cannot tell apart (true token: cat)", 0.24, NOISE).move_to(DOWN * 1.45)
        self.play(FadeIn(hn), run_time=0.6)

        # b2: random table: the nearby tokens have nothing in common
        self.at(2)
        ml, mr = class_mass(rand_tab, zl, t), class_mass(E.E, zr, t)
        names = list(CLASSES.keys())
        bl = Bars(names, ml, width=2.0, bar_h=0.17, gap=0.1, size=0.2, color=FG).move_to(LEFT * 3.5 + DOWN * 2.45)
        br = Bars(names, mr, width=2.0, bar_h=0.17, gap=0.1, size=0.2, color=FG).move_to(RIGHT * 3.5 + DOWN * 2.45)
        for b in (bl, br):
            for (t_, base, bar, _y), (_c, (_ws, col)) in zip(b.rows, CLASSES.items()):
                bar.set_fill(col, 0.95)
        self.play(FadeOut(hn), FadeIn(bl), run_time=0.8)
        cl = Tx("posterior by word class", 0.21, DIM).next_to(bl, UP, buff=0.15)
        self.play(FadeIn(cl), run_time=0.4)

        # b3: structured table: the same point already says "an animal or a place goes here"
        self.at(3)
        cr = Tx("posterior by word class", 0.21, DIM).next_to(br, UP, buff=0.15)
        self.play(FadeIn(br), FadeIn(cr), run_time=0.8)

        # b4: the paper's measurement: random Gaussian table 83.6 vs Hellinger-SVD 42.1
        self.at(4)
        self.play(*[FadeOut(m) for m in (dl, dr, tl, trr, leg, hl, hr, bl, br, cl, cr)], run_time=0.6)
        ch = BarChart(["random Gaussian\ntable, d = 32", "the paper's table\n(Hellinger-SVD), d = 32"], [83.6, 42.1], colors=["#bdbdbd", HOT], unit=0.045, bar_w=1.6, gap=1.6).move_to(DOWN * 0.4)
        cap = Tx("generative perplexity  ·  ReLF-Small, entropy 5.34 and 5.37  ·  lower is better", 0.24, DIM).to_edge(UP, buff=0.55)
        self.play(FadeIn(ch.base), FadeIn(cap), run_time=0.6)
        self.wait(max(0.1, self.dur(4) * 0.4 - 0.6))
        self.play(*ch.grow(0), run_time=0.8)
        self.wait(max(0.1, self.dur(4) * 0.65 - (self.time - self.start(4))))
        self.play(*ch.grow(1), run_time=0.8)
        self.finish()


class S14(BeatScene):
    SID = "s14"

    def construct(self):
        toks = ["cat", "dog", "the"]
        rows = [E.vocab.index(w) for w in toks]
        C = len(E.ctx)
        keep = [j for j in range(2 * C) if E.counts[rows, j].sum() > 0]
        cell = min(0.62, 11.0 / len(keep))

        def heat(mat, vmax):
            h = Heat(mat[np.ix_(rows, keep)] / vmax, cell=cell, mode="prob", color=DATA, gap=0.03)
            return h

        hc = heat(E.counts, E.counts[rows].max()).move_to(UP * 1.0)
        rl = VGroup(*[Tx(w, 0.26, FG).next_to(hc.cell_at(r, 0), LEFT, buff=0.15) for r, w in enumerate(toks)])
        nb = sum(1 for j in keep if j < C)
        g1 = Tx("token right before", 0.22, DIM).next_to(VGroup(*[hc.cell_at(0, c) for c in range(nb)]), UP, buff=0.5)
        g2 = Tx("token right after", 0.22, DIM).next_to(VGroup(*[hc.cell_at(0, c) for c in range(nb, len(keep))]), UP, buff=0.5)
        cn = VGroup()
        for c, j in enumerate(keep):
            name = E.ctx[j % C].replace("<s>", "start").replace("</s>", "end")
            t = Tx(name, 0.2, DIM).rotate(PI / 2)
            t.next_to(hc.cell_at(0, c), UP, buff=0.06)
            cn.add(t)
        g1.shift(UP * 0.55), g2.shift(UP * 0.55)
        stage = Tx("counts", 0.28, FG).next_to(hc, DOWN, buff=0.35)

        # b0: count which tokens come right before and right after
        self.at(0)
        self.wait(self.dur(0) * 0.35)
        self.play(FadeIn(rl), FadeIn(hc), FadeIn(cn), FadeIn(g1), FadeIn(g2), FadeIn(stage), run_time=1.2)

        # b1: normalise and smooth: a context distribution per token
        self.at(1)
        hq = heat(E.Q, E.Q[rows].max()).move_to(hc)
        st2 = M("Q_a(c)", size=0.4).next_to(hc, DOWN, buff=0.35)
        sm = Tx("normalised, and smoothed toward the average context (paper: strength 2,000)", 0.22, DIM).next_to(st2, DOWN, buff=0.2)
        self.play(FadeOut(hc), FadeIn(hq), FadeOut(stage), FadeIn(st2), run_time=0.9)
        self.wait(max(0.1, self.dur(1) * 0.5 - 0.9))
        self.play(FadeIn(sm), run_time=0.6)

        # b2: square roots: each row is a unit vector
        self.at(2)
        hh = heat(E.H, E.H[rows].max()).move_to(hc)
        st3 = M("H_{a,c}", "=", "\\sqrt{Q_a(c)}", size=0.4).next_to(hc, DOWN, buff=0.35)
        unit = M("\\sum_c H_{a,c}^2", "=", "\\sum_c Q_a(c)", "=", "1", size=0.4).next_to(st3, DOWN, buff=0.35)
        self.play(FadeOut(hq), FadeIn(hh), FadeOut(st2), FadeOut(sm), FadeIn(st3), run_time=0.9)
        self.wait(max(0.1, self.dur(2) * 0.5 - 0.9))
        self.play(FadeIn(unit), run_time=0.7)

        # b3: Eq. 7: squared distance between rows = 2 x squared Hellinger distance
        self.at(3)
        eq7 = M("\\|H_a - H_b\\|^2", "=", "\\sum_c \\left(\\sqrt{Q_a(c)} - \\sqrt{Q_b(c)}\\right)^2", "=", "2\\,d_{\\mathrm{Hel}}^2(Q_a,\\,Q_b)", colors={4: HOT}, size=0.44)
        fit(eq7, 10.5).move_to(DOWN * 1.6)
        tag = Tx("Eq. 7", 0.24, DIM).next_to(eq7, RIGHT, buff=0.3)
        self.play(FadeOut(st3), FadeOut(unit), run_time=0.4)
        self.play(FadeIn(eq7), FadeIn(tag), run_time=0.9)

        # b4: on the toy corpus: cat-dog 0.26, cat-the 1.20
        self.at(4)
        d1 = float(np.linalg.norm(E.H[rows[0]] - E.H[rows[1]]))
        d2 = float(np.linalg.norm(E.H[rows[0]] - E.H[rows[2]]))
        b1 = SurroundingRectangle(VGroup(hh.row(0), hh.row(1)), buff=0.05).set_stroke(DATA, 2)
        n1 = Tx(f"cat – dog:  {d1:.2f}", 0.3, DATA).move_to(LEFT * 2.6 + DOWN * 2.9)
        n2 = Tx(f"cat – the:  {d2:.2f}", 0.3, RED).move_to(RIGHT * 2.6 + DOWN * 2.9)
        self.wait(self.dur(4) * 0.4)
        self.play(ShowCreation(b1), FadeIn(n1), run_time=0.7)
        self.wait(max(0.1, self.dur(4) * 0.72 - (self.time - self.start(4))))
        b2 = SurroundingRectangle(hh.row(2), buff=0.05).set_stroke(RED, 2)
        self.play(ShowCreation(b2), FadeIn(n2), run_time=0.7)
        self.finish()


class S15(BeatScene):
    SID = "s15"

    def construct(self):
        # b0: keep the top directions of a frequency-weighted SVD
        S = E.S[:13]
        sv = BarChart([str(i + 1) for i in range(len(S))], list(S), colors=[HOT if i < 2 else "#777777" for i in range(len(S))], unit=5.5, bar_w=0.42, gap=0.16, size=0.2, fmt="{:.2f}", val_size=0.17)
        sv.move_to(LEFT * 3.2 + DOWN * 0.2)
        svt = Tx("singular values of the toy table: keep the largest d (toy: 2, paper: 32)", 0.24, DIM).next_to(sv, UP, buff=0.4)
        fit(svt, 6.6)
        shape = M("H:\\ V \\times 2V", "\\ \\longrightarrow\\ ", "E:\\ V \\times d", colors={2: HOT}, size=0.44).move_to(RIGHT * 3.6 + UP * 2.6)
        self.at(0)
        self.wait(self.dur(0) * 0.2)
        self.play(FadeIn(shape[0]), run_time=0.6)
        self.wait(max(0.1, self.dur(0) * 0.45 - 0.8))
        self.play(FadeIn(sv), FadeIn(svt), run_time=1.0)
        self.play(FadeIn(VGroup(shape[1], shape[2])), run_time=0.6)

        # b1: projection keeps close rows close
        self.at(1)
        pl = Plane2(center=RIGHT * 3.6 + DOWN * 0.5, unit=1.1)
        sc = VGroup(*[Dot(pl.p(e), radius=0.07).set_fill(HOT, 1).set_stroke(width=0) for e in E.E])
        labs = VGroup()
        for txt, w, side in [("the", "the", LEFT), ("a", "a", UP), ("prepositions", "in", UP), ("verbs", "ran", LEFT), ("animals and places", "dog", DOWN)]:
            labs.add(Tx(txt, 0.21, DIM).next_to(pl.p(E.E[E.vocab.index(w)]), side, buff=0.2))
        self.play(LaggedStart(*[FadeIn(d, scale=2) for d in sc], lag_ratio=0.04), run_time=1.4)
        self.play(FadeIn(labs), run_time=0.6)

        # b2: normalise: mean zero, squared length d under the token frequencies -> signal 1 per coordinate
        self.at(2)
        self.play(FadeOut(sv), FadeOut(svt), run_time=0.5)
        n1 = M("\\sum_w \\pi(w)\\,E(w)", "=", "0", size=0.46)
        n2 = M("\\sum_w \\pi(w)\\,\\|E(w)\\|^2", "=", "d", size=0.46)
        chk = Tx(f"toy check:  mean = ({abs((E.pi[:, None] * E.E).sum(0)[0]):.2f}, {abs((E.pi[:, None] * E.E).sum(0)[1]):.2f}),  squared length = {(E.pi * (E.E ** 2).sum(1)).sum():.2f}", 0.23, DIM)
        why = VGroup(Tx("signal per coordinate: 1", 0.26, DATA), Tx("noise per coordinate: 1", 0.26, NOISE)).arrange(DOWN, buff=0.15, aligned_edge=LEFT)
        col = ladder(n1, n2, chk, why, buff=0.45).move_to(LEFT * 3.4 + DOWN * 0.1)
        d = self.dur(2)
        self.wait(d * 0.2)
        self.play(FadeIn(n1), FadeIn(n2), run_time=0.9)
        self.play(FadeIn(chk), run_time=0.5)
        self.wait(max(0.1, d * 0.68 - (self.time - self.start(2))))
        self.play(FadeIn(why), run_time=0.7)

        # b3: the dimension ablation (Table 3)
        self.at(3)
        self.play(*[FadeOut(m) for m in (col, sc, labs, shape)], run_time=0.6)
        vals = [46.5, 24.1, 25.4, 37.6, 56.6]
        ent = ["5.32", "5.45", "5.51", "5.57", "5.61"]
        ch = BarChart([f"d = {d_}\nentropy {e}" for d_, e in zip([16, 32, 64, 128, 256], ent)], vals, colors=["#bdbdbd", HOT, "#bdbdbd", "#bdbdbd", "#bdbdbd"], unit=0.07, bar_w=1.25, gap=0.7, size=0.22).move_to(DOWN * 0.4)
        cap = Tx("generative perplexity by embedding dimension  ·  ReLF-Small, 64 steps, weakest guidance tested  ·  Table 3", 0.23, DIM).to_edge(UP, buff=0.5)
        self.play(FadeIn(ch.base), FadeIn(cap), run_time=0.6)
        d = self.dur(3)
        for i, f in enumerate([0.28, 0.45, 0.58, 0.82, 0.86]):
            self.wait(max(0.05, d * f - (self.time - self.start(3))))
            self.play(*ch.grow(i), run_time=0.6)

        # b4: every toy picture in this video used this recipe
        self.at(4)
        self.play(FadeOut(ch), FadeOut(cap), run_time=0.5)
        pl2 = Plane2(center=DOWN * 0.2, unit=1.6)
        sc2 = VGroup(*[Dot(pl2.p(e), radius=0.075).set_fill(HOT, 1).set_stroke(width=0) for e in E.E])
        l2 = VGroup(*[Tx(w, 0.2, FG).next_to(pl2.p(E.E[E.vocab.index(w)]), s_, buff=0.12) for w, s_ in [("the", LEFT), ("a", UP), ("in", UR), ("ran", LEFT), ("sat", RIGHT), ("cat", RIGHT), ("park", DL)]])
        note = Tx("the toy table of this video: the same recipe, 12 sentences, d = 2", 0.25, DIM).to_edge(DOWN, buff=0.5)
        self.play(FadeIn(sc2), FadeIn(l2), FadeIn(note), run_time=1.0)
        self.finish()


class S16(BeatScene):
    SID = "s16"

    def construct(self):
        # identification curves on the toy language: gain of the true token's log posterior over its log prior
        rng = np.random.default_rng(16)
        ts = np.linspace(0.02, 0.98, 49)
        g_pos, g_ctx = [], []
        for t in ts:
            a, b = [], []
            for _ in range(240):
                s = rng.integers(len(W.sentences))
                X1 = LANG.X[s]
                Z = t * X1 + (1 - t) * rng.normal(size=X1.shape)
                idx = LANG.idx[s]
                prior = LANG.logpi[idx]
                a.append((LANG.ref_logpost(Z, t)[np.arange(LANG.L), idx] - prior).mean())
                b.append((LANG.true_logpost(Z, t)[np.arange(LANG.L), idx] - prior).mean())
            g_pos.append(np.mean(a)), g_ctx.append(np.mean(b))
        g_pos, g_ctx = np.array(g_pos), np.array(g_ctx)
        n_pos, n_ctx = (g_pos - g_pos.min()) / np.ptp(g_pos), (g_ctx - g_ctx.min()) / np.ptp(g_ctx)
        seg = np.sqrt(np.diff(n_pos) ** 2 + np.diff(n_ctx) ** 2)
        arc = np.concatenate([[0], np.cumsum(seg)]) / seg.sum()
        samp = np.interp(np.linspace(0.02, 0.98, 40), arc, ts)

        ker = np.ones(5) / 5
        sm_pos = np.convolve(np.pad(g_pos, 2, mode="edge"), ker, mode="valid")
        sm_ctx = np.convolve(np.pad(g_ctx, 2, mode="edge"), ker, mode="valid")
        ymax = float(sm_pos.max()) * 1.08
        level = (sm_pos - sm_pos.min()) / np.ptp(sm_pos)
        samp = np.interp(np.linspace(0.03, 0.97, 40), level, ts)     # evenly spaced along the curve's rise
        plot = Plot(xr=(0, 1), yr=(0, ymax), w=8.5, h=4.2, xlabel="time t", xticks=(0, 0.5, 1), yticks=(0, 1, 2)).move_to(UP * 0.2)
        c1 = plot.curve(ts, sm_pos, HOT, 4)
        c2 = plot.curve(ts, sm_ctx, BLUE, 4)
        l1 = Tx("from the position alone", 0.24, HOT).next_to(plot.p(0.8, sm_pos[39]), DOWN, buff=0.3).shift(RIGHT * 0.9)
        l2 = Tx("with context", 0.24, BLUE).next_to(plot.p(0.55, sm_ctx[27]), UP, buff=0.3).shift(LEFT * 0.9)
        yl = Tx("gain in log probability of the true token over its prior, in nats (toy language)", 0.23, DIM).next_to(plot, UP, buff=0.2)

        # b0: very early nothing can be identified; very late everything already is
        self.at(0)
        self.play(FadeIn(plot), FadeIn(yl), run_time=0.8)
        early = Rectangle(plot.w * 0.12, plot.h).set_stroke(width=0).set_fill(DIM, 0.18).move_to(plot.p(0.06, ymax / 2))
        late = Rectangle(plot.w * 0.06, plot.h).set_stroke(width=0).set_fill(DIM, 0.18).move_to(plot.p(0.97, ymax / 2))
        self.wait(max(0.1, self.dur(0) * 0.5 - 0.8))
        self.play(FadeIn(early), run_time=0.5)
        self.wait(max(0.1, self.dur(0) * 0.78 - (self.time - self.start(0))))
        self.play(FadeIn(late), run_time=0.5)

        # b1: the two identification curves
        self.at(1)
        self.play(FadeOut(early), FadeOut(late), run_time=0.4)
        self.wait(max(0.1, self.dur(1) * 0.55 - 0.4))
        self.play(ShowCreation(c1), FadeIn(l1), run_time=1.8, rate_func=linear)

        # b2: sample times evenly along the arc length of the two curves
        self.at(2)
        ticks = VGroup(*[Line(plot.p(t, 0) + DOWN * 0.55, plot.p(t, 0) + DOWN * 0.85).set_stroke(FG, 2) for t in samp])
        tl = Tx("training times: evenly spaced along the rise of the curve", 0.24, FG).next_to(ticks, DOWN, buff=0.2)
        self.wait(self.dur(2) * 0.1)
        self.play(LaggedStart(*[ShowCreation(t) for t in ticks], lag_ratio=0.04), FadeIn(tl), run_time=2.0)
        ref = Tx("toy version with the position-alone curve only  ·  the paper combines it with a local-context curve: appendix B.1", 0.22, DIM).to_edge(DOWN, buff=0.35)
        self.wait(max(0.1, self.dur(2) * 0.75 - (self.time - self.start(2))))
        self.play(FadeIn(ref), run_time=0.6)
        self.finish()
