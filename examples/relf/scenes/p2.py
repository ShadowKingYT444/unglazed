"""Parts 1 (end) and 2: the soft token and the marginals, training with cross entropy, the plain sampler, the logit gap."""
from common import *

ORDER = ["the", "a", "cat", "dog", "bird", "sat", "ran", "slept", "sang", "on", "to", "in", "by", "mat", "rug", "door", "park", "tree"]
ROWS = [LANG.vocab.index(w) for w in ORDER]


def prob_grid(P, cell=0.3, labels=True, size=0.2):
    """Token probabilities as a V x L grid (rows in a readable word order), with row labels."""
    h = Heat(P[:, ROWS].T, cell=cell, mode="prob", color=BLUE, gap=0.03)
    g = VGroup(h)
    if labels:
        g.add(VGroup(*[Tx(w, size, DIM).next_to(h.cell_at(r, 0), LEFT, buff=0.1) for r, w in enumerate(ORDER)]))
    g.h = h
    return g


def sentence_post(Z, t):
    b = max(1 - t, 1e-9)
    ll = -((Z[None] - t * LANG.X) ** 2).sum((1, 2)) / (2 * b * b)
    ll -= ll.max()
    p = np.exp(ll)
    return p / p.sum()


class S05(BeatScene):
    SID = "s05"

    def construct(self):
        pl = Plane2(center=LEFT * 3.4 + DOWN * 0.2, unit=1.75)
        dots, labs = token_dots(pl, T4_E, T4, side=[LEFT, DOWN, UP, RIGHT])
        tt = 0.5
        zfix = np.array([0.55, 0.3])
        q = world.post4(zfix, tt)[0]
        g = q @ T4_E
        z = Dot(pl.p(zfix), radius=0.1).set_fill(HOT, 1).set_stroke(FG, 1.5)
        zl = M("z", size=0.45, color=HOT).next_to(z, DL, buff=0.06)
        self.add(dots, labs, z, zl)

        # b0: expected clean column = posterior-weighted average of table rows
        self.at(0)
        rays = VGroup(*[Line(pl.p(e), pl.p(g)).set_stroke(BLUE, 1 + 9 * p, 0.3 + 0.7 * p) for e, p in zip(T4_E, q)])
        e1 = M("\\hat{x}", "=", "\\sum_w", "E(w)", "\\,q_t(w \\mid z)", colors={0: BLUE, 3: DATA}, size=0.5)
        terms = " + ".join(f"{p:.2f}\\,E(\\mathrm{{{w}}})" for w, p in zip(T4, q))
        e2 = M("=", terms, size=0.4)
        eqs = ladder(e1, e2, buff=0.35).move_to(RIGHT * 3.4 + UP * 2.3)
        fit(eqs, 6.4)
        self.play(FadeIn(e1), run_time=0.7)
        self.play(LaggedStart(*[ShowCreation(r) for r in rays], lag_ratio=0.15), run_time=1.4)
        self.wait(max(0.1, self.dur(0) * 0.6 - 2.1))
        gr = ring(pl.p(g), 0.15, BLUE, 4)
        self.play(ShowCreation(gr), FadeIn(e2), run_time=0.8)

        # b1: the soft token; velocity = (soft token - z) / (1 - t)   [Eq. 2]
        self.at(1)
        gl = Tx("soft token", 0.28, BLUE).next_to(gr, DOWN, buff=0.2).shift(RIGHT * 0.5)
        self.play(FadeIn(gl), run_time=0.5)
        vel = arrow(pl.p(zfix), pl.p(g), HOT, 6, buff=0.05)
        e3 = M("v(z,t)", "=", "\\dfrac{\\hat{x} - z}{1-t}", colors={0: HOT}, size=0.5).next_to(eqs, DOWN, buff=0.6, aligned_edge=LEFT)
        tag = Tx("Eq. 2", 0.24, DIM).next_to(e3, RIGHT, buff=0.5)
        self.wait(max(0.1, self.dur(1) * 0.5 - 0.5))
        self.play(ShowCreation(vel), FadeIn(e3), FadeIn(tag), run_time=0.9)

        # b2: but positions are not independent: the true posterior is over whole sentences
        self.at(2)
        self.play(*[FadeOut(m) for m in (dots, labs, z, zl, rays, gr, gl, vel, eqs, e3, tag)], run_time=0.6)
        k = 10
        t = W.ts16[k]
        Z = W.demo_S[k]
        sp = sentence_post(Z, t)
        top = np.argsort(-sp)[:7]
        rows = VGroup()
        for i in top:
            tx = Tx(W.sentences[i], 0.27, FG)
            base = Rectangle(1.6, 0.2).set_stroke(FAINT, 1)
            bar = Rectangle(max(0.01, 1.6 * sp[i]), 0.2).set_stroke(width=0).set_fill(DATA, 0.95)
            base.next_to(tx, RIGHT, buff=0.3)
            base.set_x(2.0)
            bar.move_to(base.get_left() + RIGHT * bar.get_width() / 2)
            rows.add(VGroup(tx, base, bar))
        for r, row in enumerate(rows):
            row[0].move_to(np.array([-1.9, 1.6 - 0.5 * r, 0]), aligned_edge=LEFT)
            row[1].move_to(np.array([2.4, 1.6 - 0.5 * r, 0]))
            row[2].move_to(row[1].get_left() + RIGHT * row[2].get_width() / 2)
        rows.move_to(ORIGIN)
        head = Tx("posterior over whole sentences, given the noisy matrix", 0.27, DIM).next_to(rows, UP, buff=0.4)
        self.play(FadeIn(head), LaggedStart(*[FadeIn(r) for r in rows], lag_ratio=0.1), run_time=1.6)

        # b3: the velocity of a column needs only that column's expected value -> only the marginals
        self.at(3)
        P = LANG.probs(Z, t)
        self.play(VGroup(rows, head).animate.scale(0.72).move_to(LEFT * 4.0 + UP * 0.6), run_time=0.9)
        grid = prob_grid(P, cell=0.29).move_to(RIGHT * 1.6 + DOWN * 0.1)
        gt = Tx("marginals: one distribution per position", 0.25, BLUE).next_to(grid, UP, buff=0.3)
        ar = arrow(rows.get_right() + RIGHT * 0.1, grid.get_left() + LEFT * 0.1, FG, 3, buff=0.1)
        self.wait(max(0.1, self.dur(3) * 0.45 - 0.9))
        self.play(ShowCreation(ar), FadeIn(grid), FadeIn(gt), run_time=1.0)
        colbox = SurroundingRectangle(grid.h.col(1), buff=0.04).set_stroke(HOT, 2.5)
        self.play(ShowCreation(colbox), run_time=0.6)

        # b4: the network reads the whole matrix, both directions, and outputs L x V numbers
        self.at(4)
        self.play(FadeOut(rows), FadeOut(head), FadeOut(ar), FadeOut(colbox), run_time=0.6)
        zh = Heat(Z.T, cell=0.5, vmax=1.8, numbers=True).move_to(LEFT * 4.9 + UP * 0.2)
        zn = M("X_t", size=0.45, color=HOT).next_to(zh, UP, buff=0.25)
        tn = M("t", size=0.45).next_to(zh, DOWN, buff=0.35)
        box = ModelBox("network", w=1.9, h=1.2, size=0.3).move_to(LEFT * 1.9 + UP * 0.2)
        both = VGroup(arrow(box.get_left() + UP * 0.85 + RIGHT * 0.2, box.get_right() + UP * 0.85 + LEFT * 0.2, DIM, 2, buff=0),
                      arrow(box.get_right() + UP * 1.0 + LEFT * 0.2, box.get_left() + UP * 1.0 + RIGHT * 0.2, DIM, 2, buff=0))
        a1 = arrow(zh.get_right(), box.get_left(), FG, 3, buff=0.15)
        a2 = arrow(box.get_right(), grid.get_left() + LEFT * 0.5, FG, 3, buff=0.15)
        self.play(grid.animate.shift(RIGHT * 1.0), gt.animate.shift(RIGHT * 1.0 + UP * 0.0), run_time=0.6)
        a2 = arrow(box.get_right(), grid.get_left() + LEFT * 0.1, FG, 3, buff=0.15)
        self.play(FadeIn(zh), FadeIn(zn), FadeIn(tn), run_time=0.7)
        self.play(ShowCreation(a1), FadeIn(box), ShowCreation(both[0]), ShowCreation(both[1]), run_time=0.9)
        self.play(ShowCreation(a2), run_time=0.6)
        lv = Tx("L × V numbers", 0.27, BLUE).next_to(grid, DOWN, buff=0.25)
        self.wait(max(0.1, self.dur(4) * 0.55 - (self.time - self.start(4))))
        self.play(FadeIn(lv), FadeOut(gt), run_time=0.6)

        # b5: the whole interface: multiply by the table to get the guess
        self.at(5)
        G = P @ LANG.E
        gh = Heat(G.T, cell=0.5, vmax=1.8, numbers=True).move_to(RIGHT * 5.6 + DOWN * 3.0)
        self.play(VGroup(zh, zn, tn, box, both, a1, a2).animate.shift(UP * 0.9), grid.animate.shift(UP * 0.9), lv.animate.shift(UP * 0.9), run_time=0.7)
        gh.move_to(np.array([grid.get_center()[0], -3.15, 0]))
        mul = M("\\hat{X}", "=", "P\\,E", colors={0: BLUE}, size=0.45).next_to(gh, LEFT, buff=0.4)
        self.wait(max(0.1, self.dur(5) * 0.6 - 0.7))
        self.play(FadeIn(gh), FadeIn(mul), run_time=0.9)
        self.finish()


