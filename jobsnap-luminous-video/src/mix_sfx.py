#!/usr/bin/env python3
"""Punchy, Studio-Clear 48kHz Stereo Sound-Effects Bus for JobSnap Luminous Glass (32.0s).

Every sound effect is engineered to cut cleanly and unmistakably through Voiceover + BG Music:
- Real double-transient mouse/folder clicks (press + release snap at 2-7 kHz + woody body)
- Crisp airy stereo whooshes (full 180-4200 Hz sweep with stereo movement)
- Audible mechanical-glass progress ticks (0 -> 100/100) + riser swell
- Bright celebratory glass bell + confetti burst right on "Done." (14.76s)
- Crisp click + confirmation bloom ding on "1-Click ATS Fill" -> "Applied" (23.48s)
- Sparkle arpeggio shimmer on "Match. Fill. Land." (25.18-26.68s)
- Warm harmonic resolve chime + pad on "JobSnap - jobsnap.me" (27.62s)

    python src/mix_sfx.py
"""
import pathlib, subprocess
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parent.parent
SR = 48000
DUR = 32.0
N = int(DUR * SR)
bus = np.zeros((N, 2), dtype=np.float32)
rng = np.random.default_rng(2026)


def add_stereo(t0, sig_l, sig_r=None, gain=1.0):
    if sig_r is None:
        sig_r = sig_l
    start = int(round(t0 * SR))
    if start < 0:
        sig_l = sig_l[-start:]
        sig_r = sig_r[-start:]
        start = 0
    end = min(N, start + len(sig_l))
    if end > start:
        n = end - start
        bus[start:end, 0] += (sig_l[:n] * gain).astype(np.float32)
        bus[start:end, 1] += (sig_r[:n] * gain).astype(np.float32)


def band_noise(dur, f_lo, f_hi):
    m = max(64, int(round(dur * SR)))
    freqs = np.fft.rfftfreq(m, 1.0 / SR)
    mask = np.zeros_like(freqs)
    in_band = (freqs >= f_lo) & (freqs <= f_hi)
    if np.any(in_band):
        u = (freqs[in_band] - f_lo) / max(1.0, (f_hi - f_lo))
        mask[in_band] = np.sin(np.pi * u) ** 0.65
    pink = 1.0 / np.maximum(freqs, 40.0) ** 0.38
    out = []
    for _ in range(2):
        w = rng.standard_normal(m)
        y = np.fft.irfft(np.fft.rfft(w) * mask * pink, n=m)
        pk = float(np.max(np.abs(y))) or 1.0
        out.append((y / pk).astype(np.float32))
    return out[0], out[1]


def sfx_whoosh(t, dur=0.46, f0=240, f1=3400, vol=0.62, pan_dir=1.0):
    """Rich, unmistakably audible studio air whoosh with stereo sweep."""
    m = max(64, int(round(dur * SR)))
    u = np.linspace(0.0, 1.0, m, dtype=np.float32)
    env = (np.sin(np.pi * u) ** 1.35) * np.exp(-0.35 * u)
    lo_l, lo_r = band_noise(dur, max(120, f0 * 0.7), max(600, f0 * 3.0))
    hi_l, hi_r = band_noise(dur, max(700, f1 * 0.45), min(9500, f1 * 1.35))
    blend = np.sin(np.pi * u) ** 1.0
    sig_l = (lo_l * (1.0 - 0.55 * blend) + hi_l * blend * 1.15) * env
    sig_r = (lo_r * (1.0 - 0.55 * blend) + hi_r * blend * 1.15) * env
    pk = max(float(np.max(np.abs(sig_l))), float(np.max(np.abs(sig_r))), 1e-6)
    sig_l /= pk
    sig_r /= pk
    pan = 0.5 + 0.28 * pan_dir * (u * 2.0 - 1.0)
    add_stereo(t - dur * 0.32, sig_l * (1.0 - pan) * 1.4, sig_r * pan * 1.4, gain=vol)


