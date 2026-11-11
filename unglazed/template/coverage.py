"""The depth contract for this video. Write it BEFORE the script, from the source itself.

`unglazed check <video>` fails while any item below has no scene.
"""

BRIEF = dict(
    title="Straight-line interpolation, every step",
    viewer_knows=["what a vector is", "what a Gaussian is"],
    viewer_can_after=["write x_t for any t", "say why one Euler step covers h / (1 - t) of the way to the guess"],
    skip=["why generative models exist"],
)

# One entry per mechanism, equation or number the video must teach.
#   source:   where it is in the paper (section, equation, table), so every claim can be traced
#   verified: False if you could not read it word for word (then the narration must point to the source)
#   part:     for a video delivered in parts
ITEMS = [
    dict(id="interp", source="Sec. 2", what="x_t = t x1 + (1 - t) x0, with t = 0 noise and t = 1 data"),
    dict(id="step", source="Sec. 2, Eq. 4", what="an Euler step of size h moves a fraction h / (1 - t) toward the guess"),
]
