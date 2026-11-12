---
name: unglazed-voice
description: Step 3 of an unglazed video. Generate natural local narration (Pocket TTS on the CPU, or Kokoro), clone a voice from a short recording, fix mispronounced or garbled sentences, and produce the timings scenes sync to. Use when narration sounds robotic, mangles the start of sentences, mispronounces a term, or when choosing a voice.
---

# Narration

```bash
unglazed voice <video> --estimate                                   # no voice: timings from word counts
unglazed voice <video> --engine pocket --voice ref.wav --verify     # cloned voice, with listen-back
unglazed voice <video> --engine kokoro --voice af_heart             # fast, fixed voices
```

Each beat is spoken sentence by sentence and joined with pauses (0.32 s between sentences, 0.85 s between beats).
Sentence audio is cached, so editing one sentence re-records only that one. Scenes read `build/<video>/timings.json`.

## Engines

| | Pocket TTS | Kokoro |
|---|---|---|
| Runs on | CPU, about 2 times real time on 4 threads | CPU or GPU, much faster than real time |
| Intonation | follows the sentence; the more natural of the two | even, can sound read-out |
| Voices | cloned from a 10 to 25 second recording | built-in voices or a voice pack `.pt` |
| Install | `pip install pocket-tts`, or an ONNX export via `UNGLAZED_POCKET_DIR` | `unglazed[voice]` |

`UNGLAZED_TTS_PYTHON` runs the engine in another Python environment; `UNGLAZED_ASR_PYTHON` does the same for
listen-back (it needs `faster-whisper`).

## The reference recording decides the quality

The model continues from the end of the reference. Three rules, found the hard way:

1. **It must end at the end of a sentence, in a pause.** If the clip stops mid-phrase, the first word of every
   generated sentence comes out mangled or clipped ("Map it back" becomes "clap it back"). unglazed cuts a long
   clip at its longest pause and appends silence, but it cannot tell a comma from a full stop: cut the clip yourself.
2. **10 to 25 seconds.** Much longer and the model may stop after a second of speech.
3. **Continuous explanatory speech** in the tone you want, without music, in the language of the script.

## Listen-back (`--verify`)

Every sentence is transcribed (faster-whisper) and compared with its text. A sentence with a wrong word or an
unclear word is re-recorded with another seed, up to three times, and the best take is kept. What still differs is
written to `build/<video>/voice_report.json`. Read it:

- A spelling variant (`centred` / `centered`) or a term you respelled on purpose is fine.
- A real word heard wrong, every time: add a respelling to `SAY` in `script.py` (`"logit": "lowjit"`), or reword.
- Very short sentences are where a voice model stumbles; sentences under four words are spoken together with a
  neighbour automatically. Prefer rewording to fighting the model.

The check hears words, not tone. Listen to at least the first minute and one dense passage yourself, or say in your
report that nobody has.

## Writing for the voice

Numbers spelled out ("zero point five four"), symbols by name, no parentheses, no lists of three abbreviations.
Keep one name for each thing. If a sentence is hard to say aloud, it is hard to hear.
