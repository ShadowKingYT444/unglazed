"""The real model: reflow on text, the results and their limits, and the recap."""
from common import *


def group_bars(labels, series, colors, names, unit=0.13, bar_w=0.62, gap=0.9):
    """Bars side by side for each label; series is a list of value lists."""
    g, sets = VGroup(), [VGroup() for _ in series]
    k = len(series)
    for i, lab in enumerate(labels):
        x0 = i * (k * bar_w + gap)
        for j, (vals, c) in enumerate(zip(series, colors)):
            v = vals[i]
            r = Rectangle(bar_w, v * unit).set_stroke(width=0).set_fill(c, 0.95).move_to(np.array([x0 + j * bar_w, v * unit / 2, 0]))
            t = Tx(f"{v:.1f}", 0.3, c).next_to(r, UP, buff=0.08)
            sets[j].add(VGroup(r, t))
        g.add(Tx(lab, 0.3, FG).move_to(np.array([x0 + (k - 1) * bar_w / 2, -0.3, 0])))
    width = (len(labels) - 1) * (k * bar_w + gap) + k * bar_w
    base = Line(np.array([-bar_w, 0, 0]), np.array([width, 0, 0])).set_stroke(DIM, 2)
    out = VGroup(base, g, *sets)
    out.base, out.labs, out.sets, out.unit = base, g, sets, unit
    return out


