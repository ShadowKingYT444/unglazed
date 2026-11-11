"""Part 5: self-conditioning, guidance in logit space, and training guidance into one pass."""
from common import *


def loop_arrow(a, b, bend=-1.6, color=BLUE, width=3):
    arc = ArcBetweenPoints(a, b, angle=bend).set_stroke(color, width)
    arc.add_tip(width=0.18, length=0.18)
    return arc


class S17(BeatScene):
    SID = "s17"

    def construct(self):
        k = 9
        Z, G = W.demo_S[k], W.demo_G[k - 1]
        # b0: the model already made a guess at the previous step; why throw it away?
        gh = Heat(G.T, cell=0.5, vmax=1.8, numbers=True).move_to(LEFT * 3.0 + UP * 1.2)
        gl = VGroup(M("\\hat{X}", size=0.42, color=BLUE), Tx("the guess from the step before", 0.24, BLUE)).arrange(RIGHT, buff=0.2).next_to(gh, UP, buff=0.25)
        self.at(0)
        self.wait(self.dur(0) * 0.45)
        self.play(FadeIn(gh), FadeIn(gl), run_time=0.8)
        q = Tx("?", 0.6, HOT).next_to(gh, RIGHT, buff=0.4)
        self.wait(max(0.1, self.dur(0) * 0.82 - (self.time - self.start(0))))
        self.play(FadeIn(q), run_time=0.4)

        # b1: second input C: stack the noisy column and the previous guess, project to the transformer width
        self.at(1)
        zh = Heat(Z.T, cell=0.5, vmax=1.8, numbers=True).move_to(LEFT * 3.0 + UP * 2.6)
        zl = VGroup(M("z", size=0.42, color=HOT), Tx("noisy state", 0.24, HOT)).arrange(RIGHT, buff=0.2).next_to(zh, LEFT, buff=0.3)
        cl = VGroup(M("C", size=0.42, color=BLUE), Tx("previous guess", 0.24, BLUE)).arrange(RIGHT, buff=0.2)
        self.play(FadeOut(q), FadeOut(gl), FadeIn(zh), FadeIn(zl), gh.animate.next_to(zh, DOWN, buff=0.06), run_time=0.9)
        cl.next_to(gh, LEFT, buff=0.3)
        self.play(FadeIn(cl), run_time=0.5)
        colbox = SurroundingRectangle(VGroup(zh.col(1), gh.col(1)), buff=0.04).set_stroke(FG, 2)
        n64 = VGroup(Tx("one position: d + d numbers", 0.24, FG), Tx("paper: 32 + 32 = 64", 0.24, DIM)).arrange(DOWN, buff=0.1, aligned_edge=LEFT).next_to(zh, RIGHT, buff=0.6).shift(DOWN * 0.5)
        box = ModelBox("network", w=2.6, h=1.0, size=0.32).move_to(LEFT * 3.0 + DOWN * 0.9)
        pr = arrow(gh.get_bottom(), box.get_top(), FG, 3, buff=0.12)
        prl = Tx("linear projection to the transformer width", 0.22, DIM).next_to(pr, RIGHT, buff=0.2)
        self.wait(max(0.1, self.dur(1) * 0.45 - 1.4))
        self.play(ShowCreation(colbox), FadeIn(n64), run_time=0.7)
        self.play(ShowCreation(pr), FadeIn(prl), FadeIn(box), run_time=0.8)
        c0 = M("C_0 = 0", size=0.42, color=BLUE).next_to(n64, DOWN, buff=0.5, aligned_edge=LEFT)
        self.wait(max(0.1, self.dur(1) * 0.85 - (self.time - self.start(1))))
        self.play(FadeIn(c0), run_time=0.5)

        # b2: free at sampling time: the last line of the loop
        self.at(2)
        code = CodePanel(SAMPLE, size=0.2, line_gap=0.15).move_to(RIGHT * 3.4 + DOWN * 1.9)
        code.lines.set_opacity(0.3)
        out = arrow(box.get_bottom(), box.get_bottom() + DOWN * 0.9, FG, 3, buff=0.1)
        xo = M("\\hat{X}_i", size=0.42, color=BLUE).next_to(out, DOWN, buff=0.12)
        back = loop_arrow(xo.get_left() + LEFT * 0.15, gh.get_left() + LEFT * 2.6 + DOWN * 0.0, bend=-1.4)
        self.play(FadeOut(n64), FadeOut(c0), FadeOut(prl), FadeOut(colbox), FadeIn(code), ShowCreation(out), FadeIn(xo), run_time=0.9)
        self.play(ShowCreation(back), *code.hl(7), run_time=1.0)
        cc = M("C_{i+1} = \\hat{X}_i", size=0.42, color=BLUE).next_to(code, UP, buff=0.5)
        self.play(FadeIn(cc), run_time=0.5)

        # b3: training: a cold pass without gradients, then a coin per sequence
        self.at(3)
        self.play(*[FadeOut(m) for m in (zh, zl, gh, cl, box, pr, out, xo, back, code, cc)], run_time=0.6)
        xt1 = Tx("x_t", 0.3, HOT)
        b1 = ModelBox("network", w=2.0, h=0.9, size=0.28)
        b1.box.set_stroke(DIM, 2)
        g1 = M("\\hat{X}^u", size=0.42, color=BLUE)
        r1 = VGroup(VGroup(M("x_t,\\ \\ C = 0", size=0.4)), b1, g1).arrange(RIGHT, buff=1.0).move_to(UP * 1.9 + LEFT * 0.5)
        a11 = arrow(r1[0].get_right(), b1.get_left(), DIM, 2.5, buff=0.12)
        a12 = arrow(b1.get_right(), g1.get_left(), DIM, 2.5, buff=0.12)
        t1 = Tx("pass 1: cold, no gradient", 0.24, DIM).next_to(r1, UP, buff=0.3)
        coin = VGroup(Circle(radius=0.38).set_stroke(HOT, 2.5), M("k", size=0.4, color=HOT)).move_to(RIGHT * 3.6 + DOWN * 0.1)
        ctext = VGroup(Tx("heads (k = 1):  C = the cold guess", 0.24, FG), Tx("tails (k = 0):  C = 0", 0.24, FG)).arrange(DOWN, buff=0.12, aligned_edge=LEFT).next_to(coin, DOWN, buff=0.3)
        a_c = arrow(g1.get_bottom(), coin.get_top(), BLUE, 2.5, buff=0.12)
        b2 = ModelBox("network", w=2.0, h=0.9, size=0.28)
        l2 = Tx("logits  →  cross entropy", 0.28, FG)
        r2 = VGroup(VGroup(M("x_t,\\ \\ C", size=0.4)), b2, l2).arrange(RIGHT, buff=1.0).move_to(DOWN * 2.6 + LEFT * 1.6)
        a21 = arrow(r2[0].get_right(), b2.get_left(), FG, 3, buff=0.12)
        a22 = arrow(b2.get_right(), l2.get_left(), FG, 3, buff=0.12)
        t2 = Tx("pass 2: with gradient", 0.24, FG).next_to(r2, UP, buff=0.3).align_to(r2, LEFT)
        a_k = arrow(coin.get_left(), r2[0].get_top() + UP * 0.05, BLUE, 2.5, buff=0.15)
        d = self.dur(3)
        self.play(FadeIn(r1[0]), FadeIn(t1), run_time=0.6)
        self.play(ShowCreation(a11), FadeIn(b1), ShowCreation(a12), FadeIn(g1), run_time=0.9)
        self.wait(max(0.1, d * 0.5 - 1.5))
        self.play(ShowCreation(a_c), FadeIn(coin), run_time=0.7)
        self.wait(max(0.1, d * 0.68 - (self.time - self.start(3))))
        self.play(FadeIn(ctext[0]), run_time=0.5)
        self.wait(max(0.1, d * 0.85 - (self.time - self.start(3))))
        self.play(FadeIn(ctext[1]), run_time=0.5)

        # b4: one network, both jobs; one extra forward pass without gradient
        self.at(4)
        self.play(ShowCreation(a_k), FadeIn(r2[0]), FadeIn(t2), run_time=0.7)
        self.play(ShowCreation(a21), FadeIn(b2), ShowCreation(a22), FadeIn(l2), run_time=0.9)
        code = CodePanel([TRAIN[3]], size=0.22).to_edge(DOWN, buff=0.3)
        self.wait(max(0.1, self.dur(4) * 0.6 - 1.6))
        self.play(FadeIn(code), r2.animate.shift(UP * 0.5), t2.animate.shift(UP * 0.5), a21.animate.shift(UP * 0.5), a22.animate.shift(UP * 0.5), FadeOut(a_k), run_time=0.7)

        # b5: the shape of this: the same network applied again and again, fed its own previous output
        self.at(5)
        self.play(*[FadeOut(m) for m in self.mobjects if m is not self.frame], run_time=0.6)
        nb = ModelBox("network", w=3.0, h=1.4, size=0.36)
        inn = arrow(nb.get_left() + LEFT * 2.2, nb.get_left(), FG, 3, buff=0.1)
        il = M("(z_i,\\ C_i,\\ t_i)", size=0.42).next_to(inn, UP, buff=0.15)
        ou = arrow(nb.get_right(), nb.get_right() + RIGHT * 2.2, FG, 3, buff=0.1)
        ol = M("\\hat{X}_i", size=0.42, color=BLUE).next_to(ou, UP, buff=0.15)
        fb = loop_arrow(ou.get_end() + DOWN * 0.1, inn.get_start() + DOWN * 0.1, bend=-1.5)
        fl = M("C_{i+1} = \\hat{X}_i", size=0.4, color=BLUE).next_to(fb, DOWN, buff=0.2)
        self.play(FadeIn(nb), ShowCreation(inn), FadeIn(il), run_time=0.8)
        self.play(ShowCreation(ou), FadeIn(ol), run_time=0.6)
        self.play(ShowCreation(fb), FadeIn(fl), run_time=1.2)
        self.finish()


