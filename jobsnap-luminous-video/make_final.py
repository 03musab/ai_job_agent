#!/usr/bin/env python3
"""SOOTHING STUDIO FOLEY + VOICE + MUSIC MASTER BUILDER (Apple / Linear / Calm SaaS Aesthetic)
Zero harsh white-noise hiss, zero tanh distortion buzz, zero arcade pops.

Design principles (aligned with claude-motion Soft/Luminous audio spec):
  1. Only 13 curated, purposeful interaction sounds across the entire 32s film (opening hook stays pure & clean).
  2. Pure linear acoustics (NO tanh waveshaping distortion):
     - Apple Magic Trackpad / Taptic micro-tap (10ms damped warm polycarbonate tap + soft 46ms release)
     - Low-passed "Velvet Air" breeze (<720 Hz ONLY -physically zero high-frequency hiss/static!)
     - Soft iOS Picker-Wheel felt micro-ticks on the 0->100/100 bar
     - Warm Rhodes / Celesta fifths in C Major / A Minor (261-784 Hz, matching the marimba music key,
       soft 10ms felt-mallet attack, stereo chorus warmth, placed in speech pauses so VO is never masked)
  3. Subtle broadcast Foley levels (-12 dBFS to -22 dBFS, tucked gently beneath the -15 LUFS voiceover).

Run from c:\\Users\\musab\\Desktop\\ai_job_agent:
    python jobsnap-luminous-video\\make_final.py
"""
import pathlib, shutil, subprocess, sys, wave
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parent
WS = ROOT.parent
SR = 48000
DUR = 32.0
N = int(DUR * SR)
rng = np.random.default_rng(2026)


def write_wav_native(path: pathlib.Path, stereo_f64: np.ndarray):
    """Write (N, 2) float64 [-1, 1] array directly to 16-bit PCM WAV via stdlib `wave`."""
    path.parent.mkdir(parents=True, exist_ok=True)
    clipped = np.clip(stereo_f64, -0.99, 0.99)
    pcm16 = (clipped * 32767.0).astype("<i2")
    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        wf.writeframes(pcm16.tobytes())


def load_audio_to_numpy(path: pathlib.Path) -> np.ndarray:
    """Decode any audio file (.mp3/.wav/.m4a) via temporary WAV + stdlib `wave`."""
    tmp = ROOT / "work" / "_tmp_decode.wav"
    tmp.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["ffmpeg", "-v", "error", "-y", "-i", str(path), "-ac", "2", "-ar", str(SR), "-c:a", "pcm_s16le", str(tmp)],
        check=True,
    )
    with wave.open(str(tmp), "rb") as wf:
        frames = wf.readframes(wf.getnframes())
    tmp.unlink(missing_ok=True)
    arr = np.frombuffer(frames, dtype="<i2").astype(np.float64) / 32768.0
    arr = arr.reshape(-1, 2)
    out = np.zeros((N, 2), dtype=np.float64)
    k = min(N, len(arr))
    out[:k] = arr[:k]
    return out


def smooth_band_noise(dur: float, f_lo: float, f_hi: float) -> tuple[np.ndarray, np.ndarray]:
    """Silky cosine-tapered band-limited noise (strictly 0.0 outside [f_lo, f_hi] -zero harsh hiss!)."""
    m = max(64, int(round(dur * SR)))
    freqs = np.fft.rfftfreq(m, 1.0 / SR)
    mask = np.zeros_like(freqs)
    band = (freqs >= f_lo) & (freqs <= f_hi)
    if np.any(band):
        u = (freqs[band] - f_lo) / max(1.0, (f_hi - f_lo))
        # Smooth Hann^2 spectral window: zero sharp filter ringing, zero out-of-band energy
        mask[band] = (0.5 - 0.5 * np.cos(2.0 * np.pi * u)) ** 1.5
    chans = []
    for _ in range(2):
        w = rng.standard_normal(m)
        y = np.fft.irfft(np.fft.rfft(w) * mask, n=m)
        pk = float(np.max(np.abs(y))) or 1.0
        chans.append(y / pk)
    return chans[0], chans[1]


# =====================================================================
# 1. PURE, SOOTHING ACOUSTIC FOLEY PRIMITIVES (ZERO TANH DISTORTION!)
# =====================================================================
sfx = np.zeros((N, 2), dtype=np.float64)
duck = np.ones(N, dtype=np.float64)


