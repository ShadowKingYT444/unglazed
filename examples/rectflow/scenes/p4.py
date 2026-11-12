"""One word: locations for words, the guess as a soft token, the classifier, landing exactly, singular logits."""
from common import *

PL_C = np.array([-3.3, -0.35, 0.0])
Z_HERE, T_HERE = np.array([0.55, 0.15]), 0.5
P_HERE = world.post4(Z_HERE, T_HERE)[0]
G_HERE = P_HERE @ T4_E
def _pick_start():
    """A start whose bars stay undecided for a while and that ends on cat or dog (a longer, clearer trip)."""
    rng = np.random.default_rng(3)
    best = None
    for _ in range(80):
        z0 = rng.normal(size=2)
        S, P, _G = path4(z0)
        mid = P[100]
        score = -(mid * np.log(mid + 1e-12)).sum() if P[-1].argmax() in (2, 3) else -1
        if best is None or score > best[0]:
            best = (score, z0)
    return best[1]


Z_START = _pick_start()
WCOL = [BLUE, MAG, DATA, HOT]


def plane(unit=1.55):
    return Plane2(PL_C, unit)


def bars4(values, width=3.4):
    return Bars(T4, values, width=width, bar_h=0.34, gap=0.22, size=0.34)


class S13(BeatScene):
    SID = "s13"

    def construct(self):
        card(self, "4", "one word")

        # b0: a number can be nudged; a word cannot: nothing halfway between cat and dog
        cat, dog = Chip("cat", 0.44), Chip("dog", 0.44)
        row = VGroup(cat, Tx("?", 0.6, RED), dog).arrange(RIGHT, buff=1.2)
        place(row, Stage.main)
        num = VGroup(Tx("0.30", 0.44, FG), arrow(ORIGIN, RIGHT * 1.0, DIM, 3, buff=0), Tx("0.31", 0.44, FG)).arrange(RIGHT, buff=0.3).next_to(row, UP, buff=1.2)
        d = self.dur(0)
        self.wait(max(0.1, self.start(0) + d * 0.45 - self.time))
        self.play(FadeIn(num), run_time=0.6)
        self.wait(max(0.1, self.start(0) + d * 0.62 - self.time))
        self.play(FadeIn(cat), FadeIn(dog), run_time=0.6)
        self.wait(max(0.1, self.start(0) + d * 0.8 - self.time))
        self.play(FadeIn(row[1]), run_time=0.4)

        # b1: our data was never smooth: two isolated points. A two-word language
        self.at(1)
        self.play(FadeOut(row), FadeOut(num), run_time=0.5)
        xt = XT()
        ax = xt.axes()
        sel = np.arange(0, 400, 6)
        paths = xt.lines(W.ts1[::4], W.flow_paths[::4][:, sel], color=HOT, width=1.4, opacity=0.5)
        self.play(FadeIn(ax), FadeIn(paths), run_time=0.8)
        wa = Chip("word A", 0.32, DATA).next_to(xt.p(1, 1), RIGHT, buff=0.75)
        wb = Chip("word B", 0.32, DATA).next_to(xt.p(1, -1), RIGHT, buff=0.75)
        d = self.dur(1)
        self.wait(max(0.1, d * 0.45 - 0.8))
        self.play(ShowCreation(focus(ax.marks, RED, buff=0.2)), run_time=0.6)
        self.wait(max(0.1, d * 0.72 - (self.time - self.start(1))))
        self.play(FadeIn(wa), FadeIn(wb), run_time=0.6)

        # b2: give every word a location: its embedding
        self.at(2)
        self.play(*[FadeOut(m) for m in self.mobjects if m is not self.frame], run_time=0.6)
        pl = plane()
        dots, labs = token_dots(pl)
        title = concept_title("every word gets a location")
        self.play(FadeIn(title), LaggedStart(*[FadeIn(VGroup(a, b)) for a, b in zip(dots, labs)], lag_ratio=0.3), run_time=1.6)
        e = T4_E[2]
        emb = VGroup(Tx("cat", 0.4, FG), Tx("=", 0.4, DIM), Tx(f"( {e[0]:.2f},  {e[1]:.2f} )", 0.4, DATA)).arrange(RIGHT, buff=0.25)
        name = Tx("its embedding", 0.32, DATA)
        note = Tx("the paper uses 32 numbers per word", 0.3, DIM)
        col = VGroup(emb, name, note).arrange(DOWN, buff=0.35)
        note.shift(DOWN * 0.5)
        place(col, Stage.right)
        d = self.dur(2)
        self.wait(max(0.1, d * 0.3 - 1.6))
        self.play(FadeIn(emb), ShowCreation(ring(pl.p(e), 0.2, HOT, 3)), run_time=0.7)
        self.wait(max(0.1, d * 0.5 - (self.time - self.start(2))))
        self.play(FadeIn(name), run_time=0.5)
        self.wait(max(0.1, d * 0.85 - (self.time - self.start(2))))
        self.play(FadeIn(note), run_time=0.5)

        # b3: the same recipe: noise is a point on the plane, data is one of the dots, straight lines, follow the guess
        self.at(3)
        self.play(FadeOut(col), FadeOut(title), *[FadeOut(m) for m in self.mobjects if isinstance(m, Circle) and m not in dots], run_time=0.5)
        z0 = np.array([-0.4, -1.0])
        nz = Dot(pl.p(z0), radius=0.11).set_fill(NOISE, 1).set_stroke(width=0)
        nl = Tx("noise", 0.32, NOISE).next_to(nz, DOWN, buff=0.15)
        line = Line(pl.p(z0), pl.p(T4_E[2])).set_stroke(FG, 2.5)
        steps = VGroup(Tx("noise: a point on this plane", 0.34, NOISE), Tx("data: one of the four dots", 0.34, DATA),
                       Tx("travel on straight lines", 0.34, FG), Tx("follow the guess", 0.34, BLUE),
                       Tx("new question: what is the guess?", 0.36, HOT)).arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        steps[4].shift(DOWN * 0.4)
        place(steps, Stage.right)
        d = self.dur(3)
        for k, f in enumerate((0.12, 0.3, 0.45, 0.56, 0.72)):
            self.wait(max(0.05, d * f - (self.time - self.start(3))))
            extra = [FadeIn(nz), FadeIn(nl)] if k == 0 else [ShowCreation(line)] if k == 2 else []
            self.play(FadeIn(steps[k]), *extra, run_time=0.5)
        self.finish()


