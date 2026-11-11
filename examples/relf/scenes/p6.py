"""Parts 6 and 7: the stochastic sampler, reflow, the model and results, the two loops complete, looped models."""
from common import *
from p5 import loop_arrow


def one_pos_paths(z0, steps=120):
    """Exact one-position flow over the four teaching tokens (prior T4_PI). Returns ts, paths (steps+1, N, 2)."""
    ts = np.linspace(0, 1, steps + 1)
    z = np.array(z0, float)
    out = [z.copy()]
    for a, b in zip(ts[:-1], ts[1:]):
        g = world.post4(z, min(a, 0.999)) @ T4_E
        z = z + (b - a) / (1 - a) * (g - z)
        out.append(z.copy())
    return ts, np.stack(out)


class S20(BeatScene):
    SID = "s20"

    def construct(self):
        rng = np.random.default_rng(20)
        pl = Plane2(center=LEFT * 4.3 + DOWN * 0.6, unit=2.3)
        dots, labs = token_dots(pl, T4_E, T4, side=[LEFT, DOWN, UP, RIGHT])
        t, N, sigma = 0.6, 64, 24.0
        h, b = 1.0 / 4, 1 - t       # a large step so the picture is readable
        z = t * T4_E[T4.index('dog')] + b * np.array([-1.3, 0.9])
        g = world.post4(z, t)[0] @ T4_E
        eps = (z - t * g) / b
        delta = min(sigma * (1 / N) * b, b)
        xi = np.array([0.2, -1.0])
        z_t = z - delta * eps + np.sqrt(b * b - (b - delta) ** 2) * xi
        z_new = z_t + (h / b) * (g - z_t)
        code = CodePanel(SAMPLE, size=0.17, line_gap=0.12).to_corner(UR, buff=0.35)
        code.lines.set_opacity(0.25)

        zd = Dot(pl.p(z), radius=0.1).set_fill(HOT, 1).set_stroke(FG, 1.5)
        zl = M("z", size=0.42, color=HOT).next_to(zd, LEFT, buff=0.12)
        gr = ring(pl.p(g), 0.14, BLUE, 4)
        gl = M("\\hat{x}", size=0.42, color=BLUE).next_to(gr, UP, buff=0.12)
        self.add(dots, labs)

        # b0: each step first puts fresh noise back in
        self.at(0)
        self.play(FadeIn(zd), FadeIn(zl), FadeIn(gr), FadeIn(gl), FadeIn(code), run_time=0.9)
        self.wait(max(0.1, self.dur(0) * 0.6 - 0.9))
        self.play(*code.hl(5), run_time=0.6)

        # b1: recover the noise the state contains: eps = (z - t xhat) / (1 - t)
        self.at(1)
        sig = Dot(pl.p(t * g), radius=0.06).set_fill(BLUE, 1).set_stroke(width=0)
        sl = M("t\\,\\hat{x}", size=0.36, color=BLUE).next_to(sig, DOWN, buff=0.1)
        nz = arrow(pl.p(t * g), pl.p(z), NOISE, 4, buff=0)
        nl = M("(1-t)\\,\\hat{\\epsilon}", size=0.36, color=NOISE).next_to(nz, UP, buff=0.12)
        e1 = M("\\hat{\\epsilon}", "=", "\\dfrac{z - t\\,\\hat{x}}{1-t}", colors={0: NOISE}, size=0.46)
        e2 = M("\\tilde{z}", "=", "z - \\delta\\,\\hat{\\epsilon}", "+", "\\sqrt{b^2 - (b-\\delta)^2}\\ \\xi", colors={0: HOT, 4: NOISE}, size=0.46)
        e3 = M("z_{\\mathrm{next}}", "=", "\\tilde{z} + \\dfrac{h}{b}\\,(\\hat{x} - \\tilde{z})", colors={0: HOT}, size=0.46)
        e4 = M("\\delta = \\min(\\sigma\\,h\\,b,\\ b)", ",\\quad b = 1 - t", size=0.4)
        lad = ladder(e1, e2, e3, e4, buff=0.4).move_to(RIGHT * 3.7 + DOWN * 0.7)
        fit(lad, 5.8)
        self.play(FadeIn(sig), FadeIn(sl), run_time=0.6)
        self.play(ShowCreation(nz), FadeIn(nl), FadeIn(e1), run_time=0.9)

        # b2: remove part of that noise and add fresh noise of the size removed: same noise level
        self.at(2)
        keep = arrow(pl.p(t * g), pl.p(t * g + (b - delta) * eps), NOISE, 4, buff=0)
        fresh = arrow(pl.p(t * g + (b - delta) * eps), pl.p(z_t), FG, 3, buff=0)
        fl = Tx("fresh noise", 0.22, FG).next_to(fresh, RIGHT, buff=0.1)
        zt = Dot(pl.p(z_t), radius=0.1).set_fill(HOT, 1).set_stroke(FG, 1.5)
        ztl = M("\\tilde{z}", size=0.42, color=HOT).next_to(zt, DOWN, buff=0.12)
        self.play(FadeOut(nl), Transform(nz, keep), zd.animate.set_opacity(0.3), zl.animate.set_opacity(0.3), run_time=0.9)
        self.wait(max(0.1, self.dur(2) * 0.4 - 0.9))
        self.play(ShowCreation(fresh), FadeIn(fl), FadeIn(zt), FadeIn(ztl), FadeIn(e2), run_time=1.0)

        # b3: then the usual step toward the same guess; delta = min(sigma h b, b)
        self.at(3)
        st = arrow(pl.p(z_t), pl.p(z_new), HOT, 5, buff=0)
        zn = Dot(pl.p(z_new), radius=0.1).set_fill(HOT, 1).set_stroke(FG, 1.5)
        self.play(ShowCreation(st), FadeIn(zn), FadeIn(e3), *code.hl(5, 6), run_time=1.0)
        self.wait(max(0.1, self.dur(3) * 0.5 - 1.0))
        self.play(FadeIn(e4), run_time=0.7)

        # b4: why: fresh noise lets later steps overwrite early mistakes; sigma = 0 is Euler; main results sigma = 24
        self.at(4)
        nums = VGroup(Tx("σ = 0:  the plain Euler step", 0.25, DIM),
                      Tx("σ = 24 (main results):  on an even grid of 64 steps,", 0.25, FG),
                      Tx(f"δ = {sigma / N:.3f} · (1 − t), about three eighths of the noise refreshed per step", 0.25, FG)).arrange(DOWN, buff=0.14, aligned_edge=LEFT)
        fit(nums, 7.5).to_corner(DL, buff=0.35)
        d = self.dur(4)
        self.wait(d * 0.55)
        self.play(FadeIn(nums[0]), run_time=0.7)
        self.wait(max(0.1, d * 0.75 - (self.time - self.start(4))))
        self.play(FadeIn(nums[1]), FadeIn(nums[2]), run_time=0.7)
        self.finish()


