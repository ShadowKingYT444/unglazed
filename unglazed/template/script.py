"""Narration. One scene per idea, one beat per sentence group. Write for the ear: short sentences, numbers spelled out.

Each scene lists the coverage items it teaches (`covers`). In the scene file, self.at(i) waits for beat i.
"""

TITLE = "Straight-line interpolation, every step"

CHAPTERS = {"s01": "The blend"}   # scene id -> YouTube chapter title

SCENES = [
    dict(id="s01", title="the blend and the step", covers=["interp", "step"], beats=[
        "A training point is a straight blend of noise and data. At time zero it is the noise. At time one it is the data.",
        "Halfway, at time one half, it is the midpoint.",
        "Now take a step of one eighth toward the data. The time left is one half, so the step covers one quarter of the remaining distance.",
    ]),
]
