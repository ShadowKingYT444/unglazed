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
from .paths import root, video_dir


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
    from . import pedagogy
    from .coverage import check
    v = video_dir(a.video)
    bad = check(v, part=a.part)
    print()
    errors, _warns = pedagogy.check(v)
    sys.exit(1 if (bad or errors) else 0)


def cmd_voice(a):
    from .voice import make
    _need("ffmpeg")
    make(video_dir(a.video), estimate=a.estimate, engine=a.engine, voice=a.voice, speed=a.speed, verify=a.verify, threads=a.threads)


def cmd_render(a):
    from .render import render
    failed = render(video_dir(a.video), only=a.scenes or None, draft=a.draft, jobs=a.jobs, force=a.force)
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
    from . import pedagogy
    if check(v, part=a.part, quiet=True) or pedagogy.check(v, quiet=True)[0]:
        check(v, part=a.part)
        pedagogy.check(v)
        raise SystemExit("the script does not pass `unglazed check`: fix it before building")
    make(v, estimate=a.estimate, engine=a.engine, voice=a.voice, speed=a.speed, verify=a.verify, threads=a.threads)
    if not a.skip_render:
        failed = render(v, jobs=a.jobs, force=a.force)
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
        s.add_argument("--engine", choices=["kokoro", "pocket"], default="kokoro",
                       help="kokoro: fastest, fixed voices. pocket: CPU only, intonation follows the sentence, clones a voice from a recording")
        s.add_argument("--voice", default=None, help="kokoro: a voice name or a voice pack (.pt). pocket: a built-in voice name or a 10 to 30 s recording (.wav)")
        s.add_argument("--speed", type=float, default=None, help="speaking rate (default 0.95 for kokoro, 1.0 for pocket)")
        s.add_argument("--verify", action="store_true", help="listen back with faster-whisper; retake or report sentences that come out wrong")
        s.add_argument("--threads", type=int, default=4, help="CPU threads for the pocket engine")

    s = sub.add_parser("voice", help="narration and timings")
    s.add_argument("video")
    voice_args(s)
    s.set_defaults(fn=cmd_voice)

    s = sub.add_parser("render", help="render scenes (all, or the ones you name)")
    s.add_argument("video")
    s.add_argument("scenes", nargs="*")
    s.add_argument("--draft", action="store_true", help="480p at 15 fps, into build/<video>/draft")
    s.add_argument("--jobs", type=int, default=1, help="scenes rendered at the same time (more load, less waiting)")
    s.add_argument("--force", action="store_true", help="render even if nothing changed")
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
    s.add_argument("--jobs", type=int, default=1)
    s.add_argument("--force", action="store_true")
    voice_args(s)
    s.set_defaults(fn=cmd_build)

    s = sub.add_parser("demo", help="render a short gallery of the kit, to test the install")
    s.add_argument("--hd", action="store_true")
    s.set_defaults(fn=cmd_demo)

    a = p.parse_args(argv)
    a.fn(a)


if __name__ == "__main__":
    main()