class S14(BeatScene):
    SID = "s14"

    def construct(self):
        pl = plane()
        dots, labs = token_dots(pl)
        self.add(dots, labs)
        me = Dot(pl.p(Z_HERE), radius=0.11).set_fill(HOT, 1).set_stroke(FG, 1.5)

        # b0: the guess is an average of four. First the weights: how likely is each word?
        self.at(0)
        rays = VGroup(*[DashedLine(pl.p(Z_HERE), pl.p(e), dash_length=0.09).set_stroke(FG, 1.5, 0.7) for e in T4_E])
        bars = bars4([0.001] * 4)
        place(bars, Stage.right)
        bq = VGroup(*[Tx("?", 0.36, HOT).move_to(r[1].get_left() + RIGHT * 0.3) for r in bars.rows])
        bt = Tx("how likely is each word?", 0.34, FG).next_to(bars, UP, buff=0.45)
        d = self.dur(0)
        self.wait(d * 0.3)
        self.play(FadeIn(me, scale=2), run_time=0.5)
        self.play(ShowCreation(rays), run_time=0.9)
        self.wait(max(0.1, d * 0.7 - (self.time - self.start(0))))
        self.play(FadeIn(bars), FadeIn(bq), FadeIn(bt), run_time=0.7)

        # b1: where cat's travelers are right now: a cloud centred t of the way to cat, radius 1 - t
        self.at(1)
        self.play(FadeOut(rays), FadeOut(bars), FadeOut(bq), FadeOut(bt), me.animate.set_opacity(0.3), run_time=0.5)
        self.clock.set_value(T_HERE)
        rng = np.random.default_rng(14)
        eps = rng.normal(size=(260, 2))

        def cloud(i, color):
            h = halo(pl.p(self.clock.get_value() * T4_E[i]), (1 - self.clock.get_value()) * pl.u, color, 0.1, 2)
            h.add_updater(lambda m: m.become(halo(pl.p(self.clock.get_value() * T4_E[i]), max(1e-3, (1 - self.clock.get_value()) * pl.u), color, 0.1, 2)))
            pts = DotCloud(pl.p(self.clock.get_value() * T4_E[i] + (1 - self.clock.get_value()) * eps * 0.7), color=color, radius=0.03, opacity=0.7)
            pts.add_updater(lambda m: m.set_points(pl.p(self.clock.get_value() * T4_E[i] + (1 - self.clock.get_value()) * eps * 0.7)))
            return h, pts

        hc, pc = cloud(2, DATA)
        spoke = Line(pl.p([0, 0]), pl.p(T4_E[2])).set_stroke(DIM, 1.5)
        ctr = Dot(pl.p(T_HERE * T4_E[2]), radius=0.06).set_fill(FG, 1).set_stroke(width=0)
        note = VGroup(Tx("if the word is cat:", 0.34, FG), Tx("centre: a fraction t of the way to cat", 0.32, DATA), Tx("radius: the noise left, 1 − t", 0.32, NOISE)).arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        place(note, Stage.right)
        d = self.dur(1)
        self.play(FadeIn(note[0]), FadeIn(hc), FadeIn(pc), run_time=0.8)
        self.wait(max(0.1, d * 0.5 - 0.8))
        self.play(ShowCreation(spoke), FadeIn(ctr), FadeIn(note[1]), run_time=0.7)
        self.wait(max(0.1, d * 0.75 - (self.time - self.start(1))))
        self.play(FadeIn(note[2]), run_time=0.5)

        # b2: at time 0 all four clouds are the same; as time runs each slides to its word and shrinks
        self.at(2)
        self.play(FadeOut(note), FadeOut(spoke), FadeOut(ctr), FadeOut(me), run_time=0.4)
        self.play(self.clock.animate.set_value(0.0), run_time=0.8)
        others = [cloud(i, c) for i, c in ((0, BLUE), (1, MAG), (3, HOT))]
        self.add(*[m for pair in others for m in pair])
        tb = TimeBar(self.clock, width=4.2, ends=("time 0", "time 1"))
        place(tb, Stage.right)
        self.play(FadeIn(tb), run_time=0.4)
        d = self.dur(2)
        self.wait(max(0.1, d * 0.4 - 1.2))
        self.play(self.clock.animate.set_value(0.88), run_time=d * 0.5, rate_func=smooth)

        # b3: the share of each word: how common, times how close to the centre of its cloud. A softmax
        self.at(3)
        self.play(self.clock.animate.set_value(T_HERE), FadeOut(tb), run_time=0.8)
        tb.knob.clear_updaters()
        me.set_opacity(1)
        self.play(FadeIn(me), run_time=0.3)
        f = M("P(w)", "\\ \\propto\\ ", "\\pi(w)", "\\ \\cdot\\ ", "\\exp\\!\\left(-\\dfrac{|z - t\\,E(w)|^2}{2\\,(1-t)^2}\\right)", colors={0: BLUE, 2: DATA, 4: HOT}, size=0.5)
        cap = VGroup(Tx("how common", 0.3, DATA), Tx("how close to its cloud", 0.3, HOT)).arrange(RIGHT, buff=0.7)
        bars = bars4(P_HERE)
        pct = VGroup(*[Tx(f"{100 * v:.0f}%", 0.3, FG).next_to(r[1], RIGHT, buff=0.15) for r, v in zip(bars.rows, P_HERE)])
        place(f, (3.45, 2.75, 6.3, 1.3))
        cap.next_to(f, DOWN, buff=0.25)
        place(bars, (3.45, -1.1, 6.3, 3.0))
        pct = VGroup(*[Tx(f"{100 * v:.0f}%", 0.3, FG).next_to(r[1], RIGHT, buff=0.15) for r, v in zip(bars.rows, P_HERE)])
        d = self.dur(3)
        self.wait(max(0.1, d * 0.2 - 1.1))
        self.play(FadeIn(f), run_time=0.7)
        self.wait(max(0.1, d * 0.4 - (self.time - self.start(3))))
        self.play(FadeIn(cap[0]), run_time=0.4)
        self.wait(max(0.1, d * 0.52 - (self.time - self.start(3))))
        self.play(FadeIn(cap[1]), run_time=0.4)
        self.wait(max(0.1, d * 0.8 - (self.time - self.start(3))))
        self.play(FadeIn(bars), FadeIn(pct), run_time=0.7)

        # b4: the guess is the weighted average of the word locations: a soft token
        self.at(4)
        for pair in [(hc, pc)] + others:
            for m in pair:
                m.clear_updaters()
        self.play(*[FadeOut(m) for pair in [(hc, pc)] + others for m in pair], FadeOut(cap), FadeOut(f), run_time=0.5)
        pulls = VGroup(*[Line(pl.p(Z_HERE), pl.p(e)).set_stroke(DATA, 1 + 9 * p, 0.8) for e, p in zip(T4_E, P_HERE)])
        gr = ring(pl.p(G_HERE), 0.17, BLUE, 4)
        f2 = M("\\mathrm{guess}", "=", "\\sum_w\\ P(w)\\ E(w)", colors={0: BLUE}, size=0.52).next_to(bars, UP, buff=0.6)
        d = self.dur(4)
        self.play(ShowCreation(pulls), run_time=0.8)
        self.add(me)
        self.play(ShowCreation(gr), FadeIn(f2), run_time=0.7)
        soft = Tx("a soft token: between words, on no word", 0.32, BLUE).next_to(bars, DOWN, buff=0.5)
        self.wait(max(0.1, d * 0.55 - 1.5))
        self.play(FadeIn(soft), run_time=0.5)

        # b5: follow it and watch the bars: one bar takes everything, the soft token slides onto that word
        self.at(5)
        self.play(FadeOut(pulls), FadeOut(pct), FadeOut(f2), FadeOut(soft), FadeOut(me), FadeOut(gr), run_time=0.5)
        S, P, G = path4(Z_START)
        self.clock.set_value(0)
        pt = Dot(radius=0.11).set_fill(HOT, 1).set_stroke(FG, 1.5)
        pt.add_updater(lambda m: m.move_to(pl.p(lerp_traj(S, self.clock.get_value()))))
        gr2 = ring(pl.p(G[0]), 0.17, BLUE, 4)
        gr2.add_updater(lambda m: m.move_to(pl.p(lerp_traj(G, self.clock.get_value()))))
        trail = VMobject().set_stroke(HOT, 3)
        trail.add_updater(lambda m: m.set_points_as_corners(pl.p(S[: max(2, int(self.clock.get_value() * 200) + 1)])))
        live_bars(bars, lambda: lerp_traj(P, self.clock.get_value()))
        tb2 = TimeBar(self.clock, width=4.2, ends=("time 0", "time 1")).next_to(bars, DOWN, buff=0.6)
        self.add(trail, pt, gr2)
        self.play(FadeIn(tb2), run_time=0.4)
        d = self.dur(5)
        self.play(self.clock.animate.set_value(0.45), run_time=d * 0.3, rate_func=linear)
        self.play(self.clock.animate.set_value(1.0), run_time=d * 0.45, rate_func=linear)
        for m in (pt, gr2, trail, bars):
            m.clear_updaters()
        tb2.knob.clear_updaters()

        # b6: ten thousand points: each word receives its fair share
        self.at(6)
        self.play(*[FadeOut(m) for m in (pt, gr2, trail, bars, tb2)], run_time=0.5)
        rng = np.random.default_rng(15)
        z = rng.normal(size=(700, 2))
        tt = np.linspace(0, 1, 61)
        traj = [z.copy()]
        for a, b in zip(tt[:-1], tt[1:]):
            z = z + (b - a) / (1 - a) * (world.post4(z, min(a, 0.999)) @ T4_E - z)
            traj.append(z.copy())
        traj = np.array(traj)
        self.clock.set_value(0)
        cl = DotCloud(pl.p(traj[0]), color=NOISE, radius=0.035, opacity=0.8)
        cl.add_updater(lambda m: m.set_points(pl.p(lerp_traj(traj, self.clock.get_value()))))
        self.add(cl, dots)
        d = self.dur(6)
        self.play(self.clock.animate.set_value(1), run_time=d * 0.4, rate_func=linear)
        cl.clear_updaters()
        tab = VGroup()
        for n_, s_, p_ in zip(T4, W.t4_share, T4_PI):
            tab.add(VGroup(Tx(n_, 0.36, FG), Tx(f"{100 * s_:.0f}% land here", 0.34, DATA), Tx(f"(it is {100 * p_:.0f}% of the data)", 0.28, DIM)).arrange(RIGHT, buff=0.3))
        tab.arrange(DOWN, buff=0.35, aligned_edge=LEFT)
        place(tab, Stage.right)
        self.play(FadeIn(tab), run_time=0.7)
        self.finish()


