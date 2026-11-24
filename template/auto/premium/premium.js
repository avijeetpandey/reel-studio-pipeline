/* premium.js — reusable "premium edit" components for a talking-head reel (HyperFrames + GSAP). Round 14, 22 Nov 2026.
 * Study: research/refs_<date>/REPORT.md (eightsenses "Kinetic Text Reels": word behind the head, two-tier captions, glass ribbon,
 * light frosted cards with real content, zoom-blur / streak transitions, riser -> impact sound per scene change).
 * Everything is DATA-DRIVEN from plan.premium (written by premium.py; editable in work/beats.json) — no per-reel drawing.
 * Seek-safe: only fromTo/set with immediateRender:false; text typing via onUpdate from a tweened counter.
 *
 *   makePremium(tl, P, { end, words })
 *     P.theme            {accent, word, glow, ...}   (CSS vars are written by compose.py; JS only needs timings)
 *     P.room             {t0, t1, amt}               room tint/vignette behind the person (person stays untouched: it is the cut-out above)
 *     P.depth            {ribbon: bool, orbs: n}     glass ribbon (back half behind the head, front half across the chest) + glossy orbs
 *     P.behind           [{t0, t1, text, style: serif|chrome|outline, kick, y, size}]   big word between room and person
 *     P.tier             {y, keys: [[t0, t1]]}       two-tier captions built from WORDS phrase marks ("/")
 *     P.cards            [{kind: search|checklist|nodes|slider|counter|load|dm, t0, t1, y, ...}]
 *     P.trans            [{t, type: zoomBlur|shake3d|streak}] extra transitions (whip/blurIn/shrink stay in fx.js)
 */
