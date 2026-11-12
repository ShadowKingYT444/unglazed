"""The question, and the start of the two-number world: generating, diffusion in brief, the guess."""
from common import *


class S01(BeatScene):
    SID = "s01"

    def construct(self):
        rng = np.random.default_rng(1)
        words = "the river carries every leaf down to the sea".split()
        row = place(token_row(words, size=0.38, w=1.34), Stage.full).shift(UP * 1.9)
        for c in row:
            c.label.set_opacity(0)
            c.box.set_stroke(FAINT, 1.5)
        self.play(FadeIn(row), run_time=0.6)

        # b0: one word, then the next: a thousand trips
        self.at(0)
        step = self.dur(0) * 0.45 / len(words)
        for c in row:
            self.play(c.label.animate.set_opacity(1), c.box.animate.set_stroke(FG, 1.5), run_time=min(0.22, step * 0.7))
            self.wait(max(0.02, step - 0.22))
        trips = Tx("1,000 words  =  1,000 trips through the network", 0.36, DIM).next_to(row, DOWN, buff=0.45)
        self.wait(max(0.1, self.dur(0) * 0.72 - (self.time - self.start(0))))
        self.play(FadeIn(trips), run_time=0.6)

        # b1: images are improved all at once
        self.at(1)
        pic = picture()
        nz = noise_img(rng, 96, 96)
        k = ValueTracker(0)
        book = Flipbook([blend_noise(pic, nz, a ** 1.4) for a in np.linspace(0, 1, 24)], height=3.5, tracker=k)
        book.move_to(DOWN * 1.75)
        self.add(book)
        self.play(book.appear(), run_time=0.6)
        self.play(k.animate.set_value(1), run_time=self.dur(1) * 0.55, rate_func=linear)

        # b2: text can be written that way: 16 steps
        self.at(2)
        self.play(FadeOut(trips), book.vanish(), *[c.label.animate.set_opacity(0) for c in row], run_time=0.6)
        self.remove(book)
        tiles = Group(*[Tile(noise_img(rng, 20, 34), height=row[0].box.get_height() * 0.98, border=False).move_to(c) for c in row])
        self.play(*[FadeIn(t) for t in tiles], run_time=0.5)
        ticks = np.stack([(np.arange(16) - 7.5) * 0.3, np.full(16, row.get_bottom()[1] - 0.7), np.zeros(16)], 1)
        tg = DotCloud(ticks, color=FAINT, radius=0.065)
        tl = DotCloud(ticks[:1], color=HOT, radius=0.065)
        self.play(FadeIn(tg), run_time=0.3)
        per = self.dur(2) * 0.35 / 16
        for s_ in range(1, 17):
            a = s_ / 16
            tl.set_points(ticks[:s_])
            if s_ == 1:
                self.add(tl)
            self.play(*[t.img.animate.set_opacity(1 - a) for t in tiles], *[c.label.animate.set_opacity(a ** 1.5) for c in row], run_time=per * 0.6)
            self.wait(per * 0.4)
        self.remove(tiles)
        res = VGroup(Tx("16 steps", 0.5, HOT), Tx("Rectified Language Flow  ·  arXiv 2610.33811", 0.3, DIM)).arrange(DOWN, buff=0.35)
        res.next_to(tg, DOWN, buff=0.7)
        self.play(FadeIn(res), run_time=0.7)

        # b3: the usual explanation: differential equations, and you nod along
        self.at(3)
        self.play(*[FadeOut(m) for m in (row, tg, tl, res)], run_time=0.6)
        wall = ladder(
            M("\\dfrac{dZ_t}{dt} = v(Z_t,\\ t)", size=0.66),
            M("\\partial_t\\, p_t + \\nabla\\cdot(p_t\\, v_t) = 0", size=0.66),
            M("\\min_\\theta\\ \\mathrm{E}\\,\\|\\,v_\\theta(X_t,\\ t) - (X_1 - X_0)\\,\\|^2", size=0.66),
            buff=0.55, aligned_edge=ORIGIN)
        place(wall, Stage.full)
        self.play(LaggedStart(*[FadeIn(w) for w in wall], lag_ratio=0.4), run_time=self.dur(3) * 0.45)
        self.wait(max(0.1, self.dur(3) * 0.7 - (self.time - self.start(3))))
        self.play(wall.animate.set_opacity(0.15), run_time=0.8)

        # b4: the thesis, one line at a time
        self.at(4)
        self.play(FadeOut(wall), run_time=0.5)
        th = VGroup(Tx("a generator makes a guess, again and again", 0.5, FG),
                    Tx("rectified flow: one guess is nearly enough", 0.5, HOT),
                    Tx("for text: the guess is a multiple-choice answer", 0.5, BLUE)).arrange(DOWN, buff=0.7)
        place(th, Stage.full)
        d = self.dur(4)
        for line, f in zip(th, (0.2, 0.48, 0.74)):
            self.wait(max(0.05, d * f - (self.time - self.start(4))))
            self.play(FadeIn(line), run_time=0.7)

        # b5: four worlds
        self.at(5)
        self.play(FadeOut(th), run_time=0.6)
        head = concept_title("four worlds, one recipe")
        self.play(FadeIn(head), run_time=0.5)

        def card(title, sub, art):
            box = RoundedRectangle(width=3.0, height=3.9, corner_radius=0.14).set_stroke(DIM, 1.5)
            art.scale(1.5).move_to(box.get_center() + UP * 0.65)
            t1 = Tx(title, 0.36, FG).move_to(box.get_bottom() + UP * 1.0)
            t2 = fit(Tx(sub, 0.26, DIM), 2.7).move_to(box.get_bottom() + UP * 0.48)
            return VGroup(box, art, t1, t2)

        a1 = VGroup(Line(DOWN * 0.6, UP * 0.6).set_stroke(DIM, 1.5), Dot(UP * 0.4, radius=0.08).set_fill(DATA, 1), Dot(DOWN * 0.4, radius=0.08).set_fill(DATA, 1))
        a2 = VGroup(*[Dot(np.array([x, y, 0]) * 0.5, radius=0.07).set_fill(DATA, 1) for x, y in ((-1, 0.2), (0.2, -1), (0.9, 0.8), (1.1, 0.1))])
        a3 = VGroup(*[Square(0.26).set_stroke(DATA, 1.5) for _ in range(6)]).arrange(RIGHT, buff=0.07)
        a4 = VGroup(*[Square(0.09).set_stroke(width=0).set_fill(DATA, 0.25 + 0.6 * rng.random()) for _ in range(6 * 18)]).arrange_in_grid(6, 18, buff=0.025)
        cards = VGroup(card("two numbers", "do it by hand", a1), card("one word", "four words on a plane", a2),
                       card("a sentence", "six slots", a3), card("the real model", "1,024 words at once", a4)).arrange(RIGHT, buff=0.3)
        place(cards, Stage.main)
        d = self.dur(5)
        for c, f in zip(cards, (0.18, 0.55, 0.68, 0.8)):
            self.wait(max(0.05, d * f - (self.time - self.start(5))))
            self.play(FadeIn(c), run_time=0.5)
        self.finish()