class S21(BeatScene):
    SID = "s21"

    def construct(self):
        rng = np.random.default_rng(21)
        pl = Plane2(center=LEFT * 3.3 + DOWN * 0.2, unit=1.75)
        dots, labs = token_dots(pl, T4_E, T4, side=[LEFT, DOWN, UP, RIGHT])
        z0 = rng.normal(size=(500, 2))
        ts, P1 = one_pos_paths(z0)
        z1 = P1[-1]
        pf = sims.PairFlow(z0, z1, bw=0.12)
        sel = rng.choice(np.where(np.abs(z0).max(1) < 1.7)[0], 26, replace=False)
        ts2, P2 = pf.integrate(z0[sel], steps=100)

        def near(P):
            return float(np.sqrt(((P[:, None] - T4_E[None]) ** 2).sum(-1)).min(1).mean())

        def euler1(zs, n):       # n-step Euler of the first flow
            tt = np.linspace(0, 1, n + 1)
            z = zs.copy()
            for a, b in zip(tt[:-1], tt[1:]):
                z = z + (b - a) / (1 - a) * (world.post4(z, min(a, 0.999)) @ T4_E - z)
            return z

        m1 = near(euler1(z0[:300], 2))
        m2 = near(pf.integrate(z0[:300], steps=2)[1][-1])

        # b0: the paths are curved, because early guesses are blends
        self.add(dots, labs)
        self.clock.set_value(0)
        pts = DotCloud(pl.p(z0[sel]), color=NOISE, radius=0.05)
        pts.add_updater(lambda m: m.set_points(pl.p(lerp_traj(P1[:, sel], self.clock.get_value()))))
        trails = VGroup(*[VMobject().set_stroke(HOT, 2, 0.85) for _ in sel])

        def upd_tr(gp):
            k = max(1, int(self.clock.get_value() * (len(P1) - 1)))
            for j, m in enumerate(gp):
                m.set_points_as_corners(pl.p(P1[: k + 1, sel[j]]))

        trails.add_updater(upd_tr)
        self.at(0)
        self.add(trails, pts)
        self.play(FadeIn(pts), run_time=0.5)
        self.play(self.clock.animate.set_value(1), run_time=self.dur(0) * 0.7, rate_func=linear)
        pts.clear_updaters(), trails.clear_updaters()
        cap1 = Tx("one position, four tokens: the paths of the trained flow", 0.24, DIM).next_to(pl.p([0, -1.9]), DOWN, buff=0.2)
        self.play(FadeIn(cap1), run_time=0.5)

        # b1: record which sentence each noise became (about 0.5M pairs, 256-step sampler)
        self.at(1)
        rows = Group()
        for r, sent in enumerate(["the cat sat on the mat", "a dog ran to the park", "the bird slept in the tree"]):
            nz = Heat(rng.normal(size=(2, 6)), cell=0.26, vmax=1.8)
            ar = arrow(ORIGIN, RIGHT * 0.9, FG, 2.5, buff=0)
            rows.add(Group(nz, ar, Tx(sent, 0.24, DATA)).arrange(RIGHT, buff=0.25))
        rows.arrange(DOWN, buff=0.35, aligned_edge=LEFT).move_to(RIGHT * 3.4 + UP * 1.6)
        l0 = M("Z_0", size=0.4, color=NOISE).next_to(rows[0][0], UP, buff=0.2)
        l1 = M("\\hat{w}", size=0.4, color=DATA).next_to(rows[0][2], UP, buff=0.2)
        facts = Tx("about 0.5 million pairs per round, from a 256-step sampler", 0.23, DIM).next_to(rows, DOWN, buff=0.35)
        fit(facts, 6.2)
        self.play(LaggedStart(*[FadeIn(r) for r in rows], lag_ratio=0.3), FadeIn(l0), FadeIn(l1), run_time=1.6)
        self.wait(max(0.1, self.dur(1) * 0.55 - 1.6))
        self.play(FadeIn(facts), run_time=0.6)

        # b2: same cross entropy loss, on paired data   [Eq. 10]
        self.at(2)
        eq10 = M("x_t", "=", "t\\,E(\\hat{w})", "+", "(1-t)\\,Z_0", colors={0: HOT, 2: DATA, 4: NOISE}, size=0.46)
        loss = M("\\mathcal{L}", "=", "\\mathrm{E}\\left[-\\log p_\\theta(\\hat{w} \\mid x_t,\\ t)\\right]", size=0.46)
        blk = ladder(eq10, loss, buff=0.35).next_to(facts, DOWN, buff=0.5)
        fit(blk, 6.2)
        tag = Tx("Eq. 10: the same loss; only the pairing is new", 0.23, DIM).next_to(blk, DOWN, buff=0.25)
        self.play(FadeIn(eq10), run_time=0.8)
        self.wait(max(0.1, self.dur(2) * 0.45 - 0.8))
        self.play(FadeIn(loss), FadeIn(tag), run_time=0.8)

        # b3: the retrained model follows straighter paths
        self.at(3)
        self.play(FadeOut(trails), FadeOut(pts), FadeOut(cap1), run_time=0.5)
        self.clock.set_value(0)
        pts2 = DotCloud(pl.p(z0[sel]), color=NOISE, radius=0.05)
        pts2.add_updater(lambda m: m.set_points(pl.p(lerp_traj(P2, self.clock.get_value()))))
        tr2 = VGroup(*[VMobject().set_stroke(DATA, 2, 0.9) for _ in sel])

        def upd_tr2(gp):
            k = max(1, int(self.clock.get_value() * (len(P2) - 1)))
            for j, m in enumerate(gp):
                m.set_points_as_corners(pl.p(P2[: k + 1, j]))

        tr2.add_updater(upd_tr2)
        self.add(tr2, pts2)
        self.play(self.clock.animate.set_value(1), run_time=self.dur(3) * 0.6, rate_func=linear)
        pts2.clear_updaters(), tr2.clear_updaters()
        cap2 = Tx(f"after reflow on the toy  ·  2-step sampler, mean miss: {m1:.2f} before, {m2:.2f} after", 0.23, DIM).next_to(pl.p([0, -1.9]), DOWN, buff=0.2)
        fit(cap2, 6.3)
        self.play(FadeIn(cap2), run_time=0.5)

        # b4: each round drifts from real data, so blend the weights back toward the original   [Eq. 11]
        self.at(4)
        self.play(*[FadeOut(m) for m in (rows, l0, l1, facts, blk, tag)], run_time=0.5)
        A, B = RIGHT * 1.2 + UP * 1.4, RIGHT * 6.2 + UP * 1.4
        line = Line(A, B).set_stroke(DIM, 2)
        da, db = Dot(A, radius=0.09).set_fill(FG, 1).set_stroke(width=0), Dot(B, radius=0.09).set_fill(FG, 1).set_stroke(width=0)
        la = VGroup(M("\\theta_0", size=0.46), Tx("original", 0.22, DIM)).arrange(DOWN, buff=0.12).next_to(da, UP, buff=0.2)
        lb = VGroup(M("\\hat{\\theta}_{k+1}", size=0.46), Tx("after reflow", 0.22, DIM)).arrange(DOWN, buff=0.12).next_to(db, UP, buff=0.2)
        knob = Dot(B, radius=0.13).set_fill(HOT, 1).set_stroke(width=0)
        eq11 = M("\\theta_{k+1}", "=", "\\lambda\\,\\theta_0", "+", "(1-\\lambda)\\,\\hat{\\theta}_{k+1}", colors={0: HOT}, size=0.46).move_to(RIGHT * 3.7 + DOWN * 0.3)
        lam = VGroup(Tx("round 1:  λ = 0.7", 0.26, FG), Tx("round 2:  λ = 0.55", 0.26, FG)).arrange(DOWN, buff=0.14, aligned_edge=LEFT).next_to(eq11, DOWN, buff=0.4)
        d = self.dur(4)
        self.wait(d * 0.3)
        self.play(ShowCreation(line), FadeIn(da), FadeIn(db), FadeIn(la), FadeIn(lb), FadeIn(knob), run_time=0.9)
        self.wait(max(0.1, d * 0.55 - (self.time - self.start(4))))
        self.play(knob.animate.move_to(interpolate(A, B, 0.3)), FadeIn(eq11), FadeIn(lam[0]), run_time=1.2)
        self.wait(max(0.1, d * 0.85 - (self.time - self.start(4))))
        self.play(knob.animate.move_to(interpolate(A, B, 0.45)), FadeIn(lam[1]), run_time=0.9)

        # b5: results by number of steps (Table 6, ReLF-Small after two rounds)
        self.at(5)
        self.play(*[FadeOut(m) for m in self.mobjects if m is not self.frame], run_time=0.5)
        vals = [116.4, 51.2, 26.4, 22.9, 27.7]
        ch = BarChart([f"{n} steps" for n in (4, 8, 16, 32)] + ["autoregressive\n1,023 steps"], vals, colors=[RED, "#bdbdbd", HOT, "#bdbdbd", FG], unit=0.036, bar_w=1.3, gap=0.7).move_to(DOWN * 0.5)
        cap = Tx("generative perplexity after two rounds of reflow  ·  ReLF-Small, entropy 5.41 to 5.43  ·  Table 6", 0.23, DIM).to_edge(UP, buff=0.5)
        drop = Tx("8 steps: 40%, 41%, 35% lower than before reflow (Small, Medium, Large)", 0.23, DIM).to_edge(DOWN, buff=0.4)
        self.play(FadeIn(ch.base), FadeIn(cap), run_time=0.6)
        d = self.dur(5)
        self.play(*ch.grow(1), FadeIn(drop), run_time=0.7)
        self.wait(max(0.1, d * 0.32 - 1.3))
        self.play(*ch.grow(2), *ch.grow(3), run_time=0.7)
        self.play(*ch.grow(4), run_time=0.7)
        self.wait(max(0.1, d * 0.7 - (self.time - self.start(5))))
        self.play(*ch.grow(0), run_time=0.7)
        self.finish()


