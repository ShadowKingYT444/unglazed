import json
import shutil
from pathlib import Path

import pytest

from unglazed import cli
from unglazed.coverage import check
from unglazed.paths import build_dir

REPO = Path(__file__).resolve().parents[1]
EXAMPLE = REPO / "examples" / "rectflow"


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


# ---- the teaching contract
def _template(tmp_path):
    v = tmp_path / "v"
    shutil.copytree(REPO / "unglazed" / "template", v)
    return v


def test_template_and_example_pass_the_teaching_check(tmp_path):
    from unglazed import pedagogy
    assert pedagogy.check(_template(tmp_path), quiet=True)[0] == []
    errors, warnings = pedagogy.check(EXAMPLE, quiet=True)
    assert errors == [] and warnings == []


def test_teaching_check_wants_a_question_for_every_scene(tmp_path):
    from unglazed import pedagogy
    v = _template(tmp_path)
    s = (v / "script.py").read_text()
    import re
    (v / "script.py").write_text(re.sub(r'q="[^"]*\?"', 'q="No question"', s, count=1))
    assert any("no question" in e for e in pedagogy.check(v, quiet=True)[0])


def test_teaching_check_catches_a_term_used_before_it_is_introduced():
    from unglazed import pedagogy
    sc = [dict(id="s01", beats=["We follow the velocity."]), dict(id="s02", beats=["Now the velocity is named."])]
    assert pedagogy._first_use("velocity", sc) == 0
    assert pedagogy._first_use("velocities", sc) is None or pedagogy._first_use("velocities", sc) == 0


# ---- narration helpers
def test_short_sentences_are_spoken_with_a_neighbour():
    from unglazed.lexicon import sentences, speakable
    out = sentences("Map it back. The fog is not knowing the end of your line. Near a word. Not on it.")
    assert all(len(x.split()) >= 4 for x in out)
    assert " ".join(out).count("Map it back.") == 1
    assert speakable("the logit grows") == "the lowjit grows"


def test_a_reference_clip_is_cut_at_a_pause_and_ends_in_silence(tmp_path):
    np = pytest.importorskip("numpy")
    sf = pytest.importorskip("soundfile")
    from unglazed._pocket_worker import clean_reference
    sr = 16000
    t = np.arange(sr * 30) / sr
    a = 0.3 * np.sin(2 * np.pi * 180 * t).astype("float32")
    for start, dur in ((6.0, 0.4), (19.0, 0.8), (27.0, 0.5)):       # three pauses; the long one is at 19 s
        a[int(start * sr): int((start + dur) * sr)] = 0
    src = tmp_path / "ref.wav"
    sf.write(src, a, sr)
    out, sr2 = sf.read(clean_reference(str(src)))
    assert 19.0 < len(out) / sr2 < 19.8                              # cut just inside the long pause, plus silence
    assert abs(out[-int(0.3 * sr2):]).max() == 0