class S22(BeatScene):
    SID = "s22"

    def construct(self):
        card(self, "6", "the real model")

        # b0: 32 numbers per word, 1,024 words, and still 64 calls: early guesses are blends, so the paths curve
        facts = VGroup(Tx("32 numbers per word", 0.4, DATA), Tx("1,024 words at once", 0.4, DATA), Tx("64 calls", 0.44, HOT)).arrange(DOWN, buff=0.4)
        place(facts, Stage.left)
        xt = XT(zone=Stage.right, pad=0.8, vfill=0.6)
        sel = np.arange(0, 400, 6)
        curved = VGroup(xt.axes(), xt.lines(W.ts1[::4], W.flow_paths[::4][:, sel], color=HOT, width=1.4, opacity=0.6))
        why = Tx("early guesses are blends, so the paths curve", 0.3, HOT).next_to(curved, UP, buff=0.3)
        d = self.dur(0)
        for k, f in enumerate((0.3, 0.42, 0.55)):
            self.wait(max(0.05, self.start(0) + d * f - self.time))
            self.play(FadeIn(facts[k]), run_time=0.5)
        self.wait(max(0.05, self.start(0) + d * 0.72 - self.time))
        self.play(FadeIn(curved), FadeIn(why), run_time=0.8)

        # b1: the cure: run the model from about half a million noise tables and record the text each became
        self.at(1)
        self.play(*[FadeOut(m) for m in (facts, curved, why)], run_time=0.5)
        rng = np.random.default_rng(22)
        noise = Heat(rng.normal(size=(3, 5)), cell=0.36, vmax=2.2)
        nl = Tx("a noise table", 0.3, NOISE)
        left = VGroup(noise, nl).arrange(DOWN, buff=0.25)
        model = ModelBox("the trained model", w=3.4, h=1.2, size=0.34)
        ml = Tx("many careful steps", 0.28, DIM)
        mid = VGroup(model, ml).arrange(DOWN, buff=0.2)
        text = VGroup(Tx("“The harbour was quiet", 0.3, DATA), Tx("when the boats came in …”", 0.3, DATA)).arrange(DOWN, buff=0.1)
        tl = Tx("the text it became", 0.3, DATA)
        right = VGroup(text, tl).arrange(DOWN, buff=0.3)
        chain = VGroup(left, arrow(ORIGIN, RIGHT * 0.9, FG, 3, buff=0), mid, arrow(ORIGIN, RIGHT * 0.9, FG, 3, buff=0), right).arrange(RIGHT, buff=0.35)
        place(chain, Stage.main)
        chain.shift(UP * 0.4)
        count = Tx("about 500,000 pairs  (noise table, text)", 0.36, HOT).next_to(chain, DOWN, buff=0.9)
        d = self.dur(1)
        self.wait(d * 0.15)
        self.play(FadeIn(left), FadeIn(chain[1]), FadeIn(mid), run_time=0.8)
        self.wait(max(0.1, d * 0.6 - (self.time - self.start(1))))
        self.play(FadeIn(chain[3]), FadeIn(right), run_time=0.7)
        self.play(FadeIn(count), run_time=0.5)

        # b2: train again on those pairs: same loss, same network
        self.at(2)
        self.play(FadeOut(chain), count.animate.move_to(np.array([0, 3.4, 0])), run_time=0.6)
        code = CodePanel([
            "x0, x1 = noise_table, its_text      # a recorded pair",
            "t  = sample_time()",
            "xt = t * E[x1] + (1 - t) * x0",
            "loss = cross_entropy(net(xt, t), x1)",
        ], size=0.32)
        place(code, Stage.main)
        self.play(FadeIn(code), run_time=0.7)
        d = self.dur(2)
        self.wait(max(0.1, d * 0.35 - 1.3))
        self.play(*code.hl(0), run_time=0.4)
        self.wait(max(0.1, d * 0.6 - (self.time - self.start(2))))
        self.play(*code.hl(3), run_time=0.4)

        # b3: the pairs are the model's own writing: mix the new weights back toward the original (70% original)
        self.at(3)
        self.play(FadeOut(code), FadeOut(count), run_time=0.5)
        title = concept_title("the hikers' mistakes: the pairs are the model's own writing")
        bar = Line(LEFT * 4, RIGHT * 4).set_stroke(DIM, 4)
        place(bar, Stage.main)
        a = Tx("original model", 0.34, FG).next_to(bar.get_left(), DOWN, buff=0.35)
        b = Tx("retrained on its own pairs", 0.34, HOT).next_to(bar.get_right(), DOWN, buff=0.35)
        b.align_to(bar, RIGHT)
        a.align_to(bar, LEFT)
        knob = Dot(bar.get_right(), radius=0.16).set_fill(HOT, 1).set_stroke(FG, 2)
        d = self.dur(3)
        self.play(FadeIn(title), ShowCreation(bar), FadeIn(a), FadeIn(b), FadeIn(knob), run_time=0.8)
        self.wait(max(0.1, d * 0.55 - 0.8))
        target = interpolate(bar.get_left(), bar.get_right(), 0.3)
        self.play(knob.animate.move_to(target), run_time=1.2)
        mix = Tx("weights after round one:  70% original  +  30% retrained", 0.42, DATA).next_to(bar, UP, buff=0.9)
        self.play(FadeIn(mix), run_time=0.5)

        # b4: the result: 16 calls instead of 64: 26.4; left to right: 27.7 with 1,024 calls
        self.at(4)
        self.play(*[FadeOut(m) for m in (title, bar, a, b, knob, mix)], run_time=0.5)
        t4 = concept_title("perplexity (lower is better), 1,024 words")
        labels4 = ["64 calls", "16 calls\nafter reflow", "left to right\n1,024 calls", "4 calls\nafter reflow"]
        ch = BarChart(labels4[:3], [24.1, 26.4, 27.7], colors=[DATA, HOT, DIM], unit=0.12, bar_w=1.6, gap=1.0, size=0.3, val_size=0.4)
        place(ch, Stage.main)
        ch4 = BarChart(labels4, [24.1, 26.4, 27.7, 116.0], colors=[DATA, HOT, DIM, RED], unit=0.032, bar_w=1.5, gap=0.9, size=0.3, val_size=0.38)
        place(ch4, Stage.main)
        d = self.dur(4)
        self.play(FadeIn(t4), FadeIn(ch.base), *ch.grow(0), run_time=0.8)
        self.wait(max(0.1, d * 0.3 - 0.8))
        self.play(*ch.grow(1), run_time=0.7)
        self.wait(max(0.1, d * 0.62 - (self.time - self.start(4))))
        self.play(*ch.grow(2), run_time=0.7)

        # b5: not free: at 4 calls the score is above 100. Straighter, not straight
        self.at(5)
        d = self.dur(5)
        self.wait(d * 0.1)
        self.play(FadeOut(ch), FadeIn(ch4.base), *[FadeIn(VGroup(ch4.bars[i], ch4.vals[i], ch4.labs[i])) for i in range(3)], run_time=0.8)
        self.play(*ch4.grow(3), run_time=0.8)
        note = Tx("straighter, not straight: 16 calls is the practical floor here", 0.34, FG)
        place(note, Stage.foot)
        self.wait(max(0.1, d * 0.5 - (self.time - self.start(5))))
        self.play(FadeOut(t4), FadeIn(note.move_to(np.array([0, 3.4, 0]))), run_time=0.6)
        self.finish()


