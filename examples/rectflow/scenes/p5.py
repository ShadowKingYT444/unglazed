"""A sentence: one set of bars per slot, the whole loop, self-conditioning and guidance, and the embedding table."""
from common import *

P_DEMO, S_DEMO = W.demo_P, W.demo_S
N_CALL = len(P_DEMO)
GREY2 = "#bdbdbd"


def barset(vals, color, title, pos, names=("word 1", "word 2", "word 3"), w=2.6, size=0.3):
    """Three probability bars that may go below 0 or above 1 (drawn red when they do)."""
    g = VGroup()
    for i, v in enumerate(vals):
        y = pos[1] - i * 0.52
        lab = Tx(names[i], size, DIM).move_to(np.array([pos[0] - 0.42, y, 0]), aligned_edge=RIGHT)
        fr = Rectangle(w, 0.3).set_stroke(FAINT, 1).move_to(np.array([pos[0] + w / 2, y, 0]))
        c = RED if (v < 0 or v > 1) else color
        bar = Rectangle(max(0.01, abs(v) * w), 0.3).set_stroke(width=0).set_fill(c, 0.95)
        bar.move_to(np.array([pos[0] + v * w / 2, y, 0]))
        num = Tx(f"{100 * v:.0f}%", size, c).next_to(np.array([pos[0] + max(v, 0) * w, y, 0]) if v <= 1 else bar.get_right(), RIGHT, buff=0.12)
        g.add(VGroup(lab, fr, bar, num))
    g.add(Tx(title, size + 0.02, color).move_to(np.array([pos[0] + w / 2, pos[1] + 0.6, 0])))
    return g


