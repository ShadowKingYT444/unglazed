"""Synthesize beats with Kokoro. Run as a script so it can use another Python that has kokoro and torch.

    python _kokoro_worker.py jobs.json <voice name | path/to/voice.pt> <speed>
jobs.json: [{"text": "...", "out": ".../beat.wav"}, ...]

Model: hexgrad/Kokoro-82M (Apache 2.0), downloaded by the kokoro package on first use.
Set UNGLAZED_KOKORO_MODEL to a folder with config.json and kokoro-v1_0.pth to use a local copy.
"""
import json
import os
import sys
from pathlib import Path

import numpy as np
import soundfile as sf
import torch
from kokoro import KModel, KPipeline

SR = 24_000


def main():
    jobs = json.loads(Path(sys.argv[1]).read_text())
    voice, speed = sys.argv[2], float(sys.argv[3])
    device = "cuda" if torch.cuda.is_available() else "cpu"
    local = os.environ.get("UNGLAZED_KOKORO_MODEL")
    if local:
        base = Path(local)
        model = KModel(repo_id=str(base), config=str(base / "config.json"), model=str(base / "kokoro-v1_0.pth")).to(device).eval()
        pipe = KPipeline(lang_code="a", repo_id=str(base), model=model, device=device)
    else:
        pipe = KPipeline(lang_code="a", repo_id="hexgrad/Kokoro-82M", device=device)
    v = torch.load(voice, map_location="cpu", weights_only=True) if voice.endswith(".pt") else voice
    for k, job in enumerate(jobs, 1):
        chunks = []
        with torch.inference_mode():
            for r in pipe(job["text"], voice=v, speed=speed):
                if r.audio is not None:
                    chunks.append(r.audio.detach().float().cpu().numpy())
        out = Path(job["out"])
        out.parent.mkdir(parents=True, exist_ok=True)
        sf.write(out, np.concatenate(chunks), SR)
        print(f"  {k}/{len(jobs)} {out.name}", flush=True)


if __name__ == "__main__":
    main()
