/* Shot 6 (15.80s – 21.42s) — Locked to real narration:
   15.8s "Every matched role across LinkedIn, Naukri, and direct portals — ranked in one clean dashboard." */
{
  const s6 = scene("s6", 15.80, 21.45);

  /* Full 3D-tilted Light-Mode JobSnap Dashboard */
  const dash = mk(
    s6,
    "abs",
    "left:140px; top:94px; width:1640px; height:892px; background:#FFFFFF; border-radius:26px; border:1.5px solid rgba(37,99,235,0.22); box-shadow:0 36px 96px rgba(37,99,235,0.14); display:flex; overflow:hidden; transform-origin:center center;"
  );
  dash.innerHTML = `
    <!-- Left Sidebar -->
    <div style="width:270px;background:#FAFBFD;border-right:1.5px solid #EEF2F7;padding:28px 22px;display:flex;flex-direction:column;gap:24px;">
      <div style="display:flex;align-items:center;gap:10px;">
        ${LOGO_SVG(36)}
        <span style="font-size:24px;font-weight:700;letter-spacing:-0.02em;">JobSnap</span>
        <span class="mono" style="font-size:11px;padding:3px 7px;border-radius:6px;background:#EFF6FF;color:#2563EB;font-weight:700;">BETA</span>
      </div>
      <div style="display:flex;flex-direction:column;gap:8px;font-size:17px;font-weight:500;color:#64748B;">
        <div style="padding:11px 14px;border-radius:12px;">Home</div>
        <div style="padding:11px 14px;border-radius:12px;background:#EFF6FF;color:#2563EB;font-weight:600;">Job Matches</div>
        <div style="padding:11px 14px;border-radius:12px;">Career Roadmaps</div>
        <div style="padding:11px 14px;border-radius:12px;">ATS Copilot</div>
      </div>
    </div>

    <!-- Main Dashboard Feed -->
    <div style="flex:1;padding:32px 38px;">
      <div style="display:flex;justify-content:space-between;align-items:center;">
        <div style="font-size:32px;font-weight:700;letter-spacing:-0.02em;">Matched Roles</div>
        <div style="display:flex;align-items:center;gap:14px;">
          <span class="saas-chip" style="background:#ECFDF5;color:#059669;">● 48 Synced</span>
          <span style="padding:10px 20px;border-radius:12px;background:#0F172A;color:#FFFFFF;font-size:16px;font-weight:600;">+ Run AI Scan</span>
        </div>
      </div>
      <div style="display:flex;gap:24px;margin-top:20px;border-bottom:1.5px solid #EEF2F7;padding-bottom:12px;font-size:17px;font-weight:600;color:#64748B;">
        <span style="color:#2563EB;border-bottom:2.5px solid #2563EB;padding-bottom:11px;">All Sources</span>
        <span>LinkedIn</span><span>Naukri</span><span>Internshala</span><span>Direct Portals</span>
      </div>

      <!-- 3x2 Role Cards Grid -->
      <div style="display:grid;grid-template-columns:repeat(3, 1fr);gap:22px;margin-top:26px;">
        <div class="saas-card" style="padding:20px;">
          <div style="height:126px;border-radius:14px;background:linear-gradient(135deg,#EFF6FF,#DBEAFE);padding:16px;display:flex;flex-direction:column;justify-content:space-between;">
            <span class="saas-chip" style="background:#FFFFFF;color:#2563EB;align-self:flex-start;">LinkedIn</span>
            <div style="font-size:28px;font-weight:700;color:#1E3A8A;">94% Fit</div>
          </div>
          <div style="font-size:20px;font-weight:700;margin-top:14px;">AI Product Engineer</div>
          <div style="font-size:15px;color:#64748B;margin-top:4px;">Linear · Remote</div>
        </div>

        <div id="d-target-card" class="saas-card" style="padding:20px;border:2.5px solid #3B82F6;box-shadow:0 18px 44px rgba(37,99,235,0.22);">
          <div style="height:126px;border-radius:14px;background:linear-gradient(135deg,#ECFDF5,#A7F3D0);padding:16px;display:flex;flex-direction:column;justify-content:space-between;">
            <span class="saas-chip" style="background:#FFFFFF;color:#059669;align-self:flex-start;">Direct · Stripe</span>
            <div style="font-size:28px;font-weight:700;color:#065F46;">96% Fit</div>
          </div>
          <div style="font-size:20px;font-weight:700;margin-top:14px;">Senior Full-Stack Eng</div>
          <div style="font-size:15px;color:#64748B;margin-top:4px;">Stripe · Global Remote</div>
        </div>

        <div class="saas-card" style="padding:20px;">
          <div style="height:126px;border-radius:14px;background:linear-gradient(135deg,#F5F3FF,#E0E7FF);padding:16px;display:flex;flex-direction:column;justify-content:space-between;">
            <span class="saas-chip" style="background:#FFFFFF;color:#4F46E5;align-self:flex-start;">Naukri</span>
            <div style="font-size:28px;font-weight:700;color:#312E81;">92% Fit</div>
          </div>
          <div style="font-size:20px;font-weight:700;margin-top:14px;">Staff Frontend Lead</div>
          <div style="font-size:15px;color:#64748B;margin-top:4px;">Vercel · Hybrid</div>
        </div>

        <div class="saas-card" style="padding:20px;">
          <div style="height:126px;border-radius:14px;background:linear-gradient(135deg,#FFFBEB,#FEF3C7);padding:16px;display:flex;flex-direction:column;justify-content:space-between;">
            <span class="saas-chip" style="background:#FFFFFF;color:#B45309;align-self:flex-start;">Internshala</span>
            <div style="font-size:28px;font-weight:700;color:#78350F;">91% Fit</div>
          </div>
          <div style="font-size:20px;font-weight:700;margin-top:14px;">Founding ML Engineer</div>
          <div style="font-size:15px;color:#64748B;margin-top:4px;">Raycast · Remote</div>
        </div>

        <div class="saas-card" style="padding:20px;">
          <div style="height:126px;border-radius:14px;background:linear-gradient(135deg,#F0FDF4,#DCFCE7);padding:16px;display:flex;flex-direction:column;justify-content:space-between;">
            <span class="saas-chip" style="background:#FFFFFF;color:#15803D;align-self:flex-start;">LinkedIn</span>
            <div style="font-size:28px;font-weight:700;color:#14532D;">90% Fit</div>
          </div>
          <div style="font-size:20px;font-weight:700;margin-top:14px;">Backend Platform Eng</div>
          <div style="font-size:15px;color:#64748B;margin-top:4px;">Figma · Remote</div>
        </div>

        <div class="saas-card" style="padding:20px;">
          <div style="height:126px;border-radius:14px;background:linear-gradient(135deg,#EFF6FF,#E0F2FE);padding:16px;display:flex;flex-direction:column;justify-content:space-between;">
            <span class="saas-chip" style="background:#FFFFFF;color:#0369A1;align-self:flex-start;">Career Portal</span>
            <div style="font-size:28px;font-weight:700;color:#0C4A6E;">89% Fit</div>
          </div>
          <div style="font-size:20px;font-weight:700;margin-top:14px;">Design Systems Eng</div>
          <div style="font-size:15px;color:#64748B;margin-top:4px;">Notion · Remote</div>
        </div>
      </div>
    </div>
  `;

  tl.fromTo(dash, { scale: 1.75, x: -60, y: 80, rotateY: 0, rotateX: 0, opacity: 0 }, { scale: 1.45, x: -20, y: 40, opacity: 1, duration: 0.62, ease: "power3.out" }, 15.82);
  tl.to(dash, { scale: 0.96, x: 0, y: 0, rotateY: -9, rotateX: 5, duration: 0.9, ease: "power3.inOut" }, 16.50);
  tl.to(dash, { scale: 1.32, x: -110, y: 40, rotateY: -2, rotateX: 2, duration: 0.68, ease: "power3.inOut" }, 17.50);
  pointerClick(s6, 1260, 740, 1020, 480, 17.75, 18.25, 18.62);
  tl.to(dash, { opacity: 0, scale: 1.5, filter: "blur(14px)", duration: 0.38, ease: "power2.in" }, 18.50);

  const cornerSpecs = [
    { src: "LinkedIn",    fit: "96% Fit", role: "Senior Full-Stack · Stripe", bg: "linear-gradient(135deg,#EFF6FF,#DBEAFE)", col: "#2563EB", x: 110,  y: 70,  rot: 10 },
    { src: "Naukri",      fit: "94% Fit", role: "AI Product Eng · Linear",   bg: "linear-gradient(135deg,#ECFDF5,#A7F3D0)", col: "#059669", x: 1310, y: 80,  rot: -10 },
    { src: "Internshala", fit: "92% Fit", role: "Staff Frontend · Vercel",   bg: "linear-gradient(135deg,#F5F3FF,#E0E7FF)", col: "#4F46E5", x: 90,   y: 660, rot: -9 },
    { src: "Direct API",  fit: "95% Fit", role: "Platform Eng · Figma",      bg: "linear-gradient(135deg,#FFFBEB,#FEF3C7)", col: "#B45309", x: 1330, y: 650, rot: 9 }
  ];

  cornerSpecs.forEach((sp, i) => {
    const c = mk(s6, "abs saas-card", `left:${sp.x}px; top:${sp.y}px; width:500px; padding:24px; border:2px solid rgba(59,130,246,0.35); box-shadow:0 26px 64px rgba(37,99,235,0.16); opacity:0;`);
    c.innerHTML = `<div style="height:142px;border-radius:16px;background:${sp.bg};padding:18px;display:flex;flex-direction:column;justify-content:space-between;"><span class="saas-chip" style="background:#FFFFFF;color:${sp.col};align-self:flex-start;font-size:15px;">${sp.src}</span><div style="font-size:34px;font-weight:700;color:${sp.col};">${sp.fit}</div></div><div style="font-size:23px;font-weight:700;margin-top:16px;">${sp.role}</div><div style="font-size:16px;color:#64748B;margin-top:4px;">Verified & Resume-Scored</div>`;
    const fromX = i % 2 === 0 ? 420 : -420;
    const fromY = i < 2 ? 260 : -260;
    tl.fromTo(c, { x: fromX, y: fromY, scale: 0.65, rotation: 0, opacity: 0 }, { x: 0, y: 0, scale: 1, rotation: sp.rot, opacity: 1, duration: 0.65, ease: "power3.out" }, 18.58 + i * 0.04);
    tl.to(c, { x: i % 2 === 0 ? -24 : 24, y: i < 2 ? -14 : 14, duration: 1.8, ease: "sine.inOut" }, 19.28);
    tl.to(c, { opacity: 0, scale: 0.85, filter: "blur(10px)", duration: 0.34, ease: "power2.in" }, 21.08);
  });

  const multTxt = mk(s6, "lt", "left:0; width:1920px; top:488px; text-align:center; font-size:84px; font-weight:600; color:#0F172A;", `Multiple Sources`);
  blurIn(multTxt, 19.05, 0.42, { scale: 0.92, blur: 12 });
  blurOut(multTxt, 21.05, 0.32, { scale: 1.06, blur: 12 });
}
