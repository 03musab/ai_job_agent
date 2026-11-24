/* Shot 7 (21.38s – 25.25s) — Locked to real narration:
   21.4s "Pick your top match," -> 23.4s "hit one-click ATS fill," -> 24.1s "and you're applied." */
{
  const s7 = scene("s7", 21.38, 25.28);

  /* 19.85–21.4s: Sleek 3D Tilted List View Dashboard (ref 00:20–00:21) */
  const listDash = mk(
    s7,
    "abs",
    "left:170px; top:110px; width:1580px; height:860px; background:#FFFFFF; border-radius:26px; border:1.5px solid rgba(37,99,235,0.2); box-shadow:0 36px 96px rgba(37,99,235,0.12); padding:38px 46px; transform-origin:center center;"
  );
  listDash.innerHTML = `
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:26px;">
      <div style="display:flex;align-items:center;gap:12px;">${LOGO_SVG(36)}<span style="font-size:28px;font-weight:700;">ATS Queue</span></div>
      <span style="padding:10px 22px;border-radius:12px;background:#0F172A;color:#FFFFFF;font-size:16px;font-weight:600;">+ Add Role</span>
    </div>
    <div style="display:flex;flex-direction:column;gap:16px;">
      <div style="padding:22px 26px;border-radius:18px;border:1.5px solid #BFDBFE;background:#F8FAFF;display:flex;justify-content:space-between;align-items:center;">
        <div style="display:flex;align-items:center;gap:18px;">
          <div style="width:52px;height:52px;border-radius:14px;background:linear-gradient(135deg,#10B981,#059669);color:#FFFFFF;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:20px;">S</div>
          <div><div style="font-size:22px;font-weight:700;">Senior Full-Stack Engineer · Stripe</div><div style="font-size:16px;color:#64748B;">96% Match · Ready for ATS Auto-Fill</div></div>
        </div>
        <span style="padding:12px 24px;border-radius:12px;background:#0F172A;color:#FFFFFF;font-size:17px;font-weight:600;">1-Click ATS Fill</span>
      </div>
      <div style="padding:20px 26px;border-radius:18px;border:1.5px solid #EEF2F7;display:flex;justify-content:space-between;align-items:center;">
        <div style="font-size:21px;font-weight:600;">AI Product Engineer · Linear <span style="color:#64748B;font-weight:400;margin-left:12px;">94% Match</span></div>
        <span class="saas-chip" style="background:#EFF6FF;color:#2563EB;">Queued</span>
      </div>
      <div style="padding:20px 26px;border-radius:18px;border:1.5px solid #EEF2F7;display:flex;justify-content:space-between;align-items:center;">
        <div style="font-size:21px;font-weight:600;">Staff Frontend Lead · Vercel <span style="color:#64748B;font-weight:400;margin-left:12px;">92% Match</span></div>
        <span class="saas-chip" style="background:#ECFDF5;color:#059669;">Applied ✓</span>
      </div>
      <div style="padding:20px 26px;border-radius:18px;border:1.5px solid #EEF2F7;display:flex;justify-content:space-between;align-items:center;">
        <div style="font-size:21px;font-weight:600;">Founding ML Engineer · Raycast <span style="color:#64748B;font-weight:400;margin-left:12px;">91% Match</span></div>
        <span class="saas-chip" style="background:#F1F5F9;color:#475569;">Synced</span>
      </div>
    </div>
  `;
  tl.fromTo(listDash, { rotateY: 16, rotateX: 8, scale: 0.86, opacity: 0 }, { rotateY: -6, rotateX: 4, scale: 0.98, opacity: 1, duration: 0.52, ease: "power3.out" }, 21.40);
  pointerClick(s7, 1140, 680, 920, 320, 21.75, 22.10, 22.35);
  tl.to(listDash, { scale: 1.55, opacity: 0, filter: "blur(14px)", duration: 0.32, ease: "power2.in" }, 22.22);

  /* 22.40–25.25s: Macro Floating White Row -> Pans to "1-Click ATS Fill" -> Clicks on 23.45s -> "Applied ✓" on 23.6s */
  const macroRow = mk(
    s7,
    "abs",
    "left:220px; top:408px; width:2180px; height:264px; border-radius:40px; background:#FFFFFF; border:1.5px solid rgba(59,130,246,0.18); box-shadow:0 36px 96px rgba(59,130,246,0.22), 0 12px 32px rgba(16,185,129,0.12); display:flex; align-items:center; justify-content:space-between; padding:0 90px; opacity:0;"
  );
  macroRow.innerHTML = `
    <div style="display:flex;align-items:center;gap:42px;">
      <div style="width:42px;height:42px;border-radius:11px;border:3px solid #CBD5E1;"></div>
      <div style="width:142px;height:142px;border-radius:28px;background:linear-gradient(135deg,#10B981,#047857);display:flex;align-items:center;justify-content:center;box-shadow:0 16px 36px rgba(16,185,129,0.26);">${LOGO_SVG(96)}</div>
      <div>
        <div style="font-size:52px;font-weight:600;letter-spacing:-0.025em;color:#0F172A;">Senior Full-Stack · Stripe</div>
        <div style="font-size:34px;color:#64748B;margin-top:8px;">96% Resume Match · Greenhouse ATS</div>
      </div>
    </div>

    <div id="macro-cta" style="position:relative;padding:40px 76px;border-radius:26px;background:#0F172A;color:#FFFFFF;font-size:48px;font-weight:600;letter-spacing:-0.02em;box-shadow:0 22px 54px rgba(15,23,42,0.22);margin-right:120px;">
      <span id="macro-cta-txt">1-Click ATS Fill</span>
    </div>
  `;

  tl.fromTo(macroRow, { x: 140, scale: 0.9, opacity: 0 }, { x: 0, scale: 1, opacity: 1, duration: 0.42, ease: "power3.out" }, 22.40);
  tl.to(macroRow, { x: -1070, duration: 0.65, ease: "power3.inOut" }, 22.85);
  pointerClick(s7, 1220, 740, 975, 555, 23.05, 23.48, 23.95);

  const cta = macroRow.querySelector("#macro-cta");
  const ctaTxt = macroRow.querySelector("#macro-cta-txt");
  tl.to(cta, { scale: 0.92, duration: 0.1 }, 23.48);
  tl.to(cta, { scale: 1.12, background: "linear-gradient(90deg, #3B82F6 0%, #38BDF8 58%, #10B981 100%)", boxShadow: "0 26px 84px rgba(56, 189, 248, 0.52)", duration: 0.38, ease: "back.out(1.6)" }, 23.58);
  tl.to(macroRow, { background: "rgba(255,255,255,0)", borderColor: "rgba(255,255,255,0)", boxShadow: "none", duration: 0.32 }, 23.62);
  ticks.push((T) => { ctaTxt.textContent = T >= 23.62 ? "Applied via JobSnap ✓" : "1-Click ATS Fill"; });
  tl.to(cta, { scale: 0.15, opacity: 0, filter: "blur(12px)", duration: 0.34, ease: "power3.in" }, 24.85);
}
