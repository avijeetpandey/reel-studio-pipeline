#!/usr/bin/env python3
"""make-content pipeline helper: manifest, render locks, footage pickup, approval-gated Drive uploads.
Spec: $STUDIO/template/PIPELINE.md · Skill: $PLUGIN/skills/make-content/SKILL.md

  pipeline.py init <reel> [--topic T] [--playbook R03] [--carousel C02]
  pipeline.py set <reel> <stage> <status> [--note TEXT]        status: pending|running|done|failed|waiting
  pipeline.py file <reel> <key> <path>                         keys: video cover_a cover_b srt posting_kit linkedin_post linkedin_image carousel_dir
  pipeline.py approve <reel> checkpoint1|checkpoint2
  pipeline.py status [<reel>]                                  table of every topic (or one topic's stages)
  pipeline.py next <reel>                                      first stage that isn't finished
  pipeline.py locked render|final -- <command ...>             run a command under the machine-wide render limit
  pipeline.py footage <reel> [--file PATH] [--dry-run]         find the AirDropped clip, check it, copy to reels/<reel>/src.<ext>
  pipeline.py upload <reel> half1|half2                        approval-gated rclone upload + byte-size verification
  pipeline.py features <reel> key=value ...                    what the reel IS (format, hook_shape, treatment, length_s, wpm, …) for the report
  pipeline.py posted <reel> [--ig URL] [--yt URL] [--at ISO]   where/when it was posted (both platforms)
  pipeline.py stats <reel> ig|yt --window 48h|7d [--json FILE] [key=value ...]   record numbers read from Insights / Studio
  pipeline.py channel ig|yt [--json FILE] [key=value ...]      record a channel-level snapshot (followers/subs, 7/28-day totals, …)
  pipeline.py due                                              which posted reels have 48 h / 7 d stats due (nothing runs on its own)
"""
import argparse, datetime, fcntl, glob, json, os, shutil, subprocess, sys, time

_CFG_PATH = os.path.expanduser(os.environ.get("REEL_STUDIO_CONFIG", "~/.config/reel-studio/config.json"))
_CFG = json.load(open(_CFG_PATH)) if os.path.exists(_CFG_PATH) else {}
ROOT = os.path.expanduser(_CFG.get("studio_dir", "~/Documents/reel-studio"))
REELS = os.path.join(ROOT, "reels")
LOCKS = os.path.join(ROOT, ".locks")
INBOXES = [os.path.join(ROOT, "inbox"), os.path.expanduser("~/Downloads")]
REMOTE = f'{_CFG.get("drive_remote", "gdrive")}:{_CFG.get("drive_folder", "reels")}'
LIMITS = {"render": 4, "final": 1}
STAGES = ["research", "script", "carousel", "linkedin", "checkpoint1", "upload1",
          "footage", "cut", "plan", "build", "covers", "posting_kit", "qa", "checkpoint2", "final", "upload2"]
VIDEO_EXT = (".mov", ".mp4", ".m4v")
STATS_LOG = os.path.join(REELS, "stats_log.md")
CHANNEL_LOG = os.path.join(REELS, "channel_log.json")
# channel targets (CHANNEL_RULES.md): checked on the 48 h window
TARGETS = {"yt": {"stayed_pct": 70, "avg_viewed_pct": 80}, "ig": {"shares_saves": 5}}


def now():
    return datetime.datetime.now().astimezone().isoformat(timespec="seconds")


def mpath(reel):
    return os.path.join(REELS, reel, "pipeline.json")


def load(reel):
    p = mpath(reel)
    if not os.path.exists(p):
        sys.exit(f"no manifest for '{reel}' — run: pipeline.py init {reel}")
    return json.load(open(p))


def save(reel, m):
    m["updated"] = now()
    tmp = mpath(reel) + ".tmp"
    json.dump(m, open(tmp, "w"), indent=2)
    os.replace(tmp, mpath(reel))   # atomic: parallel helpers never see a half-written file


def cmd_init(a):
    os.makedirs(os.path.join(REELS, a.reel), exist_ok=True)
    if os.path.exists(mpath(a.reel)):
        print(f"manifest exists: {mpath(a.reel)} (unchanged)"); return
    m = {"reel_name": a.reel, "topic": a.topic, "playbook_id": a.playbook, "carousel_id": a.carousel,
         "created": now(), "stages": {s: {"status": "pending"} for s in STAGES},
         "files": {}, "drive": f"{REMOTE}/{a.reel}", "errors": []}
    m["stages"]["footage"]["status"] = "waiting"
    save(a.reel, m); print(mpath(a.reel))


