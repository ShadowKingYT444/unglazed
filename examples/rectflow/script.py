"""Narration: Rectified flow, from scratch: from noise to words.

The teaching plan (see docs/PEDAGOGY.md): one thesis, a ladder of four small worlds that use the same recipe,
and a question for every scene. Convention: t = 0 is pure noise, t = 1 is finished data.
Numbers are either computed in world.py or quoted from the papers listed in coverage.py.
"""

TITLE = "Rectified flow, from scratch: from noise to words"

THESIS = ("A generator is a machine that makes a guess, again and again. Rectified flow trains it so that one guess "
          "is nearly enough. And for text, the guess is a multiple-choice answer.")

LADDER = [
    dict(rung="the two-number world: data is -1 or +1", scenes=["s02", "s03", "s04", "s05", "s06", "s07", "s08", "s09", "s10", "s11", "s12"]),
    dict(rung="one word slot: four words on a plane", scenes=["s13", "s14", "s15", "s16", "s17"]),
    dict(rung="a sentence: six slots, twelve sentences", scenes=["s18", "s19", "s20", "s21"]),
    dict(rung="the real model: 32 numbers per word, 1,024 words", scenes=["s22", "s23"]),
]

CHAPTERS = {
    "s01": "The question",
    "s02": "1. The smallest world",
    "s05": "2. Straight lines and the average",
    "s09": "3. Rectified flow",
    "s13": "4. One word",
    "s18": "5. A sentence",
    "s22": "6. The real model",
    "s24": "What to remember",
}

SAY = {"x hat": "x-hat", "G P T two": "G P T 2"}