class S15(BeatScene):
    SID = "s15"

    def construct(self):
        # b0: what must the network produce? Not a direction, not a point. Just those bars
        self.at(0)
        box = ModelBox("network", w=2.6, h=1.2, size=0.36)
        inp = VGroup(Tx("noisy point", 0.34, HOT), Tx("and the time", 0.34, HOT)).arrange(DOWN, buff=0.1)
        bars = bars4(P_HERE, width=2.8)
        chain = VGroup(inp, arrow(ORIGIN, RIGHT * 0.9, FG, 3, buff=0), box, arrow(ORIGIN, RIGHT * 0.9, FG, 3, buff=0), bars).arrange(RIGHT, buff=0.35)
        place(chain, Stage.main)
        no1 = Tx("a direction", 0.36, DIM)
        no2 = Tx("a point", 0.36, DIM)
        nos = VGroup(no1, no2).arrange(RIGHT, buff=1.2).next_to(chain, UP, buff=0.9).shift(RIGHT * 3)
        d = self.dur(0)
        self.play(FadeIn(inp), FadeIn(chain[1]), FadeIn(box), run_time=0.7)
        self.wait(max(0.1, d * 0.35 - 0.7))
        self.play(FadeIn(no1), run_time=0.3)
        self.play(ShowCreation(Line(no1.get_left(), no1.get_right()).set_stroke(RED, 3)), run_time=0.3)
        self.wait(max(0.1, d * 0.5 - (self.time - self.start(0))))
        self.play(FadeIn(no2), run_time=0.3)
        self.play(ShowCreation(Line(no2.get_left(), no2.get_right()).set_stroke(RED, 3)), run_time=0.3)
        self.wait(max(0.1, d * 0.68 - (self.time - self.start(0))))
        self.play(FadeIn(chain[3]), FadeIn(bars), run_time=0.7)

        # b1: that is a classifier: one score per word (a logit), softmax turns scores into probabilities
        self.at(1)
        self.play(*[FadeOut(m) for m in self.mobjects if m is not self.frame], run_time=0.5)
        title = concept_title("a classifier")
        lg = np.log(P_HERE) + 2.0
        scores = VGroup(*[VGroup(Tx(n_, 0.36, FG), Tx(f"{v:+.1f}", 0.36, HOT)).arrange(RIGHT, buff=0.5) for n_, v in zip(T4, lg)]).arrange(DOWN, buff=0.32, aligned_edge=RIGHT)
        sl = Tx("scores (logits)", 0.32, HOT).next_to(scores, UP, buff=0.4)
        sm = ModelBox("softmax", w=2.0, h=0.9, size=0.32)
        bars = bars4(P_HERE, width=2.8)
        bl = Tx("probabilities", 0.32, BLUE)
        chain = VGroup(scores, arrow(ORIGIN, RIGHT * 0.8, FG, 3, buff=0), sm, arrow(ORIGIN, RIGHT * 0.8, FG, 3, buff=0), bars).arrange(RIGHT, buff=0.4)
        place(chain, Stage.main)
        sl.next_to(scores, UP, buff=0.4)
        bl.next_to(bars, UP, buff=0.4)
        d = self.dur(1)
        self.play(FadeIn(title), FadeIn(scores), run_time=0.7)
        self.wait(max(0.1, d * 0.3 - 0.7))
        self.play(FadeIn(sl), run_time=0.4)
        self.wait(max(0.1, d * 0.5 - (self.time - self.start(1))))
        self.play(FadeIn(chain[1]), FadeIn(sm), FadeIn(chain[3]), FadeIn(bars), FadeIn(bl), run_time=0.8)
        same = Tx("exactly what an ordinary language model does", 0.32, DIM)
        place(same, Stage.foot)
        same.shift(UP * 0.6)
        self.wait(max(0.1, d * 0.8 - (self.time - self.start(1))))
        self.play(FadeIn(same), run_time=0.5)

        # b2: train it the ordinary way: hide a real word in noise, ask which word it was, cross entropy
        self.at(2)
        self.play(*[FadeOut(m) for m in self.mobjects if m is not self.frame and m is not title], run_time=0.5)
        w = Chip("cat", 0.4, DATA)
        nz = VGroup(Dot(radius=0.11).set_fill(HOT, 1).set_stroke(FG, 1.5), Tx("hidden in noise", 0.28, HOT)).arrange(DOWN, buff=0.15)
        net = ModelBox("network", w=2.2, h=1.0, size=0.34)
        bars = bars4(P_HERE, width=2.4)
        chain = VGroup(w, arrow(ORIGIN, RIGHT * 0.7, FG, 3, buff=0), nz, arrow(ORIGIN, RIGHT * 0.7, FG, 3, buff=0), net, arrow(ORIGIN, RIGHT * 0.7, FG, 3, buff=0), bars).arrange(RIGHT, buff=0.3)
        place(chain, Stage.main)
        chain.shift(UP * 0.5)
        loss = M("\\mathrm{loss}", "=", "-\\log P(\\mathrm{cat})", "=", f"{-np.log(P_HERE[2]):.2f}", colors={0: HOT, 4: HOT}, size=0.56).next_to(chain, DOWN, buff=0.9)
        hi = focus(VGroup(*bars.rows[2][:3]), HOT, buff=0.08)
        d = self.dur(2)
        for k, f_ in ((0, 0.15), (2, 0.3), (4, 0.5)):
            self.wait(max(0.05, d * f_ - (self.time - self.start(2))))
            self.play(*([FadeIn(chain[k - 1])] if k else []), FadeIn(chain[k]), run_time=0.5)
        self.play(FadeIn(chain[5]), FadeIn(bars), run_time=0.5)
        self.wait(max(0.05, d * 0.78 - (self.time - self.start(2))))
        self.play(ShowCreation(hi), FadeIn(loss), run_time=0.7)

        # b3: why cross entropy: it is smallest when the predicted bars equal the true chances
        self.at(3)
        self.play(*[FadeOut(m) for m in self.mobjects if m is not self.frame and m is not title], run_time=0.5)
        true = bars4(P_HERE, width=3.0)
        for r in true.rows:
            r[2].set_fill(DATA, 0.95)
        pred = bars4(np.full(4, 0.25), width=3.0)
        both = VGroup(pred, true).arrange(RIGHT, buff=1.6)
        place(both, Stage.main)
        lp = Tx("the network's bars", 0.32, BLUE).next_to(pred, UP, buff=0.4)
        lt = Tx("the true chances", 0.32, DATA).next_to(true, UP, buff=0.4)

        def ce(q):
            return float(-(P_HERE * np.log(q)).sum())

        self.play(FadeIn(both), FadeIn(lp), FadeIn(lt), run_time=0.7)
        states = [np.full(4, 0.25), 0.5 * np.full(4, 0.25) + 0.5 * P_HERE, P_HERE, 0.6 * P_HERE + 0.4 * np.eye(4)[2]]
        tags = ["", "", "smallest here", "more confident than the truth: worse"]
        lab = Tx(f"average loss  {ce(states[0]):.3f}", 0.36, HOT).next_to(pred, DOWN, buff=0.6)
        self.play(FadeIn(lab), run_time=0.4)
        d = self.dur(3)
        for k, f_ in ((1, 0.3), (2, 0.5), (3, 0.78)):
            self.wait(max(0.05, d * f_ - (self.time - self.start(3))))
            new = Tx(f"average loss  {ce(states[k]):.3f}" + (f"   {tags[k]}" if tags[k] else ""), 0.36, HOT if k != 2 else DATA).next_to(pred, DOWN, buff=0.6)
            new.align_to(pred, LEFT)
            vt = ValueTracker(0)
            a_, b_ = states[k - 1], states[k]
            pred.add_updater(lambda m, a_=a_, b_=b_, vt=vt: m.set_values((1 - vt.get_value()) * a_ + vt.get_value() * b_))
            self.play(vt.animate.set_value(1), FadeOut(lab), FadeIn(new), run_time=0.8)
            pred.clear_updaters()
            lab = new

        # b4: the paper tried both losses: perplexity 24.1 with cross entropy, 25.6 with squared error
        self.at(4)
        self.play(*[FadeOut(m) for m in self.mobjects if m is not self.frame], run_time=0.5)
        ch = BarChart(["cross entropy", "squared error"], [24.1, 25.6], colors=[DATA, DIM], unit=0.14, bar_w=1.6, gap=1.0, size=0.32, val_size=0.4)
        place(ch, Stage.main)
        t2 = concept_title("same network, two losses  (perplexity: lower is better)")
        self.play(FadeIn(t2), FadeIn(ch.base), run_time=0.6)
        d = self.dur(4)
        self.wait(max(0.05, d * 0.35 - 0.6))
        self.play(*ch.grow(0), run_time=0.7)
        self.wait(max(0.05, d * 0.6 - (self.time - self.start(4))))
        self.play(*ch.grow(1), run_time=0.7)

        # b5: the thesis is literal: a classifier asked the same question again and again, on a less noisy input
        self.at(5)
        self.play(*[FadeOut(m) for m in self.mobjects if m is not self.frame], run_time=0.5)
        S, P, G = path4(Z_START)
        cols = VGroup()
        for t_ in (0.1, 0.45, 0.7, 0.95):
            b_ = Bars(T4, P[int(t_ * 200)], width=2.0, bar_h=0.26, gap=0.16, size=0.28)
            cols.add(VGroup(Tx(f"time {t_:.2f}".rstrip("0").rstrip("."), 0.3, DIM), b_).arrange(DOWN, buff=0.35))
        cols.arrange(RIGHT, buff=0.7)
        place(cols, Stage.main, grow=True, max_grow=1.3)
        t3 = concept_title("the same multiple-choice question, on a less noisy input each time")
        self.play(FadeIn(t3), run_time=0.5)
        d = self.dur(5)
        for k, c_ in enumerate(cols):
            self.wait(max(0.05, d * (0.25 + 0.15 * k) - (self.time - self.start(5))))
            self.play(FadeIn(c_), run_time=0.5)
        self.finish()


