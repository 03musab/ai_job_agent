/* Shot 8 (25.18s – 32.0s) -Locked to real narration:
   25.5s "Match. Fill. Land." -> 27.6s "JobSnap -at jobsnap.me." */
{
  const s8 = scene("s8", 25.18, null);

  const arcSvg = svgEl(
    s8,
    0,
    0,
    VW,
    VH,
    `
      <defs>
        <linearGradient id="arcGrad" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" stop-color="#38BDF8" stop-opacity="0"/>
          <stop offset="50%" stop-color="#60A5FA" stop-opacity="0.32"/>
          <stop offset="100%" stop-color="#3B82F6" stop-opacity="0.55"/>
        </linearGradient>
      </defs>
      <path id="sp-arc" d="M 520 560 Q 760 400 1020 530 T 1420 460" fill="none" stroke="url(#arcGrad)" stroke-width="26" stroke-linecap="round"/>
    `
  );
  stroke(arcSvg.querySelector("#sp-arc"), 25.45, 0.85, "power2.inOut");
  tl.to(arcSvg, { opacity: 0, duration: 0.35 }, 26.55);

  const star = mk(s8, "abs", "left:900px; top:480px; width:120px; height:120px; filter:drop-shadow(0 14px 36px rgba(59,130,246,0.45)); opacity:0;", SPARKLE_SVG(120));
  tl.fromTo(star, { scale: 0.2, rotation: -90, opacity: 0 }, { scale: 1.15, rotation: 0, opacity: 1, duration: 0.36, ease: "back.out(1.8)" }, 25.18);
  tl.to(star, { x: 382, y: -6, scale: 0.52, rotation: 180, duration: 1.15, ease: "power3.inOut" }, 25.52);
  tl.to(star, { scale: 0, opacity: 0, rotation: 300, duration: 0.28, ease: "power2.in" }, 27.25);

  const wRow = mk(s8, "lt", "left:0; width:1920px; top:486px; text-align:center; font-size:90px; font-weight:500; display:flex; justify-content:center; align-items:center; gap:26px;");
  const t1 = mk(wRow, "", "position:relative; color:#60A5FA;", "Match.");
  const t2 = mk(wRow, "", "position:relative; color:#34D399;", "Fill.");
  const t3 = mk(wRow, "", "position:relative; color:#F8FAFC; padding-right:56px;", "Land");

  blurIn(t1, 25.52, 0.36, { x: -24, blur: 12 });
  blurIn(t2, 26.12, 0.36, { x: -18, blur: 12 });
  blurIn(t3, 26.68, 0.36, { x: -18, blur: 12 });
  blurOut(wRow, 27.25, 0.28, { scale: 0.92, blur: 12 });

  const endCenter = mk(s8, "abs", "inset:0; display:flex; flex-direction:column; align-items:center; justify-content:center; text-align:center;");
  const lockup = mk(endCenter, "", "display:inline-flex; align-items:center; justify-content:center; gap:26px; opacity:0;");
  lockup.innerHTML = `<div id="fin-logo" style="filter:drop-shadow(0 16px 34px rgba(16,185,129,0.28));">${LOGO_SVG(102)}</div><div style="font-size:108px;font-weight:600;letter-spacing:-0.035em;color:#0F172A;line-height:1;">JobSnap</div>`;
  const dom = mk(endCenter, "", "margin-top:34px; font-size:34px; font-weight:500; color:#475569; letter-spacing:0.015em; opacity:0;", `jobsnap.me`);

  /* Lands RIGHT ON "JobSnap" (27.65s) and "at jobsnap.me" (28.35s) */
  tl.fromTo(lockup, { opacity: 0, scale: 0.94, y: 12, filter: "blur(10px)" }, { opacity: 1, scale: 1, y: 0, filter: "blur(0px)", duration: 0.58, ease: "power3.out" }, 27.62);
  tl.fromTo(dom, { opacity: 0, y: 14, filter: "blur(6px)" }, { opacity: 1, y: 0, filter: "blur(0px)", duration: 0.52, ease: "power2.out" }, 28.32);
  tl.to(endCenter, { scale: 1.025, duration: 3.4, ease: "none" }, 28.5);
}
