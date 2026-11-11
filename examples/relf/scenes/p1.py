"""Opening and part 1: the two loops, the flow in four lines, the state, the one-position posterior."""
from common import *


class S01(BeatScene):
    SID = "s01"

    def construct(self):
        tr = CodePanel(TRAIN, size=0.23, line_gap=0.17)
        sa = CodePanel(SAMPLE, size=0.23, line_gap=0.17)
        lt = Tx("training step", 0.26, DIM)
        ls = Tx("sampling loop", 0.26, DIM)
        g = VGroup(lt, tr, ls, sa).arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        ls.shift(DOWN * 0.25), sa.shift(DOWN * 0.25)
        g.move_to(ORIGIN)
        q = Tx("how, exactly, do you run a flow on text?", 0.42, FG)

        self.at(0)
        self.wait(self.dur(0) * 0.55)
        self.play(FadeIn(q), run_time=0.8)

        self.at(1)
        paper = VGroup(Tx("Rectified Language Flow", 0.5), Tx("Su, Liao, Chen, Liu  ·  arXiv 2610.33811", 0.25, DIM)).arrange(DOWN, buff=0.25)
        self.play(FadeOut(q), FadeIn(paper), run_time=0.8)
        self.wait(max(0.1, self.dur(1) * 0.3 - 0.8))
        self.play(FadeOut(paper), run_time=0.5)
        tr.lines.set_opacity(0.3), sa.lines.set_opacity(0.3)
        self.play(FadeIn(lt), FadeIn(tr), run_time=0.8)
        self.wait(max(0.1, self.dur(1) * 0.78 - (self.time - self.start(1))))
        self.play(FadeIn(ls), FadeIn(sa), run_time=0.8)

        def light(t_idx, s_idx, rt=0.5):
            self.play(*tr.hl(*t_idx) if t_idx else [l.animate.set_opacity(0.3) for l in tr.lines],
                      *sa.hl(*s_idx) if s_idx else [l.animate.set_opacity(0.3) for l in sa.lines], run_time=rt)

        # b2: text -> matrix; what the network predicts; cross entropy
        self.at(2)
        d = self.dur(2)
        self.wait(d * 0.28)
        light([0, 1, 2], [0])
        self.wait(max(0.1, d * 0.6 - (self.time - self.start(2))))
        light([4], [2, 3])
        self.wait(max(0.1, d * 0.8 - (self.time - self.start(2))))
        light([5], [])

        # b3: singular logits; the embedding table; self-conditioning; guidance
        self.at(3)
        d = self.dur(3)
        light([4], [2])
        self.wait(max(0.1, d * 0.3 - 0.5))
        light([0], [3])
        self.wait(max(0.1, d * 0.52 - (self.time - self.start(3))))
        light([3], [7])
        self.wait(max(0.1, d * 0.8 - (self.time - self.start(3))))
        light([5], [2])

        # b4: reflow, 64 -> 16
        self.at(4)
        light([], [1, 5, 6])
        steps = VGroup(Tx("N = 64", 0.34, FG), Tx("→", 0.34, DIM), Tx("N = 16", 0.34, HOT)).arrange(RIGHT, buff=0.3).next_to(ls, RIGHT, buff=1.2)
        self.play(FadeIn(steps[0]), run_time=0.5)
        self.wait(max(0.1, self.dur(4) * 0.3 - 1.0))
        self.play(FadeIn(steps[1]), FadeIn(steps[2]), run_time=0.6)
        self.wait(max(0.1, self.dur(4) * 0.6 - (self.time - self.start(4))))
        self.play(*[l.animate.set_opacity(1) for l in tr.lines], *[l.animate.set_opacity(1) for l in sa.lines], run_time=0.8)
        self.finish()


