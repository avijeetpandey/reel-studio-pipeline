/* kinetic.js v2 — kinetic depth track (Round 16, 22 Nov 2026). Study: research/refs_2026-11-22 (eightsenses Kinetic Text Reels, frame by frame).
 * Every phrase = designed type IN the room: lead words appear exactly as they are spoken; the BIG keyword rises letter by letter out of a light smear,
 * a sheen sweeps it, it sits behind the head (fg.webm occludes it), lights the wall, and whips out. Props are illustrations that live in the room:
 * real dot map + comet arc, a timer ring around the head, a glass search card, a load-balancer hub feeding server racks, a progress sweep, VS logos.
 * The room is graded darker behind him and breathes with the music's bars.
 * Data (plan.premium.kinetic): { dark, hair, face:{cx,cy,r}, beats:[t...], lines:[...], props:[...] }  — see premium.py kinetic().
 * Seek-safe: fromTo/set with immediateRender:false; canvases repaint from one onUpdate clock.
 */
function makeKinetic(tl, K, o) {
  const IM = { immediateRender: false };
  const END = o.end, ACC = o.accent, $ = (s) => document.querySelector(s);
  const mk = (tag, cls, parent, html) => { const e = document.createElement(tag); if (cls) e.className = cls; if (html != null) e.innerHTML = html; parent.appendChild(e); return e; };
  const esc = (t) => String(t).replace(/&/g, "&amp;").replace(/</g, "&lt;");
  const B = $("#behind"), WB = $("#wb");
  const HAIR = K.hair || 850, FACE = K.face || { cx: 540, cy: HAIR + 330, r: 330 };
  const PAINT = [];
  const clamp = (v, a, b) => Math.max(a, Math.min(b, v));
  const ease3 = (u) => 1 - Math.pow(1 - clamp(u, 0, 1), 3);

  /* ---------- stage ---------- */
  const shade = mk("div", "k-shade", B);
  const dk = K.dark || 0.42;
  shade.style.background = `radial-gradient(ellipse 85% 55% at 50% ${(HAIR + 120) / 19.2}%, rgba(0,0,0,${dk * 0.5}) 0%, rgba(0,0,0,${dk}) 65%, rgba(0,0,0,${Math.min(0.85, dk + 0.22)}) 100%)`;
  const spill = mk("div", "k-spill", B); spill.style.top = (HAIR - 560) + "px";
  B.appendChild(WB);
  (K.beats || []).forEach((b, i) => {        // the room breathes on every bar (4 beats)
    if (i % 4) return;
    tl.fromTo(spill, { scale: 1.06 }, { scale: 1, duration: 0.42, ease: "power2.out", ...IM }, b);
  });

  /* ---------- room lighting per beat (Round 17 test): "spot" drops the room to near black (he is the cut-out, so he stays lit);
     "rays" bursts light rays + twinkles from behind his head. After the effects skill's spotlight / glitter-spotlight (MIT), rebuilt seek-safe. ---------- */
  (K.lights || []).forEach((Lt, i) => {
    if (Lt.kind === "spot") {
      const d = mk("div", "k-dim", B); B.insertBefore(d, WB);
      tl.fromTo(d, { opacity: 0 }, { opacity: 1, duration: 0.18, ease: "power2.out", ...IM }, Lt.t0 - 0.05);
      tl.fromTo(d, { opacity: 1 }, { opacity: 0, duration: 0.28, ease: "power2.in", ...IM }, Lt.t1 - 0.2);
    } else if (Lt.kind === "rays") {
      const r = mk("div", "k-rays", B); B.insertBefore(r, WB); r.style.top = (FACE.cy - 1000) + "px";
      const d = mk("div", "k-dim", B); B.insertBefore(d, r);
      tl.fromTo(d, { opacity: 0 }, { opacity: 0.85, duration: 0.18, ease: "power2.out", ...IM }, Lt.t0 - 0.05);
      tl.fromTo(d, { opacity: 0.85 }, { opacity: 0, duration: 0.3, ease: "power2.in", ...IM }, Lt.t1 - 0.2);
      tl.fromTo(r, { opacity: 0, scale: 0.6, rotation: -8 }, { opacity: 1, scale: 1, rotation: 0, duration: 0.45, ease: "expo.out", ...IM }, Lt.t0 - 0.02);
      tl.fromTo(r, { rotation: 0 }, { rotation: 10, duration: Math.max(0.4, Lt.t1 - Lt.t0), ease: "none", ...IM }, Lt.t0 + 0.43);
      tl.fromTo(r, { opacity: 1 }, { opacity: 0, duration: 0.25, ...IM }, Lt.t1 - 0.25);
      for (let k = 0; k < 14; k++) {             // twinkles: deterministic positions around the head
        const a = (k * 137.5) * Math.PI / 180, rr = 260 + (k * 53) % 260, tw = mk("div", "k-twinkle", B); B.insertBefore(tw, WB);
        tw.style.left = (540 + Math.cos(a) * rr * 1.5 - 9) + "px"; tw.style.top = (FACE.cy - 330 + Math.sin(a) * rr * 0.9 - 9) + "px";
        const t0 = Lt.t0 + 0.1 + (k % 7) * 0.09;
        tl.fromTo(tw, { opacity: 0, scale: 0.2, rotation: 0 }, { opacity: 1, scale: 1, rotation: 45, duration: 0.22, ease: "power2.out", ...IM }, t0);
        tl.fromTo(tw, { opacity: 1, scale: 1 }, { opacity: 0, scale: 0.3, duration: 0.35, ease: "power2.in", ...IM }, Math.min(Lt.t1 - 0.3, t0 + 0.55 + (k % 3) * 0.2));
      }
    }
  });

  /* ---------- big words ---------- */
  const PLACED = [];                       // real (measured) top of every big word, so lead lines sit right above it
  (K.lines || []).filter((L) => L.big).forEach((L, i) => {
    const big = mk("div", "k-big " + (L.style || "block"), WB);
    const letters = [...L.big].map((ch) => '<span class="kl">' + (ch === " " ? "&nbsp;" : esc(ch)) + "</span>").join("");
    big.innerHTML = '<span class="kb-t">' + letters + '</span><span class="kb-sheen" aria-hidden="true">' + esc(L.big) + "</span>";
    let size = L.size || 220, y = L.y != null ? L.y : HAIR - size * 0.74;
    big.style.fontSize = size + "px";
    const w = big.querySelector(".kb-t").getBoundingClientRect().width;
    if (w > 860) { const k = 860 / w; const s2 = Math.floor(size * k); y += size * 0.74 - s2 * 0.74; size = s2; big.style.fontSize = size + "px"; }
    big.style.top = y + "px";
    PLACED.push({ t0: L.t0, t1: L.t1, top: y - size * 0.06 });   // Anton caps start ~0.06 em above the box top at line-height .9
    const tb = L.t0, t1 = L.t1, dir = L.out || (i % 2 ? -1 : 1);
    const ls = big.querySelectorAll(".kl"), n = ls.length, st = Math.min(0.026, 0.22 / n);
    // light smear first (bloom), then the letters rise out of it, staggered from the centre
    tl.fromTo(big, { opacity: 0, scaleX: 1.6, filter: "blur(18px) brightness(2.4)" }, { opacity: 1, scaleX: 1, filter: "blur(0px) brightness(1)", duration: 0.34, ease: "power3.out", ...IM }, tb - 0.06);
    ls.forEach((l, j) => {
      const off = Math.abs(j - (n - 1) / 2) * st;
      tl.fromTo(l, { yPercent: 55, opacity: 0, filter: "blur(10px)" }, { yPercent: 0, opacity: 1, filter: "blur(0px)", duration: 0.32, ease: "power4.out", ...IM }, tb - 0.04 + off);
    });
    const sh = big.querySelector(".kb-sheen");
    tl.fromTo(sh, { backgroundPosition: "-120% 0" }, { backgroundPosition: "220% 0", duration: 0.7, ease: "power2.inOut", ...IM }, tb + 0.32);
    tl.fromTo(big, { scale: 1 }, { scale: 1.045, duration: Math.max(0.3, t1 - tb - 0.4), ease: "none", ...IM }, tb + 0.3);
    tl.fromTo(big, { opacity: 1, x: 0, filter: "blur(0px)" }, { opacity: 0, x: dir * 260, filter: "blur(16px)", duration: 0.16, ease: "power2.in", ...IM }, t1 - 0.16);
    tl.fromTo(spill, { opacity: 0.3 }, { opacity: 1, duration: 0.14, ease: "power2.out", ...IM }, tb);
    tl.fromTo(spill, { opacity: 1 }, { opacity: 0.4, duration: 0.7, ease: "power2.out", ...IM }, tb + 0.14);
    tl.fromTo("#bump", { scale: 1 }, { scale: 1.03, duration: 0.07, ease: "power2.out", ...IM }, tb + 0.12);
    tl.fromTo("#bump", { scale: 1.03 }, { scale: 1, duration: 0.34, ease: "power2.out", ...IM }, tb + 0.19);
    if (L.strike) {
      const bar = mk("i", "k-strike", big);
      tl.fromTo(bar, { scaleX: 0 }, { scaleX: 1, duration: 0.16, ease: "power2.out", ...IM }, L.strike.t);
      tl.fromTo(big, { opacity: 1 }, { opacity: 0, y: 26, filter: "blur(10px)", duration: 0.14, ease: "power2.in", ...IM }, L.strike.t + 0.28);
    }
  });

  /* ---------- lead lines: each word appears as it is spoken ---------- */
  (K.lines || []).filter((L) => L.lead).forEach((L, i) => {
    const lead = mk("div", "k-lead" + (L.solo ? " solo" : "") + (L.narrow ? " narrow" : ""), WB);
    const on = L.narrow ? null : PLACED.filter((b) => b.t0 < L.t1 - 0.15 && b.t1 > L.t0).sort((a, b) => b.t0 - a.t0)[0];   // the newest word during this lead
    lead.style.top = (on ? on.top - 72 : L.lead_y != null ? L.lead_y : HAIR - 210) + "px";
    const ws = L.words && L.words.length ? L.words : L.lead.split(" ").map((x, j) => [x, L.t0 + j * 0.12]);
    lead.innerHTML = ws.map((w) => '<span class="kw">' + esc(w[0]) + "</span>").join(" ");
    lead.querySelectorAll(".kw").forEach((s, j) => tl.fromTo(s, { opacity: 0, y: 12, filter: "blur(6px)" }, { opacity: 1, y: 0, filter: "blur(0px)", duration: 0.16, ease: "power3.out", ...IM }, Math.max(0, ws[j][1] - 0.05)));
    tl.fromTo(lead, { opacity: 1, x: 0 }, { opacity: 0, x: (i % 2 ? -1 : 1) * 90, filter: "blur(8px)", duration: 0.14, ease: "power2.in", ...IM }, L.t1 - 0.14);
  });

  /* ---------- props ---------- */
  const P = {};
  const canvasLayer = (e, h, top) => { const cv = mk("canvas", "k-cv", e); cv.width = 1080; cv.height = h; cv.style.top = top + "px"; cv.style.height = h + "px"; return cv; };

  P.map = (p, e) => {                     // real Natural Earth dot map, radial reveal, comet arc between two cities, ripple on arrival
    const DM = (typeof WORLDDOTS !== "undefined") ? WORLDDOTS : null; if (!DM) return;
    const H = 420, top = p.y != null ? p.y : HAIR - 560, cv = canvasLayer(e, H, top), g = cv.getContext("2d");
    const W = 1080, cw = W / DM.w, ch = H / DM.h;
    const xy = (lon, lat) => [(lon + 180) / 360 * W, (DM.lat0 - lat) / (DM.lat0 - DM.lat1) * H];
    const A = xy(...(p.from || [78.9, 22.0])), Bp = xy(...(p.to || [-98, 39]));
    const dots = []; DM.rows.forEach((r, j) => { for (let i = 0; i < r.length; i++) if (r[i] === "1") dots.push([i * cw + cw / 2, j * ch + ch / 2]); });
    PAINT.push((t) => {
      g.clearRect(0, 0, W, H);
      if (t < p.t0 - 0.05 || t > p.t1 + 0.05) return;
      const k = ease3((t - p.t0) / 0.7), fade = clamp((p.t1 - t) / 0.25, 0, 1) * clamp((t - p.t0 + 0.05) / 0.15, 0, 1);
      const R = k * 1250;
      dots.forEach(([x, y]) => {
        const dd = Math.hypot(x - A[0], y - A[1]); if (dd > R) return;
        const edge = clamp((R - dd) / 140, 0, 1);
        g.globalAlpha = fade * (0.32 + 0.45 * (1 - edge));
        g.fillStyle = "#d8ecff"; g.beginPath(); g.arc(x, y, 2.6, 0, 6.283); g.fill();
      });
      const ta = clamp((t - p.arc_t) / (p.arc_d || 0.9), 0, 1), u = ease3(ta);
      const mx = (A[0] + Bp[0]) / 2, my = Math.min(A[1], Bp[1]) - 170;
      const q = (s) => [(1 - s) * (1 - s) * A[0] + 2 * (1 - s) * s * mx + s * s * Bp[0], (1 - s) * (1 - s) * A[1] + 2 * (1 - s) * s * my + s * s * Bp[1]];
      g.globalAlpha = fade; g.strokeStyle = ACC; g.lineWidth = 3; g.beginPath(); g.arc(A[0], A[1], 10 + 5 * Math.sin(t * 8), 0, 6.283); g.stroke();
      g.fillStyle = "#fff"; g.beginPath(); g.arc(A[0], A[1], 5, 0, 6.283); g.fill();
      if (ta > 0) {
        for (let s = 0; s < 48; s++) {          // trail: brighter toward the head
          const a0 = q((s / 48) * u), a1 = q(((s + 1) / 48) * u);
          g.globalAlpha = fade * (0.15 + 0.85 * (s / 48)); g.strokeStyle = ACC; g.lineWidth = 2 + 4 * (s / 48);
          g.beginPath(); g.moveTo(a0[0], a0[1]); g.lineTo(a1[0], a1[1]); g.stroke();
        }
        const hd = q(u); g.globalAlpha = fade; g.shadowColor = ACC; g.shadowBlur = 24; g.fillStyle = "#fff"; g.beginPath(); g.arc(hd[0], hd[1], 8, 0, 6.283); g.fill(); g.shadowBlur = 0;
      }
      if (ta >= 1) {                          // arrival ripples
        const since = t - p.arc_t - (p.arc_d || 0.9);
        for (let r = 0; r < 3; r++) { const ph = ((since * 1.4 + r / 3) % 1); g.globalAlpha = fade * (1 - ph); g.strokeStyle = ACC; g.lineWidth = 3; g.beginPath(); g.arc(Bp[0], Bp[1], 8 + ph * 46, 0, 6.283); g.stroke(); }
        g.globalAlpha = fade; g.fillStyle = "#fff"; g.beginPath(); g.arc(Bp[0], Bp[1], 6, 0, 6.283); g.fill();
      }
      g.globalAlpha = 1;
    });
    (p.labels || []).forEach((lb, j) => {    // pill labels (DOM so the type is crisp)
      const pt = j ? Bp : A, pl = mk("div", "k-pill", e, esc(lb));
      pl.style.left = (pt[0] - 80) + "px"; pl.style.top = (top + pt[1] + 18) + "px";
      const tt = j ? p.arc_t + (p.arc_d || 0.9) : p.t0 + 0.3;
      tl.fromTo(pl, { opacity: 0, y: 10, scale: 0.8 }, { opacity: 1, y: 0, scale: 1, duration: 0.25, ease: "expo.out", ...IM }, tt);
      tl.fromTo(pl, { opacity: 1 }, { opacity: 0, duration: 0.18, ...IM }, p.t1 - 0.18);
    });
  };

  P.ring = (p, e) => {                     // a timer ring sweeps around the head ("1 second")
    const H = 1100, top = FACE.cy - 550, cv = canvasLayer(e, H, top), g = cv.getContext("2d"), cx = 540, cy = 550, r = p.r || FACE.r * 1.22;
    const lab = { style: {} };   // 22 Nov 2026: the counter label collided with the big word; the word already says it
    PAINT.push((t) => {
      g.clearRect(0, 0, 1080, H);
      if (t < p.t0 - 0.05 || t > p.t1 + 0.05) { lab.style.opacity = 0; return; }
      const fade = clamp((p.t1 - t) / 0.2, 0, 1) * clamp((t - p.t0) / 0.15, 0, 1), u = ease3((t - p.t0 - 0.1) / (p.dur || 1.0));
      g.globalAlpha = fade * 0.3; g.strokeStyle = "#fff"; g.lineWidth = 2; g.beginPath(); g.arc(cx, cy, r, 0, 6.283); g.stroke();
      for (let k = 0; k < 60; k++) {
        const a = -Math.PI / 2 + k / 60 * 6.283, l = k % 5 ? 10 : 22, on = k / 60 <= u;
        g.globalAlpha = fade * (on ? 0.95 : 0.25); g.lineWidth = k % 5 ? 2 : 4; g.strokeStyle = on ? ACC : "#fff";
        g.beginPath(); g.moveTo(cx + Math.cos(a) * (r + 10), cy + Math.sin(a) * (r + 10)); g.lineTo(cx + Math.cos(a) * (r + 10 + l), cy + Math.sin(a) * (r + 10 + l)); g.stroke();
      }
      g.globalAlpha = fade; g.strokeStyle = ACC; g.lineWidth = 7; g.shadowColor = ACC; g.shadowBlur = 20; g.beginPath(); g.arc(cx, cy, r, -Math.PI / 2, -Math.PI / 2 + u * 6.283); g.stroke(); g.shadowBlur = 0;
      const a = -Math.PI / 2 + u * 6.283; g.fillStyle = "#fff"; g.beginPath(); g.arc(cx + Math.cos(a) * r, cy + Math.sin(a) * r, 9, 0, 6.283); g.fill();
      g.globalAlpha = 1;
      lab.style.opacity = fade; lab.textContent = (u * (p.value || 1)).toFixed(2) + (p.unit || "s");
    });
  };

  P.digits = (p, e) => {                   // slot-roll digits (each character spins before it locks)
    const dv = mk("div", "k-digits", e); dv.style.top = (p.y != null ? p.y : HAIR - 300) + "px";
    const txt = p.text, CH = "0123456789";
    dv.innerHTML = [...txt].map((c) => '<span class="kd">' + esc(c) + "</span>").join("");
    const sp = dv.querySelectorAll(".kd");
    PAINT.push((t) => {
      if (t < p.t0 || t > p.t1) { dv.style.opacity = 0; return; }
      dv.style.opacity = clamp((p.t1 - t) / 0.15, 0, 1);
      sp.forEach((s, j) => { const lock = p.t0 + 0.08 + j * 0.05, c = txt[j];
        s.textContent = t >= lock || !/\d/.test(c) ? c : CH[Math.floor(t * 40 + j * 7) % 10]; s.style.opacity = t >= p.t0 + j * 0.03 ? 1 : 0; });
    });
  };

  P.search = (p, e) => {                   // glass search bar, typed query, the answer row resolves with a drawn check
    const c = mk("div", "k-search", e, '<div class="ks-bar"><svg class="ks-g" viewBox="0 0 24 24"><circle cx="10" cy="10" r="6.5" fill="none" stroke="currentColor" stroke-width="2.6"/><path d="M15 15l6 6" stroke="currentColor" stroke-width="2.6" stroke-linecap="round"/></svg><span class="ks-q"></span><i class="ks-c"></i></div>' +
      '<div class="ks-row"><span class="ks-dot"></span><span class="ks-r">' + esc(p.result || "") + '</span><svg class="ks-ok" viewBox="0 0 24 24"><path d="M5 12.5l4.5 4.5L19 7.5" fill="none" stroke="#2de2a6" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/></svg></div><div class="ks-sheen"></div>');
    c.style.top = (p.y != null ? p.y : 292) + "px";
    tl.fromTo(c, { opacity: 0, rotationX: 24, rotationY: -26, y: 40, filter: "blur(12px)" }, { opacity: 1, rotationX: 8, rotationY: -12, y: 0, filter: "blur(0px)", duration: 0.45, ease: "power3.out", ...IM }, p.t0);
    tl.fromTo(c, { rotationY: -12 }, { rotationY: -4, duration: Math.max(0.5, p.t1 - p.t0 - 0.6), ease: "none", ...IM }, p.t0 + 0.45);
    const q = c.querySelector(".ks-q"), st = { n: 0 };
    tl.fromTo(st, { n: 0 }, { n: p.query.length, duration: p.type_d || 0.75, ease: "none", ...IM, onUpdate() { q.textContent = p.query.slice(0, Math.round(st.n)); } }, p.t0 + 0.35);
    for (let k = 0; k * 0.5 < p.t1 - p.t0; k++) tl.fromTo(c.querySelector(".ks-c"), { opacity: 1 }, { opacity: 0.1, duration: 0.01, ...IM }, p.t0 + k * 0.5 + 0.25);
    const tr = p.result_t || p.t0 + 1.4;
    tl.fromTo(c.querySelector(".ks-row"), { opacity: 0, y: 18, filter: "blur(8px)" }, { opacity: 1, y: 0, filter: "blur(0px)", duration: 0.3, ease: "power3.out", ...IM }, tr);
    const ok = c.querySelector(".ks-ok path"); ok.style.strokeDasharray = 30;
    tl.fromTo(ok, { strokeDashoffset: 30 }, { strokeDashoffset: 0, duration: 0.3, ease: "power2.out", ...IM }, tr + 0.25);
    tl.fromTo(c.querySelector(".ks-sheen"), { xPercent: -120 }, { xPercent: 220, duration: 0.8, ease: "power2.inOut", ...IM }, tr + 0.1);
    tl.fromTo(c, { opacity: 1, x: 0 }, { opacity: 0, x: 240, filter: "blur(14px)", duration: 0.18, ease: "power2.in", ...IM }, p.t1 - 0.18);
  };

  P.racks = (p, e) => {                    // load-balancer hub above the head feeds 4 racks, packets flow, the emptiest goes green
    const H = 760, top = p.y != null ? p.y : HAIR - 470, cv = canvasLayer(e, H, top), g = cv.getContext("2d");
    const xs = [84, 208, 762, 886], rw = 110, rh = 470, ry = 230, hub = [540, 70], win = p.pick != null ? p.pick : 2;
    const load = p.load || [0.92, 0.8, 0.2, 0.86];
    PAINT.push((t) => {
      g.clearRect(0, 0, 1080, H);
      if (t < p.t0 - 0.05 || t > p.t1 + 0.05) return;
      const fade = clamp((p.t1 - t) / 0.22, 0, 1), picked = t >= (p.pick_t || 1e9), hk = ease3((t - p.t0) / 0.4);
      g.globalAlpha = fade * hk; g.fillStyle = "rgba(12,16,24,.9)"; g.strokeStyle = ACC; g.lineWidth = 3; g.beginPath(); g.roundRect(hub[0] - 150, hub[1] - 42, 300, 84, 42); g.fill(); g.stroke();
      g.fillStyle = "#fff"; g.font = "800 32px PSans"; g.textAlign = "center"; g.textBaseline = "middle"; g.fillText(p.hub || "LOAD BALANCER", hub[0], hub[1] + 2);
      xs.forEach((x, i) => {
        const k = ease3((t - p.t0 - 0.15 - i * 0.07) / 0.45); if (!k) return;
        const isW = picked && i === win, y0 = ry + (1 - k) * 60;
        const ax = hub[0] + (i < 2 ? -90 : 90), ay = hub[1] + 40, bx = x + rw / 2, by = y0;
        g.globalAlpha = fade * k * (picked && !isW ? 0.25 : 0.7); g.strokeStyle = isW ? "#2de2a6" : "rgba(255,255,255,.45)"; g.lineWidth = isW ? 4 : 2;
        g.setLineDash([8, 10]); g.lineDashOffset = -t * 60; g.beginPath(); g.moveTo(ax, ay); g.bezierCurveTo(ax, ay + 90, bx, by - 90, bx, by); g.stroke(); g.setLineDash([]);
        if (!picked || isW) for (let s = 0; s < (isW ? 3 : 1); s++) {
          const u = ((t * (isW ? 1.6 : 0.9) + i * 0.27 + s / 3) % 1);
          const px = (1 - u) ** 3 * ax + 3 * (1 - u) ** 2 * u * ax + 3 * (1 - u) * u * u * bx + u ** 3 * bx, py = (1 - u) ** 3 * ay + 3 * (1 - u) ** 2 * u * (ay + 90) + 3 * (1 - u) * u * u * (by - 90) + u ** 3 * by;
          g.globalAlpha = fade * k; g.fillStyle = isW ? "#2de2a6" : ACC; g.shadowColor = g.fillStyle; g.shadowBlur = 14; g.beginPath(); g.arc(px, py, 6, 0, 6.283); g.fill(); g.shadowBlur = 0;
        }
        g.globalAlpha = fade * k;
        const gr = g.createLinearGradient(x, y0, x + rw, y0 + rh); gr.addColorStop(0, "rgba(34,42,58,.95)"); gr.addColorStop(1, "rgba(10,13,20,.95)");
        g.fillStyle = gr; g.strokeStyle = isW ? "#2de2a6" : "rgba(255,255,255,.22)"; g.lineWidth = isW ? 5 : 1.5;
        if (isW) { g.shadowColor = "#2de2a6"; g.shadowBlur = 30; }
        g.beginPath(); g.roundRect(x, y0, rw, rh, 14); g.fill(); g.stroke(); g.shadowBlur = 0;
        g.fillStyle = "rgba(255,255,255,.18)"; g.fillRect(x + 8, y0 + 4, rw - 16, 2);
        for (let r = 0; r < 8; r++) {
          const yy = y0 + 22 + r * 50, on = ((Math.floor(t * 10) + r * 3 + i * 5) % 7) < (isW ? 2 : 5);
          g.fillStyle = "rgba(255,255,255,.07)"; g.beginPath(); g.roundRect(x + 12, yy, rw - 24, 32, 6); g.fill();
          g.fillStyle = isW ? "#2de2a6" : on ? ACC : "rgba(255,255,255,.2)"; g.beginPath(); g.arc(x + 28, yy + 16, 5, 0, 6.283); g.fill();
          g.fillStyle = "rgba(255,255,255,.12)"; g.fillRect(x + 42, yy + 13, rw - 66, 6);
        }
        const lv = isW ? 0.18 : load[i], bw = (rw - 24) * lv * clamp((t - p.t0) / 0.9, 0, 1);
        g.fillStyle = "rgba(255,255,255,.12)"; g.beginPath(); g.roundRect(x + 12, y0 + rh - 26, rw - 24, 10, 5); g.fill();
        g.fillStyle = isW ? "#2de2a6" : lv > 0.6 ? "#ff5a36" : ACC; g.beginPath(); g.roundRect(x + 12, y0 + rh - 26, Math.max(6, bw), 10, 5); g.fill();
      });
      g.globalAlpha = 1;
    });
  };

  P.load = (p, e) => {                     // progress sweep across the room + percentage, lands on a check
    const wrap = mk("div", "k-loadw", e, '<div class="k-loadt"><i></i></div><div class="k-loadp">0%</div>'); wrap.style.top = (p.y != null ? p.y : HAIR - 120) + "px";
    const bar = wrap.querySelector("i"), pc = wrap.querySelector(".k-loadp"), st = { v: 0 }, D = p.dur || 1.1;
    tl.fromTo(wrap, { opacity: 0 }, { opacity: 1, duration: 0.2, ...IM }, p.t0);
    tl.fromTo(bar, { scaleX: 0 }, { scaleX: 1, duration: D, ease: "power2.inOut", ...IM }, p.t0 + 0.1);
    tl.fromTo(st, { v: 0 }, { v: 100, duration: D, ease: "power2.inOut", ...IM, onUpdate() { pc.textContent = Math.round(st.v) + "%"; } }, p.t0 + 0.1);
    PAINT.push((t) => { if (t >= p.t0 + 0.12 + D) pc.textContent = "✓ 100%"; });
    if (K.v === 4) pc.style.display = "none";
    tl.fromTo(wrap, { opacity: 1 }, { opacity: 0, duration: 0.2, ...IM }, p.t1 - 0.2);
  };

  P.versus = (p, e) => {
    (p.items || []).forEach((it, i) => {
      const b = mk("div", "k-vs-b", e, '<div class="k-vs-i"><svg viewBox="0 0 24 24"><path d="' + it.d + '" fill="#' + it.hex + '"/></svg></div><span>' + esc(it.label) + "</span>");
      b.style.left = (i ? 770 : 70) + "px"; b.style.top = (p.y != null ? p.y : HAIR - 40) + "px";
      tl.fromTo(b, { opacity: 0, x: i ? 220 : -220, rotation: i ? 18 : -18, filter: "blur(12px)" }, { opacity: 1, x: 0, rotation: i ? 6 : -6, filter: "blur(0px)", duration: 0.42, ease: "expo.out", ...IM }, (it.t || p.t0));
      tl.fromTo(b, { y: 0 }, { y: -12, duration: Math.max(0.4, p.t1 - (it.t || p.t0) - 0.4), ease: "sine.inOut", ...IM }, (it.t || p.t0) + 0.42);
      tl.fromTo(b, { opacity: 1 }, { opacity: 0, duration: 0.2, ...IM }, p.t1 - 0.2);
    });
    const vs = mk("div", "k-vs", e, "VS"); vs.style.top = (p.y != null ? p.y : HAIR - 40) - 190 + "px";
    tl.fromTo(vs, { opacity: 0, scale: 2.4, filter: "blur(14px)" }, { opacity: 1, scale: 1, filter: "blur(0px)", duration: 0.26, ease: "power4.out", ...IM }, p.vs_t || p.t0 + 0.3);
    tl.fromTo(vs, { opacity: 1 }, { opacity: 0, duration: 0.2, ...IM }, p.t1 - 0.2);
  };

  (K.props || []).forEach((p) => { const e = mk("div", "k-prop", WB); (P[p.kind] || (() => {}))(p, e); });
  if (PAINT.length) {
    const st = { t: 0 };
    tl.fromTo(st, { t: 0 }, { t: END, duration: END, ease: "none", ...IM, onUpdate() { PAINT.forEach((f) => f(st.t)); } }, 0);
  }
}