class S18(BeatScene):
    SID = "s18"

    def construct(self):
        rng = np.random.default_rng(18)
        card(self, "5", "a sentence")

        # b0: in a sentence the right word in one slot depends on all the others
        words = "the cat ___ on the mat".split()
        row = token_row(words, size=0.4, w=1.35)
        place(row, Stage.main)
        row.shift(UP * 0.8)
        gap = row[2]
        gap.label.set_opacity(0)
        gap.box.set_stroke(HOT, 3)
        ok = Tx("sat", 0.42, DATA).next_to(gap, DOWN, buff=0.6)
        no = Tx("tree", 0.42, RED).next_to(ok, DOWN, buff=0.3)
        strike = Line(no.get_left() + LEFT * 0.1, no.get_right() + RIGHT * 0.1).set_stroke(RED, 3)
        d = self.dur(0)
        self.play(FadeIn(row), run_time=0.6)
        self.wait(max(0.1, self.start(0) + d * 0.7 - self.time))
        self.play(FadeIn(ok), FadeIn(no), ShowCreation(strike), run_time=0.7)

        # b1: the thing we move is a table: one column of numbers per slot, all noise, all moving at once
        self.at(1)
        self.play(*[FadeOut(m) for m in (row, ok, no, strike)], run_time=0.5)
        slots = token_row([""] * 6, size=0.36, w=1.35)
        for c in slots:
            c.box.set_stroke(DIM, 1.5)
        sl = VGroup(*[Tx(f"slot {k + 1}", 0.28, DIM).move_to(c) for k, c in enumerate(slots)])
        a0 = rng.normal(size=(4, 6))
        heat = Heat(a0, cell=0.62, vmax=2.2)
        table = VGroup(VGroup(slots, sl), heat).arrange(DOWN, buff=0.35)
        place(table, Stage.left_wide)
        spread_cols(heat, [c.get_center()[0] for c in slots])
        note = VGroup(Tx("one column of numbers", 0.32, FG), Tx("for every slot", 0.32, FG), Tx("all noise at the start", 0.32, NOISE), Tx("all moving at once", 0.32, HOT)).arrange(DOWN, buff=0.16)
        note[2:].shift(DOWN * 0.3)
        place(note, Stage.right_narrow)
        d = self.dur(1)
        self.play(FadeIn(slots), FadeIn(sl), FadeIn(heat), FadeIn(note[:2]), run_time=0.8)
        self.wait(max(0.1, d * 0.55 - 0.8))
        self.play(FadeIn(note[2]), run_time=0.4)
        vt = ValueTracker(0)
        a1 = rng.normal(size=(4, 6))
        heat.add_updater(lambda m: m.set_values((1 - vt.get_value()) * a0 + vt.get_value() * a1))
        self.wait(max(0.1, d * 0.75 - (self.time - self.start(1))))
        self.play(vt.animate.set_value(1), FadeIn(note[3]), run_time=1.4)
        heat.clear_updaters()

        # b2: the network reads the whole noisy table, both directions, and answers for every slot
        self.at(2)
        self.play(FadeOut(note), VGroup(slots, sl).animate.set_opacity(0), run_time=0.4)
        net = RoundedRectangle(width=heat.get_width() + 0.5, height=0.85, corner_radius=0.12).set_stroke(FG, 2)
        net.next_to(heat, DOWN, buff=0.45)
        nl = Tx("network: reads every column, in both directions", 0.3, FG).move_to(net)
        fit(nl, net.get_width() - 0.3)
        ups = VGroup(*[arrow(np.array([c.get_center()[0], heat.get_bottom()[1] - 0.05, 0]), np.array([c.get_center()[0], net.get_top()[1] + 0.02, 0]), DIM, 2.5, buff=0) for c in slots])
        both = VGroup(arrow(net.get_left() + RIGHT * 0.3 + DOWN * 0.62, net.get_right() + LEFT * 0.3 + DOWN * 0.62, BLUE, 3, buff=0),
                      arrow(net.get_right() + LEFT * 0.3 + DOWN * 0.8, net.get_left() + RIGHT * 0.3 + DOWN * 0.8, BLUE, 3, buff=0))
        grp = VGroup(heat, net, nl, ups)
        self.play(grp.animate.shift(UP * 1.0), run_time=0.01)
        self.play(FadeIn(net), FadeIn(nl), FadeIn(ups), run_time=0.7)
        mid = P_DEMO[9]
        outs = VGroup()
        for l in range(6):
            top = np.argsort(-mid[l])[:3]
            b_ = Bars([LANG.vocab[v] for v in top], mid[l][top], width=0.75, bar_h=0.2, gap=0.12, size=0.24)
            b_.move_to(np.array([slots[l].get_center()[0] - 0.1, net.get_bottom()[1] - 0.95, 0]))
            outs.add(b_)
        d = self.dur(2)
        self.wait(max(0.1, d * 0.6 - 0.8))
        self.play(LaggedStart(*[FadeIn(o) for o in outs], lag_ratio=0.15), run_time=1.2)
        ol = VGroup(Tx("one set of bars", 0.32, BLUE), Tx("per slot", 0.32, BLUE)).arrange(DOWN, buff=0.14)
        place(ol, Stage.right_narrow)
        self.play(FadeIn(ol), run_time=0.4)

        # b3: the worry: the slots are not independent; should it say which combinations go together?
        self.at(3)
        combos = VGroup(Tx("cat … sat", 0.34, FG), Tx("bird … sang", 0.34, FG), Tx("cat … sang ?", 0.34, RED)).arrange(DOWN, buff=0.22)
        worry = VGroup(Tx("which combinations", 0.32, HOT), Tx("go together?", 0.32, HOT)).arrange(DOWN, buff=0.14)
        rhs = VGroup(worry, combos).arrange(DOWN, buff=0.5)
        place(rhs, Stage.right_narrow)
        self.wait(self.dur(3) * 0.35)
        self.play(FadeOut(ol), FadeIn(rhs), run_time=0.6)

        # b4: it does not have to: each column moves toward its own guess, which needs only its own chances
        self.at(4)
        hi = focus(VGroup(heat.col(2), outs[2]), HOT, buff=0.1)
        why = VGroup(Tx("each column moves toward", 0.3, FG), Tx("its own guess", 0.34, BLUE), Tx("context changes the bars", 0.3, FG), Tx("the output stays", 0.3, FG), Tx("6 slots × 18 words", 0.34, DATA)).arrange(DOWN, buff=0.16)
        why[2:].shift(DOWN * 0.3)
        place(why, Stage.right_narrow)
        d = self.dur(4)
        self.wait(d * 0.12)
        self.play(FadeOut(rhs), ShowCreation(hi), FadeIn(why[:2]), run_time=0.7)
        self.wait(max(0.1, d * 0.6 - (self.time - self.start(4))))
        self.play(FadeIn(why[2]), run_time=0.6)
        self.wait(max(0.1, d * 0.8 - (self.time - self.start(4))))
        self.play(FadeIn(why[3:]), run_time=0.5)
        self.finish()


