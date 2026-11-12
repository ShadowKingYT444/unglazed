# The visual-first explainer style

**Read METHOD.md first.** This file is only about the look and the pace. A video that follows this file and not
the method will look good and teach little: the first video made with this kit did exactly that. The rule
"a formula appears once" below describes the reference, not a limit for technical videos.

Reference: "The Breakthrough Behind Modern AI Image Generators | Diffusion Models Part 1" (Depth First), 24 min.
These rules come from measuring that video (frames every 6 s, a transcript, and the pauses between sentences).

## What the reference does

| Property | Measured in the reference | Rule for our videos |
|---|---|---|
| Canvas | Pure black, nothing decorative | `BG = #000000`, no slide titles, no progress bars |
| Objects | Real images, noise, points in a box, arrow fields, density maps | Every object on screen comes from a real computation (`unglazed.sims`) or a real image |
| Text | 0 to 6 words on screen at a time, lowercase serif | Labels only. A sentence on screen is a sign that the picture is missing |
| Math | About 3 formulas in 24 minutes | A formula appears once, after its picture, and stays under 1 line |
| Continuity | The same "image space" box stays for minutes | Build one world per chapter and keep changing it. Do not cut to a new layout for each sentence |
| Narration | 134 words a minute overall, 170 while speaking, 21% silence | `unglazed voice`: 0.85 s between beats, so the picture has time to move |
| Beats | One idea per 5 to 15 seconds | One beat = one sentence group = one change on screen |
| Chapters | 5 chapters, each opens with a Roman numeral card | `self.chapter("ii", "learning the arrows")` |
| Analogies | 1 or 2 per chapter (the blindfolded hill climber) | Give each hard idea one physical analogy, and draw it with the same objects |

## Two ways to fail

Equations on slides: the narration carries the idea and the screen only records it.
Pictures without depth: the screen is pleasant and the viewer cannot do anything new afterwards.
The target is in between: the screen carries the idea, and the idea is complete.

## Scene design checklist

1. Write the beat as one spoken sentence group. Then ask: what does the viewer SEE change during this sentence?
   If the answer is "a formula appears", find the picture first.
2. Compute the picture. The exact flow for a finite data set has a closed form (`sims.posterior`, `sims.guess`,
   `sims.velocity`, `sims.integrate`), so clouds, arrows, guesses and paths are the true ones, not sketches.
3. Use colour with one meaning for the whole video: violet = noise, mint = data, yellow = motion (the step, the arrow),
   blue = the model's guess, red = a problem.
4. Show the failure before the fix (one hop lands on the average; the path ends between words).
5. Check each beat on a contact sheet (`unglazed sheet`) before the 1080p render.

## Kit rules that save time

- Anything that follows the clock (`Cloud.follow`, `Paths(tracker=...)`, `Field`, `Flipbook`) owns its own points.
  Call `clear_updaters()` before you fade or transform it, and fade a `Flipbook` with `appear()` / `vanish()`.
- To move a whole live picture, move the camera (`self.frame.animate`), not the objects.
- `segments()` draws thousands of lines as one object. Use `growing_segments()` when all lines must grow together.
- Time a beat with fractions of `self.dur(i)` and `self.left(i + 1)`, never with fixed seconds, so a narration edit
  does not break the scene.

## Placement

Compose every scene from the named zones in `Stage` (`title`, `main`, `left` / `right`, `left_wide` /
`right_narrow`, `top` / `bottom`, `foot`) with `place(mob, zone)`.

- **One picture per rung.** Pick the picture for a part of the video and keep it: same axes, same place, same
  colours. New ideas are drawn onto it. In the demo, eleven scenes share one time-against-value picture.
- **One large object, or two balanced columns**: the picture on one side, the algebra, bars or code on the other.
- **A label sits next to its object**, outside the lines that cross it. 0.3 is the smallest comfortable text size.
- **When something appears, something dims or leaves.** About five lit labels at once is the limit.
- **Empty space is fine.** A sparse frame with one large object reads better than a full frame of small ones.

`BeatScene` checks every finished beat and prints `LAYOUT` lines for text that runs off the frame, overlaps other
text, or is too small to read at 1080p. The check cannot see a label lying on a curve or a picture that is too
small, so `unglazed sheet` and your eyes are still part of the method.