def place(t0: float, l: np.ndarray, r: np.ndarray, peak_level: float, music_dip: float = 0.0, dip_sec: float = 0.28):
    """Normalize (l, r) linearly (no distortion) to exact `peak_level` in [0, 1] and place at `t0`."""
    pk = max(float(np.max(np.abs(l))), float(np.max(np.abs(r))), 1e-8)
    l_out = (l / pk) * peak_level
    r_out = (r / pk) * peak_level
    s = int(round(t0 * SR))
    if s < 0:
        l_out, r_out = l_out[-s:], r_out[-s:]
        s = 0
    e = min(N, s + len(l_out))
    if e > s:
        k = e - s
        sfx[s:e, 0] += l_out[:k]
        sfx[s:e, 1] += r_out[:k]
        if music_dip > 0:
            d_len = min(N - s, max(k, int(dip_sec * SR)))
            u = np.linspace(0.0, 1.0, d_len)
            dip_curve = 1.0 - music_dip * (0.5 - 0.5 * np.cos(2.0 * np.pi * u))
            duck[s:s + d_len] = np.minimum(duck[s:s + d_len], dip_curve)


def add_trackpad_tap(t: float, level: float = 0.24, with_release: bool = True):
    """Clean, soothing Apple Magic Trackpad / Taptic tap (11ms damped warm impulse, zero metallic ring)."""
    dur = 0.016
    m = int(round(dur * SR))
    tt = np.linspace(0.0, dur, m)
    # Soft 0.7ms raised-cosine fade-in prevents harsh digital zero-crossing snap
    atk = np.where(tt < 0.0007, 0.5 - 0.5 * np.cos(np.pi * tt / 0.0007), 1.0)
    # Warm Taptic Engine damped low-mid pulse (215 Hz -> 95 Hz over 3.2ms)
    f_body = 95.0 + 125.0 * np.exp(-tt / 0.0028)
    ph = 2.0 * np.pi * np.cumsum(f_body) / SR
    body = np.sin(ph) * np.exp(-tt / 0.0030) * atk
    # Ultra-short damped wood/polycarbonate contact texture (650 - 2100 Hz, 1.6ms decay -> zero hiss!)
    nl, nr = smooth_band_noise(dur, 650.0, 2100.0)
    tex_env = np.exp(-tt / 0.0016) * atk * 0.42
    place(t, body + nl * tex_env, body + nr * tex_env, peak_level=level, music_dip=0.18, dip_sec=0.22)

    if with_release:
        # Subtle, quieter finger-lift Taptic micro-release 46ms later
        f_rel = 115.0 + 135.0 * np.exp(-tt / 0.0024)
        ph2 = 2.0 * np.pi * np.cumsum(f_rel) / SR
        body2 = np.sin(ph2) * np.exp(-tt / 0.0024) * atk
        nl2, nr2 = smooth_band_noise(dur, 750.0, 2200.0)
        tex2 = np.exp(-tt / 0.0014) * atk * 0.36
        place(t + 0.046, body2 + nl2 * tex2, body2 + nr2 * tex2, peak_level=level * 0.46)


def add_velvet_breeze(t: float, dur: float = 0.52, level: float = 0.085, pan_dir: float = 1.0):
    """Low-passed 'Velvet Air' camera glide (<680 Hz ONLY -zero static, zero white-noise hiss!)."""
    m = int(round(dur * SR))
    u = np.linspace(0.0, 1.0, m)
    # Silky bell-shaped envelope (zero sharp attack or cutoff)
    env = (0.5 - 0.5 * np.cos(2.0 * np.pi * u)) ** 1.5
    low_l, low_r = smooth_band_noise(dur, 120.0, 320.0)
    mid_l, mid_r = smooth_band_noise(dur, 220.0, 640.0)
    crest = np.sin(np.pi * u) ** 1.2
    # Gentle warm sub-breath (110 -> 165 -> 115 Hz) gives weight without mud
    f_sub = 110.0 + 55.0 * crest
    sub = np.sin(2.0 * np.pi * np.cumsum(f_sub) / SR) * env * 0.25
    l = (low_l * (1.0 - 0.45 * crest) + mid_l * (0.55 * crest)) * env + sub
    r = (low_r * (1.0 - 0.45 * crest) + mid_r * (0.55 * crest)) * env + sub
    pan = 0.5 + 0.24 * pan_dir * (2.0 * u - 1.0)
    place(t - dur * 0.35, l * (1.0 - pan) * 1.4, r * pan * 1.4, peak_level=level, music_dip=0.10, dip_sec=dur)