class S02(BeatScene):
    SID = "s02"

    def construct(self):
        # a number line on the left, the four lines of algebra on the right
        x0, x1 = -1.6, 2.0
        u = 1.15
        org = LEFT * 3.6 + DOWN * 0.6

        def P(x):
            return org + RIGHT * x * u

        axis = Line(P(-2.4), P(2.6)).set_stroke(DIM, 2)
        d0 = Dot(P(x0), radius=0.1).set_fill(NOISE, 1).set_stroke(width=0)
        d1 = Dot(P(x1), radius=0.1).set_fill(DATA, 1).set_stroke(width=0)
        l0 = M("X_0", size=0.42, color=NOISE).next_to(d0, DOWN, buff=0.2)
        l1 = M("X_1", size=0.42, color=DATA).next_to(d1, DOWN, buff=0.2)
        n0 = Tx("noise, t = 0", 0.24, DIM).next_to(l0, DOWN, buff=0.15)
        n1 = Tx("data, t = 1", 0.24, DIM).next_to(l1, DOWN, buff=0.15)
        xt = Dot(P(x0), radius=0.12).set_fill(HOT, 1).set_stroke(width=0)
        xt.add_updater(lambda m: m.move_to(P((1 - self.clock.get_value()) * x0 + self.clock.get_value() * x1)))
        lt = M("X_t", size=0.42, color=HOT)
        lt.add_updater(lambda m: m.next_to(xt, UP, buff=0.2))
        bar = TimeBar(self.clock, width=4.0).move_to(org + DOWN * 2.3 + RIGHT * 0.1 * u)

        r1 = M("X_t", "=", "t", "X_1", "+", "(1-t)", "X_0", colors={0: HOT, 3: DATA, 6: NOISE}, size=0.5)
        r2 = M("v^*(z,t)", "=", "\\mathrm{E}[\\,", "X_1", "-", "X_0", "\\mid X_t = z\\,]", colors={3: DATA, 5: NOISE}, size=0.5)
        r3 = M("X_0", "=", "\\dfrac{X_t - t\\,X_1}{1-t}", colors={0: NOISE}, size=0.5)
        r4 = M("v^*(z,t)", "=", "\\dfrac{\\hat{x} - z}{1-t}", colors={}, size=0.5)
        r4b = M("\\hat{x}", "=", "\\mathrm{E}[\\,X_1 \\mid X_t = z\\,]", colors={0: BLUE}, size=0.5)
        r5 = M("z", "\\leftarrow", "z + \\dfrac{h}{1-t}\\,(\\hat{x} - z)", size=0.5)
        lad = ladder(r1, r2, r3, r4, r4b, r5, buff=0.42).move_to(RIGHT * 3.6 + UP * 0.2)

        self.at(0)
        self.play(ShowCreation(axis), FadeIn(d0), FadeIn(d1), FadeIn(l0), FadeIn(l1), run_time=1.0)
        self.play(FadeIn(n0), FadeIn(n1), FadeIn(bar), run_time=0.6)
        self.add(xt, lt)
        self.play(FadeIn(r1), run_time=0.6)
        self.run_clock(0, 1, self.left(1) - 1.2, rate_func=smooth)
        self.play(self.clock.animate.set_value(0.5), run_time=0.8)

        # b1: average velocity of all blends through a point
        self.at(1)
        rng = np.random.default_rng(2)
        z = (1 - 0.5) * x0 + 0.5 * x1
        others = [(z - 0.5 * b) / 0.5 for b in (2.3, 1.2, -0.4)]
        arcs = VGroup()
        for b, a in zip((2.3, 1.2, -0.4), others):
            arcs.add(ArcBetweenPoints(P(a), P(b), angle=-1.1).set_stroke(FG, 1.5, 0.45))
        self.play(LaggedStart(*[ShowCreation(a) for a in arcs], lag_ratio=0.3), FadeIn(r2), run_time=1.6)

        # b2: the noise is fixed by the point and the data
        self.at(2)
        self.play(FadeOut(arcs), FadeIn(r3), run_time=0.8)
        br = Line(P(x0), P(z)).set_stroke(NOISE, 5).shift(UP * 0.0)
        self.play(ShowCreation(br), run_time=0.8)
        self.wait(0.6)
        self.play(FadeOut(br), run_time=0.4)

        # b3: velocity = (expected clean data - where you are) / time left
        self.at(3)
        self.play(FadeIn(r4), run_time=0.8)
        xh = 1.5
        gd = ring(P(xh), 0.16, BLUE, 4)
        vel = arrow(P(z) + UP * 1.0, P(xh) + UP * 1.0, HOT, 5, buff=0)
        self.play(ShowCreation(vel), run_time=0.8)

        # b4: the network only has to guess the clean data
        self.at(4)
        gl = M("\\hat{x}", size=0.42, color=BLUE).next_to(gd, DOWN, buff=0.2)
        self.play(ShowCreation(gd), FadeIn(gl), FadeIn(r4b), d1.animate.set_opacity(0.25), l1.animate.set_opacity(0.25), n1.animate.set_opacity(0.0), run_time=0.9)

        # b5: one Euler step covers h / (1 - t) of the way: t = 1/2, h = 1/8 -> one quarter
        self.at(5)
        self.play(FadeIn(r5), FadeOut(vel), run_time=0.7)
        xt.clear_updaters(), lt.clear_updaters()
        ticks = VGroup(*[Line(P(z + k * (xh - z) / 4) + UP * 0.12, P(z + k * (xh - z) / 4) + DOWN * 0.12).set_stroke(FG, 2) for k in range(5)])
        nums = Tx("t = 1/2,  h = 1/8:  h / (1 − t) = 1/4", 0.28, FG).next_to(axis, UP, buff=1.2).shift(RIGHT * 0.4)
        self.wait(max(0.1, self.dur(5) * 0.42 - 0.7))
        self.play(FadeIn(ticks), FadeIn(nums), run_time=0.7)
        hop = Line(P(z), P(z + (xh - z) / 4)).set_stroke(HOT, 6)
        self.play(ShowCreation(hop), xt.animate.move_to(P(z + (xh - z) / 4)), lt.animate.shift(RIGHT * (xh - z) / 4 * u), self.clock.animate.set_value(0.625), run_time=1.2)
        self.finish()


