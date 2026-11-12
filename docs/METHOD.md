# How to make a technical explainer that does not skip steps

This is the method the kit enforces. It exists because the first video made with the kit looked good and taught
little: it copied a reference video's pictures and cut the content to match its pace.

## The order of work

| Step | File | What it fixes |
|---|---|---|
| 1. Brief | `<video>/coverage.py` → `BRIEF` | Who watches, what they already know, what they must be able to DO afterwards, what to skip |
| 2. Coverage list | `<video>/coverage.py` → `ITEMS` | Every mechanism, equation and number from the source, each with its section or table. Read the source itself |
| 3. World | `<video>/world.py` | A small world where the source's own formulas can be computed exactly, so pictures and numbers are real |
| 4. Script | `<video>/script.py` | A thesis, a ladder of small worlds, and scenes that each answer a question with named teaching moves ([PEDAGOGY.md](PEDAGOGY.md)) |
| 5. Check | `unglazed check <video>` | Fails if an item has no scene, a term is used before it is introduced, a scene has no question, or a component is never broken or verified |
| 6. Voice | `unglazed voice <video> --verify` | Narration sentence by sentence, transcribed back and retaken where it came out wrong ([VOICE.md](VOICE.md)) |
| 7. Scenes | `<video>/scenes/p*.py` | Draft at 480p, read the layout check, look at a frame per beat (`unglazed sheet`), fix, then render 1080p |
| 8. Assemble | `unglazed build <video>` | Joins clips and narration without re-encoding the picture, writes chapters |

Length is an output of step 2, not an input. A short video comes from a short coverage list, never from cutting.

## The shape of a scene

1. **The question.** What does the viewer want to know right now? Often: ask them to predict before you show.
2. **The object.** Show the thing the idea is about, on the recurring picture: the lines, the cloud, the table.
3. **Numbers.** Do one instance by hand, with values from the world. A viewer who sees `0.96 E(the) + 0.04 (others)` believes the formula.
4. **The name and the equation**, only now, on the object.
5. **What breaks without it.** Run the world with the part removed, or show the source's ablation.

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
- About 135 to 150 words a minute overall with 0.85 s between beats works for dense material.
- State limits and cautions that the source itself states.

## What the kit gives you

`BeatScene` (narration sync), `Tx`/`M` (text and LaTeX-free math), `Heat` (matrices with numbers), `CodePanel`,
`Plot`, `BarChart`, `Bars`, `Chip`, `ModelBox`, `Cloud`/`Paths`/`Field` (particles and flows), `Tile`/`Flipbook`
(real pixels), `Stage`/`place`/`focus` (placement), `fit`, `spread_cols`, `ladder`. See `unglazed demo` and `examples/rectflow/`.
