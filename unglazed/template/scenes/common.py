"""Shared setup for this video's scenes."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from unglazed.kit import *  # noqa: E402,F401,F403
from unglazed import sims  # noqa: E402,F401
import world  # noqa: E402

W = world.load()
