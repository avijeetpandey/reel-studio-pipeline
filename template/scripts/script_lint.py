#!/usr/bin/env python3
"""Script gate: run on a reel's script.md BEFORE the shoot card is made. Catches what the 28 Oct analytics showed:
jargon in the first 10 s (the 3-7 s retention cliff), too many words, soft hooks, and a CTA nobody reaches.

  python3 -I script_lint.py <reel folder or script.md>      exit 0 = pass, 1 = fix before filming

Reads the spoken lines ("## What you say" numbered list, or the "## Script" blocks, or "## Teleprompter").
Rules (all from round 6 + the channel analytics): 70-95 words / 25-32 s at ~170-200 wpm; first line <= 8 words and no greeting;
zero jargon words in the first ~10 s (about the first 28 words); no wind-up phrases; a debatable question appears before the last
15% of the script, not only at the end; one concept (<= 2 terms from the jargon list in the whole script).
"""
import os, re, sys

JARGON = {"vector", "embedding", "embeddings", "backoff", "idempotent", "idempotency", "latent", "diffusion", "tokenizer", "quantization",
          "kubernetes", "microservice", "microservices", "sidecar", "mutex", "semaphore", "heuristic", "asynchronous", "protocol", "payload",
          "endpoint", "middleware", "orchestration", "inference", "gradient", "parameters", "transformer", "attention", "kv", "paging", "grep",
          "regex", "websocket", "queue", "queues", "retries", "retry", "daemon", "ack", "acks", "database", "stateless", "schema", "api"}
WINDUP = ["standard design", "in this video", "let me explain", "so today", "hi guys", "hey guys", "welcome back", "before we start", "confused?", "don't let this fancy word",
          "as you know", "let's dive", "let's talk about"]


def spoken(md):
    def sec(name):
        m = re.search(r"^##\s+" + name + r"[^\n]*\n(.*?)(?=^##\s|\Z)", md, re.S | re.M | re.I)
        return m.group(1) if m else ""
    lines = [m.group(1) for m in re.finditer(r"^\d+\.\s+(.+)$", sec("What you say"), re.M)]
    if not lines:
        for b in re.split(r"^(?=\*\*)", sec("Script"), flags=re.M):
            _, _, body = b.partition("\n")
            t = re.sub(r"\*?\([^)]*\)\*?", "", body).strip()
            if b.startswith("**") and t:
                lines.append(t)
    if not lines:
        lines = [p for p in sec("Teleprompter").split("\n\n") if p.strip()]
    return [re.sub(r"[*_`]", "", l).strip() for l in lines]


def main():
    p = sys.argv[1]
    p = os.path.join(p, "script.md") if os.path.isdir(p) else p
    lines = spoken(open(p, encoding="utf-8").read())
    if not lines:
        print("no spoken lines found"); sys.exit(1)
    words = [w for l in lines for w in l.split()]
    n, bad = len(words), []
    first = lines[0]
    if n > 95: bad.append(f"{n} words: cut to 95 or fewer (about 32 s). Every extra sentence costs viewers.")
    if n < 60: bad.append(f"{n} words is thin: 70-95 gives 25-32 s.")
    if len(first.split()) > 8: bad.append(f"Hook is {len(first.split())} words: 8 or fewer. \"{first}\"")
    low = " ".join(lines).lower()
    for w in WINDUP:
        if w in low: bad.append(f"Wind-up phrase \"{w}\": delete it, start with the payoff.")
    head = [re.sub(r"[^a-z0-9]", "", w.lower()) for w in words[:28]]
    hot = sorted({w for w in head if w in JARGON})
    if hot: bad.append(f"Jargon in the first ~10 s: {', '.join(hot)}. Say it with an everyday word first, name the term after the 10 s mark.")
    allhot = sorted({re.sub(r"[^a-z0-9]", "", w.lower()) for w in words} & JARGON)
    if len(allhot) > 2: bad.append(f"{len(allhot)} jargon terms ({', '.join(allhot)}): keep one idea, at most 2 terms.")
    cut = int(n * 0.85)
    before = " ".join(words[:cut])
    if "?" not in before:
        bad.append("No question before the last 15%. Put a debatable line at the twist (about 12-15 s); most viewers never reach the end.")
    print(f"{p}: {len(lines)} lines, {n} words (~{n / 3.0:.0f} s at 180 wpm)")
    print("PASS" if not bad else "\n".join("FIX: " + b for b in bad))
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
