"""Straight lines and the average: the line, the velocity, the check, and the training loop."""
from common import *

T0, X_HERE = 0.5, 0.3
G_HERE = float(world.guess1(X_HERE, T0))                 # 0.54
V_HERE = (G_HERE - X_HERE) / (1 - T0)                    # 0.47


def through(n_max=26, tol=0.05):
    """Random pairs whose straight line passes (nearly) through the place where we stand."""
    xt_ = T0 * W.x1_random + (1 - T0) * W.x0
    idx = np.where(np.abs(xt_ - X_HERE) < tol)[0][:n_max]
    return W.x0[idx], W.x1_random[idx]


class S05(BeatScene):
    SID = "s05"

    def construct(self):
        self.chapter("2", "straight lines and the average")
        xt = XT()
        ax = xt.axes()
        a, b = -1.3, 1.0
        self.play(FadeIn(ax), run_time=0.15)

        # b1: pick a noise number, pick a data number, stand a fraction t of the way between them
        self.at(1)
        d0 = Dot(xt.p(0, a), radius=0.1).set_fill(NOISE, 1).set_stroke(width=0)
        d1 = Dot(xt.p(1, b), radius=0.12).set_fill(DATA, 1).set_stroke(FG, 1.5)
        l0 = M("x_0", size=0.5, color=NOISE).next_to(d0, LEFT, buff=0.2)
        l1 = M("x_1", size=0.5, color=DATA).next_to(d1, RIGHT, buff=0.75)
        d = self.dur(1)
        self.play(FadeIn(d0, scale=2), FadeIn(l0), run_time=0.6)
        self.wait(max(0.1, d * 0.2 - 0.6))
        self.play(FadeIn(d1, scale=2), FadeIn(l1), run_time=0.6)
        line = Line(xt.p(0, a), xt.p(1, b)).set_stroke(FG, 2.5)
        self.wait(max(0.1, d * 0.38 - (self.time - self.start(1))))
        self.play(ShowCreation(line), run_time=0.9)
        self.clock.set_value(0.0)
        trav = Dot(radius=0.12).set_fill(HOT, 1).set_stroke(width=0)
        trav.add_updater(lambda m: m.move_to(xt.p(self.clock.get_value(), self.clock.get_value() * b + (1 - self.clock.get_value()) * a)))
        tick = always_redraw(lambda: DashedLine(xt.p(self.clock.get_value(), -3), trav.get_center(), dash_length=0.08).set_stroke(HOT, 1.5, 0.7))
        tl = Tx("t", 0.34, HOT)
        tl.add_updater(lambda m: m.next_to(xt.p(self.clock.get_value(), -3), DOWN, buff=0.12))
        self.add(tick, trav, tl)
        self.play(self.clock.animate.set_value(0.35), run_time=1.2)
        formula = M("x_t", "=", "t", "\\,x_1", "+", "(1-t)", "\\,x_0", colors={0: HOT, 2: HOT, 3: DATA, 5: HOT, 6: NOISE}, size=0.6)
        place(formula, Stage.title)
        self.wait(max(0.1, d * 0.72 - (self.time - self.start(1))))
        self.play(FadeIn(formula), run_time=0.7)

        # b2: time 0 = the noise, time 1 = the data, halfway = the midpoint
        self.at(2)
        d = self.dur(2)
        self.play(self.clock.animate.set_value(0.0), run_time=d * 0.2)
        self.wait(d * 0.12)
        self.play(self.clock.animate.set_value(1.0), run_time=d * 0.25)
        self.wait(d * 0.1)
        self.play(self.clock.animate.set_value(0.5), run_time=d * 0.2)

        # b3: thousands of random pairs: the bell at time 0, the data at time 1, a smooth change between
        self.at(3)
        tick.clear_updaters(), trav.clear_updaters(), tl.clear_updaters()
        self.play(*[FadeOut(m) for m in (tick, trav, tl, d0, d1, l0, l1, line)], run_time=0.6)
        n = 140
        x0, x1 = W.x0[:n], W.x1_random[:n]
        lines = segments(xt.P(0, x0), xt.P(1, x1), FG, 1.1, 0.22)
        self.clock.set_value(0.0)
        N = 4000
        X0, X1 = W.x0[:N], W.x1_random[:N]
        hist = live_hist(xt, lambda: (self.clock.get_value() * X1 + (1 - self.clock.get_value()) * X0, self.clock.get_value()), scale=1.3, color=HOT, opacity=0.8)
        self.play(ShowCreation(lines), run_time=1.6)
        self.add(hist)
        d = self.dur(3)
        self.wait(max(0.1, d * 0.3 - 1.6))
        self.play(self.clock.animate.set_value(1.0), run_time=d * 0.5, rate_func=smooth)

        # b4: so are we done?
        self.at(4)
        self.play(self.clock.animate.set_value(0.0), run_time=self.dur(4) * 0.3, rate_func=smooth)
        self.play(self.clock.animate.set_value(1.0), run_time=self.dur(4) * 0.3, rate_func=smooth)
        hist.clear_updaters()
        q = Tx("so are we done?", 0.4, HOT)
        place(q, Stage.foot)
        self.play(FadeOut(formula), FadeIn(q.move_to(np.array([0, 3.4, 0]))), run_time=0.6)
        self.finish()


