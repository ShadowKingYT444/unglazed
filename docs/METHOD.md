# How to make a technical explainer that does not skip steps

This is the method the kit enforces. It exists because the first video made with the kit looked good and taught
little: it copied a reference video's pictures and cut the content to match its pace.

## The order of work

| Step | File | What it fixes |
|---|---|---|
| 1. Brief | `<video>/coverage.py` → `BRIEF` | Who watches, what they already know, what they must be able to DO afterwards, what to skip |
| 2. Coverage list | `<video>/coverage.py` → `ITEMS` | Every mechanism, equation and number from the source, each with its section or table. Read the source itself |
| 3. World | `<video>/world.py` | A small world where the source's own formulas can be computed exactly, so pictures and numbers are real |
| 4. Script | `<video>/script.py` | One scene per idea, one beat per sentence group. Each scene lists the coverage items it teaches |
| 5. Check | `unglazed check <video>` | Fails if an item has no scene, or a scene cites an unknown item |
| 6. Scenes | `<video>/scenes/p*.py` | Draft at 480p, look at a frame per beat (`unglazed sheet`), fix, then render 1080p |
| 7. Assemble | `unglazed build <video>` | Joins clips and narration, writes chapters |

Length is an output of step 2, not an input. A short video comes from a short coverage list, never from cutting.

## The shape of a scene

1. **The object.** Show the thing the equation is about: the matrix, the table, the cloud, the code line.
2. **The equation, on the object.** Derive it in at most a few rows. Say the source's equation number.
3. **Numbers.** Put values into it, from the world. A viewer who sees `0.96 E(the) + 0.04 (others)` believes the formula.
4. **What breaks without it.** Run the world with the part removed, or show the source's ablation.

## Rules for pictures

- Take the **style** of a reference (dark canvas, sparse labels, colour with a fixed meaning), never its pictures.
  The pictures come from the source's own objects.
- Every number on screen is either quoted from the source with its location, or computed in `world.py`.
  If an item could not be read word for word, mark it `verified=False` and point to the source in the narration.
- Code is a picture. If the viewer should be able to implement the method, show the loop and light the line that
  each scene explains.
- If a toy needs an assumption the source does not make (for example smoothing so that a bound is finite), say so on screen.

## Rules for narration

- Write for the ear: short sentences, numbers spelled out, one idea per beat.
- About 145 words a minute overall with 0.85 s between beats works for dense material.
- State limits and cautions that the source itself states.

## What the kit gives you

`BeatScene` (narration sync), `Tx`/`M` (text and LaTeX-free math), `Heat` (matrices with numbers), `CodePanel`,
`Plot`, `BarChart`, `Bars`, `Chip`, `ModelBox`, `Cloud`/`Paths`/`Field` (particles and flows), `Tile`/`Flipbook`
(real pixels), `fit`, `spread_cols`, `ladder`. See `unglazed demo` and the `examples/relf/` example.
