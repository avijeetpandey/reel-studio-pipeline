#!/usr/bin/env python3
"""compose.py — turn an edit plan into a complete, renderable HyperFrames reel (no hand-coded index.html).

  python3 -I compose.py <edit_plan.json> <project dir containing assets/>  [--graphics g.html --graphics-js g.js --graphics-css g.css --overlay o.html]

The plan (written by autodirect.py, or edited by hand) carries every decision: words, joins, grade world, caption style, camera + effect list,
SFX list, music, hook, CTA. This script only assembles: footage + voice stem, captions, `fx.js` effects, SFX tags, music bed (carve with
carve.mjs afterwards), grain, progress bar, CTA card. A reel with no graphics is still a finished reel (captions + camera + sound + grade);
illustrations (sticker scenes) are optional and go in the `#stage` slot via --graphics / --graphics-js.

Plan keys (all optional except end, words):
  end, words (flat or islands [[text,start,end,tag?]]), caption {style: pop|serif|hero, y, accent, hero_until, size},
  hook {text, t0, t1}, fx [{fn, a:[...]}] sorted by time, sfx [{id,file,t,vol,ms}], music {file,vol,fade}, voice, video,
  cta {variant: follow|save|comment, t0, y, promise, answer, handle} — a dict, or a list (comment card for the question, then a follow card: each card ends when the next starts), progress {color}, grain (opacity), accent, bg
"""
import json, os, re, shutil, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
def _cfg():
    p = os.path.expanduser(os.environ.get("REEL_STUDIO_CONFIG", "~/.config/reel-studio/config.json"))
    try:
        return json.load(open(p))
    except Exception:
        return {}
CFG = _cfg()

T = os.path.dirname(HERE)
SFX_DIR = os.path.join(T, "composition", "assets", "audio", "sfx")
CTA = os.path.join(T, "composition", "components", "cta-card.html")
SFX_GROUP = ('<hf-audio-group id="sfx" data-label="SFX" data-volume="1" data-fx-chain="{&quot;version&quot;:1,&quot;nodes&quot;:[{&quot;type&quot;:&quot;highpass&quot;,&quot;id&quot;:&quot;s1&quot;,'
             '&quot;label&quot;:&quot;Keep SFX off the voice low end&quot;,&quot;params&quot;:{&quot;frequency&quot;:160,&quot;q&quot;:0.707,&quot;poles&quot;:&quot;2&quot;}},{&quot;type&quot;:&quot;reverb&quot;,'
             '&quot;id&quot;:&quot;s2&quot;,&quot;label&quot;:&quot;Shared room glue&quot;,&quot;params&quot;:{&quot;size&quot;:0.3,&quot;damping&quot;:0.6,&quot;wet&quot;:0.1,&quot;dry&quot;:1}}]}"></hf-audio-group>')


def sfx_path(name):
    """a bare name, 'mixkit/<file>', or a path; returns (abs path, name inside assets/audio/sfx/)"""
    for cand in (name, name + ".mp3", os.path.join(SFX_DIR, name), os.path.join(SFX_DIR, name + ".mp3")):
        if os.path.isfile(cand):
            return cand, os.path.relpath(cand, SFX_DIR) if cand.startswith(SFX_DIR) else os.path.basename(cand)
    raise SystemExit(f"SFX not found: {name}")


def dur(f):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f], capture_output=True, text=True).stdout.strip())