class S06(BeatScene):
    SID = "s06"

    def construct(self):
        xt = XT()
        ax = xt.axes()
        n = 140
        lines = segments(xt.P(0, W.x0[:n]), xt.P(1, W.x1_random[:n]), FG, 1.1, 0.22)
        self.add(ax, lines)

        # b0: to walk a line you must know where it ends; the end is what we are looking for
        self.at(0)
        a, b = -0.9, 1.0
        me = Dot(xt.p(0, a), radius=0.11).set_fill(HOT, 1).set_stroke(width=0)
        mine = Line(xt.p(0, a), xt.p(1, b)).set_stroke(HOT, 2.5)
        self.play(FadeIn(me, scale=2), run_time=0.5)
        self.play(ShowCreation(mine), run_time=1.0)
        cover = Rectangle(1.1, xt.half * 2 + 0.3).set_stroke(RED, 2).set_fill(BG, 0.92).move_to(xt.p(1, 0) + RIGHT * 0.15)
        qm = Tx("?", 0.8, RED).move_to(cover)
        self.wait(max(0.1, self.dur(0) * 0.5 - 1.5))
        self.play(FadeIn(cover), FadeIn(qm), mine.animate.set_stroke(opacity=0.25), run_time=0.8)

        # b1: stand at one place, at one time: lines pass through in both directions
        self.at(1)
        self.play(FadeOut(cover), FadeOut(qm), FadeOut(me), FadeOut(mine), lines.animate.set_stroke(opacity=0.08), run_time=0.7)
        here = Dot(xt.p(T0, X_HERE), radius=0.12).set_fill(HOT, 1).set_stroke(FG, 1.5)
        hl = Tx("you are here:  0.3,  halfway", 0.3, HOT).next_to(here, UP, buff=0.3)
        self.play(FadeIn(here, scale=2), FadeIn(hl), run_time=0.6)
        p0, p1 = through()
        up, dn = p1 > 0, p1 < 0
        g_up = segments(xt.P(0, p0[up]), xt.P(1, p1[up]), DATA, 1.8, 0.75)
        g_dn = segments(xt.P(0, p0[dn]), xt.P(1, p1[dn]), BLUE, 1.8, 0.75)
        d = self.dur(1)
        self.wait(max(0.1, d * 0.5 - 0.6))
        self.play(FadeOut(hl), ShowCreation(g_up), run_time=1.0)
        self.wait(max(0.1, d * 0.75 - (self.time - self.start(1))))
        self.play(ShowCreation(g_dn), run_time=1.0)
        self.add(here)

        # b2: you cannot tell which line you are on: pause and decide
        self.at(2)
        pause = place(Tx("which way would you go?  pause, and decide", 0.36, HOT), Stage.title)
        self.wait(self.dur(2) * 0.35)
        self.play(FadeIn(pause), run_time=0.5)

        # b3: head for the average destination: the guess, 0.54
        self.at(3)
        self.play(FadeOut(pause), run_time=0.4)
        share = VGroup(Tx(f"{100 * up.mean():.0f}% of these lines go up", 0.3, DATA), Tx(f"{100 * dn.mean():.0f}% go down", 0.3, BLUE)).arrange(DOWN, buff=0.15, aligned_edge=LEFT)
        share.next_to(xt.p(1, 0), RIGHT, buff=0.45)
        fit(share, 1.6)
        gr = ring(xt.p(1, G_HERE), 0.17, HOT, 4)
        gl = Tx(f"guess {G_HERE:.2f}", 0.32, HOT).next_to(gr, RIGHT, buff=0.18)
        d = self.dur(3)
        self.wait(d * 0.25)
        self.play(ShowCreation(gr), run_time=0.7)
        self.wait(max(0.1, d * 0.55 - (self.time - self.start(3))))
        self.play(FadeIn(gl), run_time=0.5)

        # b4: point at the guess, fast enough to arrive on time: the velocity
        self.at(4)
        self.play(g_up.animate.set_stroke(opacity=0.2), g_dn.animate.set_stroke(opacity=0.2), run_time=0.5)
        aim = DashedLine(xt.p(T0, X_HERE), xt.p(1, G_HERE), dash_length=0.1).set_stroke(HOT, 2)
        vel = arrow(xt.p(T0, X_HERE), xt.p(T0 + 0.22, X_HERE + 0.22 * V_HERE), HOT, 6, buff=0, tip=0.26)
        self.play(ShowCreation(aim), run_time=0.7)
        self.play(ShowCreation(vel), run_time=0.6)
        self.add(here)
        f1 = M("\\mathrm{velocity}", "=", "\\dfrac{\\mathrm{guess} - x}{1 - t}", colors={0: HOT}, size=0.62)
        place(f1, HEAD)
        self.wait(max(0.1, self.dur(4) * 0.6 - (self.time - self.start(4))))
        self.play(FadeIn(f1), run_time=0.7)

        # b5: with numbers
        self.at(5)
        f2 = M("\\mathrm{velocity}", "=", "\\dfrac{0.54 - 0.30}{0.5}", "=", f"{V_HERE:.2f}", colors={0: HOT, 4: HOT}, size=0.62)
        place(f2, HEAD)
        self.wait(self.dur(5) * 0.25)
        self.play(FadeOut(f1), FadeIn(f2), run_time=0.7)

        # b6: a step of 1/8 with 1/2 left covers a quarter of the way to the guess; then guess again
        self.at(6)
        h = 0.125
        x_new = X_HERE + h * V_HERE
        g_new = float(world.guess1(x_new, T0 + h))
        f3 = Tx("a step of 1/8, with 1/2 of the time left   =   1/4 of the way to the guess", 0.36, FG)
        place(f3, Stage.title)
        self.play(FadeOut(f2), FadeIn(f3), FadeOut(gl), run_time=0.7)
        trail = Line(xt.p(T0, X_HERE), xt.p(T0 + h, x_new)).set_stroke(HOT, 5)
        d = self.dur(6)
        self.wait(max(0.1, d * 0.3 - 0.7))
        self.play(ShowCreation(trail), here.animate.move_to(xt.p(T0 + h, x_new)), FadeOut(vel), run_time=1.0)
        quarter = Tx("one quarter of the way", 0.3, HOT).next_to(xt.p(T0 + h, x_new), DOWN, buff=0.35)
        self.play(FadeIn(quarter), run_time=0.5)
        self.wait(max(0.1, d * 0.8 - (self.time - self.start(6))))
        aim2 = DashedLine(xt.p(T0 + h, x_new), xt.p(1, g_new), dash_length=0.1).set_stroke(HOT, 2)
        gl2 = Tx(f"new guess {g_new:.2f}", 0.32, HOT).next_to(xt.p(1, g_new), UL, buff=0.2)
        self.play(FadeOut(aim), FadeIn(aim2), gr.animate.move_to(xt.p(1, g_new)), FadeIn(gl2), FadeOut(quarter), run_time=0.8)
        self.finish()


