"""Scene classes are named S01, S02, ... and subclass BeatScene. SID must match the scene id in script.py."""
from common import *


class S01(BeatScene):
    SID = "s01"

    def construct(self):
        u = 1.3

        def P(x):
            return LEFT * 1.0 + RIGHT * x * u

        axis = Line(P(-2.4), P(2.6)).set_stroke(DIM, 2)
        d0 = Dot(P(W.x0), radius=0.1).set_fill(NOISE, 1).set_stroke(width=0)
        d1 = Dot(P(W.x1), radius=0.1).set_fill(DATA, 1).set_stroke(width=0)
        l0 = M("x_0", size=0.42, color=NOISE).next_to(d0, DOWN, buff=0.2)
        l1 = M("x_1", size=0.42, color=DATA).next_to(d1, DOWN, buff=0.2)
        xt = Dot(P(W.x0), radius=0.12).set_fill(HOT, 1).set_stroke(width=0)
        xt.add_updater(lambda m: m.move_to(P((1 - self.clock.get_value()) * W.x0 + self.clock.get_value() * W.x1)))
        eq = M("x_t", "=", "t\\,x_1", "+", "(1-t)\\,x_0", colors={0: HOT, 2: DATA, 4: NOISE}, size=0.5).move_to(UP * 2.2)
        bar = TimeBar(self.clock, width=4.0).move_to(DOWN * 2.2)

        # beat 0: the blend, from t = 0 to t = 1
        self.at(0)
        self.play(ShowCreation(axis), FadeIn(d0), FadeIn(d1), FadeIn(l0), FadeIn(l1), FadeIn(eq), FadeIn(bar), run_time=1.0)
        self.add(xt)
        self.run_clock(0, 1, self.left(1) - 1.4, rate_func=smooth)

        # beat 1: halfway
        self.at(1)
        self.play(self.clock.animate.set_value(W.t), run_time=1.0)

        # beat 2: a step of h covers h / (1 - t) of the remaining distance
        self.at(2)
        xt.clear_updaters()                     # freeze a live object before animating it yourself
        step = M("\\dfrac{h}{1-t}", "=", f"{W.fraction:g}", size=0.5).move_to(UP * 0.9 + RIGHT * 2.2)
        hop = Line(P(W.xt), P(W.x_next)).set_stroke(HOT, 6)
        self.wait(self.dur(2) * 0.5)
        self.play(FadeIn(step), ShowCreation(hop), xt.animate.move_to(P(W.x_next)), run_time=1.2)
        self.finish()
