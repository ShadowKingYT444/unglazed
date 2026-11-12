---
name: unglazed-teach
description: Step 2 of an unglazed video. Turn a coverage list into a script that people remember - one thesis, a ladder of small worlds, a question for every scene, need before name, predict then reveal, break and verify each component. Use when writing or reviewing script.py, or whenever an explanation is correct but does not stick.
---

# Teaching: the script

Full policy with reasons: `docs/PEDAGOGY.md`. `unglazed check <video>` enforces the parts marked (checked).

## What to write, in this order

1. `THESIS` (checked): the one sentence the whole video proves. State it in the hook, pay it off in the middle,
   repeat it at the end. If it does not fit in one breath it is not one idea yet.
2. `LADDER` (checked): rungs from the smallest world to the real system. Teach the whole recipe on the first rung,
   by hand. Each later rung changes one thing and says so: "the same recipe, with more points".
3. The **questions**: for every scene, `q="..."`, the question the viewer has at that moment, usually raised by the
   scene before (checked). Write all the questions before any narration. They are the outline. A scene whose
   question you cannot phrase has no reason to exist yet.
4. The beats, written for the ear.

```python
dict(id="s06", q="When I am standing at a point, which line am I on?",
     move=["question", "predict", "build", "name"], new=["velocity"], covers=["average"],
     beats=["...", "..."])
```

## The moves (`move=[...]`, checked)

| Move | What it is |
|---|---|
| `hook` | the viewer's own question, and what is unsatisfying about the usual answer |
| `question` | pose the problem the next idea solves; make something familiar strange |
| `predict` | ask the viewer to commit to a guess before the reveal ("pause, and decide") |
| `build` | construct the idea on a small concrete case, in the picture |
| `name` | only now give the formal name or the equation for what was built |
| `why` | why this exact form: show the simpler form failing |
| `break` | remove the part and show what goes wrong |
| `verify` | check the claim by experiment on the world, and say where the check is imperfect |
| `objection` | say the viewer's doubt out loud, then answer it |
| `analogy` | a second view AFTER the mechanism, mapped back part by part, with where it stops working |
| `recap` | what we have, in the viewer's words, and what is still open |
| `transfer` | connect to something the viewer already trusts, or reuse the recipe on a new case |
| `limits` | what was simplified, deferred, or is unknown |

## Rules

- **Need before name** (checked). A term from `GLOSSARY` may not be spoken before the scene that lists it in
  `new=[...]`, and that scene must first make the viewer want the thing. Name it after they have seen it work.
- **At most two new terms per scene** (checked). Reuse the viewer's own word for a thing ("the guess") for the
  whole video; do not rotate synonyms.
- **Every component earns its place** (checked): each `kind="component"` item is covered by a scene with `break`
  or `verify`. "The paper adds X" is not an explanation. "Without X, this happens" is.
- **Numbers the viewer can redo.** Do one instance by hand with small numbers before any general formula.
- **Analogies come second**, and are mapped back ("the fog is not knowing where your line ends"), including where
  the picture is too kind.
- **Recap at least every six scenes** (checked as a warning), and before every rung change.
- **Say the limits**: what you skipped (`BRIEF.skip`), what the toy assumes, what the paper itself cautions.
- **For the ear**: sentences under about 36 words, beats under about 85 (checked as warnings), numbers spelled
  out, one idea per beat, about 135 to 150 words a minute overall. Read each beat aloud once.

## Self-review before scenes

Read only the list of questions, top to bottom. Does each follow from the last? Could a viewer who paused at any
`predict` actually answer from what they have seen? Is there a scene that only recites the paper? Rewrite those.