def add_felt_tick(t: float, step: int = 0, level: float = 0.068):
    """Delicate iOS Picker-Wheel felt micro-tick (soft warm wooden tap, whisper-quiet)."""
    dur = 0.012
    m = int(round(dur * SR))
    tt = np.linspace(0.0, dur, m)
    atk = np.where(tt < 0.0008, 0.5 - 0.5 * np.cos(np.pi * tt / 0.0008), 1.0)
    freq = 460.0 + step * 36.0  # gentle warm marimba register (460 -> 640 Hz)
    tone = np.sin(2.0 * np.pi * freq * tt) * np.exp(-tt / 0.0026) * atk
    pan = -0.14 if step % 2 == 0 else 0.14
    place(t, tone * (0.5 - pan) * 2.0, tone * (0.5 + pan) * 2.0, peak_level=level)


def add_warm_rhodes_chime(t: float, notes: tuple, level: float = 0.145, spread: float = 0.075, decay: float = 1.15):
    """Soothing Apple-Pay / Warm Rhodes felt chime in C Major / A Minor (261-784 Hz, pure linear sine + stereo warmth)."""
    dur = decay * 2.2
    m = int(round(dur * SR))
    tt = np.linspace(0.0, dur, m)
    # 10ms soft felt-mallet fade-in + natural acoustic two-stage decay + smooth cosine end taper
    atk = np.where(tt < 0.010, 0.5 - 0.5 * np.cos(np.pi * tt / 0.010), 1.0)
    tail_fade = np.where(tt > dur - 0.18, 0.5 + 0.5 * np.cos(np.pi * (tt - (dur - 0.18)) / 0.18), 1.0)
    env = atk * (0.62 * np.exp(-tt / (decay * 0.24)) + 0.38 * np.exp(-tt / (decay * 0.62))) * tail_fade

    tot_l = np.zeros(m + int(0.4 * SR), dtype=np.float64)
    tot_r = np.zeros(m + int(0.4 * SR), dtype=np.float64)
    for i, f in enumerate(notes):
        off = int(round(i * spread * SR))
        # Subtle +/- 0.35 Hz stereo chorus warmth + fast-decaying soft 2nd harmonic (pure Rhodes/kalimba tone)
        sig_l = (
            np.sin(2.0 * np.pi * (f - 0.35) * tt)
            + 0.16 * np.sin(2.0 * np.pi * (f * 2.0) * tt) * np.exp(-tt / 0.085)
        ) * env
        sig_r = (
            np.sin(2.0 * np.pi * (f + 0.35) * tt)
            + 0.16 * np.sin(2.0 * np.pi * (f * 2.0) * tt) * np.exp(-tt / 0.085)
        ) * env
        pan = -0.18 + 0.36 * (i / max(1, len(notes) - 1))
        tot_l[off:off + m] += sig_l * (0.5 - 0.3 * pan)
        tot_r[off:off + m] += sig_r * (0.5 + 0.3 * pan)
        # Soft 26ms stereo room reflection (-13 dB) for airy studio depth
        echo = int(0.026 * SR)
        if off + echo + m <= len(tot_l):
            tot_l[off + echo:off + echo + m] += sig_r * 0.22
            tot_r[off + echo:off + echo + m] += sig_l * 0.22

    place(t, tot_l, tot_r, peak_level=level, music_dip=0.18, dip_sec=0.55)


# =====================================================================
# STEP 1: ENSURE 1080p VIDEO CACHE & CLEAN OLD FILES
# =====================================================================
print("Step 1/4: Checking 1080p video cache...")
renders = ROOT / "renders"
renders.mkdir(parents=True, exist_ok=True)
work_dir = ROOT / "work"
work_dir.mkdir(parents=True, exist_ok=True)
video_cache = work_dir / "_clean_1080p_video.mp4"