class S16(BeatScene):
    SID = "s16"

    def construct(self):
        rng = np.random.default_rng(16)
        # b0: a picture that is slightly off is still a picture; a word that is slightly off is not a word
        self.at(0)
        pic = picture()
        off = np.clip(pic + rng.normal(0, 0.06, pic.shape), 0, 1)
        t1, t2 = Tile(pic, height=2.6), Tile(off, height=2.6)
        pics = Group(t1, t2).arrange(RIGHT, buff=0.5)
        cap1 = Tx("slightly off: still a picture", 0.32, DATA)
        left = Group(pics, cap1).arrange(DOWN, buff=0.4)
        place(left, Stage.left)
        c = np.array([3.45, 0.1, 0.0])
        dot = Dot(c, radius=0.13).set_fill(DATA, 1).set_stroke(width=0)
        dl = Tx("cat", 0.4, FG).next_to(dot, UP, buff=0.2)
        near = Dot(c + np.array([0.55, -0.4, 0]), radius=0.11).set_fill(HOT, 1).set_stroke(FG, 1.5)
        cap2 = Tx("slightly off: not a word", 0.32, RED).move_to(np.array([3.45, cap1.get_center()[1], 0]))
        d = self.dur(0)
        self.wait(d * 0.15)
        self.play(FadeIn(pics), run_time=0.7)
        self.play(FadeIn(cap1), run_time=0.4)
        self.wait(max(0.1, d * 0.5 - (self.time - self.start(0))))
        self.play(FadeIn(dot), FadeIn(dl), FadeIn(near), run_time=0.6)
        self.play(FadeIn(cap2), run_time=0.4)

        # b1: the last guess must be 100% one word: the logit gap has to grow without limit
        self.at(1)
        self.play(*[FadeOut(m) for m in (pics, cap1, dot, dl, near, cap2)], run_time=0.5)
        bars = bars4([0.001, 0.001, 0.997, 0.001], width=3.0)
        bl = Tx("the last guess: 100% one word", 0.34, FG).next_to(bars, UP, buff=0.45)
        lhs = VGroup(bl, bars)
        place(lhs, Stage.left)
        f = VGroup(M("\\mathrm{gap}", "=", "\\mathrm{logit}(\\mathrm{right\\ word}) - \\mathrm{logit}(\\mathrm{any\\ other})", colors={0: HOT}, size=0.42),
                   M("99\\%\\ \\to\\ \\mathrm{gap}\\ 4.6", size=0.42), M("99.99\\%\\ \\to\\ \\mathrm{gap}\\ 9.2", size=0.42),
                   M("100\\%\\ \\to\\ \\mathrm{gap}\\ \\infty", size=0.46, color=RED)).arrange(DOWN, buff=0.4)
        place(f, Stage.right)
        d = self.dur(1)
        self.play(FadeIn(lhs), run_time=0.7)
        for k, f_ in enumerate((0.4, 0.58, 0.7, 0.82)):
            self.wait(max(0.05, d * f_ - (self.time - self.start(1))))
            self.play(FadeIn(f[k]), run_time=0.5)

        # b2: the gap along a real path in the toy: below 2 for most of the trip, thousands near the end
        self.at(2)
        self.play(FadeOut(lhs), FadeOut(f), run_time=0.5)
        st = W.stats
        pltt = Plot(xr=(0, 1), yr=(0, 40), w=8.6, h=4.0, xticks=(0, 0.5, 1), yticks=(0, 10, 20, 30, 40), xlabel="time", size=0.28)
        place(pltt, Stage.main)
        yl = Tx("gap between the top two scores", 0.3, HOT).next_to(pltt.yax.get_top(), UP, buff=0.2).align_to(pltt.yax, LEFT)
        curve = pltt.curve(st["t"], st["gap"], HOT, 4)
        self.play(FadeIn(pltt), FadeIn(yl), run_time=0.6)
        self.play(ShowCreation(curve), run_time=self.dur(2) * 0.4, rate_func=linear)
        low = Tx("below 2", 0.32, FG).next_to(pltt.p(0.4, 2), UP, buff=0.3)
        up_ = arrow(pltt.p(0.93, 30), pltt.p(0.93, 39.5), HOT, 4, buff=0)
        high = Tx(f"{st['gap'][-1]:,.0f} at the end", 0.32, HOT).next_to(pltt.p(0.9, 36), LEFT, buff=0.3)
        self.play(FadeIn(low), run_time=0.4)
        self.wait(max(0.1, self.dur(2) * 0.75 - (self.time - self.start(2))))
        self.play(ShowCreation(up_), FadeIn(high), run_time=0.6)

        # b3: a network's numbers are finite: a perfect classifier with gaps capped at 6
        self.at(3)
        capl = DashedLine(pltt.p(0, 6), pltt.p(1, 6), dash_length=0.12).set_stroke(RED, 3)
        capt = Tx("a network's limit: say 6", 0.32, RED).next_to(pltt.p(0.25, 6), UP, buff=0.15)
        self.wait(self.dur(3) * 0.45)
        self.play(ShowCreation(capl), FadeIn(capt), FadeOut(low), run_time=0.7)

        # b4: its final answer is 96% one word: the path ends near a word, not on it
        self.at(4)
        self.play(*[FadeOut(m) for m in (pltt, yl, curve, up_, high, capl, capt)], run_time=0.5)
        ex = W.cap["capped"]["ex"]
        ptop = float(ex[1][-1].max(1).mean())
        bars = bars4([(1 - ptop) / 3, (1 - ptop) / 3, ptop, (1 - ptop) / 3], width=3.0)
        pc = VGroup(*[Tx(f"{100 * v:.0f}%" if v > 0.5 else f"{100 * v:.1f}%", 0.3, FG).next_to(r[1], RIGHT, buff=0.15) for r, v in zip(bars.rows, [(1 - ptop) / 3, (1 - ptop) / 3, ptop, (1 - ptop) / 3])])
        bl = Tx("the capped classifier's last answer", 0.32, FG).next_to(bars, UP, buff=0.45)
        lhs = VGroup(bl, bars, pc)
        place(lhs, Stage.left)
        c = np.array([3.45, 0.2, 0.0])
        lens = Circle(radius=2.1).set_stroke(DIM, 2).move_to(c)
        dot = Dot(c + UP * 0.5 + LEFT * 0.3, radius=0.14).set_fill(DATA, 1).set_stroke(width=0)
        dl = Tx("cat", 0.4, FG).next_to(dot, UP, buff=0.2)
        end = Dot(dot.get_center() + np.array([0.75, -0.95, 0]), radius=0.11).set_fill(HOT, 1).set_stroke(FG, 1.5)
        tr = Line(c + np.array([-0.3, -2.0, 0]) + RIGHT * 1.2, end.get_center()).set_stroke(HOT, 3)
        el = Tx("the path ends here", 0.3, HOT).next_to(end, LEFT, buff=0.2)
        zl = Tx("zoomed in", 0.26, DIM).next_to(lens, DOWN, buff=0.15)
        d = self.dur(4)
        self.play(FadeIn(lhs), run_time=0.7)
        self.wait(max(0.1, d * 0.45 - 0.7))
        self.play(FadeIn(lens), FadeIn(zl), FadeIn(dot), FadeIn(dl), run_time=0.5)
        self.play(ShowCreation(tr), run_time=0.7)
        self.play(FadeIn(end), FadeIn(el), run_time=0.4)
        verdict = Tx("near a word, not on it", 0.38, RED)
        place(verdict, Stage.title)
        self.wait(max(0.1, d * 0.85 - (self.time - self.start(4))))
        self.play(FadeIn(verdict), run_time=0.5)
        self.finish()