class S23(BeatScene):
    SID = "s23"

    def construct(self):
        # b0: two measures together: perplexity (fluency, by a judge model) and entropy (variety)
        self.at(0)
        c1 = VGroup(Tx("perplexity", 0.42, DATA), Tx("how fluent a separate judge", 0.3, FG), Tx("model finds the text", 0.3, FG), Tx("lower is better", 0.28, DIM)).arrange(DOWN, buff=0.16)
        c2 = VGroup(Tx("entropy", 0.42, HOT), Tx("how varied the words are", 0.3, FG), Tx("“the the the the the”", 0.3, RED), Tx("is fluent, and useless", 0.28, DIM)).arrange(DOWN, buff=0.16)
        two = VGroup(c1, c2).arrange(RIGHT, buff=1.8, aligned_edge=UP)
        place(two, Stage.main, grow=True, max_grow=1.4)
        d = self.dur(0)
        self.wait(d * 0.22)
        self.play(FadeIn(c1), run_time=0.6)
        self.wait(max(0.1, d * 0.55 - (self.time - self.start(0))))
        self.play(FadeIn(c2[:2]), run_time=0.6)
        self.wait(max(0.1, d * 0.75 - (self.time - self.start(0))))
        self.play(FadeIn(c2[2:]), run_time=0.5)

        # b1: 64 calls, three model sizes: 24.1, 18.6, 17.3. Real text: 17.3
        self.at(1)
        self.play(FadeOut(two), run_time=0.5)
        title = concept_title("perplexity at three model sizes (lower is better)")
        gb = group_bars(["small", "medium", "large"], [[24.1, 18.6, 17.3], [27.7, 22.3, 20.2]], [DATA, DIM], ["flow, 64 calls", "left to right"])
        place(gb, Stage.left_wide)
        leg = VGroup(Tx("the flow model, 64 calls", 0.32, DATA), Tx("left to right, 1,024 calls", 0.32, DIM), Tx("real text: 17.3", 0.32, FG)).arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        place(leg, Stage.right_narrow)
        real = DashedLine(gb.base.get_left() + UP * 17.3 * gb.unit, gb.base.get_right() + UP * 17.3 * gb.unit, dash_length=0.12).set_stroke(FG, 2)
        d = self.dur(1)
        self.play(FadeIn(title), FadeIn(gb.base), FadeIn(gb.labs), run_time=0.6)
        self.play(LaggedStart(*[FadeIn(b) for b in gb.sets[0]], lag_ratio=0.4), FadeIn(leg[0]), run_time=1.6)
        self.wait(max(0.1, d * 0.7 - 2.2))
        self.play(ShowCreation(real), FadeIn(leg[2]), run_time=0.6)

        # b2: left-to-right models of the same sizes: 27.7, 22.3, 20.2
        self.at(2)
        self.wait(self.dur(2) * 0.3)
        self.play(LaggedStart(*[FadeIn(b) for b in gb.sets[1]], lag_ratio=0.4), FadeIn(leg[1]), run_time=1.6)

        # b3: speed after reflow at 16 calls: 15 to 19 times faster one at a time; about 2 times in batches of 64
        self.at(3)
        self.play(*[FadeOut(m) for m in (title, gb, leg, real)], run_time=0.5)
        t3 = concept_title("speed, after reflow, at 16 calls")
        s1 = VGroup(Tx("one text at a time", 0.34, FG), Tx("15 to 19 times faster", 0.5, DATA)).arrange(DOWN, buff=0.25)
        s2 = VGroup(Tx("in batches of 64", 0.34, FG), Tx("about 2 times faster", 0.5, HOT)).arrange(DOWN, buff=0.25)
        sp = VGroup(s1, s2).arrange(RIGHT, buff=2.0)
        place(sp, Stage.main)
        d = self.dur(3)
        self.play(FadeIn(t3), run_time=0.5)
        self.wait(max(0.1, d * 0.4 - 0.5))
        self.play(FadeIn(s1), run_time=0.6)
        self.wait(max(0.1, d * 0.75 - (self.time - self.start(3))))
        self.play(FadeIn(s2), run_time=0.6)

        # b4: the paper's own cautions
        self.at(4)
        self.play(FadeOut(sp), FadeOut(t3), run_time=0.5)
        t4 = concept_title("the cautions (the paper's own)")
        ca = VGroup(Tx("1.  free writing only: no prompts to follow", 0.38, FG),
                    Tx("2.  these two scores do not settle the comparison", 0.38, FG),
                    Tx("3.  the variety is matched only approximately", 0.38, FG)).arrange(DOWN, buff=0.5, aligned_edge=LEFT)
        place(ca, Stage.main)
        d = self.dur(4)
        self.play(FadeIn(t4), run_time=0.5)
        for c_, f in zip(ca, (0.22, 0.48, 0.78)):
            self.wait(max(0.05, d * f - (self.time - self.start(4))))
            self.play(FadeIn(c_), run_time=0.5)
        self.finish()


