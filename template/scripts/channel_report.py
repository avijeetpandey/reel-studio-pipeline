#!/usr/bin/env python3
"""Channel report: what worked on Instagram and YouTube Shorts, from your own numbers.

  python3 -I channel_report.py [--month 2026-11] [--reels $STUDIO/reels] [--out reports/2026-11.md]

Reads every reels/*/pipeline.json that has `posts` + `stats` (pipeline.py posted / stats) and `features`
(pipeline.py features), plus reels/channel_log.json (pipeline.py channel). Writes:
  - a Markdown report (default <root>/reports/<month>.md): medians per platform, each format / hook shape /
    treatment / length band / series / post hour against the median (per platform and combined), top and bottom
    reels, where the platforms disagree, reels that beat the median 3× (follow-up candidates), channel growth;
  - reels/performance.json: per-feature scores that choose_style.py and reel-script read (only groups with n ≥ 3 count).
Score: each metric divided by your median for it (1.0 = median). Per platform = mean of its available ratios;
combined = mean of the two platforms (equal weight). Uses the 7 d window when captured, else 48 h.
Runs only when asked (the `report:` command). Nothing is scheduled.
"""
import argparse, datetime, glob, json, os, statistics, sys

CFG_PATH = os.path.expanduser(os.environ.get("REEL_STUDIO_CONFIG", "~/.config/reel-studio/config.json"))
CFG = json.load(open(CFG_PATH)) if os.path.exists(CFG_PATH) else {}
ROOT = os.path.expanduser(CFG.get("studio_dir", "~/Documents/reel-studio"))
METRICS = {"yt": ["views", "stayed_pct", "avg_viewed_pct", "shares", "subs_gained"],
           "ig": ["views", "shares_saves", "avg_view_s", "follows", "comments"]}
GROUPS = ["format", "hook_shape", "treatment", "length_band", "series", "cta"]
MIN_N = 3


def num(x):
    return x if isinstance(x, (int, float)) else None


def window(st):
    return (st or {}).get("7d") or (st or {}).get("48h")


def length_band(s):
    s = num(s)
    return None if s is None else "< 25 s" if s < 25 else "25–35 s" if s <= 35 else "36–45 s" if s <= 45 else "> 45 s"


def load_reels(reels_dir, month):
    out = []
    for mp in sorted(glob.glob(os.path.join(reels_dir, "*", "pipeline.json"))):
        m = json.load(open(mp))
        posts, stats = m.get("posts") or {}, m.get("stats") or {}
        if not posts or not stats:
            continue
        first = min((p.get("posted_at", "") for p in posts.values()), default="")
        if month and not first.startswith(month):
            continue
        f = dict(m.get("features") or {})
        f["length_band"] = length_band(f.get("length_s"))
        r = {"reel": m["reel_name"], "features": f, "posts": posts, "m": {}}
        for pf in ("yt", "ig"):
            w = window(stats.get(pf))
            if not w:
                continue
            d = {k: num(w.get(k)) for k in ("views", "stayed_pct", "avg_viewed_pct", "avg_view_s", "likes", "comments", "shares", "saves", "follows", "subs_gained")}
            if pf == "ig" and (d["shares"] is not None or d["saves"] is not None):
                d["shares_saves"] = (d["shares"] or 0) + (d["saves"] or 0)
            r["m"][pf] = d
        if r["m"]:
            out.append(r)
    return out


def score(reels):
    med = {pf: {} for pf in METRICS}
    for pf, keys in METRICS.items():
        for k in keys:
            vals = [r["m"][pf][k] for r in reels if pf in r["m"] and r["m"][pf].get(k) is not None]
            med[pf][k] = statistics.median(vals) if vals else None
    for r in reels:
        r["score"] = {}
        for pf, keys in METRICS.items():
            if pf not in r["m"]:
                continue
            ratios = [r["m"][pf][k] / med[pf][k] for k in keys if r["m"][pf].get(k) is not None and med[pf][k]]
            if ratios:
                r["score"][pf] = sum(ratios) / len(ratios)
        sc = list(r["score"].values())
        r["score"]["all"] = sum(sc) / len(sc) if sc else None
    return med


def groups(reels):
    res = {}
    for g in GROUPS:
        by = {}
        for r in reels:
            v = r["features"].get(g)
            if v in (None, ""):
                continue
            by.setdefault(str(v), []).append(r)
        res[g] = {}
        for v, rs in by.items():
            row = {"n": len(rs)}
            for pf in ("all", "yt", "ig"):
                xs = [x["score"].get(pf) for x in rs if x["score"].get(pf) is not None]
                row[pf] = round(statistics.median(xs), 2) if xs else None
            res[g][v] = row
    return res


def post_hours(reels):
    res = {}
    for pf in ("yt", "ig"):
        by = {}
        for r in reels:
            p = r["posts"].get(pf)
            if not p or r["score"].get(pf) is None:
                continue
            try:
                h = datetime.datetime.fromisoformat(p["posted_at"]).hour
            except ValueError:
                continue
            by.setdefault(h, []).append(r["score"][pf])
        res[pf] = {h: (len(v), round(statistics.median(v), 2)) for h, v in sorted(by.items())}
    return res