class S06(BeatScene):
    SID = "s06"

    def construct(self):
        rng = np.random.default_rng(6)
        words = "the cat sat on the mat".split()
        ids = [LANG.vocab.index(w) for w in words]
        X1 = LANG.E[ids]
        X0 = rng.normal(size=X1.shape)
        t = 0.55
        Xt = t * X1 + (1 - t) * X0
        P = LANG.probs(Xt, t)
        code = CodePanel(["x1 = E[w]", "x0 = randn_like(x1);  t = sample_time()", "xt = t * x1 + (1 - t) * x0", "loss = cross_entropy(net(xt, t), w)"], size=0.24, line_gap=0.2)
        code.to_corner(UR, buff=0.5)
        code.lines.set_opacity(0.3)

        row = token_row(words, size=0.28, w=0.95, gap=0.1).move_to(LEFT * 3.4 + UP * 3.3)
        xs = [c.get_center()[0] for c in row]
        h1 = spread_cols(Heat(X1.T, cell=0.5, vmax=1.8, numbers=True), xs, y=2.3)
        ht = spread_cols(Heat(Xt.T, cell=0.5, vmax=1.8, numbers=True), xs, y=0.95)
        l1 = M("x_1", size=0.42, color=DATA).next_to(h1, LEFT, buff=0.3)
        lt = M("x_t", size=0.42, color=HOT).next_to(ht, LEFT, buff=0.3)

        # b0: a real sentence, embedded, blended with noise at a random time
        self.at(0)
        self.wait(self.dur(0) * 0.45)
        self.play(FadeIn(row), FadeIn(code), run_time=0.7)
        self.play(FadeIn(h1), FadeIn(l1), *code.hl(0), run_time=0.8)
        self.play(FadeIn(ht), FadeIn(lt), *code.hl(1, 2), run_time=0.9)

        # b1: token probabilities at every position; minus log of the true token's probability; average   [Eq. 3]
        self.at(1)
        grid = prob_grid(P, cell=0.2, size=0.15)
        spread_cols(grid.h, xs, y=-1.45)
        for r, lab in enumerate(grid[1]):
            lab.next_to(grid.h.cell_at(r, 0), LEFT, buff=0.1)
        true_cells = VGroup(*[SurroundingRectangle(grid.h.cell_at(ORDER.index(w), k), buff=0.0).set_stroke(DATA, 2) for k, w in enumerate(words)])
        nll = -np.log(np.array([P[k, ids[k]] for k in range(6)]))
        nums = VGroup(*[Tx(f"{v:.2f}", 0.22, DATA).move_to(np.array([xs[k], -3.55, 0])) for k, v in enumerate(nll)])
        nl = M("-\\log p_\\theta(\\mathrm{true\\ token})", size=0.32, color=DATA).next_to(nums, RIGHT, buff=0.35)
        self.play(FadeIn(grid), *code.hl(3), run_time=0.9)
        self.wait(max(0.1, self.dur(1) * 0.3 - 0.9))
        self.play(ShowCreation(true_cells), run_time=0.8)
        self.play(FadeIn(nums), FadeIn(nl), run_time=0.7)
        eq3 = M("\\mathcal{L}(\\theta)", "=", "\\mathrm{E}_{w,\\,X_0,\\,t}\\left[-\\log p_\\theta(w \\mid X_t,\\,t)\\right]", size=0.44)
        fit(eq3, 5.6).next_to(code, DOWN, buff=0.7, aligned_edge=RIGHT)
        tag = Tx("Eq. 3", 0.24, DIM).next_to(eq3, DOWN, buff=0.2, aligned_edge=RIGHT)
        avg = Tx(f"loss = mean = {nll.mean():.2f}", 0.3, FG).next_to(eq3, DOWN, buff=0.9, aligned_edge=LEFT)
        self.wait(max(0.1, self.dur(1) * 0.62 - (self.time - self.start(1))))
        self.play(FadeIn(avg), run_time=0.6)
        self.play(FadeIn(eq3), FadeIn(tag), run_time=0.7)

        # b2-b4: why CE is right: CE(q, p) = H(q) + KL(q || p), minimum at p = q, so same optimum as squared error
        self.at(2)
        self.play(*[FadeOut(m) for m in (row, h1, l1, ht, lt, grid, true_cells, nums, nl, avg, code, eq3, tag)], run_time=0.6)
        qv = np.array([0.5, 0.3, 0.15, 0.05])
        pv0 = np.array([0.1, 0.2, 0.3, 0.4])
        a = ValueTracker(0.0)

        def pv():
            x = a.get_value()
            return (1 - x) * pv0 + x * qv

        names = ["mat", "rug", "door", "tree"]
        qb = Bars(names, qv, width=2.6, bar_h=0.26, gap=0.16, size=0.28, color=DATA).move_to(LEFT * 3.8 + UP * 1.2)
        pb = Bars(names, pv0, width=2.6, bar_h=0.26, gap=0.16, size=0.28, color=BLUE).move_to(LEFT * 3.8 + DOWN * 1.4)
        pb.add_updater(lambda b: b.set_values(pv()))
        ql = Tx("q: the true posterior for this input", 0.25, DATA).next_to(qb, UP, buff=0.25)
        pll = Tx("p: the model", 0.25, BLUE).next_to(pb, UP, buff=0.25)
        self.play(FadeIn(qb), FadeIn(ql), run_time=0.8)
        self.wait(max(0.1, self.dur(2) * 0.6 - 0.8))
        self.play(FadeIn(pb), FadeIn(pll), run_time=0.8)

        self.at(3)
        dec = M("\\mathrm{E}_q[-\\log p]", "=", "H(q)", "+", "\\mathrm{KL}(q\\,\\|\\,p)", colors={2: DATA, 4: RED}, size=0.5).move_to(RIGHT * 3.0 + UP * 2.2)
        Hq = float(-(qv * np.log(qv)).sum())
        unit = 2.2
        hbar = Rectangle(Hq * unit, 0.4).set_stroke(width=0).set_fill(DATA, 0.9)
        hbar.move_to(RIGHT * 0.9 + UP * 0.7, aligned_edge=LEFT)
        kbar = Rectangle(1, 0.4).set_stroke(width=0).set_fill(RED, 0.9)

        def upd_k(m):
            kl = float((qv * np.log(qv / pv())).sum())
            m.set_width(max(0.004, kl * unit), stretch=True)
            m.move_to(hbar.get_right(), aligned_edge=LEFT)

        kbar.add_updater(upd_k)
        hl_ = Tx("H(q): fixed", 0.24, DATA).next_to(hbar, DOWN, buff=0.15)
        kl_ = Tx("KL: the only part training can change", 0.24, RED).next_to(hbar, DOWN, buff=0.6, aligned_edge=LEFT).shift(RIGHT * 1.2)
        self.play(FadeIn(dec), run_time=0.8)
        self.play(FadeIn(hbar), FadeIn(hl_), run_time=0.6)
        self.add(kbar)
        self.play(FadeIn(kbar), FadeIn(kl_), run_time=0.6)
        self.wait(max(0.1, self.dur(3) * 0.55 - 2.0))
        self.play(a.animate.set_value(1.0), run_time=self.left(4) - 0.4, rate_func=smooth)

        self.at(4)
        chain = ladder(M("p = q", size=0.5),
                       M("\\Rightarrow\\ ", "\\hat{x} = \\mathrm{E}[X_1 \\mid X_t]", colors={1: BLUE}, size=0.5),
                       M("\\Rightarrow\\ ", "v_\\theta = v^*", colors={1: HOT}, size=0.5), buff=0.4).move_to(RIGHT * 3.0 + DOWN * 1.9)
        d = self.dur(4)
        self.play(FadeOut(kl_), FadeIn(chain[0]), run_time=0.6)
        self.wait(d * 0.15)
        self.play(FadeIn(chain[1]), run_time=0.6)
        self.wait(d * 0.2)
        self.play(FadeIn(chain[2]), run_time=0.6)

        # b5: CE 24.1 vs MSE 25.6 (Gen PPL at entropy 5.45, ReLF-Small)
        self.at(5)
        pb.clear_updaters(), kbar.clear_updaters()
        self.play(*[FadeOut(m) for m in (qb, ql, pb, pll, dec, hbar, kbar, hl_, chain)], run_time=0.6)
        ch = BarChart(["cross entropy", "squared error"], [24.1, 25.6], colors=[HOT, "#bdbdbd"], unit=0.16, bar_w=1.5, gap=1.0).move_to(DOWN * 0.3)
        cap = Tx("generative perplexity at entropy 5.45  ·  ReLF-Small, 64 steps  ·  lower is better", 0.24, DIM).to_edge(UP, buff=0.6)
        self.play(FadeIn(ch.base), FadeIn(cap), run_time=0.6)
        self.wait(max(0.1, self.dur(5) * 0.38 - 0.6))
        self.play(*ch.grow(0), run_time=0.8)
        self.wait(max(0.1, self.dur(5) * 0.62 - (self.time - self.start(5))))
        self.play(*ch.grow(1), run_time=0.8)
        self.finish()


