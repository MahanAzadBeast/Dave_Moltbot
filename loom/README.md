# Loom — running base models

[Loom](https://github.com/socketteer/loom) is a tree-based (multiverse) writing
interface built for **base models**: you write a prompt, generate N
continuations at a node, and explore/branch the tree. This folder contains a
tested installer and a guide for pointing Loom at base models.

Loom is a desktop GUI (Python + tkinter), so run it on your own machine
(Mac/Windows/Linux), not on a headless server.

## Install

```bash
./loom/install-loom.sh
```

The script:

1. finds a Python 3.10+ that has tkinter (on macOS: `brew install python-tk`;
   on Debian/Ubuntu: `sudo apt-get install python3-tk`),
2. clones `socketteer/loom` into `loom/loom/` (gitignored),
3. creates a virtualenv at `loom/.venv/` and installs
   [`requirements-modern.txt`](requirements-modern.txt) — the upstream
   `requirements.txt` pins 2020-era versions that no longer build on current
   Python, so we use a modernized set (verified working on Python 3.12).

## Run

```bash
export OPENAI_API_KEY=sk-...     # see provider options below
./loom/run-loom.sh
```

Instead of exporting, you can put keys in `loom/.env` (gitignored):

```bash
OPENAI_API_KEY=sk-...
TOGETHERAI_API_KEY=...
```

Basic workflow: type into the story box, press `g` (or the **Generate**
button) to sample continuations, arrow keys to walk the tree, `Ctrl-Shift-P`
for generation settings (model, temperature, number of continuations, length).

## Choosing a base model

Loom's generation settings (`Ctrl-Shift-P`) have a **model** dropdown. Models
are defined under **Settings → Model config**, where you can add your own with
**Add Model**.

> **Important quirk:** Loom sends the *model id* (the first field in the Add
> Model dialog, i.e. the dropdown key) as the `model` parameter of the API
> call. So when adding a model, set the **Model id to the provider's exact
> model string** (e.g. `meta-llama/Meta-Llama-3.1-405B`); the "Model name"
> field is cosmetic.

### Option 1 — OpenAI (works out of the box)

`davinci-002` and `babbage-002` are OpenAI's remaining base models and are
already in Loom's default model list. Just set `OPENAI_API_KEY` and pick
`davinci-002` in generation settings. (`gpt-3.5-turbo-instruct` is also
pre-configured; it's instruct-tuned, not a true base model.)

### Option 2 — OpenAI-compatible providers with strong base models

Any provider with an OpenAI-compatible **completions** endpoint works via
**Add Model** with type `openai`. Because type `openai` reads
`OPENAI_API_KEY`, set that env var to the *provider's* key when using one of
these (one provider per session):

| Provider | API base | Example base models |
|---|---|---|
| Hyperbolic | `https://api.hyperbolic.xyz/v1` | `meta-llama/Meta-Llama-3.1-405B` (base) |
| OpenRouter | `https://openrouter.ai/api/v1` | `meta-llama/llama-3.1-405b` (base) |
| Together AI | `https://api.together.xyz/v1` | `mistralai/Mistral-7B-v0.1` |

Add Model example for Hyperbolic's Llama 3.1 405B **base**:

- Model id: `meta-llama/Meta-Llama-3.1-405B`
- Model name: `llama-405b-base`
- Model type: `openai`
- API base: `https://api.hyperbolic.xyz/v1`

Together AI has its own model type `together` (uses `TOGETHERAI_API_KEY`, so
it can coexist with an OpenAI key); `mistralai/Mistral-7B-v0.1` is already in
the default list. Note: with type `together`, `logprobs` must be > 0 in
generation settings.

Notes:
- Base models need the plain **completions** API. Loom uses it for every type
  except `openai-chat`, which is what you want.
- Some providers don't support `logprobs`/`echo` on completions; if generation
  errors, try setting `logprobs` to 0 (or 1) in generation settings.

### Option 3 — Fully local with llama.cpp

Loom ships a preset `llama-cpp-port-8009` that points at
`http://localhost:8009/v1`. Serve any GGUF **base** model (e.g.
`Meta-Llama-3-8B`, not `-Instruct`) with:

```bash
pip install "llama-cpp-python[server]"
python -m llama_cpp.server --model /path/to/Meta-Llama-3-8B.Q4_K_M.gguf --port 8009
```

Then pick `llama-cpp-port-8009` in generation settings. No API key needed.
(llama.cpp can't batch, so Loom makes N sequential calls for N continuations.)

### Option 4 — Zero-key local GPT-2 (tested end-to-end)

If you have no API keys at all, [`gpt2-local/`](gpt2-local/) runs OpenAI's
original GPT-2 base model (124M) fully locally on CPU behind a
Loom-compatible completions server — echo, logprobs, and batched
multi-continuation sampling included. Weights come from the official
`onnx/models` zoo (checksum-verified), the tokenizer from `openai/whisper`'s
repo, so no Hugging Face account is needed.

```bash
./loom/gpt2-local/fetch-gpt2.sh                       # ~665 MB download
./loom/.venv/bin/pip install onnxruntime tiktoken flask
./loom/.venv/bin/python loom/gpt2-local/server.py \
    --model loom/gpt2-local/gpt2-lm-head-10.onnx \
    --tokenizer loom/gpt2-local/gpt2.tiktoken --port 8010
```

Then in Loom (with `OPENAI_API_KEY` set to any placeholder), add a model via
Settings → Model config → Add Model:

- Model id: `gpt2` · type: `openai` · API base: `http://127.0.0.1:8010/v1`

Or start from the ready-made tree `gpt2-local/gpt2_demo.json` (File → Open),
which has this model config baked in.

## The Arago experiment

[`base-model/`](base-model/) holds a ready-to-run experiment in the
[cyborgism](https://cyborgism.wiki/hypha/arago) vein: a seed framing François
Arago's last notebook so that a simulator's own artifacts (repetition,
anachronism, format collapse) read as the narrator's dawning suspicion that
his world is not continuous.

- `arago-seed.txt` — the seed prompt.
- `arago.json` — a Loom tree with the seed and four models pre-configured
  (`davinci-002`, Hyperbolic Llama-3.1-405B base, Together Mistral-7B-v0.1,
  and `local-gguf`). Open it, pick a model in generation settings (`Ctrl-Shift-P`),
  press `g`.
- `serve-gguf.sh` — serve any local GGUF base model to Loom via llama.cpp on
  `http://127.0.0.1:8011/v1`, no API key.
- `explore.py` — headless curated exploration, for terminals and remote
  sessions with no display. It grows the same Loom JSON, so you can explore
  from a shell and open the result in the GUI afterwards:

  ```bash
  export OPENAI_API_KEY=sk-...
  ./loom/base-model/explore.py init run.json
  ./loom/base-model/explore.py gen  run.json <node_id> -n 5 --tokens 90
  ./loom/base-model/explore.py tree run.json          # outline
  ./loom/base-model/explore.py show run.json <node_id>  # one full path
  ```

  Pick the model with `--model` (or `LOOM_MODEL`); `explore.py models
  run.json` lists what the tree has configured.

### Runs

`arago-mistral-7b-run.json` (19 nodes) is a run against **Mistral-7B-v0.1
base**, served locally with `serve-gguf.sh` — no API key. It is the one to
read: the narrator holds his voice across paragraphs, and the model's own
errors arrive *as his evidence*. He misattributes "there is nothing outside
the text" to Mallarmé (it is Derrida, 1967) and reasons from it; he computes
his own age wrongly and concludes he has not aged; and at depth the
repetition attractor that base models fall into reads as perseveration —
"I have seen the world, and it is not continuous. / I have seen the world. /
I have seen the world." One branch closes its syllogism into an infinite
loop; another escapes by a Cartesian move, arguing itself into existence in
order to deny its world.

Reproduce with:

```bash
hf download TheBloke/Mistral-7B-v0.1-GGUF mistral-7b-v0.1.Q4_K_M.gguf --local-dir ~/models
./loom/base-model/serve-gguf.sh ~/models/mistral-7b-v0.1.Q4_K_M.gguf 8011
./loom/base-model/explore.py init run.json
./loom/base-model/explore.py gen run.json <seed_id> -n 4 --tokens 95 --model local-gguf
```

A run against GPT-2 124M is preserved in
[`../gpt2-local/arago-gpt2-run.json`](../gpt2-local/arago-gpt2-run.json) (42
nodes). It is worth opening as a baseline: at that scale the *leaks* are real
but no narrator survives to notice them — the document decays into archival
debris and terminates on a literal end-of-text token. Model scale is the
variable that matters here; a base model large enough to hold a character
across paragraphs turns those same artifacts into something that reads as
awareness.

## Troubleshooting

- **`ModuleNotFoundError: tkinter`** — your Python lacks Tk bindings; install
  `python3-tk` (Linux) / `brew install python-tk` (macOS) and rerun the
  installer.
- **PyTorch warning from transformers at startup** — harmless; Loom only uses
  the tokenizer utilities.
- **Blank error on Generate** — check the terminal Loom was launched from; API
  errors (bad key, unsupported `logprobs`, wrong model id) are printed there.
- **Model config is saved per tree file** — models you add via Settings →
  Model config live in the currently open tree's JSON, so re-add them (or
  reuse a tree file as a template) for new trees.