class S17(BeatScene):
    SID = "s17"

    def construct(self):
        pl = plane(1.45)
        dots, labs = token_dots(pl)

        # b0: older models snapped to the nearest word. Where does the exploding certainty come from?
        self.at(0)
        e = T4_E[2]
        end = Dot(pl.p(e + np.array([0.3, -0.4])), radius=0.11).set_fill(HOT, 1).set_stroke(FG, 1.5)
        snap = arrow(end.get_center(), pl.p(e), RED, 4, buff=0.1)
        sl = Tx("snap to the nearest word", 0.32, RED).next_to(labs[2], UP, buff=0.3)
        self.play(FadeIn(dots), FadeIn(labs), FadeIn(end), run_time=0.7)
        self.play(ShowCreation(snap), FadeIn(sl), run_time=0.7)
        q = VGroup(Tx("a better question:", 0.34, FG), Tx("where does that certainty", 0.36, HOT), Tx("come from in the first place?", 0.36, HOT)).arrange(DOWN, buff=0.2)
        place(q, Stage.right)
        self.wait(max(0.1, self.dur(0) * 0.55 - 1.4))
        self.play(FadeIn(q), run_time=0.6)

        # b1: from distance: next to cat with almost no noise left, closeness alone says cat
        self.at(1)
        self.play(FadeOut(q), FadeOut(snap), FadeOut(sl), FadeOut(end), run_time=0.5)
        self.clock.set_value(0.5)
        zfix = e + np.array([0.12, -0.1])
        pt = Dot(radius=0.11).set_fill(HOT, 1).set_stroke(FG, 1.5)
        pt.add_updater(lambda m: m.move_to(pl.p(self.clock.get_value() * zfix + (1 - self.clock.get_value()) * np.array([0.5, -0.5]))))
        hc = halo(pl.p(0.5 * e), 0.5 * pl.u, DATA, 0.1, 2)
        hc.add_updater(lambda m: m.become(halo(pl.p(self.clock.get_value() * e), max(1e-3, (1 - self.clock.get_value()) * pl.u), DATA, 0.1, 2)))
        bars = bars4(P_HERE, width=3.2)

        def close_bars():
            t = self.clock.get_value()
            return world.post4(t * zfix + (1 - t) * np.array([0.5, -0.5]), min(t, 0.999))[0]

        live_bars(bars, close_bars)
        bl = Tx("from closeness alone (no network)", 0.32, DATA).next_to(bars, UP, buff=0.45)
        tb = TimeBar(self.clock, width=4.0, ends=("time 0", "time 1")).next_to(bars, DOWN, buff=0.6)
        rhs = VGroup(bl, bars, tb)
        place(rhs, Stage.right)
        self.play(FadeIn(hc), FadeIn(pt), FadeIn(rhs), run_time=0.7)
        d = self.dur(1)
        self.wait(max(0.1, d * 0.3 - 0.7))
        self.play(self.clock.animate.set_value(0.97), run_time=d * 0.55, rate_func=smooth)

        # b2: closeness is something we can compute: the same formula as before
        self.at(2)
        for m in (pt, hc, bars):
            m.clear_updaters()
        tb.knob.clear_updaters()
        self.play(FadeOut(rhs), run_time=0.4)
        f = VGroup(Tx("closeness of word w", 0.34, DATA),
                   M("\\log\\pi(w)", "\\ -\\ ", "\\dfrac{|z - t\\,E(w)|^2}{2\\,(1-t)^2}", colors={0: DATA, 2: HOT}, size=0.52),
                   VGroup(Tx("how common", 0.3, DATA), Tx("how far", 0.3, HOT)).arrange(RIGHT, buff=1.3),
                   Tx("a formula: nothing to learn", 0.34, FG)).arrange(DOWN, buff=0.4)
        f[3].shift(DOWN * 0.3)
        place(f, Stage.right)
        d = self.dur(2)
        self.play(FadeIn(f[0]), FadeIn(f[1]), run_time=0.7)
        self.wait(max(0.1, d * 0.5 - 0.7))
        self.play(FadeIn(f[2]), run_time=0.5)
        self.wait(max(0.1, d * 0.8 - (self.time - self.start(2))))
        self.play(FadeIn(f[3]), run_time=0.5)

        # b3: split the scores in two: the formula (singular logits) plus what the network adds
        self.at(3)
        self.play(*[FadeOut(m) for m in self.mobjects if m is not self.frame], run_time=0.5)
        a = VGroup(Tx("closeness", 0.46, DATA), Tx("a formula", 0.3, DIM), Tx("the singular logits", 0.34, DATA)).arrange(DOWN, buff=0.22)
        b = VGroup(Tx("network", 0.46, BLUE), Tx("learned", 0.3, DIM), Tx("what the rest of the sentence", 0.3, BLUE), Tx("says about this word", 0.3, BLUE)).arrange(DOWN, buff=0.22)
        b[3].shift(UP * 0.1)
        eq = VGroup(Tx("scores", 0.46, FG), Tx("=", 0.46, FG), a, Tx("+", 0.46, FG), b).arrange(RIGHT, buff=0.55, aligned_edge=UP)
        place(eq, Stage.main)
        for m in (a[1:], b[1:]):
            m.set_opacity(0)
        d = self.dur(3)
        self.play(FadeIn(eq[0]), FadeIn(eq[1]), run_time=0.5)
        self.wait(max(0.1, d * 0.25 - 0.5))
        self.play(FadeIn(a[0]), a[1].animate.set_opacity(1), run_time=0.5)
        self.wait(max(0.1, d * 0.42 - (self.time - self.start(3))))
        self.play(a[2].animate.set_opacity(1), run_time=0.5)
        self.wait(max(0.1, d * 0.62 - (self.time - self.start(3))))
        self.play(FadeIn(eq[3]), FadeIn(b[0]), b[1:].animate.set_opacity(1), run_time=0.6)

        # b4: why the split is safe: the formula carries everything that explodes
        self.at(4)
        ex1 = VGroup(Tx("grows without limit", 0.3, HOT), Tx("as the noise shrinks", 0.3, HOT)).arrange(DOWN, buff=0.12).next_to(a, DOWN, buff=0.6)
        ex2 = VGroup(Tx("how much more likely the word is", 0.3, FG), Tx("in this sentence than in general:", 0.3, FG), Tx("an ordinary, finite number", 0.32, DATA)).arrange(DOWN, buff=0.12).next_to(b, DOWN, buff=0.6)
        d = self.dur(4)
        self.wait(d * 0.2)
        self.play(FadeIn(ex1), run_time=0.5)
        self.wait(max(0.1, d * 0.5 - (self.time - self.start(4))))
        self.play(FadeIn(ex2), run_time=0.6)

        # b5: the paper proves a bound; on the toy: bound 30, network part never above 19, formula part past 3,000
        self.at(5)
        self.play(*[FadeOut(m) for m in self.mobjects if m is not self.frame], run_time=0.5)
        st = W.stats
        pltt = Plot(xr=(0, 1), yr=(0, 40), w=8.0, h=3.9, xticks=(0, 0.5, 1), yticks=(0, 10, 20, 30, 40), xlabel="time", size=0.28)
        place(pltt, Stage.left_wide)
        bound = DashedLine(pltt.p(0, W.bound), pltt.p(1, W.bound), dash_length=0.12).set_stroke(RED, 3)
        c_f = pltt.curve(st["t"], st["fmax"], BLUE, 4)
        c_g = pltt.curve(st["t"], st["gap"], HOT, 4)
        leg = VGroup(Tx(f"the proven bound: {W.bound:.0f}", 0.32, RED), Tx(f"the network's part: at most {st['fmax'].max():.1f}", 0.32, BLUE),
                     Tx(f"the formula's part: {st['gap'][-1]:,.0f}", 0.32, HOT), Tx("30 paths on the toy", 0.28, DIM)).arrange(DOWN, buff=0.35, aligned_edge=LEFT)
        place(leg, Stage.right_narrow)
        d = self.dur(5)
        self.play(FadeIn(pltt), run_time=0.5)
        self.wait(max(0.1, d * 0.2 - 0.5))
        self.play(ShowCreation(bound), FadeIn(leg[0]), run_time=0.7)
        self.wait(max(0.1, d * 0.45 - (self.time - self.start(5))))
        self.play(ShowCreation(c_f), FadeIn(leg[1]), run_time=1.2)
        self.wait(max(0.1, d * 0.72 - (self.time - self.start(5))))
        self.play(ShowCreation(c_g), FadeIn(leg[2]), FadeIn(leg[3]), run_time=1.2)

        # b6: the same capped classifier, with the split, lands exactly on its word
        self.at(6)
        self.play(*[FadeOut(m) for m in self.mobjects if m is not self.frame], run_time=0.5)

        def lensed(center, offset, color, label, miss_):
            lens = Circle(radius=1.7).set_stroke(DIM, 2).move_to(center)
            dot = Dot(center, radius=0.14).set_fill(DATA, 1).set_stroke(width=0)
            end = Dot(center + offset, radius=0.1).set_fill(HOT, 1).set_stroke(FG, 1.5)
            tr = Line(center + np.array([1.0, -1.35, 0]), end.get_center()).set_stroke(HOT, 3)
            head = Tx(label, 0.32, color).next_to(lens, UP, buff=0.25)
            m_ = Tx(f"average miss {miss_:.3f}", 0.32, color).next_to(lens, DOWN, buff=0.25)
            return VGroup(lens, tr, dot, end, head, m_)

        a = lensed(np.array([-3.45, -0.2, 0]), np.array([0.55, -0.7, 0]), RED, "scores capped at 6", W.cap["capped"]["miss"])
        b = lensed(np.array([3.45, -0.2, 0]), np.array([0.0, 0.0, 0]), DATA, "formula + a network capped at 6", abs(W.cap["split"]["miss"]))
        d = self.dur(6)
        self.play(FadeIn(a), run_time=0.7)
        self.wait(max(0.1, d * 0.3 - 0.7))
        self.play(FadeIn(b), run_time=0.7)
        end_ = Tx("the network no longer has to produce certainty. It only has to choose.", 0.34, FG)
        place(end_, Stage.title)
        self.wait(max(0.1, d * 0.6 - (self.time - self.start(6))))
        self.play(FadeIn(end_), run_time=0.6)
        self.finish()