class S18(BeatScene):
    SID = "s18"

    def construct(self):
        cold, warm, om = np.array([0.5, 0.3, 0.2]), np.array([0.7, 0.2, 0.1]), 3.0
        lin = cold + om * (warm - cold)
        geo = cold ** (1 - om) * warm ** om
        geo /= geo.sum()
        names = ["token 1", "token 2", "token 3"]

        def barset(vals, color, title, pos):
            g = VGroup()
            base_x, w = pos[0], 2.4
            for i, v in enumerate(vals):
                y = pos[1] - i * 0.42
                lab = Tx(names[i], 0.22, DIM).move_to(np.array([base_x - 0.2, y, 0]), aligned_edge=RIGHT)
                fr = Rectangle(w, 0.24).set_stroke(FAINT, 1).move_to(np.array([base_x + w / 2, y, 0]))
                c = RED if (v < 0 or v > 1) else color
                bar = Rectangle(max(0.01, abs(v) * w), 0.24).set_stroke(width=0).set_fill(c, 0.95)
                bar.move_to(np.array([base_x + (v * w / 2 if v >= 0 else v * w / 2), y, 0]))
                num = Tx(f"{100 * v:.0f}%", 0.22, c).next_to(np.array([base_x + max(v, 1.0 if v > 1 else 0) * w, y, 0]) if v >= 0 else fr.get_right(), RIGHT, buff=0.12)
                g.add(VGroup(lab, fr, bar, num))
            t = Tx(title, 0.24, color).move_to(np.array([base_x + w / 2, pos[1] + 0.5, 0]))
            g.add(t)
            return g

        bc = barset(cold, "#bdbdbd", "cold:  C = 0", (-5.6, 1.8))
        bw = barset(warm, BLUE, "warm:  C = previous guess", (-5.6, -0.6))

        # b0: two predictions for the same input
        self.at(0)
        self.wait(self.dur(0) * 0.4)
        self.play(FadeIn(bc), run_time=0.8)
        self.wait(max(0.1, self.dur(0) * 0.72 - (self.time - self.start(0))))
        self.play(FadeIn(bw), run_time=0.8)

        # b1: guidance: l_g = l(0) + omega (l(C) - l(0))   [Eq. 8]
        self.at(1)
        eq8 = M("\\ell^g", "=", "\\ell(0)", "+", "\\omega", "\\left(\\ell(C) - \\ell(0)\\right)", colors={0: HOT, 4: HOT}, size=0.5).move_to(RIGHT * 2.6 + UP * 2.6)
        tag = Tx("Eq. 8", 0.24, DIM).next_to(eq8, RIGHT, buff=0.3)
        nl = Line(LEFT * 2.2, RIGHT * 2.6).set_stroke(DIM, 2).move_to(RIGHT * 2.6 + UP * 1.0)

        def X(o):
            return nl.get_left() + RIGHT * (0.3 + o * 1.35)

        pts = VGroup()
        for o, lab, col in [(0, "cold", "#bdbdbd"), (1, "warm", BLUE), (3, "ω = 3", HOT)]:
            dd = Dot(X(o), radius=0.09).set_fill(col, 1).set_stroke(width=0)
            pts.add(VGroup(dd, Tx(lab, 0.24, col).next_to(dd, DOWN, buff=0.15)))
        self.play(FadeIn(eq8), FadeIn(tag), run_time=0.8)
        self.play(ShowCreation(nl), FadeIn(pts[0]), FadeIn(pts[1]), run_time=0.7)
        self.wait(max(0.1, self.dur(1) * 0.5 - 1.5))
        ext = arrow(X(1), X(3), HOT, 3, buff=0.12)
        self.play(ShowCreation(ext), FadeIn(pts[2]), run_time=0.8)

        # b2: earlier work extrapolated velocities = extrapolating probabilities linearly
        self.at(2)
        vel = M("v", "=", "\\dfrac{\\sum_w E(w)\\,p(w) - z}{1-t}", size=0.46).move_to(RIGHT * 2.6 + DOWN * 0.9)
        vn = Tx("the velocity is linear in the probabilities", 0.24, RED).next_to(vel, DOWN, buff=0.3)
        self.play(FadeIn(vel), run_time=0.8)
        self.wait(max(0.1, self.dur(2) * 0.45 - 0.8))
        self.play(FadeIn(vn), run_time=0.6)

        # b3: the linear rule with omega = 3: 110%, 0%, -10%
        self.at(3)
        self.play(*[FadeOut(m) for m in (eq8, tag, nl, pts, ext, vel, vn)], run_time=0.5)
        bl = barset(lin, DATA, "linear rule, ω = 3:   p(0) + ω (p(C) − p(0))", (1.2, 1.8))
        self.wait(max(0.1, self.dur(3) * 0.5 - 0.5))
        self.play(FadeIn(bl), run_time=0.9)
        bad = Tx("not a distribution", 0.26, RED).next_to(bl, DOWN, buff=0.2)
        self.wait(max(0.1, self.dur(3) * 0.85 - (self.time - self.start(3))))
        self.play(FadeIn(bad), run_time=0.5)

        # b4: the logit rule: p_g ~ p(0)^(1 - omega) p(C)^omega: 92%, 6%, 2%
        self.at(4)
        bg = barset(geo, HOT, "logit rule, ω = 3", (1.2, -1.0))
        eq16 = M("p^g(w)", "\\propto", "p(w \\mid 0)^{1-\\omega}", "\\,p(w \\mid C)^{\\omega}", colors={0: HOT}, size=0.46).move_to(RIGHT * 2.6 + DOWN * 3.0)
        self.wait(self.dur(4) * 0.25)
        self.play(FadeIn(eq16), bad.animate.set_opacity(0.0), run_time=0.8)
        self.wait(max(0.1, self.dur(4) * 0.6 - (self.time - self.start(4))))
        self.play(FadeIn(bg), run_time=0.9)

        # b5: the singular logits cancel: guidance acts only on the residual
        self.at(5)
        self.play(*[FadeOut(m) for m in (bc, bw, bl, bg, eq16, bad)], run_time=0.5)
        c1 = M("\\ell(C)", "=", "\\log r_t", "+", "f_\\theta(\\cdot\\,;\\,C)", colors={2: HOT, 4: BLUE}, size=0.5)
        c2 = M("\\ell(0)", "=", "\\log r_t", "+", "f_\\theta(\\cdot\\,;\\,0)", colors={2: HOT, 4: BLUE}, size=0.5)
        c3 = M("\\ell(C) - \\ell(0)", "=", "f_\\theta(\\cdot\\,;\\,C) - f_\\theta(\\cdot\\,;\\,0)", colors={2: BLUE}, size=0.5)
        lad = ladder(c1, c2, c3, buff=0.55).move_to(ORIGIN)
        self.play(FadeIn(c1), FadeIn(c2), run_time=0.9)
        x1 = Line(c1[2].get_corner(DL), c1[2].get_corner(UR)).set_stroke(RED, 3)
        x2 = Line(c2[2].get_corner(DL), c2[2].get_corner(UR)).set_stroke(RED, 3)
        self.wait(max(0.1, self.dur(5) * 0.45 - 0.9))
        self.play(ShowCreation(x1), ShowCreation(x2), run_time=0.6)
        self.play(FadeIn(c3), run_time=0.8)
        self.finish()


