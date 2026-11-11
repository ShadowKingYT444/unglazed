"""Narration: flow matching on text, every step (Rectified Language Flow, arXiv 2610.33811).

Viewer brief and the list of items this video must teach are in coverage.py; each scene names the items it covers.
Convention (the paper's): t = 0 is pure noise, t = 1 is clean data.
Every number spoken here is either from the paper (source noted in coverage.py) or computed in world.py.
"""

TITLE = "Flow matching on text, every step"

CHAPTERS = {
    "s01": "What you will be able to write",
    "s03": "1. The state",
    "s06": "2. Training and sampling",
    "s08": "3. Singular logits",
    "s13": "4. The embedding table",
    "s17": "5. Self-conditioning and guidance",
    "s20": "6. Fewer steps",
    "s22": "7. The model, the results, and looped models",
}

SCENES = [
    # ------------------------------------------------------------------ opening
    dict(id="s01", title="the two loops", covers=[], beats=[
        "This video answers one question. You know diffusion, and you roughly know flow matching. How, exactly, do you run a flow on text?",
        "The answer here is the model from the paper Rectified Language Flow. By the end, you should be able to write its two loops from memory. The training step. And the sampling loop.",
        "Every line has a reason, and we will go through all of them. How text becomes a matrix of numbers. What the network predicts. Why the loss is cross entropy.",
        "Why a formula is added to the logits. How the word vectors are built. How the model feeds its own guess back in, and how guidance is trained into it.",
        "And how reflow takes it from sixty-four steps to sixteen. I will not skip steps. Where there is a formula, we will put numbers into it.",
    ]),
    dict(id="s02", title="the flow in four lines", covers=["conv", "vel", "step"], beats=[
        "First, the flow itself, in four lines, with the paper's conventions. Time runs from zero, pure noise, to one, clean data. A training point is a straight blend of the two.",
        "The network has to learn the average velocity of all the blends that pass through a point. That is the expected value of data minus noise, given the point.",
        "Here is the one piece of algebra that everything else rests on. On the line, the noise is fixed by the point and the data: x zero equals x t, minus t x one, over one minus t.",
        "Substitute that in, and the velocity becomes: the expected clean data, minus where you are, divided by the time left.",
        "So the network never has to output a velocity. It only has to guess the clean data. Call the guess x hat.",
        "And one Euler step of size h moves you a fraction, h over one minus t, of the way to the guess. With numbers: at time one half, a step of one eighth covers one quarter of the remaining distance.",
    ]),
    # ------------------------------------------------------------------ 1. the state
    dict(id="s03", title="text becomes a matrix", covers=["state", "discrete"], beats=[
        "Part one. The state. Text is a list of token ids. The paper uses the G P T two vocabulary, about fifty thousand tokens, and sequences of one thousand twenty-four.",
        "Every token has a fixed vector, its embedding. It is not learned with the model. It is built once, before training, and part four shows how. In the paper it has thirty-two numbers. In our toy, two.",
        "Look up each token, and the sentence becomes a matrix, with one column per position. This matrix is the clean data, x one.",
        "The noise, x zero, is a matrix of the same shape. Every entry is drawn from a standard Gaussian.",
        "The state at time t is their blend. This is the only thing the flow ever moves: thirty-two numbers per position, for all positions at once.",
        "Notice what is unusual. For an image, any pixel value is allowed. Here, every clean column must be exactly one row of the table. The data is a finite set of points.",
    ]),
    dict(id="s04", title="one position: which token made this point", covers=["lik", "post"], beats=[
        "Look at one position on its own. Four tokens, at four locations. If the clean token is cat, where can the noisy point be at time t?",
        "It is t times the embedding of cat, plus one minus t times Gaussian noise. So it lies in a cloud centred at t times E of cat, with radius one minus t.",
        "At time zero, every token has the same cloud: centred at the origin, radius one. As time runs, each cloud slides out toward its own token, and shrinks.",
        "Now go backward. We see a point z, and ask which token made it. Bayes' rule says: the prior of the token, times how likely that token's cloud is to produce z.",
        "For a Gaussian cloud, that likelihood is e to the minus squared distance from z to the cloud's centre, over two times the radius squared. So the posterior is a softmax, with these logits.",
        "Watch the same point as time runs. While the clouds overlap, the posterior stays close to the prior. Once they separate, one token takes almost everything.",
        "Two limits to remember. Near time zero, the point tells you nothing, and the posterior is the prior. Near time one, the nearest token wins outright.",
    ]),
    dict(id="s05", title="the guess is a soft token", covers=["soft", "marg"], beats=[
        "Now the guess. The clean column is one of the table rows. So its expected value is a weighted average of the rows, weighted by the posterior.",
        "This average is called the soft token. It usually lies between tokens, on no word at all. And the velocity is the soft token minus z, over one minus t. That is equation two of the paper.",
        "But positions are not independent. The word at one position depends on the words around it. The true posterior is over whole sentences.",
        "Here is why that is fine. The velocity of a column needs only the expected value of that column. And that expected value needs only that position's own probabilities: the marginals.",
        "So the network reads the whole noisy matrix, in both directions, and outputs one distribution over the vocabulary for each position. L times V numbers. Context changes those numbers, but the network never has to say which combinations go together.",
        "That is the whole interface. A noisy matrix and a time go in. A table of token probabilities comes out. Multiply it by the embedding table, and you have the guess.",
    ]),
    # ------------------------------------------------------------------ 2. training and sampling
    dict(id="s06", title="training with cross entropy", covers=["ce", "ceopt", "cemse"], beats=[
        "Part two. Training. Predicting a token is classification, so the loss is cross entropy. Take a real sentence, embed it, and blend it with noise at a random time.",
        "Ask the network for token probabilities at every position. Take minus the log of the probability it gave to the true token, and average over positions. That is equation three, and it is the entire loss.",
        "Why is this the right loss for a flow? Fix one noisy input. Many clean sentences could have produced it, each with posterior probability q. The expected loss is the cross entropy between q and the model's p.",
        "Cross entropy splits into two terms. The entropy of q, which the model cannot change. And the K L divergence from q to p, which is zero only when p equals q. So the minimum is exactly the true posterior.",
        "At the true posterior, the soft token is the true expected clean data, so the velocity is the true velocity. Cross entropy and the usual squared error have the same optimum. They differ only on the way there.",
        "The paper measures that difference with the same network. Cross entropy reaches a generative perplexity of twenty-four point one. Squared error reaches twenty-five point six, at the same diversity.",
    ]),
    dict(id="s07", title="the plain sampling loop", covers=["sampler"], beats=[
        "Now the sampler, in its plain form. Start from a Gaussian matrix, and choose a grid of times from zero to just below one.",
        "At each time: run the network, get the probabilities, form the soft tokens, and move every column a fraction, h over one minus t, toward its soft token.",
        "Watch it on a toy language of twelve sentences, with a perfect denoiser. Early on, the probabilities are spread over several words, and the state barely knows where to go.",
        "Then a few positions sharpen. The other positions see that through the network, and the sentence locks in.",
        "One detail from the paper. With N network calls there are only N minus one moves. The last call does not move the state. It just picks the most likely token at each position. The state never has to arrive anywhere.",
        "The default is sixty-four calls for one thousand twenty-four tokens. An autoregressive model needs one thousand twenty-three.",
    ]),
    # ------------------------------------------------------------------ 3. singular logits
    dict(id="s08", title="the logit gap blows up", covers=["gap"], beats=[
        "Part three. The paper's first new idea, and the one with a theorem. Look again at the true logits of one position, for two tokens, a and b.",
        "Their difference is the log ratio of the priors, plus a difference of two squared distances, divided by two times one minus t, squared.",
        "The top stays a normal size. But the bottom goes to zero. So as the noise vanishes, the gap between the right token and every other token grows without limit.",
        "Here it is on a toy trajectory. For most of the path the gap is below two. At time point nine nine five, it is in the thousands.",
        "A network with finite weights and an ordinary softmax cannot output that. Whatever its largest logit gap is, call it B, each other token keeps at least a share of e to the minus B.",
    ]),
    dict(id="s09", title="what a bounded network does to the path", covers=["miss"], beats=[
        "What does that do to the flow? I ran the toy sampler with a perfect denoiser, but with its logit gaps capped at six.",
        "At the end, the top token gets about ninety-six percent, not one hundred. So the soft token is ninety-six percent of the right row, plus four percent of the others.",
        "The state moves toward the soft token, so that is where it ends. Near a token, not on it.",
        "The miss is small. But no amount of training removes it, and it sits exactly where the model is supposed to commit. Earlier continuous models patched it afterward, by rounding to the nearest token, or with a separate decoder. This paper removes the cause.",
    ]),
    dict(id="s10", title="split the logits", covers=["split", "ref"], beats=[
        "The idea is to write the true log posterior as a sum of two parts. One part blows up, but can be computed exactly. The other is left for the network.",
        "For the first part, pretend the text came from a much simpler source, called the reference. The paper uses the unigram model: every position independent, each token with its corpus frequency.",
        "Under that reference, the posterior at one position depends only on that position's own noisy column. Every other position cancels in Bayes' rule. So it is exactly the one position formula from part one.",
        "Log prior, minus squared distance over two times one minus t squared, then normalised. These are the singular logits, equation six. They are cheap, because the vectors have only thirty-two numbers: about one percent of the compute of the small model.",
        "The network outputs the rest, a residual f. The model's probabilities are the softmax of the singular logits plus f. That is equation five, and it is this line of the code.",
    ]),
    dict(id="s11", title="the theorem: the residual stays bounded", covers=["thm"], beats=[
        "Why is the residual safe for a network? The theorem says this. Suppose the true probability of every sequence is within a factor kappa of its reference probability. Then the exact residual is at most two log kappa in size, at every time before one, for every input.",
        "The proof takes three lines. By Bayes' rule, the posterior of token w at one position is a fraction. On top: a sum over all sequences that have w at that position, of prior times likelihood. On the bottom: the same sum over all sequences.",
        "Write that fraction for the data, and for the reference. The likelihood terms are identical. Only the priors differ, and each data prior lies between one over kappa and kappa times the reference prior.",
        "A sum of such terms keeps the same bounds. So the ratio of the two tops lies between one over kappa and kappa. So does the ratio of the two bottoms. The ratio of the posteriors therefore lies between one over kappa squared and kappa squared.",
        "Take the log. The residual lies between minus two log kappa and plus two log kappa. And time does not appear anywhere in that bound.",
        "I checked it on the toy language. There the bound is thirty. Over thirty real trajectories the residual never exceeds nineteen, while the singular gap passes three thousand. The explosion is entirely in the part we compute.",
    ]),
    dict(id="s12", title="commitment, and landing on a token", covers=["commit", "land", "singabl"], beats=[
        "Two things follow. First, the model is forced to commit. If the residual is bounded by M, the model's probability on the wrong tokens is at most e to the two M times the reference's probability on the wrong tokens. The reference commits as the noise vanishes, so the model must too.",
        "Second, the state really arrives. Take the flow equation, and divide it by one minus t, squared. The left side becomes the derivative of z over one minus t.",
        "Integrate it. The state at time t is a weighted average of the starting noise and all the past guesses. The weight on the guess made at time u is one minus t, over one minus u squared. Those weights pile up on the most recent guesses.",
        "So if the guesses converge to one row of the table, the state converges to that same row. Every path ends exactly on a token, however well or badly the network is trained. The network only decides which token.",
        "Here is the capped toy again, now with the split. The cap applies only to the residual, and the miss is gone.",
        "On the real model, without guidance, singular logits take the perplexity from sixty-four point two down to fifty-seven point two, at the same diversity. With strong guidance, it is twenty-four against thirty-six.",
    ]),
    # ------------------------------------------------------------------ 4. the embedding table
    dict(id="s13", title="why the geometry matters", covers=["geom"], beats=[
        "Part four. The embedding table. In theory, any table with distinct rows would work. In practice, the table decides how hard the network's job is.",
        "Noise blurs nearby tokens together first. So the geometry decides which tokens get confused with each other at each noise level.",
        "Take a half-noisy point. With a random table, the tokens near it have nothing in common. The point tells the rest of the sentence nothing.",
        "If tokens that are used the same way sit together, the same half-noisy point already says: a noun goes here. That is partial information the other positions can use, long before the exact word is known.",
        "The paper measures it. With a random Gaussian table of the same size, the perplexity is eighty-three point six. With its own table, forty-two point one, at about the same diversity.",
    ]),
    dict(id="s14", title="Hellinger distance between contexts", covers=["hel"], beats=[
        "How do you build such a table without training anything? You count. For every token, count which tokens come right before it and right after it, over the whole corpus.",
        "Normalise the counts, and every token has a context distribution. Rare tokens have noisy counts, so each distribution is smoothed toward the average context.",
        "Now take the square root of every entry. Each row becomes a unit vector, because the squares of its entries add up to one.",
        "Here is why square roots. The squared distance between two rows is exactly twice the squared Hellinger distance between the two context distributions. That is equation seven.",
        "So ordinary straight-line distance between rows now measures how differently two tokens are used. On the toy corpus, cat and dog are point two six apart. Cat and the are one point two apart.",
    ]),
    dict(id="s15", title="down to thirty-two numbers", covers=["svd", "dimabl"], beats=[
        "Each of those rows has about a hundred thousand entries: two for every token in the vocabulary. So the paper keeps only the thirty-two directions that hold the most variance, weighting tokens by how frequent they are. That is a singular value decomposition.",
        "A projection like this keeps close rows close. So the short vectors inherit the geometry of the long ones.",
        "Then one last step, which matters more than it looks. Shift and scale the table so that, averaged over token frequency, the mean is zero and the squared length is d. Every coordinate then carries signal of size one, the same size as the unit Gaussian noise.",
        "Why thirty-two? It is a free choice, and the paper tests it. Sixteen is too cramped: perplexity forty-six. Thirty-two gives twenty-four. Sixty-four gives twenty-five, and needs stronger guidance to get there. At two hundred fifty-six, it is fifty-six.",
        "Every toy picture in this video used this same recipe, run on twelve sentences, with two dimensions instead of thirty-two.",
    ]),
    dict(id="s16", title="which times to train on", covers=["sched"], beats=[
        "One more training detail. Not every noise level is equally useful. Very early, no token can be identified. Very late, every token already is.",
        "The paper measures how identifiable the true token is as a function of time: how much its posterior log probability has gained over the prior. Once using the position alone, and once with local context.",
        "Training times are then drawn evenly along the arc length of those two curves. So most training happens while tokens are in the middle of becoming identifiable. The schedule is computed once from the data. The exact formulas are in appendix B one of the paper.",
    ]),
    # ------------------------------------------------------------------ 5. self-conditioning and guidance
    dict(id="s17", title="self-conditioning", covers=["selfc"], beats=[
        "Part five. Two additions that make the guesses better. First, self-conditioning. At every sampling step, the model already made a guess at the step before. Why throw it away?",
        "So the network gets a second input, C: the previous soft tokens. At each position, the noisy column and the previous guess are stacked, sixty-four numbers, and projected into the transformer. At the first step, C is zero.",
        "At sampling time this is free. The guess is already there. It is the last line of the loop.",
        "Training has to imitate that. First run the network once with C equal to zero, without gradients, and take its soft tokens. Then flip one coin per sequence. Heads, feed that guess in as C. Tails, feed zero.",
        "So one network learns both jobs: guess from scratch, and improve a guess. The cost is one extra forward pass per training step, with no gradient.",
        "Notice the shape of this. The same network is applied again and again, and part of its input is its own previous output. Keep that in mind for the last chapter.",
    ]),
    dict(id="s18", title="guidance in logit space", covers=["guide"], beats=[
        "Second, guidance. The model can make two predictions for the same input. A cold one, with C equal to zero. And a warm one, with its previous guess.",
        "Guidance exaggerates the difference. Start at the cold logits, move toward the warm ones, and keep going, by a factor omega. Omega equal to one is just the warm prediction. A larger omega trades diversity for fluency.",
        "Earlier work did this with velocities. But the velocity is a straight-line function of the token probabilities. So extrapolating velocities means extrapolating probabilities, and that can leave the valid range.",
        "Three tokens. Cold: fifty, thirty, twenty percent. Warm: seventy, twenty, ten. With omega equal to three, the straight-line rule gives one hundred and ten percent, zero, and minus ten percent. That is not a distribution.",
        "In logit space, the same rule multiplies probabilities instead of adding them. Cold to the power one minus omega, times warm to the power omega, renormalised. Here: ninety-two, six, and two percent. Always valid.",
        "And the singular logits are identical in the cold and the warm pass, so they cancel. Guidance only ever touches the learned residual.",
    ]),
    dict(id="s19", title="training guidance into one pass", covers=["distill"], beats=[
        "Applied literally, guidance needs two network calls per step. The paper trains it into one. The network takes omega as an extra input, and learns to output the guided logits directly.",
        "Here is the trick. During training, compute the cold logits and the warm logits, both without gradients. Then form a correction, delta: one minus one over omega, times warm minus cold.",
        "The loss is still cross entropy, but on the network's logits minus delta. For half of the sequences, chosen by the same coin as before, delta is zero.",
        "Why does that work? Cross entropy pushes whatever it is given toward the true log posterior, l star. Here it is given the output minus delta. And at the optimum, the warm logits inside delta are the network's own output.",
        "So: the output, minus one minus one over omega, times output minus cold, equals l star. Solve for the output. It equals cold, plus omega times l star minus cold. That is exactly the guidance rule, with the truth in place of warm.",
        "In training, omega is drawn between one point five and six, so you can choose it freely afterward. The paper samples with one point seven for the small and medium models, and one point nine for the large one. One network call per step.",
    ]),
    # ------------------------------------------------------------------ 6. fewer steps
    dict(id="s20", title="the stochastic sampler", covers=["sde"], beats=[
        "Part six. Fewer steps. First, the sampler the paper actually uses. It is not the plain Euler step. Each step first puts some fresh noise back in.",
        "From the state and the guess, recover the noise that the state currently contains: z, minus t times the guess, over one minus t.",
        "Remove a part of that noise, delta, and add fresh Gaussian noise of exactly the size that was removed. The state stays at the same noise level, but part of its randomness is new.",
        "Then take the usual step toward the same guess. There is no extra network call. Delta is sigma, times the step size, times one minus t, capped so it never removes more noise than there is.",
        "Why add noise? A deterministic path carries every early mistake to the end. Fresh noise lets later steps overwrite them. With sigma equal to zero this is exactly the Euler step. The paper's main results use sigma equal to twenty-four.",
    ]),
    dict(id="s21", title="reflow for text", covers=["reflow", "fewstep"], beats=[
        "Even so, sixty-four steps is a lot. The paths are curved, because the early guesses are blends. Reflow straightens them.",
        "Run the trained model from about half a million noise matrices, with a fine two hundred fifty-six step sampler, and record which sentence each one became.",
        "Then keep training with the same cross entropy loss, but on paired data. The noisy input is built from a recorded sentence and the very noise that produced it. Nothing else changes. Not the loss, not the singular logits, not the network.",
        "Because the pairs come from a flow, their straight lines hardly cross, and the retrained model follows straighter paths.",
        "There is a catch. The pairs are the model's own writing, not real text, so every round drifts away from the data. So after each round the paper blends the weights back toward the original model: seventy percent original after round one, fifty-five percent after round two.",
        "The result. At eight steps, perplexity drops by about forty percent. At sixteen steps the small model reaches twenty-six point four, ahead of the same-size autoregressive model at twenty-seven point seven. But at four steps it is still above one hundred. Sixteen is the practical floor.",
    ]),
    # ------------------------------------------------------------------ 7. the model, the results, looped models
    dict(id="s22", title="the model and the results", covers=["arch", "results"], beats=[
        "Part seven. The network itself is ordinary: a bidirectional transformer of the kind used for image diffusion, with the time fed into its normalisation layers. Three sizes: one hundred thirty-eight, four hundred twenty-one, and seven hundred eighty-four million parameters.",
        "Each one is trained for eighty thousand steps on OpenWebText, about a million tokens per step.",
        "Quality is measured two ways at once. Generative perplexity: how fluent a judge model, G P T two large, finds the samples. And entropy: how varied the words in each sample are. A low perplexity only counts at a normal entropy.",
        "With sixty-four steps the three sizes score twenty-four point one, eighteen point six, and seventeen point three. Real text scores seventeen point three. Autoregressive models of the same sizes, at about the same entropy, score twenty-seven point seven, twenty-two point three, and twenty point two.",
        "Speed, at sixteen steps after reflow, for one thousand twenty-four tokens. Writing one sequence at a time, the flow is fifteen to nineteen times faster. In batches of sixty-four, about two times.",
        "Two cautions, from the paper itself. This is unconditional generation only, and the authors say these two metrics do not settle the comparison. And the entropies are matched only approximately.",
    ]),
    dict(id="s23", title="the two loops, complete", covers=[], beats=[
        "Now read the two loops again. Every line should mean something.",
        "Training. Embed the tokens with the fixed table. Draw noise, and a time from the schedule. Blend. Run a cold pass for the self-conditioning guess, and keep it for half of the sequences. Add the singular logits to the network's residual. Cross entropy, shifted by the guidance correction.",
        "Sampling. Start from noise. At each step: singular logits plus residual, softmax, soft tokens. On the last call, return the most likely tokens. Otherwise refresh some of the noise, step toward the guess, and pass the guess on.",
        "Reflow changes no line. It only changes which noise is paired with which sentence, and it lets N be sixteen.",
    ]),
    dict(id="s24", title="what this becomes in a looped model", covers=["loops"], beats=[
        "Last chapter. This video was made for someone who works on looped models. So here is what carries over, and what has to be decided.",
        "First, look at the sampler as an architecture. One network, one set of weights, applied N times. Between applications it keeps a state: the noisy matrix, the previous soft tokens, and the time. That is already a looped transformer. Its recurrent state is the pair z and C.",
        "So the loop count of a looped model can play the role of the step index. Each loop is one flow step: read the state, output token probabilities, move toward the soft token.",
        "Three things in this paper make that loop well behaved. A target at every iteration: cross entropy at every noise level, with no backpropagation through the loop. A reason to stop: the singular logits force commitment as time approaches one. And fewer iterations: reflow on the model's own pairs.",
        "And three things are open, because the paper does not cover them. Its network is bidirectional, and all positions share one time, so a causal model would need a time per position. The singular logits would still work there, because they are computed one position at a time. And the state here has thirty-two numbers per token, not the hidden width.",
        "Those are design questions, not results. But every piece you need to answer them is now on the table. Thanks for watching.",
    ]),
]
