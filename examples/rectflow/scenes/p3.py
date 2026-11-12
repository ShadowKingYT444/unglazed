"""Rectified flow: why one step fails, what the flow did to the pairs, reflow, and what it costs."""
from common import *

T0, X_HERE = 0.5, 0.3


def miss(n):
    return float(np.abs(np.abs(W.few[n]) - 1).mean())


def town(point, color=DATA, s=0.2):
    body = Square(s).set_stroke(color, 2).set_fill(BG, 1).move_to(point)
    roof = Polygon(body.get_corner(UL) + LEFT * 0.05, body.get_corner(UR) + RIGHT * 0.05, body.get_top() + UP * s * 0.7).set_stroke(color, 2).set_fill(BG, 1)
    return VGroup(body, roof)


class S09(BeatScene):
    SID = "s09"

    def construct(self):
        num, ttl = Tx("3.", 0.5).move_to(UP * 0.75), Tx("rectified flow", 0.62).move_to(DOWN * 0.45)
        self.play(FadeIn(num), FadeIn(ttl), run_time=0.8)
        self.wait(2.4)
        self.play(FadeOut(num), FadeOut(ttl), run_time=0.6)
        xt = XT(zone=Stage.left_wide, pad=1.0)
        ax = xt.axes()
        n = 400
        crowd = xt.crowd(W.x0[:n], 0.0)
        self.play(FadeIn(ax), FadeIn(crowd), run_time=0.7)

        # b0 (after the card): one giant step from time 0 to time 1. Decide before I show you
        giant = arrow(xt.p(0.04, -2.6), xt.p(0.96, -2.6), HOT, 5, buff=0, tip=0.26)
        gl = Tx("one giant step", 0.34, HOT).next_to(giant, UP, buff=0.12)
        d = self.dur(0)
        self.wait(max(0.1, self.start(0) + d * 0.55 - self.time))
        self.play(ShowCreation(giant), FadeIn(gl), run_time=0.9)
        ask = Tx("where do the points land?", 0.36, HOT)
        place(ask, Stage.right_narrow)
        self.wait(max(0.1, self.start(0) + d * 0.8 - self.time))
        self.play(FadeIn(ask), run_time=0.5)

        # b1: every point lands on zero
        self.at(1)
        self.play(FadeOut(ask), run_time=0.3)
        idx = np.arange(0, n, 3)
        lines = growing_segments(xt.P(0, W.x0[idx]), xt.P(1, W.few[1][idx]), self.clock, HOT, 1.3, 0.5)
        self.clock.set_value(0)
        self.add(lines)
        self.play(self.clock.animate.set_value(1), run_time=1.6)
        lines.clear_updaters()
        he = xt.hist(W.few[1], 1, direction=1, scale=0.55, color=RED)
        zl = VGroup(Tx("10,000 points", 0.34, RED), Tx("all on 0", 0.44, RED), Tx("which is not in the data", 0.3, DIM)).arrange(DOWN, buff=0.2)
        place(zl, Stage.right_narrow)
        self.play(FadeIn(he), FadeIn(zl[0]), FadeIn(zl[1]), run_time=0.7)
        self.wait(max(0.1, self.dur(1) * 0.7 - 2.6))
        self.play(FadeIn(zl[2]), run_time=0.5)

        # b2: why: at time 0 the guess is flat, zero everywhere. One step lands on the first guess
        self.at(2)
        self.play(FadeOut(zl), run_time=0.4)
        self.clock.set_value(0.0)
        gp = guess_plot(Stage.right_narrow, self.clock)
        gt = Tx("the guess at time 0", 0.32, BLUE).next_to(gp, UP, buff=0.3)
        self.play(FadeIn(gp), FadeIn(gt), run_time=0.8)
        flat = Tx("flat: zero everywhere", 0.3, BLUE).next_to(gp, DOWN, buff=0.3)
        d = self.dur(2)
        self.wait(max(0.1, d * 0.3 - 0.8))
        self.play(FadeIn(flat), run_time=0.5)
        blur = Tx("the first guess is the average of everything", 0.3, HOT)
        place(blur, Stage.title)
        self.wait(max(0.1, d * 0.7 - (self.time - self.start(2))))
        self.play(FadeIn(blur), run_time=0.6)

        # b3: the paths the points really take: drift to the middle, bend away later
        self.at(3)
        gp.curve.clear_updaters()
        self.play(*[FadeOut(m) for m in (gp, gt, flat, blur, lines, he, giant, gl)], run_time=0.6)
        self.clock.set_value(0)
        ts, FP = W.ts1, W.flow_paths
        idx = np.arange(0, n, 5)
        trails = VGroup(*[VMobject().set_stroke(HOT, 1.5, 0.6) for _ in idx])

        def upd(g):
            k = max(1, int(self.clock.get_value() * (len(ts) - 1)))
            for m, i in zip(g, idx):
                m.set_points_as_corners(xt.P(ts[: k + 1], FP[: k + 1, i]))

        trails.add_updater(upd)
        self.add(trails)
        self.play(self.clock.animate.set_value(1), run_time=self.dur(3) * 0.55, rate_func=linear)
        trails.clear_updaters()
        say = VGroup(Tx("the training lines", 0.32, FG), Tx("were straight", 0.32, FG), Tx("the paths", 0.32, HOT), Tx("are curved", 0.32, HOT)).arrange(DOWN, buff=0.14)
        say[2:].shift(DOWN * 0.3)
        place(say, Stage.right_narrow)
        self.play(FadeIn(say), run_time=0.6)

        # b4: curved paths need small steps: 2, 4, 16
        self.at(4)
        self.play(FadeOut(say), trails.animate.set_stroke(opacity=0.15), run_time=0.5)
        rows = VGroup()
        for k in (1, 2, 4, 16):
            m_ = miss(k)
            rows.add(VGroup(Tx(f"{k} step" + ("s" if k > 1 else ""), 0.34, FG), Tx(f"{m_:.2f}", 0.34, RED if m_ > 0.1 else DATA)))
        for r in rows:
            r[0].move_to(LEFT * 0.9, aligned_edge=LEFT)
            r[1].move_to(RIGHT * 1.1, aligned_edge=RIGHT)
        rows.arrange(DOWN, buff=0.3)
        head = Tx("average miss", 0.3, DIM).next_to(rows, UP, buff=0.35)
        tab = VGroup(head, rows)
        place(tab, Stage.right_narrow)
        self.play(FadeIn(head), FadeIn(rows[0]), run_time=0.5)
        d = self.dur(4)
        shown = None
        for j, (k, f) in enumerate(((2, 0.2), (4, 0.42), (16, 0.62))):
            tk, pk = world.flow1(W.x0[:n], k)
            sel = np.arange(0, n, 5)
            poly = xt.lines(tk, pk[:, sel], color=FG, width=1.6, opacity=0.6)
            self.wait(max(0.05, d * f - (self.time - self.start(4))))
            self.play(*([FadeOut(shown)] if shown is not None else []), ShowCreation(poly), FadeIn(rows[j + 1]), run_time=0.9)
            shown = poly
        self.finish()


