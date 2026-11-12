"""unglazed.kit: the visual kit for technical explainer videos (ManimGL).

Style rules (see docs/STYLE.md):
  black canvas, one idea on screen, real images and real simulations as the objects,
  a few lowercase serif labels, colour with a fixed meaning, slow continuous motion.

What is here
  BeatScene      scene whose animations wait for narration beats: self.at(i)
  Tx, M          serif text and LaTeX-free math (matplotlib mathtext glyphs)
  Space          a boxed 2D space with data coordinates -> screen
  Cloud          thousands of points that follow a precomputed trajectory
  Paths          the trails those points leave
  Field          a grid of little direction dashes that follows any function of time
  Tile, Flipbook real pixels on screen (numpy arrays), still or as a sequence
  Chip, token_row, Bars, ModelBox   words, probabilities, networks
  Heat, CodePanel, Plot, BarChart   matrices with numbers, code, plots, charts
"""
from __future__ import annotations

import hashlib
import json
import os

import numpy as np
from manimlib import *  # noqa: F401,F403
from PIL import Image

import matplotlib

matplotlib.use("Agg")
from matplotlib.font_manager import FontProperties  # noqa: E402
from matplotlib.path import Path as MplPath  # noqa: E402
from matplotlib.textpath import TextPath, TextToPath  # noqa: E402

from .paths import build_dir  # noqa: E402

BUILD = build_dir()          # build/<video>, set by `unglazed render` through UNGLAZED_BUILD
CACHE = BUILD / "tiles"
_NO_HOLD = os.environ.get("UNGLAZED_NO_HOLD") == "1"


def _encoder_args(fps):
    """Fast encoders. The clips are joined without re-encoding, so this is the only video encode in a build."""
    gop = str(int(2 * fps))
    if os.environ.get("UNGLAZED_ENCODER") == "nvenc":
        return ["-c:v", "h264_nvenc", "-preset", "p5", "-tune", "hq", "-rc", "constqp", "-qp", "19", "-g", gop, "-pix_fmt", "yuv420p"]
    return ["-c:v", "libx264", "-preset", "veryfast", "-crf", "17", "-g", gop, "-pix_fmt", "yuv420p",
            "-threads", os.environ.get("UNGLAZED_THREADS", "4")]


def _patch_writer():
    import manimlib.scene.scene_file_writer as sfw
    if getattr(sfw.SceneFileWriter, "_unglazed", False):
        return
    orig = sfw.SceneFileWriter.open_movie_pipe

    def open_movie_pipe(self, file_path):
        real = sfw.sp.Popen
        fps = self.scene.camera.fps

        def popen(cmd, **kw):
            i = cmd.index("-loglevel") + 2            # keep the raw-frame input options, replace the encoder options
            return real(cmd[:i] + _encoder_args(fps) + [cmd[-1]], **kw)

        sfw.sp.Popen = popen
        try:
            return orig(self, file_path)
        finally:
            sfw.sp.Popen = real

    sfw.SceneFileWriter.open_movie_pipe = open_movie_pipe
    sfw.SceneFileWriter._unglazed = True


_patch_writer()

# ---------------------------------------------------------------- style
BG = "#000000"
FG = "#f4f1ea"
DIM = "#8d8d8d"
FAINT = "#4a4a4a"
NOISE = "#b98cff"   # anything that is noise
DATA = "#7ff0cf"    # anything that is real data
HOT = "#ffd23f"     # motion: arrow heads, the model's step
MAG = "#e84fd8"     # arrow tails
RED = "#ff5d5d"     # problems
BLUE = "#62c7ff"    # the model's guess
FONT = os.environ.get("UNGLAZED_FONT", "Noto Serif")

_MATH_PROP = FontProperties(size=1, math_fontfamily="cm")
_T2P = TextToPath()
_H48: dict = {}


def Tx(text: str, size: float = 0.42, color=FG, weight=NORMAL, **kw) -> Text:
    """Serif text; `size` is roughly the cap height in scene units."""
    if weight not in _H48:
        _H48[weight] = Text("Hg", font=FONT, weight=weight, font_size=48).get_height()
    fs = 48 * size * 0.9 / _H48[weight]
    t = Text(text, font=FONT, weight=weight, font_size=fs, **kw)
    t.set_color(color)
    t._label = text
    return t


def _mathtext_mob(s: str):
    expr = f"${s}$"
    width, _h, _d = _T2P.get_text_width_height_descent(expr, _MATH_PROP, ismath=True)
    tp = TextPath((0, 0), expr, prop=_MATH_PROP)
    mob = VMobject()
    started = False
    for verts, code in tp.iter_segments(curves=True, simplify=False):
        pts = [np.array([verts[i], verts[i + 1], 0.0]) for i in range(0, len(verts), 2)]
        if code == MplPath.MOVETO:
            if started:
                mob.close_path()
            mob.start_new_path(pts[0])
            started = True
        elif code == MplPath.LINETO:
            mob.add_line_to(pts[0])
        elif code == MplPath.CURVE3:
            mob.add_quadratic_bezier_curve_to(pts[0], pts[1])
        elif code == MplPath.CURVE4:
            mob.add_cubic_bezier_curve_to(pts[0], pts[1], pts[2])
        elif code == MplPath.CLOSEPOLY:
            mob.close_path()
    if started and mob.has_points():
        mob.close_path()
    return mob, width


