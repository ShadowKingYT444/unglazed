"""Listen back: transcribe each synthesized sentence and report how far it is from its text (word error rate).

    python _asr_worker.py jobs.json out.json        jobs: [{"wav": "...", "text": "..."}]
Uses faster-whisper (pip install faster-whisper). Model: UNGLAZED_ASR_MODEL (default small.en), on the CPU by default.
"""
import difflib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

import numpy as np
from faster_whisper import WhisperModel

NUM = {"0": "zero", "1": "one", "2": "two", "3": "three", "4": "four", "5": "five", "6": "six", "7": "seven", "8": "eight", "9": "nine", "10": "ten"}


SAME = {"recognise": "recognize", "colour": "color", "centre": "center", "travellers": "travelers", "ok": "okay"}


def norm(s):
    s = re.sub(r"[^a-z0-9 ]", " ", s.lower().replace("any more", "anymore").replace("-", " "))
    return [SAME.get(NUM.get(w, w), NUM.get(w, w)) for w in s.split()]


def main():
    jobs = json.loads(Path(sys.argv[1]).read_text())
    device = os.environ.get("UNGLAZED_ASR_DEVICE", "cpu")
    m = WhisperModel(os.environ.get("UNGLAZED_ASR_MODEL", "small.en"), device=device, compute_type="int8" if device == "cpu" else "int8_float16")
    out = []
    for j in jobs:
        raw = subprocess.check_output(["ffmpeg", "-v", "error", "-i", j["wav"], "-ac", "1", "-ar", "16000", "-f", "s16le", "-"])
        audio = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768
        segs, _ = m.transcribe(audio, language="en", word_timestamps=True)
        segs = list(segs)
        probs = [w.probability for x in segs for w in (x.words or [])]
        hyp, ref = norm(" ".join(x.text for x in segs)), norm(j["text"])
        sm = difflib.SequenceMatcher(a=ref, b=hyp)
        ops = [op for op in sm.get_opcodes() if op[0] != "equal"]
        # digits against number words are not errors: only count words that differ and are not numeric
        diffs = [(" ".join(ref[a1:a2]), " ".join(hyp[b1:b2])) for _t, a1, a2, b1, b2 in ops
                 if not all(w.isdigit() for w in hyp[b1:b2]) or a2 == a1]
        err = sum(max(len(a.split()), len(b.split())) for a, b in diffs)
        onset = bool(ref and (not hyp or hyp[0] != ref[0]))          # a wrong first word is the commonest fault
        out.append({"wav": j["wav"], "wer": err / max(1, len(ref)), "errors": err, "diffs": diffs, "onset": onset,
                    "clarity": float(min(probs)) if probs else 0.0})
    Path(sys.argv[2]).write_text(json.dumps(out))


if __name__ == "__main__":
    main()