def main():
    plan = json.load(open(sys.argv[1], encoding="utf-8"))
    proj = os.path.abspath(sys.argv[2])
    gh = open(sys.argv[sys.argv.index("--graphics") + 1], encoding="utf-8").read() if "--graphics" in sys.argv else ""
    gj = open(sys.argv[sys.argv.index("--graphics-js") + 1], encoding="utf-8").read() if "--graphics-js" in sys.argv else ""
    gc = open(sys.argv[sys.argv.index("--graphics-css") + 1], encoding="utf-8").read() if "--graphics-css" in sys.argv else ""
    ov = open(sys.argv[sys.argv.index("--overlay") + 1], encoding="utf-8").read() if "--overlay" in sys.argv else ""   # static overlays outside the camera (CTA cards that carry their own animation)
    END = round(float(plan["end"]), 2)
    words = plan["words"]
    flat = [w for isl in words for w in isl] if words and isinstance(words[0][0], list) else words
    cap = {"style": "pop", "y": 1230, "accent": plan.get("accent", "#ffd23f"), "hero_until": 2.0, "size": 76}
    cap.update(plan.get("caption", {}))
    accent = plan.get("accent", cap["accent"])
    video = plan.get("video", "assets/main.mp4")
    voice = plan.get("voice", "assets/audio/voice.wav")
    music = plan.get("music")
    os.makedirs(os.path.join(proj, "assets", "audio", "sfx"), exist_ok=True)
    os.makedirs(os.path.join(proj, "assets", "img"), exist_ok=True)
    # grain tile (one shared texture)
    g = os.path.join(proj, "assets", "img", "grain.jpg")
    if not os.path.exists(g):
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "color=c=gray:s=1200x2100", "-vf", "noise=alls=46:allf=t+u,format=gray", "-frames:v", "1", g], check=True)
    av = os.path.join(proj, "assets", "img", "avatar.png")         # approved cartoon avatar for the CTA cards
    for cand in (os.path.join(T, "carousel", "assets", "avatar-cartoon.png"), os.path.join(T, "carousel", "assets", "avatar.png")):
        if not os.path.exists(av) and os.path.exists(cand):
            shutil.copy(cand, av)
    # voice stem from the cut
    vp = os.path.join(proj, voice)
    if not os.path.exists(vp):
        os.makedirs(os.path.dirname(vp), exist_ok=True)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", os.path.join(proj, video), "-vn", "-ac", "2", "-ar", "48000", vp], check=True)
    # SFX tags
    tags, tr = [], 40
    for s in plan.get("sfx", []):
        src, rel = sfx_path(s["file"])
        dst = os.path.join(proj, "assets", "audio", "sfx", rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        if not os.path.exists(dst):
            shutil.copy(src, dst)
        ms = float(s.get("ms", 0)); t = max(0.0, float(s["t"]))
        d = round(min(dur(src) - ms, END - t) - 0.01, 2)
        if d <= 0.03:
            continue
        m = f' data-media-start="{ms}"' if ms else ""
        tags.append(f'      <audio id="sfx-{s["id"]}" src="assets/audio/sfx/{rel}" data-start="{t:.2f}" data-duration="{d}"{m} data-track-index="{tr}" data-audio-group="sfx" data-volume="{round(min(float(s.get("vol", 0.25)), 1.0), 2)}"></audio>')
        tr += 1
    # CTA component pieces
    cta_css = cta_html = cta_js = cta_style = cta_calls = ""
    ctas = plan.get("cta") or []
    if isinstance(ctas, dict):
        ctas = [ctas]
    if ctas:
        raw = open(CTA, encoding="utf-8").read()
        cta_css = re.search(r"<style>(.*?)</style>", raw, re.S).group(1)
        cta_js = re.search(r"<script>(.*?)</script>", raw, re.S).group(1)
        base = raw[raw.index("</style>") + 8: raw.index("<!-- JS -->")]
        base = re.sub(r"<!--.*?-->", "", base, flags=re.S).strip()
        for i, c in enumerate(ctas):                      # e.g. a comment card for the question, then a follow card for the sign-off
            nxt = ctas[i + 1]["t0"] if i + 1 < len(ctas) else END
            cta_html += (f'<div id="g-cta{i}" class="clip" data-start="{c["t0"]}" data-duration="{round(nxt - c["t0"], 2)}" data-track-index="{15 + i}" data-role="cta" data-component="cta-card">'
                         + base.replace('id="cta"', f'id="cta{i}"') + '</div>')
            cta_style += f'      #g-cta{i} {{ position: absolute; inset: 0; pointer-events: none; }}\n      #g-cta{i} .cta {{ top: {c.get("y", 1010)}px; }}\n'
            cta_calls += "buildCtaCard(tl, " + json.dumps({"el": f"#cta{i}", "variant": c.get("variant", "follow"), "start": round(c["t0"] + 0.1, 2),
                         "promise": c.get("promise", CFG.get("promise", "one useful idea every day")), "answer": c.get("answer", "YES").replace(" ", "\u00a0"), "handle": c.get("handle", CFG.get("handle", "yourhandle")), "avatar": c.get("avatar") or "assets/img/avatar.png"}) + ");\n        "
    # music bed
    music_tag = ""
    if music:
        fade = float(music.get("fade", 0.28))
        auto = json.dumps({"version": 1, "lanes": [{"target": "volume", "points": [{"t": 0, "v": 1}, {"t": round(END - fade - 0.05, 2), "v": 1}, {"t": round(END - 0.03, 2), "v": 0}]}]}).replace('"', "&quot;")
        music_tag = (f'      <audio id="music" src="{music["file"]}" data-start="0" data-duration="{END}" data-track-index="31" data-audio-group="music" '
                     f'data-volume="{music.get("vol", 0.2)}" data-automation="{auto}"></audio>')
    hook = plan.get("hook")
    hook_html = ""
    if hook:
        hook_html = f'<div id="hook" class="clip" data-start="{hook.get("t0", 0)}" data-duration="{round(hook.get("t1", 0.6) - hook.get("t0", 0), 2)}" data-track-index="22" data-role="hook"><div class="hk">{hook["text"]}</div></div>'
    scene_cls = "pop"
    html = TEMPLATE
    rep = {
        "{{END}}": str(END), "{{ACCENT}}": accent, "{{BG}}": plan.get("bg", "#05070f"),
        "{{CAPY}}": str(cap["y"]), "{{CAPSIZE}}": str(cap["size"]), "{{GRAIN}}": str(plan.get("grain", 0.1)),
        "{{VIDEO}}": video, "{{VOICE}}": voice, "{{CTA_CSS}}": cta_css, "{{CTA_HTML}}": cta_html,
        "{{CTA_JS}}": cta_js, "{{HOOK}}": hook_html, "{{GRAPHICS}}": gh, "{{GRAPHICS_JS}}": gj, "{{GRAPHICS_CSS}}": gc, "{{OVERLAY}}": ov, "{{MUSIC}}": music_tag, "{{SFX_GROUP}}": SFX_GROUP if tags else "", "{{SFX}}": "\n".join(tags),
        "{{FXJS}}": open(os.path.join(HERE, "fx.js"), encoding="utf-8").read(),
        "{{WORDS}}": json.dumps(flat, ensure_ascii=False), "{{CAP}}": json.dumps(cap), "{{FX}}": json.dumps(plan.get("fx", [])),
        "{{CTA_CALL}}": cta_calls,
        "{{CTA_STYLE}}": cta_style,
        "{{PROGRESS}}": f'<div id="g-progress"><div id="pg-bar"></div></div>' if plan.get("progress", True) else "",
        "{{PROGRESS_JS}}": f'tl.fromTo("#pg-bar", {{ scaleX: 0 }}, {{ scaleX: 1, duration: {round(END - 0.1, 2)}, ease: "none", ...IM }}, 0);' if plan.get("progress", True) else "",
        "{{LEAK}}": '<div id="leak"></div>' if any(f.get("fn") == "leak" for f in plan.get("fx", [])) else '<div id="leak"></div>',
    }
    for k, v in rep.items():
        html = html.replace(k, v)
    open(os.path.join(proj, "index.html"), "w", encoding="utf-8").write(html)
    print(f"wrote {proj}/index.html — {len(flat)} words, {len(plan.get('fx', []))} fx, {len(tags)} sfx, end {END}s")


TEMPLATE = r"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
    <style>
      * { margin: 0; padding: 0; box-sizing: border-box; }
      html, body { margin: 0; width: 1080px; height: 1920px; overflow: hidden; background: {{BG}}; }
      :root { --accent: {{ACCENT}}; --avatar: none; }
      #root { position: relative; width: 100%; height: 100%; overflow: hidden; font-family: Montserrat, sans-serif; background: {{BG}}; }
      #world { position: absolute; inset: 0; overflow: hidden; }
      #cam { position: absolute; inset: 0; overflow: hidden; transform-origin: 50% 44%; }
      #bump { position: absolute; inset: 0; transform-origin: 50% 44%; }
      #a-roll { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; }
      #stage { position: absolute; inset: 0; transform-origin: 50% 44%; pointer-events: none; }
      #leak { position: absolute; inset: -60px; opacity: 0; mix-blend-mode: screen; pointer-events: none; }
      #captions, #hook { position: absolute; inset: 0; pointer-events: none; }
      /* captions: pop (default) · serif (warm, above the hair) · hero (giant opening words) */
      .cap { position: absolute; left: 70px; right: 70px; top: {{CAPY}}px; display: flex; justify-content: center; flex-wrap: nowrap; gap: 0 30px; opacity: 0; }
      .cw { display: inline-block; font-size: {{CAPSIZE}}px; font-weight: 900; line-height: 1.1; color: #fff; -webkit-text-stroke: 10px rgba(14, 16, 24, 0.92); paint-order: stroke fill; text-shadow: 0 6px 0 rgba(14, 16, 24, 0.3); white-space: nowrap; }
      .serif .cw { font-family: "Playfair Display", serif; font-weight: 600; font-size: 70px; -webkit-text-stroke: 0; text-shadow: 0 2px 22px rgba(0, 0, 0, 0.55); letter-spacing: 0.01em; }
      .serif .cw.em { font-style: italic; font-weight: 700; }
      .hero .cw { font-size: 150px; text-transform: uppercase; letter-spacing: -0.01em; -webkit-text-stroke: 14px rgba(14, 16, 24, 0.9); }
      .hk { position: absolute; left: 60px; right: 60px; top: 300px; text-align: center; font: 900 120px/1.02 Montserrat, sans-serif; color: #fff; -webkit-text-stroke: 14px rgba(14,16,24,.9); paint-order: stroke fill; text-transform: uppercase; }
      #grain { position: absolute; left: -60px; top: -60px; width: 1200px; height: 2100px; background: url(assets/img/grain.jpg) 0 0 / 1200px 2100px; mix-blend-mode: overlay; opacity: {{GRAIN}}; pointer-events: none; }
      #g-progress { position: absolute; left: 0; top: 0; width: 1080px; height: 8px; pointer-events: none; }
      #pg-bar { width: 100%; height: 8px; background: var(--accent); transform-origin: 0 50%; }
{{CTA_STYLE}}{{CTA_CSS}}
{{GRAPHICS_CSS}}
    </style>
  </head>
  <body>
    <svg width="0" height="0" style="position:absolute" aria-hidden="true">
      <defs>
        <filter id="mbH" x="-25%" y="-5%" width="150%" height="110%"><feGaussianBlur stdDeviation="0 0"/></filter>
        <filter id="mbV" x="-5%" y="-25%" width="110%" height="150%"><feGaussianBlur stdDeviation="0 0"/></filter>
        <filter id="rgb" color-interpolation-filters="sRGB">
          <feColorMatrix in="SourceGraphic" type="matrix" values="1 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 1 0" result="r"/>
          <feColorMatrix in="SourceGraphic" type="matrix" values="0 0 0 0 0  0 1 0 0 0  0 0 0 0 0  0 0 0 1 0" result="g"/>
          <feColorMatrix in="SourceGraphic" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 1 0 0  0 0 0 1 0" result="b"/>
          <feOffset in="r" id="rgbR" dx="0" dy="0" result="r2"/><feOffset in="b" id="rgbB" dx="0" dy="0" result="b2"/>
          <feBlend in="r2" in2="g" mode="screen" result="rg"/><feBlend in="rg" in2="b2" mode="screen"/>
        </filter>
      </defs>
    </svg>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{{END}}" data-width="1080" data-height="1920">
      <div id="world">
        <div id="cam"><div id="bump"><video id="a-roll" class="clip" src="{{VIDEO}}" data-start="0" data-duration="{{END}}" data-track-index="0" muted playsinline></video></div></div>
        <div id="stage" data-role="graphics">
{{GRAPHICS}}
        </div>
      </div>
      {{LEAK}}
      <div id="captions" class="clip" data-start="0" data-duration="{{END}}" data-track-index="20" data-role="caption"></div>
      {{HOOK}}
      {{CTA_HTML}}
{{OVERLAY}}
      <div id="grain"></div>
      {{PROGRESS}}

      <audio id="voice" src="{{VOICE}}" data-start="0" data-duration="{{END}}" data-track-index="30" data-audio-group="voiceover" data-volume="1"></audio>
{{MUSIC}}
      {{SFX_GROUP}}
{{SFX}}
    </div>
    <script>
{{CTA_JS}}
    </script>
    <script>
{{FXJS}}
    </script>
    <script>
      (function () {
        const tl = gsap.timeline({ paused: true });
        const IM = { immediateRender: false };
        const END = {{END}};
        const WORDS = {{WORDS}};
        const CAP = {{CAP}};
        const COL = { r: "#ff5470", y: CAP.accent, g: "#2de2a6" };
        const WEAK = /^(a|an|the|to|of|and|or|but|in|on|at|for|is|it|ka|ke|ki|se|ko|na|ek|hi|ye|toh|mein|pe|par|hai|aur|ho|tum|ya|bhi)$/i;
        const bare = (t) => t.replace(/[.,?!;:"“”]/g, "");
        const fx = makeFX(tl, { end: END });

        /* ---------- captions ---------- */
        const chunks = [];
        let cur = [];
        WORDS.forEach((w, i) => {
          cur.push(w);
          const punct = /[.,?!]$/.test(w[0]), last = i === WORDS.length - 1;
          const chars = cur.reduce((a, x) => a + bare(x[0]).length, 0);
          const hero = CAP.style === "hero" && w[1] < CAP.hero_until;
          const weakEnd = !punct && !last && WEAK.test(bare(w[0])) && chars < 11;
          const maxw = hero ? 1 : CAP.style === "serif" ? 3 : 2;
          if (!weakEnd && (punct || cur.length >= maxw || chars >= (hero ? 8 : 14) || last)) { chunks.push(cur); cur = []; }
        });
        const capRoot = document.getElementById("captions");
        chunks.forEach((c, ci) => {
          const el = document.createElement("div");
          const isHero = CAP.style === "hero" && c[0][1] < CAP.hero_until;
          el.className = "cap" + (CAP.style === "serif" ? " serif" : isHero ? " hero" : "");
          el.id = "cap-" + ci;
          if (isHero) el.style.top = "430px";
          c.forEach((w, wi) => {
            const s = document.createElement("span");
            s.className = "cw" + (CAP.style === "serif" && w[3] ? " em" : "");
            s.id = "cap-" + ci + "-" + wi;
            s.textContent = bare(w[0]);
            el.appendChild(s);
          });
          capRoot.appendChild(el);
          const start = Math.max(0.02, c[0][1] - 0.04), next = chunks[ci + 1];
          const end = next ? Math.max(start + 0.2, next[0][1] - 0.04) : END;
          tl.fromTo(el, { opacity: 0, y: isHero ? 0 : 10, scale: isHero ? 1.12 : 0.95 }, { opacity: 1, y: 0, scale: 1, duration: isHero ? 0.1 : 0.12, ease: "power2.out", ...IM }, start);
          tl.set(el, { opacity: 0 }, end);
          c.forEach((w, wi) => {
            const hot = w[3] ? COL[w[3]] || CAP.accent : isHero ? "#fff" : "#ffffff";
            tl.fromTo("#cap-" + ci + "-" + wi, { color: "#ffffff", scale: 1 }, { color: hot, scale: 1.08, duration: 0.08, ease: "power1.out", ...IM }, w[1]);
            tl.to("#cap-" + ci + "-" + wi, { scale: 1, duration: 0.1 }, w[2]);
          });
        });

        /* ---------- effects from the plan (camera track, whips, shrinks, leaks, shakes…) in time order ---------- */
        {{FX}}.forEach((e) => fx[e.fn](...e.a));
        {{PROGRESS_JS}}
        fx.grain(END);
        {{CTA_CALL}}
{{GRAPHICS_JS}}
        window.__timelines = window.__timelines || {};
        window.__timelines["main"] = tl;
        tl.seek(0);
      })();
    </script>
  </body>
</html>
"""

if __name__ == "__main__":
    main()