SCENES = [
    # ================================================================== the question
    dict(id="s01", title="why one word at a time?", q="Why is text written one word at a time, when a picture is painted all at once?",
         move=["hook"], new=["guess", "rectified flow"], covers=[], beats=[
        "Every language model you have used writes the same way. One word. Then the next. Then the next. A thousand words means a thousand trips through the network.",
        "Image generators do not work like that. They start from static, and improve the whole picture at once, a little at a time. So why can't text be written that way?",
        "It can. A recent paper does it, with a method called rectified flow. Sixteen steps for a thousand words, and the text scores better than a same-size model that writes left to right.",
        "The usual way to explain this starts with differential equations, and you nod along without being able to rebuild any of it. I think that is backwards.",
        "Because underneath, there is one small idea. A generator is a machine that makes a guess, again and again. Rectified flow trains it so that one guess is nearly enough. And for text, the guess is a multiple-choice answer.",
        "We will build that idea four times, in four worlds. First a world with only two numbers in it, where you can do everything by hand. Then one word. Then a sentence. Then the real model.",
    ]),
    # ================================================================== rung 1: the two-number world
    dict(id="s02", title="the smallest world", q="What does it mean to generate, in the smallest world I can think of?",
         move=["question", "predict"], covers=["sampling"], beats=[
        "Chapter one. The smallest world. Generating means pressing a button and getting a new example. A new picture. A new sentence. So let us shrink the problem until we can hold it in one hand.",
        "In this world, the data is a single number, and it is always minus one or plus one. Half the time each. That is the whole data set. Think of it as a language with two words.",
        "What can a computer produce easily? Noise. Numbers from a bell curve. Most of them near zero, a few far out.",
        "So here is the problem, in its smallest form. I hand you a number from the bell curve. You must turn it into minus one or plus one, half the time each. Pause, and decide how you would do it.",
        "You probably said: take the sign. Negative numbers go to minus one, positive numbers go to plus one. That works. But notice what it used. You already knew where the data was.",
        "For pictures or sentences, nobody knows where the data is. We only have examples. So we need a method that learns the way from examples alone. Remember the sign trick, though. It comes back.",
    ]),
    dict(id="s03", title="diffusion, briefly", q="How do diffusion models get from noise to data?",
         move=["build", "verify"], covers=["diffusion"], beats=[
        "The most famous answer is diffusion. It starts by going the wrong way on purpose. Take a real data point, and mix in more and more noise, until nothing of it is left.",
        "Here it is in our world. Time zero on the left is pure noise. Time one on the right is clean data. In between, each point is partly data and partly noise.",
        "Then a network is trained to undo a little of the damage. Show it a noisy number and how noisy it is, and ask what the clean number was.",
        "To generate, start from pure noise and take many small steps. At each step: ask the network, move a little toward its answer, and stir in a little fresh noise.",
        "Watch four hundred points do that, two hundred steps each. They wander, they hesitate, and they settle. Half on plus one, half on minus one.",
        "So it works. But it took two hundred trips through the network, and every path is jittery. Hold on to that cost.",
    ]),
    dict(id="s04", title="the network is a guesser", q="What exactly did that network learn?",
         move=["name", "build", "recap"], covers=["guesser"], beats=[
        "Look closely at what the network was asked. Given a noisy number, what was the clean one? It cannot know. The same noisy number can come from minus one or from plus one.",
        "So the best it can do is the average of the possible answers, weighted by how likely each one is. I will call that the guess. Everything in this video is built on it.",
        "In our world we can write the guess down exactly. It is this curve. Read it like this: along the bottom, where you are. Up the side, what you should guess.",
        "Late, when little noise is left, the curve is a step. Slightly positive means plus one. Slightly negative means minus one. The guess is confident.",
        "Early, when it is almost all noise, the curve is flat. Wherever you stand, the guess is zero. Zero is not a data point. It is the average of minus one and plus one. It means: I do not know yet.",
        "So here is where we are. A generator is a guesser, used over and over. Diffusion uses it with hundreds of noisy steps. Next question: can we use the same guesser with no noise, and far fewer steps?",
    ]),
    # ================================================================== flow matching
    dict(id="s05", title="straight lines", q="What is the simplest way to travel from a noise point to a data point?",
         move=["question", "build"], covers=["line"], beats=[
        "Chapter two. Straight lines and the average. What is the simplest path from a noise point to a data point? A straight line.",
        "Pick a noise number. Pick a data number, at random. At time t, stand a fraction t of the way between them. That is this formula, and it is the only formula for the path we will need.",
        "At time zero you are the noise. At time one you are the data. Halfway, you are the midpoint.",
        "Now do that for thousands of random pairs. At time zero the travelers form the bell curve. At time one they sit on the two data points. In between, the crowd changes shape smoothly.",
        "That looks like exactly the trip we wanted. Noise at one end, data at the other, straight lines between. So are we done?",
    ]),
    dict(id="s06", title="which line am I on?", q="When I am standing at a point, which line am I on?",
         move=["question", "predict", "build", "name"], new=["velocity"], covers=["average"], beats=[
        "Not yet. To walk one of those lines, you must know where it ends. But when we generate, the end is the thing we are trying to find.",
        "Stand at one place, at one time. Say, at zero point three, halfway through. Lines pass through here in both directions. Some are going up to plus one. Some are going down to minus one.",
        "You cannot tell which line you are on. So what would you do? Pause and decide.",
        "The honest answer is: head for the average destination. And we already have a name for that. It is the guess. Here, the guess is about zero point five four, because from this spot, plus one is more likely than minus one.",
        "So the rule is: point at your guess, and move just fast enough to arrive on time. That direction and speed is called the velocity. It is the guess, minus where you are, divided by the time left.",
        "With numbers: the guess is zero point five four, you are at zero point three, and half the time is left. So the velocity is about zero point four seven, upward.",
        "And a step is simple. If you take a step of one eighth while one half of the time is left, you cover one quarter of the distance to your guess. Then you guess again.",
    ]),
    dict(id="s07", title="does the average really work?", q="Averaging two directions sounds like it should land in the middle. Does it actually land on the data?",
         move=["objection", "verify"], covers=["average", "fm_works"], beats=[
        "You should be suspicious now. Half the lines go up, half go down, and we follow the average. That sounds like a recipe for ending up in the middle, on nothing.",
        "So let us run it. Ten thousand noise points. Each one follows its own guess, in two hundred small steps. No randomness along the way.",
        "Here is where they end. Two sharp spikes, at minus one and plus one. Fifty-one percent on top, forty-nine below. Nobody is in the middle.",
        "Why? Because the guess does not stay in the middle. As a point drifts, its guess sharpens, and it is pulled to one side.",
        "And there is something deeper. Freeze both crowds at the same time: the travelers on their straight lines, and the points following the guess. The two crowds have the same shape, at every moment.",
        "Each point takes a different route than its line did. But the crowd as a whole cannot tell the difference. That is a theorem, and we will not prove it here. But you just watched it hold.",
    ]),
    dict(id="s08", title="training: flow matching", q="How does a network learn the guess from examples alone?",
         move=["build", "name", "recap"], new=["flow matching"], covers=["fm_train"], beats=[
        "We computed the guess with a formula, because our world is tiny. A real model has to learn it. How do you learn an average that you never see?",
        "Show the network one random pair. Pick a random time, and put a point on their line. Ask for the guess. Then nudge its answer toward the real end of that line.",
        "The next pair through that spot pulls it toward a different end. And the next. Pulled both ways, the answer settles at the average. That is all regression is.",
        "This training loop is called flow matching. Four lines. No long chains to simulate, and no noise schedule to design.",
        "So compared with diffusion: the same guesser, straight training lines, and a sampler with no randomness in it. Two things are now on the table. The guess. And the rule: step toward it.",
    ]),
    # ================================================================== rectified flow
    dict(id="s09", title="one step lands on the average", q="If the training lines are straight, why do we still need many steps?",
         move=["question", "predict", "break"], covers=["curve"], beats=[
        "Chapter three. Rectified flow. Every training line was straight. So here is a tempting idea. Take one giant step, from time zero all the way to time one. What happens? Decide before I show you.",
        "Every single point lands on zero. Not near zero. Exactly zero. Ten thousand points, all on a number that is not in the data.",
        "And now you can say why. At time zero, the guess is flat. It is zero everywhere. One giant step lands you on your first guess. And the first guess is the average of everything: a blur.",
        "Look at the paths the points really take. They start by drifting toward the middle, and only later bend away to one side. The lines were straight. The paths are curved.",
        "Curved paths need small steps. Two steps: still far off. Four steps: close. Sixteen: fine. That is the price of a blurry first guess.",
    ]),
    dict(id="s10", title="the flow re-pairs noise and data", q="What made the first guess blurry, and has anything changed since?",
         move=["question", "build", "transfer"], covers=["nocross"], beats=[
        "So what made the first guess a blur? The pairing. We joined noise to data at random, so the lines cross everywhere. From any starting point, a line might go up or down.",
        "But look at what the finished flow did. For each noise point, mark where it ended. Every negative number went to minus one. Every positive number went to plus one. Without exception.",
        "The flow untangled the pairs. And it had to. Two points that follow the same rule can never cross, because a crossing would need two different directions at one place.",
        "Do you recognise this pairing? Negative to minus one, positive to plus one. It is the sign trick from the beginning. Nobody told the flow where the data was. It found the trick from examples.",
    ]),
    dict(id="s11", title="reflow", q="What happens if we train again, on the pairs the flow just made?",
         move=["build", "verify", "name"], new=["reflow"], covers=["reflow"], beats=[
        "Here is the move that gives this video its name. Train a second time. Same recipe, same loss. But instead of random pairs, use the pairs the first flow produced.",
        "Draw their lines. They do not cross any more. Through each place, at each time, there is only one line.",
        "So ask the old question again. Standing at a point, which line am I on? Now there is only one answer. The guess is not an average any more. It is exact, from the very first moment.",
        "Which means the path is the line. Straight. And on a straight path, one giant step is enough.",
        "Check it. One step, ten thousand points. Two clean spikes, on minus one and plus one. The same single step that put everything on zero a minute ago.",
        "Training again on your own pairs is called reflow. And a flow whose paths have been straightened this way is a rectified flow.",
    ]),
    dict(id="s12", title="is that cheating?", q="Isn't that cheating, since we needed the slow model to make the pairs?",
         move=["objection", "analogy", "limits", "recap"], covers=["reflow", "reflow_cost"], beats=[
        "Is that cheating? We needed the slow model first, to make the pairs. Yes. Reflow does not replace the first model. It compresses it. You pay for the slow sampler once, offline, and afterwards every sample is cheap.",
        "Here is a picture for it. The first model is a crowd of hikers in fog. Nobody knows which town they will reach, so everyone drifts toward the middle of the map before choosing. Slow, curved trails.",
        "Reflow hands the next crowd a list: who ended up where. With the list, nobody hesitates. They walk straight roads.",
        "Map it back. The fog is not knowing the end of your line. The list is the pairs. The roads are the new straight paths.",
        "And here is where the picture is too kind. The list only records where the hikers ended, and they are not perfect. Their mistakes are copied into the roads. Each round of reflow inherits the errors of the last. Keep that in mind for the real model.",
        "So, the two-number world gave us three things. A generator is a guesser. Flow matching learns the guess from straight lines. And reflow makes the paths themselves straight. Now we climb.",
    ]),
    # ================================================================== rung 2: one word
    dict(id="s13", title="words are points", q="What changes when the data is words?",
         move=["transfer", "question"], new=["embedding"], covers=["words"], beats=[
        "Chapter four. One word. It may seem that numbers and words are different problems. A number can be nudged a little. A word cannot. There is nothing halfway between cat and dog.",
        "But look back at what we just did. Our data was never smooth. It was two isolated points, and the flow had to land exactly on one of them. We have been working with a two-word language the whole time.",
        "So for real words, do the same thing with more points. Give every word a location. A fixed list of numbers, called its embedding. Here, two numbers per word, so we can draw them. The paper uses thirty-two.",
        "Now the recipe is the one you know. Noise is a point somewhere on this plane. Data is one of these four dots. Travel on straight lines. Follow the guess. The only new question is what the guess looks like.",
    ]),
    dict(id="s14", title="the guess is a blend of words", q="What is the guess when the possible answers are words?",
         move=["build", "name", "verify"], new=["soft token"], covers=["post", "soft"], beats=[
        "In the two-number world, the guess was an average of two possible answers. Here it is an average of four. So first we need the weights. Given this noisy point, how likely is each word?",
        "Picture where each word's travelers are right now. If the word is cat, the traveler is somewhere in a cloud. The cloud is centred a fraction t of the way out to cat, and its radius is the noise that is left, one minus t.",
        "At time zero, all four clouds are the same cloud, sitting at the centre. As time runs, each cloud slides toward its own word and shrinks.",
        "So how likely is each word? Its share is how common the word is, times how close our point is to the centre of that word's cloud. That is all of this formula. A softmax over words.",
        "Then the guess is the weighted average of the four word locations. It is called a soft token, because it usually sits between words, on no word at all.",
        "Follow it, and watch the bars. Early on, the clouds overlap and the bars are close to how common each word is. As the clouds separate, one bar takes everything, and the soft token slides onto that word.",
        "And if you start ten thousand points this way, each word receives its fair share. About forty percent land on the common word, and about twenty on each of the others.",
    ]),
    dict(id="s15", title="the network is a classifier", q="So what does the network have to output?",
         move=["name", "transfer"], new=["logit"], covers=["ce"], beats=[
        "So what must the network produce? Not a direction. Not a point. Just those bars. One probability for every word.",
        "That is a classifier. It outputs one score per word, called a logit, and a softmax turns the scores into probabilities. Exactly what an ordinary language model does.",
        "And you train it the ordinary way. Hide a real word in noise. Ask which word it was. Score the answer with cross entropy.",
        "Why is that the right loss? Cross entropy is smallest when the predicted bars equal the true chances. And the true chances are exactly the weights that the guess needs.",
        "The paper tried both losses on the same network. With cross entropy, a score called perplexity comes out at twenty-four point one. With the squared error that flows usually use, twenty-five point six. Lower is better.",
        "So the multiple-choice part of the thesis is literal. For text, a flow model is a classifier that is asked the same question again and again, on a less noisy input each time.",
    ]),
    dict(id="s16", title="landing between words", q="Does the path really end exactly on a word?",
         move=["question", "break"], covers=["land"], beats=[
        "Now a problem that pictures do not have. A picture that is slightly off is still a picture. A word that is slightly off is not a word. The path has to end exactly on a dot.",
        "For that, the last guess must be one hundred percent one word. Look at what that asks of the scores. As the noise shrinks, the gap between the right word's logit and every other one has to grow without limit.",
        "Here is that gap along a real path in our toy. For most of the trip it is below two. Near the end it is in the thousands.",
        "A network cannot output that. Its numbers are finite. So I ran the toy with a perfect classifier whose gaps are capped at six, which is generous.",
        "Its final answer is ninety-six percent one word. So the soft token is ninety-six percent of that word, plus four percent of all the others. The path ends there. Near a word. Not on it.",
    ]),
    dict(id="s17", title="singular logits", q="Where should the missing certainty come from?",
         move=["why", "build", "verify"], new=["singular logits"], covers=["singular"], beats=[
        "Older models patched this at the end, by snapping to the nearest word. The paper asks a better question. Where does that exploding certainty come from in the first place?",
        "From distance. When almost no noise is left, and your point sits next to cat, you do not need a network to tell you it is cat. Closeness alone says so, louder and louder as the noise shrinks.",
        "And closeness is something we can simply compute. It is the same formula as before: how common the word is, and how far the point is from it. No learning involved.",
        "So split the scores in two. One part is that formula. The paper calls it the singular logits. The other part is what the network adds: what the rest of the sentence says about this word.",
        "Here is why that split is safe. The formula carries everything that explodes. What is left for the network is how much more likely a word is in this sentence than in general, and that is an ordinary, finite number.",
        "The paper proves it: the network's part stays below a fixed bound at every moment. On our toy the bound is thirty. Over thirty paths, the network's part never passed nineteen, while the formula's part went past three thousand.",
        "And the same capped classifier, now with the split, lands exactly on its word. The network no longer has to produce certainty. It only has to choose.",
    ]),
    # ================================================================== rung 3: a sentence
    dict(id="s18", title="the other words", q="What about the other words in the sentence?",
         move=["question", "build"], covers=["context"], beats=[
        "Chapter five. A sentence. One word alone is not language. In a sentence, the right word in one slot depends on all the others.",
        "So now the thing we move is a table. One column of numbers for every slot in the sentence. All of it starts as noise, and all of it moves at once.",
        "The network reads the whole noisy table, in both directions, and answers the same multiple-choice question for every slot. One set of bars per slot.",
        "You might worry that this misses something. The slots are not independent. Should the network not say which combinations go together?",
        "It does not have to, and here is the reason. Each column moves toward its own guess. And a slot's guess only needs that slot's own chances. Context changes those chances. But the output stays one set of bars per slot.",
    ]),
    dict(id="s19", title="the whole loop", q="What does the whole loop look like when it runs?",
         move=["verify", "recap"], covers=["loop"], beats=[
        "Let us run the whole loop on a toy language of twelve sentences, with a perfect classifier. Six slots, six columns of noise.",
        "First call. The bars are spread out. Every slot is a mix of several words. Each column takes a small step toward its soft token.",
        "A few calls later, one slot sharpens. Watch the others. The network sees that, and their bars move to agree with it.",
        "By the last call, every slot has chosen, and the choices fit together. Nobody wrote this sentence from left to right.",
        "One detail. The last call does not move anything. It just reads off the most likely word in each slot. Sixteen calls here. The real model uses sixty-four for a thousand words, where writing left to right needs a thousand.",
        "Look at the code. It is the rule from the two-number world, unchanged. Guess. Step a fraction of the way. Guess again.",
    ]),
    dict(id="s20", title="two helpers", q="Can the network use the guess it made a moment ago?",
         move=["question", "build", "why"], new=["self-conditioning", "guidance"], covers=["selfc", "guide"], beats=[
        "The loop throws something away. At every call the network makes a guess, uses it once, and forgets it. The paper keeps it. The previous soft tokens are fed back in as a second input. This is called self-conditioning.",
        "To train that, the network is run once without the extra input, to get a rough guess. Then a coin is flipped. Heads, it sees the rough guess. Tails, it does not. So it learns both to start from nothing and to improve.",
        "That gives two predictions for the same input. A cold one, without help, and a warm one, with it. The second helper, guidance, pushes further in the direction that the help moved things.",
        "Where you do that matters. Push probabilities directly, and you can break them. Cold says fifty, thirty, twenty percent. Warm says seventy, twenty, ten. Push three times as far, and you get one hundred and ten percent, zero, and minus ten.",
        "Push the logits instead, and the same move gives ninety-two, six and two. Always a valid answer. And the paper trains the network to output the pushed logits directly, so the helper costs no extra calls.",
    ]),
    dict(id="s21", title="where words should sit", q="Does it matter where each word sits?",
         move=["question", "break", "build"], covers=["table"], beats=[
        "One thing we have taken for granted: where the words sit. Does it matter? In principle, no. Any table with distinct locations works. In practice, a great deal.",
        "Noise blurs neighbours together first. So take a half-noisy point. With a random table, the words it could be have nothing in common. It tells the rest of the sentence nothing.",
        "If words that are used alike sit together, the same half-noisy point already says something useful: an animal or a place goes here. The other slots can use that long before the exact word is known.",
        "The paper's recipe needs no training. For each word, count which words come right before and right after it. Take square roots of the counts, so that ordinary distance compares how two words are used.",
        "Then keep the thirty-two most important directions, and scale the table so that a word's signal is the same size as the noise. Every toy picture in this video was built with that recipe.",
        "And the difference is large. Same model, random table: perplexity eighty-three point six. The paper's table: forty-two point one.",
    ]),
    # ================================================================== rung 4: the real model
    dict(id="s22", title="reflow on text", q="Does reflow work on text?",
         move=["transfer", "verify", "limits"], covers=["reflow_text"], beats=[
        "Chapter six. The real model. Thirty-two numbers per word, a thousand words. And it still needs sixty-four calls, for the reason you already know: early guesses are blends, so the paths curve.",
        "You also know the cure. Run the model from about half a million noise tables, slowly and carefully, and record which text each one became.",
        "Then train again on those pairs. Same loss. Same network. Nothing else changes.",
        "Remember the hikers' mistakes. The pairs are the model's own writing, not real text. So after each round, the paper mixes the new weights part of the way back toward the original model. Seventy percent original after the first round.",
        "The result. With sixteen calls instead of sixty-four, the perplexity is twenty-six point four. A left-to-right model of the same size scores twenty-seven point seven, using a thousand calls.",
        "It is not free. At four calls the score is above one hundred. The paths are straighter, not straight. Sixteen is the practical floor in this paper.",
    ]),
    dict(id="s23", title="how good is it?", q="How good is it, and how sure are we?",
         move=["verify", "limits"], covers=["results"], beats=[
        "How good is it? The paper measures two things together. Perplexity, from a separate judge model: how fluent it finds the text. And entropy: how varied the words are. A model that repeats itself is fluent and useless.",
        "With sixty-four calls, three model sizes score twenty-four point one, eighteen point six, and seventeen point three. Real text scores seventeen point three.",
        "Left-to-right models of the same sizes, at about the same variety, score twenty-seven point seven, twenty-two point three, and twenty point two.",
        "And speed. After reflow, at sixteen calls, writing one text at a time is fifteen to nineteen times faster. In batches of sixty-four, about two times.",
        "Now the cautions, which are the paper's own. This is free writing only, with no prompts to follow. The authors say these two scores do not settle the comparison. And the variety is matched only approximately.",
    ]),
    # ================================================================== what to remember
    dict(id="s24", title="what to remember", q="What should I remember from all this?",
         move=["recap", "transfer"], covers=[], beats=[
        "Let us collect it. We built one idea four times.",
        "In the two-number world: a generator is a guesser. Follow the guess, and noise becomes data. The first guess is a blur, so the paths curve. Train again on your own pairs, and they straighten.",
        "With one word: the guess is a blend of word locations, and the network is a classifier. A formula for closeness makes every path land exactly on a word.",
        "In a sentence: one set of bars per slot, the whole table moving at once, with the previous guess fed back in.",
        "And here is the whole method as code. A training step, and a sampling loop. Every line is something you have now seen happen.",
        "Notice the shape of that loop. One network, applied again and again, each time fed its own last answer. If you work on models that reuse their layers in a loop, that shape should look familiar.",
        "A generator is a machine that makes a guess, again and again. Rectified flow trains it so that one guess is nearly enough. And for text, the guess is a multiple-choice answer. Thanks for watching.",
    ]),
]