candidate_videos = [
    video_cache,
    renders / "JobSnap_FINAL_WITH_SFX.mp4",
    renders / "JobSnap_Launch_FINAL_1080p.mp4",
]
found_vid = next((p for p in candidate_videos if p.exists() and p.stat().st_size > 100_000), None)

if found_vid is None or "--rerender" in sys.argv:
    print("  Rendering fresh 1080p video frames via HyperFrames...")
    subprocess.run([sys.executable, str(ROOT / "src" / "build.py")], cwd=ROOT, check=True)
    npx_bin = shutil.which("npx.cmd") or shutil.which("npx") or "npx.cmd"
    subprocess.run([npx_bin, "--yes", "hyperframes", "render", "-q", "high", "-o", str(video_cache)], cwd=ROOT, check=True)
elif found_vid != video_cache:
    subprocess.run(
        ["ffmpeg", "-v", "error", "-y", "-i", str(found_vid), "-an", "-c:v", "copy", str(video_cache)],
        check=True,
    )

# =====================================================================
# STEP 2: PLACE ONLY 13 CURATED, SOOTHING LUXURY UI CUES
# =====================================================================
print("Step 2/4: Crafting 13 soothing studio UI cues (Trackpad taps, velvet breezes, warm Rhodes fifths)...")

# 0.00s - 3.35s: Pure, uninterrupted founder voice + marimba opening hook!
# 1) 3.40s: Cursor clicks 3D Frosted Glass Folder (sits cleanly in the pause after "instantly.")
add_trackpad_tap(3.40, level=0.25, with_release=True)

# 2) 3.68s: Soft velvet-air breeze as the 3D Workspace unfolds
add_velvet_breeze(3.68, dur=0.52, level=0.090, pan_dir=-1.0)

# 3) 5.85s: Gentle stereo air-silk glide as the 4 iPhones form the radial ring
add_velvet_breeze(5.85, dur=0.54, level=0.082, pan_dir=1.0)

# 4) 10.72s: Smooth warm breeze as the luminous ribbon flows into the 0->100 bar
add_velvet_breeze(10.72, dur=0.58, level=0.092, pan_dir=1.0)

# 5) 11.75s - 13.85s: 6 delicate iOS Picker-Wheel felt micro-ticks during 0 -> 100/100
for k in range(6):
    add_felt_tick(11.75 + k * 0.42, step=k, level=0.065)

# 6) 14.96s: "Done." -> Soothing Apple-Pay warm two-note Rhodes fifth (C5 -> G5: 523.25 -> 783.99 Hz)
#    Timed right as "Done." finishes so the voice speaks clearly and the warm fifth blooms into the pause!
add_warm_rhodes_chime(14.96, (523.25, 783.99), level=0.145, spread=0.080, decay=1.10)

# 7) 18.25s: Cursor clicks Stripe 96% match card
add_trackpad_tap(18.25, level=0.23, with_release=True)

# 8) 18.58s: Soft velvet breeze as 4-Corner source cards fan out
add_velvet_breeze(18.58, dur=0.50, level=0.080, pan_dir=-1.0)

# 9) 22.10s: Subtle single Trackpad tap selecting top ATS Queue row
add_trackpad_tap(22.10, level=0.20, with_release=False)

# 10) 23.48s: Hero Trackpad click on "1-Click ATS Fill" button
add_trackpad_tap(23.48, level=0.25, with_release=True)

# 11) 24.35s: Warm soothing A4 -> E5 (440 -> 659.25 Hz) confirmation fifth right after "and you're applied."
add_warm_rhodes_chime(24.35, (440.00, 659.25), level=0.135, spread=0.080, decay=1.05)

# 12) 25.22s: Whisper-delicate warm harmonic (E5 -> G5) as the 4-point sparkle sweeps across
add_warm_rhodes_chime(25.22, (659.25, 783.99), level=0.090, spread=0.065, decay=0.80)

# 13) 30.05s: Warm Cmaj9 Rhodes bloom (C4 - G4 - E5: 261.63, 392.00, 659.25 Hz) right after "jobsnap dot me."
add_warm_rhodes_chime(30.05, (261.63, 392.00, 659.25), level=0.140, spread=0.090, decay=1.65)