class S24(BeatScene):
    SID = "s24"

    def construct(self):
        # b0: one idea, built four times
        self.at(0)
        names = ["two numbers", "one word", "a sentence", "the real model"]
        tabs = VGroup(*[Chip(n, 0.34, DIM) for n in names]).arrange(RIGHT, buff=0.4)
        place(tabs, Stage.title)
        big = Tx("one idea, built four times", 0.5, FG)
        self.play(FadeIn(big), run_time=0.6)
        self.wait(max(0.1, self.dur(0) * 0.6 - 0.6))
        self.play(FadeIn(tabs), run_time=0.6)

        def light(k):
            return [t.animate.set_color(HOT if i == k else DIM) for i, t in enumerate(tabs)]

        def bullets(lines, colors):
            g = VGroup(*[Tx(s, 0.34, c) for s, c in zip(lines, colors)]).arrange(DOWN, buff=0.32, aligned_edge=LEFT)
            return place(g, Stage.right)

        # b1: two numbers
        self.at(1)
        xt = XT(zone=Stage.left, pad=0.8, vfill=0.62)
        sel = np.arange(0, 400, 6)
        ax = xt.axes()
        curved = xt.lines(W.ts1[::4], W.flow_paths[::4][:, sel], color=FG, width=1.4, opacity=0.55)
        straight = xt.lines(W.ts1[::50], W.reflow_paths[::50][:, sel], color=HOT, width=1.4, opacity=0.6)
        b1 = bullets(["a generator is a guesser", "follow the guess: noise becomes data", "the first guess is a blur: paths curve", "train again on your own pairs: straight"], [FG, BLUE, FG, HOT])
        self.play(FadeOut(big), *light(0), FadeIn(ax), FadeIn(curved), run_time=0.7)
        d = self.dur(1)
        for k, f in enumerate((0.08, 0.25, 0.5, 0.75)):
            self.wait(max(0.05, d * f - (self.time - self.start(1))))
            extra = [FadeOut(curved), FadeIn(straight)] if k == 3 else []
            self.play(FadeIn(b1[k]), *extra, run_time=0.5)

        # b2: one word
        self.at(2)
        self.play(*[FadeOut(m) for m in (ax, straight, b1)], *light(1), run_time=0.5)
        pl = Plane2(np.array([-3.4, -0.4, 0]), 1.4)
        dots, labs = token_dots(pl)
        S, P, G = path4(np.array([-0.2, -0.9]))
        tr = VMobject().set_points_as_corners(pl.p(S)).set_stroke(HOT, 3)
        b2 = bullets(["the guess is a blend of word locations", "the network is a classifier", "a formula for closeness:", "every path lands exactly on a word"], [BLUE, FG, DATA, DATA])
        self.play(FadeIn(dots), FadeIn(labs), ShowCreation(tr), run_time=0.9)
        d = self.dur(2)
        for k, f in enumerate((0.1, 0.3, 0.55, 0.7)):
            self.wait(max(0.05, d * f - (self.time - self.start(2))))
            self.play(FadeIn(b2[k]), run_time=0.5)

        # b3: a sentence
        self.at(3)
        self.play(*[FadeOut(m) for m in (dots, labs, tr, b2)], *light(2), run_time=0.5)
        grid = ProbGrid(W.demo_P[-1], col_w=0.95, row_h=0.24, gap_x=0.08, size=0.25)
        place(grid, Stage.left)
        b3 = bullets(["one set of bars per slot", "the whole table moves at once", "the previous guess is fed back in"], [BLUE, FG, HOT])
        self.play(FadeIn(grid), run_time=0.6)
        d = self.dur(3)
        for k, f in enumerate((0.15, 0.4, 0.65)):
            self.wait(max(0.05, d * f - (self.time - self.start(3))))
            self.play(FadeIn(b3[k]), run_time=0.5)

        # b4: the whole method as code
        self.at(4)
        self.play(*[FadeOut(m) for m in (grid, b3)], *light(3), run_time=0.5)
        tr_c = CodePanel(TRAIN_FULL, size=0.22, line_gap=0.15)
        sa_c = CodePanel(SAMPLE_FULL, size=0.22, line_gap=0.15)
        h1, h2 = Tx("training step", 0.32, DATA), Tx("sampling loop", 0.32, HOT)
        col = VGroup(h1, tr_c, h2, sa_c).arrange(DOWN, buff=0.28, aligned_edge=LEFT)
        place(col, Stage.main)
        d = self.dur(4)
        self.play(FadeIn(h1), FadeIn(tr_c), run_time=0.7)
        self.wait(max(0.1, d * 0.4 - 0.7))
        self.play(FadeIn(h2), FadeIn(sa_c), run_time=0.7)

        # b5: the shape of that loop: one network, applied again and again, fed its own last answer
        self.at(5)
        self.play(FadeOut(col), FadeOut(tabs), run_time=0.5)
        net = ModelBox("one network", w=3.4, h=1.5, size=0.4)
        net.move_to(DOWN * 0.3)
        loop = ArcBetweenPoints(net.get_right() + UP * 0.3, net.get_left() + UP * 0.3, angle=4.2).set_stroke(HOT, 5)
        loop.add_tip(width=0.26, length=0.26)
        ll = Tx("its own last answer", 0.36, HOT).next_to(loop, UP, buff=0.2)
        again = Tx("applied again and again", 0.36, FG).next_to(net, DOWN, buff=0.5)
        d = self.dur(5)
        self.play(FadeIn(net), run_time=0.6)
        self.wait(max(0.1, d * 0.25 - 0.6))
        self.play(FadeIn(again), run_time=0.4)
        self.wait(max(0.1, d * 0.42 - (self.time - self.start(5))))
        self.play(ShowCreation(loop), FadeIn(ll), run_time=0.9)
        fam = Tx("models that reuse their layers in a loop have this shape", 0.34, DATA)
        place(fam, Stage.foot)
        fam.shift(UP * 0.4)
        self.wait(max(0.1, d * 0.7 - (self.time - self.start(5))))
        self.play(FadeIn(fam), run_time=0.6)

        # b6: the thesis
        self.at(6)
        self.play(*[FadeOut(m) for m in (net, loop, ll, again, fam)], run_time=0.5)
        th = VGroup(Tx("a generator makes a guess, again and again", 0.5, FG),
                    Tx("rectified flow: one guess is nearly enough", 0.5, HOT),
                    Tx("for text: the guess is a multiple-choice answer", 0.5, BLUE)).arrange(DOWN, buff=0.7)
        place(th, Stage.full)
        d = self.dur(6)
        for line, f in zip(th, (0.05, 0.35, 0.62)):
            self.wait(max(0.05, d * f - (self.time - self.start(6))))
            self.play(FadeIn(line), run_time=0.7)
        self.finish(fade=True)