def sfx_riser(t_peak, dur=0.72, vol=0.55):
    """Crisp rising air + harmonic lift peaking cleanly into a reveal."""
    m = max(64, int(round(dur * SR)))
    u = np.linspace(0.0, 1.0, m, dtype=np.float32)
    env = (u ** 1.8) * np.clip((1.0 - u) / 0.06, 0.0, 1.0)
    nl, nr = band_noise(dur, 600, 5200)
    tt = np.linspace(0.0, dur, m, dtype=np.float32)
    phase = 2.0 * np.pi * (320.0 * tt + 440.0 * (tt ** 2) / dur)
    tone = np.sin(phase) * 0.38
    add_stereo(t_peak - dur, (nl * 0.72 + tone) * env, (nr * 0.72 + tone) * env, gain=vol)


def _one_click_hit(dur, f_hi, f_lo, bright_lo, bright_hi):
    m = int(round(dur * SR))
    tt = np.linspace(0.0, dur, m, dtype=np.float32)
    # Sharp crisp micro-switch crack (2.5-8 kHz)
    nl, nr = band_noise(dur, bright_lo, bright_hi)
    crack_env = np.exp(-tt / 0.0028)
    # Tactile plastic/glass body knock
    f = f_lo + (f_hi - f_lo) * np.exp(-tt / 0.0045)
    ph = 2.0 * np.pi * np.cumsum(f) / SR
    body = np.sin(ph) * np.exp(-tt / 0.009)
    # Sub-click thump for presence
    thump = np.sin(2.0 * np.pi * 240.0 * tt) * np.exp(-tt / 0.006) * 0.35
    l = nl * crack_env * 0.85 + body * 0.65 + thump
    r = nr * crack_env * 0.85 + body * 0.65 + thump
    pk = max(float(np.max(np.abs(l))), float(np.max(np.abs(r))), 1e-6)
    return l / pk, r / pk


def sfx_click(t, vol=0.88):
    """Unmistakable realistic mouse/folder click (sharp press + 34ms micro-release click)."""
    l1, r1 = _one_click_hit(0.045, 3200.0, 680.0, 2200, 8800)
    l2, r2 = _one_click_hit(0.038, 3900.0, 920.0, 2800, 9600)
    add_stereo(t, l1, r1, gain=vol)
    add_stereo(t + 0.036, l2, r2, gain=vol * 0.58)


def sfx_pop(t, freq=620.0, vol=0.52, pan=0.0):
    """Crisp modern UI bubble-pop arrival."""
    dur = 0.12
    m = int(round(dur * SR))
    tt = np.linspace(0.0, dur, m, dtype=np.float32)
    f = freq * (0.68 + 0.56 * (1.0 - np.exp(-tt / 0.016)))
    ph = 2.0 * np.pi * np.cumsum(f) / SR
    env = np.clip(tt / 0.005, 0.0, 1.0) * np.exp(-tt / 0.032)
    nl, nr = band_noise(dur, 1800, 5200)
    s = (np.sin(ph) + 0.25 * np.sin(2.0 * ph)) * env
    l = s + nl * np.exp(-tt / 0.004) * 0.18
    r = s + nr * np.exp(-tt / 0.004) * 0.18
    pk = max(float(np.max(np.abs(l))), float(np.max(np.abs(r))), 1e-6)
    add_stereo(t, (l / pk) * (0.5 - 0.18 * pan) * 1.4, (r / pk) * (0.5 + 0.18 * pan) * 1.4, gain=vol)


def sfx_tick(t, step=0, vol=0.44):
    """Clearly audible crisp progress-bar tick."""
    dur = 0.045
    m = int(round(dur * SR))
    tt = np.linspace(0.0, dur, m, dtype=np.float32)
    freq = 920.0 + step * 72.0
    nl, nr = band_noise(dur, 2400, 7200)
    tone = (np.sin(2.0 * np.pi * freq * tt) + 0.30 * np.sin(4.0 * np.pi * freq * tt)) * np.exp(-tt / 0.012)
    l = tone * 0.75 + nl * np.exp(-tt / 0.003) * 0.45
    r = tone * 0.75 + nr * np.exp(-tt / 0.003) * 0.45
    pk = max(float(np.max(np.abs(l))), float(np.max(np.abs(r))), 1e-6)
    pan = -0.22 if step % 2 == 0 else 0.22
    add_stereo(t, (l / pk) * (0.5 - pan) * 1.4, (r / pk) * (0.5 + pan) * 1.4, gain=vol)


