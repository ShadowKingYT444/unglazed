"""Render scene classes S01, S02, ... (subclasses of BeatScene) found in <video>/scenes/*.py."""
from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

from .paths import build_dir

SCENE_RE = re.compile(r"^class (S\d\d)\(BeatScene\)", re.M)
KEEP = re.compile(r"OVERRUN|scene time|Error|Exception|Traceback|^\s+File .*scenes|line \d+, in")


def find(video_dir: Path) -> list[tuple[str, Path, str]]:
    """[(sid, file, class name)] in scene order."""
    out = []
    for f in sorted((video_dir / "scenes").glob("*.py")):
        for cls in SCENE_RE.findall(f.read_text()):
            out.append(("s" + cls[1:], f, cls))
    return sorted(out)


def manimgl() -> str:
    exe = shutil.which("manimgl") or str(Path(sys.executable).with_name("manimgl"))
    if not Path(exe).exists():
        raise SystemExit("manimgl not found. Install unglazed with its dependencies (see the README).")
    return exe


def render(video_dir: Path, only: list[str] | None = None, draft: bool = False, fps: int = 30) -> list[str]:
    build = build_dir(video_dir)
    if not (build / "timings.json").exists():
        raise SystemExit("no timings yet: run `unglazed voice <video>` (or with --estimate) first")
    out = build / ("draft" if draft else "clips")
    (out / "raw").mkdir(parents=True, exist_ok=True)
    env = dict(os.environ)
    env["UNGLAZED_BUILD"] = str(build)
    env["UNGLAZED_VIDEO_DIR"] = str(video_dir)
    env["PYTHONPATH"] = os.pathsep.join([str(video_dir), str(video_dir / "scenes"), env.get("PYTHONPATH", "")])
    failed = []
    for sid, f, cls in find(video_dir):
        if only and sid not in only:
            continue
        print(f"== {sid}", flush=True)
        cmd = [manimgl(), str(f), cls, "-w", "-l" if draft else "--hd", "--fps", str(fps), "--video_dir", str(out / "raw"), "--file_name", sid]
        p = subprocess.run(cmd, cwd=f.parent, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        for line in p.stdout.replace("\r", "\n").splitlines():
            if KEEP.search(line):
                print(line)
        raw = out / "raw" / f"{sid}.mp4"
        if p.returncode == 0 and raw.exists():
            raw.replace(out / f"{sid}.mp4")
        else:
            failed.append(sid)
            print(f"[{sid}] FAILED")
    return failed
