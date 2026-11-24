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
    const MAXW = K.maxw || 860; if (w > MAXW) { const k = MAXW / w; const s2 = Math.floor(size * k); y += size * 0.74 - s2 * 0.74; size = s2; big.style.fontSize = size + "px"; }
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

  /* ---------- web-crawler props (22 Nov 2026, web-crawler reel): request flood, URL trap, per-domain politeness queues.
     All three are pure functions of t (seek-safe) painted on one canvas in the ceiling band (y 285-535, x kept inside the 60-930 safe box). ---------- */
  const RR = (g, x, y, w, h, r) => { g.beginPath(); g.roundRect(x, y, w, h, r); };
  const hash = (n) => { const x = Math.sin(n * 127.1 + 311.7) * 43758.5453; return x - Math.floor(x); };
  const RED = "#ff4d3d", GRN = "#2de2a6", AMB = "#ffc233";
  const mixc = (a, b, u) => { const pa = [1, 3, 5].map((i) => parseInt(a.slice(i, i + 2), 16)), pb = [1, 3, 5].map((i) => parseInt(b.slice(i, i + 2), 16)); return "rgb(" + pa.map((v, i) => Math.round(v + (pb[i] - v) * u)).join(",") + ")"; };

  P.flood = (p, e) => {                    // many requests hit one server: its load climbs, it turns red and shakes, an IP-BLOCKED stamp slams on, later requests bounce off
    const H = 250, top = p.y != null ? p.y : 285, cv = canvasLayer(e, H, top), g = cv.getContext("2d");
    const cx = 540, cy = 128, peak = p.peak_t != null ? p.peak_t : p.t0 + 2.4, blk = p.block_t != null ? p.block_t : p.t1 - 0.8, TR = 0.62;
    const sp = []; { let c = p.t0 + 0.15, i = 0; while (c < blk) { const u = clamp((c - p.t0) / Math.max(0.5, peak - p.t0), 0, 1), r = 3 + 43 * u * u; sp.push({ s: c, side: i % 2 ? 1 : -1, y: 26 + hash(i + 1) * 196, j: hash(i + 9) }); c += 1 / r; i++; } }
    PAINT.push((t) => {
      g.clearRect(0, 0, 1080, H);
      if (t < p.t0 - 0.05 || t > p.t1 + 0.05) return;
      const fade = clamp((p.t1 - t) / 0.22, 0, 1) * clamp((t - p.t0 + 0.05) / 0.2, 0, 1);
      const load = clamp((t - p.t0) / Math.max(0.5, peak - p.t0 + 0.2), 0, 1), hot = clamp((load - 0.45) / 0.55, 0, 1);
      const col = load < 0.5 ? mixc("#2de2a6", "#ffc233", load / 0.5) : mixc("#ffc233", "#ff4d3d", clamp((load - 0.5) / 0.5, 0, 1));
      const dx = Math.sin(t * 70) * hot * 5, dy = Math.cos(t * 83) * hot * 2.5;
      // requests
      sp.forEach((c) => {
        const u = (t - c.s) / TR; if (u < 0 || u > 1.25) return;
        const x0 = c.side < 0 ? -80 : 1160, ty = cy - 14 + (c.j - 0.5) * 36, e1 = u < 1 ? Math.pow(u, 1.5) : 1;
        let x = x0 + (cx - x0) * e1, y = c.y + (ty - c.y) * e1, a = 1;
        if (t >= blk) { const wall = cx + c.side * 240; if ((c.side < 0 && x > wall) || (c.side > 0 && x < wall)) { const over = Math.abs(x - wall); x = wall - c.side * over * 0.9; a = clamp(1 - over / 160, 0, 1); } }
        else if (u > 1) a = clamp(1 - (u - 1) * 5, 0, 1);
        if (a <= 0) return;
        g.globalAlpha = fade * a; g.fillStyle = "rgba(10,14,22,.88)"; g.strokeStyle = t >= blk && Math.abs(x - cx) > 190 ? RED : ACC; g.lineWidth = 2.5;
        RR(g, x - 52, y - 19, 104, 38, 11); g.fill(); g.stroke();
        g.fillStyle = "#fff"; g.font = "800 24px PSans"; g.textAlign = "center"; g.textBaseline = "middle"; g.fillText("GET /", x, y + 1);
      });
      // server
      g.globalAlpha = fade; g.fillStyle = "rgba(255,255,255,.9)"; g.font = "800 31px PSans"; g.textAlign = "center"; g.textBaseline = "middle"; g.fillText(p.host || "website.com", cx, 22);
      for (let i = 0; i < 3; i++) {
        const y = cy - 64 + i * 54 + dy, x = cx - 112 + dx, gr = g.createLinearGradient(x, y, x + 224, y + 44); gr.addColorStop(0, "rgba(40,48,66,.98)"); gr.addColorStop(1, "rgba(14,18,28,.98)");
        g.fillStyle = gr; g.strokeStyle = col; g.lineWidth = 3.5; if (hot > 0.3) { g.shadowColor = col; g.shadowBlur = 24 * hot; }
        RR(g, x, y, 224, 44, 12); g.fill(); g.stroke(); g.shadowBlur = 0;
        for (let k = 0; k < 3; k++) { const on = ((Math.floor(t * (6 + 30 * load)) + k + i * 2) % 3) !== 0; g.fillStyle = on ? col : "rgba(255,255,255,.18)"; g.beginPath(); g.arc(x + 26 + k * 27, y + 22, 7, 0, 6.283); g.fill(); }
        g.fillStyle = "rgba(255,255,255,.14)"; g.fillRect(x + 118, y + 19, 82, 7);
      }
      g.fillStyle = "rgba(255,255,255,.15)"; RR(g, cx - 130, 226, 260, 15, 7); g.fill(); g.fillStyle = col; RR(g, cx - 130, 226, Math.max(10, 260 * load), 15, 7); g.fill();
      // stamp
      if (t >= blk) {
        const k = clamp((t - blk) / 0.16, 0, 1), sc = 2.4 - 1.4 * ease3(k), a = clamp((t - blk) / 0.08, 0, 1);
        g.save(); g.translate(cx, cy); g.rotate(-0.1); g.scale(sc, sc); g.globalAlpha = fade * a;
        g.fillStyle = "rgba(34,6,6,.9)"; g.strokeStyle = RED; g.lineWidth = 7; g.shadowColor = RED; g.shadowBlur = 26; RR(g, -215, -52, 430, 104, 16); g.fill(); g.stroke(); g.shadowBlur = 0;
        g.fillStyle = "#ff6a58"; g.font = "400 72px PAnton"; g.textAlign = "center"; g.textBaseline = "middle"; g.fillText("IP BLOCKED", 0, 5); g.restore();
      }
      g.globalAlpha = 1;
    });
  };

  P.urls = (p, e) => {                     // an infinite URL trap: /page/1, /page/2, /page/3 ... /page/∞, the last row loops forever
    const H = 250, top = p.y != null ? p.y : 285, cv = canvasLayer(e, H, top), g = cv.getContext("2d");
    const rows = p.rows || ["shop.com/page/1", "shop.com/page/2", "shop.com/page/3", "shop.com/page/∞"], x0 = 150, w = 780, rh = 55, y0 = 12, gap = p.gap || 0.3;
    PAINT.push((t) => {
      g.clearRect(0, 0, 1080, H);
      if (t < p.t0 - 0.05 || t > p.t1 + 0.05) return;
      const fade = clamp((p.t1 - t) / 0.2, 0, 1) * clamp((t - p.t0 + 0.05) / 0.12, 0, 1);
      g.globalAlpha = fade; g.fillStyle = "rgba(10,14,22,.84)"; g.strokeStyle = "rgba(255,255,255,.2)"; g.lineWidth = 2; RR(g, x0 - 24, y0 - 12, w + 48, rows.length * rh + 18, 26); g.fill(); g.stroke();
      rows.forEach((r, i) => {
        const k = ease3((t - (p.t0 + 0.12 + i * gap)) / 0.26); if (k <= 0) return;
        const last = i === rows.length - 1, y = y0 + i * rh + (1 - k) * 20, col = last ? RED : ACC, hh = rh - 8;
        g.globalAlpha = fade * k; g.fillStyle = last ? "rgba(255,77,61,.16)" : "rgba(255,255,255,.07)"; RR(g, x0, y, w, hh, 14); g.fill();
        g.fillStyle = col; g.beginPath(); g.arc(x0 + 26, y + hh / 2, 8, 0, 6.283); g.fill();
        g.fillStyle = last ? "#ffb3a8" : "#fff"; g.font = "700 35px PSans"; g.textAlign = "left"; g.textBaseline = "middle"; g.fillText(r, x0 + 54, y + hh / 2 + 2);
        const ax = x0 + w - 44, ay = y + hh / 2;
        if (!last) { g.strokeStyle = "rgba(255,255,255,.55)"; g.lineWidth = 4; g.lineCap = "round"; g.beginPath(); g.moveTo(ax - 7, ay - 11); g.lineTo(ax + 6, ay); g.lineTo(ax - 7, ay + 11); g.stroke(); }
        else {
          const spin = (t - (p.t0 + 0.12 + i * gap)) * 5.5; g.strokeStyle = RED; g.lineWidth = 5; g.lineCap = "round"; g.beginPath(); g.arc(ax, ay, 14, spin, spin + 4.5); g.stroke();
          const ea = spin + 4.5; g.fillStyle = RED; g.beginPath(); g.moveTo(ax + Math.cos(ea) * 14 + Math.cos(ea + 1.57) * 9, ay + Math.sin(ea) * 14 + Math.sin(ea + 1.57) * 9);
          g.lineTo(ax + Math.cos(ea) * 14 - Math.cos(ea + 1.57) * 9 + Math.cos(ea) * 8, ay + Math.sin(ea) * 14 - Math.sin(ea + 1.57) * 9 + Math.sin(ea) * 8); g.lineTo(ax + Math.cos(ea) * 14 - Math.cos(ea + 1.57) * 9 - Math.cos(ea) * 8, ay + Math.sin(ea) * 14 - Math.sin(ea + 1.57) * 9 - Math.sin(ea) * 8); g.fill();
        }
      });
      g.globalAlpha = 1;
    });
  };

  P.queues = (p, e) => {                   // politeness queues: URLs are routed into one lane per domain, each lane has ONE worker that pulls one URL at a time
    const H = 250, top = p.y != null ? p.y : 285, cv = canvasLayer(e, H, top), g = cv.getContext("2d");
    const hosts = p.hosts || ["amazon.in", "github.com", "bbc.com", "imdb.com"], N = hosts.length;
    const LY = (i) => 34 + i * 54, LH = 46, TX = 330, TW = 340, SLOT = 80, WX = 716, order = p.order || [0, 2, 1, 3, 0, 1, 2, 3, 0, 2, 1, 3, 1, 0, 2, 3];
    const R0 = p.route_t, RG = p.route_gap || 0.13, W0 = p.worker_t, P0 = p.pull_t, PG = p.pull_gap || 0.8, DONE = 0.62;
    const chips = order.map((ln, j) => ({ ln, j, slot: order.slice(0, j).filter((x) => x === ln).length, tr: R0 + j * RG }));
    chips.forEach((c) => { c.tp = P0 + c.ln * 0.19 + c.slot * PG; });
    const slotX = (s) => TX + TW - (s + 1) * SLOT + 8;
    const chip = (x, y, a, hl) => { g.globalAlpha = a; g.fillStyle = hl ? "#fff" : ACC; RR(g, x, y - 16, 64, 32, 10); g.fill(); g.fillStyle = "rgba(10,14,22,.55)"; g.fillRect(x + 12, y - 6, 36, 4.5); g.fillRect(x + 12, y + 3, 24, 4.5); };
    PAINT.push((t) => {
      g.clearRect(0, 0, 1080, H);
      if (t < p.t0 - 0.05 || t > p.t1 + 0.05) return;
      const fade = clamp((p.t1 - t) / 0.22, 0, 1) * clamp((t - p.t0 + 0.05) / 0.2, 0, 1);
      for (let i = 0; i < N; i++) {
        const y = LY(i), k = ease3((t - p.t0 - i * 0.07) / 0.3);
        g.globalAlpha = fade * k; g.fillStyle = "rgba(255,255,255,.07)"; g.strokeStyle = "rgba(255,255,255,.2)"; g.lineWidth = 2; RR(g, TX, y, TW, LH, 22); g.fill(); g.stroke();
        g.fillStyle = "rgba(255,255,255,.95)"; g.font = "800 31px PSans"; g.textAlign = "left"; g.textBaseline = "middle"; g.fillText(hosts[i], 128, y + LH / 2 + 2);
      }
      let done = new Array(N).fill(0);
      chips.forEach((c) => {
        const y = LY(c.ln) + LH / 2;
        if (t < c.tr) return;
        const shifted = chips.reduce((a, o) => a + (o.ln === c.ln && o.slot < c.slot ? ease3((t - o.tp) / 0.25) : 0), 0), pos = c.slot - shifted;
        if (t >= c.tp + DONE) { done[c.ln]++; return; }
        let x = slotX(pos), yy = y, a = fade, hl = false;
        const ur = clamp((t - c.tr) / 0.34, 0, 1);
        if (ur < 1) { const e1 = ease3(ur); x = 540 + (slotX(c.slot) - 540) * e1; yy = -30 + (y + 30) * e1 - Math.sin(Math.PI * e1) * 18; }
        if (t >= c.tp) { const m = ease3((t - c.tp) / 0.3); x = slotX(0) + (WX - 33 - slotX(0)) * m; hl = true; if (t > c.tp + 0.3) a = fade * clamp(1 - (t - c.tp - 0.3) / 0.3, 0, 1); }
        chip(x, yy, a, hl);
      });
      for (let i = 0; i < N; i++) {
        const y = LY(i) + LH / 2, wk = ease3((t - W0 - i * 0.1) / 0.3); if (wk <= 0) continue;
        const busy = chips.some((c) => c.ln === i && t >= c.tp + 0.3 && t < c.tp + DONE), r = 27 * wk;
        g.globalAlpha = fade * wk; g.fillStyle = "rgba(12,16,24,.96)"; g.strokeStyle = busy ? ACC : "rgba(255,255,255,.85)"; g.lineWidth = 3.5; if (busy) { g.shadowColor = ACC; g.shadowBlur = 20; }
        g.beginPath(); g.arc(WX, y, r, 0, 6.283); g.fill(); g.stroke(); g.shadowBlur = 0;
        g.fillStyle = "#fff"; g.beginPath(); g.arc(WX - 8, y - 4, 3.6, 0, 6.283); g.arc(WX + 8, y - 4, 3.6, 0, 6.283); g.fill();
        g.strokeStyle = "#fff"; g.lineWidth = 3; g.beginPath(); g.arc(WX, y + 2, 8, 0.25, 2.9); g.stroke();
        if (done[i] > 0) { g.globalAlpha = fade; g.fillStyle = GRN; g.font = "800 30px PSans"; g.textAlign = "left"; g.textBaseline = "middle"; g.fillText("✓ " + done[i], WX + 46, y + 2); }
      }
      if (t >= P0 - 0.2) { const a = ease3((t - P0 + 0.2) / 0.3); g.globalAlpha = fade * a; g.fillStyle = ACC; g.font = "800 29px PSans"; g.textAlign = "center"; g.textBaseline = "middle"; g.fillText("1 req / sec", WX + 40, 14); }
      g.globalAlpha = 1;
    });
  };

  /* ---------- distributed-ID props (23 Nov 2026, reel snowflake_unique_id_generator): shard collision, random-UUID page scatter, the 64-bit ID bar,
     a one-server ID ticker, the clock rewind. Same rules as the crawler props: pure functions of t on one canvas in the ceiling band (y 285-535, x 60-930). ---------- */
  const CORAL = "#ff8a5c", INK = "#0b0f19";
  const fadeOf = (p, t) => clamp((p.t1 - t) / 0.22, 0, 1) * clamp((t - p.t0 + 0.05) / 0.2, 0, 1);
  const tx = (g, s, x, y, font, col, al) => { g.font = font; g.fillStyle = col; g.textAlign = al || "center"; g.textBaseline = "middle"; g.fillText(s, x, y); };
  const band = (e, p) => { const cv = canvasLayer(e, 250, p.y != null ? p.y : 285); return cv.getContext("2d"); };

  P.shards = (p, e) => {                   // 3 shards each count 1, 2, 3 on their own: the same IDs exist in every shard -> they collide (red)
    const g = band(e, p), CW = 230, GP = 40, X0 = (1080 - (3 * CW + 2 * GP)) / 2;
    PAINT.push((t) => {
      g.clearRect(0, 0, 1080, 250);
      if (t < p.t0 - 0.05 || t > p.t1 + 0.05) return;
      const fade = fadeOf(p, t), hit = clamp((t - p.hit_t) / 0.16, 0, 1), sh = hit > 0 && t < p.hit_t + 0.25 ? Math.sin(t * 90) * 4 : 0;
      for (let i = 0; i < 3; i++) {
        const k = ease3((t - p.t0 - i * 0.08) / 0.3), x = X0 + i * (CW + GP) + sh;
        g.globalAlpha = fade * k; g.fillStyle = "rgba(10,14,22,.88)"; g.strokeStyle = hit ? RED : "rgba(255,255,255,.3)"; g.lineWidth = 3.5; RR(g, x, 12 + (1 - k) * 16, CW, 226, 24); g.fill(); g.stroke();
        tx(g, "SHARD " + (i + 1), x + CW / 2, 44, "800 30px PSans", "#fff");
        for (let r = 0; r < 3; r++) {
          const rk = ease3((t - (p.t0 + 0.5 + r * 0.3)) / 0.22); if (rk <= 0) continue;
          const y = 74 + r * 54, bad = r === 2 && t >= p.hit_t;
          g.globalAlpha = fade * rk; g.fillStyle = bad ? "rgba(255,77,61,.26)" : "rgba(255,255,255,.09)"; RR(g, x + 20, y, CW - 40, 44, 12); g.fill();
          tx(g, "ID " + (r + 1), x + CW / 2, y + 23, "800 31px PSans", bad ? "#ff8f80" : ACC);
        }
      }
      if (t >= p.hit_t) { const k = ease3((t - p.hit_t) / 0.2); [0, 1].forEach((i) => { g.globalAlpha = fade * k; tx(g, "=", X0 + (i + 1) * (CW + GP) - GP / 2, 74 + 2 * 54 + 23, "800 46px PSans", RED); }); }
      g.globalAlpha = 1;
    });
  };

  P.pages = (p, e) => {                    // B-Tree leaf pages: each random UUID lands on a random page; pages fill, crack and turn red (fragmentation); SLOW WRITES lands
    const g = band(e, p), N = 12, PW = 58, PG = 10, X0 = 60 + (870 - (N * PW + (N - 1) * PG)) / 2, PY = 100, PH = 112, STOP = (p.slow_t != null ? p.slow_t : p.t1 - 0.8) - 0.25;
    const base = Array.from({ length: N }, (_, i) => 0.25 + hash(i + 50) * 0.35), ins = [];
    { let c = p.t0 + 0.5, i = 0; while (c < STOP) { ins.push({ s: c, pg: Math.floor(hash(i + 3) * N), id: [0, 1, 2, 3].map((k) => Math.floor(hash(i * 7 + k + 1) * 65535).toString(16).padStart(4, "0")).join("-") }); c += Math.max(0.2, 0.44 - i * 0.03); i++; } }
    PAINT.push((t) => {
      g.clearRect(0, 0, 1080, 250);
      if (t < p.t0 - 0.05 || t > p.t1 + 0.05) return;
      const fade = fadeOf(p, t);
      g.globalAlpha = fade; tx(g, "B-TREE LEAF PAGES", X0, PY + PH + 24, "800 24px PSans", "rgba(255,255,255,.65)", "left");
      for (let i = 0; i < N; i++) {
        const k = ease3((t - p.t0 - i * 0.03) / 0.3), x = X0 + i * (PW + PG), fill = base[i] + ins.filter((c) => c.pg === i && t >= c.s + 0.3).length * 0.22, red = fill >= 1;
        const sh = red && t < ins.filter((c) => c.pg === i && c.s + 0.3 <= t).slice(-1)[0].s + 0.7 ? Math.sin(t * 80 + i) * 3 : 0;
        g.globalAlpha = fade * k; g.fillStyle = "rgba(10,14,22,.86)"; g.strokeStyle = red ? RED : "rgba(255,255,255,.3)"; g.lineWidth = 3; RR(g, x + sh, PY, PW, PH, 12); g.fill(); g.stroke();
        const fh = Math.min(fill, 1) * (PH - 14); g.fillStyle = red ? RED : fill > 0.75 ? AMB : ACC; g.globalAlpha = fade * k * 0.85; RR(g, x + 7 + sh, PY + PH - 7 - fh, PW - 14, fh, 6); g.fill();
        if (red) { g.globalAlpha = fade; g.strokeStyle = "#fff"; g.lineWidth = 2.5; g.beginPath(); g.moveTo(x + 14 + sh, PY + 22); g.lineTo(x + 30 + sh, PY + 46); g.lineTo(x + 22 + sh, PY + 66); g.lineTo(x + 44 + sh, PY + 92); g.stroke(); }
      }
      ins.forEach((c) => {
        const u = (t - c.s) / 0.3; if (u < 0 || u > 1.5) return;
        const px = X0 + c.pg * (PW + PG) + PW / 2, e1 = ease3(Math.min(u, 1)), x = 495 + (clamp(px, 175, 815) - 495) * e1, y = 20 + (PY - 6 - 20) * e1, a = u > 1 ? clamp(1 - (u - 1) * 3, 0, 1) : 1;
        g.globalAlpha = fade * a; g.fillStyle = "rgba(255,194,51,.95)"; RR(g, x - 115, y - 17, 230, 34, 11); g.fill(); tx(g, c.id, x, y + 1, "800 22px PSans", INK);
        if (u > 1) { g.globalAlpha = fade * a * 0.6; g.strokeStyle = AMB; g.lineWidth = 3; g.beginPath(); g.arc(px, PY + PH / 2, 20 + (u - 1) * 50, 0, 6.283); g.stroke(); }
      });
      if (p.slow_t != null && t >= p.slow_t) {
        const k = clamp((t - p.slow_t) / 0.16, 0, 1), sc = 2.2 - 1.2 * ease3(k);
        g.save(); g.translate(540, 56); g.rotate(-0.04); g.scale(sc, sc); g.globalAlpha = fade * clamp((t - p.slow_t) / 0.08, 0, 1); g.fillStyle = "rgba(34,6,6,.92)"; g.strokeStyle = RED; g.lineWidth = 6; RR(g, -190, -38, 380, 76, 16); g.fill(); g.stroke();
        tx(g, "SLOW WRITES", 0, 3, "400 56px PAnton", "#ff6a58"); g.restore();
      }
      g.globalAlpha = 1;
    });
  };

  P.idbits = (p, e) => {                   // the 64-bit ID: 1 sign + 41 timestamp + 5 datacenter + 5 machine + 12 sequence; each part fills as it is spoken
    const g = band(e, p), X0 = 100, W = 830, BY = 104, BH = 62, bw = W / 64;
    const S = [{ n: 1, c: "rgba(255,255,255,.35)", t: p.t0 + 0.2 }, { n: 41, c: ACC, t: p.ts_t, l: "TIMESTAMP" }, { n: 5, c: AMB, t: p.dc_t, l: "DATACENTER ID", up: 1 },
               { n: 5, c: "#5ab8ff", t: p.mc_t, l: "MACHINE ID", up: 0 }, { n: 12, c: CORAL, t: p.sq_t, l: "SEQUENCE" }];
    let acc = 0; S.forEach((s) => { s.x = X0 + acc * bw; s.w = s.n * bw; acc += s.n; });
    PAINT.push((t) => {
      g.clearRect(0, 0, 1080, 250);
      if (t < p.t0 - 0.05 || t > p.t1 + 0.05) return;
      const fade = fadeOf(p, t), k0 = ease3((t - p.t0) / 0.3);
      g.globalAlpha = fade * k0; tx(g, "64 BITS", X0, 36, "400 54px PAnton", "#fff", "left");
      g.fillStyle = "rgba(10,14,22,.82)"; g.strokeStyle = "rgba(255,255,255,.3)"; g.lineWidth = 3; RR(g, X0 - 6, BY - 6, W + 12, BH + 12, 18); g.fill(); g.stroke();
      g.strokeStyle = "rgba(255,255,255,.12)"; g.lineWidth = 1.5; for (let i = 1; i < 64; i++) { g.beginPath(); g.moveTo(X0 + i * bw, BY + 6); g.lineTo(X0 + i * bw, BY + BH - 6); g.stroke(); }
      S.forEach((s) => {
        const u = ease3((t - s.t) / 0.38); if (u <= 0) return;
        g.globalAlpha = fade; g.fillStyle = s.c; if (u > 0 && u < 1) { g.shadowColor = s.c; g.shadowBlur = 22; }
        g.beginPath(); g.rect(s.x, BY, s.w * u, BH); g.fill(); g.shadowBlur = 0;
        if (s.l && u > 0.6) {
          const a = clamp((u - 0.6) / 0.4, 0, 1); g.globalAlpha = fade * a;
          if (s.up == null) tx(g, s.l, s.x + s.w / 2, BY + BH / 2 + 2, "800 30px PSans", INK);
          else { const ly = s.up ? 52 : 214, cx = s.x + s.w / 2; g.strokeStyle = s.c; g.lineWidth = 3; g.beginPath(); g.moveTo(cx, s.up ? ly + 16 : BY + BH); g.lineTo(cx, s.up ? BY : ly - 16); g.stroke(); tx(g, s.l, cx - (s.up ? 60 : 0), ly, "800 29px PSans", s.c); }
        }
      });
      g.globalAlpha = 1;
    });
  };

  P.idstream = (p, e) => {                 // one server, no coordinator (crossed out): it prints strictly increasing IDs, faster and faster, then SORTED
    const g = band(e, p), RX = 330, RW = 600, RH = 42, ids = [], X1 = p.rows_t;
    { let c = X1, i = 0; while (c < p.t1) { ids.push({ s: c, n: i }); c += Math.max(0.1, 0.3 - i * 0.02); i++; } }
    const idtxt = (n) => "17902847" + String(5532187461 + n).padStart(11, "0");
    PAINT.push((t) => {
      g.clearRect(0, 0, 1080, 250);
      if (t < p.t0 - 0.05 || t > p.t1 + 0.05) return;
      const fade = fadeOf(p, t), k = ease3((t - p.t0) / 0.3);
      g.globalAlpha = fade * k; tx(g, "SERVER", 190, 30, "800 28px PSans", "#fff");
      for (let i = 0; i < 3; i++) { const y = 56 + i * 54, on = Math.floor(t * 9) % 3; g.fillStyle = "rgba(24,30,44,.98)"; g.strokeStyle = ACC; g.lineWidth = 3.5; RR(g, 90, y, 200, 44, 12); g.fill(); g.stroke(); for (let q = 0; q < 3; q++) { g.fillStyle = (on + q + i) % 3 ? "rgba(255,255,255,.18)" : ACC; g.beginPath(); g.arc(116 + q * 27, y + 22, 7, 0, 6.283); g.fill(); } }
      if (t < p.x_t + 0.55) {              // the coordinator: struck out
        const a = ease3((t - p.t0 - 0.25) / 0.3) * clamp((p.x_t + 0.55 - t) / 0.25, 0, 1);
        g.globalAlpha = fade * a; g.setLineDash([10, 8]); g.strokeStyle = "rgba(255,255,255,.55)"; g.lineWidth = 3; RR(g, 520, 60, 380, 110, 22); g.stroke(); g.setLineDash([]);
        tx(g, "COORDINATOR", 710, 115, "800 40px PSans", "rgba(255,255,255,.9)");
        const x = ease3((t - p.x_t) / 0.16); if (x > 0) { g.strokeStyle = RED; g.lineWidth = 12; g.lineCap = "round"; g.shadowColor = RED; g.shadowBlur = 20; g.beginPath(); g.moveTo(560, 70); g.lineTo(560 + 300 * x, 70 + 90 * x); g.moveTo(860, 70); g.lineTo(860 - 300 * x, 70 + 90 * x); g.stroke(); g.shadowBlur = 0; }
      }
      const vis = ids.filter((c) => t >= c.s), last = vis.length - 1;
      vis.slice(-3).forEach((c, j, arr) => {
        const pos = arr.length - 1 - j, u = ease3((t - c.s) / 0.14), y = 50 + (2 - pos) * (RH + 8) - (1 - u) * 24, a = (pos === 2 ? 0.4 : 1) * u;
        g.globalAlpha = fade * a; g.fillStyle = "rgba(10,14,22,.88)"; g.strokeStyle = t >= p.sorted_t ? GRN : "rgba(255,255,255,.25)"; g.lineWidth = 2.5; RR(g, RX + 60, y, RW - 60, RH, 14); g.fill(); g.stroke();
        tx(g, idtxt(c.n), RX + 60 + (RW - 60) / 2, y + RH / 2 + 2, "800 29px PSans", pos === 0 ? "#fff" : "rgba(255,255,255,.78)");
        g.fillStyle = ACC; g.beginPath(); g.moveTo(RX + 22, y + 14); g.lineTo(RX + 42, y + RH / 2); g.lineTo(RX + 22, y + RH - 14); g.closePath(); g.fill();
      });
      if (t >= p.sorted_t) { const u = ease3((t - p.sorted_t) / 0.2); g.globalAlpha = fade * u; g.fillStyle = GRN; RR(g, 720, 0, 210, 44, 22); g.fill(); tx(g, "✓ SORTED", 825, 23, "800 28px PSans", INK); }
      g.globalAlpha = 1;
    });
  };

  P.clockback = (p, e) => {                // the system clock ticks 100..105 ms (ID chips), NTP rewinds it 5 ms, the next ID reuses a timestamp -> DUPLICATE
    const g = band(e, p), N = 6, CW = 118, GP = 14, X0 = (1080 - (N * CW + (N - 1) * GP)) / 2, CY = 56, step = p.step || 0.28;
    PAINT.push((t) => {
      g.clearRect(0, 0, 1080, 250);
      if (t < p.t0 - 0.05 || t > p.t1 + 0.05) return;
      const fade = fadeOf(p, t), dup = t >= p.dup_t, shake = dup && t < p.dup_t + 0.3 ? Math.sin(t * 90) * 4 : 0;
      const tick = clamp(Math.floor((t - p.tick_t) / step), -1, N - 1), back = clamp((t - p.rewind_t) / 0.4, 0, 1), ms = back > 0 ? Math.round(105 - 5 * back) : 100 + Math.max(0, tick);
      g.globalAlpha = fade * ease3((t - p.t0) / 0.3); tx(g, "ID TIMESTAMPS (ms)", X0, 22, "800 24px PSans", "rgba(255,255,255,.65)", "left");
      for (let i = 0; i < N; i++) {
        const u = ease3((t - (p.tick_t + i * step)) / 0.22); if (u <= 0) continue;
        const hot = dup && i === 0, x = X0 + i * (CW + GP) + (hot ? shake : 0);
        g.globalAlpha = fade * u; g.fillStyle = hot ? "rgba(255,77,61,.28)" : "rgba(10,14,22,.88)"; g.strokeStyle = hot ? RED : ACC; g.lineWidth = 3.5; RR(g, x, CY - 22 + (1 - u) * 14, CW, 56, 16); g.fill(); g.stroke();
        tx(g, String(100 + i), x + CW / 2, CY + 7 + (1 - u) * 14, "800 34px PSans", hot ? "#ff8f80" : "#fff");
      }
      if (t >= p.drop_t) {                 // the new ID drops onto the first chip
        const u = ease3((t - p.drop_t) / 0.3), x = X0, y = CY - 22 + (1 - u) * 120;
        g.globalAlpha = fade * clamp((t - p.drop_t) / 0.08, 0, 1) * (dup ? 0 : 1); g.fillStyle = "rgba(255,77,61,.4)"; g.strokeStyle = RED; g.lineWidth = 3.5; RR(g, x + 8, y + 6, CW - 16, 50, 16); g.fill(); g.stroke(); tx(g, "100", x + CW / 2, y + 33, "800 34px PSans", "#ff8f80");
      }
      g.globalAlpha = fade * ease3((t - p.t0 - 0.2) / 0.3); g.fillStyle = back > 0 ? "rgba(34,6,6,.92)" : "rgba(10,14,22,.9)"; g.strokeStyle = back > 0 ? RED : "rgba(255,255,255,.35)"; g.lineWidth = 3.5; RR(g, 330, 172, 420, 72, 22); g.fill(); g.stroke();
      tx(g, "CLOCK", 356, 208, "800 24px PSans", "rgba(255,255,255,.6)", "left"); tx(g, ms + " ms", 610, 210, "800 50px PSans", back > 0 ? "#ff6a58" : "#fff");
      if (t >= p.rewind_t) { const u = ease3((t - p.rewind_t) / 0.16), sc = 2 - u; g.save(); g.translate(836, 208); g.rotate(-0.06); g.scale(sc, sc); g.globalAlpha = fade * clamp((t - p.rewind_t) / 0.08, 0, 1); g.fillStyle = RED; RR(g, -92, -30, 184, 60, 14); g.fill(); tx(g, "−5 ms", 0, 3, "800 42px PSans", "#fff"); g.restore(); }
      if (dup) { const u = ease3((t - p.dup_t) / 0.16), sc = 2.2 - 1.2 * u; g.save(); g.translate(540, 130); g.rotate(-0.07); g.scale(sc, sc); g.globalAlpha = fade * clamp((t - p.dup_t) / 0.08, 0, 1); g.fillStyle = "rgba(34,6,6,.94)"; g.strokeStyle = RED; g.lineWidth = 7; g.shadowColor = RED; g.shadowBlur = 24; RR(g, -230, -38, 460, 76, 14); g.fill(); g.stroke(); g.shadowBlur = 0; tx(g, "DUPLICATE ID", 0, 3, "400 58px PAnton", "#ff6a58"); g.restore(); }
      g.globalAlpha = 1;
    });
  };

  /* ---------- notification-system props (23 Nov 2026, notification-system reel): ONE clogged queue (jam), HIGH / LOW priority lanes feeding SMS / EMAIL / PUSH
     workers (priority), exponential-backoff retries (retry), the same payment alert twice (dupe). Same rules: pure functions of t on one canvas, band y 285-535, content inside x 100-960. ---------- */
  const group = (n) => String(Math.round(n)).replace(/\B(?=(\d{3})+(?!\d))/g, ",");
  const stampAt = (g, t, t0, cx, cy, w, label, size, fade) => {
    if (t < t0) return; const k = clamp((t - t0) / 0.16, 0, 1), sc = 2.3 - 1.3 * ease3(k);
    g.save(); g.translate(cx, cy); g.rotate(-0.07); g.scale(sc, sc); g.globalAlpha = fade * clamp((t - t0) / 0.08, 0, 1); g.fillStyle = "rgba(34,6,6,.94)"; g.strokeStyle = RED; g.lineWidth = 7; g.shadowColor = RED; g.shadowBlur = 24;
    RR(g, -w / 2, -38, w, 76, 14); g.fill(); g.stroke(); g.shadowBlur = 0; tx(g, label, 0, 4, "400 " + size + "px PAnton", "#ff6a58"); g.restore();
  };
  const botAt = (g, x, y, r, busy, a) => {
    g.globalAlpha = a; g.fillStyle = "rgba(12,16,24,.96)"; g.strokeStyle = busy ? ACC : "rgba(255,255,255,.85)"; g.lineWidth = 3.5; if (busy) { g.shadowColor = ACC; g.shadowBlur = 20; }
    g.beginPath(); g.arc(x, y, r, 0, 6.283); g.fill(); g.stroke(); g.shadowBlur = 0; g.fillStyle = "#fff"; g.beginPath(); g.arc(x - r * 0.3, y - r * 0.15, r * 0.13, 0, 6.283); g.arc(x + r * 0.3, y - r * 0.15, r * 0.13, 0, 6.283); g.fill();
    g.strokeStyle = "#fff"; g.lineWidth = 3; g.beginPath(); g.arc(x, y + r * 0.08, r * 0.3, 0.25, 2.9); g.stroke();
  };

  P.jam = (p, e) => {                      // everything in ONE queue: promo chips flood in (counter to 10,000,000), the login OTP joins at the very back and waits -> STUCK -> USER DROP-OFF
    const g = band(e, p), LX = 100, LW = 700, LY = 84, LH = 72, CW = 108, CH = 40, PIT = 36, NV = 11, WX = 862, WY = LY + LH / 2, OX = LX + 12;
    const fl = p.flood_t, ot = p.otp_t, st = p.stuck_t, dr = p.drop_t, DR = 0.8, D0 = fl + 0.7, chips = [];
    { let c = fl, i = 0; while (c < p.t1) { chips.push(c); c += Math.max(0.06, 0.32 - i * 0.03); i++; } }
    const slot = (pos) => LX + LW - 14 - CW - Math.min(pos, NV - 1) * PIT, CY = LY + (LH - CH) / 2;
    PAINT.push((t) => {
      g.clearRect(0, 0, 1080, 250);
      if (t < p.t0 - 0.05 || t > p.t1 + 0.05) return;
      const fade = fadeOf(p, t), k0 = ease3((t - p.t0) / 0.3), drain = Math.max(0, (t - D0) / DR);
      g.globalAlpha = fade * k0; tx(g, "SINGLE QUEUE", LX, 40, "800 30px PSans", "#fff", "left");
      g.fillStyle = "rgba(10,14,22,.86)"; g.strokeStyle = t >= st ? "rgba(255,77,61,.7)" : "rgba(255,255,255,.3)"; g.lineWidth = 3; RR(g, LX, LY, LW, LH, 20); g.fill(); g.stroke();
      if (t >= fl) {                       // counter
        const n = 10000000 * ease3((t - fl) / Math.max(0.5, ot - fl - 0.3));
        g.globalAlpha = fade; tx(g, group(n), LX + LW - 138, 40, "800 36px PSans", AMB, "right"); tx(g, "PROMOS", LX + LW - 126, 41, "800 28px PSans", "rgba(255,255,255,.75)", "left");
      }
      for (let j = chips.length - 1; j >= 0; j--) {   // promo chips: drop in at the back of the visible queue, the head drains into the worker (conveyor)
        const s = chips[j]; if (t < s) continue;
        const pos = j - drain, u = clamp((t - s) / 0.22, 0, 1);
        let x = slot(pos), y = CY - (1 - ease3(u)) * 70, a = u;
        if (pos < 0) { const w = (t - (D0 + j * DR)) / 0.25; if (w > 1) continue; x = slot(0) + (WX - 30 - slot(0)) * ease3(w); a = 1 - w; }
        g.globalAlpha = fade * a; g.fillStyle = "rgba(255,194,51,.95)"; g.strokeStyle = "rgba(10,14,22,.9)"; g.lineWidth = 2; RR(g, x, y, CW, CH, 11); g.fill(); g.stroke(); tx(g, "PROMO", x + CW / 2, y + CH / 2 + 2, "800 26px PSans", INK);
      }
      g.globalAlpha = fade * 0.7; tx(g, "· · ·", (OX + CW + slot(NV - 1)) / 2, WY + 2, "800 34px PSans", "rgba(255,255,255,.55)");
      const bad = t >= st, sh = bad && t < st + 0.45 ? Math.sin(t * 90) * 4 : 0;       // the OTP, last in line
      if (t >= ot) {
        const u = ease3((t - ot) / 0.35);
        g.globalAlpha = fade * u; g.fillStyle = bad ? "rgba(255,77,61,.9)" : GRN; g.strokeStyle = "rgba(10,14,22,.9)"; g.lineWidth = 2; if (bad) { g.shadowColor = RED; g.shadowBlur = 22; }
        RR(g, OX + sh, CY - (1 - u) * 80, CW, CH, 11); g.fill(); g.stroke(); g.shadowBlur = 0; tx(g, "OTP", OX + CW / 2 + sh, CY - (1 - u) * 80 + CH / 2 + 2, "800 28px PSans", bad ? "#fff" : INK);
        const cx = OX + 22, cy = LY + LH + 40;           // waiting spinner -> STUCK tag
        g.globalAlpha = fade * u;
        if (!bad) { const sp = (t - ot) * 6; g.strokeStyle = "#fff"; g.lineWidth = 5; g.lineCap = "round"; g.beginPath(); g.arc(cx, cy, 15, sp, sp + 4.4); g.stroke(); }
        else tx(g, "STUCK", OX, cy, "800 32px PSans", "#ff6a58", "left");
      }
      botAt(g, WX, WY, 28, t >= D0 && (Math.floor(t * 7) % 2 === 0), fade * k0); g.globalAlpha = fade * k0; tx(g, "WORKER", WX, WY + 52, "800 28px PSans", "rgba(255,255,255,.8)");
      stampAt(g, t, dr, 560, 203, 470, "USER DROP-OFF", 54, fade);
      g.globalAlpha = 1;
    });
  };

  P.priority = (p, e) => {                 // two lanes: HIGH PRIORITY (OTP / PAY, fast) and LOW PRIORITY (PROMO, slow) feed a pool of per-channel workers: SMS, EMAIL, PUSH
    const g = band(e, p), LX = 100, PX = 736, CH = 42, LANE = 54;
    const L = [{ ly: 40, lab: "HIGH PRIORITY", col: GRN, t: p.hi_t, cross: 0.85, gap: 0.5, names: ["OTP", "PAY", "OTP", "PAY"], w: 96 },
               { ly: 158, lab: "LOW PRIORITY", col: AMB, t: p.lo_t, cross: 2.5, gap: 0.55, names: ["PROMO"], w: 116 }];
    L.forEach((ln) => { ln.chips = []; let c = ln.t, i = 0; while (c < p.t1) { ln.chips.push({ s: c, name: ln.names[i % ln.names.length], i }); c += ln.gap; i++; } });
    const BN = ["SMS", "EMAIL", "PUSH"], BY = [76, 140, 204], PT = p.pool_ts || [p.pool_t, p.pool_t + 0.12, p.pool_t + 0.24], PS = p.pool_show != null ? p.pool_show : PT[0] - 0.3;
    PAINT.push((t) => {
      g.clearRect(0, 0, 1080, 250);
      if (t < p.t0 - 0.05 || t > p.t1 + 0.05) return;
      const fade = fadeOf(p, t), pk = ease3((t - PS) / 0.3);
      g.globalAlpha = fade * pk; g.fillStyle = "rgba(10,14,22,.86)"; g.strokeStyle = "rgba(255,255,255,.4)"; g.lineWidth = 3; RR(g, PX, 8, 224, 234, 22); g.fill(); g.stroke();
      if (pk > 0) { g.globalAlpha = fade * pk; tx(g, "WORKERS", PX + 112, 34, "800 28px PSans", ACC); }
      const busy = [0, 0, 0];
      L.forEach((ln, li) => {
        const k = ease3((t - (li ? (p.lo_show != null ? p.lo_show : ln.t - 0.5) : p.t0)) / 0.3); if (k <= 0) return;
        g.globalAlpha = fade * k; tx(g, ln.lab, LX, ln.ly - 17, "800 29px PSans", ln.col, "left");
        g.fillStyle = "rgba(10,14,22,.86)"; g.strokeStyle = "rgba(255,255,255,.28)"; g.lineWidth = 3; RR(g, LX, ln.ly, PX - 8 - LX, LANE, 18); g.fill(); g.stroke();
        ln.chips.forEach((c) => {
          const u = (t - c.s) / ln.cross; if (u < 0 || u > 1.2) return;
          const x = LX + 8 + Math.min(u, 1) * (PX - 8 - ln.w - 16 - LX), a = u > 1 ? clamp(1 - (u - 1) * 5, 0, 1) : clamp(u * 8, 0, 1);
          if (u > 0.96 && u < 1.2) busy[c.i % 3] = 1;
          g.globalAlpha = fade * a; g.fillStyle = li ? "rgba(10,14,22,.9)" : GRN; g.strokeStyle = ln.col; g.lineWidth = 3; RR(g, x, ln.ly + (LANE - CH) / 2, ln.w, CH, 11); g.fill(); g.stroke();
          tx(g, c.name, x + ln.w / 2, ln.ly + LANE / 2 + 2, "800 27px PSans", li ? AMB : INK);
        });
      });
      BN.forEach((nm, i) => {
        const k = ease3((t - PS - i * 0.1) / 0.3), la = ease3((t - PT[i]) / 0.25); if (k <= 0) return;
        botAt(g, PX + 52, BY[i], 24 * k, busy[i] && pk >= 1, fade * k); g.globalAlpha = fade * la; tx(g, nm, PX + 92, BY[i] + 2, "800 30px PSans", "#fff", "left");
      });
      g.globalAlpha = 1;
    });
  };

  P.retry = (p, e) => {                    // a PAY notification times out and retries with DOUBLING waits: x, 1x, x, 2x, x, 4x, then it lands
    const g = band(e, p), X = [190, 270, 430, 750], Y = 118, H = p.hops, HS = [0, 1, 2].map((i) => H[i + 1] - Math.min(0.35, 0.7 * (H[i + 1] - H[i])));
    PAINT.push((t) => {
      g.clearRect(0, 0, 1080, 250);
      if (t < p.t0 - 0.05 || t > p.t1 + 0.05) return;
      const fade = fadeOf(p, t), k0 = ease3((t - p.t0) / 0.3);
      g.globalAlpha = fade * k0; g.strokeStyle = "rgba(255,255,255,.22)"; g.lineWidth = 4; g.setLineDash([3, 12]); g.lineCap = "round"; g.beginPath(); g.moveTo(X[0], Y); g.lineTo(X[3], Y); g.stroke(); g.setLineDash([]);
      for (let i = 0; i < 3; i++) {         // wait brackets 1x / 2x / 4x grow while the worker waits
        const w = clamp((t - H[i] - 0.15) / Math.max(0.2, H[i + 1] - H[i] - 0.5), 0, 1); if (w <= 0) continue;
        const a = X[i] + 26, b = a + (X[i + 1] - X[i] - 52) * ease3(w);
        g.globalAlpha = fade; g.strokeStyle = ACC; g.lineWidth = 4; g.beginPath(); g.moveTo(a, Y + 52); g.lineTo(b, Y + 52); g.moveTo(a, Y + 42); g.lineTo(a, Y + 62); g.moveTo(b, Y + 42); g.lineTo(b, Y + 62); g.stroke();
        if (w > 0.85) tx(g, ["1×", "2×", "4×"][i], (X[i] + X[i + 1]) / 2, Y + 96, "800 34px PSans", ACC);
      }
      for (let i = 0; i < 4; i++) {          // attempt nodes: x x x then a tick
        const u = ease3((t - H[i]) / 0.22), ok = i === 3;
        g.globalAlpha = fade * k0; g.fillStyle = "rgba(10,14,22,.9)"; g.strokeStyle = t >= H[i] ? (ok ? GRN : RED) : "rgba(255,255,255,.4)"; g.lineWidth = 4; g.beginPath(); g.arc(X[i], Y, 27, 0, 6.283); g.fill(); g.stroke();
        if (u > 0) { g.globalAlpha = fade * u; g.strokeStyle = ok ? GRN : RED; g.lineWidth = 6; g.lineCap = "round"; g.beginPath(); if (ok) { g.moveTo(X[i] - 12, Y + 1); g.lineTo(X[i] - 3, Y + 11); g.lineTo(X[i] + 13, Y - 10); } else { g.moveTo(X[i] - 11, Y - 11); g.lineTo(X[i] + 11, Y + 11); g.moveTo(X[i] + 11, Y - 11); g.lineTo(X[i] - 11, Y + 11); } g.stroke(); }
      }
      let cx = 40, cy = Y - 62, ca = clamp((t - p.t0) / 0.2, 0, 1);       // the PAY chip hops node to node
      if (t < H[0]) { const w = ease3((t - p.t0 - 0.1) / Math.max(0.2, H[0] - p.t0 - 0.1)); cx = 40 + (X[0] - 40) * w; cy = Y - 62 + 62 * w; }
      else { let node = 0, f = 0; for (let i = 0; i < 3; i++) { if (t >= H[i + 1]) node = i + 1; else if (t >= HS[i]) { node = i; f = ease3((t - HS[i]) / (H[i + 1] - HS[i])); } } cx = X[node] + ((X[node + 1] != null ? X[node + 1] : X[node]) - X[node]) * f; cy = Y - 52 - Math.sin(Math.PI * f) * 46; }
      g.globalAlpha = fade * ca; g.fillStyle = AMB; RR(g, cx - 40, cy - 20, 80, 40, 12); g.fill(); tx(g, "PAY", cx, cy + 2, "800 28px PSans", INK);
      g.globalAlpha = 1;
    });
  };

  P.dupe = (p, e) => {                     // a payment alert is sent, the ack times out, the worker retries and the SAME alert pops up again -> DUPLICATE
    const g = band(e, p), CX = 190, CWd = 600, CHt = 78;
    const card = (y, t0, t, fade, dup) => {
      const u = ease3((t - t0) / 0.3); if (u <= 0) return;
      g.globalAlpha = fade * u; g.fillStyle = "rgba(10,14,22,.92)"; g.strokeStyle = dup ? RED : "rgba(255,255,255,.35)"; g.lineWidth = dup ? 4.5 : 3; if (dup) { g.shadowColor = RED; g.shadowBlur = 20; }
      RR(g, CX, y - (1 - u) * 60, CWd, CHt, 22); g.fill(); g.stroke(); g.shadowBlur = 0;
      g.fillStyle = GRN; RR(g, CX + 16, y - (1 - u) * 60 + 15, 48, 48, 13); g.fill(); g.strokeStyle = INK; g.lineWidth = 6; g.lineCap = "round"; const yy = y - (1 - u) * 60; g.beginPath(); g.moveTo(CX + 28, yy + 40); g.lineTo(CX + 38, yy + 50); g.lineTo(CX + 54, yy + 28); g.stroke();
      tx(g, "Payment successful", CX + 82, y - (1 - u) * 60 + 40, "800 34px PSans", "#fff", "left"); tx(g, "now", CX + CWd - 20, y - (1 - u) * 60 + 40, "700 27px PSans", "rgba(255,255,255,.55)", "right");
    };
    PAINT.push((t) => {
      g.clearRect(0, 0, 1080, 250);
      if (t < p.t0 - 0.05 || t > p.t1 + 0.05) return;
      const fade = fadeOf(p, t), dup = t >= p.dup_t, sh = dup && t < p.dup_t + 0.4 ? Math.sin(t * 90) * 4 : 0;
      g.save(); g.translate(sh, 0); card(8, p.card1_t, t, fade, dup); card(94, p.card2_t, t, fade, dup); g.restore();
      if (t >= p.timeout_t && t < p.card2_t + 0.3) {          // ack lost -> retry arrow
        const u = ease3((t - p.timeout_t) / 0.25), a = fade * u * clamp((p.card2_t + 0.3 - t) / 0.2, 0, 1);
        g.globalAlpha = a; g.fillStyle = "rgba(255,77,61,.16)"; g.strokeStyle = RED; g.lineWidth = 3.5; RR(g, 812, 28, 148, 52, 14); g.fill(); g.stroke(); tx(g, "TIMEOUT", 886, 55, "800 27px PSans", "#ff8f80");
        g.strokeStyle = ACC; g.lineWidth = 5; g.lineCap = "round"; g.beginPath(); g.moveTo(886, 86); g.quadraticCurveTo(900, 140, 806, 152); g.stroke(); g.fillStyle = ACC; g.beginPath(); g.moveTo(798, 152); g.lineTo(816, 140); g.lineTo(816, 164); g.closePath(); g.fill();
        tx(g, "RETRY", 906, 176, "800 28px PSans", ACC);
      }
      stampAt(g, t, p.dup_t, 560, 212, 410, "SENT TWICE", 54, fade);
      g.globalAlpha = 1;
    });
  };

  (K.props || []).forEach((p) => { const e = mk("div", "k-prop", WB); (P[p.kind] || (() => {}))(p, e); });
  if (PAINT.length) {
    const st = { t: 0 };
    tl.fromTo(st, { t: 0 }, { t: END, duration: END, ease: "none", ...IM, onUpdate() { PAINT.forEach((f) => f(st.t)); } }, 0);
  }
}
