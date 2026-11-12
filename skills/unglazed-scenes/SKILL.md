---
name: unglazed-scenes
description: Step 4 of an unglazed video. Write the ManimGL scenes with the unglazed kit so that pictures are computed, synced to narration beats and well placed on the frame. Use when writing or fixing scenes/p*.py, when a layout looks crowded or small, or when a render fails or is slow.
---

# Scenes

Scene files are `<video>/scenes/p*.py`. Classes are `S01`, `S02`, ... , subclass `BeatScene`, and set `SID`.
Put shared setup (loading the world, the recurring picture, code constants) in `scenes/common.py`.

```python
class S06(BeatScene):
    SID = "s06"

    def construct(self):
        xt = XT()                                  # the recurring picture of this video (from common.py)
        self.add(xt.axes())
        self.at(1)                                 # wait for narration beat 1
        d = self.dur(1)
        self.play(FadeIn(here, scale=2), run_time=0.5)
        self.wait(max(0.1, d * 0.5 - 0.5))         # time by fractions of the beat, never by fixed seconds
        self.play(ShowCreation(lines), run_time=1.0)
        self.finish()
```

## One recurring picture per rung

Choose one picture for each rung of the ladder and keep it for the whole rung: the same axes, the same place on
the frame, the same colours. New ideas are added **to** it. A viewer who has learned to read the picture can spend
their attention on the idea. Do not introduce a new kind of diagram for every scene.

## Placement: compose from `Stage` zones

```python
place(code, Stage.right)             # fit into the zone and centre it; shrinks, never enlarges unless grow=True
title = concept_title("flow matching")
box = focus(bars.rows[2][1])         # the one "look here" box of the moment
```

`Stage.title`, `main`, `full`, `left`/`right`, `left_wide`/`right_narrow`, `left_narrow`/`right_wide`,
`top`/`bottom`, `foot`.

- One main object, large. Or two balanced columns: the picture on one side, the algebra, bars or code on the other.
- Recurring things keep their place. A label sits next to its object, outside the paths that cross it.
- Text sizes: 0.3 is the smallest comfortable label; titles 0.44; a result the viewer must remember 0.5.
- Empty space is fine. A sparse frame with one large object reads better than a full frame of small ones.
- When something new appears, something old dims or leaves. Never more than about five labelled things lit at once.

Every `self.at(i)` runs a layout check of the finished previous beat and prints lines like
`[s06] LAYOUT beat 3: 'guess 0.54' overlaps 'the average'` (off-frame, overlapping, or too small to read).
Treat each line as a failing test. Then make the sheet and **look**: the lint cannot see a label lying on top of a
curve, a picture that is too small, or a beat whose picture does not show what the voice says.

```bash
unglazed render <video> s05 s06 --draft && unglazed sheet <video> s06 --draft
```

## The kit

| Piece | For |
|---|---|
| `BeatScene` | `at(i)`, `dur(i)`, `left(i)`, `start(i)`, `chapter(n, title)`, `self.clock`, `finish()` |
| `Tx`, `M`, `ladder`, `fit` | serif text, math without LaTeX (matplotlib mathtext), stacked rows, shrink to width |
| `Stage`, `place`, `focus`, `concept_title` | zones and placement |
| `Plot`, `BarChart`, `Bars` | curves, result charts, live probability bars (`set_values`) |
| `Heat`, `spread_cols` | matrices as cells, columns lined up with a row of tokens |
| `CodePanel` | the code the viewer should be able to write; `hl(i, j)` lights lines |
| `Space`, `Cloud`, `Paths`, `Field`, `segments`, `growing_segments` | thousands of points, trails, arrow fields |
| `Tile`, `Flipbook`, `noise_img` | real pixels |
| `Chip`, `token_row`, `ModelBox`, `TimeBar`, `halo`, `ring`, `arrow` | tokens, networks, the clock, markers |

Code is a picture: if the viewer should be able to implement the method, show the loop and light the line each
scene explains. Colours keep one meaning for the whole video (`NOISE`, `DATA`, `HOT` for motion or "you are
here", `BLUE` for the model's guess, `RED` for a problem).

## Speed

- Held frames are free: a `wait()` with nothing moving is drawn once. So prefer "change, then hold" over slow
  continuous motion, and clear updaters as soon as an animation ends.
- Updaters that only read a tracker (`self.clock`) are fine. Time-based updaters `(mob, dt)` disable the fast path.
- `--draft` is 480p at 15 fps. Unchanged scenes are skipped (hash of the scene, the world, the kit and the timings).
  `--jobs 2` renders two scenes at once. Encoding uses NVENC when the GPU has it.

## Gotchas (each of these cost an hour once)

- An updater with two or more parameters is called as `(mobject, dt)`. Never write `lambda m, i=i: ...`; build the
  closure with a factory function.
- Freeze anything with an updater (`clear_updaters()`) before fading or transforming it. Fade a `Flipbook` with
  `appear()` / `vanish()`. To move a whole live picture, move the camera (`self.frame.animate`).
- `arrow()` returns a stroke arrow: animate it with `ShowCreation`, not `GrowArrow`, and keep it longer than its tip.
- `M()`: use `\\dfrac`, and never split one `M()` part inside a fraction or a root.
- `self.chapter()` holds the card until beat 1. If beat 0 continues after the chapter is announced, show a short
  card yourself and go on.
- After moving parts of a group by hand, call `refresh_bounding_box(recurse_down=True)` before placing things
  relative to it.
