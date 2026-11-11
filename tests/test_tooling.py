import json
import shutil
from pathlib import Path

import pytest

from unglazed import cli
from unglazed.coverage import check
from unglazed.paths import build_dir

REPO = Path(__file__).resolve().parents[1]
EXAMPLE = REPO / "examples" / "relf"


def test_example_covers_every_item():
    assert check(EXAMPLE, quiet=True) == []


def test_check_fails_when_an_item_has_no_scene(tmp_path, monkeypatch):
    v = tmp_path / "v"
    shutil.copytree(REPO / "unglazed" / "template", v)
    assert check(v, quiet=True) == []
    script = (v / "script.py").read_text().replace('covers=["interp", "step"]', 'covers=["interp"]')
    (v / "script.py").write_text(script)
    assert check(v, quiet=True) == ["step"]


def test_check_reports_unknown_items(tmp_path):
    v = tmp_path / "v"
    shutil.copytree(REPO / "unglazed" / "template", v)
    (v / "script.py").write_text((v / "script.py").read_text().replace('"step"]', '"step", "nope"]'))
    assert check(v, quiet=True) == ["unknown:nope"]


def test_new_then_check_from_the_command_line(tmp_path, monkeypatch):
    monkeypatch.setenv("UNGLAZED_ROOT", str(tmp_path))
    cli.main(["new", "demo"])
    with pytest.raises(SystemExit) as e:
        cli.main(["check", "demo"])
    assert e.value.code == 0


@pytest.mark.skipif(shutil.which("ffmpeg") is None, reason="ffmpeg not installed")
def test_estimated_voice_writes_timings_and_silent_audio(tmp_path, monkeypatch):
    monkeypatch.setenv("UNGLAZED_ROOT", str(tmp_path))
    cli.main(["new", "demo"])
    cli.main(["voice", "demo", "--estimate"])
    b = build_dir(tmp_path / "demo")
    tm = json.loads((b / "timings.json").read_text())
    assert tm["_mode"] == "estimate"
    beats = tm["s01"]["beats"]
    assert len(beats) == 3 and beats[0]["start"] < beats[1]["start"] < beats[2]["start"] < tm["s01"]["total"]
    assert (b / "audio" / "s01.wav").stat().st_size > 1000


def test_scripts_are_well_formed():
    from unglazed._load import scenes
    for v in (EXAMPLE, REPO / "unglazed" / "template"):
        sc = scenes(v)
        assert all(s["id"].startswith("s") and s["beats"] for s in sc)
        assert all(isinstance(b, str) and len(b.split()) >= 3 for s in sc for b in s["beats"])