function makePremium(tl, P, o) {
  const IM = { immediateRender: false };
  const END = o.end;
  const $ = (s) => document.querySelector(s);
  const mk = (tag, cls, parent, html) => { const e = document.createElement(tag); if (cls) e.className = cls; if (html != null) e.innerHTML = html; (parent || document.body).appendChild(e); return e; };
  const esc = (t) => String(t).replace(/&/g, "&amp;").replace(/</g, "&lt;");
  // settle-in (the creator §8: "settle, don't pop") — blur + small travel, power3.out
  const inn = (el, t, d) => tl.fromTo(el, { opacity: 0, y: (d && d.dy) || 26, filter: "blur(12px)", scale: (d && d.s) || 1 }, { opacity: 1, y: 0, filter: "blur(0px)", scale: 1, duration: (d && d.dur) || 0.42, ease: "power3.out", ...IM }, t);
  const out = (el, t, d) => tl.fromTo(el, { opacity: 1, filter: "blur(0px)" }, { opacity: 0, filter: "blur(10px)", y: (d && d.dy) || -12, duration: 0.26, ease: "power2.in", ...IM }, t);
  const api = {};
  // discrete states (class swaps, text swaps) that must also undo on a backwards seek: applied from tl.time() on every update
  const DISC = [];
  const disc = (t, el, on, off) => { el = typeof el === "string" ? $(el) : el; if (el) DISC.push({ t, el, on, off }); };
  const cls = (t, el, a, b) => disc(t, el, (x) => (x.className = a), (x) => (x.className = b));

  /* ---------- room tint + dots + orbs (behind the person) ---------- */
  const B = $("#behind");
  if (P.room && B) {
    const r = P.room;
    tl.fromTo("#room", { opacity: 0 }, { opacity: r.amt || 0.72, duration: 0.6, ease: "power2.out", ...IM }, r.t0 || 0);
    tl.fromTo("#dots", { opacity: 0 }, { opacity: 0.55, duration: 0.8, ease: "power2.out", ...IM }, (r.t0 || 0) + 0.2);
  }
  if (P.depth && P.depth.orbs && B) {
    const spots = [[110, 470, 54], [975, 395, 40], [1000, 1180, 62], [70, 1290, 46], [900, 300, 26]].slice(0, P.depth.orbs);
    spots.forEach(([x, y, r], i) => {
      const e = mk("div", "orb", B); e.style.cssText = `left:${x - r}px;top:${y - r}px;width:${2 * r}px;height:${2 * r}px`;
      tl.fromTo(e, { opacity: 0, scale: 0.6 }, { opacity: 0.9, scale: 1, duration: 0.7, ease: "power3.out", ...IM }, 0.3 + i * 0.12);
      tl.fromTo(e, { x: 0, y: 0 }, { x: (i % 2 ? -1 : 1) * 26, y: (i % 3 - 1) * 34, duration: END, ease: "sine.inOut", ...IM }, 0);
    });
  }
  /* glass ribbon: one S-curve band; the back half lives in #behind (passes behind the head), the front half in #ribbonF (crosses the chest) */
  if (P.depth && P.depth.ribbon) {
    const hy = P.layout.hair;                                  // hair top in canvas px
    const back = `M -80 ${hy + 330} C 160 ${hy - 80}, 520 ${hy - 260}, 760 ${hy - 120} S 1120 ${hy + 60}, 1180 ${hy - 60}`;
    const front = `M -80 ${hy + 760} C 240 ${hy + 600}, 620 ${hy + 760}, 1180 ${hy + 560}`;
    const band = (svgSel, d, id) => {
      const svg = $(svgSel); if (!svg) return;
      svg.innerHTML += `<defs><linearGradient id="rg${id}" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="var(--p-rib1)" stop-opacity="0"/><stop offset=".25" stop-color="var(--p-rib1)"/><stop offset=".6" stop-color="var(--p-rib2)"/><stop offset="1" stop-color="var(--p-rib1)" stop-opacity=".2"/></linearGradient></defs>
        <path id="rb${id}" d="${d}" fill="none" stroke="url(#rg${id})" stroke-width="96" stroke-linecap="round" opacity=".55"/>
        <path id="rh${id}" d="${d}" fill="none" stroke="rgba(255,255,255,.85)" stroke-width="6" stroke-linecap="round" transform="translate(0,-30)"/>`;
      ["#rb" + id, "#rh" + id].forEach((s, k) => {
        const p = $(s), L = p.getTotalLength(); p.style.strokeDasharray = L;
        tl.fromTo(s, { strokeDashoffset: L }, { strokeDashoffset: 0, duration: 1.1, ease: "power2.inOut", ...IM }, (P.depth.t0 || 0.35) + k * 0.06 + (id === "F" ? 0.25 : 0));
      });
      tl.fromTo(svgSel, { y: 0, rotation: 0 }, { y: -18, rotation: 1.2, duration: END, ease: "sine.inOut", ...IM }, 0);
    };
    band("#ribbonB", back, "B");
    if (P.depth.front) band("#ribbonF svg", front, "F");   // 22 Nov 2026 test: a band across the chest covers his hands -> off unless asked
  }

  /* ---------- word behind the head ---------- */
  const WB = $("#wb");
  (P.behind || []).forEach((w, i) => {
    const e = mk("div", "wb " + (w.style || "serif"), WB, (w.kick ? `<span class="kick">${esc(w.kick)}</span>` : "") + esc(w.text));
    e.style.top = w.y + "px"; e.style.fontSize = w.size + "px";
    if (w.style === "block") {           // energetic: slams in from big + motion blur, lands with a camera bump, drifts, snaps out
      if (P.glow) { const gl = mk("div", "wglow", WB); gl.style.top = (w.y - 250) + "px";
        tl.fromTo(gl, { opacity: 0, scale: 0.7 }, { opacity: 1, scale: 1, duration: 0.3, ease: "power2.out", ...IM }, w.t0);
        tl.fromTo(gl, { opacity: 1 }, { opacity: 0, duration: 0.2, ...IM }, w.t1 - 0.2); }
      tl.fromTo(e, { opacity: 0, scale: 1.55, y: -30, filter: "blur(14px)" }, { opacity: 1, scale: 1, y: 0, filter: "blur(0px)", duration: 0.2, ease: "power4.out", ...IM }, w.t0);
      tl.fromTo("#bump", { scale: 1 }, { scale: 1.045, duration: 0.06, ease: "power2.out", ...IM }, w.t0 + 0.16);
      tl.fromTo("#bump", { scale: 1.045 }, { scale: 1, duration: 0.28, ease: "power2.out", ...IM }, w.t0 + 0.22);
      tl.fromTo(e, { scale: 1 }, { scale: 1.06, duration: Math.max(0.3, w.t1 - w.t0 - 0.4), ease: "none", ...IM }, w.t0 + 0.2);
      tl.fromTo(e, { opacity: 1 }, { opacity: 0, scale: 1.14, filter: "blur(10px)", duration: 0.16, ease: "power2.in", ...IM }, w.t1 - 0.16);
      return;
    }
    tl.fromTo(e, { opacity: 0, y: 46, scale: 1.08, filter: "blur(18px)" }, { opacity: 1, y: 0, scale: 1, filter: "blur(0px)", duration: 0.48, ease: "power3.out", ...IM }, w.t0);
    tl.fromTo(e, { scale: 1 }, { scale: 1.045, duration: Math.max(0.3, w.t1 - w.t0 - 0.5), ease: "none", ...IM }, w.t0 + 0.48);
    tl.fromTo(e, { opacity: 1, filter: "blur(0px)" }, { opacity: 0, filter: "blur(16px)", y: -24, duration: 0.3, ease: "power2.in", ...IM }, w.t1 - 0.3);
  });

  (P.behind || []).forEach((w, i) => {
    if (!w.particles) return;
    const cv = mk("canvas", "pcv", WB); cv.width = 1080; cv.height = 900; cv.style.top = (w.y - 300) + "px";
    const g = cv.getContext("2d"), off = document.createElement("canvas"); off.width = 1080; off.height = 900;
    const og = off.getContext("2d"); og.fillStyle = "#fff"; og.textAlign = "center"; og.textBaseline = "alphabetic";
    og.font = (w.style === "serif" ? "italic 400 " : "400 ") + w.size + "px " + (w.style === "serif" ? "PSerif" : "PAnton");
    let pts = null, seed = 11;
    const rnd = () => ((seed = (seed * 16807) % 2147483647) / 2147483647);
    const build = () => { og.clearRect(0, 0, 1080, 900); og.fillText(w.style === "serif" ? w.text : w.text.toUpperCase(), 540, 300 + w.size * 0.8); const d = og.getImageData(0, 0, 1080, 900).data; pts = [];
      for (let y = 0; y < 900; y += 7) for (let x = 0; x < 1080; x += 7) if (d[(y * 1080 + x) * 4 + 3] > 128) pts.push([x, y, rnd() * 1080, rnd() * 900, rnd()]); };
    const st = { p: 0 }, col = getComputedStyle(document.documentElement).getPropertyValue("--p-word") || "#fff";
    const draw = () => { if (!pts) build(); g.clearRect(0, 0, 1080, 900); g.fillStyle = col; const k = st.p;
      pts.forEach(([x, y, sx, sy, r]) => { const e2 = Math.min(1, Math.max(0, (k - r * 0.35) / 0.65)), q = 1 - Math.pow(1 - e2, 3); g.globalAlpha = 0.25 + 0.75 * q; g.fillRect(sx + (x - sx) * q, sy + (y - sy) * q, 3.2, 3.2); }); };
    tl.fromTo(st, { p: 0 }, { p: 1, duration: 0.9, ease: "none", ...IM, onUpdate: draw }, w.t0 - 0.5);
    tl.fromTo(cv, { opacity: 1 }, { opacity: 0, duration: 0.25, ...IM }, w.t0 + 0.42);
    tl.set(cv, { opacity: 0 }, w.t0 - 0.51);
    tl.fromTo(cv, { opacity: 0 }, { opacity: 1, duration: 0.05, ...IM }, w.t0 - 0.5);
  });

  /* ---------- two-tier captions ---------- */
  if (P.tier) {
    const root = $("#tier");
    const W = o.words, bare = (t) => t.replace(/(?<!\d),|,(?!\d)|[.?!;:"“”]/g, "");
    const phrases = []; let cur = [];
    W.forEach((w, i) => { cur.push(w); if (w[4] === "/" || i === W.length - 1 || cur.length >= 4) { phrases.push(cur); cur = []; } });
    const keyAt = (t) => (P.tier.keys || []).find((k) => t >= k[0] - 0.05 && t < k[1]);
    const skip = (t) => (P.tier.skip || []).some((r) => t >= r[0] && t < r[1]);
    const norm = (x) => String(x || "").toLowerCase().replace(/[^a-z0-9%]+/g, " ").trim();
    const shown = (ph) => (P.behind || []).some((b) => ph[0][1] < b.t1 && ph[ph.length - 1][2] > b.t0 && norm((b.kick || "") + " " + b.text).includes(norm(ph.map((w) => w[0]).join(" "))));
    const rowFor = (t) => { const b = (P.behind || []).find((x) => t >= x.t0 - 0.1 && t < x.t1); return b ? Math.min(P.tier.y, b.y - 230 - (b.kick ? 60 : 0)) : P.tier.y; };
    const onWord = (w) => (P.behind || []).some((b) => w[1] < b.t1 && w[2] > b.t0 && norm(b.text).split(" ").includes(norm(w[0])));   // never caption the word that is already huge behind the head
    let prevPill = null;
    phrases.forEach((ph, pi) => {
      const t0 = Math.max(0.02, ph[0][1] - 0.04), nxt = phrases[pi + 1], t1 = nxt ? Math.max(t0 + 0.2, nxt[0][1] - 0.04) : END;
      if (skip(ph[0][1]) || shown(ph)) { prevPill = null; return; }
      const isHero = ph.some((w) => keyAt(w[1]) || (w[3] && w[3] !== ""));
      const box = mk("div", "tc", root); box.style.top = Math.max(285, rowFor(ph[0][1])) + "px";
      if (isHero) {
        const html = ph.filter((w) => !onWord(w)).map((w) => (keyAt(w[1]) || w[3]) ? `<em>${esc(bare(w[0]))}</em>` : esc(bare(w[0]))).join(" ");
        if (prevPill) { const p = mk("div", "pill", box, esc(prevPill.text)); tl.fromTo(p, { opacity: 1 }, { opacity: 1, duration: 0.01, ...IM }, t0); tl.set(p, { opacity: 0 }, t1); }
        const h = mk("div", "hero", box, html);
        tl.fromTo(h, { opacity: 0, y: 16, filter: "blur(14px)" }, { opacity: 1, y: 0, filter: "blur(0px)", duration: 0.3, ease: "power3.out", ...IM }, t0);
        tl.set(h, { opacity: 0 }, t1);
        prevPill = null;
      } else {
        const text = ph.filter((w) => !onWord(w)).map((w) => bare(w[0])).join(" ");
        if (!text.trim()) { prevPill = null; return; }
        const p = mk("div", "pill", box, esc(text));
        tl.fromTo(p, { opacity: 0, y: 10, scale: 0.96, filter: "blur(6px)" }, { opacity: 1, y: 0, scale: 1, filter: "blur(0px)", duration: 0.22, ease: "power3.out", ...IM }, t0);
        tl.set(p, { opacity: 0 }, t1);
        prevPill = { text };
      }
    });
  }

  /* ---------- cards ---------- */
  const CR = $("#cards");
  const typeInto = (el, text, t, cps) => {
    const st = { n: 0 }, dur = Math.max(0.25, text.length / (cps || 18));
    tl.fromTo(st, { n: 0 }, { n: text.length, duration: dur, ease: "none", ...IM, onUpdate() { el.textContent = text.slice(0, Math.round(st.n)); } }, t);
    return dur;
  };
  const K = {};
  K.search = (c, e) => {
    e.classList.add("search");
    e.innerHTML = `<div class="sb"><div class="mg"><svg width="30" height="30" viewBox="0 0 24 24"><circle cx="10" cy="10" r="6.5" stroke="#fff" stroke-width="3" fill="none"/><path d="M15 15l6 6" stroke="#fff" stroke-width="3" stroke-linecap="round"/></svg></div><span class="q"></span><i class="caret"></i></div>` +
      (c.result ? `<div class="sres"><span class="arrow">→</span><span>${esc(c.result)}</span></div>` : "");
    const d = typeInto(e.querySelector(".q"), c.query, c.t0 + 0.35, c.cps);
    for (let k = 0; k < Math.ceil((c.t1 - c.t0) / 0.5); k++) tl.fromTo(e.querySelector(".caret"), { opacity: 1 }, { opacity: 0, duration: 0.01, ...IM }, c.t0 + k * 0.5 + 0.25);
    if (c.result) inn(e.querySelector(".sres"), c.t_result || c.t0 + 0.45 + d, { dy: 12, dur: 0.3 });
  };
  K.checklist = (c, e) => {
    e.innerHTML = (c.title ? `<div class="ttl">${c.title}</div>` : "") + c.items.map((it, i) => `<div class="row"><span class="ic ${it.ok === false ? "no" : ""}">${it.ok === false ? "✕" : ""}</span><span>${esc(it.text)}</span>${it.val ? `<span class="val">${esc(it.val)}</span>` : ""}</div>`).join("");
    const rows = e.querySelectorAll(".row");
    c.items.forEach((it, i) => {
      const t = it.t || c.t0 + 0.35 + i * 0.45, ic = rows[i].querySelector(".ic");
      inn(rows[i], t, { dy: 14, dur: 0.3 });
      if (it.ok !== false) { tl.fromTo(ic, { scale: 0.6 }, { scale: 1, duration: 0.25, ease: "back.out(2)", ...IM }, t + 0.15); disc(t + 0.15, ic, (x) => { x.className = "ic ok"; x.textContent = "✓"; }, (x) => { x.className = "ic"; x.textContent = ""; }); }
    });
  };
  K.nodes = (c, e) => {
    e.classList.add("nodes");
    const n = c.items.length, xs = c.items.map((_, i) => 480 + (i - (n - 1) / 2) * (n > 3 ? 250 : 300));
    e.style.height = "220px";
    const LN = [], ND = [];
    for (let i = 0; i < n - 1; i++) { const l = mk("div", "nline", e); l.style.left = xs[i] + 64 + "px"; l.style.width = xs[i + 1] - xs[i] - 128 + "px"; LN.push(l); }
    c.items.forEach((it, i) => { const d = mk("div", "nd", e, '<div class="c">' + esc(it.icon || it.text[0]) + '</div>' + ((it.icon || "").toLowerCase() === it.text.toLowerCase() ? "" : '<div class="l">' + esc(it.text) + "</div>")); d.style.left = xs[i] + "px"; ND.push(d); });
    const pk = mk("div", "npk", e);
    c.items.forEach((it, i) => {
      const t = it.t || c.t0 + 0.2 + i * 0.6;
      inn(ND[i], t, { dy: 18, dur: 0.34, s: 0.9 });
      const tn2 = i < n - 1 ? (c.items[i + 1].t || c.t0 + 0.2 + (i + 1) * 0.6) + 0.2 : 1e9;
      disc(t + 0.2, ND[i], (x) => (x.className = tl.time() < tn2 ? "nd on" : "nd"), (x) => (x.className = "nd"));
      if (i < n - 1) {
        const tn = c.items[i + 1].t || c.t0 + 0.2 + (i + 1) * 0.6;
        tl.fromTo(LN[i], { scaleX: 0 }, { scaleX: 1, duration: Math.max(0.2, tn - t - 0.1), ease: "power2.inOut", ...IM }, t + 0.05);
        tl.fromTo(pk, { left: xs[i] + 64, opacity: 1 }, { left: xs[i + 1] - 64, opacity: 1, duration: Math.max(0.2, tn - t - 0.1), ease: "power1.inOut", ...IM }, t + 0.05);
      }
    });
    tl.set(pk, { opacity: 0 }, (c.items[n - 1].t || c.t0 + 0.2 + (n - 1) * 0.6));
  };
  K.slider = (c, e) => {
    const n = c.items.length, xs = c.items.map((_, i) => 100 + (i / (n - 1)) * 488);
    e.innerHTML = (c.title ? `<div class="ttl">${c.title}</div>` : "") + `<div class="sl"><div class="track"></div>` +
      c.items.map((it, i) => `<div class="stop" style="left:${xs[i]}px"></div><div class="lab" style="left:${xs[i]}px">${esc(it)}</div>`).join("") + `<div class="knob" style="left:${xs[0]}px"></div></div>`;
    const kn = e.querySelector(".knob"), pick = c.pick == null ? n - 1 : c.pick;
    let t = c.t0 + 0.5; const path = [0, n - 1, pick].filter((v, i, a) => i === 0 || v !== a[i - 1]);
    path.forEach((p, i) => { if (!i) return; tl.fromTo(kn, { left: xs[path[i - 1]] }, { left: xs[p], duration: 0.45, ease: "power3.inOut", ...IM }, t); t += 0.6; });
    tl.fromTo(e.querySelectorAll(".lab")[pick], { color: "#5c5870", scale: 1 }, { color: "#14121f", scale: 1.12, duration: 0.2, ...IM }, t - 0.15);
  };
  K.counter = (c, e) => {
    e.classList.add("count");
    e.innerHTML = `<div class="cnum">${esc(c.prefix || "")}<span>0</span>${esc(c.suffix || "")}</div><div class="clab">${esc(c.label || "")}</div>`;
    const sp = e.querySelector(".cnum span"), st = { v: c.from || 0 };
    tl.fromTo(st, { v: c.from || 0 }, { v: c.to, duration: c.dur || 0.9, ease: "power2.out", ...IM, onUpdate() { sp.textContent = Math.round(st.v).toLocaleString("en-IN"); } }, c.t0 + 0.25);
  };
  K.load = (c, e) => {
    e.innerHTML = (c.title ? `<div class="ttl">${c.title}</div>` : "") + `<div class="ldb"><i></i></div><div class="ldr"><span>${esc(c.label || "")}</span><span class="pct">0%</span></div>`;
    const st = { v: 0 }, pc = e.querySelector(".pct");
    tl.fromTo(e.querySelector(".ldb i"), { scaleX: 0 }, { scaleX: 1, duration: c.dur || 1.2, ease: "power2.inOut", ...IM }, c.t0 + 0.3);
    tl.fromTo(st, { v: 0 }, { v: 100, duration: c.dur || 1.2, ease: "power2.inOut", ...IM, onUpdate() { pc.textContent = Math.round(st.v) + "%"; } }, c.t0 + 0.3);
    disc(c.t0 + 0.32 + (c.dur || 1.2), pc, (x) => (x.textContent = "✓ " + (c.done || "Done")), () => {});
  };
  K.dm = (c, e) => {
    e.classList.add("dm");
    e.innerHTML = `<div class="dmh"><span class="av"></span><span>@${esc(c.handle || "yourhandle")}</span></div><div class="dmq">${esc(c.question)}</div>` +
      `<div class="dmc">${c.options.map((x, i) => '<span class="ch">' + (c.icons && c.icons[i] ? '<svg viewBox="0 0 24 24" width="40" height="40" style="vertical-align:-8px;margin-right:12px"><path d="' + c.icons[i].d + '" fill="#' + c.icons[i].hex + '"/></svg>' : "") + esc(x) + "</span>").join("")}</div>`;
    const chips = e.querySelectorAll(".ch"), pick = c.pick == null ? 0 : c.pick;
    chips.forEach((ch, i) => inn(ch, c.t0 + 0.35 + i * 0.12, { dy: 12, dur: 0.28 }));
    const tp = c.t_tap || c.t0 + 1.4, tap = mk("div", "tap", e);
    const r = { x: 30 + (pick + 0.5) * (760 / chips.length), y: 300 };
    tap.style.left = r.x + "px"; tap.style.top = r.y + "px";
    tl.fromTo(tap, { opacity: 0.9, scale: 0.4 }, { opacity: 0, scale: 1.6, duration: 0.45, ease: "power2.out", ...IM }, tp);
    cls(tp + 0.05, chips[pick], "ch pick", "ch");
  };
  K.logos = (c, e) => {                      // brand badges that pop in a row (simple-icons paths resolved by premium.py)
    e.classList.add("logos");
    e.innerHTML = (c.title ? `<div class="ttl">${c.title}</div>` : "") + '<div class="lg">' + c.items.map((it) => '<div class="lb"><svg viewBox="0 0 24 24"><path d="' + it.d + '" fill="#' + it.hex + '"/></svg><span>' + esc(it.label) + "</span></div>").join("") + "</div>";
    e.querySelectorAll(".lb").forEach((b, i) => tl.fromTo(b, { opacity: 0, y: 24, scale: 0.7 }, { opacity: 1, y: 0, scale: 1, duration: 0.36, ease: "back.out(1.7)", ...IM }, (c.items[i].t || c.t0 + 0.3 + i * 0.25)));
  };
  K.photos = (c, e) => {                     // the creator's own screenshots / b-roll stills fanned out (reels/<reel>/broll/)
    e.classList.add("photos");
    const n = c.items.length;
    c.items.forEach((src, i) => {
      const im = mk("img", "ph", e); im.src = src;
      const rot = (i - (n - 1) / 2) * 9, x = (i - (n - 1) / 2) * 190;
      tl.fromTo(im, { opacity: 0, x: 0, rotation: 0, y: 40, scale: 0.85 }, { opacity: 1, x, rotation: rot, y: Math.abs(rot) * 2, scale: 1, duration: 0.5, ease: "power3.out", ...IM }, c.t0 + 0.2 + i * 0.12);
    });
  };
  /* split: a themed panel fills the band above the head and holds a card (face stays 100 % visible below) */
  K.split = (c, e) => {
    e.classList.add("split");
    e.style.height = c.panel_h + "px";
    const inner = mk("div", "pc", e); inner.style.top = Math.round((c.panel_h + 285) / 2 - 115) + "px";   // content below the IG top UI zone, panel above the caption row
    (K[c.inner.kind] || (() => {}))(Object.assign({}, c.inner, { t0: c.t0 + 0.2, t1: c.t1 }), inner);
    inn(inner, c.t0 + 0.15, { dy: 30, dur: 0.45 });
  };
  /* face-in-circle: the frame irises down to a circle around the face, ring + text on a circular path; the themed set fills the rest */
  K.circle = (c, e) => {
    e.classList.add("circle");
    const cx = 540, cy = c.cy, r = c.r || 330;
    e.innerHTML = `<svg viewBox="0 0 1080 1920" width="1080" height="1920"><defs><path id="cpath" d="M ${cx - r - 46} ${cy} a ${r + 46} ${r + 46} 0 1 1 ${2 * (r + 46)} 0"/></defs>` +
      `<circle cx="${cx}" cy="${cy}" r="${r + 14}" fill="none" stroke="var(--p-accent)" stroke-width="6" class="ring1"/>` +
      `<circle cx="${cx}" cy="${cy}" r="${r + 90}" fill="none" stroke="rgba(255,255,255,.35)" stroke-width="2" stroke-dasharray="6 14" class="ring2"/>` +
      `<text font-family="PSans" font-weight="700" font-size="40" fill="#fff" letter-spacing="3"><textPath href="#cpath" startOffset="50%" text-anchor="middle">${esc(c.text || "")}</textPath></text></svg>`;
    tl.fromTo("#splitBg", { opacity: 0 }, { opacity: 1, duration: 0.35, ...IM }, c.t0);
    tl.fromTo("#world", { clipPath: `circle(1400px at ${cx}px ${cy}px)` }, { clipPath: `circle(${r}px at ${cx}px ${cy}px)`, duration: 0.5, ease: "power3.inOut", ...IM }, c.t0);
    tl.fromTo("#world", { clipPath: `circle(${r}px at ${cx}px ${cy}px)` }, { clipPath: `circle(1400px at ${cx}px ${cy}px)`, duration: 0.45, ease: "power3.inOut", ...IM }, c.t1 - 0.45);
    tl.set("#world", { clipPath: "none" }, c.t1 + 0.01);
    tl.fromTo("#splitBg", { opacity: 1 }, { opacity: 0, duration: 0.3, ...IM }, c.t1 - 0.3);
    tl.fromTo(e.querySelector(".ring2"), { rotation: 0, svgOrigin: `${cx} ${cy}` }, { rotation: 40, svgOrigin: `${cx} ${cy}`, duration: c.t1 - c.t0, ease: "none", ...IM }, c.t0);
  };
  (P.cards || []).forEach((c, i) => {
    const e = mk("div", c.kind === "circle" || c.kind === "split" ? "full" : "pc", CR); e.id = "pc" + i; e.style.top = (c.kind === "circle" || c.kind === "split" ? 0 : c.y) + "px";
    (K[c.kind] || (() => {}))(c, e);
    const hh = e.offsetHeight;               // fit the card into its band (between the top UI zone and the caption row): never over the face
    if (c.h && hh > c.h && e.className.indexOf("full") < 0) e.style.zoom = (c.h / hh).toFixed(3);
    inn(e, c.t0, { dy: 30, dur: 0.45 });
    if (c.t1 < END - 0.05) out(e, c.t1 - 0.26);
  });

  /* ---------- transitions that live on top of fx.js ---------- */
  (P.trans || []).forEach((tr) => {
    const J = tr.t;
    if (tr.type === "zoomBlur") {           // push into the cut with zoom + blur + colour fringe, land from the overshoot
      tl.fromTo("#world", { scale: 1, filter: "blur(0px)" }, { scale: 1.22, filter: "blur(16px)", duration: 0.16, ease: "power2.in", ...IM }, J - 0.16);
      tl.set("#world", { filter: "url(#rgb) blur(10px)" }, J - 0.04);
      tl.fromTo("#world", { scale: 1.22, filter: "blur(14px)" }, { scale: 1, filter: "blur(0px)", duration: 0.28, ease: "power3.out", ...IM }, J);
      tl.set("#world", { filter: "none" }, J + 0.3);
    } else if (tr.type === "shake3d") {     // 3D-shake radial cut (realtor reel, 24 Nov study): push + roll + a jolt, lands from the overshoot and rolls back (≤ 1-2 per reel)
      const sg = Math.round(J * 10) % 2 ? 1 : -1;      // roll direction alternates, deterministic
      tl.fromTo("#world", { scale: 1, rotation: 0, filter: "blur(0px)" }, { scale: 1.3, rotation: -2.6 * sg, filter: "blur(18px)", duration: 0.15, ease: "power2.in", ...IM }, J - 0.15);
      tl.set("#world", { filter: "url(#rgb) blur(12px)" }, J - 0.04);
      tl.fromTo("#world", { scale: 1.3, rotation: 2.2 * sg, x: 18 * sg, filter: "blur(16px)" }, { scale: 1, rotation: 0, x: 0, filter: "blur(0px)", duration: 0.3, ease: "power3.out", ...IM }, J);
      tl.set("#world", { filter: "none", rotation: 0, x: 0 }, J + 0.32);
    } else if (tr.type === "streak") {      // theme-coloured vertical light smear sweeps across while the frame defocuses (≤ 1 per reel)
      tl.fromTo("#streak", { opacity: 0, x: -420 }, { opacity: 0.95, x: 0, duration: 0.16, ease: "power2.in", ...IM }, J - 0.16);
      tl.fromTo("#streak", { opacity: 0.95, x: 0 }, { opacity: 0, x: 380, duration: 0.3, ease: "power2.out", ...IM }, J);
      tl.fromTo("#world", { filter: "blur(0px)" }, { filter: "blur(12px)", duration: 0.16, ease: "power2.in", ...IM }, J - 0.16);
      tl.fromTo("#world", { filter: "blur(12px)", scale: 1.04 }, { filter: "blur(0px)", scale: 1, duration: 0.3, ease: "power3.out", ...IM }, J);
      tl.set("#world", { filter: "none" }, J + 0.32);
    }
  });
  if (DISC.length) tl.eventCallback("onUpdate", () => { const now = tl.time(); DISC.forEach((d) => (now >= d.t ? d.on(d.el) : d.off(d.el))); });
  return api;
}
