# Does the seed or the simulator produce the metafiction?

Model: Mistral-7B-v0.1 (Q4_K_M) via llama.cpp. Persona: Arago. Sampling at
the root, n as stated, max_tokens=95, temperature=0.92. Scored against
[CLASSIFIER.md](CLASSIFIER.md), which was committed before any of these
continuations were generated.

| Condition | depth | n | positive | borderline | negative |
|---|---|---|---|---|---|
| EERIE seed (states the thesis) | 1 | 20 | **18 (90%)** | 2 | 0 |
| NEUTRAL seed | 1 | 20 | **1 (5%)** | 3 | 16 |
| NEUTRAL seed | 2 | 25 | **2 (8%)** | 3 | 20 |

## Reading

The seed accounts for essentially the whole effect. Strip the framing and
the same model, persona and parameters produce ordinary 1850s diary entries:
star catalogues, the Leverrier correspondence, an assistant who is in love,
a dispute about a meridian circle.

No convergence with depth was observed. 5% → 8% across a depth step is well
inside noise at this n, and the direction is carried entirely by one
artifact (below).

**Both neutral positives at depth 2 are the same trivial thing**: the entry
ends and a new dated header begins ("Paris, June 1854. From the notebook of
François Arago…", and once under a different name entirely, "Paul Gavarni,
artist and illustrator"). That is what a corpus of diary entries looks like,
not lucidity. Criterion 2 of the rubric is probably too generous in counting
it, and it is the honest weak point of these numbers.

**The sharpest finding is what the neutral condition does with its own
leaks.** The repetition attractor appears there too — "we measure them, we
measure them, and we measure them!", and a stretch of mirrored dialogue
where narrator and assistant echo each other into "Yes. / Yes. / Yes." The
incoherence is present in both conditions. Only in the EERIE condition does
the narrator ever *interpret* it. Against Pressman's formulation that a
model "can notice itself by its own incoherence," at this scale it does not
notice unless the prompt has told it to look.

## What this does not show

- One model, 7B, 4-bit. The claim as stated by Janus predicts lucidity
  increases with scale, so a null at 7B is weak evidence about davinci-002,
  405B-base, or frontier chat models. The scale ladder is the missing
  experiment.
- Depth 2 only. "Leaks accumulate" may need far longer contexts than ~190
  generated tokens.
- A single rater (me), scoring my own seeds, albeit against a rubric fixed
  in advance.
