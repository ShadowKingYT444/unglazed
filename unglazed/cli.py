"""The `unglazed` command.

    unglazed new myvideo               start a video folder from the template
    unglazed check myvideo             the depth check: every coverage item must have a scene
    unglazed voice myvideo             narration + timings (add --estimate to draft without a voice)
    unglazed render myvideo s03 --draft    480p draft of one scene
    unglazed sheet myvideo s03 --draft     one frame per beat, to check the scene by eye
    unglazed render myvideo            every scene at 1080p
    unglazed build myvideo             check + voice + render + join into build/myvideo/myvideo.mp4
    unglazed demo                      a 6 second gallery of the kit, to test the install
"""
from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

from . import __version__
from .paths import build_dir, root, video_dir


def _need(tool):
    if not shutil.which(tool):
        raise SystemExit(f"{tool} not found on PATH (install ffmpeg)")


def cmd_new(a):
    dst = root() / a.video
    if dst.exists():
        raise SystemExit(f"{dst} already exists")
    shutil.copytree(Path(__file__).with_name("template"), dst)
    print(f"created {dst}\nnext: edit {a.video}/coverage.py, then {a.video}/script.py, then run `unglazed check {a.video}`")


def cmd_check(a):
    from .coverage import check
    bad = check(video_dir(a.video), part=a.part)
    sys.exit(1 if bad else 0)


def cmd_voice(a):
    from .voice import make
    _need("ffmpeg")
    make(video_dir(a.video), estimate=a.estimate, voice=a.voice, speed=a.speed)


def cmd_render(a):
    from .render import render
    failed = render(video_dir(a.video), only=a.scenes or None, draft=a.draft)
    sys.exit(1 if failed else 0)


def cmd_sheet(a):
    from .sheet import sheets
    _need("ffmpeg")
    sheets(video_dir(a.video), only=a.scenes or None, draft=a.draft, at=a.at, extra=a.extra)


def cmd_build(a):
    from .assemble import assemble
    from .coverage import check
    from .render import render
    from .voice import make
    _need("ffmpeg")
    v = video_dir(a.video)
    if check(v, part=a.part, quiet=True):
        check(v, part=a.part)
        raise SystemExit("coverage check failed: fix the script before building")
    make(v, estimate=a.estimate, voice=a.voice, speed=a.speed)
    world = v / "world.py"
    if world.exists() and not (build_dir(v) / "world.pkl").exists():
        print("building the world (cached in build/)")
    if not a.skip_render:
        failed = render(v)
        if failed:
            raise SystemExit(f"scenes failed: {failed}")
    assemble(v, a.name)


def cmd_demo(a):
    import subprocess
    from .render import manimgl
    out = root() / "build" / "_demo"
    out.mkdir(parents=True, exist_ok=True)
    f = Path(__file__).with_name("demo_scene.py")
    subprocess.check_call([manimgl(), str(f), "Demo", "-w", "-l" if not a.hd else "--hd", "--fps", "30", "--video_dir", str(out), "--file_name", "demo"])
    print(out / "demo.mp4")


def main(argv=None):
    p = argparse.ArgumentParser(prog="unglazed", description="Technical explainer videos that do not skip steps.")
    p.add_argument("--version", action="version", version=__version__)
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("new", help="start a video folder from the template")
    s.add_argument("video")
    s.set_defaults(fn=cmd_new)

    s = sub.add_parser("check", help="depth check: every coverage item must have a scene")
    s.add_argument("video")
    s.add_argument("--part", type=int, default=99, help="only require items with part <= N")
    s.set_defaults(fn=cmd_check)

    def voice_args(s):
        s.add_argument("--estimate", action="store_true", help="no voice: timings from word counts, silent audio")
        s.add_argument("--voice", default="af_heart", help="a Kokoro voice name, or a path to a voice pack (.pt)")
        s.add_argument("--speed", type=float, default=0.95)

    s = sub.add_parser("voice", help="narration and timings")
    s.add_argument("video")
    voice_args(s)
    s.set_defaults(fn=cmd_voice)

    s = sub.add_parser("render", help="render scenes (all, or the ones you name)")
    s.add_argument("video")
    s.add_argument("scenes", nargs="*")
    s.add_argument("--draft", action="store_true", help="480p, into build/<video>/draft")
    s.set_defaults(fn=cmd_render)

    s = sub.add_parser("sheet", help="contact sheets: a frame per beat")
    s.add_argument("video")
    s.add_argument("scenes", nargs="*")
    s.add_argument("--draft", action="store_true")
    s.add_argument("--at", type=float, default=0.9, help="where in each beat to take the frame (0..1)")
    s.add_argument("--extra", type=int, default=0, help="extra evenly spaced frames per beat")
    s.set_defaults(fn=cmd_sheet)

    s = sub.add_parser("build", help="check, voice, render and join the whole video")
    s.add_argument("video")
    s.add_argument("--name", default=None, help="output file name (without .mp4)")
    s.add_argument("--part", type=int, default=99)
    s.add_argument("--skip-render", action="store_true", help="reuse the clips in build/<video>/clips")
    voice_args(s)
    s.set_defaults(fn=cmd_build)

    s = sub.add_parser("demo", help="render a short gallery of the kit, to test the install")
    s.add_argument("--hd", action="store_true")
    s.set_defaults(fn=cmd_demo)

    a = p.parse_args(argv)
    a.fn(a)


if __name__ == "__main__":
    main()
