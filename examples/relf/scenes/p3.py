"""Part 3: singular logits. What a bounded network does, the split, the theorem, commitment and landing."""
from common import *
from p2 import ORDER, ROWS, prob_grid

CLASS_LABELS = [("the", LEFT), ("a", UP), ("on · to · in · by", UP), ("sat · ran · slept · sang", LEFT), ("cat · dog · bird · mat · rug · door · park · tree", DOWN)]
CLASS_AT = ["the", "a", "in", "ran", "dog"]


def vocab_scatter(pl, radius=0.06, size=0.22):
    """All 18 toy tokens at their Hellinger-SVD positions; one label per cluster (tokens of a class nearly coincide)."""
    dots = VGroup(*[Dot(pl.p(e), radius=radius).set_fill(DATA, 1).set_stroke(width=0) for e in LANG.E])
    labs = VGroup()
    for (txt, side), w in zip(CLASS_LABELS, CLASS_AT):
        labs.add(Tx(txt, size, DIM).next_to(pl.p(LANG.E[LANG.vocab.index(w)]), side, buff=0.22))
    return dots, labs


class S09(BeatScene):
    SID = "s09"

    def construct(self):
        S_, P_, G_ = W.cap["capped"]["ex"]
        l = 4                                           # the position that ends on "the"
        tok = int(P_[-1, l].argmax())
        pl = Plane2(center=LEFT * 2.9 + DOWN * 0.2, unit=1.8)
        dots, labs = vocab_scatter(pl)
        cap_l = Tx("a perfect denoiser, logit gaps capped at B = 6", 0.26, BLUE).to_edge(UP, buff=0.45)
        path = VMobject().set_points_as_corners(pl.p(S_[:, l])).set_stroke(HOT, 2.5)
        end = G_[-1, l]
        miss = float(np.linalg.norm(end - LANG.E[tok]))

        # b0: the toy sampler with capped logit gaps
        self.at(0)
        self.play(FadeIn(dots), FadeIn(labs), FadeIn(cap_l), run_time=1.0)
        self.play(ShowCreation(path), run_time=self.dur(0) * 0.5, rate_func=linear)

        # b1: the top token gets about 95%, so the soft token is 95% of the right row plus 5% of the others
        self.at(1)
        top = np.argsort(-P_[-1, l])[:4]
        names = [LANG.vocab[i] for i in top]
        bars = Bars(names, P_[-1, l, top], width=2.6, bar_h=0.26, gap=0.16, size=0.28).move_to(RIGHT * 3.6 + UP * 1.4)
        pct = VGroup(*[Tx(f"{100 * P_[-1, l, i]:.1f}%", 0.26, FG if k == 0 else RED).next_to(bars.rows[k][1], RIGHT, buff=0.15) for k, i in enumerate(top)])
        bt = Tx("final probabilities at this position", 0.24, DIM).next_to(bars, UP, buff=0.3)
        ptop = float(P_[-1, l, tok])
        soft = M("\\hat{x}", "=", f"{ptop:.2f}\\,E(\\mathrm{{{LANG.vocab[tok]}}})", "+", f"{1 - ptop:.2f}\\,(\\mathrm{{average\\ of\\ the\\ others}})", colors={0: BLUE, 4: RED}, size=0.42)
        fit(soft, 6.0).move_to(RIGHT * 3.6 + DOWN * 0.6)
        self.play(FadeIn(bars), FadeIn(pct), FadeIn(bt), run_time=0.9)
        self.wait(max(0.1, self.dur(1) * 0.45 - 0.9))
        self.play(FadeIn(soft), run_time=0.8)

        # b2: the state ends at the soft token: near a token, not on it
        self.at(2)
        tgt, gp = pl.p(LANG.E[tok]), pl.p(end)
        ZK = 0.11
        g = ring(gp, 0.018, RED, 2)
        zc = Dot(gp, radius=0.009).set_fill(HOT, 1).set_stroke(width=0)
        self.add(g, zc)
        self.play(self.frame.animate.scale(ZK).move_to((tgt + gp) / 2), dots.animate.scale(0.18, about_point=tgt).set_opacity(1), path.animate.set_stroke(width=0.6),
                  labs.animate.set_opacity(0), run_time=2.2)
        gapline = DashedLine(gp, tgt, dash_length=0.006).set_stroke(RED, 0.6)
        lw = Tx(LANG.vocab[tok], 0.035, FG).next_to(tgt, UP, buff=0.03)
        ls = Tx("soft token = where the path ends", 0.028, RED).next_to(gp, DOWN, buff=0.035)
        lm = Tx(f"miss = {miss:.2f}", 0.03, RED).next_to((tgt + gp) / 2, UP, buff=0.05)
        self.play(FadeIn(lw), FadeIn(ls), ShowCreation(gapline), run_time=0.9)
        self.play(FadeIn(lm), run_time=0.5)

        # b3: small, but untrainable, and exactly where the model should commit; older fixes; this paper removes the cause
        self.at(3)
        d = self.dur(3)
        avg = Tx(f"average miss over 200 runs: {W.cap['capped']['miss']:.3f}", 0.03, FG).next_to(ls, DOWN, buff=0.05)
        self.play(FadeIn(avg), run_time=0.6)
        self.wait(max(0.1, d * 0.5 - 0.6))
        snap = arrow(gp, tgt, DIM, 1.2, buff=0.012)
        sl = Tx("older fix: round to the nearest token", 0.028, DIM).next_to(snap, RIGHT, buff=0.04).shift(UP * 0.02)
        self.play(ShowCreation(snap), FadeIn(sl), FadeOut(lm), run_time=0.7)
        self.finish()