class S02(BeatScene):
    SID = "s02"

    def construct(self):
        rng = np.random.default_rng(2)
        self.chapter("1", "the smallest world")
        xt = XT()
        ax = xt.axes()
        hd = xt.hist(np.repeat([-1.0, 1.0], 5000), 1, direction=1, scale=0.9, color=DATA)
        hn = xt.hist(W.x0, 0, direction=-1, scale=1.5, color=NOISE)

        # b1: the data: -1 or +1, half each
        self.at(1)
        self.play(ShowCreation(ax.right), FadeIn(ax.l1), run_time=0.7)
        self.play(FadeIn(ax.marks), FadeIn(hd), run_time=0.9)
        two = place(Tx("a language with two words", 0.34, DATA), Stage.title)
        self.wait(max(0.1, self.dur(1) * 0.75 - 1.6))
        self.play(FadeIn(two), run_time=0.6)

        # b2: what a computer produces easily: noise from a bell curve
        self.at(2)
        self.play(FadeOut(two), ShowCreation(ax.left), FadeIn(ax.l0), run_time=0.7)
        dots = xt.crowd(W.x0[:300], 0.0)
        self.play(FadeIn(dots), FadeIn(hn), run_time=1.2)

        # b3: the problem in its smallest form; pause and decide
        self.at(3)
        q = Tx("?", 0.9, HOT).move_to(xt.p(0.5, 0))
        ar = arrow(xt.p(0.12, 0), xt.p(0.88, 0), DIM, 3, buff=0)
        self.play(ShowCreation(ar), run_time=0.8)
        self.play(FadeIn(q), run_time=0.5)
        pause = Tx("pause, and decide how you would do it", 0.36, HOT)
        place(pause, Stage.title)
        self.wait(max(0.1, self.dur(3) * 0.8 - 1.3))
        self.play(FadeIn(pause), run_time=0.5)

        # b4: take the sign. It works, but it used knowledge of where the data is
        self.at(4)
        self.play(FadeOut(q), FadeOut(ar), FadeOut(pause), run_time=0.5)
        xs = W.x0[:70]
        up = segments(xt.P(0, xs[xs > 0]), xt.P(1, np.ones((xs > 0).sum())), DATA, 1.3, 0.5)
        dn = segments(xt.P(0, xs[xs < 0]), xt.P(1, -np.ones((xs < 0).sum())), BLUE, 1.3, 0.5)
        sign = Tx("take the sign", 0.4, FG)
        place(sign, Stage.title)
        self.play(ShowCreation(up), ShowCreation(dn), FadeIn(sign), run_time=1.6)
        self.wait(max(0.1, self.dur(4) * 0.62 - 1.6))
        know = focus(ax.marks, RED, buff=0.25)
        kl = Tx("you already knew where the data was", 0.3, RED).next_to(know, UP, buff=0.2).align_to(know, RIGHT)
        self.play(ShowCreation(know), FadeIn(kl), run_time=0.8)

        # b5: for pictures or sentences we only have examples; remember the sign trick
        self.at(5)
        self.play(FadeOut(know), FadeOut(kl), up.animate.set_stroke(opacity=0.12), dn.animate.set_stroke(opacity=0.12), FadeOut(sign), run_time=0.7)
        ex = Tx("all we get is examples:   +1   −1   −1   +1   −1   +1   +1   …", 0.36, DATA)
        place(ex, Stage.title)
        self.play(FadeIn(ex), run_time=0.8)
        self.finish()


