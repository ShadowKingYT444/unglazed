"""Synthesize sentences with Pocket TTS (Kyutai), a small CPU model that follows the sentence's intonation.

    python _pocket_worker.py jobs.json <voice> <threads>
jobs.json: [{"text": "...", "out": ".../x.wav"}, ...]
voice: a reference recording to clone (wav, about 10 to 30 seconds), a saved voice state (.npz / .safetensors),
       or the name of a built-in voice.

Two backends, tried in this order:
  1. a local ONNX export (set UNGLAZED_POCKET_DIR to the folder that holds pocket_tts_onnx.py): no PyTorch needed
  2. the `pocket-tts` package (pip install pocket-tts)
"""
import json
import os
import sys
from pathlib import Path

import numpy as np
import soundfile as sf


def clean_reference(path, max_s=24.0, min_s=8.0):
    """Cut a reference recording so that it ends in a pause, with silence after it.

    The model continues from the end of the reference. If the clip stops in the middle of a phrase, the first word
    of every generated sentence comes out mangled or clipped. So: keep at most max_s seconds, end at the longest
    pause, fade out, and append 0.4 s of silence. Best of all is to supply a clip that ends at the end of a sentence.
    """
    src = Path(path)
    out = src.with_suffix(".ref.wav")
    if out.exists() and out.stat().st_mtime >= src.stat().st_mtime:
        return str(out)
    a, sr = sf.read(src, dtype="float32")
    if a.ndim > 1:
        a = a.mean(1)
    hop = int(0.02 * sr)
    n = len(a) // hop
    rms = np.sqrt((a[: n * hop].reshape(n, hop) ** 2).mean(1) + 1e-12)
    quiet = rms < 0.06 * np.percentile(rms, 95)
    runs, k = [], 0
    while k < n:
        if quiet[k]:
            j = k
            while j < n and quiet[j]:
                j += 1
            if (j - k) * 0.02 >= 0.3 or j == n:
                runs.append((k * 0.02, (j - k) * 0.02))
            k = j
        else:
            k += 1
    end = min(len(a) / sr, max_s)
    inside = [r for r in runs if min_s <= r[0] <= max_s]
    if len(a) / sr > max_s and inside:
        end = max(inside, key=lambda r: r[1])[0] + 0.12
    elif runs and runs[-1][0] + runs[-1][1] >= n * 0.02 - 0.05 and runs[-1][0] <= max_s:
        end = runs[-1][0] + 0.12                                  # already ends in silence: keep it all
    seg = a[: int(end * sr)].copy()
    f = min(len(seg), int(0.1 * sr))
    seg[-f:] *= np.linspace(1, 0, f)
    sf.write(out, np.concatenate([seg, np.zeros(int(0.4 * sr), dtype=np.float32)]), sr)
    return str(out)


def polish(a, sr, target=0.07):
    """Even loudness from sentence to sentence, and no click at either end."""
    a = np.asarray(a, dtype=np.float32)
    loud = np.sqrt((a ** 2).mean() + 1e-12)
    a = a * min(target / loud, 0.95 / (np.abs(a).max() + 1e-9))
    f0, f1 = int(0.008 * sr), int(0.03 * sr)
    if len(a) > f0 + f1:
        a[:f0] *= np.linspace(0, 1, f0)
        a[-f1:] *= np.linspace(1, 0, f1)
    return a


def onnx_backend(voice, threads):
    root = Path(os.environ["UNGLAZED_POCKET_DIR"])
    sys.path.insert(0, str(root))
    from pocket_tts_onnx import PocketTTSOnnx
    tts = PocketTTSOnnx(temperature=float(os.environ.get("UNGLAZED_POCKET_TEMP", "0.2")), precision=os.environ.get("UNGLAZED_POCKET_PRECISION", "fp32"), intra_op_num_threads=threads)
    state = voice
    if not str(voice).endswith((".npz", ".safetensors")) and Path(voice).exists():
        ref = clean_reference(voice)
        cached = Path(ref).with_suffix(f".{tts.precision}.pocket_state.npz")   # conditioning on the reference is done once
        voice = ref
        if not cached.exists() or cached.stat().st_mtime < Path(ref).stat().st_mtime:
            tts.save_voice_state(voice, str(cached))
        state = str(cached)
    return (lambda text: np.asarray(tts.generate(text, voice=state), dtype=np.float32)), tts.sample_rate


def pip_backend(voice, threads):
    import torch
    from pocket_tts import TTSModel
    torch.set_num_threads(threads)
    model = TTSModel.load_model()
    if Path(voice).exists():
        voice = clean_reference(voice)
    state = model.get_state_for_audio_prompt(voice)
    return (lambda text: model.generate_audio(state, text).numpy().astype(np.float32)), model.sample_rate


def main():
    jobs = json.loads(Path(sys.argv[1]).read_text())
    voice, threads = sys.argv[2], int(sys.argv[3])
    say, sr = (onnx_backend if os.environ.get("UNGLAZED_POCKET_DIR") else pip_backend)(voice, threads)
    for k, job in enumerate(jobs, 1):
        seed = job.get("seed")
        if seed is not None:
            np.random.seed(seed)
        audio = polish(say(job["text"]), sr)
        out = Path(job["out"])
        out.parent.mkdir(parents=True, exist_ok=True)
        sf.write(out, audio, sr)
        print(f"  {k}/{len(jobs)} {out.name}", flush=True)


if __name__ == "__main__":
    main()
