"""The teaching contract: a script is checked for the moves that make an explanation stick, not only for coverage.

script.py declares
    THESIS = "one sentence the whole video proves"
    LADDER = [dict(rung="the two-number world", scenes=["s02", "s03"]), ...]     # small cases, same recipe
    SCENES = [dict(id="s05", q="Which line am I on?", move=["question", "build"], new=["guess"], covers=[...], beats=[...])]
coverage.py declares
    GLOSSARY = {"guess": "the average of all the places you could be heading"}     # every term the video introduces
    ITEMS = [dict(id=..., kind="component", ...)]                                  # parts whose necessity must be shown

See docs/PEDAGOGY.md for the policy and the reasons. Errors fail `unglazed check`; warnings are printed.
"""
from __future__ import annotations

import re
from pathlib import Path

from ._load import load, scenes
from .lexicon import sentences

MOVES = {
    "hook": "the viewer's own question, and what is unsatisfying about the usual answer",
    "question": "pose the problem the next idea solves; make something familiar strange",
    "predict": "ask the viewer to commit to a guess before the reveal",
    "build": "construct the idea on a small concrete case, in the picture",
    "name": "only now give the formal name or equation for what was built",
    "why": "why this exact form: show the simpler form failing",
    "break": "remove the part and show what goes wrong",
    "verify": "check the claim by experiment on the world, and say where the check is imperfect",
    "objection": "say the viewer's doubt out loud, then answer it",
    "analogy": "a second view AFTER the mechanism, mapped back part by part, with where it stops working",
    "recap": "what we have, in the viewer's words, and what is still open",
    "transfer": "connect to something the viewer already trusts, or apply the recipe to a new case",
    "limits": "what was simplified, deferred or is unknown",
}
MAX_NEW_PER_SCENE = 2
MAX_SCENES_WITHOUT_RECAP = 6
MAX_SENTENCE_WORDS = 36
MAX_BEAT_WORDS = 85


def _first_use(term: str, sc: list[dict]) -> int | None:
    pat = re.compile(rf"(?<![\w-]){re.escape(term)}(?:s|es)?(?![\w-])", re.I)
    for k, s in enumerate(sc):
        if any(pat.search(b) for b in s["beats"]):
            return k
    return None


def check(video_dir: Path, quiet: bool = False) -> tuple[list[str], list[str]]:
    script = load(video_dir, "script")
    cov = load(video_dir, "coverage")
    sc = scenes(video_dir)
    glossary: dict = getattr(cov, "GLOSSARY", {})
    errors, warns = [], []

    thesis = getattr(script, "THESIS", "")
    if not thesis:
        errors.append("script.py has no THESIS: write the one sentence the whole video proves")
    elif len(thesis.split()) > 45:
        errors.append(f"THESIS is {len(thesis.split())} words: if it does not fit in one breath it is not one idea yet")

    ladder = getattr(script, "LADDER", [])
    if len(ladder) < 2:
        warns.append("no LADDER with at least two rungs: teach on a small case first, then repeat the same recipe on a harder one")
    else:
        ids = {s["id"] for s in sc}
        for r in ladder:
            for sid in r.get("scenes", []):
                if sid not in ids:
                    errors.append(f"LADDER rung '{r.get('rung')}' names unknown scene {sid}")

    introduced: dict[str, int] = {}
    since_recap = 0
    for k, s in enumerate(sc):
        sid = s["id"]
        q = s.get("q", "")
        if not q.strip().endswith("?"):
            errors.append(f"{sid}: no question (q=...?). Every scene answers a question the viewer has by then")
        moves = s.get("move", [])
        if not moves:
            errors.append(f"{sid}: no teaching move (move=[...]); choose from {', '.join(MOVES)}")
        for m in moves:
            if m not in MOVES:
                errors.append(f"{sid}: unknown move '{m}'")
        new = s.get("new", [])
        if len(new) > MAX_NEW_PER_SCENE:
            errors.append(f"{sid}: introduces {len(new)} new terms ({', '.join(new)}); at most {MAX_NEW_PER_SCENE} per scene")
        for term in new:
            if term not in glossary:
                errors.append(f"{sid}: new term '{term}' has no plain-words entry in GLOSSARY (coverage.py)")
            introduced.setdefault(term, k)
        since_recap = 0 if "recap" in moves else since_recap + 1
        if since_recap > MAX_SCENES_WITHOUT_RECAP:
            warns.append(f"{sid}: {since_recap} scenes since the last recap; the viewer needs a place to consolidate")
            since_recap = 0
        for b in s["beats"]:
            if len(b.split()) > MAX_BEAT_WORDS:
                warns.append(f"{sid}: a beat of {len(b.split())} words; split it so the picture can change")
            for sent in sentences(b):
                if len(sent.split()) > MAX_SENTENCE_WORDS:
                    warns.append(f"{sid}: a sentence of {len(sent.split())} words: \"{sent[:60]}...\"")

    for term in glossary:
        used = _first_use(term, sc)
        if term not in introduced:
            if used is not None:
                errors.append(f"term '{term}' is spoken in {sc[used]['id']} but no scene lists it in new=[...]")
            continue
        if used is not None and used < introduced[term]:
            errors.append(f"term '{term}' is spoken in {sc[used]['id']} before {sc[introduced[term]]['id']} introduces it: need before name")

    if sc and "hook" not in sc[0].get("move", []):
        warns.append(f"{sc[0]['id']}: the first scene has no 'hook' (the viewer's question and what is unsatisfying about the usual answer)")
    if sc and not ({"recap", "transfer"} & set(sc[-1].get("move", []))):
        warns.append(f"{sc[-1]['id']}: the last scene has neither 'recap' nor 'transfer'")
    all_moves = {m for s in sc for m in s.get("move", [])}
    for m, why in (("predict", "ask the viewer to guess before a reveal at least once"),
                   ("objection", "voice at least one doubt the viewer will have"),
                   ("verify", "check at least one claim by experiment"),
                   ("limits", "say what was simplified or deferred")):
        if m not in all_moves:
            warns.append(f"no scene uses the move '{m}': {why}")

    shown = {}
    for s in sc:
        if {"break", "verify"} & set(s.get("move", [])):
            for c in s.get("covers", []):
                shown[c] = s["id"]
    for it in getattr(cov, "ITEMS", []):
        if it.get("kind") == "component" and it["id"] not in shown:
            errors.append(f"component '{it['id']}' is never broken or verified: add a scene with move 'break' or 'verify' that covers it")

    built = set()
    for s in sc:
        mv = set(s.get("move", []))
        if "analogy" in mv and not ({"build", "name"} & mv) and not (set(s.get("covers", [])) & built) and s.get("covers"):
            warns.append(f"{s['id']}: an analogy before its mechanism was built; analogies come second")
        if {"build", "name", "verify"} & mv:
            built |= set(s.get("covers", []))

    if not quiet:
        if thesis:
            print(f"thesis: {thesis}")
        for r in ladder:
            print(f"  rung: {r.get('rung')}  ({', '.join(r.get('scenes', []))})")
        counts = {m: sum(m in s.get('move', []) for s in sc) for m in MOVES}
        print("moves: " + ", ".join(f"{m} {n}" for m, n in counts.items() if n))
        for w in warns:
            print("warning:", w)
        for e in errors:
            print("ERROR:", e)
        print(f"pedagogy: {len(errors)} errors, {len(warns)} warnings")
    return errors, warns
