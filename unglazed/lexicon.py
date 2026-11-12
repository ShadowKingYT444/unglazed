"""How to say things. The script stays readable; these replacements are applied only to the text sent to the voice.

Add video-specific entries in script.py:   SAY = {"ReLF": "relf", "x hat": "x-hat"}
Keys are matched as whole words, case-insensitively. Keep this list short: add a word only after you heard it go wrong
(or after `unglazed voice --verify` flagged it).
"""
from __future__ import annotations

import re

DEFAULT = {
    "logit": "lowjit",
    "logits": "lowjits",
    "denoiser": "de-noiser",
    "denoise": "de-noise",
    "denoising": "de-noising",
    "softmax": "soft max",
    "argmax": "arg max",
    "i.e.": "that is",
    "e.g.": "for example",
    "vs": "versus",
}

MIN_WORDS = 4
SENT_END = re.compile(r"(?<=[.!?])\s+(?=[A-Z0-9\"'(])")


def speakable(text: str, extra: dict | None = None) -> str:
    table = {**DEFAULT, **(extra or {})}
    for k in sorted(table, key=len, reverse=True):
        text = re.sub(rf"(?<![\w-]){re.escape(k)}(?![\w-])", table[k], text, flags=re.I)
    return text


def sentences(text: str) -> list[str]:
    """Split a beat into sentences. Each sentence is spoken on its own, which resets the intonation naturally."""
    parts = [p.strip() for p in SENT_END.split(text.strip()) if p.strip()]
    out: list[str] = []
    for p in parts:                       # short fragments ("Map it back.") are where a voice model stumbles:
        if out and (len(p.split()) < MIN_WORDS or len(out[-1].split()) < MIN_WORDS):
            out[-1] = out[-1] + " " + p   # say them in one breath with a neighbour
        else:
            out.append(p)
    return out
