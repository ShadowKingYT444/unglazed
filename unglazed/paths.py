"""Where things live. A video is a folder (script.py, coverage.py, world.py, scenes/); its outputs go to build/<name>/."""
from __future__ import annotations

import os
from pathlib import Path


def root() -> Path:
    """The project root: the folder you run `unglazed` from (or $UNGLAZED_ROOT)."""
    return Path(os.environ.get("UNGLAZED_ROOT", os.getcwd())).resolve()


def video_dir(video: str | os.PathLike) -> Path:
    p = Path(video)
    p = p if p.is_absolute() else root() / p
    if not (p / "script.py").exists():
        raise SystemExit(f"{p} is not a video folder (no script.py). Create one with `unglazed new <name>`.")
    return p.resolve()


def build_dir(video: str | os.PathLike | None = None) -> Path:
    """build/<video name>. Inside a render, the tool passes it through $UNGLAZED_BUILD."""
    if video is None:
        env = os.environ.get("UNGLAZED_BUILD")
        return Path(env) if env else root() / "build" / "_scratch"
    return root() / "build" / Path(video).name
