"""Join scene clips with their narration into one MP4 and write YouTube chapters."""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

from ._load import load
from .paths import build_dir


def _ffmpeg(*a):
    subprocess.check_call(["ffmpeg", "-y", "-loglevel", "error", *map(str, a)])


def assemble(video_dir: Path, name: str | None = None, first: str = "", last: str = "~") -> Path:
    """Each scene's audio sets its length. Scenes that did not change since the last run are reused."""
    build = build_dir(video_dir)
    script = load(video_dir, "script")
    tm = json.loads((build / "timings.json").read_text())
    mux = build / "muxed"
    mux.mkdir(exist_ok=True)
    lst, t, chapters = [], 0.0, []
    for s in script.SCENES:
        sid = s["id"]
        if not (first <= sid <= last):
            continue
        clip, wav, out = build / "clips" / f"{sid}.mp4", build / "audio" / f"{sid}.wav", mux / f"{sid}.mp4"
        if not clip.exists():
            raise SystemExit(f"missing clip {clip}: run `unglazed render {video_dir.name} {sid}`")
        if not (out.exists() and out.stat().st_mtime > max(clip.stat().st_mtime, wav.stat().st_mtime)):
            _ffmpeg("-i", clip, "-i", wav, "-filter_complex", "[0:v]tpad=stop_mode=clone:stop_duration=3,fps=30,format=yuv420p[v]",
                    "-map", "[v]", "-map", "1:a", "-c:v", "libx264", "-preset", "medium", "-crf", "17",
                    "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2", "-shortest", out)
        lst.append(f"file '{out}'")
        if sid in getattr(script, "CHAPTERS", {}):
            chapters.append(f"{int(t // 60)}:{int(t % 60):02d} {script.CHAPTERS[sid]}")
        t += tm[sid]["total"]
    (mux / "list.txt").write_text("\n".join(lst) + "\n")
    _ffmpeg("-f", "concat", "-safe", "0", "-i", mux / "list.txt", "-c", "copy", build / "joined.mp4")
    final = build / f"{name or video_dir.name}.mp4"
    silent = tm.get("_mode") == "estimate"
    af = [] if silent else ["-af", "loudnorm=I=-16:TP=-1.5:LRA=11"]
    _ffmpeg("-i", build / "joined.mp4", "-c:v", "copy", *af, "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", final)
    (build / "chapters.txt").write_text("\n".join(chapters) + "\n")
    dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(final)]))
    print(f"{final}  {int(dur // 60)}:{int(dur % 60):02d}" + ("  (silent draft: timings were estimated)" if silent else ""))
    if chapters:
        print("\n".join(chapters))
    return final
