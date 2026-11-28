#!/usr/bin/env python3
"""Weekly outlier scan: which Shorts beat their own channel's median by >= 5x (feeds the idea bank).

  outlier_scan.py [--channels FILE] [--per 60] [--min-x 5] [--out DIR]
  outlier_scan.py --selftest

One yt-dlp call at a time under `nice` (flat listing, no video download), so it never loads the machine.
Paid-promotion Shorts are not detected automatically: likes are not in a flat listing, so read the top rows by eye
(a promo usually names a sponsor or a course). Run only when the creator types `scan:`; never schedule it.
"""
import argparse, datetime, json, os, statistics, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
_CFG_PATH = os.path.expanduser(os.environ.get("REEL_STUDIO_CONFIG", "~/.config/reel-studio/config.json"))
_CFG = json.load(open(_CFG_PATH)) if os.path.exists(_CFG_PATH) else {}
ROOT = os.path.expanduser(_CFG.get("studio_dir", "~/Documents/reel-studio"))
SEP = "\x1f"


def fetch(handle, per):
    """[(id, views, title, upload_date or '')] for a channel's Shorts tab, newest first."""
    url = f"https://www.youtube.com/@{handle}/shorts"
    p = subprocess.run(["nice", "-n", "15", "yt-dlp", "--flat-playlist", "--playlist-end", str(per), "--socket-timeout", "20",
                        "--print", f"%(id)s{SEP}%(view_count)s{SEP}%(title)s", url], capture_output=True, text=True, timeout=180)
    out = []
    for line in p.stdout.splitlines():
        f = line.split(SEP)
        if len(f) == 3 and f[1].isdigit():
            out.append((f[0], int(f[1]), f[2]))
    return out


def outliers(vids, min_x, min_n=10):
    """Shorts at >= min_x times the channel median, best first. Channels with < min_n Shorts are skipped (median meaningless)."""
    if len(vids) < min_n:
        return None, []
    med = statistics.median(v for _, v, _ in vids) or 1
    return med, sorted([(i, v, round(v / med, 1), t) for i, v, t in vids if v >= min_x * med], key=lambda r: -r[2])


def selftest():
    vids = [(f"id{i}", 1000, "t") for i in range(12)] + [("big", 9000, "hit"), ("mid", 4000, "ok")]
    med, top = outliers(vids, 5)
    assert med == 1000 and [r[0] for r in top] == ["big"] and top[0][2] == 9.0, (med, top)
    assert outliers(vids[:5], 5) == (None, [])
    print("selftest ok")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--channels", default=os.path.join(HERE, "outlier_channels.txt"))
    ap.add_argument("--per", type=int, default=60, help="newest N Shorts per channel")
    ap.add_argument("--min-x", type=float, default=5)
    ap.add_argument("--out", default=os.path.join(ROOT, "research", "outliers"))
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    chans = [l.split("#")[0].strip() for l in open(a.channels, encoding="utf-8")]
    chans = [c for c in chans if c]
    rows, skipped = [], []
    for i, h in enumerate(chans, 1):
        try:
            med, top = outliers(fetch(h, a.per), a.min_x)
        except subprocess.TimeoutExpired:
            med, top = None, []
        print(f"[{i}/{len(chans)}] {h}: " + (f"median {med:,.0f}, {len(top)} outliers" if med else "skipped"), file=sys.stderr)
        if med is None:
            skipped.append(h)
        rows += [(h, med) + r for r in top]
    rows.sort(key=lambda r: -r[4])
    os.makedirs(a.out, exist_ok=True)
    f = os.path.join(a.out, f"{datetime.date.today()}.md")
    md = [f"# Outlier scan {datetime.date.today()} — Shorts at >= {a.min_x:g}x their channel median (newest {a.per} per channel)", "",
          "Score every row you'd use against `template/IDEA_SCORECARD.md` (which engine?) before it enters the idea bank. Check the top rows for paid promotions.", "",
          "| x median | views | channel | title | link |", "|---|---|---|---|---|"]
    md += [f"| {r[4]} | {r[3]:,} | {r[0]} | {r[5].replace('|', '/')} | https://youtube.com/shorts/{r[2]} |" for r in rows[:80]]
    if skipped:
        md += ["", "Skipped (handle not found or < 10 Shorts): " + ", ".join(skipped)]
    open(f, "w", encoding="utf-8").write("\n".join(md) + "\n")
    print(f)


if __name__ == "__main__":
    main()
