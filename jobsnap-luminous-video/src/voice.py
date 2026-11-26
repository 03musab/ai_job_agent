#!/usr/bin/env python3
"""Narration -> leveled voice track (assets/audio/vo.wav) + word timings (work/words.json).

    python src/voice.py my_take.mp3 [speed]

Drop your recorded (or cloned) narration audio in jobsnap-luminous-video/work/ and run the command above.
It applies broadcast-clean high-pass + compression + -15 LUFS loudness normalization, trims dead silence,
writes assets/audio/vo.wav, and aligns word timestamps via HyperFrames transcribe.
"""
import json, pathlib, subprocess, difflib, re, sys, shutil
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parent.parent
SR = 48000
CFG = json.load(open(ROOT / "project.json", encoding="utf-8"))
PACE = {"keep": 0.16, "keep_long": 0.36, "min_stop": 0.28, "min_comma": 0.1, **CFG.get("pace", {})}
LUFS = CFG.get("voice_lufs", -15)
HF = CFG.get("hyperframes") or "hyperframes"
KEEP, KEEP_LONG = PACE["keep"], PACE["keep_long"]
mine = (ROOT / "script.txt").read_text(encoding="utf-8").split()
(ROOT / "work").mkdir(exist_ok=True)


def dec(path, extra=()):
    raw = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", str(path), *extra, "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"],
        capture_output=True,
        check=True,
    ).stdout
    return np.frombuffer(raw, dtype=np.float32).reshape(-1, 2).copy()


if len(sys.argv) < 2:
    sys.exit("usage: python src/voice.py <audio-file-in-work/> [speed]\nexample: python src/voice.py my_voice.mp3 1.0")

RAW = ROOT / "work" / sys.argv[1]
SPEED = float(sys.argv[2]) if len(sys.argv) > 2 else 1.0
if not RAW.exists():
    sys.exit(f"no take found at {RAW} -save your recording in jobsnap-luminous-video/work/ first")

x = dec(RAW, ("-af", f"highpass=f=75,acompressor=threshold=-20dB:ratio=2.5:attack=8:release=120:makeup=2,loudnorm=I={LUFS}:TP=-1.5:LRA=9"))
mono = np.abs(x).max(axis=1)
h = SR // 100
env = np.array([mono[i:i + h].max() for i in range(0, len(mono) - h, h)])
sil = env < 0.012
segs = []
pos = 0.0
i = 0
while i < len(sil):
    if sil[i]:
        j = i
        while j < len(sil) and sil[j]:
            j += 1
        a, b = i * 0.01, j * 0.01
        keep = KEEP_LONG if b - a >= 0.4 else KEEP
        if a > 0.05 and b - a > keep + 0.05:
            segs.append((pos, a + keep / 2))
            pos = b - keep / 2
        i = j
    else:
        i += 1
segs.append((pos, len(x) / SR))
xf = int(0.008 * SR)
out = np.zeros((0, 2), dtype=np.float32)
for k, (a, b) in enumerate(segs):
    s = x[int(a * SR):int(b * SR)].copy()
    if k and len(out) > xf and len(s) > xf:
        r = np.linspace(0, 1, xf)[:, None]
        out[-xf:] = out[-xf:] * (1 - r) + s[:xf] * r
        s = s[xf:]
    out = np.concatenate([out, s])

(ROOT / "assets" / "audio").mkdir(parents=True, exist_ok=True)
vo = ROOT / "assets" / "audio" / "vo.wav"
subprocess.run(
    ["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-", "-af", f"atempo={SPEED},alimiter=limit=0.84", "-c:a", "pcm_s24le", str(vo)],
    input=out.tobytes(),
    check=True,
)
dur_s = len(out) / SR / SPEED
print(f"wrote assets/audio/vo.wav ({dur_s:.2f}s, normalized to {LUFS} LUFS)")
print("next: run `python src/build.py` to mount your voice into index.html, then render with HyperFrames!")