class S19(BeatScene):
    SID = "s19"

    def construct(self):
        # b0: two calls per step -> one call that takes omega as an input
        def call(label, col):
            b = ModelBox("network", w=1.9, h=0.8, size=0.26)
            b.box.set_stroke(col, 2)
            return VGroup(b, Tx(label, 0.22, col).next_to(b, UP, buff=0.12))

        two = VGroup(call("cold call", "#bdbdbd"), call("warm call", BLUE)).arrange(RIGHT, buff=0.5).move_to(LEFT * 3.4 + UP * 0.6)
        tl = Tx("explicit guidance: 2 calls per step", 0.25, DIM).next_to(two, DOWN, buff=0.3)
        one = call("one call, with ω as an input", HOT).move_to(RIGHT * 3.4 + UP * 0.6)
        ol = Tx("distilled guidance: 1 call per step", 0.25, HOT).next_to(one, DOWN, buff=0.3)
        ar = arrow(two.get_right(), one.get_left(), FG, 3, buff=0.4)
        self.at(0)
        self.wait(self.dur(0) * 0.15)
        self.play(FadeIn(two), FadeIn(tl), run_time=0.8)
        self.wait(max(0.1, self.dur(0) * 0.5 - 1.0))
        self.play(ShowCreation(ar), FadeIn(one), FadeIn(ol), run_time=0.9)

        # b1: the correction delta
        self.at(1)
        self.play(*[FadeOut(m) for m in (two, tl, one, ol, ar)], run_time=0.5)
        lu = M("\\ell^u", ":\\ \\mathrm{cold\\ logits}\\ (C = 0),\\ \\mathrm{no\\ gradient}", colors={0: "#bdbdbd"}, size=0.4)
        lc = M("\\ell^c", ":\\ \\mathrm{warm\\ logits}\\ (C = \\hat{X}^u),\\ \\mathrm{no\\ gradient}", colors={0: BLUE}, size=0.4)
        dl = M("\\Delta", "=", "k\\,\\left(1 - \\dfrac{1}{\\omega}\\right)\\,\\mathrm{sg}\\left[\\ell^c - \\ell^u\\right]", colors={0: HOT}, size=0.5)
        top = ladder(lu, lc, dl, buff=0.4).move_to(UP * 1.9)
        self.play(FadeIn(lu), FadeIn(lc), run_time=0.9)
        self.wait(max(0.1, self.dur(1) * 0.55 - 0.9))
        self.play(FadeIn(dl), run_time=0.8)

        # b2: cross entropy on the logits minus delta   [Eq. 9]
        self.at(2)
        eq9 = M("\\mathcal{L}(\\theta)", "=", "\\mathrm{E}\\left[-\\log\\,\\mathrm{softmax}\\left(\\ell_\\theta(X_t,\\,t;\\ C,\\,\\omega) - \\Delta\\right)_w\\right]", size=0.46)
        fit(eq9, 10.0).move_to(DOWN * 0.6)
        tag = Tx("Eq. 9", 0.24, DIM).next_to(eq9, RIGHT, buff=0.3)
        code = CodePanel([TRAIN[5]], size=0.24).move_to(DOWN * 1.8)
        kk = Tx("k = 0 for half of the sequences: ordinary cross entropy", 0.24, DIM).move_to(DOWN * 2.8)
        self.play(FadeIn(eq9), FadeIn(tag), run_time=0.9)
        self.play(FadeIn(code), run_time=0.6)
        self.wait(max(0.1, self.dur(2) * 0.6 - 1.5))
        self.play(FadeIn(kk), run_time=0.6)

        # b3 + b4: the stationary point
        self.at(3)
        self.play(*[FadeOut(m) for m in (lu, lc, eq9, tag, code, kk)], dl.animate.scale(0.8).to_corner(UR, buff=0.5), run_time=0.7)
        s1 = M("\\ell_\\theta - \\Delta", "=", "\\ell^*", colors={2: DATA}, size=0.5)
        n1 = Tx("cross entropy pushes its input to the true log posterior", 0.23, DIM)
        s2 = M("\\ell^c", "=", "\\ell_\\theta", colors={0: BLUE}, size=0.5)
        n2 = Tx("the warm logits are the network's own output", 0.23, DIM)
        s3 = M("\\ell_\\theta - \\left(1 - \\dfrac{1}{\\omega}\\right)\\left(\\ell_\\theta - \\ell^u\\right)", "=", "\\ell^*", colors={2: DATA}, size=0.5)
        s4 = M("\\dfrac{1}{\\omega}\\,\\ell_\\theta + \\left(1 - \\dfrac{1}{\\omega}\\right)\\ell^u", "=", "\\ell^*", colors={2: DATA}, size=0.5)
        s5 = M("\\ell_\\theta", "=", "\\ell^u + \\omega\\,\\left(\\ell^* - \\ell^u\\right)", colors={0: HOT}, size=0.54)
        lad = ladder(s1, s2, s3, s4, s5, buff=0.42).move_to(LEFT * 1.6 + DOWN * 0.2)
        n1.next_to(s1, RIGHT, buff=0.5)
        n2.next_to(s2, RIGHT, buff=0.5)
        d = self.dur(3)
        self.wait(d * 0.12)
        self.play(FadeIn(s1), FadeIn(n1), run_time=0.8)
        self.wait(max(0.1, d * 0.7 - (self.time - self.start(3))))
        self.play(FadeIn(s2), FadeIn(n2), run_time=0.8)
        self.at(4)
        d = self.dur(4)
        self.play(FadeIn(s3), run_time=0.8)
        self.wait(max(0.1, d * 0.42 - 0.8))
        self.play(FadeIn(s4), run_time=0.8)
        self.wait(max(0.1, d * 0.6 - (self.time - self.start(4))))
        self.play(FadeIn(s5), run_time=0.8)
        box = SurroundingRectangle(s5, buff=0.18).set_stroke(HOT, 2)
        same = Tx("the guidance rule (Eq. 8), with the truth in place of warm", 0.23, HOT).next_to(box, DOWN, buff=0.2)
        fit(same, 7.5)
        self.play(ShowCreation(box), FadeIn(same), run_time=0.7)

        # b5: omega in training and at sampling
        self.at(5)
        self.play(*[FadeOut(m) for m in (lad, n1, n2, box, same, dl)], run_time=0.5)
        ax = Line(LEFT * 4.5, RIGHT * 4.5).set_stroke(DIM, 2).move_to(UP * 0.4)

        def X(o):
            return ax.get_left() + RIGHT * (np.log(o) - np.log(1.0)) / (np.log(6.5) - np.log(1.0)) * 9.0

        band = Line(X(1.5), X(6)).set_stroke(BLUE, 10, 0.6)
        ticks = VGroup()
        for o in (1, 1.5, 2, 3, 4, 6):
            tk = Line(X(o) + UP * 0.12, X(o) + DOWN * 0.12).set_stroke(DIM, 2)
            ticks.add(tk, Tx(f"{o:g}", 0.24, DIM).next_to(tk, DOWN, buff=0.12))
        bl = Tx("training: ω drawn log-uniformly from 1.5 to 6, one per sequence", 0.24, BLUE).next_to(band, UP, buff=0.3)
        s17 = Dot(X(1.7), radius=0.1).set_fill(HOT, 1).set_stroke(width=0)
        s19 = Dot(X(1.9), radius=0.1).set_fill(HOT, 1).set_stroke(width=0)
        sl = Tx("sampling: 1.7 (Small, Medium), 1.9 (Large)", 0.24, HOT).next_to(ax, DOWN, buff=0.8)
        wl = M("\\omega", size=0.44).next_to(ax, RIGHT, buff=0.2)
        self.play(ShowCreation(ax), FadeIn(ticks), FadeIn(wl), run_time=0.7)
        self.play(ShowCreation(band), FadeIn(bl), run_time=0.8)
        self.wait(max(0.1, self.dur(5) * 0.5 - 1.5))
        self.play(FadeIn(s17, scale=2), FadeIn(s19, scale=2), FadeIn(sl), run_time=0.7)
        fin = Tx("one network call per step", 0.3, FG).to_edge(DOWN, buff=0.7)
        self.wait(max(0.1, self.dur(5) * 0.85 - (self.time - self.start(5))))
        self.play(FadeIn(fin), run_time=0.5)
        self.finish()