def cmd_set(a):
    m = load(a.reel)
    if a.stage not in m["stages"]:
        sys.exit(f"unknown stage {a.stage}; stages: {', '.join(STAGES)}")
    st = m["stages"][a.stage]
    st["status"], st["at"] = a.status, now()
    if a.status == "running":
        st["attempts"] = st.get("attempts", 0) + 1
    if a.note:
        st["note"] = a.note
        if a.status == "failed":
            m["errors"].append({"stage": a.stage, "at": now(), "error": a.note})
    save(a.reel, m); print(f"{a.reel}: {a.stage} → {a.status}")


def cmd_file(a):
    m = load(a.reel)
    p = os.path.abspath(os.path.expanduser(a.path))
    if not os.path.exists(p):
        sys.exit(f"not found: {p}")
    m["files"][a.key] = p
    save(a.reel, m); print(f"{a.reel}: {a.key} = {p}")


def cmd_approve(a):
    m = load(a.reel)
    m["stages"][a.checkpoint].update(status="approved", by="the creator", at=now())
    save(a.reel, m); print(f"{a.reel}: {a.checkpoint} approved")


DONE = ("done", "approved")


def cmd_next(a):
    m = load(a.reel)
    for s in STAGES:
        if m["stages"][s]["status"] not in DONE:
            print(s); return
    print("complete")


def cmd_status(a):
    reels = [a.reel] if a.reel else sorted(os.path.basename(os.path.dirname(p)) for p in glob.glob(os.path.join(REELS, "*", "pipeline.json")))
    if a.reel:
        m = load(a.reel)
        print(f"{a.reel}  ({m.get('playbook_id') or '-'} / {m.get('carousel_id') or '-'})  {m.get('topic') or ''}")
        for s in STAGES:
            st = m["stages"][s]
            print(f"  {s:12} {st['status']:9} {st.get('at', '')}  {st.get('note', '')}")
        for k, v in m["files"].items():
            print(f"  file {k}: {v}")
        return
    if not reels:
        print("no pipelines yet"); return
    for r in reels:
        m = load(r)
        nxt = next((s for s in STAGES if m["stages"][s]["status"] not in DONE), "complete")
        failed = [s for s in STAGES if m["stages"][s]["status"] == "failed"]
        print(f"{r:45} next: {nxt:12} {'FAILED: ' + ','.join(failed) if failed else ''}")


def cmd_locked(a):
    """Machine-wide semaphore: at most LIMITS[kind] commands of this kind run at once (lock files + flock)."""
    os.makedirs(LOCKS, exist_ok=True)
    while True:
        for i in range(LIMITS[a.kind]):
            f = open(os.path.join(LOCKS, f"{a.kind}-{i}"), "w")
            try:
                fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                f.close(); continue
            try:
                sys.exit(subprocess.call(a.command))
            finally:
                fcntl.flock(f, fcntl.LOCK_UN); f.close()
        time.sleep(1)


def probe(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration:stream=codec_type,width,height",
                          "-of", "json", path], capture_output=True, text=True).stdout
    d = json.loads(out or "{}")
    v = [s for s in d.get("streams", []) if s.get("codec_type") == "video"]
    return {"duration": float(d.get("format", {}).get("duration", 0) or 0),
            "audio": any(s.get("codec_type") == "audio" for s in d.get("streams", [])),
            "w": v[0].get("width", 0) if v else 0, "h": v[0].get("height", 0) if v else 0}


