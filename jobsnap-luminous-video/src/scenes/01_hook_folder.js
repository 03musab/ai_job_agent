/* Shot 1 & 2 (0.0s – 4.35s) -Locked to real narration:
   0:00 "Turn your resume" -> 0:01 "into interviews" -> 0:02 "for any role, instantly." */
{
  const s1 = scene("s1", 0.0, 4.42);

  /* 0.0–0.98s: "Turn Resumes" */
  const w1 = mk(s1, "lt", "left:0; width:1920px; top:480px; text-align:center; font-size:96px;", `<span class="lt-blue">Turn</span> <span>Resumes</span>`);
  blurIn(w1, 0.02, 0.36, { x: -28, blur: 14 });
  blurOut(w1, 0.90, 0.24, { x: 42, blur: 14 });

  /* 1.0–1.95s: "Interviews" */
  const w2 = mk(s1, "lt lt-grad", "left:0; width:1920px; top:480px; text-align:center; font-size:104px;", `Interviews`);
  blurIn(w2, 1.02, 0.36, { x: 48, blur: 16 });
  blurOut(w2, 1.85, 0.24, { x: -42, blur: 16 });

  /* 2.0–2.40s: "Any" */
  const wAny = mk(s1, "lt lt-blue", "left:0; width:1920px; top:484px; text-align:center; font-size:92px;", `Any`);
  blurIn(wAny, 1.98, 0.24, { scale: 0.9, blur: 12 });
  blurOut(wAny, 2.24, 0.18, { x: -160, blur: 10 });

  /* 2.4–3.65s: "Any role" [3D FROSTED GLASS FOLDER] "Instantly" */
  const leftTxt = mk(s1, "lt", "left:210px; top:492px; font-size:76px; font-weight:600; color:#FFFFFF; text-shadow:0 6px 28px rgba(154,52,18,0.28);", `Any role`);
  const rightTxt = mk(s1, "lt", "right:230px; top:492px; font-size:76px; font-weight:600; color:#0F172A;", `Instantly`);
  blurIn(leftTxt, 2.42, 0.36, { x: 60, blur: 12 });
  blurIn(rightTxt, 2.92, 0.36, { x: -60, blur: 12 });

  const folder = mk(s1, "g-folder", "left:805px; top:418px;");
  folder.innerHTML = `
    <div class="g-folder-tab"></div>
    <div class="g-folder-back"></div>
    <div class="g-folder-doc" style="left:26px;top:16px;width:236px;height:150px;transform:rotate(-4deg);">
      <div style="display:flex;align-items:center;gap:8px;">
        ${LOGO_SVG(24)}
        <div style="height:8px;width:96px;border-radius:4px;background:#E2E8F0;"></div>
      </div>
      <div style="height:8px;width:170px;border-radius:4px;background:#F1F5F9;margin-top:12px;"></div>
      <div style="height:8px;width:130px;border-radius:4px;background:#DBEAFE;margin-top:8px;"></div>
    </div>
    <div class="g-folder-doc" style="left:46px;top:24px;width:236px;height:150px;transform:rotate(5deg);background:#F8FAFC;">
      <div class="mono" style="font-size:12px;color:#059669;font-weight:600;">96% MATCH · STRIPE</div>
      <div style="height:9px;width:160px;border-radius:4px;background:#E2E8F0;margin-top:10px;"></div>
    </div>
    <div class="g-folder-front">
      <div style="font-size:26px;font-weight:600;letter-spacing:-0.02em;">JobSnap</div>
      <div style="display:flex;justify-content:space-between;align-items:center;margin-top:4px;">
        <span style="font-size:15px;opacity:0.85;">Resume & 48 Matches</span>
        <span style="width:26px;height:26px;border-radius:50%;background:rgba(255,255,255,0.28);display:inline-flex;align-items:center;justify-content:center;font-size:16px;">→</span>
      </div>
    </div>
  `;
  tl.fromTo(folder, { opacity: 0, scale: 0.72, y: 50, rotation: -12 }, { opacity: 1, scale: 1, y: 0, rotation: 5.5, duration: 0.52, ease: "back.out(1.4)" }, 2.42);
  pointerClick(s1, 1260, 720, 1040, 560, 2.95, 3.40, 3.72);
  tl.to(folder, { scale: 0.94, rotation: 2, duration: 0.1 }, 3.40);
  blurOut(leftTxt, 3.50, 0.26, { x: -40, blur: 14 });
  blurOut(rightTxt, 3.50, 0.26, { x: 40, blur: 14 });
  tl.to(folder, { scale: 1.55, opacity: 0, filter: "blur(18px)", duration: 0.36, ease: "power3.in" }, 3.52);

  /* 3.65–4.38s: 3D Perspective Workspace Glass Plane unfolding into "Just drop it into JobSnap" */
  const glassPlane = mk(
    s1,
    "abs",
    "left:170px; top:140px; width:1580px; height:800px; border-radius:28px; background:linear-gradient(180deg, rgba(255,255,255,0.96), rgba(245,249,255,0.98)); border:2px solid rgba(59,130,246,0.42); box-shadow:0 40px 100px rgba(59,130,246,0.18); opacity:0; transform-origin:center bottom; padding:38px 44px; display:flex; flex-direction:column; justify-content:space-between;"
  );
  glassPlane.innerHTML = `
    <div style="display:flex;justify-content:space-between;align-items:center;">
      <div style="display:flex;align-items:center;gap:12px;">${LOGO_SVG(38)}<span style="font-size:26px;font-weight:700;color:#0F172A;">JobSnap Workspace</span></div>
      <span class="saas-chip" style="background:#EFF6FF;color:#2563EB;font-size:15px;padding:7px 16px;">● Auto-Scan Active</span>
    </div>
    <div style="display:grid;grid-template-columns:250px 1fr;gap:30px;flex:1;margin:26px 0;">
      <div style="background:#F8FAFC;border:1.5px solid #E2E8F0;border-radius:20px;padding:22px;display:flex;flex-direction:column;gap:14px;">
        <div style="padding:12px 16px;border-radius:12px;background:#EFF6FF;color:#2563EB;font-size:17px;font-weight:600;">Job Matches (48)</div>
        <div style="padding:12px 16px;border-radius:12px;color:#64748B;font-size:17px;">AI Resume Match</div>
        <div style="padding:12px 16px;border-radius:12px;color:#64748B;font-size:17px;">Career Roadmaps</div>
        <div style="padding:12px 16px;border-radius:12px;color:#64748B;font-size:17px;">1-Click ATS Fill</div>
      </div>
      <div style="display:flex;flex-direction:column;gap:20px;">
        <div style="border:2px dashed rgba(59,130,246,0.45);border-radius:20px;background:linear-gradient(135deg, rgba(239,246,255,0.85), rgba(236,253,245,0.75));padding:28px 34px;display:flex;justify-content:space-between;align-items:center;">
          <div>
            <div class="mono" style="font-size:13px;color:#2563EB;font-weight:700;">AI RESUME ENGINE READY</div>
            <div style="font-size:28px;font-weight:700;color:#0F172A;margin-top:4px;">Drop your resume to match live roles</div>
            <div style="font-size:17px;color:#64748B;margin-top:4px;">Scanning LinkedIn · Naukri · Internshala · Direct Portals</div>
          </div>
          <span style="padding:14px 28px;border-radius:14px;background:linear-gradient(90deg,#2563EB,#38BDF8);color:#FFFFFF;font-size:18px;font-weight:600;box-shadow:0 12px 28px rgba(37,99,235,0.28);">Upload Resume</span>
        </div>
        <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:18px;flex:1;">
          <div class="saas-card" style="padding:20px;display:flex;flex-direction:column;justify-content:space-between;background:linear-gradient(180deg,#FFFFFF,#F8FAFF);"><span class="saas-chip" style="background:#ECFDF5;color:#059669;align-self:flex-start;">96% Match</span><div><div style="font-size:20px;font-weight:700;color:#0F172A;">Senior Full-Stack</div><div style="font-size:15px;color:#64748B;margin-top:4px;">Stripe · Remote</div></div></div>
          <div class="saas-card" style="padding:20px;display:flex;flex-direction:column;justify-content:space-between;background:linear-gradient(180deg,#FFFFFF,#F8FAFF);"><span class="saas-chip" style="background:#EFF6FF;color:#2563EB;align-self:flex-start;">94% Match</span><div><div style="font-size:20px;font-weight:700;color:#0F172A;">AI Product Engineer</div><div style="font-size:15px;color:#64748B;margin-top:4px;">Linear · Remote</div></div></div>
          <div class="saas-card" style="padding:20px;display:flex;flex-direction:column;justify-content:space-between;background:linear-gradient(180deg,#FFFFFF,#F8FAFF);"><span class="saas-chip" style="background:#F5F3FF;color:#4F46E5;align-self:flex-start;">92% Match</span><div><div style="font-size:20px;font-weight:700;color:#0F172A;">Staff Frontend Lead</div><div style="font-size:15px;color:#64748B;margin-top:4px;">Vercel · Hybrid</div></div></div>
        </div>
      </div>
    </div>
    <div style="display:flex;justify-content:space-between;align-items:center;font-size:17px;color:#64748B;padding-top:8px;border-top:1px solid #EEF2F7;">
      <span>Synced LinkedIn · Naukri · Internshala · Direct Portals</span>
      <span style="color:#0F172A;font-weight:600;">jobsnap.me</span>
    </div>
  `;
  tl.fromTo(glassPlane, { opacity: 0, rotateX: 56, scale: 0.78, y: 120 }, { opacity: 1, rotateX: 26, scale: 1.0, y: 0, duration: 0.44, ease: "power3.out" }, 3.65);
  tl.to(glassPlane, { opacity: 0, rotateX: 0, scale: 1.24, filter: "blur(14px)", duration: 0.34, ease: "power2.in" }, 4.08);
}
