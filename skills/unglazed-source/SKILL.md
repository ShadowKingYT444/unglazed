---
name: unglazed-source
description: Step 1 of an unglazed video. Read the paper itself, write the coverage list and glossary (coverage.py), and build a small world that computes the paper's formulas exactly (world.py). Use before any script or scene is written.
---

# Source, coverage and world

## Read the source itself

Read the paper (HTML or PDF), not a summary and not your memory of it. For every mechanism, equation,
hyperparameter and result, note the section, equation or table number. If you could not read something word for
word (an appendix behind a broken link, a number from a secondary summary), record that: it becomes
`verified=False`, and the narration points to the paper instead of stating it as fact.

## `coverage.py`

```python
BRIEF = dict(
    title="...",
    viewer_knows=["..."],                # be specific: "softmax and cross entropy", not "ML basics"
    viewer_can_after=["compute one step by hand", "say what breaks without X"],
    skip=["the proof of the marginal property"],      # said out loud in the video as deferred
)
GLOSSARY = {"guess": "the model's prediction of the finished thing, made from the unfinished one"}
ITEMS = [
    dict(id="post", source="Eq. 6", what="which word made this point: prior times closeness"),
    dict(id="singular", source="Eq. 5-6, Thm 3.1", kind="component", what="..."),
    dict(id="reflow_text", source="Sec. 3.4", verified=False, what="..."),
]
```

- One item per thing the video must teach. The list decides the length. Never shorten by dropping items.
- `kind="component"` marks a part of the method whose necessity must be **shown**: some scene has to break it or
  verify it (`unglazed check` enforces this).
- `GLOSSARY` holds every term the video introduces, in plain words a newcomer would use. If you cannot write the
  plain-words line, you do not understand the term well enough to teach it yet.

## `world.py`

Find the **smallest world in which the whole idea already happens** and can be computed exactly, then one or two
larger ones that reuse the same recipe (these become the rungs of the ladder in `unglazed-teach`).

- Compute with the paper's own formulas. `unglazed.sims` has exact flow-matching math for finite data.
- Every picture and every number that is not quoted from the paper comes from here. No manim imports in this file.
- Check the paper's claims on the world where you can (a bound, an identity, the direction of an ablation), and
  keep the numbers: a claim the viewer watches hold is worth more than a claim they are told.
- Print the numbers the narration will say (`python world.py`) and copy them from that output, never from memory.
  If the toy needs an assumption the paper does not make, write it down; it must be said on screen.
- Cache the result (`build/<video>/world.pkl`) so scenes load instantly.