def cmd_footage(a):
    m = load(a.reel)
    if a.file:
        cands = [os.path.expanduser(a.file)]
    else:
        since = datetime.datetime.fromisoformat(m["created"]).timestamp() - 3600
        cands = [p for d in INBOXES for p in glob.glob(os.path.join(d, "*"))
                 if p.lower().endswith(VIDEO_EXT) and os.path.getmtime(p) >= since]
        keys = [k.lower() for k in (a.reel, m.get("playbook_id")) if k]
        named = [p for p in cands if any(k in os.path.basename(p).lower() for k in keys)]
        cands = sorted(named or cands, key=os.path.getmtime, reverse=True)
    if not cands:
        sys.exit("NO_FOOTAGE: no new video in ~/Downloads or inbox/ since this topic started — AirDrop it, or pass --file")
    if len(cands) > 1 and not a.file:
        print("CANDIDATES (newest first) — confirm one with --file:")
        for p in cands[:5]:
            print(f"  {p}  {os.path.getsize(p) / 1e6:.0f} MB  {datetime.datetime.fromtimestamp(os.path.getmtime(p)):%d %b %H:%M}")
        if not a.dry_run:
            sys.exit(2)
        return
    src = cands[0]
    s1 = os.path.getsize(src); time.sleep(15)
    if os.path.getsize(src) != s1:
        sys.exit("STILL_COPYING: file size is changing — try again in a minute")
    info, problems = probe(src), []
    if min(info["w"], info["h"]) < 1080: problems.append(f"resolution {info['w']}x{info['h']} (< 1080p)")
    if not 15 <= info["duration"] <= 480: problems.append(f"duration {info['duration']:.0f}s (expected 15 s–8 min)")
    if not info["audio"]: problems.append("no audio track")
    free = shutil.disk_usage(ROOT).free / 1e9
    if free < 20: problems.append(f"only {free:.0f} GB free disk (need 20)")
    print(f"footage: {src}\n  {info['w']}x{info['h']}, {info['duration']:.1f}s, audio={info['audio']}, disk free {free:.0f} GB")
    if problems:
        print("PREFLIGHT FAILED: " + "; ".join(problems)); sys.exit(3)
    if a.dry_run:
        print("dry run — not copied"); return
    dst = os.path.join(REELS, a.reel, "src" + os.path.splitext(src)[1].lower())
    shutil.copy2(src, dst)   # copy, never move/delete the creator's original
    m["stages"]["footage"].update(status="done", at=now(), note=src)
    m["files"]["source"] = dst
    save(a.reel, m); print(f"copied → {dst}")