class S19(BeatScene):
    SID = "s19"

    def construct(self):
        call = ValueTracker(0.0)

        def Pnow():
            return lerp_traj(P_DEMO, call.get_value() / (N_CALL - 1))

        grid = ProbGrid(P_DEMO[0])
        slots = token_row([""] * 6, size=0.36, w=1.15, gap=0.12)
        grp = VGroup(slots, grid).arrange(DOWN, buff=0.25)
        place(grp, Stage.left_wide)
        grp.move_to(np.array([-2.0, 0.0, 0]))
        slots.shift(RIGHT * (grid.col_x(0) - slots[0].get_center()[0]))
        # the word on top of each slot is the current favourite, as bright as the network is sure
        def fav(l, v):
            def upd(m):
                p = Pnow()[l]
                m.set_opacity(float(p[v]) if int(p.argmax()) == v else 0.0)
            return upd

        tops = VGroup()
        for l in range(6):
            cands = sorted(set(P_DEMO[:, l].argmax(1)))
            for v in cands:
                t = Tx(LANG.vocab[v], 0.36, FG).move_to(slots[l])

                t.add_updater(fav(l, int(v)))
                tops.add(t)
        counter = Tx("call 1 of 16", 0.4, HOT)

        # b0: twelve sentences, a perfect classifier, six columns of noise
        self.at(0)
        sents = VGroup(*[Tx(s, 0.28, DIM) for s in W.sentences[:6]], Tx("… twelve sentences", 0.28, DIM)).arrange(DOWN, buff=0.14, aligned_edge=LEFT)
        place(sents, Stage.right_narrow)
        self.play(FadeIn(sents), run_time=0.7)
        self.wait(max(0.1, self.dur(0) * 0.55 - 0.7))
        self.play(FadeIn(slots), FadeIn(grid.labels), *[FadeIn(grid.column(c)) for c in range(6)], run_time=1.0)
        self.add(grid, tops)

        # b1: first call: the bars are spread out
        self.at(1)
        place(counter, Stage.right_narrow)
        counter.shift(UP * 1.6)
        n1 = VGroup(Tx("every slot is a mix", 0.32, FG), Tx("of several words", 0.32, FG)).arrange(DOWN, buff=0.14).next_to(counter, DOWN, buff=0.6)
        self.play(FadeOut(sents), FadeIn(counter), FadeIn(n1), run_time=0.6)
        grid.add_updater(lambda m: m.set_values(Pnow()))

        def step_to(k, run_time):
            nonlocal counter
            new = Tx(f"call {k + 1} of 16", 0.4, HOT).move_to(counter)
            self.play(call.animate.set_value(k), FadeOut(counter), FadeIn(new), run_time=run_time)
            counter = new

        # b2: a few calls later one slot sharpens; the others move to agree
        self.at(2)
        self.play(FadeOut(n1), run_time=0.3)
        d = self.dur(2)
        for k in range(1, 10):
            step_to(k, d * 0.03)
            self.wait(d * 0.015)
        hi = focus(VGroup(slots[1], grid.column(1)), HOT, buff=0.06)
        n2 = VGroup(Tx("one slot sharpens", 0.32, HOT), Tx("the others move", 0.32, FG), Tx("to agree with it", 0.32, FG)).arrange(DOWN, buff=0.14).next_to(counter, DOWN, buff=0.6)
        self.play(ShowCreation(hi), FadeIn(n2[0]), run_time=0.5)
        for k in range(10, 13):
            step_to(k, d * 0.05)
            self.wait(d * 0.03)
        self.play(FadeIn(n2[1:]), run_time=0.4)

        # b3: by the last call every slot has chosen; nobody wrote it left to right
        self.at(3)
        self.play(FadeOut(hi), FadeOut(n2), run_time=0.3)
        d = self.dur(3)
        for k in range(13, 16):
            step_to(k, d * 0.08)
            self.wait(d * 0.04)
        n3 = VGroup(Tx("“" + W.demo_sent + "”", 0.3, DATA), Tx("not written left to right", 0.3, FG)).arrange(DOWN, buff=0.25).next_to(counter, DOWN, buff=0.6)
        fit(n3, 3.9)
        self.play(FadeIn(n3), run_time=0.5)

        # b4: the last call moves nothing: it reads off the most likely word. 16 here; 64 for 1,024 words
        self.at(4)
        grid.clear_updaters()
        for t in tops:
            t.clear_updaters()
        final = P_DEMO[-1].argmax(1)
        self.play(*[t.animate.set_opacity(1.0) for t in tops if t.get_opacity() > 0.05], run_time=0.6)
        rd = VGroup(Tx("the last call only reads", 0.3, FG), Tx("the most likely words", 0.3, FG)).arrange(DOWN, buff=0.14)
        cmp_ = VGroup(Tx("the real model:", 0.3, DIM), Tx("64 calls for 1,024 words", 0.32, DATA), Tx("left to right: 1,024 calls", 0.32, RED)).arrange(DOWN, buff=0.18)
        rhs = VGroup(rd, cmp_).arrange(DOWN, buff=0.6)
        place(rhs, Stage.right_narrow)
        self.play(FadeOut(n3), FadeOut(counter), FadeIn(rd), run_time=0.5)
        self.wait(max(0.1, self.dur(4) * 0.55 - 1.1))
        self.play(FadeIn(cmp_), run_time=0.6)

        # b5: the code: the rule from the two-number world, unchanged
        self.at(5)
        self.play(*[FadeOut(m) for m in self.mobjects if m is not self.frame], run_time=0.5)
        code = CodePanel(LOOP_CODE, size=0.28)
        place(code, Stage.main)
        title = concept_title("the same rule as in the two-number world")
        self.play(FadeIn(code), FadeIn(title), run_time=0.7)
        d = self.dur(5)
        for idx, f in (((2, 3), 0.5), ((5,), 0.65), ((1, 2, 3), 0.82)):
            self.wait(max(0.05, d * f - (self.time - self.start(5))))
            self.play(*code.hl(*idx), run_time=0.4)
        self.finish()


