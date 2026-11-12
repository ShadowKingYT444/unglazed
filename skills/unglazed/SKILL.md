---
name: unglazed
description: Make a technical explainer video of a paper or method that derives every step and is built to be remembered. Use when the user asks for an explainer, a video walkthrough or an animated explanation of a paper, an algorithm or a piece of math. This is the entry point; it calls the four step skills (unglazed-source, unglazed-teach, unglazed-scenes, unglazed-voice).
---

# unglazed: the workflow

The failure this prevents: a video that looks good and teaches little, because the content was cut to fit a pace,
the pictures were borrowed from another video, or the explanation recited the paper in the paper's order.

Do the steps in this order. Do not start with scenes. Each step has its own skill file; read it when you get there.

| Step | Skill | You produce | Gate |
|---|---|---|---|
| 0 | this file | install, a brief | `unglazed --version` |
| 1 | `unglazed-source` | `coverage.py` (brief, items, glossary), `world.py` | numbers print and match the paper |
| 2 | `unglazed-teach` | `script.py` (thesis, ladder, scenes with a question and moves) | `unglazed check <video>`: 0 errors |
| 3 | `unglazed-voice` | narration and `timings.json` | listen-back report read |
| 4 | `unglazed-scenes` | `scenes/p*.py` | a frame of every beat looked at, no LAYOUT lines |
| 5 | this file | `unglazed build <video>` | honest report |

## 0. Before anything

- `unglazed --version`. If it is missing: `uv tool install "unglazed[voice] @ git+https://github.com/ShadowKingYT444/unglazed"`.
- Ask, or infer and write down, two things: **what the viewer already knows**, and **what they must be able to do
  after watching**. "Understand X" is not an answer. "Compute one step by hand" is.
- `unglazed new <video>` makes the folder from the template.

## The loop you will actually run

```bash
unglazed check <video>                     # coverage + teaching contract; fix every error
unglazed voice <video> --estimate          # silent timings, so scenes can be drafted before a voice exists
unglazed render <video> s03 s04 --draft    # 480p, 15 fps; unchanged scenes are skipped
unglazed sheet <video> s03 --draft         # one frame per beat; LOOK at build/<video>/sheets/s03.jpg
unglazed voice <video> --engine pocket --voice ref.wav --verify
unglazed build <video>                     # check + voice + 1080p + join -> build/<video>/<video>.mp4
```

Work in batches of three or four scenes: write, draft, look, fix. Never write all scenes before looking at one.

## 5. Report honestly

Say which frames you looked at, what you did not watch or listen to in real time, which coverage items are
`verified=False`, which numbers come from the toy world rather than the paper, and what the listen-back report
still flags. Do not call the video finished on the strength of a clean render.
