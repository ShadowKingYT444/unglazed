"""Narration. One scene per idea, one beat per sentence group. Write for the ear: short sentences, numbers spelled out.

Each scene has q (the question it answers), move (its teaching moves), new (terms it introduces) and covers
(the coverage items it teaches). In the scene file, self.at(i) waits for beat i.
"""

TITLE = "Straight-line interpolation, every step"

# The one sentence the whole video proves (see docs/PEDAGOGY.md).
THESIS = "A straight blend of noise and data is all a flow needs: one step covers the fraction h over one minus t of what is left."

# Small cases first, the same recipe each time. A real video has at least two rungs.
LADDER = [dict(rung="one number", scenes=["s01"])]

CHAPTERS = {"s01": "The blend"}   # scene id -> YouTube chapter title

SCENES = [
    dict(id="s01", title="the blend and the step", q="How far does one step take me?", move=["build", "name", "recap"],
         new=["blend"], covers=["interp", "step"], beats=[
        "A training point is a straight blend of noise and data. At time zero it is the noise. At time one it is the data.",
        "Halfway, at time one half, it is the midpoint.",
        "Now take a step of one eighth toward the data. The time left is one half, so the step covers one quarter of the remaining distance.",
    ]),
]
