"""Narration: each beat is spoken sentence by sentence, joined with natural pauses, and timed for the scenes.

Engines (both local, no API key):
  pocket   Pocket TTS: a small CPU model whose intonation follows the sentence. Clones a voice from a short recording.
  kokoro   Kokoro-82M: very fast, fixed voices (or a voice pack .pt).
With estimate=True no voice is needed: timings come from word counts and the audio is silence.

Sentence audio is cached by a hash of (engine, voice, speed, text): editing one sentence re-synthesizes only that one.
With verify=True each sentence is transcribed back (faster-whisper); a sentence that comes out wrong is retaken
(Pocket) and, if it still differs, reported so you can add the word to the SAY table in script.py.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import subprocess
import sys
from pathlib import Path

from ._load import load, scenes
from .lexicon import sentences, speakable
from .paths import build_dir

FPS = 30
LEAD_IN, GAP, TAIL = 0.9, 0.85, 1.4   # seconds of silence: before a scene's first beat, between beats, after the last
SENT_GAP = 0.32                       # between sentences inside a beat
EST_WPS = 2.55                        # words per second while speaking, for estimate mode


def duration(p: Path) -> float:
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)]))


def _ffmpeg(*a):
    subprocess.check_call(["ffmpeg", "-y", "-loglevel", "error", *map(str, a)])


def _run_worker(name: str, *args: str, env: dict | None = None):
    py = os.environ.get("UNGLAZED_TTS_PYTHON", sys.executable)
    worker = Path(__file__).with_name(name)
    subprocess.check_call([py, str(worker), *args], env={**os.environ, **(env or {})})


def _synthesize(todo: list[dict], engine: str, voice: str, speed: float, build: Path, threads: int):
    jf = build / "voice_jobs.json"
    jf.write_text(json.dumps(todo))
    try:
        if engine == "pocket":
            _run_worker("_pocket_worker.py", str(jf), voice, str(threads))
        else:
            _run_worker("_kokoro_worker.py", str(jf), voice, str(speed))
    except subprocess.CalledProcessError:
        extra = "pocket-tts" if engine == "pocket" else "unglazed[voice]"
        raise SystemExit(
            f"voice synthesis failed. Install the engine (pip install '{extra}'), or point UNGLAZED_TTS_PYTHON at a "
            "Python that has it, or draft without a voice: unglazed voice <video> --estimate"
        ) from None


def _verify(items: list[dict], build: Path) -> list[dict]:
    jf, of = build / "asr_jobs.json", build / "asr_out.json"
    jf.write_text(json.dumps(items))
    py = os.environ.get("UNGLAZED_ASR_PYTHON", os.environ.get("UNGLAZED_TTS_PYTHON", sys.executable))
    try:
        subprocess.check_call([py, str(Path(__file__).with_name("_asr_worker.py")), str(jf), str(of)])
    except subprocess.CalledProcessError:
        raise SystemExit("--verify needs faster-whisper (pip install faster-whisper), or set UNGLAZED_ASR_PYTHON") from None
    return json.loads(of.read_text())


def make(video_dir: Path, estimate: bool = False, engine: str = "kokoro", voice: str | None = None, speed: float | None = None,
         verify: bool = False, threads: int = 4, retakes: int = 3) -> dict:
    sc = scenes(video_dir)
    say = getattr(load(video_dir, "script"), "SAY", {})
    build = build_dir(video_dir)
    audio = build / "audio"
    (audio / "sent").mkdir(parents=True, exist_ok=True)
    voice = voice or ("af_heart" if engine == "kokoro" else "alba")
    speed = speed if speed is not None else (0.95 if engine == "kokoro" else 1.0)
    vtag = Path(voice).name

    def sent_path(text: str, take: int = 0) -> Path:
        h = hashlib.sha1(f"{engine}|{vtag}|{speed}|{text}|{take}".encode()).hexdigest()[:12]
        return audio / "sent" / f"{h}.wav"

    # every sentence of every beat, as it will be spoken
    plan = {}                                   # (sid, beat) -> [spoken sentence, ...]
    for s in sc:
        for i, text in enumerate(s["beats"]):
            plan[(s["id"], i)] = [speakable(x, say) for x in sentences(text)]
    chosen: dict[str, Path] = {}                # spoken sentence -> wav
    report = []
    if not estimate:
        uniq = list(dict.fromkeys(x for v in plan.values() for x in v))
        todo = [{"text": x, "out": str(sent_path(x)), "seed": 7 + k} for k, x in enumerate(uniq) if not sent_path(x).exists()]
        print(f"{len(todo)} of {len(uniq)} sentences to synthesize ({engine}, voice {vtag})")
        if todo:
            _synthesize(todo, engine, voice, speed, build, threads)
        chosen = {x: sent_path(x) for x in uniq}
        if verify:
            res = {r["wav"]: r for r in _verify([{"wav": str(chosen[x]), "text": x} for x in uniq], build)}

            def rank(r):                        # fewer wrong words first, then a clean first word, then clarity
                return (r["errors"], r["onset"], -r["clarity"])

            def is_bad(x):
                r = res[str(chosen[x])]
                return r["errors"] > 0 or r["clarity"] < 0.2

            bad = [x for x in uniq if is_bad(x)]
            for take in range(1, retakes + 1):
                if not bad or engine != "pocket":
                    break                       # Kokoro is deterministic: a retake would be identical
                print(f"retake {take}: {len(bad)} sentences")
                jobs = [{"text": x, "out": str(sent_path(x, take)), "seed": 1000 * take + k} for k, x in enumerate(bad)]
                fresh = [j for j in jobs if not Path(j["out"]).exists()]
                if fresh:
                    _synthesize(fresh, engine, voice, speed, build, threads)
                new = {r["wav"]: r for r in _verify([{"wav": j["out"], "text": j["text"]} for j in jobs], build)}
                for j in jobs:
                    res[j["out"]] = new[j["out"]]
                    if rank(new[j["out"]]) < rank(res[str(chosen[j["text"]])]):
                        chosen[j["text"]] = Path(j["out"])
                bad = [x for x in bad if is_bad(x)]
            bad = [x for x in bad if res[str(chosen[x])]["errors"] > 0]
            report = [{"text": x, "heard_differently": res[str(chosen[x])]["diffs"]} for x in bad]
            (build / "voice_report.json").write_text(json.dumps(report, indent=1))
            print(f"listen-back: {len(uniq) - len(bad)} of {len(uniq)} sentences match their text" + (f"; see {build / 'voice_report.json'}" if bad else ""))
            for r in report[:8]:
                print("  check:", r["text"][:70], "->", r["heard_differently"][:3])

    timings: dict = {"_mode": "estimate" if estimate else f"{engine}:{vtag}"}
    words = 0
    tempo = [] if (engine == "kokoro" or abs(speed - 1.0) < 1e-3) else [f"atempo={speed}"]
    for s in sc:
        t, beats, inputs, filters, parts = LEAD_IN, [], [], [], []
        k = 0
        for i, text in enumerate(s["beats"]):
            words += len(text.split())
            sents = plan[(s["id"], i)]
            start = t
            for j, x in enumerate(sents):
                if estimate:
                    d = len(x.split()) / EST_WPS
                else:
                    d = duration(chosen[x]) / (speed if tempo else 1.0)
                    pre = (LEAD_IN if i == 0 else GAP) if j == 0 else SENT_GAP
                    inputs += ["-i", str(chosen[x])]
                    chain = ",".join(["aresample=48000", "aformat=channel_layouts=stereo", *tempo, f"adelay={int(pre * 1000)}:all=1"])
                    filters.append(f"[{k}:a]{chain}[a{k}]")
                    parts.append(f"[a{k}]")
                    k += 1
                t += d + (SENT_GAP if j + 1 < len(sents) else 0)
            beats.append({"start": round(start, 3), "dur": round(t - start, 3)})
            t += GAP
        total = math.ceil((t - GAP + TAIL) * FPS) / FPS          # a whole number of frames, so clips join without drift
        out = audio / f"{s['id']}.wav"
        if estimate:
            _ffmpeg("-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo", "-t", f"{total:.4f}", "-c:a", "pcm_s16le", out)
        else:
            filters.append(f"{''.join(parts)}concat=n={k}:v=0:a=1,apad=whole_dur={total:.4f}[out]")
            _ffmpeg(*inputs, "-filter_complex", ";".join(filters), "-map", "[out]", "-t", f"{total:.4f}", "-c:a", "pcm_s16le", out)
        timings[s["id"]] = {"beats": beats, "total": round(total, 4)}
    (build / "timings.json").write_text(json.dumps(timings, indent=1))
    tot = sum(v["total"] for k_, v in timings.items() if not k_.startswith("_"))
    print(f"wrote {build / 'timings.json'} ({timings['_mode']}): {tot / 60:.1f} min, {words} words, {words / (tot / 60):.0f} words/min overall")
    return timings