class S20(BeatScene):
    SID = "s20"

    def construct(self):
        # b0: the loop throws the guess away; keep it: feed it back in. Self-conditioning
        self.at(0)
        z = Chip("noisy table", 0.34, HOT)
        net = ModelBox("network", w=2.6, h=1.2, size=0.36)
        g = Chip("guess", 0.34, BLUE)
        chain = VGroup(z, arrow(ORIGIN, RIGHT * 1.0, FG, 3, buff=0), net, arrow(ORIGIN, RIGHT * 1.0, FG, 3, buff=0), g).arrange(RIGHT, buff=0.35)
        place(chain, Stage.main)
        used = Tx("used once, then forgotten", 0.3, RED).next_to(g, DOWN, buff=0.4)
        d = self.dur(0)
        self.play(FadeIn(chain), run_time=0.7)
        self.wait(max(0.1, d * 0.2 - 0.7))
        self.play(FadeIn(used), run_time=0.5)
        back = ArcBetweenPoints(g.get_top() + UP * 0.05, net.get_top() + UP * 0.05, angle=1.6).set_stroke(BLUE, 4)
        back.add_tip(width=0.2, length=0.2)
        bl = Tx("the previous guess, as a second input", 0.32, BLUE).next_to(back, UP, buff=0.2)
        self.wait(max(0.1, d * 0.5 - (self.time - self.start(0))))
        self.play(FadeOut(used), ShowCreation(back), FadeIn(bl), run_time=0.9)
        name = concept_title("self-conditioning")
        self.wait(max(0.1, d * 0.82 - (self.time - self.start(0))))
        self.play(FadeIn(name), run_time=0.5)

        # b1: training: one pass without the extra input, then a coin
        self.at(1)
        self.play(*[FadeOut(m) for m in (chain, back, bl)], run_time=0.5)
        p1 = VGroup(Tx("pass 1", 0.34, DIM), Tx("no extra input  →  a rough guess", 0.34, FG)).arrange(RIGHT, buff=0.5)
        coin = Circle(radius=0.42).set_stroke(HOT, 3)
        ct = Tx("coin", 0.28, HOT).move_to(coin)
        heads = VGroup(Tx("heads", 0.34, HOT), Tx("pass 2 sees the rough guess", 0.34, BLUE)).arrange(RIGHT, buff=0.5)
        tails = VGroup(Tx("tails", 0.34, HOT), Tx("pass 2 sees nothing", 0.34, GREY2)).arrange(RIGHT, buff=0.5)
        learn = Tx("so it learns to start from nothing, and to improve", 0.32, FG)
        col = VGroup(p1, VGroup(coin, ct), heads, tails, learn).arrange(DOWN, buff=0.42)
        learn.shift(DOWN * 0.3)
        place(col, Stage.main)
        d = self.dur(1)
        for m, f in ((p1, 0.1), (VGroup(coin, ct), 0.42), (heads, 0.55), (tails, 0.68), (learn, 0.8)):
            self.wait(max(0.05, d * f - (self.time - self.start(1))))
            self.play(FadeIn(m), run_time=0.5)

        # b2: two predictions for the same input; guidance pushes further in the direction the help moved things
        self.at(2)
        self.play(FadeOut(col), FadeOut(name), run_time=0.5)
        cold, warm, om = np.array([0.5, 0.3, 0.2]), np.array([0.7, 0.2, 0.1]), 3.0
        lin = cold + om * (warm - cold)
        geo = cold ** (1 - om) * warm ** om
        geo /= geo.sum()
        bc = barset(cold, GREY2, "cold: without help", (-5.3, 1.9))
        bw = barset(warm, BLUE, "warm: with the previous guess", (-5.3, -0.9))
        d = self.dur(2)
        self.wait(d * 0.2)
        self.play(FadeIn(bc), run_time=0.6)
        self.wait(max(0.1, d * 0.35 - (self.time - self.start(2))))
        self.play(FadeIn(bw), run_time=0.6)
        nl = Line(LEFT * 2.6, RIGHT * 2.6).set_stroke(DIM, 2).move_to(np.array([3.4, 0.9, 0]))

        def X(o):
            return nl.get_left() + RIGHT * (0.4 + o * 1.5)

        pts = VGroup()
        for o, lab, col_ in [(0, "cold", GREY2), (1, "warm", BLUE), (3, "pushed", HOT)]:
            dd = Dot(X(o), radius=0.1).set_fill(col_, 1).set_stroke(width=0)
            pts.add(VGroup(dd, Tx(lab, 0.3, col_).next_to(dd, DOWN, buff=0.18)))
        gname = Tx("guidance", 0.4, HOT).next_to(nl, UP, buff=0.9)
        ext = arrow(X(1), X(3), HOT, 4, buff=0.14)
        self.wait(max(0.1, d * 0.55 - (self.time - self.start(2))))
        self.play(ShowCreation(nl), FadeIn(pts[0]), FadeIn(pts[1]), FadeIn(gname), run_time=0.7)
        self.wait(max(0.1, d * 0.75 - (self.time - self.start(2))))
        self.play(ShowCreation(ext), FadeIn(pts[2]), run_time=0.7)

        # b3: push probabilities three times as far: 110%, 0%, -10%
        self.at(3)
        self.play(*[FadeOut(m) for m in (nl, pts, gname, ext)], run_time=0.5)
        bl_ = barset(lin, DATA, "push the probabilities, 3×", (1.6, 1.9))
        bad = Tx("not a valid answer", 0.32, RED).next_to(bl_, DOWN, buff=0.3)
        d = self.dur(3)
        self.wait(max(0.1, d * 0.6 - 0.5))
        self.play(FadeIn(bl_), run_time=0.7)
        self.wait(max(0.1, d * 0.88 - (self.time - self.start(3))))
        self.play(FadeIn(bad), run_time=0.4)

        # b4: push the logits instead: 92, 6, 2. Trained into one pass
        self.at(4)
        bg = barset(geo, HOT, "push the logits, 3×", (1.6, -0.9))
        d = self.dur(4)
        self.wait(d * 0.12)
        self.play(FadeOut(bad), FadeIn(bg), run_time=0.7)
        ok = Tx("always a valid answer", 0.32, DATA).next_to(bg, DOWN, buff=0.3)
        self.wait(max(0.1, d * 0.4 - (self.time - self.start(4))))
        self.play(FadeIn(ok), run_time=0.4)
        one = Tx("the network is trained to output the pushed logits directly: no extra calls", 0.32, FG)
        place(one, Stage.title)
        self.wait(max(0.1, d * 0.6 - (self.time - self.start(4))))
        self.play(FadeIn(one), run_time=0.6)
        self.finish()