class S22(BeatScene):
    SID = "s22"

    def construct(self):
        # b0: the network: a bidirectional diffusion transformer; three sizes
        inp = VGroup(Rectangle(1.5, 0.5).set_stroke(HOT, 2), Tx("z  (d)", 0.22, HOT))
        inc = VGroup(Rectangle(1.5, 0.5).set_stroke(BLUE, 2), Tx("C  (d)", 0.22, BLUE))
        VGroup(inp, inc).arrange(RIGHT, buff=0.0)
        ins = VGroup(inp, inc).move_to(LEFT * 3.6 + DOWN * 2.6)
        proj = VGroup(Rectangle(3.0, 0.5).set_stroke(FG, 1.5), Tx("linear projection", 0.22, FG)).move_to(LEFT * 3.6 + DOWN * 1.7)
        blocks = VGroup(*[VGroup(Rectangle(3.0, 0.55).set_stroke(FG, 2), Tx("attention (both directions) + MLP", 0.19, FG)) for _ in range(3)]).arrange(UP, buff=0.12).move_to(LEFT * 3.6 + DOWN * 0.15)
        times = Tx("× 12 / 24 / 32", 0.24, DIM).next_to(blocks, LEFT, buff=0.3)
        head = VGroup(Rectangle(3.0, 0.5).set_stroke(BLUE, 2), Tx("residual logits f  (V per position)", 0.19, BLUE)).move_to(LEFT * 3.6 + UP * 1.45)
        sing = VGroup(Rectangle(2.3, 0.5).set_stroke(HOT, 2), Tx("singular logits", 0.2, HOT)).move_to(LEFT * 0.4 + UP * 1.45)
        plus = Tx("+", 0.4, FG).move_to((head.get_right() + sing.get_left()) / 2)
        sm = Tx("softmax  →  p", 0.26, FG).move_to(LEFT * 2.4 + UP * 2.5)
        tcond = VGroup(Tx("t, ω", 0.26, FG), Tx("into the normalisation layers", 0.19, DIM)).arrange(DOWN, buff=0.08).move_to(LEFT * 0.2 + DOWN * 0.15)
        ta = arrow(tcond.get_left(), blocks.get_right(), DIM, 2, buff=0.12)
        arch = VGroup(ins, proj, blocks, times, head, sing, plus, sm, tcond, ta)
        sizes = VGroup()
        for name, par, lay, wid in [("Small", "138M", 12, "768"), ("Medium", "421M", 24, "1,056"), ("Large", "784M", 32, "1,280")]:
            sizes.add(VGroup(Tx(name, 0.28, FG), Tx(par, 0.28, HOT), Tx(f"{lay} layers, width {wid}", 0.22, DIM)).arrange(RIGHT, buff=0.3))
        sizes.arrange(DOWN, buff=0.3, aligned_edge=LEFT).move_to(RIGHT * 4.0 + UP * 1.6)
        self.at(0)
        self.play(FadeIn(arch), run_time=1.4)
        self.wait(max(0.1, self.dur(0) * 0.6 - 1.4))
        self.play(LaggedStart(*[FadeIn(s) for s in sizes], lag_ratio=0.3), run_time=1.5)

        # b1: training: 80,000 steps on OpenWebText, about a million tokens per step
        self.at(1)
        tr = VGroup(Tx("80,000 steps", 0.26, FG), Tx("1,024 sequences × 1,024 tokens per step", 0.24, DIM), Tx("OpenWebText", 0.24, DIM)).arrange(DOWN, buff=0.14, aligned_edge=LEFT).next_to(sizes, DOWN, buff=0.7, aligned_edge=LEFT)
        self.play(FadeIn(tr), run_time=0.9)

        # b2 + b3: the two metrics; the numbers
        self.at(2)
        self.play(FadeOut(arch), FadeOut(sizes), FadeOut(tr), run_time=0.6)
        plot = Plot(xr=(5.40, 5.54), yr=(14, 30), w=7.2, h=4.6, xlabel="entropy of the samples (variety)", xticks=(5.42, 5.46, 5.50), yticks=(15, 20, 25, 30)).move_to(LEFT * 1.6 + DOWN * 0.2)
        yl = Tx("generative perplexity (judge: GPT-2 Large), lower is better", 0.22, DIM).next_to(plot.yax.get_top(), UP, buff=0.2).shift(RIGHT * 2.3)
        self.play(FadeIn(plot), run_time=0.8)
        self.wait(max(0.1, self.dur(2) * 0.3 - 0.8))
        self.play(FadeIn(yl), run_time=0.6)
        real = VGroup(Dot(plot.p(5.49, 17.3), radius=0.11).set_fill(DATA, 1).set_stroke(width=0))
        real.add(Tx("real text  17.3", 0.22, DATA).next_to(real[0], DOWN, buff=0.12))
        self.wait(max(0.1, self.dur(2) * 0.75 - (self.time - self.start(2))))
        self.play(FadeIn(real), run_time=0.6)

        self.at(3)
        relf = [("S", 5.45, 24.1), ("M", 5.48, 18.6), ("L", 5.51, 17.3)]
        ar = [("S", 5.43, 27.7), ("M", 5.46, 22.3), ("L", 5.47, 20.2)]
        gr, ga = VGroup(), VGroup()
        for n, x, y in relf:
            dd = Dot(plot.p(x, y), radius=0.1).set_fill(HOT, 1).set_stroke(width=0)
            gr.add(VGroup(dd, Tx(f"{n}  {y}", 0.22, HOT).next_to(dd, RIGHT, buff=0.1)))
        for n, x, y in ar:
            dd = Square(0.18).set_fill("#bdbdbd", 1).set_stroke(width=0).move_to(plot.p(x, y))
            ga.add(VGroup(dd, Tx(f"{n}  {y}", 0.22, "#bdbdbd").next_to(dd, LEFT, buff=0.1)))
        leg = VGroup(Tx("● flow, 64 steps", 0.24, HOT), Tx("■ autoregressive, same size", 0.24, "#bdbdbd")).arrange(DOWN, buff=0.14, aligned_edge=LEFT).move_to(RIGHT * 4.6 + UP * 1.6)
        d = self.dur(3)
        self.play(LaggedStart(*[FadeIn(m) for m in gr], lag_ratio=0.4), FadeIn(leg[0]), run_time=d * 0.3)
        self.wait(max(0.1, d * 0.55 - (self.time - self.start(3))))
        self.play(LaggedStart(*[FadeIn(m) for m in ga], lag_ratio=0.4), FadeIn(leg[1]), run_time=d * 0.3)

        # b4: speed
        self.at(4)
        self.play(*[FadeOut(m) for m in (plot, yl, real, gr, ga, leg)], run_time=0.5)
        c1 = BarChart(["Small", "Medium", "Large"], [15.3, 17.7, 18.9], colors=[HOT] * 3, unit=0.16, bar_w=0.9, gap=0.4, fmt="{:.1f}×").move_to(LEFT * 3.2 + DOWN * 0.5)
        c2 = BarChart(["Small", "Medium", "Large"], [1.7, 2.6, 1.8], colors=["#bdbdbd"] * 3, unit=0.16, bar_w=0.9, gap=0.4, fmt="{:.1f}×").move_to(RIGHT * 3.2 + DOWN * 0.5)
        c2.shift(UP * (c1.base.get_center()[1] - c2.base.get_center()[1]))
        t1 = Tx("one sequence at a time", 0.26, HOT).next_to(c1, UP, buff=0.4)
        t2 = Tx("batches of 64", 0.26, "#bdbdbd").move_to(np.array([c2.get_center()[0], t1.get_center()[1], 0]))
        cap = Tx("speed-up over the same-size autoregressive model  ·  16 steps after reflow, 1,024 tokens", 0.23, DIM).to_edge(UP, buff=0.5)
        self.play(FadeIn(cap), FadeIn(c1.base), FadeIn(t1), run_time=0.6)
        self.play(*[a for i in range(3) for a in c1.grow(i)], run_time=0.9)
        self.wait(max(0.1, self.dur(4) * 0.72 - 1.5))
        self.play(FadeIn(c2.base), FadeIn(t2), *[a for i in range(3) for a in c2.grow(i)], run_time=0.9)

        # b5: two cautions from the paper
        self.at(5)
        self.play(*[FadeOut(m) for m in (c1, c2, t1, t2, cap)], run_time=0.5)
        ca = VGroup(Tx("unconditional generation only; the authors ask for richer benchmarks", 0.28, FG),
                    Tx("entropies are matched only approximately (5.43 to 5.51)", 0.28, FG)).arrange(DOWN, buff=0.5, aligned_edge=LEFT)
        self.play(FadeIn(ca[0]), run_time=0.7)
        self.wait(max(0.1, self.dur(5) * 0.7 - 0.7))
        self.play(FadeIn(ca[1]), run_time=0.7)
        self.finish()