def fmt(x):
    return "—" if x is None else f"{x:.2f}×" if isinstance(x, float) else str(x)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--month", default=datetime.date.today().strftime("%Y-%m"), help="YYYY-MM, or 'all'")
    ap.add_argument("--reels", default=os.path.join(ROOT, "reels"))
    ap.add_argument("--out")
    a = ap.parse_args()
    month = None if a.month == "all" else a.month
    reels = load_reels(a.reels, month)
    all_reels = load_reels(a.reels, None)  # performance.json learns from everything posted so far
    out = a.out or os.path.join(os.path.dirname(a.reels.rstrip("/")), "reports", f"{a.month}.md")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    L = [f"# Channel report — {a.month}", ""]
    if not reels:
        L += ["No posted reels with stats for this period yet. Record them with `pipeline.py posted` and `pipeline.py stats` (the `stats:` command), then run `report:` again."]
    else:
        med = score(reels)
        L += [f"{len(reels)} reels with stats. Score = your own median for each metric (1.00× = median); 7-day numbers when captured, else 48 h.", "",
              "## Your medians", "| platform | " + " | ".join(sorted({k for v in METRICS.values() for k in v})) + " |", "|---|" + "---|" * len({k for v in METRICS.values() for k in v})]
        keys = sorted({k for v in METRICS.values() for k in v})
        for pf in ("yt", "ig"):
            L.append(f"| {'YouTube Shorts' if pf == 'yt' else 'Instagram'} | " + " | ".join("—" if med[pf].get(k) is None else f"{med[pf][k]:g}" for k in keys) + " |")
        ranked = sorted([r for r in reels if r["score"].get("all") is not None], key=lambda r: -r["score"]["all"])
        L += ["", "## Reels, best first", "| reel | combined | YouTube | Instagram | format | hook | treatment | length |", "|---|---|---|---|---|---|---|---|"]
        for r in ranked:
            f = r["features"]
            L.append(f"| {r['reel']} | {fmt(r['score'].get('all'))} | {fmt(r['score'].get('yt'))} | {fmt(r['score'].get('ig'))} | {f.get('format', '—')} | {f.get('hook_shape', '—')} | {f.get('treatment', '—')} | {f.get('length_band') or '—'} |")
        G = groups(reels)
        for g in GROUPS:
            if not G[g]:
                continue
            L += ["", f"## By {g.replace('_', ' ')}", "| value | n | combined | YouTube | Instagram | used for learning |", "|---|---|---|---|---|---|"]
            for v, row in sorted(G[g].items(), key=lambda kv: -(kv[1]["all"] or 0)):
                L.append(f"| {v} | {row['n']} | {fmt(row['all'])} | {fmt(row['yt'])} | {fmt(row['ig'])} | {'yes' if row['n'] >= MIN_N else f'not yet (n < {MIN_N})'} |")
        dis = [(g, v, row) for g in GROUPS for v, row in G[g].items() if row["yt"] and row["ig"] and ((row["yt"] >= 1.2 and row["ig"] <= 0.85) or (row["ig"] >= 1.2 and row["yt"] <= 0.85))]
        L += ["", "## Where the platforms disagree"]
        L += [f"- **{g} = {v}** (n {row['n']}): YouTube {fmt(row['yt'])}, Instagram {fmt(row['ig'])} → consider a platform-specific title/cover/caption for this kind of reel." for g, v, row in dis] or ["- No clear disagreement yet."]
        H = post_hours(reels)
        L += ["", "## Post time vs result (your slots: your Instagram / YouTube slots; suggestions only)"]
        for pf, rows in H.items():
            if rows:
                L.append(f"- {'YouTube' if pf == 'yt' else 'Instagram'}: " + ", ".join(f"{h:02d}:00 → {s:.2f}× (n {n})" for h, (n, s) in rows.items()))
        win = [r for r in ranked if any((r["m"].get(pf, {}).get("views") or 0) >= 3 * (med[pf].get("views") or float("inf")) for pf in ("yt", "ig"))]
        L += ["", "## Beat the median 3× on views (CHANNEL_RULES.md: suggest 2–3 follow-ups)"]
        L += [f"- **{r['reel']}** ({r['features'].get('format', '?')}, {r['features'].get('hook_shape', '?')}) → write 2–3 follow-up topics on the same idea" for r in win] or ["- None this period."]
    log = os.path.join(a.reels, "channel_log.json")
    if os.path.exists(log):
        snaps = json.load(open(log))
        L += ["", "## Channel growth"]
        for pf, key in (("yt", "subscribers"), ("ig", "followers")):
            s = [x for x in snaps if x.get("platform") == pf and num(x.get(key)) is not None and (not month or x["captured_at"].startswith(month))]
            if s:
                L.append(f"- {'YouTube' if pf == 'yt' else 'Instagram'} {key}: {s[0][key]} → {s[-1][key]} ({s[-1][key] - s[0][key]:+d}) between {s[0]['captured_at'][:10]} and {s[-1]['captured_at'][:10]}")
                last = s[-1]
                extra = {k: v for k, v in last.items() if k not in ("platform", "captured_at", key)}
                if extra:
                    L.append("  - latest snapshot: " + ", ".join(f"{k} {v}" for k, v in extra.items()))
    open(out, "w", encoding="utf-8").write("\n".join(L) + "\n")
    # performance.json: learn from every posted reel, only groups with n >= MIN_N
    if all_reels:
        score(all_reels)
        G = groups(all_reels)
        perf = {"generated": datetime.datetime.now().astimezone().isoformat(timespec="seconds"), "reels": len(all_reels), "min_n": MIN_N}
        for g in ("treatment", "format", "hook_shape", "length_band"):
            perf[g] = {v: row for v, row in G[g].items() if row["n"] >= MIN_N and row["all"] is not None}
        json.dump(perf, open(os.path.join(a.reels, "performance.json"), "w"), indent=1, ensure_ascii=False)
    print(out)


if __name__ == "__main__":
    main()