class S03(BeatScene):
    SID = "s03"

    def construct(self):
        rng = np.random.default_rng(3)
        xt = XT()
        ax = xt.axes()
        title = concept_title("diffusion")
        self.add(ax)

        # b0-b1: the forward direction: mix real data with more and more noise
        self.at(0)
        self.play(FadeIn(title), run_time=0.6)
        n = 300
        x1 = W.x1_random[:n]
        x0 = W.x0[:n]
        self.clock.set_value(1.0)
        jit = xt.jitter(n)
        crowd = DotCloud(xt.P(1.0, x1) + jit, color=DATA, radius=0.045)

        def upd(m):
            t = self.clock.get_value()
            m.set_points(xt.P(t, t * x1 + (1 - t) * x0) + jit)
            m.set_color(interpolate_color(NOISE, DATA, t ** 2))

        crowd.add_updater(upd)
        self.wait(self.dur(0) * 0.35)
        self.play(FadeIn(crowd), run_time=0.5)
        self.play(self.clock.animate.set_value(0.0), run_time=self.left(1) - 0.6, rate_func=smooth)
        self.at(1)
        d = self.dur(1)
        self.play(self.clock.animate.set_value(1.0), run_time=d * 0.4, rate_func=smooth)
        self.play(self.clock.animate.set_value(0.5), run_time=d * 0.3, rate_func=smooth)

        # b2: a network is trained to undo the damage: noisy number + how noisy -> the clean number?
        self.at(2)
        k = 17
        t0 = 0.5
        pt = Dot(xt.p(t0, t0 * x1[k] + (1 - t0) * x0[k]), radius=0.11).set_fill(HOT, 1).set_stroke(FG, 1.5)
        box = ModelBox("network", w=1.9, h=0.8, size=0.28)
        ask = VGroup(Tx("a noisy number, and how noisy", 0.32, FG), arrow(ORIGIN, RIGHT * 0.8, FG, 2.5, buff=0), box,
                     arrow(ORIGIN, RIGHT * 0.8, FG, 2.5, buff=0), Tx("what was the clean number?", 0.32, BLUE)).arrange(RIGHT, buff=0.2)
        place(ask, Stage.title)
        self.play(FadeOut(title), crowd.animate.set_opacity(0.25), FadeIn(pt, scale=2), run_time=0.7)
        self.play(FadeIn(ask), run_time=0.9)

        # b3: to generate: many small steps: ask, move a little, stir in fresh noise
        self.at(3)
        crowd.clear_updaters()
        self.play(FadeOut(crowd), FadeOut(pt), FadeOut(ask), run_time=0.5)
        title2 = concept_title("diffusion: generating")
        self.play(FadeIn(title2), run_time=0.5)
        j = 5
        one = VMobject().set_stroke(HOT, 2.5)
        self.clock.set_value(0)

        def upd_one(m):
            kk = max(1, int(self.clock.get_value() * (len(W.ts_noisy) - 1)))
            m.set_points_as_corners(xt.P(W.ts_noisy[: kk + 1], W.noisy_paths[: kk + 1, j]))

        one.add_updater(upd_one)
        head = Dot(radius=0.09).set_fill(FG, 1).set_stroke(width=0)
        head.add_updater(lambda m: m.move_to(xt.p(self.clock.get_value(), lerp_traj(W.noisy_paths[:, j], self.clock.get_value()))))
        self.add(one, head)
        self.play(self.clock.animate.set_value(1), run_time=self.left(4) - 1.2, rate_func=linear)
        one.clear_updaters(), head.clear_updaters()

        # b4: 400 points, 200 steps each: they settle half and half
        self.at(4)
        self.play(FadeOut(head), one.animate.set_stroke(opacity=0.25), run_time=0.4)
        self.clock.set_value(0)
        idx = np.arange(60)
        trails = VGroup(*[VMobject().set_stroke(NOISE, 1.2, 0.55) for _ in idx])

        def upd_tr(g):
            kk = max(1, int(self.clock.get_value() * (len(W.ts_noisy) - 1)))
            for m, i in zip(g, idx):
                m.set_points_as_corners(xt.P(W.ts_noisy[: kk + 1], W.noisy_paths[: kk + 1, i]))

        trails.add_updater(upd_tr)
        cr = DotCloud(xt.P(0.0, W.x0[:400]), color=NOISE, radius=0.04)
        cr.add_updater(lambda m: m.set_points(xt.P(self.clock.get_value(), lerp_traj(W.noisy_paths, self.clock.get_value()))))
        self.add(trails, cr)
        self.play(self.clock.animate.set_value(1), run_time=self.dur(4) * 0.7, rate_func=linear)
        trails.clear_updaters(), cr.clear_updaters()
        he = xt.hist(W.noisy_end, 1, direction=1, scale=0.9, color=NOISE)
        share = Tx(f"{100 * (W.noisy_end > 0).mean():.0f}% / {100 * (W.noisy_end < 0).mean():.0f}%", 0.32, FG).next_to(xt.p(1, 0), RIGHT, buff=0.3)
        self.play(FadeIn(he), FadeIn(share), run_time=0.7)

        # b5: the cost: 200 trips, jittery paths
        self.at(5)
        cost = Tx("200 trips through the network for every sample", 0.38, RED)
        self.wait(self.dur(5) * 0.3)
        self.play(FadeOut(title2), FadeIn(cost.move_to(np.array([0, 3.4, 0]))), run_time=0.7)
        self.finish()