class S10(BeatScene):
    SID = "s10"

    def construct(self):
        xt = XT(zone=Stage.left_wide, pad=1.0)
        ax = xt.axes()
        self.add(ax)
        n = 120
        x0, x1 = W.x0[:n], W.x1_random[:n]

        # b0: the pairing was random, so the lines cross everywhere
        self.at(0)
        lines = segments(xt.P(0, x0), xt.P(1, x1), FG, 1.3, 0.35)
        title = concept_title("random pairs: the lines cross")
        self.play(ShowCreation(lines), FadeIn(title), run_time=1.6)
        a = (X_HERE - T0) / (1 - T0)
        b = (X_HERE + T0) / (1 - T0)
        up = Line(xt.p(0, a), xt.p(1, 1)).set_stroke(DATA, 3)
        dn = Line(xt.p(0, b), xt.p(1, -1)).set_stroke(BLUE, 3)
        here = Dot(xt.p(T0, X_HERE), radius=0.1).set_fill(HOT, 1).set_stroke(width=0)
        self.wait(max(0.1, self.dur(0) * 0.65 - 1.6))
        self.play(ShowCreation(up), ShowCreation(dn), FadeIn(here), run_time=0.9)

        # b1: what the finished flow did: every negative went to -1, every positive to +1
        self.at(1)
        self.play(*[FadeOut(m) for m in (lines, up, dn, here, title)], run_time=0.6)
        title2 = concept_title("where the flow sent each noise point")
        ts, FP = W.ts1, W.flow_paths
        sel = np.arange(0, 400, 4)
        pos = [i for i in sel if W.x0[i] > 0]
        neg = [i for i in sel if W.x0[i] < 0]
        g_pos = xt.lines(ts[::4], FP[::4][:, pos], color=DATA, width=1.5, opacity=0.6)
        g_neg = xt.lines(ts[::4], FP[::4][:, neg], color=BLUE, width=1.5, opacity=0.6)
        zero = DashedLine(xt.p(-0.06, 0), xt.p(0.3, 0), dash_length=0.08).set_stroke(FG, 2)
        self.play(FadeIn(title2), ShowCreation(zero), run_time=0.6)
        d = self.dur(1)
        self.wait(max(0.1, d * 0.4 - 0.6))
        self.play(ShowCreation(g_neg), run_time=1.2)
        self.wait(max(0.1, d * 0.62 - (self.time - self.start(1))))
        self.play(ShowCreation(g_pos), run_time=1.2)
        kept = 100 * (np.sign(W.flow_end) == np.sign(W.x0)).mean()
        note = VGroup(Tx("positive  →  +1", 0.34, DATA), Tx("negative  →  −1", 0.34, BLUE), Tx(f"{kept:.0f}% of 10,000", 0.3, FG)).arrange(DOWN, buff=0.25)
        place(note, Stage.right_narrow)
        self.play(FadeIn(note), run_time=0.6)

        # b2: two points that follow the same rule can never cross
        self.at(2)
        self.play(FadeOut(note), run_time=0.4)
        c = np.array([4.6, 0.2, 0.0])
        p1 = Line(c + LEFT * 1.4 + UP * 0.9, c + RIGHT * 1.4 + DOWN * 0.9).set_stroke(DATA, 3)
        p2 = Line(c + LEFT * 1.4 + DOWN * 0.9, c + RIGHT * 1.4 + UP * 0.9).set_stroke(BLUE, 3)
        a1 = arrow(c, c + RIGHT * 0.9 + DOWN * 0.58, DATA, 6, buff=0, tip=0.24)
        a2 = arrow(c, c + RIGHT * 0.9 + UP * 0.58, BLUE, 6, buff=0, tip=0.24)
        dot = Dot(c, radius=0.1).set_fill(HOT, 1).set_stroke(width=0)
        bad = VGroup(Line(c + UL * 1.3, c + DR * 1.3), Line(c + UR * 1.3, c + DL * 1.3)).set_stroke(RED, 5, 0.85)
        cap = VGroup(Tx("one place,", 0.32, FG), Tx("two directions?", 0.32, FG), Tx("impossible", 0.36, RED)).arrange(DOWN, buff=0.14).next_to(c, DOWN, buff=1.5)
        d = self.dur(2)
        self.wait(d * 0.2)
        self.play(ShowCreation(p1), ShowCreation(p2), run_time=0.8)
        self.play(FadeIn(dot), ShowCreation(a1), ShowCreation(a2), FadeIn(cap[0]), FadeIn(cap[1]), run_time=0.8)
        self.wait(max(0.1, d * 0.75 - (self.time - self.start(2))))
        self.play(ShowCreation(bad), FadeIn(cap[2]), run_time=0.6)

        # b3: do you recognise this pairing? It is the sign trick
        self.at(3)
        self.play(*[FadeOut(m) for m in (p1, p2, a1, a2, dot, bad, cap, title2)], run_time=0.5)
        sign = concept_title("take the sign")
        d = self.dur(3)
        self.wait(max(0.1, d * 0.45 - 0.5))
        self.play(FadeIn(sign), run_time=0.6)
        told = VGroup(Tx("nobody told the flow", 0.32, FG), Tx("where the data was", 0.32, FG), Tx("it found the trick", 0.32, HOT), Tx("from examples", 0.32, HOT)).arrange(DOWN, buff=0.14)
        told[2:].shift(DOWN * 0.3)
        place(told, Stage.right_narrow)
        self.wait(max(0.1, d * 0.68 - (self.time - self.start(3))))
        self.play(FadeIn(told), run_time=0.6)
        self.finish()


