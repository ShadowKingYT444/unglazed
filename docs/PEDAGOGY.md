# The teaching policy

A video can cover everything and still teach nothing. This policy is what `unglazed check` enforces on a script,
and what the agent skill follows. It comes from taking apart explanations that stick (the reference is the
Depth First diffusion series), and each rule has a reason.

## The one-sentence test

Before any scene: write `THESIS`, the single sentence the whole video proves. State it in the opening, pay it off in
the middle, and repeat it at the end. If it does not fit in one breath, it is not one idea yet.

> Example: "A generator is a guesser that you ask again and again. Rectified flow trains the guesser so that asking
> once is nearly enough. For text, the guess is a multiple-choice answer."

## The ladder

Do not explain the real system first. Find the **smallest world in which the whole idea already happens** and can be
computed by hand, teach the recipe there, then climb: the same recipe, one change per rung.

> Two numbers (-1 and +1) → one word slot with four words → a six-word sentence → the real model.

The viewer should recognise the recipe at each rung ("you should be getting the hang of this by now"). Declare the
rungs in `LADDER`. The last rung is the paper.

## Every scene answers a question

Each scene has a `q`: the question the viewer has at that moment, usually raised by the scene before. Write the
questions first; they are the outline. If you cannot phrase the question, the scene has no reason to exist yet.

## The moves

Each scene declares one or more moves. They are the vocabulary of the policy:

| Move | What it does | Why it works |
|---|---|---|
| `hook` | Starts from the viewer's own question and says what is unsatisfying about the usual answer | Motivation before content: "why should I care" comes first |
| `question` | Poses the problem the next idea solves; makes something familiar strange ("how does a computer actually roll a die?") | A gap the viewer wants closed |
| `predict` | Asks the viewer to commit to a guess before the reveal | A wrong guess that gets corrected is remembered |
| `build` | Constructs the idea on a small concrete case, in the picture | Concrete before abstract |
| `name` | Only now gives the formal name and the equation | Need before name: a term is a label for something already understood |
| `why` | Shows why the idea has this exact form by letting the simpler form fail ("why the logarithm?") | Kills the feeling that the form was arbitrary |
| `break` | Removes a part and shows what goes wrong | A part is understood when you know what it prevents |
| `verify` | Checks the claim by experiment (10,000 samples, a histogram) and admits where it is imperfect | Trust, and honesty about approximations |
| `objection` | Says the viewer's doubt out loud ("isn't that cheating?") and answers it | The viewer stops arguing and listens |
| `analogy` | A second view **after** the mechanism, mapped back part by part, with where it stops working | An analogy before the mechanism replaces understanding; after, it anchors it |
| `recap` | What we have, in plain words, and what is still open | Consolidation every few ideas |
| `transfer` | Connects to something the viewer already trusts, or applies the recipe to a new case | Makes the idea feel inevitable, not foreign |
| `limits` | What was simplified, deferred, or is unknown | Honest scope |

## Rules the check enforces

| Rule | Check |
|---|---|
| One thesis | `THESIS` exists and has at most 45 words |
| A question per scene | every scene has `q` ending in "?" |
| A move per scene | every scene has `move=[...]` from the table |
| Need before name | every term in `GLOSSARY` is first spoken in, or after, the scene that lists it in `new` |
| Plain words | every `new` term has a plain-words entry in `GLOSSARY` |
| One or two new things at a time | at most 2 `new` terms per scene |
| Necessity is shown | every coverage item with `kind="component"` is covered by a `break` or `verify` scene |

Warnings: no ladder, more than 6 scenes without a recap, no `predict`, `objection`, `verify` or `limits` anywhere,
an analogy before its mechanism, sentences over 36 words, a first scene without a hook.

## Rules the check cannot enforce (the agent must)

1. **Start where the viewer is.** Open the first rung with something they can already do.
2. **Say the confusing part out loud.** If you found a step surprising or hard, say so. It tells the viewer their
   confusion is normal and where to pay attention.
3. **One change at a time on screen**, with one red box that says where to look.
4. **Numbers, then symbols.** Put values through the formula before generalising it.
5. **Say it twice, differently.** After the precise statement, restate it in everyday words.
6. **Never skip the step that made you think.** Skip only what the brief says the viewer knows.
7. **End each chapter by telling the viewer what they can now do.**

## Writing order

1. Brief → thesis → ladder.
2. The list of questions, in order (this is the outline).
3. Coverage items, attached to the questions.
4. The world: the smallest case computed exactly.
5. Narration, beat by beat, for the ear.
6. `unglazed check`.
