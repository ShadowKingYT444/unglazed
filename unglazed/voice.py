"""Narration: one audio file per beat, one WAV per scene, and timings.json that the scenes sync to.

Pacing: about 0.85 s of silence between beats, so the picture has time to move (about 145 words a minute overall).
Beat audio is cached by a hash of (voice, speed, text): editing one beat re-synthesizes only that beat.
With estimate=True no voice is needed: timings come from word counts and the scene audio is silence.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

from ._load import scenes
from .paths import build_dir

LEAD_IN, GAP, TAIL = 0.9, 0.85, 1.4   # seconds of silence: before a scene's first beat, between beats, after the last
EST_WPS = 2.55                        # words per second while speaking, for estimate mode


def duration(p: Path) -> float:
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)]))


def _ffmpeg(*a):
    subprocess.check_call(["ffmpeg", "-y", "-loglevel", "error", *map(str, a)])


def make(video_dir: Path, estimate: bool = False, voice: str = "af_heart", speed: float = 0.95) -> dict:
    sc = scenes(video_dir)
    build = build_dir(video_dir)
    audio = build / "audio"
    (audio / "beats").mkdir(parents=True, exist_ok=True)

    def beat_path(sid, i, text):
        h = hashlib.sha1(f"{Path(voice).name}@{speed}|{text}".encode()).hexdigest()[:10]
        return audio / "beats" / f"{sid}_{i:02d}_{h}.wav"

    jobs = [(s["id"], i, t) for s in sc for i, t in enumerate(s["beats"])]
    if not estimate:
        todo = [j for j in jobs if not beat_path(*j).exists()]
        print(f"{len(todo)} of {len(jobs)} beats to synthesize with voice {voice}")
        if todo:
            jf = build / "voice_jobs.json"
            jf.write_text(json.dumps([{"text": t, "out": str(beat_path(sid, i, t))} for sid, i, t in todo]))
            py = os.environ.get("UNGLAZED_TTS_PYTHON", sys.executable)
            worker = Path(__file__).with_name("_kokoro_worker.py")
            try:
                subprocess.check_call([py, str(worker), str(jf), voice, str(speed)])
            except subprocess.CalledProcessError:
                raise SystemExit(
                    "voice synthesis failed. Install the voice extra (pip install 'unglazed[voice]'), or point "
                    "UNGLAZED_TTS_PYTHON at a Python that has kokoro, or draft without a voice: unglazed voice <video> --estimate"
                ) from None

    timings: dict = {"_mode": "estimate" if estimate else f"kokoro:{Path(voice).name}"}
    words = 0
    for s in sc:
        t, beats, files = LEAD_IN, [], []
        for i, text in enumerate(s["beats"]):
            words += len(text.split())
            if estimate:
                d = len(text.split()) / EST_WPS
            else:
                p = beat_path(s["id"], i, text)
                d = duration(p)
                files.append(p)
            beats.append({"start": round(t, 3), "dur": round(d, 3)})
            t += d + GAP
        total = round(t - GAP + TAIL, 3)
        out = audio / f"{s['id']}.wav"
        if estimate:
            _ffmpeg("-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo", "-t", total, "-c:a", "pcm_s16le", out)
        else:
            inputs, filters, parts = [], [], []
            for k, f in enumerate(files):
                inputs += ["-i", str(f)]
                pre = LEAD_IN if k == 0 else GAP
                post = TAIL if k == len(files) - 1 else 0
                filters.append(f"[{k}:a]aresample=48000,aformat=channel_layouts=stereo,adelay={int(pre * 1000)}:all=1,apad=pad_dur={post}[a{k}]")
                parts.append(f"[a{k}]")
            filters.append(f"{''.join(parts)}concat=n={len(files)}:v=0:a=1[out]")
            _ffmpeg(*inputs, "-filter_complex", ";".join(filters), "-map", "[out]", "-c:a", "pcm_s16le", out)
            total = round(duration(out), 3)   # the picture is rendered to the exact audio length
        timings[s["id"]] = {"beats": beats, "total": total}
    (build / "timings.json").write_text(json.dumps(timings, indent=1))
    tot = sum(v["total"] for k, v in timings.items() if not k.startswith("_"))
    print(f"wrote {build / 'timings.json'} ({timings['_mode']}): {tot / 60:.1f} min, {words} words, {words / (tot / 60):.0f} words/min overall")
    return timings