def M(*parts, colors=None, size=0.62, gap=0.06, color=FG) -> VGroup:
    """Math in parts, each part its own submobject: M("x_t", "=", "t\\,x_1", colors={0: HOT})."""
    colors = colors or {}
    group = VGroup()
    x = 0.0
    for i, p in enumerate(parts):
        mob, w = (VMobject(), 0.0) if p == "" else _mathtext_mob(p)
        mob.shift(np.array([x, 0, 0]))
        mob.set_fill(colors.get(i, color), 1).set_stroke(width=0)
        group.add(mob)
        x += w + gap
    group.scale(size, about_point=ORIGIN)
    group.center()
    group._label = "math: " + " ".join(parts)[:40]
    return group


# ---------------------------------------------------------------- narration sync
class BeatScene(Scene):
    """self.at(i) waits until narration beat i starts; self.finish() pads to the audio length."""

    SID = ""
    default_camera_config = dict(background_color=BG)

    def setup(self):
        f = BUILD / "timings.json"
        if not f.exists():
            raise FileNotFoundError(f"{f} missing; run `unglazed voice <video>` (or add --estimate) first")
        self.tm = json.loads(f.read_text())[self.SID]
        self.overruns = []
        self._lint_seen = set()
        self.clock = ValueTracker(0.0)

    def start(self, i: int) -> float:
        return self.tm["beats"][i]["start"]

    def dur(self, i: int) -> float:
        return self.tm["beats"][i]["dur"]

    def left(self, i: int) -> float:
        """Seconds from now until beat i starts (at least 0.1)."""
        return max(0.1, self.start(i) - self.time)

    def at(self, i: int, offset: float = 0.0):
        if i > 0 and offset == 0.0:
            self.lint(i - 1)                       # the picture of the previous beat is complete now
        dt = self.start(i) + offset - self.time
        if dt > 1 / 60:
            self.wait(dt)
        elif dt < -0.25:
            self.overruns.append((i, round(-dt, 2)))

    def wait(self, duration=None, stop_condition=None, **kw):
        """Like Scene.wait, but a still picture is drawn once and its bytes are written for every held frame.

        Explainers hold the picture while the voice talks, so this is where most frames are. A wait is 'still' when
        no mobject has a time-based updater (updaters that only read trackers give the same frame every time).
        Set UNGLAZED_NO_HOLD=1 to switch this off.
        """
        fw = getattr(self, "file_writer", None)
        fps = self.camera.fps
        still = (
            not _NO_HOLD and duration and stop_condition is None and not kw and not self.skip_animations
            and fw is not None and getattr(fw, "write_to_movie", False) and getattr(fw, "frames", None) is not None
            and not any(m.has_time_based_updaters() for m in self.mobjects)
        )
        n = len(np.arange(0, duration, 1 / fps)) if still else 0
        if n < 3:
            return super().wait(duration, stop_condition, **kw)
        self.pre_play()
        self.update_mobjects(dt=0)
        self.update_frame(1 / fps)
        self.emit_frame()                          # one real frame
        fw.frames.drain()                          # everything in flight reaches ffmpeg, in order
        frame = bytes(self.camera.get_frame_bytes())
        sink = fw.writing_process.stdin
        for _ in range(n - 1):
            self.increment_time(1 / fps)
            sink.write(frame)
        if getattr(fw, "progress_display", None) is not None:
            fw.progress_display.update(n - 1)
        self.held_frames = getattr(self, "held_frames", 0) + n - 1
        self.post_play()

    def lint(self, beat):
        """Layout check of the picture as it stands: labels off the frame, overlapping, or too small to read."""
        for msg in layout_problems(self):
            line = f"[{self.SID}] LAYOUT beat {beat}: {msg}"
            if line not in self._lint_seen:
                self._lint_seen.add(line)
                print(line)

    def finish(self, fade=True):
        end = self.tm["total"] + 2 / self.camera.fps     # two spare frames; the join cuts each clip to its exact length
        self.lint(len(self.tm["beats"]) - 1)
        mobs = [m for m in self.mobjects if m is not self.frame]
        if fade and mobs and end - self.time > 0.8:
            self.wait(end - self.time - 0.7)
            self.play(*[FadeOut(m) for m in mobs], run_time=0.6)
        if end - self.time > 1 / 60:
            self.wait(end - self.time)
        if self.overruns:
            print(f"[{self.SID}] OVERRUN beats (beat, seconds late): {self.overruns}")
        held = getattr(self, "held_frames", 0)
        total = max(1, int(round(self.time * self.camera.fps)))
        print(f"[{self.SID}] scene time {self.time:.2f}s vs audio {end:.2f}s  ({100 * held // total}% of frames held)")

    def chapter(self, numeral: str, title: str, until_beat: int = 1):
        """Roman numeral + lowercase title on a black screen, like the reference."""
        n = Tx(numeral + ".", 0.5).move_to(UP * 0.75)
        t = Tx(title, 0.62).move_to(DOWN * 0.45)
        self.play(FadeIn(n), FadeIn(t), run_time=0.8)
        self.wait(max(0.2, self.start(until_beat) - self.time - 0.9))
        self.play(FadeOut(n), FadeOut(t), run_time=0.7)

    def run_clock(self, a: float, b: float, run_time: float, rate_func=linear, others=()):
        self.clock.set_value(a)
        self.play(self.clock.animate.set_value(b), *others, run_time=run_time, rate_func=rate_func)


