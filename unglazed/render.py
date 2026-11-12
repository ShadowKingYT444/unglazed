"""Render scene classes S01, S02, ... (subclasses of BeatScene) found in <video>/scenes/*.py."""
from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

from .paths import build_dir

SCENE_RE = re.compile(r"^class (S\d\d)\(BeatScene\)", re.M)
KEEP = re.compile(r"OVERRUN|LAYOUT|scene time|Error|Exception|Traceback|^\s+File .*scenes|line \d+, in")
IMPORT_RE = re.compile(r"^(?:from|import) (\w+)", re.M)


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


def encoder() -> str:
    """nvenc if this machine has a working NVIDIA encoder (almost no CPU load), else a fast x264 preset."""
    want = os.environ.get("UNGLAZED_ENCODER", "auto")
    if want != "auto":
        return want
    try:
        subprocess.run(["ffmpeg", "-v", "error", "-f", "lavfi", "-i", "color=black:s=256x144:d=0.2", "-c:v", "h264_nvenc", "-f", "null", "-"],
                       check=True, capture_output=True, timeout=20)
        return "nvenc"
    except Exception:
        return "x264"


def _digest(video_dir: Path, f: Path, sid: str, draft: bool, fps: int) -> str:
    """Everything a scene's picture depends on: its file, the scene files it imports, world.py, the kit, its timings."""
    h = hashlib.sha1()
    todo, seen = [f], set()
    while todo:
        p = todo.pop()
        if p in seen or not p.exists():
            continue
        seen.add(p)
        txt = p.read_text()
        h.update(txt.encode())
        for name in IMPORT_RE.findall(txt):
            for cand in (video_dir / "scenes" / f"{name}.py", video_dir / f"{name}.py"):
                todo.append(cand)
    h.update(Path(__file__).with_name("kit.py").read_bytes())
    h.update(Path(__file__).with_name("sims.py").read_bytes())
    tm = json.loads((build_dir(video_dir) / "timings.json").read_text()).get(sid, {})
    h.update(json.dumps(tm, sort_keys=True).encode())
    h.update(f"{draft}|{fps}".encode())
    return h.hexdigest()


def _one(job):
    sid, f, cls, cmd, env, out, digest = job
    p = subprocess.run(cmd, cwd=f.parent, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    lines = [ln for ln in p.stdout.replace("\r", "\n").splitlines() if KEEP.search(ln)]
    raw = out / "raw" / f"{sid}.mp4"
    ok = p.returncode == 0 and raw.exists()
    if ok:
        raw.replace(out / f"{sid}.mp4")
        (out / f"{sid}.hash").write_text(digest)
    return sid, ok, lines


def render(video_dir: Path, only: list[str] | None = None, draft: bool = False, fps: int | None = None,
           jobs: int = 1, force: bool = False) -> list[str]:
    """Render scenes. Unchanged scenes are skipped (same scene code, world, kit and timings) unless force=True."""
    build = build_dir(video_dir)
    if not (build / "timings.json").exists():
        raise SystemExit("no timings yet: run `unglazed voice <video>` (or with --estimate) first")
    fps = fps or (15 if draft else 30)
    out = build / ("draft" if draft else "clips")
    (out / "raw").mkdir(parents=True, exist_ok=True)
    env = dict(os.environ)
    env["UNGLAZED_BUILD"] = str(build)
    env["UNGLAZED_VIDEO_DIR"] = str(video_dir)
    env["UNGLAZED_ENCODER"] = encoder()
    env["PYTHONPATH"] = os.pathsep.join([str(video_dir), str(video_dir / "scenes"), env.get("PYTHONPATH", "")])
    todo, skipped = [], []
    for sid, f, cls in find(video_dir):
        if only and sid not in only:
            continue
        digest = _digest(video_dir, f, sid, draft, fps)
        hf = out / f"{sid}.hash"
        if not force and (out / f"{sid}.mp4").exists() and hf.exists() and hf.read_text() == digest:
            skipped.append(sid)
            continue
        cmd = [manimgl(), str(f), cls, "-w", "-l" if draft else "--hd", "--fps", str(fps), "--video_dir", str(out / "raw"), "--file_name", sid]
        todo.append((sid, f, cls, cmd, env, out, digest))
    if skipped:
        print(f"unchanged, skipped: {' '.join(skipped)}")
    world = video_dir / "world.py"
    if todo and world.exists() and jobs > 1:
        subprocess.run([sys.executable, "-c", "import world; world.load()"], cwd=video_dir, env=env)   # build the cache once, not in every worker
    failed = []
    t0 = time.time()
    if jobs > 1 and len(todo) > 1:
        from concurrent.futures import ThreadPoolExecutor
        with ThreadPoolExecutor(jobs) as ex:
            results = list(ex.map(_one, todo))
    else:
        results = []
        for job in todo:
            print(f"== {job[0]}", flush=True)
            r = _one(job)
            print("\n".join(r[2]), flush=True)
            results.append(r)
    for sid, ok, lines in results:
        if jobs > 1:
            print(f"== {sid}\n" + "\n".join(lines))
        if not ok:
            failed.append(sid)
            print(f"[{sid}] FAILED")
    if todo:
        print(f"rendered {len(todo) - len(failed)} scene(s) in {time.time() - t0:.0f} s with the {env['UNGLAZED_ENCODER']} encoder")
    return failed