class S10(BeatScene):
    SID = "s10"

    def construct(self):
        rng = np.random.default_rng(10)
        eq5 = M("\\log q_t(w \\mid Z_t)", "=", "\\log r_t(w \\mid Z_t)", "+", "f^*(w;\\ Z_t,\\ t)", colors={2: HOT, 4: BLUE}, size=0.5)
        fit(eq5, 9.5).move_to(UP * 3.0)
        n1 = Tx("blows up, but can be computed exactly", 0.25, HOT).next_to(eq5[2], DOWN, buff=0.3)
        n2 = Tx("left for the network", 0.25, BLUE).next_to(eq5[4], DOWN, buff=0.3)
        n1.shift(LEFT * 0.6)

        # b0: split the true log posterior into two parts
        self.at(0)
        self.play(FadeIn(eq5[0]), run_time=0.7)
        self.wait(max(0.1, self.dur(0) * 0.45 - 0.7))
        self.play(FadeIn(VGroup(eq5[1], eq5[2])), FadeIn(n1), run_time=0.7)
        self.wait(max(0.1, self.dur(0) * 0.8 - (self.time - self.start(0))))
        self.play(FadeIn(VGroup(eq5[3], eq5[4])), FadeIn(n2), run_time=0.7)

        # b1: the reference: unigram, every position independent
        self.at(1)
        order = np.argsort(-LANG.pi)[:7]
        pib = Bars([LANG.vocab[i] for i in order], LANG.pi[order] / LANG.pi.max(), width=2.2, bar_h=0.2, gap=0.12, size=0.24, color=HOT).move_to(LEFT * 4.4 + DOWN * 0.8)
        pit = VGroup(Tx("reference: token frequencies,", 0.24, HOT), Tx("each position on its own", 0.24, HOT)).arrange(DOWN, buff=0.1).next_to(pib, UP, buff=0.3)
        samp = VGroup(*[Tx(" ".join(rng.choice(LANG.vocab, size=6, p=LANG.pi)), 0.27, HOT) for _ in range(3)]).arrange(DOWN, buff=0.25, aligned_edge=LEFT)
        real = VGroup(*[Tx(s, 0.27, DATA) for s in W.sentences[:3]]).arrange(DOWN, buff=0.25, aligned_edge=LEFT)
        st = Tx("what the reference writes", 0.23, DIM)
        rt = Tx("what the data looks like", 0.23, DIM)
        col = VGroup(st, samp, rt, real).arrange(DOWN, buff=0.3, aligned_edge=LEFT).move_to(RIGHT * 2.6 + DOWN * 0.9)
        self.play(FadeIn(pib), FadeIn(pit), run_time=0.9)
        self.wait(max(0.1, self.dur(1) * 0.5 - 0.9))
        self.play(FadeIn(st), LaggedStart(*[FadeIn(s) for s in samp], lag_ratio=0.3), run_time=1.2)
        self.play(FadeIn(rt), FadeIn(real), run_time=0.8)

        # b2: under the reference, the other positions cancel in Bayes' rule
        self.at(2)
        self.play(*[FadeOut(m) for m in (pib, pit, col, n1, n2)], run_time=0.6)
        lhs = M("r_t^{(l)}(w \\mid Z)", "=", size=0.48)
        top = M("\\pi(w)\\,\\mathcal{N}(z_l;\\ t\\,E(w))", size=0.44, color=HOT)
        bot = M("\\sum_u \\pi(u)\\,\\mathcal{N}(z_l;\\ t\\,E(u))", size=0.44, color=HOT)
        o1 = VGroup(RoundedRectangle(width=3.0, height=0.7, corner_radius=0.1).set_stroke(DIM, 1.5), Tx("all other positions", 0.24, DIM))
        o2 = o1.copy()
        x1 = Tx("×", 0.34, DIM)
        x2 = x1.copy()
        numer = VGroup(top, x1, o1).arrange(RIGHT, buff=0.25)
        denom = VGroup(bot, x2, o2).arrange(RIGHT, buff=0.25)
        frac = VGroup(numer, denom).arrange(DOWN, buff=0.5)
        bar = Line(LEFT, RIGHT).set_stroke(FG, 2).set_width(frac.get_width() + 0.3).move_to(frac)
        whole = VGroup(lhs, VGroup(frac, bar)).arrange(RIGHT, buff=0.35).move_to(DOWN * 0.3)
        self.play(FadeIn(whole), run_time=1.0)
        self.wait(max(0.1, self.dur(2) * 0.45 - 1.0))
        c1 = Line(o1.get_corner(DL), o1.get_corner(UR)).set_stroke(RED, 3)
        c2 = Line(o2.get_corner(DL), o2.get_corner(UR)).set_stroke(RED, 3)
        self.play(ShowCreation(c1), ShowCreation(c2), run_time=0.7)
        self.play(*[m.animate.set_opacity(0.2) for m in (o1, o2, x1, x2)], c1.animate.set_stroke(opacity=0.3), c2.animate.set_stroke(opacity=0.3), run_time=0.6)

        # b3: the singular logits, Eq. 6; cheap
        self.at(3)
        self.play(FadeOut(whole), FadeOut(c1), FadeOut(c2), run_time=0.5)
        eq6 = M("\\log r_t(w \\mid Z_t)", "=", "\\log\\,\\mathrm{softmax}_w\\!\\left(\\log \\pi(w) - \\dfrac{\\|z_l - t\\,E(w)\\|^2}{2\\,(1-t)^2}\\right)", colors={0: HOT}, size=0.48)
        fit(eq6, 10.0).move_to(UP * 0.9)
        tag = Tx("singular logits  ·  Eq. 6", 0.26, HOT).next_to(eq6, DOWN, buff=0.35)
        cost = Tx("about 1.1% of the compute per step for the small model, 0.2% for the large one", 0.25, DIM).next_to(tag, DOWN, buff=0.4)
        self.play(FadeIn(eq6), run_time=0.9)
        self.wait(max(0.1, self.dur(3) * 0.4 - 0.9))
        self.play(FadeIn(tag), run_time=0.5)
        self.wait(max(0.1, self.dur(3) * 0.68 - (self.time - self.start(3))))
        self.play(FadeIn(cost), run_time=0.6)

        # b4: the network outputs the residual f; probabilities = softmax(singular + f)   [Eq. 5] = this line of code
        self.at(4)
        self.play(*[FadeOut(m) for m in (eq5, eq6, tag, cost)], run_time=0.6)
        t = 0.9
        ts = np.concatenate([np.linspace(0, t, 60)])
        S_, P_, G_ = LANG.euler(W.demo_Z0, ts)
        Z = S_[-1]
        sing = LANG.ref_logpost(Z, t)
        f = LANG.true_logpost(Z, t) - sing
        hs = Heat(np.clip(1 + sing[:, ROWS].T / 30, 0, 1), cell=0.22, mode="prob", color=HOT, gap=0.03).move_to(LEFT * 4.6 + UP * 0.5)
        hf = Heat(np.clip(f[:, ROWS].T, -16, 16), cell=0.22, vmax=16, gap=0.03).move_to(LEFT * 1.3 + UP * 0.5)
        gp = prob_grid(P_[-1], cell=0.22, labels=False).move_to(RIGHT * 3.0 + UP * 0.5)
        plus = Tx("+", 0.5, FG).move_to((hs.get_right() + hf.get_left()) / 2)
        arr = arrow(hf.get_right() + RIGHT * 0.1, gp.get_left() + LEFT * 0.1, FG, 3, buff=0.1)
        sm = Tx("softmax", 0.22, DIM).next_to(arr, UP, buff=0.1)
        l1 = VGroup(Tx("singular(z, t)", 0.25, HOT), Tx("a formula", 0.22, DIM)).arrange(DOWN, buff=0.08).next_to(hs, UP, buff=0.2)
        l2 = VGroup(Tx("net(z, t): the residual f", 0.25, BLUE), Tx("orange: context says yes · blue: context says no", 0.2, DIM)).arrange(DOWN, buff=0.08).next_to(hf, UP, buff=0.2)
        l3 = Tx("p", 0.3, BLUE).next_to(gp, UP, buff=0.3)
        rl = VGroup(*[Tx(w, 0.15, DIM).next_to(hs.cell_at(r, 0), LEFT, buff=0.08) for r, w in enumerate(ORDER)])
        code = CodePanel(["logits = singular(xt, t) + net(xt, t, C, om)"], size=0.25).to_edge(DOWN, buff=0.5)
        tag5 = Tx("Eq. 5", 0.24, DIM).next_to(code, RIGHT, buff=0.4)
        self.play(FadeIn(hs), FadeIn(l1), FadeIn(rl), run_time=0.8)
        self.play(FadeIn(plus), FadeIn(hf), FadeIn(l2), run_time=0.8)
        self.wait(max(0.1, self.dur(4) * 0.4 - 1.6))
        self.play(ShowCreation(arr), FadeIn(sm), FadeIn(gp), FadeIn(l3), run_time=0.9)
        self.wait(max(0.1, self.dur(4) * 0.78 - (self.time - self.start(4))))
        self.play(FadeIn(code), FadeIn(tag5), run_time=0.7)
        self.finish()


