"""Contact sheets: one frame near the end of every beat (when its picture is complete), to check a scene by eye."""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

from .paths import build_dir


def sheets(video_dir: Path, only: list[str] | None = None, draft: bool = False, at: float = 0.9, extra: int = 0) -> list[Path]:
    build = build_dir(video_dir)
    tm = json.loads((build / "timings.json").read_text())
    out = build / "sheets"
    out.mkdir(exist_ok=True)
    made = []
    for sid in only or [k for k in tm if not k.startswith("_")]:
        clip = build / ("draft" if draft else "clips") / f"{sid}.mp4"
        if not clip.exists():
            continue
        beats = tm[sid]["beats"]
        times = []
        for i, b in enumerate(beats):
            end = beats[i + 1]["start"] if i + 1 < len(beats) else tm[sid]["total"] - 1.0
            fr = [at] if not extra else [(k + 1) / (extra + 1) for k in range(extra)] + [0.97]
            times += [b["start"] + f * (end - b["start"]) for f in fr]
        tmp = out / f"_{sid}"
        tmp.mkdir(exist_ok=True)
        for k, t in enumerate(times):
            subprocess.check_call(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{t:.2f}", "-i", str(clip), "-frames:v", "1", "-vf", "scale=640:360", str(tmp / f"{k:03d}.jpg")])
        cols = 4 if not extra else extra + 1
        rows = -(-len(times) // cols)
        dst = out / f"{sid}.jpg"
        subprocess.check_call(["ffmpeg", "-y", "-loglevel", "error", "-i", str(tmp / "%03d.jpg"), "-vf", f"tile={cols}x{rows}:padding=4:color=0x333333", "-frames:v", "1", "-q:v", "3", str(dst)])
        for f in tmp.iterdir():
            f.unlink()
        tmp.rmdir()
        made.append(dst)
        print(f"{dst}  ({len(times)} frames, {cols} per row)")
    return made
