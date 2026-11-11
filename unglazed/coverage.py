"""The depth contract: a video lists every item it must teach, and the check fails if one has no scene.

coverage.py in a video folder:
    BRIEF = dict(viewer_knows=[...], viewer_can_after=[...], skip=[...])
    ITEMS = [dict(id="post", what="token posterior is a softmax of ...", source="Sec. 2, Eq. 2", verified=True), ...]
script.py: each scene names the items it teaches:  dict(id="s04", covers=["post", "soft"], beats=[...])

An item with verified=False was not read word for word in the source: the narration must point to the source.
An item with part=N is only required when checking with part >= N (for a video delivered in parts).
"""
from __future__ import annotations

from pathlib import Path

from ._load import load, scenes


def check(video_dir: Path, part: int = 99, quiet: bool = False) -> list[str]:
    """Print the item -> scene table and return the ids of items that no scene covers."""
    cov = load(video_dir, "coverage")
    sc = scenes(video_dir)
    where: dict[str, list[str]] = {}
    for s in sc:
        for c in s.get("covers", []):
            where.setdefault(c, []).append(s["id"])
    ids = {i["id"] for i in cov.ITEMS}
    unknown = sorted(set(where) - ids)
    missing = []
    rows = []
    for it in cov.ITEMS:
        got = where.get(it["id"], [])
        late = it.get("part", 1) > part
        if not got and not late:
            missing.append(it["id"])
        flag = ",".join(got) or ("(later part)" if late else "MISSING")
        mark = "" if it.get("verified", True) else "  [not read word for word]"
        rows.append(f"{it['id']:12s} {flag:16s} {it.get('source', ''):24s} {it['what'][:84]}{mark}")
    words = sum(len(b.split()) for s in sc for b in s["beats"])
    if not quiet:
        brief = getattr(cov, "BRIEF", {})
        for k in ("viewer_knows", "viewer_can_after", "skip"):
            if brief.get(k):
                print(f"{k}:")
                for line in brief[k]:
                    print(f"  - {line}")
        print(f"\n{'item':12s} {'scenes':16s} {'source':24s} what")
        print("\n".join(rows))
        print(f"\n{len(cov.ITEMS)} items, {len(cov.ITEMS) - len(missing)} covered, {len(sc)} scenes, {words} words "
              f"(about {words / 145:.0f} minutes)")
        if unknown:
            print("scenes cite items that are not in coverage.py:", unknown)
        if missing:
            print("NOT COVERED:", missing)
    return missing + [f"unknown:{u}" for u in unknown]