class S11(BeatScene):
    SID = "s11"

    def construct(self):
        kap = W.kappa
        # b0: the statement, and what the assumption looks like on the toy language
        thm = M("\\kappa^{-1} \\leq \\dfrac{q_1(\\mathbf{w})}{r_1(\\mathbf{w})} \\leq \\kappa\\ \\ \\mathrm{for\\ every\\ sequence}", "\\ \\ \\Rightarrow\\ \\ ", "|f^*(w;\\,Z_t,\\,t)| \\leq 2\\log\\kappa", colors={2: BLUE}, size=0.46)
        fit(thm, 11.5).move_to(UP * 3.0)
        tag = Tx("Theorem 3.1", 0.24, DIM).next_to(thm, DOWN, buff=0.25)
        self.at(0)
        self.wait(self.dur(0) * 0.12)
        self.play(FadeIn(thm[0]), run_time=0.9)
        # the ratio ruler: log10(q1 / r1) for the 12 real sentences and for 12 random non-sentences
        rng = np.random.default_rng(11)
        r_sent = np.exp(LANG.logpi[LANG.idx].sum(1))
        ratio_s = ((1 - LANG.eps) / len(W.sentences) + LANG.eps * r_sent) / r_sent
        lk = np.log10(kap)
        ax = Line(LEFT * 5.2, RIGHT * 5.2).set_stroke(DIM, 2).move_to(DOWN * 0.2)

        def X(v):
            return ax.get_center() + RIGHT * (v / lk) * 5.0

        ticks = VGroup()
        for v, lab in [(-lk, "1/κ"), (0, "1"), (lk, "κ")]:
            tk = Line(X(v) + UP * 0.12, X(v) + DOWN * 0.12).set_stroke(DIM, 2)
            ticks.add(tk, Tx(lab, 0.26, DIM).next_to(tk, DOWN, buff=0.12))
        sd = VGroup(*[Dot(X(np.log10(v)) + UP * 0.25, radius=0.055).set_fill(DATA, 1).set_stroke(width=0) for v in ratio_s])
        nd = VGroup(*[Dot(X(np.log10(LANG.eps)) + UP * (0.25 + 0.0 * k), radius=0.055).set_fill(RED, 1).set_stroke(width=0) for k in range(1)])
        sl = Tx("the 12 real sentences", 0.23, DATA).next_to(sd, UP, buff=0.2)
        nl = Tx("every other sequence", 0.23, RED).next_to(nd, UP, buff=0.2)
        al = Tx("q₁ / r₁ on the toy language (log scale)", 0.23, DIM).next_to(ax, DOWN, buff=0.75)
        self.wait(max(0.1, self.dur(0) * 0.3 - 1.0))
        self.play(ShowCreation(ax), FadeIn(ticks), FadeIn(al), run_time=0.8)
        self.play(FadeIn(sd), FadeIn(sl), FadeIn(nd), FadeIn(nl), run_time=0.8)
        self.wait(max(0.1, self.dur(0) * 0.62 - (self.time - self.start(0))))
        self.play(FadeIn(VGroup(thm[1], thm[2])), FadeIn(tag), run_time=0.9)

        # b1: Bayes: the posterior of w at one position is a fraction of sums over sequences
        self.at(1)
        self.play(*[FadeOut(m) for m in (ax, ticks, sd, nd, sl, nl, al)], thm.animate.scale(0.75).to_edge(UP, buff=0.35), FadeOut(tag), run_time=0.8)
        fq = M("q_t(w \\mid Z)", "=", "\\dfrac{\\sum_{\\mathbf{u}:\\,u_l = w}\\ q_1(\\mathbf{u})\\,L(Z \\mid \\mathbf{u})}{\\sum_{\\mathbf{u}}\\ q_1(\\mathbf{u})\\,L(Z \\mid \\mathbf{u})}", colors={0: DATA}, size=0.46)
        fr = M("r_t(w \\mid Z)", "=", "\\dfrac{\\sum_{\\mathbf{u}:\\,u_l = w}\\ r_1(\\mathbf{u})\\,L(Z \\mid \\mathbf{u})}{\\sum_{\\mathbf{u}}\\ r_1(\\mathbf{u})\\,L(Z \\mid \\mathbf{u})}", colors={0: HOT}, size=0.46)
        fq.move_to(LEFT * 3.3 + UP * 1.0)
        fr.move_to(LEFT * 3.3 + DOWN * 1.3)
        note = VGroup(Tx("top: sequences with w at position l", 0.23, DIM), Tx("bottom: all sequences", 0.23, DIM), Tx("L: the Gaussian likelihood of the noisy matrix", 0.23, DIM)).arrange(DOWN, buff=0.14, aligned_edge=LEFT).move_to(RIGHT * 3.6 + UP * 1.0)
        self.play(FadeIn(fq), run_time=0.9)
        self.wait(max(0.1, self.dur(1) * 0.4 - 0.9))
        self.play(FadeIn(note[0]), run_time=0.5)
        self.wait(max(0.1, self.dur(1) * 0.75 - (self.time - self.start(1))))
        self.play(FadeIn(note[1]), FadeIn(note[2]), run_time=0.5)

        # b2: the same fraction for the reference: identical likelihoods, priors within a factor kappa
        self.at(2)
        self.play(FadeIn(fr), run_time=0.9)
        same = Tx("same L in both", 0.24, FG)
        diff = M("\\kappa^{-1}\\,r_1(\\mathbf{u}) \\leq q_1(\\mathbf{u}) \\leq \\kappa\\,r_1(\\mathbf{u})", size=0.4)
        VGroup(same, diff).arrange(DOWN, buff=0.3, aligned_edge=LEFT).move_to(RIGHT * 3.6 + DOWN * 1.3)
        self.wait(max(0.1, self.dur(2) * 0.4 - 0.9))
        self.play(FadeIn(same), run_time=0.5)
        self.wait(max(0.1, self.dur(2) * 0.62 - (self.time - self.start(2))))
        self.play(FadeIn(diff), run_time=0.6)

        # b3: ratio of tops in [1/k, k], ratio of bottoms in [1/k, k] -> ratio of posteriors in [1/k^2, k^2]
        self.at(3)
        self.play(*[FadeOut(m) for m in (note, same, diff)], VGroup(fq, fr).animate.scale(0.8).move_to(LEFT * 4.0 + DOWN * 0.1), run_time=0.8)
        ratio = M("\\dfrac{q_t}{r_t}", "=", "\\dfrac{\\mathrm{top}_q}{\\mathrm{top}_r}", "\\cdot", "\\dfrac{\\mathrm{bottom}_r}{\\mathrm{bottom}_q}", size=0.5).move_to(RIGHT * 2.9 + UP * 0.9)
        b1 = M("\\in [\\kappa^{-1},\\ \\kappa]", size=0.3, color=HOT).next_to(ratio[2], DOWN, buff=0.3).shift(LEFT * 0.35)
        b2 = M("\\in [\\kappa^{-1},\\ \\kappa]", size=0.3, color=HOT).next_to(ratio[4], DOWN, buff=0.3).shift(RIGHT * 0.35)
        res = M("\\kappa^{-2} \\leq \\dfrac{q_t(w \\mid Z)}{r_t(w \\mid Z)} \\leq \\kappa^{2}", size=0.48).move_to(RIGHT * 2.9 + DOWN * 1.6)
        d = self.dur(3)
        self.play(FadeIn(ratio), run_time=0.8)
        self.wait(max(0.1, d * 0.3 - 0.8))
        self.play(FadeIn(b1), run_time=0.5)
        self.wait(max(0.1, d * 0.5 - (self.time - self.start(3))))
        self.play(FadeIn(b2), run_time=0.5)
        self.wait(max(0.1, d * 0.7 - (self.time - self.start(3))))
        self.play(FadeIn(res), run_time=0.7)

        # b4: take the log; no t anywhere
        self.at(4)
        fin = M("-2\\log\\kappa", "\\leq", "f^* = \\log q_t - \\log r_t", "\\leq", "2\\log\\kappa", colors={2: BLUE}, size=0.52)
        fit(fin, 6.4).move_to(RIGHT * 3.3 + DOWN * 1.9)
        box = SurroundingRectangle(fin, buff=0.22).set_stroke(BLUE, 2)
        self.play(FadeOut(res), FadeIn(fin), run_time=0.8)
        self.wait(max(0.1, self.dur(4) * 0.55 - 0.8))
        nt = Tx("no t on either side", 0.26, FG).next_to(box, DOWN, buff=0.3)
        self.play(ShowCreation(box), FadeIn(nt), run_time=0.7)

        # b5: the check on the toy language
        self.at(5)
        self.play(*[FadeOut(m) for m in (fq, fr, ratio, b1, b2, fin, box, nt, thm)], run_time=0.6)
        st = W.stats
        plot = Plot(xr=(0, 1), yr=(-0.5, 3.8), w=8.0, h=4.6, xlabel="time t", xticks=(0, 0.5, 1)).move_to(DOWN * 0.3 + LEFT * 0.6)
        for e, lab in [(0, "1"), (1, "10"), (2, "100"), (3, "1,000")]:
            tk = Line(plot.p(0, e), plot.p(0, e) + LEFT * 0.08).set_stroke(DIM, 2)
            plot.add(tk, Tx(lab, 0.22, DIM).next_to(tk, LEFT, buff=0.08))
        cg = plot.curve(st["t"], np.log10(np.maximum(st["gap"], 0.3)), HOT, 4)
        cf = plot.curve(st["t"], np.log10(np.maximum(st["fmax"], 0.3)), BLUE, 4)
        bd = DashedLine(plot.p(0, np.log10(W.bound)), plot.p(1, np.log10(W.bound)), dash_length=0.1).set_stroke(FG, 2)
        lb = Tx(f"the bound, 2 log κ = {W.bound:.0f}", 0.24, FG).next_to(bd, UP, buff=0.1).align_to(plot.p(0.03, 0), LEFT)
        lf = Tx(f"largest residual |f*| (30 trajectories): at most {st['fmax'].max():.0f}", 0.24, BLUE).next_to(plot.p(0.03, np.log10(st["fmax"][5])), DOWN, buff=0.25).align_to(plot.p(0.03, 0), LEFT)
        lg = Tx("singular logit gap", 0.24, HOT).next_to(plot.p(0.9, 2.6), LEFT, buff=0.3)
        self.play(FadeIn(plot), run_time=0.7)
        self.play(ShowCreation(bd), FadeIn(lb), run_time=0.7)
        self.wait(max(0.1, self.dur(5) * 0.35 - 1.4))
        self.play(ShowCreation(cf), FadeIn(lf), run_time=1.6, rate_func=linear)
        self.wait(max(0.1, self.dur(5) * 0.62 - (self.time - self.start(5))))
        self.play(ShowCreation(cg), FadeIn(lg), run_time=1.6, rate_func=linear)
        self.finish()