def rclone(*args):
    r = subprocess.run(["rclone", *args], capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(r.stderr.strip().splitlines()[-1] if r.stderr.strip() else "rclone failed")
    return r.stdout


def remote_sizes(remote):
    out = rclone("lsl", remote)
    sizes = {}
    for line in out.splitlines():
        parts = line.split(None, 3)
        if len(parts) == 4:
            sizes[parts[3]] = int(parts[0])
    return sizes


def cmd_upload(a):
    m = load(a.reel)
    gate = "checkpoint1" if a.half == "half1" else "checkpoint2"
    if m["stages"][gate]["status"] != "approved":
        sys.exit(f"REFUSED: {gate} is not approved for {a.reel} (CHANNEL_RULES.md: upload only after the creator approves)")
    f, r, plan = m["files"], m["drive"], []
    if a.half == "half1":
        cd = f.get("carousel_dir")
        if cd:
            for p in sorted(glob.glob(os.path.join(cd, "out", "slide-*.jpg"))):
                plan.append((p, f"carousel/{os.path.basename(p)}"))
            for p in glob.glob(os.path.join(cd, "out", "*-linkedin.pdf")):
                plan.append((p, f"carousel/{a.reel}_carousel-linkedin.pdf"))
            if os.path.exists(os.path.join(cd, "caption.md")):
                plan.append((os.path.join(cd, "caption.md"), f"carousel/{a.reel}_carousel_caption.md"))
        for key, name in (("linkedin_post", "_linkedin_post.md"), ("linkedin_image", "_linkedin_image.png")):
            if f.get(key): plan.append((f[key], a.reel + name))
    else:
        for key, name in (("video", ".mp4"), ("video_b", "_hookB.mp4"), ("cover_a", "_thumbnail.jpg"), ("cover_b", "_thumbnail_b.jpg"),
                          ("srt", ".srt"), ("posting_kit", "_posting_kit.md")):
            if f.get(key): plan.append((f[key], a.reel + name))
            elif key in ("video", "cover_a", "cover_b"): sys.exit(f"REFUSED: missing file '{key}' — record it with: pipeline.py file {a.reel} {key} <path>")
    if not plan:
        sys.exit("nothing to upload")
    stage = "upload1" if a.half == "half1" else "upload2"
    m["stages"][stage].update(status="running", at=now()); save(a.reel, m)
    try:
        rclone("mkdir", r)
        for local, rel in plan:
            rclone("copyto", local, f"{r}/{rel}")
        sizes = remote_sizes(r)
        bad = [rel for local, rel in plan if sizes.get(rel) != os.path.getsize(local)]
        for local, rel in plan:   # one retry for any mismatch
            if rel in bad: rclone("copyto", local, f"{r}/{rel}")
        if bad:
            sizes = remote_sizes(r)
            bad = [rel for local, rel in plan if sizes.get(rel) != os.path.getsize(local)]
    except RuntimeError as e:
        m = load(a.reel); m["stages"][stage].update(status="failed", note=str(e)); m["errors"].append({"stage": stage, "at": now(), "error": str(e)}); save(a.reel, m)
        sys.exit(f"UPLOAD FAILED: {e}")
    m = load(a.reel)
    if bad:
        m["stages"][stage].update(status="failed", note="size mismatch: " + ", ".join(bad)); save(a.reel, m)
        sys.exit("UPLOAD MISMATCH: " + ", ".join(bad))
    m["stages"][stage].update(status="done", at=now(), verified=True); save(a.reel, m)
    for local, rel in plan:
        print(f"  ✓ {rel}  {os.path.getsize(local)} B")
    print(f"uploaded + verified → {r}")


def kv(pairs):
    """key=value strings -> dict with numbers parsed ("72%" -> 72.0, "1,234" -> 1234)."""
    out = {}
    for s in pairs or []:
        if "=" not in s:
            sys.exit(f"expected key=value, got '{s}'")
        k, v = s.split("=", 1)
        x = v.strip().replace(",", "").rstrip("%")
        try:
            out[k.strip()] = int(x) if x.lstrip("-").isdigit() else float(x)
        except ValueError:
            out[k.strip()] = None if v.strip().lower() in ("", "na", "n/a", "none") else v.strip()
    return out


def cmd_features(a):
    m = load(a.reel); m.setdefault("features", {}).update(kv(a.pairs)); save(a.reel, m)
    print(json.dumps(m["features"], indent=1))


def cmd_posted(a):
    m = load(a.reel); posts = m.setdefault("posts", {})
    at = a.at or now()
    if a.ig: posts["ig"] = {"url": a.ig, "posted_at": at}
    if a.yt: posts["yt"] = {"url": a.yt, "posted_at": at}
    if not (a.ig or a.yt): sys.exit("give --ig and/or --yt")
    save(a.reel, m); print(json.dumps(posts, indent=1))


def verdict(platform, s):
    if platform == "yt":
        bad = [f"{k} {s.get(k)} < {v}" for k, v in TARGETS["yt"].items() if isinstance(s.get(k), (int, float)) and s[k] < v]
        miss = [k for k in TARGETS["yt"] if not isinstance(s.get(k), (int, float))]
    else:
        ss = (s.get("shares") or 0) + (s.get("saves") or 0) if any(isinstance(s.get(k), (int, float)) for k in ("shares", "saves")) else None
        bad = [f"shares+saves {ss} < 5"] if ss is not None and ss < TARGETS["ig"]["shares_saves"] else []
        miss = [] if ss is not None else ["shares/saves"]
    return ("below target: " + "; ".join(bad)) if bad else ("target not checkable: " + ", ".join(miss)) if miss else "on target"


def cmd_stats(a):
    m = load(a.reel)
    s = json.load(open(a.json)) if a.json else {}
    s.update(kv(a.pairs)); s["captured_at"] = now()
    m.setdefault("stats", {}).setdefault(a.platform, {})[a.window] = s
    save(a.reel, m)
    v = verdict(a.platform, s) if a.window == "48h" else "—"
    new = not os.path.exists(STATS_LOG)
    with open(STATS_LOG, "a", encoding="utf-8") as f:
        if new:
            f.write("# Stats log — one row per reel × platform × window (pipeline.py stats). Read by channel_report.py.\n\n"
                    "| captured | reel | platform | window | views | stayed % | avg viewed % | avg view s | likes | comments | shares | saves | follows/subs | verdict |\n"
                    "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|\n")
        g = lambda k: "" if s.get(k) is None else str(s.get(k))
        f.write(f"| {s['captured_at'][:16]} | {a.reel} | {a.platform} | {a.window} | {g('views')} | {g('stayed_pct')} | {g('avg_viewed_pct')} | "
                f"{g('avg_view_s')} | {g('likes')} | {g('comments')} | {g('shares')} | {g('saves')} | {g('follows') or g('subs_gained')} | {v} |\n")
    print(f"{a.reel} {a.platform} {a.window}: {v}")


def cmd_channel(a):
    s = json.load(open(a.json)) if a.json else {}
    s.update(kv(a.pairs)); s.update(platform=a.platform, captured_at=now())
    log = json.load(open(CHANNEL_LOG)) if os.path.exists(CHANNEL_LOG) else []
    log.append(s); json.dump(log, open(CHANNEL_LOG, "w"), indent=1)
    prev = [x for x in log[:-1] if x.get("platform") == a.platform]
    key = "followers" if a.platform == "ig" else "subscribers"
    if prev and isinstance(s.get(key), (int, float)) and isinstance(prev[-1].get(key), (int, float)):
        print(f"{a.platform} {key}: {s[key]} ({s[key] - prev[-1][key]:+d} since {prev[-1]['captured_at'][:10]})")
    else:
        print(f"{a.platform} snapshot saved")


def cmd_due(a):
    t0 = datetime.datetime.now().astimezone()
    rows = []
    for mp in sorted(glob.glob(os.path.join(REELS, "*", "pipeline.json"))):
        m = json.load(open(mp))
        for pf, post in (m.get("posts") or {}).items():
            try:
                age = (t0 - datetime.datetime.fromisoformat(post["posted_at"])).total_seconds() / 3600
            except (KeyError, ValueError):
                continue
            have = (m.get("stats") or {}).get(pf, {})
            for w, hrs in (("48h", 48), ("7d", 168)):
                if age >= hrs and w not in have:
                    rows.append((m["reel_name"], pf, w, post["url"], round(age)))
    if not rows:
        print("nothing due"); return
    for r in rows:
        print(f"{r[0]:40} {r[1]:3} {r[2]:4} posted {r[4]} h ago  {r[3]}")


ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
sub = ap.add_subparsers(dest="cmd", required=True)
p = sub.add_parser("init"); p.add_argument("reel"); p.add_argument("--topic"); p.add_argument("--playbook"); p.add_argument("--carousel"); p.set_defaults(fn=cmd_init)
p = sub.add_parser("set"); p.add_argument("reel"); p.add_argument("stage"); p.add_argument("status", choices=["pending", "running", "done", "failed", "waiting"]); p.add_argument("--note"); p.set_defaults(fn=cmd_set)
p = sub.add_parser("file"); p.add_argument("reel"); p.add_argument("key"); p.add_argument("path"); p.set_defaults(fn=cmd_file)
p = sub.add_parser("approve"); p.add_argument("reel"); p.add_argument("checkpoint", choices=["checkpoint1", "checkpoint2"]); p.set_defaults(fn=cmd_approve)
p = sub.add_parser("status"); p.add_argument("reel", nargs="?"); p.set_defaults(fn=cmd_status)
p = sub.add_parser("next"); p.add_argument("reel"); p.set_defaults(fn=cmd_next)
p = sub.add_parser("locked"); p.add_argument("kind", choices=list(LIMITS)); p.add_argument("command", nargs=argparse.REMAINDER); p.set_defaults(fn=cmd_locked)
p = sub.add_parser("footage"); p.add_argument("reel"); p.add_argument("--file"); p.add_argument("--dry-run", action="store_true"); p.set_defaults(fn=cmd_footage)
p = sub.add_parser("upload"); p.add_argument("reel"); p.add_argument("half", choices=["half1", "half2"]); p.set_defaults(fn=cmd_upload)
p = sub.add_parser("features"); p.add_argument("reel"); p.add_argument("pairs", nargs="*"); p.set_defaults(fn=cmd_features)
p = sub.add_parser("posted"); p.add_argument("reel"); p.add_argument("--ig"); p.add_argument("--yt"); p.add_argument("--at"); p.set_defaults(fn=cmd_posted)
p = sub.add_parser("stats"); p.add_argument("reel"); p.add_argument("platform", choices=["ig", "yt"]); p.add_argument("--window", choices=["48h", "7d"], required=True); p.add_argument("--json"); p.add_argument("pairs", nargs="*"); p.set_defaults(fn=cmd_stats)
p = sub.add_parser("channel"); p.add_argument("platform", choices=["ig", "yt"]); p.add_argument("--json"); p.add_argument("pairs", nargs="*"); p.set_defaults(fn=cmd_channel)
p = sub.add_parser("due"); p.set_defaults(fn=cmd_due)
a = ap.parse_args()
if a.cmd == "locked":
    a.command = a.command[1:] if a.command[:1] == ["--"] else a.command
    if not a.command: sys.exit("usage: pipeline.py locked render -- <command ...>")
a.fn(a)
