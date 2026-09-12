#!/usr/bin/env python
"""Minimal OpenAI-completions-compatible server for GPT-2 (ONNX).

Serves the classic /v1/completions API (echo + logprobs included) that
Loom's "openai" model type speaks, backed by the official GPT-2 124M
LM-head model from the ONNX model zoo running on CPU.

Zero API keys, zero GPU, fully local.

Usage:
    python server.py --model /path/to/gpt2-lm-head-10.onnx \
                     --tokenizer /path/to/gpt2.tiktoken --port 8010
"""

import argparse
import base64
import time
import uuid

import numpy as np
import onnxruntime as ort
import tiktoken
from flask import Flask, jsonify, request

GPT2_PAT = (
    r"""'s|'t|'re|'ve|'m|'ll|'d| ?\p{L}+| ?\p{N}+|"""
    r""" ?[^\s\p{L}\p{N}]+|\s+(?!\S)|\s+"""
)
EOT = 50256  # <|endoftext|>
CTX = 1024   # GPT-2 context window

app = Flask(__name__)
session = None
enc = None


def load(model_path, tokenizer_path):
    global session, enc
    ranks = {}
    with open(tokenizer_path, "rb") as f:
        for line in f:
            tok, rank = line.split()
            ranks[base64.b64decode(tok)] = int(rank)
    enc = tiktoken.Encoding(
        name="gpt2", pat_str=GPT2_PAT, mergeable_ranks=ranks,
        special_tokens={"<|endoftext|>": EOT},
    )
    session = ort.InferenceSession(model_path, providers=["CPUExecutionProvider"])


def logits_for(batch_ids):
    """batch_ids: list of equal-length token id lists -> [n, seq, vocab]."""
    x = np.array(batch_ids, dtype=np.int64)[:, None, :]  # [n, 1, seq]
    out = session.run(["output1"], {"input1": x})[0]     # [n, 1, seq, vocab]
    return out[:, 0]


def sample_row(logits, temperature, top_p, bias, rng):
    """Return (token_id, logprob_of_token, top_logprobs dict base)."""
    logits = logits.astype(np.float64)
    for tok_id, b in bias.items():
        logits[tok_id] += b
    logprobs_greedy = logits - logsumexp(logits)  # pre-temperature, for reporting
    if temperature <= 0.01:
        tok = int(np.argmax(logits))
        return tok, logprobs_greedy
    scaled = logits / temperature
    probs = np.exp(scaled - logsumexp(scaled))
    if top_p < 1.0:
        order = np.argsort(probs)[::-1]
        csum = np.cumsum(probs[order])
        cutoff = np.searchsorted(csum, top_p) + 1
        keep = order[:cutoff]
        mask = np.zeros_like(probs)
        mask[keep] = probs[keep]
        probs = mask / mask.sum()
    tok = int(rng.choice(len(probs), p=probs))
    return tok, logprobs_greedy


def logsumexp(x):
    m = np.max(x)
    return m + np.log(np.sum(np.exp(x - m)))


def top_k_dict(logprobs, k):
    idx = np.argsort(logprobs)[::-1][:k]
    return {enc.decode([int(i)]): round(float(logprobs[i]), 5) for i in idx}


@app.route("/v1/models", methods=["GET"])
def models():
    return jsonify({"object": "list",
                    "data": [{"id": "gpt2", "object": "model", "owned_by": "local"}]})


@app.route("/v1/completions", methods=["POST"])
def completions():
    body = request.get_json(force=True)
    prompt = body.get("prompt", "")
    if isinstance(prompt, list):
        prompt = prompt[0]
    n = int(body.get("n", 1))
    max_tokens = int(body.get("max_tokens", 16))
    temperature = float(body.get("temperature", 1.0))
    top_p = float(body.get("top_p", 1.0))
    echo = bool(body.get("echo", False))
    n_logprobs = body.get("logprobs") or 0
    stop = body.get("stop") or []
    if isinstance(stop, str):
        stop = [stop]
    bias = {}
    for k, v in (body.get("logit_bias") or {}).items():
        try:
            bias[int(k)] = float(v)
        except (TypeError, ValueError):
            pass

    prompt_ids = enc.encode(prompt) if prompt else [EOT]
    # keep room for generation inside GPT-2's context window
    prompt_ids = prompt_ids[-(CTX - max_tokens - 1):]
    plen = len(prompt_ids)
    rng = np.random.default_rng()

    # --- prompt logprobs (single forward pass, shared by all continuations)
    prompt_lp = logits_for([prompt_ids])[0]  # [seq, vocab]
    prompt_tok_strs = [enc.decode([t]) for t in prompt_ids]
    prompt_token_logprobs = [None]
    prompt_top_logprobs = [None]
    for i in range(1, plen):
        lp = prompt_lp[i - 1] - logsumexp(prompt_lp[i - 1].astype(np.float64))
        prompt_token_logprobs.append(round(float(lp[prompt_ids[i]]), 5))
        prompt_top_logprobs.append(top_k_dict(lp, n_logprobs) if n_logprobs else None)

    # --- batched sampling of n continuations
    seqs = [list(prompt_ids) for _ in range(n)]
    gen_logprobs = [[] for _ in range(n)]
    gen_top = [[] for _ in range(n)]
    finished = [None] * n
    for _step in range(max_tokens):
        if all(finished):
            break
        batch = logits_for(seqs)  # [n, seq, vocab]
        for j in range(n):
            if finished[j]:
                seqs[j].append(EOT)  # pad so the batch stays rectangular
                continue
            tok, lp = sample_row(batch[j, -1], temperature, top_p, bias, rng)
            seqs[j].append(tok)
            gen_logprobs[j].append(round(float(lp[tok]), 5))
            gen_top[j].append(top_k_dict(lp, n_logprobs) if n_logprobs else None)
            if tok == EOT:
                finished[j] = "stop"
    choices = []
    for j in range(n):
        gen_ids = seqs[j][plen:plen + len(gen_logprobs[j])]
        text = enc.decode(gen_ids)
        finish = finished[j] or "length"
        for s in stop:
            cut = text.find(s)
            if cut != -1:
                text = text[:cut]
                finish = "stop"
        tokens = [enc.decode([t]) for t in gen_ids]
        logprobs_obj = {
            "tokens": prompt_tok_strs + tokens if echo else tokens,
            "token_logprobs": (prompt_token_logprobs + gen_logprobs[j]
                               if echo else gen_logprobs[j]),
            "top_logprobs": (prompt_top_logprobs + gen_top[j]
                             if echo else gen_top[j]),
            "text_offset": [],
        }
        choices.append({
            "index": j,
            "text": (prompt + text) if echo else text,
            "finish_reason": finish,
            "logprobs": logprobs_obj if (n_logprobs or echo) else None,
        })

    return jsonify({
        "id": "cmpl-" + uuid.uuid4().hex[:24],
        "object": "text_completion",
        "created": int(time.time()),
        "model": body.get("model", "gpt2"),
        "choices": choices,
        "usage": {"prompt_tokens": plen,
                  "completion_tokens": sum(len(s) - plen for s in seqs),
                  "total_tokens": sum(len(s) for s in seqs)},
    })


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--tokenizer", required=True)
    ap.add_argument("--port", type=int, default=8010)
    args = ap.parse_args()
    load(args.model, args.tokenizer)
    app.run(host="127.0.0.1", port=args.port, threaded=False)