class S12(BeatScene):
    SID = "s12"

    def construct(self):
        # b0: commitment: model mass on wrong tokens <= e^(2M) x reference mass on wrong tokens
        com = M("p_\\theta(\\mathrm{wrong\\ tokens})", "\\leq", "e^{2M}", "\\cdot", "r_t(\\mathrm{wrong\\ tokens})", colors={0: BLUE, 4: HOT}, size=0.5)
        fit(com, 9.0).move_to(UP * 2.9)
        tf = np.concatenate([np.linspace(0, 0.9, 46), np.linspace(0.91, 0.995, 40)])
        S_, P_, G_ = LANG.euler(W.demo_Z0, tf)
        wrong = np.array([1 - np.exp(LANG.ref_logpost(S_[i], t)).max(1).mean() for i, t in enumerate(tf)])
        plot = Plot(xr=(0, 1), yr=(0, 1), w=6.0, h=3.2, xlabel="time t", xticks=(0, 0.5, 1), yticks=(0, 1)).move_to(DOWN * 0.9)
        cw = plot.curve(tf, wrong, HOT, 4)
        lw = Tx("reference: probability left on the other tokens", 0.24, HOT).next_to(plot, UP, buff=0.2)
        self.at(0)
        self.wait(self.dur(0) * 0.12)
        self.play(FadeIn(com), run_time=0.9)
        self.wait(max(0.1, self.dur(0) * 0.55 - 1.0))
        self.play(FadeIn(plot), FadeIn(lw), run_time=0.7)
        self.play(ShowCreation(cw), run_time=self.dur(0) * 0.25, rate_func=linear)

        # b1: the state arrives: divide the flow equation by (1 - t)^2
        self.at(1)
        self.play(*[FadeOut(m) for m in (com, plot, cw, lw)], run_time=0.6)
        o1 = M("\\dfrac{dZ_t}{dt}", "=", "\\dfrac{\\hat{X}_t - Z_t}{1-t}", colors={2: BLUE}, size=0.5)
        o2 = M("\\dfrac{d}{dt}\\left(\\dfrac{Z_t}{1-t}\\right)", "=", "\\dfrac{\\hat{X}_t}{(1-t)^2}", colors={2: BLUE}, size=0.5)
        o3 = M("Z_t", "=", "(1-t)\\,Z_0", "+", "\\int_0^t \\dfrac{1-t}{(1-u)^2}\\ \\hat{X}_u\\ du", colors={2: NOISE, 4: BLUE}, size=0.5)
        lad = ladder(o1, o2, o3, buff=0.55).move_to(LEFT * 3.2 + UP * 0.4)
        self.play(FadeIn(o1), run_time=0.8)
        self.wait(max(0.1, self.dur(1) * 0.5 - 0.8))
        self.play(FadeIn(o2), run_time=0.8)

        # b2: integrate: a weighted average of the start and all past guesses; weights pile up on recent guesses
        self.at(2)
        self.play(FadeIn(o3), run_time=0.9)
        wp = Plot(xr=(0, 1), yr=(0, 8), w=4.6, h=3.4, xlabel="time u of the guess", xticks=(0, 0.5, 1)).move_to(RIGHT * 3.6 + DOWN * 0.2)
        wl = M("\\mathrm{weight} = \\dfrac{1-t}{(1-u)^2}", size=0.38).next_to(wp, UP, buff=0.2)
        curves, labs = VGroup(), VGroup()
        for tt, c in [(0.5, DIM), (0.8, "#c9a227"), (0.95, HOT)]:
            u = np.linspace(0, tt, 80)
            curves.add(wp.curve(u, (1 - tt) / (1 - u) ** 2, c, 3.5))
            labs.add(Tx(f"t = {tt}", 0.22, c).next_to(wp.p(tt, min(8, 1 / (1 - tt))), UR if tt < 0.9 else UL, buff=0.08))
        self.wait(max(0.1, self.dur(2) * 0.42 - 0.9))
        self.play(FadeIn(wp), FadeIn(wl), run_time=0.7)
        for cv, lb in zip(curves, labs):
            self.play(ShowCreation(cv), FadeIn(lb), run_time=0.9)

        # b3: if the guesses converge to a row, the state converges to that row
        self.at(3)
        self.play(*[FadeOut(m) for m in (lad, wp, wl, curves, labs)], run_time=0.6)
        pl = Plane2(center=DOWN * 0.1, unit=1.3)
        dots = VGroup(*[Dot(pl.p(e), radius=0.06).set_fill(DATA, 1).set_stroke(width=0) for e in LANG.E])
        paths = VGroup(*[VMobject().set_points_as_corners(pl.p(S_[:, l])).set_stroke(HOT, 2.2, 0.9) for l in range(LANG.L)])
        self.play(FadeIn(dots), run_time=0.5)
        self.play(*[ShowCreation(p) for p in paths], run_time=self.dur(3) * 0.55, rate_func=linear)
        ends = VGroup(*[ring(pl.p(LANG.E[P_[-1, l].argmax()]), 0.16, DATA, 2.5) for l in range(LANG.L)])
        note = Tx("the six positions of one sample: every path ends on a token", 0.25, FG).to_edge(DOWN, buff=0.5)
        self.play(ShowCreation(ends), FadeIn(note), run_time=0.8)

        # b4: the capped toy again, with the split: the miss is gone
        self.at(4)
        self.play(*[FadeOut(m) for m in (dots, paths, ends, note)], run_time=0.5)
        ch = BarChart(["cap on the\nwhole logits", "cap on the\nresidual only"], [W.cap["capped"]["miss"], max(W.cap["split"]["miss"], 1e-4)],
                      colors=[RED, DATA], unit=45, bar_w=1.6, gap=1.2, fmt="{:.3f}").move_to(DOWN * 0.4)
        cap = Tx("average distance from the end of the path to its token  ·  toy, 200 runs, same cap B = 6", 0.24, DIM).to_edge(UP, buff=0.6)
        self.play(FadeIn(ch.base), FadeIn(cap), run_time=0.6)
        self.play(*ch.grow(0), run_time=0.8)
        self.wait(max(0.1, self.dur(4) * 0.6 - 1.4))
        self.play(*ch.grow(1), run_time=0.8)

        # b5: the paper's ablation
        self.at(5)
        self.play(FadeOut(ch), FadeOut(cap), run_time=0.5)
        ch2 = BarChart(["without", "with\nsingular logits", "without", "with\nsingular logits"], [64.2, 57.2, 36.3, 24.0], colors=["#bdbdbd", HOT, "#bdbdbd", HOT],
                       unit=0.06, bar_w=1.2, gap=0.55).move_to(DOWN * 0.5)
        g1 = Tx("no guidance (entropy 5.48)", 0.26, FG).next_to(VGroup(ch2.bars[0], ch2.bars[1]), UP, buff=0.75)
        g2 = Tx("momentum guidance, α = 0.7", 0.26, FG).next_to(VGroup(ch2.bars[2], ch2.bars[3]), UP, buff=1.7)
        cap2 = Tx("generative perplexity  ·  ReLF-Small, 64 steps  ·  lower is better", 0.24, DIM).to_edge(UP, buff=0.5)
        self.play(FadeIn(ch2.base), FadeIn(cap2), FadeIn(g1), run_time=0.6)
        self.wait(max(0.1, self.dur(5) * 0.3 - 0.6))
        self.play(*ch2.grow(0), *ch2.grow(1), run_time=0.9)
        self.wait(max(0.1, self.dur(5) * 0.72 - (self.time - self.start(5))))
        self.play(FadeIn(g2), *ch2.grow(2), *ch2.grow(3), run_time=0.9)
        self.finish()
