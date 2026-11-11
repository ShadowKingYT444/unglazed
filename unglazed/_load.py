"""Load a video folder's script.py / coverage.py as modules."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


def load(video_dir: Path, name: str):
    f = Path(video_dir) / f"{name}.py"
    if not f.exists():
        raise SystemExit(f"missing {f}")
    spec = importlib.util.spec_from_file_location(f"_unglazed_{Path(video_dir).name}_{name}", f)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def scenes(video_dir: Path):
    sc = load(video_dir, "script").SCENES
    ids = [s["id"] for s in sc]
    if len(set(ids)) != len(ids):
        raise SystemExit("script.py: scene ids must be unique")
    for s in sc:
        if not s.get("beats"):
            raise SystemExit(f"script.py: scene {s['id']} has no beats")
    return sc
