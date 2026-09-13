#!/usr/bin/env python
"""Headless curated exploration of a Loom tree against any base model.

Grows a tree in Loom's own JSON format by calling an OpenAI-compatible
/v1/completions endpoint, so you can explore from a terminal (or a remote
session with no display) and then open the result in the Loom GUI.

The model and endpoint come from the tree's own frame -- the same
model_config Loom uses -- so a tree file is fully self-describing.

  ./explore.py init   tree.json [--seed arago-seed.txt]
  ./explore.py tree   tree.json                 # outline of the whole tree
  ./explore.py show   tree.json [node_id]       # full text along one path
  ./explore.py gen    tree.json <node_id> [-n 4] [--tokens 90] [--temp 0.9]
  ./explore.py models tree.json                 # list configured models

Model selection: --model <id> on any command, else LOOM_MODEL, else the
tree's generation_settings.model. The API key comes from LOOM_API_KEY or
OPENAI_API_KEY (not needed for a local llama.cpp server).
"""
import argparse
import json
import os
import sys
import uuid

import requests

HERE = os.path.dirname(os.path.abspath(__file__))


def load(fn):
    with open(fn) as f:
        return json.load(f)


def save(fn, tree):
    with open(fn, "w") as f:
        json.dump(tree, f, indent=1, ensure_ascii=False)


def new_node(text):
    return {"id": uuid.uuid4().hex[:8], "text": text,
            "children": [], "visited": True, "open": True}


def find(node, nid):
    if node.get("id") == nid:
        return node
    for c in node["children"]:
        r = find(c, nid)
        if r:
            return r
    return None


def path_text(root, nid):
    def walk(node, prefix):
        prefix += node["text"]
        if node.get("id") == nid:
            return prefix
        for c in node["children"]:
            r = walk(c, prefix)
            if r is not None:
                return r
        return None
    return walk(root, "")


def settings_for(tree, model_override):
    frame = tree.get("frame", {})
    gen = dict(frame.get("generation_settings", {}))
    models = frame.get("model_config", {}).get("models", {})
    model = model_override or os.environ.get("LOOM_MODEL") or gen.get("model")
    if model not in models:
        sys.exit(f"model {model!r} not in tree's model_config "
                 f"(have: {', '.join(models)})")
    info = models[model]
    base = info.get("api_base") or "https://api.openai.com/v1"
    key = os.environ.get("LOOM_API_KEY") or os.environ.get("OPENAI_API_KEY") or "none"
    return model, info, base.rstrip("/"), key, gen


def cmd_init(args):
    seed_file = args.seed or os.path.join(HERE, "arago-seed.txt")
    with open(seed_file) as f:
        seed = f.read().rstrip("\n")
    node = new_node(seed)
    template = load(os.path.join(HERE, "arago.json"))
    tree = {"root": {"id": "root", "mutable": False, "visited": True,
                     "open": True, "text": "", "children": [node]},
            "selected_node_id": node["id"],
            "frame": template["frame"]}
    save(args.tree, tree)
    print(f"seed node: {node['id']}")


def cmd_gen(args):
    tree = load(args.tree)
    node = find(tree["root"], args.node)
    if not node:
        sys.exit(f"no node {args.node}")
    model, info, base, key, gen = settings_for(tree, args.model)
    prompt = path_text(tree["root"], args.node)
    payload = {
        "model": model,
        "prompt": prompt,
        "n": args.n,
        "max_tokens": args.tokens,
        "temperature": args.temp,
        "top_p": gen.get("top_p", 1),
        "echo": False,
        "logprobs": gen.get("logprobs", 0) or 0,
    }
    if info.get("type") == "together" and not payload["logprobs"]:
        payload["logprobs"] = 1  # Together rejects logprobs=0

    def complete(pl):
        r = requests.post(f"{base}/completions", json=pl, timeout=900,
                          headers={"Authorization": f"Bearer {key}"})
        if r.status_code != 200:
            sys.exit(f"{r.status_code} from {base}: {r.text[:400]}")
        return r.json().get("choices", [])

    # llama.cpp's server has no batched sampling and rejects logprobs on
    # /v1/completions, so fan out into one call per continuation. Any other
    # endpoint that quietly ignores n gets the same treatment as a fallback.
    if info.get("type") == "llama-cpp":
        payload.pop("logprobs", None)
        choices = []
        for _ in range(args.n):
            choices += complete(dict(payload, n=1))
    else:
        choices = complete(payload)
        while len(choices) < args.n:
            choices += complete(dict(payload, n=1))

    for ch in choices:
        child = new_node(ch["text"])
        node["children"].append(child)
        print(f"[{child['id']}] {ch['text']!r}\n")
    save(args.tree, tree)
    print(f"({model} via {base})")


def cmd_show(args):
    tree = load(args.tree)
    print(path_text(tree["root"], args.node or tree["selected_node_id"]))


def cmd_tree(args):
    tree = load(args.tree)

    def walk(n, d=0):
        t = n.get("text", "").replace("\n", " / ")
        if t:
            print("  " * d + f"[{n['id']}] " + t[:150] + ("…" if len(t) > 150 else ""))
        for c in n["children"]:
            walk(c, d + 1)
    walk(tree["root"])


def cmd_models(args):
    tree = load(args.tree)
    models = tree.get("frame", {}).get("model_config", {}).get("models", {})
    cur = tree.get("frame", {}).get("generation_settings", {}).get("model")
    for k, v in models.items():
        print(f"{'*' if k == cur else ' '} {k:38} {v.get('type'):10} {v.get('api_base')}")


p = argparse.ArgumentParser(description=__doc__,
                            formatter_class=argparse.RawDescriptionHelpFormatter)
sub = p.add_subparsers(dest="cmd", required=True)
for name, fn in (("init", cmd_init), ("gen", cmd_gen), ("show", cmd_show),
                 ("tree", cmd_tree), ("models", cmd_models)):
    s = sub.add_parser(name)
    s.add_argument("tree")
    s.set_defaults(func=fn)
    if name == "init":
        s.add_argument("--seed")
    if name in ("gen", "show"):
        s.add_argument("node", nargs="?" if name == "show" else None)
    if name == "gen":
        s.add_argument("-n", type=int, default=4)
        s.add_argument("--tokens", type=int, default=90)
        s.add_argument("--temp", type=float, default=0.9)
    if name in ("gen",):
        s.add_argument("--model")

args = p.parse_args()
args.func(args)