class S03(BeatScene):
    SID = "s03"

    def construct(self):
        rng = np.random.default_rng(3)
        words = "the cat sat on the mat".split()
        ids = [LANG.vocab.index(w) for w in words]
        row = token_row(words, size=0.34, w=1.15, gap=0.12).move_to(UP * 3.0 + RIGHT * 1.6)
        idt = VGroup(*[Tx(str(1000 + 37 * i % 50257 if False else [262, 3797, 3332, 319, 262, 2603][k]), 0.24, DIM).next_to(row[k], DOWN, buff=0.15) for k, i in enumerate(ids)])

        # b0: text is a list of token ids
        self.at(0)
        self.play(FadeIn(row), run_time=0.8)
        self.wait(max(0.1, self.dur(0) * 0.35 - 0.8))
        self.play(LaggedStart(*[FadeIn(t) for t in idt], lag_ratio=0.1), run_time=1.0)
        facts = VGroup(Tx("V = 50,257 tokens", 0.27, DIM), Tx("L = 1,024 positions", 0.27, DIM)).arrange(DOWN, buff=0.15, aligned_edge=LEFT).to_corner(DL, buff=0.5)
        self.wait(max(0.1, self.dur(0) * 0.6 - (self.time - self.start(0))))
        self.play(FadeIn(facts), run_time=0.6)

        # b1: the embedding table E, fixed, built before training
        self.at(1)
        show = ["the", "a", "cat", "dog", "sat", "on", "mat"]
        tab = Heat(np.array([LANG.E[LANG.vocab.index(w)] for w in show]), cell=0.55, vmax=1.8, numbers=True)
        tab.move_to(LEFT * 4.9 + UP * 0.3)
        tl = VGroup(*[Tx(w, 0.26, FG).next_to(tab.cell_at(r, 0), LEFT, buff=0.15) for r, w in enumerate(show)])
        dots = Tx("⋮", 0.3, DIM).next_to(tab, DOWN, buff=0.1)
        tn = M("E", size=0.5).next_to(tab, UP, buff=0.25)
        dn = Tx("paper: 32 numbers per token", 0.24, DIM).next_to(dots, DOWN, buff=0.2)
        self.play(FadeIn(tab), FadeIn(tl), FadeIn(dots), FadeIn(tn), run_time=1.0)
        self.wait(max(0.1, self.dur(1) * 0.72 - 1.0))
        self.play(FadeIn(dn), run_time=0.6)

        # b2: look up each token: X1, one column per position
        self.at(2)
        X1 = LANG.E[ids].T                                  # (d, L)
        h1 = Heat(X1, cell=0.55, vmax=1.8, numbers=True)
        xs = [c.get_center()[0] for c in row]
        spread_cols(h1, xs, y=1.35)
        n1 = M("X_1", size=0.5, color=DATA).next_to(h1, RIGHT, buff=0.3)
        per = (self.dur(2) * 0.6) / 6
        for k, w in enumerate(words):
            r = show.index(w)
            hlr = SurroundingRectangle(tab.row(r), buff=0.04).set_stroke(HOT, 2)
            self.play(ShowCreation(hlr), run_time=per * 0.3)
            self.play(TransformFromCopy(tab.row(r), h1.col(k)), FadeIn(VGroup(h1.nums[k], h1.nums[6 + k])), run_time=per * 0.5)
            self.play(FadeOut(hlr), run_time=per * 0.2)
        self.add(h1)
        self.play(FadeIn(n1), run_time=0.5)

        # b3: X0, a Gaussian matrix of the same shape
        self.at(3)
        X0 = rng.normal(size=X1.shape)
        h0 = Heat(X0, cell=0.55, vmax=1.8, numbers=True)
        spread_cols(h0, xs, y=-2.6)
        n0 = M("X_0", size=0.5, color=NOISE).next_to(h0, RIGHT, buff=0.3)
        self.play(FadeIn(h0), FadeIn(n0), run_time=1.0)

        # b4: X_t, the blend; the only thing the flow moves
        self.at(4)
        self.clock.set_value(0.0)
        ht = Heat(X0, cell=0.55, vmax=1.8)
        spread_cols(ht, xs, y=-0.62)
        ht.add_updater(lambda m: m.set_values(self.clock.get_value() * X1 + (1 - self.clock.get_value()) * X0))
        nt = M("X_t", size=0.5, color=HOT).next_to(ht, RIGHT, buff=0.3)
        bar = TimeBar(self.clock, width=1.5).next_to(nt, DOWN, buff=0.45).shift(RIGHT * 0.35)
        self.play(FadeIn(ht), FadeIn(nt), FadeIn(bar), FadeOut(facts), run_time=0.8)
        d = self.dur(4)
        self.play(self.clock.animate.set_value(1.0), run_time=d * 0.35, rate_func=smooth)
        self.play(self.clock.animate.set_value(0.4), run_time=d * 0.25, rate_func=smooth)
        ht.clear_updaters()
        shape = Tx("paper: X is 32 × 1,024", 0.27, DIM).to_corner(DL, buff=0.5)
        self.play(FadeIn(shape), run_time=0.6)

        # b5: every clean column must be exactly one row of the table
        self.at(5)
        self.wait(self.dur(5) * 0.4)
        c2 = SurroundingRectangle(h1.col(1), buff=0.05).set_stroke(HOT, 2.5)
        r2 = SurroundingRectangle(tab.row(show.index("cat")), buff=0.05).set_stroke(HOT, 2.5)
        link = Line(r2.get_right(), c2.get_left()).set_stroke(HOT, 1.5)
        self.play(ShowCreation(c2), ShowCreation(r2), run_time=0.7)
        self.play(ShowCreation(link), run_time=0.6)
        self.finish()


