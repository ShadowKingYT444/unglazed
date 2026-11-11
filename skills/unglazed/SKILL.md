---
name: unglazed
description: Make a technical explainer video of a paper or method that derives every step. Use when the user asks for an explainer, a video walkthrough or an animated explanation of a paper, an algorithm or a piece of math, and wants depth rather than a summary. Uses the `unglazed` CLI (ManimGL scenes, local Kokoro narration, a coverage check).
---

# unglazed: explainer videos that do not skip steps

The failure this skill prevents: a video that looks good and teaches little, because the content was cut to fit a
pace, or the pictures were borrowed from another video. Follow the order below. Do not start with scenes.

## 0. Before anything

- Run `unglazed --version`. If it is missing, install it: `uv tool install "unglazed[voice] @ git+https://github.com/ShadowKingYT444/unglazed"`.
- Ask (or infer from the request) two things, and write them down in the brief:
  **what the viewer already knows**, and **what they must be able to do after watching**.
  "Understand X" is not an answer. "Write the training step from memory" is.

## 1. Read the source itself

Read the paper (the HTML or PDF), not a summary and not your memory of it. Extract every mechanism, equation,
hyperparameter and result with its section, equation or table number. If you could not read something word for
word, record that.

## 2. Write `coverage.py` first

```bash
unglazed new <video>
```

Fill `<video>/coverage.py`:

- `BRIEF`: `viewer_knows`, `viewer_can_after`, `skip`.
- `ITEMS`: one entry per thing the video must teach: `id`, `what`, `source` (where it is in the paper),
  `verified=False` if you did not read it word for word, `part=N` if the video is delivered in parts.

The list decides the length. Never shorten a video by dropping items the brief needs.

## 3. Build the world (`world.py`)

Make a world small enough to compute exactly with the paper's own formulas (a few tokens, two dimensions, a dozen
sentences). Use it for every picture and every number that is not quoted from the paper. Check the paper's claims on
it where you can (a bound, an identity, an ablation direction) and show the check. No manim imports in this file.

## 4. Write `script.py`

- One scene per idea, one beat per sentence group, written for the ear: short sentences, numbers spelled out.
- Each scene lists the items it teaches: `covers=["post", "soft"]`.
- Scene shape: the object, then the equation on the object, then numbers in the equation, then what breaks without it.
- Say the paper's equation numbers. Say the paper's own cautions.
- For an item with `verified=False`, describe the idea and point to the place in the paper. Do not invent a formula.

```bash
unglazed check <video>      # must pass before any scene is written
```

## 5. Voice and timings

```bash
unglazed voice <video> --estimate     # draft timings, silent
unglazed voice <video>                # Kokoro narration (cached per beat)
```

## 6. Scenes, a few at a time

Scene files are `<video>/scenes/p*.py`; classes are `S01`, `S02`, ... and subclass `BeatScene`; `SID` matches the
scene id. `self.at(i)` waits for beat `i`. Time things with fractions of `self.dur(i)` and `self.left(i + 1)`, never
with fixed seconds.

```bash
unglazed render <video> s03 s04 --draft
unglazed sheet <video> s03 s04 --draft     # then LOOK at build/<video>/sheets/s03.jpg
```

Look at every sheet. Fix overlaps, text that runs off the frame, and pictures that do not show what the beat says.
Only then render at full quality.

### Rules for pictures

- Take the style of a reference (dark canvas, sparse labels, colour with a fixed meaning). Never copy its pictures.
  Draw the paper's own objects: its matrices, tables, losses, loops.
- Code is a picture. If the viewer should be able to implement the method, show the loop with `CodePanel` and light
  the line each scene explains.
- Colours keep one meaning for the whole video (`NOISE`, `DATA`, `HOT` for motion, `BLUE` for the model's guess,
  `RED` for a problem).
- If the toy needs an assumption the paper does not make, say so on screen.

### Kit gotchas (these cost hours)

- An object that follows the clock (`Cloud.follow`, `Paths(tracker=...)`, `Field`, a `Flipbook`, anything with an
  updater that changes its points) must be frozen with `clear_updaters()` before you fade or transform it.
  Fade a `Flipbook` with `appear()` / `vanish()`.
- To move a whole live picture, move the camera (`self.frame.animate`), not the objects.
- An updater with two parameters is called as `(mobject, dt)`. Never write `lambda m, i=i: ...`; make the closure
  another way.
- `M()` draws math with matplotlib mathtext: use `\\dfrac` for readable fractions, and never split one `M()` part
  inside a fraction or a root.
- Use `fit(mob, max_width)` for long formulas and `spread_cols(heat, xs)` to line a matrix up with a row of tokens.
- `segments()` draws thousands of lines as one object; `growing_segments()` when all must grow together.

## 7. Build and report

```bash
unglazed build <video>
```

Report honestly: which frames you checked, what you did not watch in real time, which items were not verified word
for word, and any number that came from the toy world rather than the paper.