# ---------------------------------------------------------------- spaces, clouds, paths, fields
class Space(VGroup):
    """A square window onto a 2D space: data coords in [-lim, lim]^2."""

    def __init__(self, side=5.6, lim=3.0, center=ORIGIN, stroke=2.0, color=FG):
        self.lim = lim
        self.box = Square(side).set_stroke(color, stroke)
        super().__init__(self.box)
        self.move_to(center)

    def p(self, xy):
        xy = np.asarray(xy, float)
        k = self.box.get_width() / (2 * self.lim)
        out = np.zeros(xy.shape[:-1] + (3,))
        out[..., :2] = xy * k
        return out + self.box.get_center()

    def unit(self):
        return self.box.get_width() / (2 * self.lim)


def lerp_traj(traj, a):
    """traj (T, ...) sampled at fraction a in [0, 1] with linear interpolation."""
    T = len(traj)
    x = float(np.clip(a, 0, 1)) * (T - 1)
    i = min(int(x), T - 2)
    f = x - i
    return (1 - f) * traj[i] + f * traj[i + 1]


class Cloud(DotCloud):
    def __init__(self, space: Space, xy, color=DATA, radius=0.035, glow=0.0, opacity=1.0):
        super().__init__(space.p(xy), color=color, radius=radius, glow_factor=glow, opacity=opacity)
        self.space = space

    def set_xy(self, xy):
        self.set_points(self.space.p(xy))
        return self

    def follow(self, traj, tracker):
        """Follow traj (T, N, 2) as tracker goes 0 -> 1."""
        self.add_updater(lambda m: m.set_xy(lerp_traj(traj, tracker.get_value())))
        return self


class Paths(VGroup):
    """Trails of a trajectory (T, N, 2). With a tracker they are drawn up to the current time."""

    def __init__(self, space: Space, traj, color=HOT, width=2.0, opacity=0.8, tracker=None):
        super().__init__()
        self.space, self.traj = space, np.asarray(traj)
        for i in range(self.traj.shape[1]):
            m = VMobject().set_stroke(color, width, opacity)
            m.set_points_as_corners(space.p(self.traj[:, i]))
            self.add(m)
        if tracker is not None:
            self.add_updater(lambda g: g.draw_to(tracker.get_value()))
            self.draw_to(tracker.get_value())

    def draw_to(self, a):
        T = len(self.traj)
        x = float(np.clip(a, 0, 1)) * (T - 1)
        k = int(x)
        head = lerp_traj(self.traj, a)
        for i, m in enumerate(self.submobjects):
            pts = np.concatenate([self.traj[: k + 1, i], head[i][None]], 0)
            if len(pts) < 2:
                pts = np.concatenate([pts, pts], 0)
            m.set_points_as_corners(self.space.p(pts))
        return self


def segments(P, Q, color=FG, width=2.0, opacity=1.0, color2=None) -> VMobject:
    """Many separate line segments P[i] -> Q[i] as ONE mobject (fast). Optional gradient to color2."""
    m = VMobject()
    set_segments(m, P, Q)
    m.set_stroke(color, width, opacity)
    if color2 is not None:
        _grad(m, color, color2, opacity)
    return m


def set_segments(m: VMobject, P, Q):
    P, Q = np.asarray(P, float), np.asarray(Q, float)
    n = len(P)
    pts = np.zeros((4 * n, 3))
    pts[0::4], pts[1::4], pts[2::4], pts[3::4] = P, (P + Q) / 2, Q, Q
    m.set_points(pts[:-1])
    return m