class S04(BeatScene):
    SID = "s04"

    def construct(self):
        rng = np.random.default_rng(4)
        pl = Plane2(center=LEFT * 3.0 + DOWN * 0.1, unit=1.75)
        dots, labs = token_dots(pl, T4_E, T4, side=[LEFT, DOWN, UP, RIGHT])
        origin = Dot(pl.p([0, 0]), radius=0.035).set_fill(DIM, 1).set_stroke(width=0)
        cat = T4.index("cat")
        self.clock.set_value(0.5)

        def t():
            return float(np.clip(self.clock.get_value(), 0, 0.995))

        # b0: four tokens; if the clean token is cat, where can the noisy point be?
        self.at(0)
        self.play(LaggedStart(*[FadeIn(VGroup(d, l)) for d, l in zip(dots, labs)], lag_ratio=0.2), FadeIn(origin), run_time=1.6)
        self.wait(max(0.1, self.dur(0) * 0.5 - 1.6))
        hl = ring(pl.p(T4_E[cat]), 0.2, HOT, 3)
        self.play(ShowCreation(hl), run_time=0.6)

        # b1: a cloud centred at t E(cat), radius 1 - t
        self.at(1)
        eps = rng.normal(size=(260, 2))
        cloud = DotCloud(pl.p(0.5 * T4_E[cat] + 0.5 * eps), color=NOISE, radius=0.025, opacity=0.8)
        cloud.add_updater(lambda m: m.set_points(pl.p(t() * T4_E[cat] + (1 - t()) * eps)))
        h_cat = halo(pl.p(0.5 * T4_E[cat]), 0.5 * pl.u)
        h_cat.add_updater(lambda m: m.set_width(2 * (1 - t()) * pl.u).move_to(pl.p(t() * T4_E[cat])))
        ray = DashedLine(pl.p([0, 0]), pl.p(T4_E[cat]), dash_length=0.08).set_stroke(DIM, 1.5)
        cdot = Dot(radius=0.05).set_fill(NOISE, 1).set_stroke(width=0)
        cdot.add_updater(lambda m: m.move_to(pl.p(t() * T4_E[cat])))
        eq1 = M("X_t", "=", "t\\,E(\\mathrm{cat})", "+", "(1-t)\\,\\epsilon", colors={0: HOT, 2: DATA, 4: NOISE}, size=0.44).move_to(RIGHT * 3.9 + UP * 2.8)
        lik = M("X_t \\mid w", "\\sim", "\\mathcal{N}\\!\\left(t\\,E(w),\\ (1-t)^2 I\\right)", size=0.44).next_to(eq1, DOWN, buff=0.45)
        self.play(FadeOut(hl), FadeIn(eq1), ShowCreation(ray), run_time=0.8)
        self.add(h_cat, cloud, cdot)
        self.play(FadeIn(cloud), FadeIn(h_cat), FadeIn(cdot), run_time=0.8)
        self.wait(max(0.1, self.dur(1) * 0.5 - 1.6))
        self.play(FadeIn(lik), run_time=0.7)

        # b2: at t = 0 every token has the same cloud; they slide apart and shrink
        self.at(2)
        halos = VGroup()
        for i in range(4):
            if i == cat:
                continue
            hh = halo(pl.p(t() * T4_E[i]), (1 - t()) * pl.u, color=FG, fill=0.05, width=1.2)
            hh.add_updater((lambda i: (lambda m: m.set_width(2 * (1 - t()) * pl.u).move_to(pl.p(t() * T4_E[i]))))(i))
            halos.add(hh)
        self.add(halos)
        self.play(FadeIn(halos), cloud.animate.set_opacity(0.0), run_time=0.6)
        cloud.clear_updaters()
        self.remove(cloud)
        d = self.dur(2)
        self.play(self.clock.animate.set_value(0.0), run_time=d * 0.25)
        self.wait(d * 0.1)
        self.play(self.clock.animate.set_value(0.85), run_time=d * 0.45, rate_func=linear)

        # b3: go backward: we see z; which token made it? Bayes
        self.at(3)
        self.play(self.clock.animate.set_value(0.35), run_time=1.0)
        zfix = np.array([0.62, 0.45])
        z = Dot(pl.p(zfix), radius=0.1).set_fill(HOT, 1).set_stroke(FG, 1.5)
        zl = M("z", size=0.45, color=HOT).next_to(z, UR, buff=0.08)
        self.play(FadeIn(z, scale=2.5), FadeIn(zl), FadeOut(eq1), FadeOut(lik), FadeOut(ray), run_time=0.8)
        bayes = M("q_t(w \\mid z)", "\\propto", "\\pi(w)", "\\cdot", "\\mathcal{N}\\!\\left(z;\\ t\\,E(w),\\ (1-t)^2 I\\right)", colors={2: DATA}, size=0.46)
        fit(bayes, 6.2).move_to(RIGHT * 3.75 + UP * 2.9)
        self.wait(max(0.1, self.dur(3) * 0.5 - 1.8))
        self.play(FadeIn(bayes), run_time=0.8)

        # b4: the posterior is a softmax with these logits
        self.at(4)
        soft = M("q_t(w \\mid z)", "=", "\\mathrm{softmax}_w\\!\\left(\\log \\pi(w) - \\dfrac{\\|z - t\\,E(w)\\|^2}{2\\,(1-t)^2}\\right)", size=0.46)
        fit(soft, 6.2).move_to(RIGHT * 3.75 + UP * 1.75)
        dist = VGroup(*[Line(pl.p(zfix), pl.p(0.35 * T4_E[i])).set_stroke(HOT, 1.5, 0.8) for i in range(4)])
        dist.add_updater(lambda g: [ln.put_start_and_end_on(z.get_center(), pl.p(t() * T4_E[i])) for i, ln in enumerate(g)])
        bars = Bars(T4, world.post4(zfix, 0.35)[0], width=2.6, bar_h=0.26, gap=0.16, size=0.3).move_to(RIGHT * 3.7 + DOWN * 1.2)
        prior = VGroup(*[Line(UP * 0.2, DOWN * 0.2).set_stroke(DATA, 2.5).move_to(bars.rows[i][1].get_left() + RIGHT * T4_PI[i] * 2.6) for i in range(4)])
        pl_lab = Tx("prior", 0.22, DATA).next_to(prior[0], UP, buff=0.08)
        self.play(ShowCreation(dist), run_time=0.9)
        self.wait(max(0.1, self.dur(4) * 0.55 - 0.9))
        self.play(FadeIn(soft), run_time=0.8)
        self.play(FadeIn(bars), FadeIn(prior), FadeIn(pl_lab), run_time=0.7)

        # b5: the same point as time runs
        self.at(5)
        zpath_t = np.linspace(0.35, 0.97, 80)
        # a real one-position path: follow the exact flow from z at t = 0.35
        zz, path = zfix.copy(), [zfix.copy()]
        for a, b in zip(zpath_t[:-1], zpath_t[1:]):
            g = world.post4(zz, a)[0] @ T4_E
            zz = zz + (b - a) / (1 - a) * (g - zz)
            path.append(zz.copy())
        path = np.array(path)

        def zpos():
            return path[int(np.clip((t() - 0.35) / (0.97 - 0.35), 0, 1) * (len(path) - 1))] if t() >= 0.35 else zfix

        z.add_updater(lambda m: m.move_to(pl.p(zpos())))
        zl.add_updater(lambda m: m.next_to(z, UR, buff=0.08))
        bars.add_updater(lambda b: b.set_values(world.post4(zpos(), t())[0]))
        tb = TimeBar(self.clock, width=3.0).move_to(RIGHT * 3.7 + DOWN * 2.9)
        self.play(FadeIn(tb), run_time=0.4)
        self.play(self.clock.animate.set_value(0.97), run_time=self.left(6) - 0.6, rate_func=linear)

        # b6: the two limits
        self.at(6)
        d = self.dur(6)
        z.clear_updaters()
        z.add_updater(lambda m: m.move_to(pl.p(zfix * min(1.0, 0.2 + t()) if t() < 0.35 else zpos())))
        self.play(self.clock.animate.set_value(0.02), run_time=d * 0.3)
        self.wait(d * 0.2)
        self.play(self.clock.animate.set_value(0.97), run_time=d * 0.3)
        for m in (z, zl, bars, dist, halos, h_cat, cdot, tb.knob):
            m.clear_updaters()
        for hh in halos:
            hh.clear_updaters()
        self.finish()