class S07(BeatScene):
    SID = "s07"

    def construct(self):
        S_, P_, G_ = W.demo_S, W.demo_P, W.demo_G
        N = len(W.ts16)
        code = CodePanel(["z = randn(L, d)", "for i in range(N):", "    p = softmax(net(z, t[i]))", "    xhat = p @ E",
                          "    if i == N - 1: return argmax(p)", "    z = z + (t[i+1]-t[i]) / (1-t[i]) * (xhat - z)"], size=0.22, line_gap=0.2)
        code.to_corner(UL, buff=0.5)
        code.lines.set_opacity(0.3)
        cx = 3.3
        xs = [cx + (k - 2.5) * 0.62 for k in range(6)]
        zh = spread_cols(Heat(S_[0].T, cell=0.5, vmax=1.8), xs, y=2.9)
        zl = M("z", size=0.42, color=HOT).next_to(zh, LEFT, buff=0.3)
        grid = prob_grid(P_[0], cell=0.25, size=0.18)
        spread_cols(grid.h, xs, y=-0.1)
        for r, lab in enumerate(grid[1]):
            lab.next_to(grid.h.cell_at(r, 0), LEFT, buff=0.12)
        pl_ = M("p", size=0.42, color=BLUE).next_to(grid[1], LEFT, buff=0.25)
        ticks = np.stack([np.linspace(code.get_left()[0] + 0.1, code.get_left()[0] + 4.6, N), np.full(N, -1.2), np.zeros(N)], 1)
        tg = DotCloud(ticks, color=FAINT, radius=0.06)
        tlit = DotCloud(ticks[:1], color=HOT, radius=0.06)
        tlab = Tx("network calls", 0.22, DIM).next_to(tg, UP, buff=0.2).align_to(code, LEFT)
        dec = VGroup(*[word_on_baseline(LANG.vocab[P_[0, k].argmax()], 0.26, FG) for k in range(6)])

        def decoded(i):
            g = VGroup()
            for k in range(6):
                w = word_on_baseline(LANG.vocab[P_[i, k].argmax()], 0.24, FG)
                w.shift(RIGHT * (xs[k] - w.get_center()[0]) + UP * (-2.95))
                w.set_opacity(float(np.clip(0.15 + P_[i, k].max() ** 1.5, 0, 1)))
                g.add(w)
            return g

        cur = decoded(0)

        def show(i, rt):
            nonlocal cur
            zh.set_values(S_[i].T)
            grid.h.set_values(P_[i][:, ROWS].T)
            tlit.set_points(ticks[: i + 1])
            new = decoded(i)
            self.remove(cur)
            self.add(new)
            cur = new
            self.wait(rt)

        # b0: start from a Gaussian matrix; a grid of times from 0 to just below 1
        self.at(0)
        self.play(FadeIn(code), run_time=0.7)
        self.play(*code.hl(0), FadeIn(zh), FadeIn(zl), run_time=0.8)
        self.wait(max(0.1, self.dur(0) * 0.55 - 1.5))
        self.play(FadeIn(tg), FadeIn(tlab), run_time=0.6)

        # b1: run the network, probabilities, soft tokens, move a fraction h / (1 - t)
        self.at(1)
        d = self.dur(1)
        self.add(tlit)
        self.play(*code.hl(2), FadeIn(grid), FadeIn(pl_), run_time=0.9)
        self.add(cur)
        self.wait(max(0.1, d * 0.45 - 0.9))
        self.play(*code.hl(3), run_time=0.5)
        self.wait(max(0.1, d * 0.62 - (self.time - self.start(1))))
        self.play(*code.hl(5), run_time=0.5)
        show(1, 0.3)

        # b2: early on, probabilities are spread over several words
        self.at(2)
        self.play(*code.hl(2, 3, 5), run_time=0.4)
        per = (self.left(3) - 0.2) / 5
        for i in range(2, 7):
            show(i, per)

        # b3: a few positions sharpen, the others follow
        self.at(3)
        per = (self.left(4) - 0.2) / 8
        for i in range(7, 15):
            show(i, per)

        # b4: N calls, N - 1 moves; the last call only decodes (argmax)
        self.at(4)
        d = self.dur(4)
        self.wait(d * 0.35)
        show(15, 0.2)
        self.play(*code.hl(4), run_time=0.5)
        box = SurroundingRectangle(cur, buff=0.15).set_stroke(DATA, 2.5)
        self.play(ShowCreation(box), run_time=0.7)
        note = Tx("N calls, N − 1 moves", 0.27, FG).next_to(tg, DOWN, buff=0.35).align_to(code, LEFT)
        self.play(FadeIn(note), run_time=0.5)

        # b5: 64 calls for 1,024 tokens; autoregressive needs 1,023
        self.at(5)
        c1 = Tx("flow: 64 calls for 1,024 tokens", 0.3, HOT)
        c2 = Tx("autoregressive: 1,023 calls", 0.3, DIM)
        VGroup(c1, c2).arrange(DOWN, buff=0.2, aligned_edge=LEFT).next_to(note, DOWN, buff=0.5).align_to(code, LEFT)
        self.play(FadeIn(c1), run_time=0.6)
        self.wait(max(0.1, self.dur(5) * 0.55 - 0.6))
        self.play(FadeIn(c2), run_time=0.6)
        self.finish()


