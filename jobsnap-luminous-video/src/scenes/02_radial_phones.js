/* Shot 3 (4.35s – 10.75s) — Locked to real narration:
   4.35s "Just drop it into JobSnap." -> 6.0s "Jobs, match scores, and one-click applications — all in one platform." */
{
  const s3 = scene("s3", 4.35, 10.78);

  const lineDrop = mk(s3, "lt", "left:0; width:1920px; top:486px; text-align:center; font-size:80px; font-weight:600; color:#FFFFFF; text-shadow:0 8px 36px rgba(0,0,0,0.45);", `<span style="color:#93C5FD;">Just drop it</span> <span>into JobSnap</span>`);
  blurIn(lineDrop, 4.38, 0.36, { y: 18, blur: 12 });
  blurOut(lineDrop, 5.72, 0.26, { scale: 0.92, blur: 12 });

  const c1 = mk(s3, "lt", "left:0; width:1920px; top:496px; text-align:center; font-size:64px; font-weight:600; color:#FFFFFF; text-shadow:0 6px 30px rgba(0,0,0,0.45);", `Jobs.`);
  blurIn(c1, 6.00, 0.32, { scale: 0.94, blur: 10 });
  blurOut(c1, 6.72, 0.22, { blur: 8 });

  const c2 = mk(s3, "lt", "left:0; width:1920px; top:496px; text-align:center; font-size:60px; font-weight:600; color:#FFFFFF; text-shadow:0 6px 32px rgba(0,0,0,0.42);", `Jobs. Match. Apply`);
  blurIn(c2, 6.88, 0.36, { scale: 0.95, blur: 10 });
  blurOut(c2, 8.78, 0.24, { blur: 10 });

  const c3 = mk(s3, "lt", "left:0; width:1920px; top:496px; text-align:center; font-size:58px; font-weight:600; color:#FFFFFF; text-shadow:0 6px 32px rgba(0,0,0,0.45);", `All In One Platform`);
  blurIn(c3, 8.92, 0.36, { scale: 0.95, blur: 10 });
  blurOut(c3, 10.42, 0.26, { x: 160, blur: 14 });

  /* Helper for the 4 radial iPhones (crisp rim-light border so bezels gleam on dark obsidian) */
  function makePhone(css, screenHtml) {
    const p = mk(s3, "iphone", css + " border:1.5px solid rgba(255,255,255,0.22); box-shadow:0 36px 90px rgba(0,0,0,0.55), 0 0 40px rgba(59,130,246,0.18);");
    p.innerHTML = `<div class="iphone-island"></div><div class="iphone-scr">${screenHtml}</div>`;
    return p;
  }

  /* 1. Left Phone (Job Match Feed) */
  const pL = makePhone(
    "left:-72px; top:110px; transform-origin:center center;",
    `
      <div class="mono" style="font-size:14px;color:#2563EB;font-weight:600;">LIVE AGGREGATOR</div>
      <div style="font-size:28px;font-weight:700;margin-top:8px;">Top Matches</div>
      <div style="margin-top:20px;display:flex;flex-direction:column;gap:14px;">
        <div style="padding:16px;border-radius:16px;background:#EFF6FF;border:1px solid #BFDBFE;">
          <div style="font-size:19px;font-weight:700;">Senior Full-Stack</div>
          <div style="font-size:15px;color:#475569;margin-top:4px;">Stripe · 96% Match</div>
        </div>
        <div style="padding:16px;border-radius:16px;background:#F8FAFC;border:1px solid #E2E8F0;">
          <div style="font-size:19px;font-weight:700;">AI Product Engineer</div>
          <div style="font-size:15px;color:#475569;margin-top:4px;">Linear · 94% Match</div>
        </div>
        <div style="padding:16px;border-radius:16px;background:#ECFDF5;border:1px solid #A7F3D0;">
          <div style="font-size:19px;font-weight:700;">Staff Frontend</div>
          <div style="font-size:15px;color:#065F46;margin-top:4px;">Vercel · 92% Match</div>
        </div>
      </div>
    `
  );

  /* 2. Right Phone (AI Resume Match Score) */
  const pR = makePhone(
    "right:-72px; top:110px; transform-origin:center center;",
    `
      <div class="mono" style="font-size:14px;color:#059669;font-weight:600;">AI RESUME ENGINE</div>
      <div style="font-size:28px;font-weight:700;margin-top:8px;">Skill Match</div>
      <div style="margin-top:24px;padding:22px;border-radius:20px;background:linear-gradient(135deg,#EFF6FF,#ECFDF5);text-align:center;">
        <div style="font-size:58px;font-weight:700;color:#2563EB;">96%</div>
        <div style="font-size:16px;color:#0F172A;font-weight:600;margin-top:4px;">High Compatibility</div>
      </div>
      <div style="margin-top:18px;display:flex;flex-wrap:wrap;gap:8px;">
        <span class="saas-chip" style="background:#EFF6FF;color:#2563EB;">✓ TypeScript</span>
        <span class="saas-chip" style="background:#ECFDF5;color:#059669;">✓ Python</span>
        <span class="saas-chip" style="background:#EFF6FF;color:#2563EB;">✓ Flask</span>
      </div>
    `
  );

  /* 3. Top Phone (horizontal / tilted from top edge) */
  const pT = makePhone(
    "left:740px; top:-530px; transform-origin:center center;",
    `
      <div style="position:absolute;bottom:34px;left:28px;right:28px;">
        <div class="mono" style="font-size:14px;color:#2563EB;">CAREER ROADMAP</div>
        <div style="font-size:24px;font-weight:700;margin-top:6px;">Close Skill Gaps Faster</div>
        <div style="height:10px;border-radius:999px;background:#E2E8F0;margin-top:12px;overflow:hidden;">
          <div style="width:82%;height:100%;background:linear-gradient(90deg,#3B82F6,#10B981);"></div>
        </div>
      </div>
    `
  );

  /* 4. Bottom Phone (tilted from bottom edge) */
  const pB = makePhone(
    "left:740px; top:750px; transform-origin:center center;",
    `
      <div style="display:flex;justify-content:space-between;align-items:center;">
        <span class="mono" style="font-size:14px;color:#059669;font-weight:600;">1-CLICK ATS COPILOT</span>
        <span class="saas-chip" style="background:#ECFDF5;color:#059669;">SYNCED</span>
      </div>
      <div style="font-size:24px;font-weight:700;margin-top:12px;">Workday · Greenhouse · Lever</div>
      <div style="margin-top:16px;padding:14px;border-radius:14px;background:#0F172A;color:#FFFFFF;text-align:center;font-size:17px;font-weight:600;">Auto-Fill Complete ✓</div>
    `
  );

  /* Radial choreography synced to 5.1s–10.7s */
  tl.fromTo(pL, { x: -560, y: 240, rotation: 28, opacity: 0 }, { x: 110, y: 0, rotation: 16, opacity: 1, duration: 0.85, ease: "power3.out" }, 5.15);
  tl.fromTo(pR, { x: 560, y: -220, rotation: -28, opacity: 0 }, { x: -110, y: 0, rotation: -16, opacity: 1, duration: 0.85, ease: "power3.out" }, 5.75);
  tl.fromTo(pT, { y: -320, rotation: -98, opacity: 0 }, { y: 40, rotation: -84, opacity: 1, duration: 0.8, ease: "power3.out" }, 5.85);
  tl.fromTo(pB, { y: 320, rotation: 98, opacity: 0 }, { y: -36, rotation: 84, opacity: 1, duration: 0.8, ease: "power3.out" }, 5.92);

  tl.to(pL, { rotation: 7, x: 150, duration: 3.5, ease: "sine.inOut" }, 6.7);
  tl.to(pR, { rotation: -7, x: -150, duration: 3.5, ease: "sine.inOut" }, 6.7);
  tl.to(pT, { rotation: -90, y: 70, duration: 3.5, ease: "sine.inOut" }, 6.7);
  tl.to(pB, { rotation: 90, y: -64, duration: 3.5, ease: "sine.inOut" }, 6.7);

  /* Exit at 10.35s into Ribbon Launch at 10.72s */
  tl.to(pR, { x: 640, opacity: 0, duration: 0.4, ease: "power3.in" }, 10.32);
  tl.to(pT, { y: -420, opacity: 0, duration: 0.4, ease: "power3.in" }, 10.32);
  tl.to(pB, { y: 420, opacity: 0, duration: 0.4, ease: "power3.in" }, 10.32);
  tl.to(pL, { rotation: 0, x: -20, duration: 0.38, ease: "power3.inOut" }, 10.32);
  tl.set(s3, { display: "none" }, 10.72);
}