class S23(BeatScene):
    SID = "s23"

    def construct(self):
        tr = CodePanel(TRAIN, size=0.23, line_gap=0.17)
        sa = CodePanel(SAMPLE, size=0.23, line_gap=0.17)
        lt, ls = Tx("training step", 0.26, DIM), Tx("sampling loop", 0.26, DIM)
        g = VGroup(lt, tr, ls, sa).arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        ls.shift(DOWN * 0.25), sa.shift(DOWN * 0.25)
        g.move_to(LEFT * 1.3)
        tr.lines.set_opacity(0.3), sa.lines.set_opacity(0.3)
        tags_t = ["part 1, part 4", "part 4: schedule", "part 1", "part 5: self-conditioning", "part 3: singular logits", "part 2, part 5: guidance"]
        tags_s = ["part 1", "", "part 3", "part 1: soft token", "part 2", "part 6: fresh noise", "part 2", "part 5"]
        tt = VGroup(*[Tx(s, 0.2, HOT).next_to(tr.lines[i], RIGHT, buff=0.4).set_x(5.6) for i, s in enumerate(tags_t)])
        ts_ = VGroup(*[(Tx(s, 0.2, HOT) if s else VGroup()).next_to(sa.lines[i], RIGHT, buff=0.4) for i, s in enumerate(tags_s)])
        for m in ts_:
            if len(m):
                m.set_x(5.6)
        self.at(0)
        self.play(FadeIn(g), run_time=1.0)

        # b1: the training step, line by line
        self.at(1)
        d = self.dur(1)
        for i, f in enumerate([0.06, 0.22, 0.38, 0.46, 0.68, 0.84]):
            self.wait(max(0.02, d * f - (self.time - self.start(1))))
            self.play(tr.lines[i].animate.set_opacity(1), FadeIn(tt[i]), run_time=0.4)

        # b2: the sampling loop, line by line
        self.at(2)
        d = self.dur(2)
        for i, f in enumerate([0.08, 0.2, 0.26, 0.42, 0.52, 0.68, 0.78, 0.9]):
            self.wait(max(0.02, d * f - (self.time - self.start(2))))
            self.play(sa.lines[i].animate.set_opacity(1), *([FadeIn(ts_[i])] if len(ts_[i]) else []), run_time=0.4)

        # b3: reflow changes no line
        self.at(3)
        rf = VGroup(Tx("reflow: no line changes", 0.28, DATA), Tx("x0 is paired with the sentence it produced, and N = 16", 0.24, DATA)).arrange(DOWN, buff=0.12, aligned_edge=LEFT).to_edge(DOWN, buff=0.3)
        self.play(FadeIn(rf), run_time=0.8)
        self.finish()