class S08(BeatScene):
    SID = "s08"

    def construct(self):
        a, b = T4.index("cat"), T4.index("dog")
        Ea, Eb = T4_E[a], T4_E[b]
        u = 2.6
        pl = Plane2(center=LEFT * 4.7 + DOWN * 0.7 - u * np.append((Ea + Eb) / 2 * 0.85, 0), unit=u)
        tt = 0.8
        zfix = tt * Ea + np.array([-0.12, 0.05])
        da = Dot(pl.p(Ea), radius=0.08).set_fill(DATA, 1).set_stroke(width=0)
        db = Dot(pl.p(Eb), radius=0.08).set_fill(DATA, 1).set_stroke(width=0)
        la = Tx("a", 0.32, FG).next_to(da, UP, buff=0.12)
        lb = Tx("b", 0.32, FG).next_to(db, RIGHT, buff=0.12)
        ca = Dot(pl.p(tt * Ea), radius=0.05).set_fill(NOISE, 1).set_stroke(width=0)
        cb = Dot(pl.p(tt * Eb), radius=0.05).set_fill(NOISE, 1).set_stroke(width=0)
        z = Dot(pl.p(zfix), radius=0.09).set_fill(HOT, 1).set_stroke(FG, 1.5)
        zl = M("z", size=0.42, color=HOT).next_to(z, LEFT, buff=0.1)
        d_a = Line(pl.p(zfix), pl.p(tt * Ea)).set_stroke(DATA, 3)
        d_b = Line(pl.p(zfix), pl.p(tt * Eb)).set_stroke(RED, 3)
        ta = M("t\\,E(a)", size=0.34, color=NOISE).next_to(ca, UP, buff=0.1)
        tb = M("t\\,E(b)", size=0.34, color=NOISE).next_to(cb, DOWN, buff=0.1)

        # b0: the true logits of one position, two tokens a and b
        self.at(0)
        self.wait(self.dur(0) * 0.5)
        self.play(FadeIn(da), FadeIn(db), FadeIn(la), FadeIn(lb), run_time=0.7)
        self.play(FadeIn(ca), FadeIn(cb), FadeIn(ta), FadeIn(tb), FadeIn(z), FadeIn(zl), run_time=0.8)

        # b1: gap = log prior ratio + (difference of squared distances) / (2 (1 - t)^2)
        self.at(1)
        gap = M("\\ell_a - \\ell_b", "=", "\\log\\dfrac{\\pi(a)}{\\pi(b)}", "+", "\\dfrac{\\|z - t\\,E(b)\\|^2 - \\|z - t\\,E(a)\\|^2}{2\\,(1-t)^2}", size=0.46)
        fit(gap, 10.5).move_to(UP * 3.0)
        self.play(FadeIn(VGroup(gap[0], gap[1], gap[2])), run_time=0.8)
        self.wait(max(0.1, self.dur(1) * 0.4 - 0.8))
        self.play(ShowCreation(d_a), ShowCreation(d_b), FadeIn(VGroup(gap[3], gap[4])), run_time=1.0)

        # b2: the top stays normal, the bottom goes to zero
        self.at(2)
        num = SurroundingRectangle(gap[4], buff=0.06).set_stroke(FG, 0)
        d = self.dur(2)
        top_note = Tx("top: stays a normal size", 0.25, FG).move_to(LEFT * 6.4 + UP * 1.95, aligned_edge=LEFT)
        bot_note = Tx("bottom: goes to 0 as t → 1", 0.25, RED).next_to(top_note, DOWN, buff=0.15, aligned_edge=LEFT)
        self.play(FadeIn(top_note), run_time=0.6)
        self.wait(max(0.1, d * 0.3 - 0.6))
        self.play(FadeIn(bot_note), run_time=0.6)

        # b3: on toy trajectories: below 2 for most of the path, in the thousands at t = 0.995
        self.at(3)
        st = W.stats
        plot = Plot(xr=(0, 1), yr=(-0.5, 3.8), w=5.4, h=3.9, xlabel="time t", xticks=(0, 0.5, 1))
        plot.move_to(RIGHT * 3.3 + DOWN * 1.0)
        for e, lab in [(0, "1"), (1, "10"), (2, "100"), (3, "1,000")]:
            tk = Line(plot.p(0, e), plot.p(0, e) + LEFT * 0.08).set_stroke(DIM, 2)
            plot.add(tk, Tx(lab, 0.22, DIM).next_to(tk, LEFT, buff=0.08))
        yl = Tx("logit gap, top token over runner-up (log scale)", 0.23, HOT).next_to(plot.yax.get_top(), UP, buff=0.15).shift(RIGHT * 2.2)
        curve = plot.curve(st["t"], np.log10(np.maximum(st["gap"], 0.3)), HOT, 4)
        self.play(FadeIn(plot), FadeIn(yl), run_time=0.8)
        self.play(ShowCreation(curve), run_time=self.dur(3) * 0.6, rate_func=linear)
        end = Tx(f"{st['gap'][-1]:,.0f} at t = 0.995", 0.24, HOT).next_to(plot.p(0.995, np.log10(st["gap"][-1])), LEFT, buff=0.2)
        self.play(FadeIn(end), run_time=0.5)

        # b4: a bounded network cannot output that: with largest gap B, every other token keeps about e^-B
        self.at(4)
        B = 6.0
        cap = DashedLine(plot.p(0, np.log10(B)), plot.p(1, np.log10(B)), dash_length=0.1).set_stroke(BLUE, 2.5)
        cl = Tx("the most a bounded network can output (B = 6)", 0.23, BLUE).next_to(cap, DOWN, buff=0.12).align_to(plot.p(0.02, 0), LEFT)
        self.play(ShowCreation(cap), FadeIn(cl), run_time=0.9)
        share = M("\\mathrm{share\\ of\\ each\\ other\\ token}", "\\ \\gtrsim\\ ", "e^{-B}", "=", "0.0025", colors={2: BLUE}, size=0.4)
        fit(share, 5.0).move_to(LEFT * 6.4 + DOWN * 3.2, aligned_edge=LEFT)
        self.wait(max(0.1, self.dur(4) * 0.5 - 0.9))
        self.play(FadeIn(share), run_time=0.7)
        self.finish()
