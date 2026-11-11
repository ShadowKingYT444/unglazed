"""Depth contract for the technical video on Rectified Language Flow (arXiv 2610.33811v1).

Read on 2026-11-11 from the arXiv HTML. `verified=False` marks items that were not read word for word
(they came from a summary of the appendix), so the narration points to the appendix instead of quoting a formula.
"""

BRIEF = dict(
    title="Flow matching on text, every step: Rectified Language Flow",
    viewer_knows=[
        "diffusion models: forward noising, a denoiser, the ELBO",
        "roughly what flow matching is: a velocity field, straight noise-to-data lines",
        "transformers, softmax, cross entropy; looped (weight-shared) transformers",
    ],
    viewer_can_after=[
        "write the ReLF training step and sampling loop from memory, and say what each line is for",
        "derive the token posterior, the soft token, the singular logits and the guidance target",
        "say what breaks when each part is removed, with the paper's ablation numbers",
        "decide what each part would become in a looped or causal model",
    ],
    skip=["what diffusion is", "image-space intuition", "why generative models exist"],
)

ITEMS = [
    # ---- part 1: the state, the posterior, training, sampling, singular logits
    dict(id="conv", part=1, source="Sec. 2", what="time convention: t = 0 noise, t = 1 data; X_t = t X1 + (1 - t) X0"),
    dict(id="vel", part=1, source="Sec. 2, Eq. 1-2", what="v* = E[X1 - X0 | X_t] = (E[X1 | X_t] - X_t) / (1 - t), derived"),
    dict(id="step", part=1, source="Sec. 2, Eq. 4", what="Euler step moves a fraction h / (1 - t) toward the guess"),
    dict(id="state", part=1, source="Sec. 2", what="tokens -> fixed embedding table E (d = 32) -> X1 in R^(d x L), L = 1024, V = GPT-2 vocab; X0 Gaussian"),
    dict(id="discrete", part=1, source="Sec. 2", what="clean columns are a finite set of points (rows of E)"),
    dict(id="lik", part=1, source="App. A", what="corruption likelihood: X_t | w ~ N(t E(w), (1 - t)^2 I)"),
    dict(id="post", part=1, source="Sec. 3.1, Eq. 6", what="one-position posterior = softmax(log prior - |z - t E(w)|^2 / (2 (1 - t)^2)); limits t -> 0 and t -> 1"),
    dict(id="soft", part=1, source="Sec. 2, Eq. 2", what="guess = sum_w E(w) q_t(w | X_t), the soft token; velocity from it"),
    dict(id="marg", part=1, source="Sec. 2", what="only per-position marginals are needed, although positions are dependent; network output is L x V"),
    dict(id="ce", part=1, source="Sec. 2, Eq. 3", what="loss = E[-log p_theta(w | X_t, t)], token averaged, no time weighting"),
    dict(id="ceopt", part=1, source="App. A.1", what="CE = H(q) + KL(q || p): minimised at the true posterior, so same optimum as the squared-error flow loss"),
    dict(id="cemse", part=1, source="Sec. 4.3, Fig. 6c", what="CE 24.1 vs MSE 25.6 Gen PPL at entropy 5.45"),
    dict(id="sampler", part=1, source="Sec. 2, Eq. 4; App. B.4", what="sampling loop; N evaluations, N - 1 moves; last evaluation decodes by argmax at t < 1; 64 NFE default"),
    dict(id="gap", part=1, source="Sec. 3.1", what="logit gap between two tokens diverges like 1 / (1 - t)^2; a bounded network cannot produce it"),
    dict(id="miss", part=1, source="Sec. 3.1", what="consequence: residual mass on other tokens, the path ends between tokens (shown on the toy with capped logits)"),
    dict(id="split", part=1, source="Sec. 3.1, Eq. 5", what="p_theta = softmax(log r_t + f_theta): singular logits plus a learned residual"),
    dict(id="ref", part=1, source="Sec. 3.1, Lemma 3.2, Eq. 6", what="reference = unigram, factorised, so singular logits are computed per position in closed form; about 1.1% of FLOPs (Small)"),
    dict(id="thm", part=1, source="Thm 3.1 / A.1", what="if 1/kappa <= q1/r1 <= kappa then |f*| <= 2 log kappa for all t < 1; proof by Bayes ratio"),
    dict(id="commit", part=1, source="Sec. 3.1", what="bounded residual forces commitment: model mass on wrong tokens <= e^(2M) x reference mass"),
    dict(id="land", part=1, source="Prop. 3.3 / A.3", what="Z_t is a weighted average of past guesses with weights (1 - t) / (1 - u)^2, so the path ends on a token embedding"),
    dict(id="singabl", part=1, source="Sec. 4.3, Fig. 6a", what="ablation: 57.2 vs 64.2 without guidance; 24.0 vs 36.3 with momentum guidance"),
    # ---- part 2: embedding, schedule, self-conditioning, guidance, SDE, reflow, architecture, results, loops
    dict(id="geom", part=2, source="Sec. 3.2", what="why geometry matters: which tokens are confused at each noise level"),
    dict(id="hel", part=2, source="Sec. 3.2, Eq. 7", what="context distributions, smoothing, H = sqrt(Q), Euclidean distance = sqrt(2) Hellinger"),
    dict(id="svd", part=2, source="Sec. 3.2, App. A.4", what="frequency-weighted centred SVD to d dims; normalise so sum pi E = 0 and sum pi |E|^2 = d (signal 1 per coordinate)"),
    dict(id="dimabl", part=2, source="Table 3, Sec. 4.3", what="d = 16/32/64/128/256 ablation; Hellinger-SVD 42.1 vs random Gaussian 83.6; vs one-hot"),
    dict(id="sched", part=2, source="Sec. 3.2, App. B.1", verified=False, what="training times sampled uniformly in the arc length of token-identification curves"),
    dict(id="selfc", part=2, source="Sec. 3.3, App. A.1", what="self-conditioning: input [z, C], C = previous soft token, C0 = 0; training with a no-grad cold pass and k ~ Bernoulli(1/2)"),
    dict(id="guide", part=2, source="Sec. 3.3, Eq. 8, 16", what="guidance in logit space: l_g = l(0) + omega (l(C) - l(0)); p_g ~ p(0)^(1 - omega) p(C)^omega; why not in velocity space"),
    dict(id="distill", part=2, source="Sec. 3.3, Eq. 9, App. B.3", what="distilled guidance: Delta = k (1 - 1/omega) sg[l_c - l_u]; stationary point derivation; omega ~ log-uniform [1.5, 6]; one pass per step"),
    dict(id="sde", part=2, source="App. B.4, Eq. 17-18", what="stochastic sampler: re-noise by delta = min(sigma h b, b), then the Euler step; sigma = 24 default"),
    dict(id="reflow", part=2, source="Sec. 3.4, Eq. 10-11", what="reflow on (noise, decoded tokens) couplings with the same CE loss; weight interpolation toward theta_0, lambda 0.7 then 0.55"),
    dict(id="fewstep", part=2, source="Table 6, Fig. 5, 7", what="few-step numbers per NFE and size; 8 NFE -40/41/35%; 16 NFE beats same-size AR"),
    dict(id="arch", part=2, source="Sec. 4.1, App. B.2", what="bidirectional diffusion transformer, 138M/421M/784M, time and omega embeddings, 80k steps, batch 1024 x 1024"),
    dict(id="results", part=2, source="Sec. 4.2, Tables 4-6", what="64 NFE: 24.1 / 18.6 / 17.3 vs AR 27.7 / 22.3 / 20.2, real text 17.3; latency 15-19x at batch 1, about 2x at batch 64; caveats"),
    dict(id="loops", part=2, source="this video", what="what each part becomes in a looped or causal model: the sampler is a weight-shared loop with state (Z, C, t)"),
]