class S11(BeatScene):
    SID = "s11"

    def construct(self):
        xt = XT(zone=Stage.left_wide, pad=1.0)
        ax = xt.axes()
        self.add(ax)
        n = 90
        x0 = W.x0[:n]
        x1 = np.sign(x0)

        # b0: train a second time, on the pairs the first flow produced
        self.at(0)
        title = concept_title("train again, on the flow's own pairs")
        self.play(FadeIn(title), run_time=0.6)
        rows = VGroup()
        for k in range(6):
            e = W.flow_end[k]
            rows.add(VGroup(Tx(f"{W.x0[k]:+.2f}", 0.32, NOISE), Tx("→", 0.5, DIM), Tx(f"{e:+.0f}", 0.32, DATA)).arrange(RIGHT, buff=0.3))
        rows.arrange(DOWN, buff=0.2, aligned_edge=RIGHT)
        head = VGroup(Tx("noise", 0.28, NOISE), Tx("where it ended", 0.28, DATA)).arrange(RIGHT, buff=0.35).next_to(rows, UP, buff=0.3)
        tab = VGroup(head, rows)
        place(tab, Stage.right_narrow)
        d = self.dur(0)
        self.wait(max(0.1, d * 0.55 - 0.6))
        self.play(FadeIn(head), LaggedStart(*[FadeIn(r) for r in rows], lag_ratio=0.25), run_time=1.6)

        # b1: draw their lines: they do not cross any more
        self.at(1)
        up, dn = x1 > 0, x1 < 0
        l_up = segments(xt.P(0, x0[up]), xt.P(1, x1[up]), DATA, 1.5, 0.6)
        l_dn = segments(xt.P(0, x0[dn]), xt.P(1, x1[dn]), BLUE, 1.5, 0.6)
        self.play(ShowCreation(l_up), ShowCreation(l_dn), run_time=1.8)

        # b2: standing at a point, which line am I on? Only one. The guess is exact
        self.at(2)
        self.play(FadeOut(tab), FadeOut(title), run_time=0.4)
        here = Dot(xt.p(T0, X_HERE), radius=0.12).set_fill(HOT, 1).set_stroke(FG, 1.5)
        a = (X_HERE - T0) / (1 - T0)
        only = Line(xt.p(0, a), xt.p(1, 1)).set_stroke(HOT, 4)
        d = self.dur(2)
        self.wait(d * 0.2)
        self.play(FadeIn(here, scale=2), run_time=0.5)
        self.wait(max(0.1, d * 0.5 - (self.time - self.start(2))))
        self.play(l_up.animate.set_stroke(opacity=0.2), l_dn.animate.set_stroke(opacity=0.2), ShowCreation(only), run_time=0.9)
        self.add(here)
        gr = ring(xt.p(1, 1), 0.18, HOT, 4)
        ex = VGroup(Tx("the guess here:", 0.32, FG), Tx("+1, exactly", 0.44, HOT), Tx("not an average", 0.3, DIM)).arrange(DOWN, buff=0.2)
        place(ex, Stage.right_narrow)
        self.wait(max(0.1, d * 0.7 - (self.time - self.start(2))))
        self.play(ShowCreation(gr), FadeIn(ex), run_time=0.7)

        # b3: the path is the line: one giant step is enough
        self.at(3)
        self.play(FadeOut(ex), run_time=0.3)
        start = Dot(xt.p(0, a), radius=0.11).set_fill(NOISE, 1).set_stroke(width=0)
        hop = arrow(xt.p(0, a), xt.p(1, 1), HOT, 6, buff=0.05, tip=0.28)
        one = VGroup(Tx("straight path", 0.34, FG), Tx("one step is enough", 0.4, HOT)).arrange(DOWN, buff=0.25)
        place(one, Stage.right_narrow)
        self.play(FadeOut(here), FadeOut(only), FadeIn(start), run_time=0.4)
        self.play(ShowCreation(hop), FadeIn(one[0]), run_time=1.0)
        self.wait(max(0.1, self.dur(3) * 0.6 - 1.4))
        self.play(FadeIn(one[1]), run_time=0.5)

        # b4: check: one step, 10,000 points: two clean spikes
        self.at(4)
        self.play(*[FadeOut(m) for m in (one, hop, start, gr)], run_time=0.4)
        idx = np.arange(0, 400, 3)
        self.clock.set_value(0)
        lines = growing_segments(xt.P(0, W.x0[idx]), xt.P(1, W.reflow_one[idx]), self.clock, HOT, 1.3, 0.5)
        self.add(lines)
        self.play(self.clock.animate.set_value(1), run_time=1.4)
        lines.clear_updaters()
        he = xt.hist(W.reflow_one, 1, direction=1, scale=0.55, color=HOT)
        pu = 100 * (W.reflow_one > 0).mean()
        chk = VGroup(Tx("one step", 0.34, FG), Tx("10,000 points", 0.34, FG), Tx(f"{pu:.0f}% on +1", 0.36, DATA), Tx(f"{100 - pu:.0f}% on −1", 0.36, DATA), Tx("0% anywhere else", 0.36, HOT)).arrange(DOWN, buff=0.2)
        chk[2:].shift(DOWN * 0.25)
        place(chk, Stage.right_narrow)
        self.play(FadeIn(he), FadeIn(chk[:2]), run_time=0.6)
        self.wait(max(0.1, self.dur(4) * 0.45 - 2.4))
        self.play(FadeIn(chk[2:]), run_time=0.6)

        # b5: the names: reflow, rectified flow; before and after
        self.at(5)
        self.play(*[FadeOut(m) for m in (chk, he, lines, l_up, l_dn, ax)], run_time=0.6)
        xa, xb = XT(zone=Stage.left, pad=0.8, vfill=0.6), XT(zone=Stage.right, pad=0.8, vfill=0.6)
        sel = np.arange(0, 400, 6)
        before = VGroup(xa.axes(), xa.lines(W.ts1[::4], W.flow_paths[::4][:, sel], color=FG, width=1.4, opacity=0.6))
        after = VGroup(xb.axes(), xb.lines(W.ts1[::50], W.reflow_paths[::50][:, sel], color=HOT, width=1.4, opacity=0.6))
        tb_ = Tx("flow matching: curved paths, many steps", 0.32, FG).next_to(before, UP, buff=0.35)
        ta_ = Tx("after reflow: a rectified flow", 0.32, HOT).next_to(after, UP, buff=0.35)
        mid = VGroup(arrow(LEFT * 0.45, RIGHT * 0.45, HOT, 4, buff=0), Tx("reflow", 0.3, HOT)).arrange(DOWN, buff=0.12).move_to(np.array([0, -0.3, 0]))
        self.play(FadeIn(before), FadeIn(tb_), run_time=0.7)
        d = self.dur(5)
        self.wait(max(0.1, d * 0.3 - 0.7))
        self.play(FadeIn(mid), run_time=0.5)
        self.wait(max(0.1, d * 0.55 - (self.time - self.start(5))))
        self.play(FadeIn(after), FadeIn(ta_), run_time=0.8)
        self.finish()