class S21(BeatScene):
    SID = "s21"

    def construct(self):
        rng = np.random.default_rng(21)
        pl = Plane2(np.array([-3.5, -0.45, 0]), 1.5)
        E = LANG.E
        # Words that are used alike sit almost on top of each other. For the picture only, each tight group is
        # opened into a small ring around its centre, so that the labels can be read.
        groups, left_ = [], list(range(len(E)))
        while left_:
            g = [left_.pop(0)]
            grew = True
            while grew:
                grew = False
                for j in list(left_):
                    if min(np.linalg.norm(E[j] - E[i]) for i in g) < 0.45:
                        g.append(j), left_.remove(j)
                        grew = True
            groups.append(g)
        Ej, out = E.copy(), np.zeros_like(E)
        for g in groups:
            c = E[g].mean(0)
            if len(g) == 1:
                out[g[0]] = [0.0, 1.0]
                continue
            r = 0.15 + 0.04 * len(g)
            for k, i in enumerate(sorted(g, key=lambda i: LANG.vocab[i])):
                a_ = 2 * np.pi * k / len(g) + 0.3
                out[i] = [np.cos(a_), np.sin(a_)]
                Ej[i] = c + r * out[i]
        nouns = {"cat", "dog", "bird", "tree", "door", "rug", "mat", "park"}
        centre = E[[LANG.vocab.index(w) for w in nouns]].mean(0)
        rad = 0.66

        def inside_idx(P_):
            return [i for i, e in enumerate(P_) if np.linalg.norm(e - centre) < rad]

        for seed in range(200):                                # a shuffle that leaves few nouns in the circle
            perm = np.random.default_rng(seed).permutation(len(E))
            got = [LANG.vocab[perm[i]] for i in inside_idx(Ej)]
            if sum(w in nouns for w in got) <= 3:
                break
        names_r = [LANG.vocab[perm[i]] for i in range(len(E))]  # the same spots, with the words shuffled onto them

        def table(names, color=DATA):
            dots = VGroup(*[Dot(pl.p(e), radius=0.06).set_fill(color, 1).set_stroke(width=0) for e in Ej])
            labs = VGroup(*[Tx(w, 0.28, FG).move_to(pl.p(e) + np.array([o[0] * 1.25, o[1], 0]) * 0.3) for w, e, o in zip(names, Ej, out)])
            return dots, labs

        d_s, l_s = table(LANG.vocab)
        d_r, l_r = table(names_r)

        def inside(names):
            return [names[i] for i in inside_idx(Ej)]

        # b0: where the words sit: in principle it does not matter; in practice a great deal
        self.at(0)
        title = concept_title("does it matter where each word sits?")
        self.play(FadeIn(title), FadeIn(d_r), FadeIn(l_r), run_time=0.8)
        ans = VGroup(Tx("in principle: no", 0.36, DIM), Tx("in practice: a great deal", 0.36, HOT)).arrange(DOWN, buff=0.35)
        place(ans, Stage.right)
        d = self.dur(0)
        self.wait(max(0.1, d * 0.5 - 0.8))
        self.play(FadeIn(ans[0]), run_time=0.4)
        self.wait(max(0.1, d * 0.8 - (self.time - self.start(0))))
        self.play(FadeIn(ans[1]), run_time=0.4)

        # b1: a half-noisy point with a random table: the words it could be have nothing in common
        self.at(1)
        self.play(FadeOut(ans), FadeOut(title), run_time=0.4)
        t1 = concept_title("a random table")
        hz = halo(pl.p(centre), rad * pl.u, HOT, 0.12, 2.5)
        pt = Dot(pl.p(centre), radius=0.09).set_fill(HOT, 1).set_stroke(FG, 1.5)
        in_r = inside(names_r)
        could = VGroup(Tx("a half-noisy point could be:", 0.32, FG), Tx(",  ".join(in_r), 0.38, HOT), Tx("nothing in common", 0.32, RED)).arrange(DOWN, buff=0.3)
        fit(could[1], 5.8)
        place(could, Stage.right)
        d = self.dur(1)
        self.play(FadeIn(t1), run_time=0.4)
        self.wait(max(0.1, d * 0.25 - 0.4))
        self.play(FadeIn(hz), FadeIn(pt), FadeIn(could[0]), run_time=0.6)
        self.wait(max(0.1, d * 0.5 - (self.time - self.start(1))))
        self.play(FadeIn(could[1]), run_time=0.5)
        self.wait(max(0.1, d * 0.75 - (self.time - self.start(1))))
        self.play(FadeIn(could[2]), run_time=0.4)

        # b2: words used alike sit together: the same point already says "an animal or a place goes here"
        self.at(2)
        t2 = concept_title("words that are used alike sit together")
        in_s = inside(LANG.vocab)
        could2 = VGroup(Tx("the same point could be:", 0.32, FG), Tx(",  ".join(in_s), 0.38, DATA), Tx("an animal or a place goes here", 0.32, DATA)).arrange(DOWN, buff=0.3)
        fit(could2[1], 5.8)
        place(could2, Stage.right)
        self.play(FadeOut(could), FadeOut(t1), FadeOut(d_r), FadeOut(l_r), FadeIn(d_s), FadeIn(l_s), FadeIn(t2), run_time=1.0)
        self.add(hz, pt)
        d = self.dur(2)
        self.wait(max(0.1, d * 0.3 - 1.0))
        self.play(FadeIn(could2[:2]), run_time=0.5)
        self.wait(max(0.1, d * 0.5 - (self.time - self.start(2))))
        self.play(FadeIn(could2[2]), run_time=0.5)

        # b3: the recipe: count which words come right before and right after; take square roots
        self.at(3)
        self.play(FadeOut(could2), FadeOut(hz), FadeOut(pt), FadeOut(t2), run_time=0.4)
        t3 = concept_title("the recipe (no training)")
        ctx = lambda w: (sorted({s.split()[i - 1] for s in W.sentences for i, x in enumerate(s.split()) if x == w and i > 0}),
                         sorted({s.split()[i + 1] for s in W.sentences for i, x in enumerate(s.split()) if x == w and i + 1 < len(s.split())}))
        rows = VGroup()
        for w in ("cat", "dog"):
            b_, a_ = ctx(w)
            rows.add(VGroup(Tx(", ".join(b_), 0.3, BLUE), Chip(w, 0.34, FG), Tx(", ".join(a_), 0.3, HOT)).arrange(RIGHT, buff=0.3))
        head = VGroup(Tx("right before", 0.28, BLUE), Tx("right after", 0.28, HOT)).arrange(RIGHT, buff=1.6)
        steps = VGroup(Tx("1.  count the neighbours of every word", 0.32, FG), Tx("2.  take square roots of the counts", 0.32, FG),
                       Tx("     so distance compares how words are used", 0.28, DIM)).arrange(DOWN, buff=0.2, aligned_edge=LEFT)
        col = VGroup(head, rows.arrange(DOWN, buff=0.3), steps).arrange(DOWN, buff=0.45)
        place(col, Stage.right)
        d = self.dur(3)
        self.play(FadeIn(t3), run_time=0.4)
        self.wait(max(0.1, d * 0.2 - 0.4))
        self.play(FadeIn(head), FadeIn(rows), FadeIn(steps[0]), run_time=0.7)
        self.wait(max(0.1, d * 0.62 - (self.time - self.start(3))))
        self.play(FadeIn(steps[1:]), run_time=0.6)

        # b4: keep the 32 most important directions; scale so a word's signal is the size of the noise
        self.at(4)
        more = VGroup(Tx("3.  keep the 32 most important directions", 0.32, FG), Tx("4.  scale: a word's signal = the size of the noise", 0.32, FG),
                      Tx("every toy picture here uses this recipe", 0.3, DATA)).arrange(DOWN, buff=0.25, aligned_edge=LEFT)
        more[2].shift(DOWN * 0.3)
        fit(more, 6.2)
        place(more, Stage.right)
        self.play(FadeOut(col), FadeIn(more[0]), run_time=0.6)
        d = self.dur(4)
        self.wait(max(0.1, d * 0.3 - 0.6))
        self.play(FadeIn(more[1]), run_time=0.5)
        self.wait(max(0.1, d * 0.7 - (self.time - self.start(4))))
        self.play(FadeIn(more[2]), run_time=0.5)

        # b5: same model: random table 83.6, the paper's table 42.1
        self.at(5)
        self.play(*[FadeOut(m) for m in self.mobjects if m is not self.frame], run_time=0.5)
        ch = BarChart(["random table", "the paper's table"], [83.6, 42.1], colors=[DIM, DATA], unit=0.05, bar_w=1.7, gap=1.0, size=0.32, val_size=0.4)
        place(ch, Stage.main)
        t5 = concept_title("same model, two tables  (perplexity: lower is better)")
        self.play(FadeIn(t5), FadeIn(ch.base), run_time=0.6)
        d = self.dur(5)
        self.wait(max(0.05, d * 0.4 - 0.6))
        self.play(*ch.grow(0), run_time=0.7)
        self.wait(max(0.05, d * 0.7 - (self.time - self.start(5))))
        self.play(*ch.grow(1), run_time=0.7)
        self.finish()
