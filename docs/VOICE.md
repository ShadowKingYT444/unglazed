# Narration that sounds like a person

`unglazed voice` speaks each beat sentence by sentence, joins the sentences with pauses, and writes the timings the
scenes sync to. Two local engines, no API key.

| | Pocket TTS (`--engine pocket`) | Kokoro (`--engine kokoro`) |
|---|---|---|
| Runs on | CPU, about 2 times real time on 4 threads | CPU or GPU, far faster than real time |
| Intonation | follows the sentence | even; can sound read-out on long explanations |
| Voices | built-in names, or cloned from a 10 to 25 second recording | built-in voices, or a voice pack `.pt` |
| Install | `pip install "unglazed[pocket]"` | `pip install "unglazed[voice]"` |

Cloning with the pip package needs the gated weights: accept the terms at
<https://huggingface.co/kyutai/pocket-tts> and run `uvx hf auth login`. Built-in voices (`--voice alba`) need nothing.
A local ONNX export also works: set `UNGLAZED_POCKET_DIR` to the folder that holds `pocket_tts_onnx.py`.

## Three things that made the demo's voice clean

1. **The reference clip ends at the end of a sentence.** The model continues from the end of the reference. Our
   first clip was cut at 24 seconds, mid-phrase, and the first word of nearly every sentence came out mangled
   ("Map it back" was heard as "clap it back", "Flow matching" as "Slow matching"). A clip that ends in a pause
   after a full stop fixed it: on the 16 hardest sentences, wrong words fell from 13 to 8, and none were left at
   sentence starts except in three-word sentences. `unglazed` now cuts a long clip at its longest pause and
   appends silence, but it cannot tell a comma from a full stop, so cut the clip yourself when you can.
2. **Short sentences are spoken with a neighbour.** A three-word sentence on its own is where the model stumbles.
   Sentences under four words are joined to the one before.
3. **Listen-back with retakes** (`--verify`, needs `faster-whisper`). Every sentence is transcribed and compared
   with its text. One with a wrong or unclear word is re-recorded with another seed, up to three times, and the
   best take is kept. In the demo, 31 of 428 sentences were retaken and 406 ended up matching exactly; the rest
   are spelling variants, respelled terms, and "guess" heard as "guests" at the end of a sentence.

Full-precision weights are the default for the ONNX export (`UNGLAZED_POCKET_PRECISION=int8` is slightly faster and
slightly rougher). Each sentence is levelled to the same loudness and faded at both ends.

## Pronunciation

`SAY = {"logit": "lowjit"}` in `script.py` respells a word for the voice only; the script stays readable.
Add a word only after `voice_report.json` or your ears flagged it.

## Environment

| Variable | Meaning |
|---|---|
| `UNGLAZED_TTS_PYTHON` | a Python that has the voice engine, if it is not the one running `unglazed` |
| `UNGLAZED_ASR_PYTHON`, `UNGLAZED_ASR_MODEL`, `UNGLAZED_ASR_DEVICE` | the same for listen-back (default `small.en` on the CPU) |
| `UNGLAZED_POCKET_DIR`, `UNGLAZED_POCKET_PRECISION`, `UNGLAZED_POCKET_TEMP` | the ONNX export, `fp32` or `int8`, sampling temperature (default 0.2) |

The check hears words, not tone. Listen to the first minute yourself before you publish.