class S12(BeatScene):
    SID = "s12"

    def construct(self):
        # b0: cheating? Reflow compresses the first model: pay once, offline
        self.at(0)
        m1 = ModelBox("first model", w=2.9, h=1.1, size=0.34)
        m2 = ModelBox("second model", w=2.9, h=1.1, size=0.34)
        m2.box.set_stroke(HOT, 2.5)
        pairs = VGroup(Tx("pairs", 0.36, DATA), Tx("(noise, result)", 0.28, DIM)).arrange(DOWN, buff=0.1)
        chain = VGroup(m1, arrow(ORIGIN, RIGHT * 1.1, FG, 3, buff=0), pairs, arrow(ORIGIN, RIGHT * 1.1, FG, 3, buff=0), m2).arrange(RIGHT, buff=0.3)
        place(chain, Stage.main, grow=True, max_grow=1.25)
        c1 = Tx("200 steps per sample", 0.3, RED).next_to(m1, DOWN, buff=0.3)
        c2 = Tx("1 step per sample", 0.3, DATA).next_to(m2, DOWN, buff=0.3)
        q = concept_title("is that cheating?")
        d = self.dur(0)
        self.play(FadeIn(q), FadeIn(m1), FadeIn(c1), run_time=0.7)
        self.wait(max(0.1, d * 0.25 - 0.7))
        self.play(ShowCreation(chain[1]), FadeIn(pairs), run_time=0.7)
        self.wait(max(0.1, d * 0.5 - (self.time - self.start(0))))
        self.play(ShowCreation(chain[3]), FadeIn(m2), FadeIn(c2), run_time=0.7)
        once = Tx("pay for the slow sampler once, offline; after that every sample is cheap", 0.32, FG)
        place(once, Stage.foot)
        once.shift(UP * 1.0)
        self.wait(max(0.1, d * 0.72 - (self.time - self.start(0))))
        self.play(FadeIn(once), run_time=0.6)

        # b1: hikers in fog: everyone drifts to the middle of the map before choosing
        self.at(1)
        self.play(*[FadeOut(m) for m in (q, chain, c1, c2, once)], run_time=0.6)
        xt = XT(zone=Stage.left_wide, pad=1.0)
        frame = Rectangle(xt.b - xt.a + 1.2, xt.half * 2 + 0.3).set_stroke(DIM, 1.5).move_to(xt.p(0.5, 0))
        towns = VGroup(town(xt.p(1, 1)), town(xt.p(1, -1)))
        tl = VGroup(Tx("town", 0.26, DATA).next_to(towns[0], UP, buff=0.12), Tx("town", 0.26, DATA).next_to(towns[1], DOWN, buff=0.12))
        sel = np.arange(0, 400, 9)
        hikers = xt.crowd(W.x0[sel], 0.0, color=FG, radius=0.06, jitter=0.0)
        fog = Rectangle((xt.b - xt.a) * 0.78, xt.half * 2 + 0.1).set_stroke(width=0).set_fill("#9aa0a6", 0.3).move_to(xt.p(0.61, 0))
        title = concept_title("a picture for it: hikers in fog")
        self.play(FadeIn(title), FadeIn(frame), FadeIn(towns), FadeIn(tl), FadeIn(hikers), run_time=0.8)
        self.play(FadeIn(fog), run_time=0.6)
        self.clock.set_value(0)
        ts, FP = W.ts1, W.flow_paths
        trails = VGroup(*[VMobject().set_stroke(FG, 1.5, 0.6) for _ in sel])

        def upd(g):
            k = max(1, int(self.clock.get_value() * (len(ts) - 1)))
            for m, i in zip(g, sel):
                m.set_points_as_corners(xt.P(ts[: k + 1], FP[: k + 1, i]))

        trails.add_updater(upd)
        hikers.add_updater(lambda m: m.set_points(xt.P(self.clock.get_value(), lerp_traj(FP[:, sel], self.clock.get_value()))))
        self.add(trails, hikers, fog, towns)
        self.wait(max(0.1, self.dur(1) * 0.4 - 1.4))
        self.play(self.clock.animate.set_value(1), run_time=self.dur(1) * 0.5, rate_func=linear)
        trails.clear_updaters(), hikers.clear_updaters()
        slow = Tx("slow, curved trails", 0.32, FG)
        place(slow, Stage.right_narrow)
        self.play(FadeIn(slow), run_time=0.4)

        # b2: reflow hands the next crowd a list: who ended up where. Straight roads
        self.at(2)
        lst = VGroup(*[Tx(f"hiker {k + 1}:  {'north' if W.x0[sel[k]] > 0 else 'south'} town", 0.32, HOT) for k in range(5)]).arrange(DOWN, buff=0.18, aligned_edge=LEFT)
        place(lst, Stage.right_narrow)
        self.play(FadeOut(slow), FadeIn(lst), run_time=0.8)
        roads = segments(xt.P(0, W.x0[sel]), xt.P(1, np.sign(W.x0[sel])), HOT, 2, 0.75)
        self.wait(max(0.1, self.dur(2) * 0.5 - 0.8))
        self.play(FadeOut(fog), trails.animate.set_stroke(opacity=0.15), FadeOut(hikers), run_time=0.6)
        self.play(ShowCreation(roads), run_time=1.2)
        self.add(towns)

        # b3: map it back
        self.at(3)
        mp = VGroup()
        for a_, b_ in (("the fog", "not knowing your line's end"), ("the list", "the pairs"), ("the roads", "the new straight paths")):
            mp.add(VGroup(Tx(a_, 0.36, HOT), Tx("= " + b_, 0.3, FG)).arrange(DOWN, buff=0.1, aligned_edge=LEFT))
        mp.arrange(DOWN, buff=0.4, aligned_edge=LEFT)
        place(mp, Stage.right_narrow)
        self.play(FadeOut(lst), run_time=0.3)
        d = self.dur(3)
        for r, f in zip(mp, (0.15, 0.5, 0.75)):
            self.wait(max(0.05, d * f - (self.time - self.start(3))))
            self.play(FadeIn(r), run_time=0.5)

        # b4: where the picture is too kind: the list copies the hikers' mistakes
        self.at(4)
        self.play(FadeOut(mp), FadeOut(title), run_time=0.4)
        rng = np.random.default_rng(12)
        off = np.sign(W.x0[sel]) + rng.normal(0, 0.22, len(sel))
        roads2 = segments(xt.P(0, W.x0[sel]), xt.P(1, off), RED, 2, 0.75)
        ends = DotCloud(xt.P(1, off), color=RED, radius=0.06)
        d = self.dur(4)
        self.wait(d * 0.3)
        self.play(FadeOut(roads), FadeIn(roads2), FadeIn(ends), run_time=0.9)
        self.add(towns)
        warn = VGroup(Tx("the first model's errors", 0.32, RED), Tx("are copied into the roads", 0.32, RED), Tx("each round of reflow", 0.3, FG), Tx("inherits the last one's", 0.3, FG)).arrange(DOWN, buff=0.14)
        warn[2:].shift(DOWN * 0.3)
        place(warn, Stage.right_narrow)
        self.play(FadeIn(warn[:2]), run_time=0.5)
        self.wait(max(0.1, d * 0.7 - (self.time - self.start(4))))
        self.play(FadeIn(warn[2:]), run_time=0.5)

        # b5: the two-number world gave us three things. Now we climb
        self.at(5)
        self.play(*[FadeOut(m) for m in (warn, roads2, ends, trails, frame, towns, tl)], run_time=0.6)
        three = VGroup(Tx("1.  a generator is a guesser", 0.44, FG),
                       Tx("2.  flow matching learns the guess from straight lines", 0.44, BLUE),
                       Tx("3.  reflow makes the paths themselves straight", 0.44, HOT)).arrange(DOWN, buff=0.55, aligned_edge=LEFT)
        place(three, Stage.full)
        d = self.dur(5)
        for r, f in zip(three, (0.22, 0.38, 0.6)):
            self.wait(max(0.05, d * f - (self.time - self.start(5))))
            self.play(FadeIn(r), run_time=0.5)
        climb = Tx("next: one word", 0.36, DATA)
        place(climb, Stage.foot)
        self.wait(max(0.05, d * 0.88 - (self.time - self.start(5))))
        self.play(FadeIn(climb), run_time=0.4)
        self.finish()
