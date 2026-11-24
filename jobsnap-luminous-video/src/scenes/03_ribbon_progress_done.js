/* Shot 4 & 5 (10.70s – 15.88s) — Locked to real narration:
   10.7s "Our AI scans live roles and scores your fit in seconds." -> 14.8s "Done." */
{
  const s4 = scene("s4", 10.70, 15.88);

  /* 9.94–10.65s: Curved Luminous Ribbon shooting OUT from behind the left iPhone bezel (exact reference 00:10 shot — zero exposed left edge!) */
  const rib = svgEl(
    s4,
    0,
    0,
    VW,
    VH,
    `
      <defs>
        <linearGradient id="ribGrad" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" stop-color="#4F46E5"/>
          <stop offset="48%" stop-color="#3B82F6"/>
          <stop offset="86%" stop-color="#38BDF8"/>
          <stop offset="100%" stop-color="#38BDF8" stop-opacity="0"/>
        </linearGradient>
      </defs>
      <path id="rib-p" d="M 0 0 L 290 0 C 560 320, 960 400, 1860 445 L 1860 635 C 960 680, 560 760, 290 1080 L 0 1080 Z" fill="url(#ribGrad)" />
    `
  );
  /* Carry-over Left iPhone sitting ON TOP of the ribbon's left edge, then gliding off as the ribbon morphs into the progress bar */
  const launchPhone = mk(s4, "iphone", "left:-92px; top:110px; z-index:4; border:1.5px solid rgba(255,255,255,0.22); box-shadow:0 36px 90px rgba(0,0,0,0.55), 0 0 40px rgba(59,130,246,0.18);");
  launchPhone.innerHTML = `
    <div class="iphone-island"></div>
    <div class="iphone-scr">
      <div class="mono" style="font-size:14px;color:#2563EB;font-weight:600;">LIVE AGGREGATOR</div>
      <div style="font-size:28px;font-weight:700;margin-top:8px;">Top Matches</div>
      <div style="margin-top:20px;display:flex;flex-direction:column;gap:14px;">
        <div style="padding:16px;border-radius:16px;background:#EFF6FF;border:1px solid #BFDBFE;"><div style="font-size:19px;font-weight:700;">Senior Full-Stack</div><div style="font-size:15px;color:#475569;margin-top:4px;">Stripe · 96% Match</div></div>
        <div style="padding:16px;border-radius:16px;background:#F8FAFC;border:1px solid #E2E8F0;"><div style="font-size:19px;font-weight:700;">AI Product Engineer</div><div style="font-size:15px;color:#475569;margin-top:4px;">Linear · 94% Match</div></div>
        <div style="padding:16px;border-radius:16px;background:#ECFDF5;border:1px solid #A7F3D0;"><div style="font-size:19px;font-weight:700;">Staff Frontend</div><div style="font-size:15px;color:#065F46;margin-top:4px;">Vercel · 92% Match</div></div>
      </div>
    </div>
  `;
  tl.fromTo(rib, { scaleX: 0.15, transformOrigin: "260px 540px", opacity: 0 }, { scaleX: 1, opacity: 1, duration: 0.44, ease: "power3.out" }, 10.70);
  tl.to(launchPhone, { x: -460, opacity: 0, duration: 0.42, ease: "power3.in" }, 11.02);
  tl.to(rib, { scaleY: 0.12, opacity: 0, transformOrigin: "0% 50%", duration: 0.36, ease: "power3.inOut" }, 11.16);

  /* 11.30–14.60s: Oversized Luminous Progress Bar climbing across "scores your fit in seconds" */
  const barWrap = mk(s4, "abs", "inset:0; opacity:0;");
  barWrap.innerHTML = `
    <div id="p-cnt-wrap" style="position:absolute; left:1120px; top:324px; font-size:94px; font-weight:400; letter-spacing:-0.03em; font-variant-numeric:tabular-nums;">
      <span id="p-cnt" style="color:#38BDF8;">0</span><span style="color:rgba(248,250,252,0.38);">/100</span>
    </div>
    <div class="prog-track" style="background:rgba(255,255,255,0.09); border:1.5px solid rgba(255,255,255,0.14); box-shadow:0 28px 90px rgba(56,189,248,0.32);">
      <div id="p-fill" class="prog-fill"></div>
    </div>
  `;
  const pFill = barWrap.querySelector("#p-fill");
  const pCnt  = barWrap.querySelector("#p-cnt");
  const pCntWrap = barWrap.querySelector("#p-cnt-wrap");

  tl.to(barWrap, { opacity: 1, duration: 0.28 }, 11.30);
  tl.fromTo(pFill, { scaleX: 0.14 }, { scaleX: 0.99, duration: 3.15, ease: "power2.out" }, 11.32);
  tl.fromTo(pCntWrap, { x: -240 }, { x: 160, duration: 3.15, ease: "power2.out" }, 11.32);
  counter(pCnt, 12, 100, 11.32, 3.05, (v) => String(Math.round(v)));
  tl.to(barWrap, { opacity: 0, scale: 0.85, filter: "blur(12px)", duration: 0.26, ease: "power2.in" }, 14.48);

  /* 14.76–15.85s: "Done." lands RIGHT on the spoken word "Done" at 14.8s! */
  const doneTxt = mk(s4, "lt", "left:0; width:1920px; top:208px; text-align:center; font-size:84px; font-weight:600; color:#1D4ED8;", `Done`);
  blurIn(doneTxt, 14.75, 0.28, { y: 20, blur: 10 });
  blurOut(doneTxt, 15.42, 0.22, { y: -18, blur: 10 });

  const sphere = mk(
    s4,
    "abs",
    "left:820px; top:390px; width:280px; height:280px; border-radius:50%; background:radial-gradient(circle at 30% 25%, #FFFFFF 0%, #EFF6FF 58%, #BFDBFE 100%); border:3px solid rgba(59,130,246,0.55); box-shadow:0 28px 80px rgba(59,130,246,0.28), inset 0 6px 18px rgba(255,255,255,0.9); display:flex; align-items:center; justify-content:center; opacity:0;"
  );
  sphere.innerHTML = `<svg width="124" height="124" viewBox="0 0 120 120"><path id="chk-p" d="M 28 62 L 52 86 L 94 36" fill="none" stroke="#2563EB" stroke-width="8" stroke-linecap="round" stroke-linejoin="round"/></svg>`;
  tl.fromTo(sphere, { scale: 0.55, opacity: 0 }, { scale: 1, opacity: 1, duration: 0.36, ease: "back.out(1.7)" }, 14.74);
  stroke(sphere.querySelector("#chk-p"), 14.82, 0.36, "power2.out");

  const confColors = ["#2563EB", "#38BDF8", "#10B981", "#818CF8", "#F472B6"];
  for (let i = 0; i < 18; i++) {
    const ang = (i / 18) * Math.PI * 2 + (hash(i + 1) - 0.5) * 0.35;
    const dist = 340 + hash(i + 20) * 380;
    const cw = 18 + Math.round(hash(i + 40) * 28);
    const ch = 12 + Math.round(hash(i + 60) * 22);
    const col = confColors[i % confColors.length];
    const cf = mk(s4, "abs", `left:960px; top:530px; width:${cw}px; height:${ch}px; background:${col}; border-radius:4px; opacity:0; pointer-events:none;`);
    tl.fromTo(cf, { x: 0, y: 0, rotation: 0, scale: 0.3, opacity: 0 }, { x: Math.cos(ang) * dist, y: Math.sin(ang) * dist - 60, rotation: (hash(i + 80) - 0.5) * 420, scale: 1, opacity: 1, duration: 0.52, ease: "power3.out" }, 14.80 + (i % 4) * 0.02);
    tl.to(cf, { opacity: 0, y: "+=60", duration: 0.32, ease: "power2.in" }, 15.32);
  }
  tl.to(sphere.querySelector("#chk-p"), { opacity: 0, duration: 0.18 }, 15.40);
  tl.to(sphere, { borderRadius: "54px", width: 340, height: 340, left: 790, top: 370, background: "#FFFFFF", boxShadow: "0 0 80px rgba(59,130,246,0.34)", duration: 0.28, ease: "power3.inOut" }, 15.42);
  tl.to(sphere, { scale: 2.2, opacity: 0, duration: 0.24, ease: "power2.in" }, 15.65);
}