def sfx_chime(t, notes=(523.25, 659.25, 783.99, 1046.5), vol=0.48, spread=0.045, decay=1.05):
    """Bright, crystalline stereo UI confirmation bell chime."""
    dur = decay * 2.0
    m = int(round(dur * SR))
    tt = np.linspace(0.0, dur, m, dtype=np.float32)
    env = np.clip(tt / 0.008, 0.0, 1.0) * np.exp(-tt / (decay * 0.38))
    for i, f in enumerate(notes):
        s = (
            np.sin(2.0 * np.pi * f * tt)
            + 0.28 * np.sin(2.0 * np.pi * (f * 2.0) * tt) * np.exp(-tt / (decay * 0.20))
            + 0.12 * np.sin(2.0 * np.pi * (f * 3.0) * tt) * np.exp(-tt / (decay * 0.12))
        ) * env
        pk = float(np.max(np.abs(s))) or 1.0
        s /= pk
        pan = -0.32 + 0.64 * (i / max(1, len(notes) - 1))
        add_stereo(t + i * spread, s * (0.5 - 0.35 * pan) * 1.4, s * (0.5 + 0.35 * pan) * 1.4, gain=vol * 0.58)


def sfx_confetti_pop(t, vol=0.72):
    """Festive crisp pop + airy sparkle burst for 'Done.' confetti explosion."""
    sfx_pop(t, freq=480.0, vol=vol * 0.85, pan=0.0)
    nl, nr = band_noise(0.28, 2200, 9500)
    m = len(nl)
    tt = np.linspace(0.0, 0.28, m, dtype=np.float32)
    env = np.clip(tt / 0.008, 0.0, 1.0) * np.exp(-tt / 0.075)
    add_stereo(t + 0.015, nl * env, nr * env, gain=vol * 0.52)


def sfx_brand_pad(t, dur=3.8, vol=0.38):
    """Warm studio major-9th resolve pad for JobSnap finale."""
    m = int(round(dur * SR))
    tt = np.linspace(0.0, dur, m, dtype=np.float32)
    env = np.clip(tt / 0.38, 0.0, 1.0) * np.exp(-np.maximum(0.0, tt - 0.38) / 1.35)
    env *= np.clip((dur - tt) / 0.4, 0.0, 1.0)
    chord = [261.63, 392.00, 493.88, 587.33, 659.25]
    acc_l = np.zeros(m, dtype=np.float32)
    acc_r = np.zeros(m, dtype=np.float32)
    for i, f in enumerate(chord):
        sl = np.sin(2.0 * np.pi * (f * 0.9985) * tt) + 0.16 * np.sin(4.0 * np.pi * f * tt)
        sr = np.sin(2.0 * np.pi * (f * 1.0015) * tt) + 0.16 * np.sin(4.0 * np.pi * f * tt)
        acc_l += sl * (0.26 if i == 0 else 0.18)
        acc_r += sr * (0.26 if i == 0 else 0.18)
    add_stereo(t, acc_l * env, acc_r * env, gain=vol)


# =====================================================================
# ALL 36 VOICE-SYNCED STUDIO SFX CUES (0.00s -> 32.00s)
# =====================================================================

# Shot 1 & 2 (0.0–4.35s): Hook + 3D Glass Folder CLICK + Workspace unfold
sfx_whoosh(0.08,  0.40, 260, 2600, 0.56,  1.0)    # "Turn Resumes"
sfx_whoosh(1.06,  0.38, 340, 3000, 0.56, -1.0)    # "Interviews"
sfx_pop(2.00,     560,  0.50, -0.2)               # "Any"
sfx_whoosh(2.44,  0.44, 240, 2800, 0.62,  1.0)    # 3D Frosted Glass Folder arrives
sfx_click(3.40,   0.92)                           # CRISP FOLDER CLICK on "instantly"
sfx_whoosh(3.66,  0.50, 220, 3600, 0.66, -1.0)    # 3D Workspace Glass Plane unfolds

# Shot 3 (4.35–10.72s): Noir Light-Beam -> 4-Phone Radial Surround
sfx_whoosh(4.38,  0.50, 200, 2400, 0.60,  1.0)    # "Just drop it into JobSnap"
sfx_whoosh(5.16,  0.40, 300, 2800, 0.52, -1.0)    # Left iPhone glides in
sfx_whoosh(5.82,  0.46, 320, 3200, 0.58,  1.0)    # 4-Phone Radial Ring locks
sfx_pop(6.02,     580,  0.46,  0.0)               # "Jobs."
sfx_pop(6.88,     680,  0.50,  0.2)               # "Jobs. Match. Apply"
sfx_pop(8.92,     760,  0.52, -0.2)               # "All In One Platform"