class S07(BeatScene):
    SID = "s07"

    def construct(self):
        xt = XT()
        ax = xt.axes()
        self.add(ax)
        ts, FP = W.ts1, W.flow_paths
        full = world.flow1(W.x0, 200)[1]                         # (201, 10000): every point of the big run

        # b0: the objection: half up, half down, follow the average: surely the middle?
        self.at(0)
        ups = segments(xt.P(0, [-1.8, -1.0, -0.2, 0.6]), xt.P(1, [1, 1, 1, 1]), DATA, 1.8, 0.7)
        dns = segments(xt.P(0, [1.8, 1.0, 0.2, -0.6]), xt.P(1, [-1, -1, -1, -1]), BLUE, 1.8, 0.7)
        self.play(ShowCreation(ups), ShowCreation(dns), run_time=1.2)
        mid = arrow(xt.p(0.06, 0), xt.p(0.92, 0), RED, 5, buff=0, tip=0.26)
        ml = Tx("the middle?", 0.36, RED).next_to(xt.p(1, 0), RIGHT, buff=0.3)
        self.wait(max(0.1, self.dur(0) * 0.6 - 1.2))
        self.play(ShowCreation(mid), FadeIn(ml), run_time=0.8)

        # b1: run it: 10,000 points, 200 small steps, no randomness
        self.at(1)
        self.play(*[FadeOut(m) for m in (ups, dns, mid, ml)], run_time=0.5)
        run = place(Tx("10,000 points   ·   200 small steps   ·   no randomness", 0.34, FG), Stage.title)
        self.play(FadeIn(run), run_time=0.6)
        self.clock.set_value(0)
        idx = np.arange(0, 400, 4)
        trails = VGroup(*[VMobject().set_stroke(HOT, 1.3, 0.5) for _ in idx])

        def upd_tr(g):
            k = max(1, int(self.clock.get_value() * (len(ts) - 1)))
            for m, i in zip(g, idx):
                m.set_points_as_corners(xt.P(ts[: k + 1], FP[: k + 1, i]))

        trails.add_updater(upd_tr)
        cr = DotCloud(xt.P(0.0, W.x0[:400]), color=FG, radius=0.04)
        cr.add_updater(lambda m: m.set_points(xt.P(self.clock.get_value(), lerp_traj(FP, self.clock.get_value()))))
        self.add(trails, cr)
        self.play(self.clock.animate.set_value(1), run_time=self.left(2) - 0.3, rate_func=linear)
        trails.clear_updaters(), cr.clear_updaters()

        # b2: two sharp spikes: 51% on top, 49% below, nobody in the middle
        self.at(2)
        he = xt.hist(W.flow_end, 1, direction=1, scale=0.55, color=HOT)
        pu = 100 * (W.flow_end > 0).mean()
        s_up = Tx(f"{pu:.0f}%", 0.36, FG).next_to(xt.p(1, 1), RIGHT, buff=1.05)
        s_dn = Tx(f"{100 - pu:.0f}%", 0.36, FG).next_to(xt.p(1, -1), RIGHT, buff=1.05)
        self.play(FadeIn(he), FadeOut(cr), run_time=0.7)
        self.play(FadeIn(s_up), FadeIn(s_dn), run_time=0.5)
        none = Tx("0%", 0.36, RED).next_to(xt.p(1, 0), RIGHT, buff=0.3)
        self.wait(max(0.1, self.dur(2) * 0.75 - 1.2))
        self.play(FadeIn(none), run_time=0.5)

        # b3: why: the guess does not stay in the middle: follow one point and its guess
        self.at(3)
        self.play(FadeOut(run), FadeOut(none), trails.animate.set_stroke(opacity=0.12), run_time=0.5)
        j = int(np.argmin(np.abs(W.x0[:400] - 0.12)))
        self.clock.set_value(0)
        one = VMobject().set_stroke(HOT, 3.5)
        one.add_updater(lambda m: m.set_points_as_corners(xt.P(ts[: max(1, int(self.clock.get_value() * 200)) + 1], FP[: max(1, int(self.clock.get_value() * 200)) + 1, j])))
        head = Dot(radius=0.1).set_fill(FG, 1).set_stroke(width=0)
        gr = ring(xt.p(1, 0), 0.17, BLUE, 4)

        def upd_head(m):
            t = self.clock.get_value()
            x = float(lerp_traj(FP[:, j], t))
            m.move_to(xt.p(t, x))
            gr.move_to(xt.p(1, float(world.guess1(x, min(t, 0.995)))))

        head.add_updater(upd_head)
        aim = always_redraw(lambda: DashedLine(head.get_center(), gr.get_center(), dash_length=0.1).set_stroke(BLUE, 1.5))
        gl = Tx("its guess", 0.3, BLUE)
        gl.add_updater(lambda m: m.next_to(gr, LEFT, buff=0.2).shift(UP * 0.3))
        self.add(one, aim, head, gr, gl)
        self.play(self.clock.animate.set_value(1.0), run_time=self.dur(3) * 0.8, rate_func=linear)
        for m in (one, head, gl):
            m.clear_updaters()
        aim.clear_updaters()

        # b4: freeze both crowds at the same time: same shape, at every moment
        self.at(4)
        self.play(*[FadeOut(m) for m in (one, head, gr, gl, aim, he, s_up, s_dn, trails)], run_time=0.6)
        self.clock.set_value(0.25)
        N = 10_000
        on_lines = live_hist(xt, lambda: (self.clock.get_value() * W.x1_random[:N] + (1 - self.clock.get_value()) * W.x0[:N], self.clock.get_value()), direction=-1, scale=1.2, color=FG, opacity=0.8)
        on_flow = live_hist(xt, lambda: (lerp_traj(full, self.clock.get_value()), self.clock.get_value()), direction=1, scale=1.2, color=HOT, opacity=0.8)
        leg = VGroup(Tx("travelers on their straight lines", 0.3, FG), Tx("points following the guess", 0.3, HOT)).arrange(RIGHT, buff=1.2)
        place(leg, Stage.title)
        self.play(FadeIn(on_lines), FadeIn(on_flow), FadeIn(leg), run_time=0.8)
        d = self.dur(4)
        self.wait(max(0.1, d * 0.45 - 0.8))
        self.play(self.clock.animate.set_value(0.9), run_time=d * 0.3, rate_func=smooth)
        self.play(self.clock.animate.set_value(0.5), run_time=d * 0.15, rate_func=smooth)

        # b5: each point takes a different route than its line did; the crowd cannot tell
        self.at(5)
        k = int(np.argmax((W.x0[:400] > 0.5) & (W.x0[:400] < 0.7) & (W.x1_random[:400] < 0)))
        straight = Line(xt.p(0, W.x0[k]), xt.p(1, W.x1_random[k])).set_stroke(FG, 3)
        curved = VMobject().set_points_as_corners(xt.P(ts, FP[:, k])).set_stroke(HOT, 3)
        start = Dot(xt.p(0, W.x0[k]), radius=0.1).set_fill(NOISE, 1).set_stroke(width=0)
        self.play(on_lines.animate.set_opacity(0.25), on_flow.animate.set_opacity(0.25), FadeIn(start), run_time=0.5)
        on_lines.clear_updaters(), on_flow.clear_updaters()
        self.play(ShowCreation(straight), run_time=0.9)
        self.play(ShowCreation(curved), run_time=0.9)
        note = Tx("a theorem (not proved here): the two crowds match at every time", 0.32, FG)
        place(note, Stage.title)
        self.wait(max(0.1, self.dur(5) * 0.6 - 2.3))
        self.play(FadeOut(leg), FadeIn(note), run_time=0.6)
        self.finish()


