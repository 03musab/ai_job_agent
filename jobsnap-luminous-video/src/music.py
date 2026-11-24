#!/usr/bin/env python3
"""Music bed mixer for JobSnap Luminous Glass (32.0s).
Reads work/music-edit.mp3 or work/music-edit.wav, automatically levels & ducks it
under your narration voice, lifts gently on the final jobsnap.me outro, fades out at 32.0s,
and writes assets/audio/music.wav for HyperFrames.

    python src/music.py
"""
import json, pathlib, subprocess, sys
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parent.parent
cfg = json.load(open(ROOT / "project.json", encoding="utf-8"))
SRC = ROOT / cfg.get("music_source", "work/music-edit.wav")
if not SRC.exists():
    for alt in ("work/music-edit.mp3", "work/bg_music.mp3", "work/bg_music.wav", "work/music.mp3", "work/music.wav"):
        if (ROOT / alt).exists():
            SRC = ROOT / alt
            break
if not SRC.exists():
    print("No music file found in work/ (expected work/music-edit.mp3 or work/music-edit.wav). Skipping music track.")
    sys.exit(0)

SR = 48000
DUR = 32.0
VOICE_END = 29.3  # end of "at jobsnap.me"
BED = cfg.get("music_bed") if cfg.get("music_bed") is not None else 0.22
OUTRO_GAIN = min(0.55, BED * 2.1)

raw = subprocess.run(
    ["ffmpeg", "-v", "error", "-i", str(SRC), "-af", "loudnorm=I=-15:TP=-1.5:LRA=9", "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"],
    capture_output=True,
    check=True,
).stdout
x = np.frombuffer(raw, dtype=np.float32).reshape(-1, 2).copy()
total = len(x) / SR
if DUR > total + 0.05:
    print(f"!! Note: film is {DUR}s but {SRC.name} is {total:.1f}s — pick a track >= 33s for best results.")

N = min(int(DUR * SR), len(x))
y = x[:N]
tt = np.arange(N) / SR

# Smooth studio envelope: gentle fade-in (0->0.8s), tucked cleanly under narration (-13dB),
# warm lift on final "JobSnap — at jobsnap.me" logo hold (28.8->30.9s), silky fade-out to 32.0s
pts = [
    (0.0, 0.0),
    (0.7, BED),
    (VOICE_END - 0.5, BED),
    (VOICE_END + 0.6, OUTRO_GAIN),
    (DUR - 1.1, OUTRO_GAIN),
    (DUR, 0.0),
]
g = np.interp(tt, [p[0] for p in pts], [p[1] for p in pts]).astype(np.float32)[:, None]

(ROOT / "assets" / "audio").mkdir(parents=True, exist_ok=True)
out = ROOT / "assets" / "audio" / "music.wav"
subprocess.run(
    ["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-", "-c:a", "pcm_s24le", str(out)],
    input=(y * g).tobytes(),
    check=True,
)
print(f"wrote {out.relative_to(ROOT)} from {SRC.name} ({DUR}s, bed={BED}, outro={OUTRO_GAIN})")
print("next: run `python src/build.py` to mount music + voice into index.html!")
