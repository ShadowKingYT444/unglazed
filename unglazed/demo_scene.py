"""Kit gallery: the main kit pieces in one 6 second clip (`unglazed demo`). It needs no narration and no video folder."""
import numpy as np

from unglazed import sims
from unglazed.kit import *  # noqa: F401,F403


class Demo(Scene):
    default_camera_config = dict(background_color=BG)

    def construct(self):
        rng = np.random.default_rng(0)
        X = sims.islands(rng, [(-1.6, 1.4), (1.5, 1.2), (-1.0, -1.5), (1.4, -1.3)], 25, 0.16)
        z0 = rng.normal(size=(300, 2))
        _ts, traj = sims.integrate(z0, X, steps=120)
        clock = ValueTracker(0.0)
        sp = Space(side=4.6, center=LEFT * 4.2 + UP * 0.6)
        data = Cloud(sp, X, DATA, 0.03)
        cloud = Cloud(sp, z0, NOISE, 0.03).follow(traj, clock)
        paths = Paths(sp, traj[:, :10], HOT, 1.5, 0.7, tracker=clock)
        fld = Field(sp, lambda t: np.zeros((1, 2)), None, n=13)
        fld.func = lambda t: sims.velocity(fld.grid, min(t, 0.97), X)
        fld.add_updater(lambda m: m.refresh(clock.get_value()))

        A, B = rng.normal(size=(2, 6)), rng.normal(size=(2, 6))
        heat = Heat(A, cell=0.5, vmax=1.8, numbers=True).move_to(RIGHT * 1.2 + UP * 2.6)
        live = Heat(A, cell=0.5, vmax=1.8).next_to(heat, DOWN, buff=0.3)
        live.add_updater(lambda m: m.set_values((1 - clock.get_value()) * A + clock.get_value() * B))
        bars = Bars(["cat", "dog", "the"], [0.34, 0.33, 0.33]).move_to(RIGHT * 5.0 + UP * 2.2)
        E = np.array([[1, 0.0], [-1, 0.5], [0, -1.0]])
        bars.add_updater(lambda b: b.set_values(sims.posterior(np.array([[clock.get_value(), 0.2]]), clock.get_value() * 0.95, E, s=0.6)[0]))
        code = CodePanel(["xt = t * x1 + (1 - t) * x0", "loss = cross_entropy(net(xt, t), w)"], size=0.2).move_to(RIGHT * 3.0 + DOWN * 0.1)
        eq = M("x_t", "=", "t\\,x_1", "+", "(1-t)\\,x_0", colors={2: DATA, 4: NOISE}, size=0.46).move_to(RIGHT * 3.0 + DOWN * 1.1)
        plot = Plot(xr=(0, 1), yr=(0, 1), w=3.0, h=1.5, xticks=(0, 1)).move_to(RIGHT * 1.6 + DOWN * 2.7)
        xs = np.linspace(0, 1, 60)
        curve = plot.curve(xs, xs ** 3, HOT, 3)
        chart = BarChart(["a", "b"], [24.1, 25.6], colors=[HOT, "#bdbdbd"], unit=0.05, bar_w=0.6, gap=0.4, size=0.2, val_size=0.22).move_to(RIGHT * 5.2 + DOWN * 2.5)
        row = token_row(["the", "cat", "sat"], size=0.26, w=0.9).next_to(sp, DOWN, buff=0.4)
        box = ModelBox("network", w=1.8, h=0.7, size=0.26).next_to(row, DOWN, buff=0.3)
        self.add(sp, fld, data, paths, cloud, heat, live, bars, code, eq, plot, chart, row, box)
        self.play(clock.animate.set_value(1.0), ShowCreation(curve), run_time=5, rate_func=linear)
        self.wait(1)