def _grad(m: VMobject, c1, c2, opacity=1.0):
    n = len(m.get_points())
    a, b = np.array(color_to_rgb(c1)), np.array(color_to_rgb(c2))
    pat = np.stack([a, (a + b) / 2, b, b])
    rgba = np.concatenate([np.tile(pat, (n // 4 + 1, 1))[:n], np.full((n, 1), opacity)], 1)
    m.set_stroke(width=m.get_stroke_width())
    m.data["stroke_rgba"][:] = rgba
    m.note_changed_data() if hasattr(m, "note_changed_data") else None


class Field(Group):
    """Direction dashes on a grid. func(t) -> (G*G, 2) velocities at self.grid (data coords).

    Dashes have a fixed length (direction only) unless speed_scale is given; a bright dot
    marks the head so the direction reads at a glance.
    """

    def __init__(self, space: Space, func, tracker=None, n=17, length=0.19, width=2.2,
                 opacity=0.9, speed_scale=None, margin=0.35, tail=MAG, head=HOT):
        super().__init__()
        self.space, self.func, self.length, self.speed_scale = space, func, length, speed_scale
        g = np.linspace(-space.lim + margin, space.lim - margin, n)
        self.grid = np.stack(np.meshgrid(g, g), -1).reshape(-1, 2)
        self.tail_c, self.head_c, self.op = tail, head, opacity
        self.lines = VMobject().set_stroke(tail, width, opacity)
        self.heads = DotCloud(space.p(self.grid), color=head, radius=width * 0.011, opacity=opacity)
        self.add(self.lines, self.heads)
        self.tracker = tracker
        self.refresh(tracker.get_value() if tracker is not None else 0.0)
        if tracker is not None:
            self.add_updater(lambda m: m.refresh(tracker.get_value()))

    def refresh(self, t):
        v = np.asarray(self.func(t), float)
        sp = np.linalg.norm(v, axis=1, keepdims=True)
        d = v / np.maximum(sp, 1e-9)
        L = self.length * (np.clip(sp / self.speed_scale, 0.15, 1.0) if self.speed_scale else 1.0)
        c = self.space.p(self.grid)
        d3 = np.concatenate([d, np.zeros((len(d), 1))], 1) * L
        set_segments(self.lines, c - d3 / 2, c + d3 / 2)
        _grad(self.lines, self.tail_c, self.head_c, self.op)
        self.heads.set_points(c + d3 / 2)
        return self


# ---------------------------------------------------------------- real pixels
def _to_png(arr, min_px=540) -> str:
    a = np.asarray(arr)
    if a.dtype != np.uint8:
        a = (np.clip(a, 0, 1) * 255).astype(np.uint8)
    key = hashlib.sha1(a.tobytes() + str(a.shape).encode()).hexdigest()[:16]
    CACHE.mkdir(parents=True, exist_ok=True)
    path = CACHE / f"{key}.png"
    if not path.exists():
        im = Image.fromarray(a)
        k = int(np.ceil(min_px / max(1, min(im.size))))
        if k > 1:
            im = im.resize((im.size[0] * k, im.size[1] * k), Image.NEAREST)
        im.save(path)
    return str(path)


class Tile(Group):
    """A numpy image (H, W) or (H, W, 3), floats in 0..1 or uint8, with a thin border."""

    def __init__(self, arr, height=2.0, border=True, border_color=FG, border_width=1.5):
        self.img = ImageMobject(_to_png(arr), height=height)
        super().__init__(self.img)
        if border:
            self.frame_rect = Rectangle(self.img.get_width(), self.img.get_height()).set_stroke(border_color, border_width)
            self.add(self.frame_rect)


class Flipbook(Group):
    """A stack of image frames at one place; follows `tracker` (0..1) through the sequence.

    It starts invisible. Fade it with the scene helpers: self.play(book.appear()) / book.vanish()
    (do not use FadeIn/FadeOut on it: its updater owns the opacities).
    """

    def __init__(self, frames, height=2.0, border=True, tracker=None, border_color=FG, visible=False):
        self.imgs = [ImageMobject(_to_png(f), height=height) for f in frames]
        super().__init__(*self.imgs)
        self.frame_rect = Rectangle(self.imgs[0].get_width(), self.imgs[0].get_height()).set_stroke(border_color, 1.5 if border else 0)
        self.add(self.frame_rect)
        self.master = ValueTracker(1.0 if visible else 0.0)
        self.tracker = tracker
        self.a = 0.0
        self.add_updater(lambda m: m.show(m.tracker.get_value() if m.tracker is not None else m.a))
        self.show(0.0)

    def show(self, a):
        self.a = a
        o = self.master.get_value()
        n = len(self.imgs)
        x = float(np.clip(a, 0, 1)) * (n - 1)
        k = min(int(x), n - 1)
        f = x - k
        for i, im in enumerate(self.imgs):
            im.set_opacity(o * (1.0 if i == k else (f if i == k + 1 else 0.0)))
        self.frame_rect.set_stroke(opacity=o)
        return self

    def appear(self):
        return self.master.animate.set_value(1.0)

    def vanish(self):
        return self.master.animate.set_value(0.0)


def noise_img(rng, h=96, w=96, color=True):
    a = rng.normal(0.5, 0.25, size=(h, w, 3) if color else (h, w))
    return np.clip(a, 0, 1)


def blend_noise(img, noise, t):
    """x_t = t * image + (1 - t) * noise, as pixels (t = 1 is the clean image)."""
    return np.clip(t * img + (1 - t) * noise, 0, 1)


# ---------------------------------------------------------------- words, bars, boxes
class Chip(VGroup):
    """A word in a rounded box."""

    def __init__(self, word, size=0.34, color=FG, w=None, h=None, fill=0.0, stroke=1.5):
        self.label = word_on_baseline(word, size, color)
        w = w or self.label.get_width() + size * 1.2
        h = h or size * 2.1
        self.box = RoundedRectangle(width=w, height=h, corner_radius=min(0.12, h / 3)).set_stroke(color, stroke).set_fill(color, fill)
        self.label.shift(RIGHT * (self.box.get_center()[0] - self.label.get_center()[0]))
        super().__init__(self.box, self.label)


def word_on_baseline(word, size=0.34, color=FG) -> VGroup:
    """A word whose baseline does not depend on its letters: a capital H next to it would be centred on y = 0."""
    ref = Tx("H" + word, size, color)
    ref.shift(DOWN * ref[0].get_center()[1])
    g = VGroup(*ref.submobjects[1:])
    return g


def token_row(words, size=0.34, w=1.25, gap=0.14, color=FG) -> VGroup:
    return VGroup(*[Chip(x, size, color, w=w) for x in words]).arrange(RIGHT, buff=gap)


class Bars(VGroup):
    """Horizontal probability bars with word labels; set_values() to update."""

    def __init__(self, labels, values, width=2.6, bar_h=0.22, gap=0.14, color=BLUE, size=0.26, label_w=0.9):
        super().__init__()
        self.width_, self.bar_h, self.color_ = width, bar_h, color
        self.rows = []
        for i, lab in enumerate(labels):
            y = -i * (bar_h + gap)
            t = Tx(lab, size, FG)
            t.move_to(np.array([-0.12, y, 0]), aligned_edge=RIGHT)
            base = Rectangle(width, bar_h).set_stroke(FAINT, 1).move_to(np.array([width / 2, y, 0]))
            bar = Rectangle(width, bar_h).set_stroke(width=0).set_fill(color, 0.95)
            self.rows.append((t, base, bar, y))
            self.add(t, base, bar)
        self.set_values(values)
        self.center()

    def set_values(self, values):
        for (t, base, bar, _y), v in zip(self.rows, values):
            w = max(1e-3, float(v)) * base.get_width()
            bar.set_width(w, stretch=True)
            bar.move_to(base.get_left() + RIGHT * w / 2)
        return self


class ModelBox(VGroup):
    def __init__(self, text="model", w=2.2, h=1.1, size=0.34, color=FG):
        self.box = RoundedRectangle(width=w, height=h, corner_radius=0.12).set_stroke(color, 2)
        self.label = Tx(text, size, color)
        super().__init__(self.box, self.label)


def arrow(a, b, color=FG, width=3, buff=0.08, tip=0.18):
    return Arrow(a, b, buff=buff, fill_color=color, thickness=width, tip_width_ratio=4) if False else \
        StrokeArrow(a, b, stroke_color=color, stroke_width=width, buff=buff)


def pointer(a, b, color=FG, width=1.2, opacity=0.8):
    return Line(a, b).set_stroke(color, width, opacity)


class TimeBar(VGroup):
    """The clock: a line from 0 to 1 with a knob that follows a tracker."""

    def __init__(self, tracker, width=4.0, ends=("0", "1"), color=DIM, knob=HOT):
        self.line = Line(LEFT * width / 2, RIGHT * width / 2).set_stroke(color, 2)
        self.t0 = Tx(ends[0], 0.24, color).next_to(self.line.get_left(), DOWN, buff=0.14)
        self.t1 = Tx(ends[1], 0.24, color).next_to(self.line.get_right(), DOWN, buff=0.14)
        self.knob = Dot(radius=0.075).set_fill(knob, 1).set_stroke(width=0)
        super().__init__(self.line, self.t0, self.t1, self.knob)
        self.knob.add_updater(lambda m: m.move_to(interpolate(self.line.get_left(), self.line.get_right(), float(np.clip(tracker.get_value(), 0, 1)))))


def blob_outline(space: Space, pts, k=2.6, color=FG, width=1.3, opacity=0.9) -> VMobject:
    """A smooth outline around a cluster of data points (covariance ellipse, k sigmas)."""
    pts = np.asarray(pts, float)
    mu, cov = pts.mean(0), np.cov(pts.T)
    w, V = np.linalg.eigh(cov)
    th = np.linspace(0, 2 * np.pi, 49)
    ring = mu + (np.stack([np.cos(th), np.sin(th)], 1) * (k * np.sqrt(w))) @ V.T
    m = VMobject().set_points_smoothly(space.p(ring))
    return m.set_stroke(color, width, opacity)


def ring(point, r=0.12, color=BLUE, width=2.5) -> Circle:
    return Circle(radius=r).set_stroke(color, width).move_to(point)


def fade_img(tile: "Tile", a: float):
    """Animations that fade a Tile (image + border) to opacity a."""
    out = [tile.img.animate.set_opacity(a)]
    if hasattr(tile, "frame_rect"):
        out.append(tile.frame_rect.animate.set_stroke(opacity=a))
    return out


def growing_segments(P, Q, tracker, color=FG, width=2.0, opacity=1.0) -> VMobject:
    """Segments P[i] -> Q[i] that all grow together as tracker goes 0 -> 1 (ShowCreation would draw them one by one)."""
    P, Q = np.asarray(P, float), np.asarray(Q, float)
    m = segments(P, P + (Q - P) * max(1e-3, tracker.get_value()), color, width, opacity)
    m.add_updater(lambda mob: set_segments(mob, P, P + (Q - P) * max(1e-3, float(np.clip(tracker.get_value(), 0, 1)))))
    return m


# ---------------------------------------------------------------- technical pieces: matrices, code, plots, charts
MONO = os.environ.get("UNGLAZED_MONO", "DejaVu Sans Mono")
POS = "#ffb347"   # positive numbers in a heat grid
NEG = "#4da3ff"   # negative numbers


def heat_color(v, vmax=1.0):
    """Diverging colour on black: blue for negative, orange for positive, dark near zero."""
    a = float(np.clip(abs(v) / vmax, 0, 1)) ** 0.8
    return interpolate_color("#101010", POS if v >= 0 else NEG, a)


class Heat(VGroup):
    """A matrix as a grid of coloured cells (rows x cols), optionally with the numbers written inside.

    set_values(new) recolours in place (cheap, fine inside an updater); relabel() rewrites the numbers.
    For probabilities use mode="prob": one colour, opacity = value.
    """

    def __init__(self, values, cell=0.5, vmax=None, numbers=False, mode="signed", color=BLUE, fmt="{:.1f}", gap=0.04, num_size=None):
        super().__init__()
        self.vals = np.atleast_2d(np.asarray(values, float))
        self.cell, self.mode, self.color_, self.fmt, self.gap = cell, mode, color, fmt, gap
        self.vmax = vmax or (1.0 if mode == "prob" else float(np.abs(self.vals).max() + 1e-9))
        R, C = self.vals.shape
        self.cells = VGroup()
        for r in range(R):
            for c in range(C):
                sq = Square(cell - gap).set_stroke(FAINT, 1)
                sq.move_to(np.array([c * cell, -r * cell, 0]))
                self.cells.add(sq)
        self.add(self.cells)
        self.nums = VGroup()
        self.num_size = num_size or cell * 0.36
        self.add(self.nums)
        self.set_values(self.vals)
        self.center()
        if numbers:
            self.relabel()

    def cell_at(self, r, c):
        return self.cells[r * self.vals.shape[1] + c]

    def col(self, c):
        return VGroup(*[self.cell_at(r, c) for r in range(self.vals.shape[0])])

    def row(self, r):
        return VGroup(*[self.cell_at(r, c) for c in range(self.vals.shape[1])])

    def set_values(self, values):
        self.vals = np.atleast_2d(np.asarray(values, float))
        for sq, v in zip(self.cells, self.vals.ravel()):
            if self.mode == "prob":
                sq.set_fill(self.color_, float(np.clip(v / self.vmax, 0, 1)))
            else:
                sq.set_fill(heat_color(v, self.vmax), 1)
        return self

    def relabel(self):
        new = VGroup()
        for sq, v in zip(self.cells, self.vals.ravel()):
            t = Tx(self.fmt.format(v), self.num_size, FG)
            t.move_to(sq)
            new.add(t)
        self.remove(self.nums)
        self.nums = new
        self.add(self.nums)
        return self


class CodePanel(VGroup):
    """A few lines of code in a monospace font. hl(i, j, ...) lights those lines and dims the rest."""

    def __init__(self, lines, size=0.26, line_gap=0.2, color=FG, comment=DIM):
        super().__init__()
        self.lines = VGroup()
        ref_h = Text("Hg", font=MONO, font_size=48).get_height()
        fs = 48 * size * 0.9 / ref_h
        y = 0.0
        for ln in lines:
            body = ln if ln.strip() else "."
            t = Text(body, font=MONO, font_size=fs)
            t.set_color(comment if ln.strip().startswith("#") else color)
            if not ln.strip():
                t.set_opacity(0)
            # left-align on the first non-space character, keeping the indent
            indent = len(ln) - len(ln.lstrip(" "))
            t.move_to(np.array([indent * size * 0.62, y, 0]), aligned_edge=LEFT)
            self.lines.add(t)
            y -= size + line_gap
        self.add(self.lines)
        self.bar = Rectangle(0.06, size + line_gap * 0.6).set_stroke(width=0).set_fill(HOT, 0)
        self.add(self.bar)
        self.center()

    def hl(self, *idx, dim=0.3):
        """Animations: light lines idx, dim the others."""
        an = []
        for i, t in enumerate(self.lines):
            an.append(t.animate.set_opacity(1.0 if (i in idx or not idx) else dim))
        return an

    def box(self, i, j=None, color=HOT, buff=0.1):
        j = i if j is None else j
        grp = VGroup(*[self.lines[k] for k in range(i, j + 1)])
        return SurroundingRectangle(grp, buff=buff).set_stroke(color, 2)


class Plot(VGroup):
    """Bare axes with data coordinates: p(x, y) -> point, curve(xs, ys) -> polyline."""

    def __init__(self, xr=(0, 1), yr=(0, 1), w=4.5, h=3.0, color=DIM, xlabel=None, ylabel=None, xticks=(), yticks=(), size=0.24):
        super().__init__()
        self.xr, self.yr, self.w, self.h = xr, yr, w, h
        self.xax = Line(ORIGIN, RIGHT * w).set_stroke(color, 2)
        self.yax = Line(ORIGIN, UP * h).set_stroke(color, 2)
        self.add(self.xax, self.yax)
        self.labels = VGroup()
        for x in xticks:
            tk = Line(self._p(x, yr[0]), self._p(x, yr[0]) + DOWN * 0.08).set_stroke(color, 2)
            self.labels.add(tk, Tx(f"{x:g}", size, color).next_to(tk, DOWN, buff=0.08))
        for y in yticks:
            tk = Line(self._p(xr[0], y), self._p(xr[0], y) + LEFT * 0.08).set_stroke(color, 2)
            self.labels.add(tk, Tx(f"{y:g}", size, color).next_to(tk, LEFT, buff=0.08))
        if xlabel:
            self.labels.add(Tx(xlabel, size, color).next_to(self.xax, DOWN, buff=0.42 if xticks else 0.15))
        if ylabel:
            self.labels.add(Tx(ylabel, size, color).next_to(self.yax.get_top(), UP, buff=0.15))
        self.add(self.labels)

    def _p(self, x, y):
        return np.array([(x - self.xr[0]) / (self.xr[1] - self.xr[0]) * self.w, (y - self.yr[0]) / (self.yr[1] - self.yr[0]) * self.h, 0.0])

    def p(self, x, y):
        return self.xax.get_start() + self._p(x, y)

    def curve(self, xs, ys, color=HOT, width=3.5):
        ys = np.clip(ys, self.yr[0], self.yr[1])
        pts = np.stack([self.p(x, y) for x, y in zip(xs, ys)])
        return VMobject().set_points_as_corners(pts).set_stroke(color, width)


class BarChart(VGroup):
    """Vertical bars from zero with the value on top and a label under each."""

    def __init__(self, labels, values, colors=None, unit=0.1, bar_w=1.0, gap=0.5, size=0.26, fmt="{:.1f}", val_size=0.3):
        super().__init__()
        colors = colors or [FG] * len(values)
        self.bars, self.vals, self.labs = VGroup(), VGroup(), VGroup()
        for i, (lab, v, c) in enumerate(zip(labels, values, colors)):
            x = i * (bar_w + gap)
            r = Rectangle(bar_w, max(1e-3, v * unit)).set_stroke(width=0).set_fill(c, 0.95)
            r.move_to(np.array([x, v * unit / 2, 0]))
            self.bars.add(r)
            self.vals.add(Tx(fmt.format(v), val_size, c).next_to(r, UP, buff=0.1))
            lines = VGroup(*[Tx(s, size, FG) for s in lab.split("\n")]).arrange(DOWN, buff=0.08)
            self.labs.add(lines.next_to(np.array([x, 0, 0]), DOWN, buff=0.15))
        n = len(values)
        self.base = Line(np.array([-bar_w * 0.8, 0, 0]), np.array([(n - 1) * (bar_w + gap) + bar_w * 0.8, 0, 0])).set_stroke(DIM, 2)
        self.add(self.base, self.bars, self.vals, self.labs)
        self.center()

    def grow(self, i, run_time=0.7):
        return [GrowFromEdge(self.bars[i], DOWN), FadeIn(self.labs[i]), FadeIn(self.vals[i])]


def halo(center, radius, color=NOISE, fill=0.12, width=1.5):
    return Circle(radius=max(radius, 1e-3)).set_stroke(color, width, 0.9).set_fill(color, fill).move_to(center)


def ladder(*rows, buff=0.45, aligned_edge=LEFT):
    """Stack equation rows (the result of M(...) or Tx(...)) top to bottom."""
    return VGroup(*rows).arrange(DOWN, buff=buff, aligned_edge=aligned_edge)


def fit(mob, max_width=None, max_height=None):
    """Shrink mob (never enlarge) so it fits inside max_width / max_height. Returns mob."""
    if max_width and mob.get_width() > max_width:
        mob.scale(max_width / mob.get_width())
    if max_height and mob.get_height() > max_height:
        mob.scale(max_height / mob.get_height())
    return mob


def spread_cols(heat: "Heat", xs, y=None):
    """Put column c of a Heat at x = xs[c] (to line a matrix up with a row of tokens), optionally at height y."""
    R, C = heat.vals.shape
    for c in range(C):
        for r in range(R):
            cell = heat.cell_at(r, c)
            cell.move_to(np.array([xs[c], cell.get_center()[1], 0]))
    heat.refresh_bounding_box(recurse_down=True)
    if y is not None:
        heat.shift(UP * (y - heat.cells.get_center()[1]))
    if len(heat.nums):
        heat.relabel()
    return heat


# ---------------------------------------------------------------- composition: zones, focus, and a layout check
class Stage:
    """Named zones of the 14.2 x 8 frame, as (centre x, centre y, width, height).

    Compose every scene from these, so that recurring things sit in the same place for the whole video:
    the concept title on top, one large object in `main`, or two balanced columns `left` / `right`
    (code or algebra on one side, the picture on the other), a one-line note in `foot`.
    """

    title = (0.0, 3.4, 12.6, 0.7)
    main = (0.0, -0.3, 13.0, 6.1)          # everything under the title
    full = (0.0, 0.0, 13.2, 7.0)           # no title
    left = (-3.45, -0.3, 6.3, 6.1)
    right = (3.45, -0.3, 6.3, 6.1)
    left_wide = (-2.45, -0.3, 8.3, 6.1)
    right_narrow = (4.6, -0.3, 4.0, 6.1)
    left_narrow = (-4.6, -0.3, 4.0, 6.1)
    right_wide = (2.45, -0.3, 8.3, 6.1)
    top = (0.0, 1.55, 13.0, 2.6)           # upper half of main
    bottom = (0.0, -2.0, 13.0, 2.8)        # lower half of main
    foot = (0.0, -3.6, 12.6, 0.45)


def place(mob, zone, align=ORIGIN, grow=False, max_grow=1.5):
    """Fit mob into a Stage zone (shrink if needed, enlarge if grow=True) and put it there.

    align: ORIGIN for the centre, or LEFT / RIGHT / UP / DOWN (and corners) to push it to that side of the zone.
    """
    cx, cy, w, h = zone
    k = min(w / max(mob.get_width(), 1e-6), h / max(mob.get_height(), 1e-6))
    if k < 1 or grow:
        mob.scale(min(k, max_grow) if grow else k)
    mob.move_to(np.array([cx, cy, 0.0]))
    if np.any(np.asarray(align) != 0):
        dx = (w - mob.get_width()) / 2 * align[0]
        dy = (h - mob.get_height()) / 2 * align[1]
        mob.shift(np.array([dx, dy, 0.0]))
    return mob


def focus(mob, color=RED, buff=0.1, width=3):
    """The red box that says 'look here': one per moment."""
    return SurroundingRectangle(mob, buff=buff).set_stroke(color, width)


def concept_title(text, size=0.44, color=FG):
    """The title of the current concept. It stays on top while the content under it changes."""
    return place(Tx(text, size, color), Stage.title)


def _label_boxes(scene):
    out, seen = [], set()
    for top in scene.mobjects:
        if top is scene.frame:
            continue
        for m in top.get_family():
            if not hasattr(m, "_label") or id(m) in seen:
                continue
            seen.add(id(m))
            parts = [x for x in m.get_family() if isinstance(x, VMobject) and x.has_points()]
            if not parts:
                continue
            op = max(max(float(x.get_fill_opacity()), float(x.get_stroke_opacity()) if x.get_stroke_width() > 0 else 0.0) for x in parts)
            if op < 0.2:
                continue
            c, w, h = m.get_center(), m.get_width(), m.get_height()
            out.append((str(m._label)[:28], c[0] - w / 2, c[0] + w / 2, c[1] - h / 2, c[1] + h / 2))
    return out


_TALL = set("bdfhijkltgpqyABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789()[]|/")   # a word without these is only x-height tall


def layout_problems(scene, limit=6):
    """Labels (text and math) that run off the frame, overlap each other, or are too small to read at 1080p."""
    fc, fw, fh = scene.frame.get_center(), scene.frame.get_width(), scene.frame.get_height()
    k = fw / 14.222                                   # camera zoom: sizes are judged as they appear on screen
    x0, x1, y0, y1 = fc[0] - fw / 2, fc[0] + fw / 2, fc[1] - fh / 2, fc[1] + fh / 2
    edge = 0.12 * k
    boxes = _label_boxes(scene)
    out = []
    for name, a, b, c, d in boxes:
        if b < x0 or a > x1 or d < y0 or c > y1:
            continue                                   # completely outside: parked on purpose
        side = [s for s, bad in (("left", a < x0 + edge), ("right", b > x1 - edge), ("bottom", c < y0 + edge), ("top", d > y1 - edge)) if bad]
        if side:
            out.append(f"'{name}' runs off the frame ({', '.join(side)})")
        elif (d - c) < (0.15 if any(ch in _TALL for ch in name) else 0.095) * k and (b - a) > 0.1 * k and any(ch.isalnum() for ch in name):
            out.append(f"'{name}' is too small to read ({(d - c) / k * 135:.0f} px tall at 1080p)")
    vis = [bx for bx in boxes if not (bx[2] < x0 or bx[1] > x1 or bx[4] < y0 or bx[3] > y1)]
    for i in range(len(vis)):
        n1, a1, b1, c1, d1 = vis[i]
        for j in range(i + 1, len(vis)):
            n2, a2, b2, c2, d2 = vis[j]
            ix, iy = min(b1, b2) - max(a1, a2), min(d1, d2) - max(c1, c2)
            if ix <= 0 or iy <= 0:
                continue
            small = min((b1 - a1) * (d1 - c1), (b2 - a2) * (d2 - c2))
            if small > 0 and ix * iy / small > 0.2:
                out.append(f"'{n1}' overlaps '{n2}'")
    return out[:limit]
