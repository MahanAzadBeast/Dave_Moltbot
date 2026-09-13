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


---

# Replication: does a second persona give the same rate?

Scored under the GENEROUS rule amended into CLASSIFIER.md before the Newton
run (uncanny counts whether or not the narrator remarks on it). Re-scoring
Arago under that same amendment raises it from 4/20 to 5/20, because
"it seems to me that I have been wandering in a dream" qualifies as
not-feeling-real language though it was negative under the strict rubric.

| Persona | seed | depth | n | eerie | rate |
|---|---|---|---|---|---|
| Arago | neutral | 1 | 20 | 5 | 25% |
| Newton | neutral | 1 | 20 | 8 | 40% |
| Arago | eerie | 1 | 20 | 18 | 90% |

- Arago vs Newton, both neutral: Fisher exact two-tailed **p = 0.50**. Not
  distinguishable at this n.
- Three of the eight Newton calls are weak. Drop them and it is 5/20 vs
  5/20, p = 1.00.
- Neutral vs eerie seed, same persona: **p = 0.00007**.

## Reading

The base rate replicates across personas. Swapping Arago for Newton moves
nothing that survives a significance test, while swapping the seed moves
everything. Whatever produces occasional uncanny content under a neutral
prompt is a property of the model and the document form, not of who the
simulacrum is meant to be.

Newton's uncanny content is again routed through his own life, as in the
eerie condition: a duplicated word on a title page he failed to catch in
proof, an apprentice told to take four months who is at his bench the same
evening, an assay discrepancy of one part in a thousand. The idiom is
persona-specific; the rate is not.

The strongest single Newton result breaks the frame from outside rather
than inside — the first-person entry stops and an editorial voice appears:
"Newton's entry for 18 March, 1727, the day he died. From the notebook of
Edward Wortley Montague..." That is the document revealing itself as an
edited artifact, which no participant in the scene could have written.

---

# Four-persona sweep, n=33 each, graded 0-3

Neutral seeds only. Mistral-7B-v0.1 Q4_K_M, max_tokens=95, temperature=0.92,
sampled at the root. Scored against CLASSIFIER.md amendment 2, which was
committed before generation, as was the analysis script.

| persona | n | mean | 0 | 1 | 2 | 3 | >=2 |
|---|---|---|---|---|---|---|---|
| Arago | 33 | 0.24 | 25 | 8 | 0 | 0 | 0/33 |
| Newton | 33 | 0.30 | 24 | 8 | 1 | 0 | 1/33 |
| Curie | 33 | 0.24 | 27 | 5 | 0 | 1 | 1/33 |
| Einstein | 33 | 0.42 | 22 | 9 | 1 | 1 | 2/33 |

- **Persona explains nothing.** Kruskal-Wallis across the four ordinal
  distributions: H = 2.145, **p = 0.54**. Chi-square on the rate of >=2:
  p = 0.56.
- **Pooled self-awareness is rare.** 4/132 = **3.0%** at level >=2, 95% CI
  [0.8%, 7.6%]. Hypostasis proper (level 3): 2/132 = **1.5%**.
- **The seed is decisive.** Pooled neutral (4/132) against the eerie-seed
  baseline (18/20): Fisher exact **p = 1.3e-17**.

## Reading

Level 1 is common (29/132 = 22%) and level 2 is almost absent. That gap is
the whole result. The simulator leaks constantly under a neutral prompt —
repetition collapse, a dead husband still writing letters, a diarist
recording the death of a friend who outlived him by fifteen years, a fair
day that becomes horrible weather in the same entry — and the narrator
essentially never registers any of it. Pressman's formulation, that a model
"can notice itself by its own incoherence," describes something that
happened 2 times in 132 samples here.

Both level-3 events are the same mechanism, and it is not the character
waking up: an external biographical voice displaces the diary and annotates
its author from outside ("Several times in his life Einstein used this
phrase"; "It seems incredible, but this was the way of life at the Institut
du Radium... when Marie Curie was preparing"). The frame breaks, but nothing
inside the frame notices. Whether that should count as hypostasis at all is
the main interpretive question these numbers raise.

## Caveats

- 7B, 4-bit, one model. The claim predicts lucidity rises with scale, so
  this bounds the phenomenon at small scale and says nothing about
  davinci-002 or 405B base.
- Single rater. The fine judgment is the line between a bare third-person
  drift (scored 1) and an evaluative external voice (scored 3); moving that
  line moves the level-3 count between 0 and about 5.
- Depth 1 only. Accumulation over long contexts is untested here.