sfx_wav = ROOT / "assets" / "audio" / "sfx.wav"
write_wav_native(sfx_wav, sfx)
sfx_pk_db = 20.0 * np.log10(max(float(np.max(np.abs(sfx))), 1e-6))
print(f"  Saved {sfx_wav.relative_to(WS)} (gentle studio peak = {sfx_pk_db:.1f} dBFS -zero clipping, zero static)")

# =====================================================================
# STEP 3: TRANSPARENT LINEAR MIX (VOICE HERO + SOOTHING MUSIC + SUBTLE FOLEY)
# =====================================================================
print("Step 3/4: Mixing Voiceover + Soothing Marimba Bed + Subtle Foley...")
master = sfx.copy()

vo_wav = ROOT / "assets" / "audio" / "vo.wav"
vo_rms = 0.12
if vo_wav.exists():
    vo = load_audio_to_numpy(vo_wav)
    active_vo = vo[np.abs(vo[:, 0]) > 0.015]
    if len(active_vo) > 0:
        vo_rms = float(np.sqrt(np.mean(active_vo ** 2)))
    master += vo * 0.92
    print("  + Added Voiceover (untouched warm clarity)")

mu_wav = ROOT / "assets" / "audio" / "music.wav"
if mu_wav.exists():
    mu = load_audio_to_numpy(mu_wav)
    mu_rms = float(np.sqrt(np.mean(mu ** 2))) or 0.05
    # Smoothly tuck marimba bed ~12.5 dB under active speech, lifting gently for the final 2s logo hold
    target_mu_rms = vo_rms * 0.235
    mu_scale = min(0.85, target_mu_rms / mu_rms)
    tail_lift = np.ones(N, dtype=np.float64)
    t_tail = int(29.8 * SR)
    tail_lift[t_tail:] = np.linspace(1.0, 1.28, N - t_tail)
    # Soft 1.2s fade-out at the very end (30.8s -> 32.0s) for a polished finish
    t_fade = int(30.8 * SR)
    tail_lift[t_fade:] *= 0.5 + 0.5 * np.cos(np.pi * np.linspace(0.0, 1.0, N - t_fade))
    master += (mu * mu_scale) * (duck * tail_lift)[:, None]
    print("  + Added Soothing Marimba Music (smoothly balanced + polished ending fade)")

# Pure transparent peak safety ceiling at -1.0 dBFS (NO tanh waveshaper on the master!)
m_pk = float(np.max(np.abs(master))) or 1.0
if m_pk > 0.89:
    master *= 0.89 / m_pk

master_wav = ROOT / "assets" / "audio" / "FINAL_MASTER_MIX.wav"
write_wav_native(master_wav, master)
print(f"  Saved {master_wav.relative_to(WS)} (clean linear peak = {20 * np.log10(float(np.max(np.abs(master)))):.1f} dBFS)")

# =====================================================================
# STEP 4: MUX ONTO 1080p VIDEO (WRITES UNLOCKED V2 IF V1 IS OPEN IN PLAYER!)
# =====================================================================
print("Step 4/4: Exporting final 1080p MP4...")
out_mp4 = renders / "JobSnap_FINAL_WITH_SFX.mp4"
try:
    if out_mp4.exists():
        out_mp4.unlink()
except PermissionError:
    out_mp4 = renders / "JobSnap_FINAL_SOOTHING_1080p.mp4"
    print(f"  (Note: previous MP4 is open in player -saving to {out_mp4.name} instead!)")

out_social = renders / (out_mp4.stem + "_Social.mp4")

subprocess.run(
    [
        "ffmpeg", "-v", "error", "-y",
        "-i", str(video_cache),
        "-i", str(master_wav),
        "-map", "0:v:0",
        "-map", "1:a:0",
        "-c:v", "copy",
        "-c:a", "aac", "-b:a", "256k",
        "-t", str(DUR),
        "-movflags", "+faststart",
        str(out_mp4),
    ],
    check=True,
)

subprocess.run(
    [
        "ffmpeg", "-v", "error", "-y",
        "-i", str(out_mp4),
        "-c:v", "libx264", "-b:v", "4500k", "-maxrate", "6000k", "-bufsize", "12000k",
        "-preset", "fast", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k",
        "-movflags", "+faststart",
        str(out_social),
    ],
    check=True,
)

print("\n============================================================")
print("DONE! Play your updated soothing 1080p video:")
print(f"  {out_mp4}")
print("============================================================")