class S08(BeatScene):
    SID = "s08"

    def construct(self):
        rng = np.random.default_rng(8)
        xt = XT(zone=Stage.left, pad=0.75)
        ax = xt.axes()
        self.add(ax)
        here = Dot(xt.p(T0, X_HERE), radius=0.11).set_fill(HOT, 1).set_stroke(FG, 1.5)

        # b0: we used a formula; a real model must learn an average it never sees
        self.at(0)
        formula = M("\\mathrm{guess}", "=", "\\tanh\\!\\left(\\dfrac{t\\,x}{(1-t)^2}\\right)", colors={0: BLUE}, size=0.5)
        place(formula, Stage.right)
        self.play(FadeIn(formula), run_time=0.7)
        cross = Line(formula.get_corner(DL), formula.get_corner(UR)).set_stroke(RED, 4)
        note = Tx("only in a tiny world", 0.32, RED).next_to(formula, DOWN, buff=0.4)
        self.wait(max(0.1, self.dur(0) * 0.45 - 0.7))
        self.play(ShowCreation(cross), FadeIn(note), run_time=0.7)

        # b1: one random pair, a random time, a point on their line; nudge the answer toward the real end
        self.at(1)
        box = ModelBox("network", w=2.4, h=1.0, size=0.34)
        net = VGroup(Tx("a point, and the time", 0.32, HOT), arrow(ORIGIN, DOWN * 0.7, FG, 2.5, buff=0), box,
                     arrow(ORIGIN, DOWN * 0.7, FG, 2.5, buff=0), Tx("the guess?", 0.32, BLUE)).arrange(DOWN, buff=0.22)
        place(net, Stage.right_narrow)
        self.play(FadeOut(formula), FadeOut(cross), FadeOut(note), FadeIn(net), run_time=0.7)
        ans = ring(xt.p(1, -0.25), 0.17, BLUE, 4)
        al = Tx("its answer", 0.3, BLUE)
        al.add_updater(lambda m: m.next_to(ans, RIGHT, buff=0.2))
        a0 = (X_HERE - T0 * 1.0) / (1 - T0)
        pair = Line(xt.p(0, a0), xt.p(1, 1)).set_stroke(DATA, 2.5)
        d = self.dur(1)
        self.play(ShowCreation(pair), run_time=0.8)
        self.play(FadeIn(here, scale=2), run_time=0.4)
        self.wait(max(0.1, d * 0.5 - (self.time - self.start(1))))
        self.play(FadeIn(ans), FadeIn(al), run_time=0.5)
        self.wait(max(0.1, d * 0.75 - (self.time - self.start(1))))
        val = -0.25
        val += 0.3 * (1 - val)
        nudge = arrow(ans.get_center() + UP * 0.2, xt.p(1, val) + UP * 0.05, HOT, 4, buff=0, tip=0.2).shift(LEFT * 0.35)
        self.play(ShowCreation(nudge), ans.animate.move_to(xt.p(1, val)), run_time=0.8)

        # b2: other pairs through the same spot pull other ways; it settles at the average
        self.at(2)
        self.play(FadeOut(nudge), FadeOut(pair), run_time=0.3)
        d = self.dur(2)
        n_pull = 22
        per = d * 0.62 / n_pull
        ends = np.where(rng.random(n_pull) < (1 + G_HERE) / 2, 1.0, -1.0)
        ends[0], ends[1] = -1.0, 1.0
        lr = np.linspace(0.3, 0.06, n_pull)
        for e, r in zip(ends, lr):
            s0 = (X_HERE - T0 * e) / (1 - T0)
            ln = Line(xt.p(0, s0), xt.p(1, e)).set_stroke(DATA if e > 0 else BLUE, 2.2, 0.85)
            val += r * (e - val)
            self.add(ln, here)
            self.play(ans.animate.move_to(xt.p(1, val)), run_time=per * 0.7)
            self.play(ln.animate.set_stroke(opacity=0.12), run_time=per * 0.3)
        avg = DashedLine(xt.p(0.72, G_HERE), xt.p(1, G_HERE), dash_length=0.08).set_stroke(HOT, 2)
        avl = Tx(f"the average: {G_HERE:.2f}", 0.32, HOT).next_to(xt.p(1, G_HERE), RIGHT, buff=0.3)
        al.clear_updaters()
        self.play(ans.animate.move_to(xt.p(1, G_HERE)), ShowCreation(avg), FadeOut(al), FadeIn(avl), run_time=0.7)

        # b3: this loop is flow matching: four lines
        self.at(3)
        al.clear_updaters()
        title = concept_title("flow matching")
        code = CodePanel(FM_CODE, size=0.27)
        place(code, Stage.right)
        self.play(FadeOut(net), FadeOut(avl), FadeIn(code), FadeIn(title), run_time=0.8)
        d = self.dur(3)
        for i in range(4):
            self.play(*code.hl(i), run_time=0.35)
            self.wait(max(0.05, d * 0.14 - 0.35))
        self.play(*code.hl(), run_time=0.4)

        # b4: compared with diffusion; the two things on the table
        self.at(4)
        comp = VGroup(Tx("the same guesser", 0.34, FG), Tx("straight training lines", 0.34, DATA), Tx("no randomness in the sampler", 0.34, HOT)).arrange(DOWN, buff=0.22, aligned_edge=LEFT)
        comp.next_to(code, DOWN, buff=0.6).align_to(code, LEFT)
        d = self.dur(4)
        for c_, f in zip(comp, (0.12, 0.22, 0.34)):
            self.wait(max(0.05, d * f - (self.time - self.start(4))))
            self.play(FadeIn(c_), run_time=0.4)
        two = VGroup(Tx("1.  the guess", 0.5, BLUE), Tx("2.  step toward it", 0.5, HOT)).arrange(DOWN, buff=0.35, aligned_edge=LEFT)
        place(two, Stage.right)
        self.wait(max(0.05, d * 0.6 - (self.time - self.start(4))))
        self.play(FadeOut(code), FadeOut(comp), FadeOut(title), FadeIn(two[0]), run_time=0.6)
        self.wait(max(0.05, d * 0.8 - (self.time - self.start(4))))
        self.play(FadeIn(two[1]), run_time=0.5)
        self.finish()