class S24(BeatScene):
    SID = "s24"

    def construct(self):
        # b0: what carries over to looped models, and what has to be decided
        self.at(0)
        ttl = Tx("what this becomes in a looped model", 0.44, FG)
        self.play(FadeIn(ttl), run_time=0.8)
        self.wait(max(0.1, self.left(1) - 1.4))
        self.play(FadeOut(ttl), run_time=0.5)

        # b1: the sampler as an architecture: one network, N applications, state (z, C, t)
        self.at(1)
        boxes = VGroup(*[ModelBox("network", w=1.7, h=0.9, size=0.24) for _ in range(4)]).arrange(RIGHT, buff=0.9).move_to(UP * 1.9)
        arrs = VGroup(*[arrow(boxes[i].get_right(), boxes[i + 1].get_left(), BLUE, 2.5, buff=0.08) for i in range(3)])
        sl = VGroup(*[M("(z_%d, C_%d)" % (i + 1, i + 1), size=0.28, color=BLUE).next_to(arrs[i], UP, buff=0.1) for i in range(3)])
        same = Tx("the same weights at every step", 0.24, DIM).next_to(boxes, DOWN, buff=0.3)
        self.play(LaggedStart(*[FadeIn(b) for b in boxes], lag_ratio=0.2), run_time=1.2)
        self.play(*[ShowCreation(a) for a in arrs], FadeIn(sl), FadeIn(same), run_time=1.0)
        nb = ModelBox("network", w=3.0, h=1.3, size=0.34).move_to(DOWN * 1.5)
        fb = loop_arrow(nb.get_right() + RIGHT * 0.1, nb.get_left() + LEFT * 0.1, bend=-2.4)
        st = M("\\mathrm{state:}\\ \\ (z,\\ C,\\ t)", size=0.42, color=BLUE).next_to(fb, DOWN, buff=0.2)
        self.wait(max(0.1, self.dur(1) * 0.6 - 2.2))
        self.play(FadeIn(nb), ShowCreation(fb), run_time=1.0)
        self.play(FadeIn(st), run_time=0.6)

        # b2: loop count = step index; each loop is one flow step
        self.at(2)
        self.play(FadeOut(boxes), FadeOut(arrs), FadeOut(sl), FadeOut(same), VGroup(nb, fb, st).animate.scale(0.8).move_to(LEFT * 4.7 + UP * 0.2), run_time=0.8)
        steps = VGroup(Tx("one loop = one flow step", 0.36, HOT),
                       Tx("1.  read the state", 0.32, FG), Tx("2.  output token probabilities", 0.32, FG), Tx("3.  move toward the soft token", 0.32, FG)).arrange(DOWN, buff=0.28, aligned_edge=LEFT).move_to(RIGHT * 1.6 + UP * 0.2)
        self.play(FadeIn(steps[0]), run_time=0.6)
        d = self.dur(2)
        for i, f in enumerate([0.5, 0.65, 0.8]):
            self.wait(max(0.05, d * f - (self.time - self.start(2))))
            self.play(FadeIn(steps[i + 1]), run_time=0.5)

        # b3: three things that make the loop well behaved
        self.at(3)
        self.play(FadeOut(steps), run_time=0.5)
        have = VGroup(
            VGroup(Tx("a target at every iteration", 0.28, DATA), Tx("cross entropy at every noise level, no backpropagation through the loop", 0.21, DIM)).arrange(DOWN, buff=0.08, aligned_edge=LEFT),
            VGroup(Tx("a reason to stop", 0.28, DATA), Tx("singular logits force commitment as t → 1", 0.21, DIM)).arrange(DOWN, buff=0.08, aligned_edge=LEFT),
            VGroup(Tx("fewer iterations", 0.28, DATA), Tx("reflow on the model's own (noise, text) pairs", 0.21, DIM)).arrange(DOWN, buff=0.08, aligned_edge=LEFT),
        ).arrange(DOWN, buff=0.5, aligned_edge=LEFT).scale(1.25).move_to(RIGHT * 1.9 + UP * 0.2)
        fit(have, 9.0)
        d = self.dur(3)
        for i, f in enumerate([0.18, 0.5, 0.78]):
            self.wait(max(0.05, d * f - (self.time - self.start(3))))
            self.play(FadeIn(have[i]), run_time=0.6)

        # b4: three open questions
        self.at(4)
        self.play(FadeOut(have), run_time=0.5)
        open_ = VGroup(
            VGroup(Tx("causal instead of bidirectional?", 0.28, HOT), Tx("then each position needs its own time", 0.21, DIM)).arrange(DOWN, buff=0.08, aligned_edge=LEFT),
            VGroup(Tx("singular logits with a time per position?", 0.28, HOT), Tx("still fine: they are computed one position at a time", 0.21, DIM)).arrange(DOWN, buff=0.08, aligned_edge=LEFT),
            VGroup(Tx("where does the flow state live?", 0.28, HOT), Tx("here: 32 numbers per token, not the hidden width", 0.21, DIM)).arrange(DOWN, buff=0.08, aligned_edge=LEFT),
        ).arrange(DOWN, buff=0.5, aligned_edge=LEFT).scale(1.25).move_to(RIGHT * 1.9 + UP * 0.2)
        fit(open_, 9.0)
        d = self.dur(4)
        for i, f in enumerate([0.15, 0.52, 0.8]):
            self.wait(max(0.05, d * f - (self.time - self.start(4))))
            self.play(FadeIn(open_[i]), run_time=0.6)

        # b5: design questions, not results
        self.at(5)
        self.wait(self.dur(5) * 0.5)
        self.finish()
