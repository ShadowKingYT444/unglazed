"""Depth and teaching contract for "Rectified flow, from scratch: from noise to words".

Sources: Rectified Flow (Liu, Gong, Liu, arXiv 2209.03003), Flow Matching (Lipman et al., arXiv 2210.02747) and
Rectified Language Flow (Su, Liao, Chen, Liu, arXiv 2610.33811, version 1, read from the arXiv HTML).
`verified=False` marks numbers that came from a summary of the appendix rather than from text read word for word.
"""

BRIEF = dict(
    title="Rectified flow, from scratch: from noise to words",
    viewer_knows=[
        "what a neural network is and that it is trained by gradient descent",
        "what a probability distribution and a bell curve are",
        "softmax and cross entropy as the usual way to train a classifier",
        "that diffusion models make images from noise (no details needed)",
    ],
    viewer_can_after=[
        "rebuild flow matching on paper for a tiny data set, and compute a guess and a step by hand",
        "explain why generated paths curve, why one step lands on the average, and how reflow fixes it",
        "write the training step and the sampling loop of a flow on text, and say what each line is for",
        "say what breaks without singular logits, without a structured embedding table, and without reflow",
    ],
    skip=["the continuity equation and the proof that the marginals match", "score matching", "the ELBO"],
)

# Every term the video introduces, in plain words. A term may not be spoken before the scene that lists it in new=[...].
GLOSSARY = {
    "guess": "the model's prediction of the finished thing, made from the unfinished one",
    "flow matching": "learning the guess by regression on straight lines between random noise and data pairs",
    "velocity": "which way a point should move right now, and how fast",
    "reflow": "training again on the pairs the first flow produced",
    "rectified flow": "a flow whose paths are (nearly) straight, so a few big steps are enough",
    "embedding": "a fixed list of numbers that gives a word a location",
    "soft token": "the probability-weighted average of word locations",
    "logit": "a word's score before the softmax turns scores into probabilities",
    "singular logits": "the part of the scores that comes from distance alone, written as a formula",
    "self-conditioning": "feeding the model's previous guess back in as an extra input",
    "guidance": "pushing the prediction further in the direction that the extra input moved it",
}

ITEMS = [
    # ---- rung 1: the two-number world
    dict(id="sampling", source="background", what="generating = drawing a new sample; easy for a bell curve, hard for data"),
    dict(id="diffusion", source="background", what="diffusion in brief: noise is added gradually; a network learns to guess the clean value; sampling takes many small noisy steps"),
    dict(id="guesser", source="RF Sec. 2; ReLF Eq. 2", what="the network's job is the guess E[x1 | x_t]; in the two-number world it is tanh(t x / (1 - t)^2)"),
    dict(id="line", source="ReLF Sec. 2", what="x_t = t x1 + (1 - t) x0 with t = 0 noise and t = 1 data; random pairs; the crowd is the bell at 0 and the data at 1"),
    dict(id="average", source="ReLF Eq. 1-2", kind="component", what="lines cross, so follow the average: velocity = (guess - x) / (1 - t); a step moves h / (1 - t) of the way"),
    dict(id="fm_works", source="RF Thm 3.3 (marginals)", what="following the guess moves the noise crowd exactly onto the data (checked with 10,000 samples)"),
    dict(id="fm_train", source="FM Eq. 23; RF Eq. 1", what="training by regression on one random pair, one time, one point: flow matching"),
    dict(id="curve", source="RF Sec. 2.2", kind="component", what="generated paths curve; one step lands on the average; steps needed: 1, 2, 4, 16"),
    dict(id="nocross", source="RF Sec. 3.1", what="paths of a flow never cross, so the flow re-pairs noise and data (in one dimension: it sorts them)"),
    dict(id="reflow", source="RF Sec. 2.1, 3.2", kind="component", what="reflow: retrain on the flow's own pairs; lines do not cross, the guess is exact, one step lands on data"),
    dict(id="reflow_cost", source="RF Sec. 2.1; ReLF Sec. 3.4", what="reflow needs the slow model first and inherits its errors"),
    # ---- rung 2: one word slot
    dict(id="words", source="ReLF Sec. 2", what="words get fixed locations (embeddings); the data is a finite set of points; the two-number world was already a two-word language"),
    dict(id="post", source="ReLF Eq. 6", what="which word made this point: prior times closeness, a softmax of log prior - |z - t E(w)|^2 / (2 (1 - t)^2)"),
    dict(id="soft", source="ReLF Eq. 2", what="the guess is the soft token sum_w E(w) q(w); same velocity formula"),
    dict(id="ce", source="ReLF Eq. 3, Sec. 4.3", what="the network is a classifier trained with cross entropy; CE 24.1 vs squared error 25.6"),
    dict(id="land", source="ReLF Sec. 3.1", kind="component", what="the path must end exactly on a word; a bounded classifier leaves mass on other words and ends between words"),
    dict(id="singular", source="ReLF Eq. 5-6, Thm 3.1, Prop. 3.3", kind="component", what="singular logits: the distance part as a formula plus a bounded learned residual; every path lands on a word"),
    # ---- rung 3: a sentence
    dict(id="context", source="ReLF Sec. 2", what="the network reads the whole noisy row, both directions, and outputs one distribution per slot (L x V numbers)"),
    dict(id="loop", source="ReLF Eq. 4, App. B.4", what="the sampling loop: N calls, N - 1 moves, the last call picks the most likely words; 64 calls for 1,024 tokens"),
    dict(id="selfc", source="ReLF Sec. 3.3", what="self-conditioning: the previous soft tokens are an extra input; trained with a cold pass and a coin"),
    dict(id="guide", source="ReLF Eq. 8-9, 16", what="guidance in logit space, why not in probability space, and that it is trained into one pass"),
    dict(id="table", source="ReLF Sec. 3.2, Table 3", kind="component", what="the embedding table: words used alike sit together (context counts, square roots, SVD to 32, signal scaled to the noise); 42.1 vs 83.6"),
    # ---- rung 4: the real model
    dict(id="reflow_text", source="ReLF Sec. 3.4, Eq. 10-11, Table 6", verified=False, what="reflow on (noise, text) pairs with the same loss; weights blended back toward the original; 16 steps: 26.4; 4 steps: 116"),
    dict(id="results", source="ReLF Sec. 4.2, Tables 4-6", what="64 steps: 24.1 / 18.6 / 17.3 vs autoregressive 27.7 / 22.3 / 20.2; real text 17.3; 15 to 19 times faster at batch 1, about 2 times at batch 64; cautions"),
]