# Shot 4 & 5 (10.70–15.85s): Ribbon Launch -> 100/100 Bar -> "Done." + Confetti
sfx_whoosh(10.72, 0.58, 220, 4200, 0.76,  1.0)    # Glowing ribbon launches off left iPhone
for k in range(10):
    sfx_tick(11.45 + k * 0.29, step=k, vol=0.46)  # Audible progress ticks 0 -> 100/100
sfx_riser(14.70,  0.65, 0.56)                     # Swell into 100/100 completion
sfx_confetti_pop(14.76, 0.78)                     # Confetti pop right on "Done."
sfx_chime(14.78,  (523.25, 659.25, 783.99, 1046.5), vol=0.56, spread=0.042, decay=1.0)

# Shot 6 (15.80–21.40s): 3D Dashboard Pullback -> Stripe Card CLICK -> 4-Corner Sources
sfx_whoosh(15.82, 0.44, 260, 2800, 0.56, -1.0)    # Card carousel opens
sfx_whoosh(16.52, 0.46, 360, 2400, 0.50,  1.0)    # 3D perspective dashboard pullback
sfx_click(18.25,  0.92)                           # CRISP CARD CLICK on "Stripe 96%"
sfx_whoosh(18.58, 0.50, 280, 3600, 0.66, -1.0)    # 4 corner source cards fan out
sfx_pop(19.05,    640,  0.50,  0.0)               # "Multiple Sources"

# Shot 7 (21.38–25.25s): Dark Obsidian ATS Queue -> Macro Row -> "1-Click ATS Fill" CLICK
sfx_whoosh(21.40, 0.48, 210, 2600, 0.58,  1.0)    # ATS Queue opens
sfx_click(22.10,  0.84)                           # CRISP QUEUE ROW CLICK
sfx_whoosh(22.40, 0.40, 300, 3000, 0.54, -1.0)    # Macro floating row arrives
sfx_whoosh(22.85, 0.46, 260, 2800, 0.54,  1.0)    # Pan across to "1-Click ATS Fill"
sfx_click(23.48,  0.94)                           # CRISP BUTTON CLICK on "1-Click ATS Fill"
sfx_chime(23.60,  (523.25, 783.99, 1046.5), vol=0.56, spread=0.050, decay=0.95)  # "Applied ✓" bloom ding

# Shot 8 (25.18–32.00s): Sparkle Arc -> "Match. Fill. Land." -> Radiant JobSnap Finale
sfx_chime(25.18,  (783.99, 1174.66, 1567.98), vol=0.46, spread=0.042, decay=0.72) # Sparkle blooms
sfx_whoosh(25.46, 0.52, 400, 4200, 0.56,  1.0)    # Sparkle sweeps light ribbon arc
sfx_pop(25.52,    580,  0.50, -0.25)              # "Match."
sfx_pop(26.12,    680,  0.50,  0.0)               # "Fill."
sfx_pop(26.68,    820,  0.54,  0.25)              # "Land."
sfx_whoosh(27.50, 0.54, 260, 3400, 0.58, -1.0)    # Radiant studio light bloom
sfx_brand_pad(27.62, dur=4.1, vol=0.38)           # Warm finale chord
sfx_chime(27.64,  (523.25, 659.25, 987.77), vol=0.52, spread=0.065, decay=1.8)    # Centered JobSnap resolve

# Soft-limit cleanly to -1.5 dBFS peak (0.84) so every click, whoosh, and ding cuts clearly through music + VO!
bus = np.tanh(bus * 1.05)
peak = float(np.max(np.abs(bus))) or 1.0
bus = (bus / peak) * 0.84

(ROOT / "assets" / "audio").mkdir(parents=True, exist_ok=True)
out = ROOT / "assets" / "audio" / "sfx.wav"
subprocess.run(
    ["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-", "-c:a", "pcm_s24le", str(out)],
    input=bus.astype(np.float32).tobytes(),
    check=True,
)
print(f"wrote {out.relative_to(ROOT)} (32.0s, 36 punchy stereo SFX cues, peak {20*np.log10(float(np.max(np.abs(bus)))+1e-9):.1f} dBFS)")