class S04(BeatScene):
    SID = "s04"

    def construct(self):
        xt = XT(zone=Stage.left, pad=0.75)
        ax = xt.axes()
        title = concept_title("the guess")
        t0, x_here = 0.5, 0.3
        self.clock.set_value(t0)
        here = Dot(xt.p(t0, x_here), radius=0.11).set_fill(HOT, 1).set_stroke(FG, 1.5)
        up = DashedLine(xt.p(t0, x_here), xt.p(1, 1), dash_length=0.1).set_stroke(FG, 2)
        dn = DashedLine(xt.p(t0, x_here), xt.p(1, -1), dash_length=0.1).set_stroke(FG, 2)

        # b0: the same noisy number can come from -1 or from +1
        self.play(FadeIn(ax), run_time=0.6)
        self.at(0)
        self.wait(self.dur(0) * 0.3)
        self.play(FadeIn(here, scale=2), run_time=0.5)
        self.play(ShowCreation(up), ShowCreation(dn), run_time=1.0)
        q = Tx("?", 0.6, HOT).next_to(xt.p(0.78, 0), RIGHT, buff=0.0)
        self.play(FadeIn(q), run_time=0.4)

        # b1: the best it can do: the weighted average of the possible answers = the guess
        self.at(1)
        g = float(world.guess1(x_here, t0))
        p_up = (1 + g) / 2
        self.play(FadeOut(q), up.animate.set_stroke(DATA, 1.5 + 6 * p_up), dn.animate.set_stroke(DATA, 1.5 + 6 * (1 - p_up)), FadeIn(title), run_time=0.9)
        wl = VGroup(Tx(f"{100 * p_up:.0f}%", 0.32, DATA).next_to(xt.p(0.75, 0.65), UP, buff=0.16),
                    Tx(f"{100 * (1 - p_up):.0f}%", 0.32, DATA).next_to(xt.p(0.75, -0.35), DOWN, buff=0.16))
        self.play(FadeIn(wl), run_time=0.6)
        gr = ring(xt.p(1, g), 0.16, BLUE, 4)
        gl = Tx(f"guess {g:.2f}", 0.32, BLUE).next_to(gr, RIGHT, buff=0.18)
        self.wait(max(0.1, self.dur(1) * 0.6 - 1.5))
        self.play(ShowCreation(gr), FadeIn(gl), run_time=0.8)

        # b2: in this world the guess is a curve we can write down
        self.at(2)
        gp = guess_plot(Stage.right, self.clock)
        formula = M("\\mathrm{guess}", "=", "\\tanh\\!\\left(\\dfrac{t\\,x}{(1-t)^2}\\right)", colors={0: BLUE}, size=0.42)
        formula.next_to(gp, UP, buff=0.25)
        fit(formula, 5.6)
        mark = Dot(radius=0.09).set_fill(HOT, 1).set_stroke(width=0)
        mark.add_updater(lambda m: m.move_to(gp.plot.p(x_here, world.guess1(x_here, min(self.clock.get_value(), 0.995)))))
        self.play(FadeOut(title), FadeOut(gl), FadeIn(gp), run_time=0.9)
        self.add(mark)
        self.play(FadeIn(formula), run_time=0.6)
        tb = TimeBar(self.clock, width=3.6, ends=("time 0", "time 1")).next_to(gp, DOWN, buff=0.45)
        self.play(FadeIn(tb), run_time=0.5)

        # the left picture follows the clock too
        def upd_left(_m):
            t = float(np.clip(self.clock.get_value(), 0.02, 0.97))
            gg = float(world.guess1(x_here, t))
            pu = (1 + gg) / 2
            here.move_to(xt.p(t, x_here))
            up.become(DashedLine(xt.p(t, x_here), xt.p(1, 1), dash_length=0.1).set_stroke(DATA, 1.5 + 6 * pu))
            dn.become(DashedLine(xt.p(t, x_here), xt.p(1, -1), dash_length=0.1).set_stroke(DATA, 1.5 + 6 * (1 - pu)))
            gr.move_to(xt.p(1, gg))

        driver = VMobject()
        driver.add_updater(upd_left)

        # b3: late: the curve is a step, the guess is confident
        self.at(3)
        self.play(FadeOut(wl), run_time=0.4)
        self.add(driver)
        self.play(self.clock.animate.set_value(0.93), run_time=self.dur(3) * 0.6, rate_func=smooth)

        # b4: early: the curve is flat at zero: "I do not know yet"
        self.at(4)
        self.play(self.clock.animate.set_value(0.03), run_time=self.dur(4) * 0.35, rate_func=smooth)
        idk = Tx("zero: the average of −1 and +1", 0.3, BLUE).next_to(gp.plot.p(0, 0), UP, buff=0.5)
        self.wait(max(0.1, self.dur(4) * 0.55 - (self.time - self.start(4))))
        self.play(FadeIn(idk), run_time=0.6)

        # b5: where we are
        self.at(5)
        driver.clear_updaters()
        rec = Tx("a generator is a guesser, used over and over", 0.36, FG)
        place(rec, (3.45, -3.5, 6.3, 0.5))
        tb.knob.clear_updaters()
        self.play(FadeIn(rec), FadeOut(idk), FadeOut(tb), run_time=0.7)
        gp.curve.clear_updaters(), mark.clear_updaters()
        self.finish()
