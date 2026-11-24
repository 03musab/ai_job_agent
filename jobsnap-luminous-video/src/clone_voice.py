#!/usr/bin/env python3
"""Clone your voice from work/My_voice.mp3 and narrate the 32s JobSnap script.

Supports two modes:
  1. ElevenLabs API (highest realism):
       $env:ELEVENLABS_API_KEY="sk_..."
       python src/clone_voice.py --elevenlabs

  2. Local open-source voice cloning (free, runs on your PC via F5-TTS):
       pip install f5-tts
       python src/clone_voice.py --local

Output: work/vo_cloned.mp3 (or .wav), ready for `python src/voice.py vo_cloned.mp3 && python src/build.py`.
"""
import argparse, os, pathlib, subprocess, sys, urllib.request, json

ROOT = pathlib.Path(__file__).resolve().parent.parent
SAMPLE = ROOT / "work" / "My_voice.mp3"
SCRIPT = (
    "Turn your resume into interviews — for any role, instantly. "
    "Just drop it into JobSnap. "
    "Jobs, match scores, and one-click applications — all in one platform. "
    "Our AI scans live roles and scores your fit in seconds. "
    "Done. "
    "Every matched role across LinkedIn, Naukri, and direct portals — ranked in one clean dashboard. "
    "Pick your top match, hit one-click ATS fill, and you're applied. "
    "Match. Fill. Land. "
    "JobSnap — at jobsnap dot me."
)


def run_elevenlabs():
    key = os.environ.get("ELEVENLABS_API_KEY")
    if not key:
        sys.exit("Set ELEVENLABS_API_KEY first, e.g.:\n  $env:ELEVENLABS_API_KEY='your-key'\n  python src/clone_voice.py --elevenlabs")
    if not SAMPLE.exists():
        sys.exit(f"Missing voice sample at {SAMPLE}")

    # 1. Create instant voice clone from work/My_voice.mp3
    print("Uploading work/My_voice.mp3 to ElevenLabs Instant Voice Cloning...")
    import requests
    with open(SAMPLE, "rb") as f:
        r = requests.post(
            "https://api.elevenlabs.io/v1/voices/add",
            headers={"xi-api-key": key},
            data={"name": "JobSnap Founder Voice", "remove_background_noise": "true"},
            files={"files": ("My_voice.mp3", f, "audio/mpeg")},
            timeout=60,
        )
    r.raise_for_status()
    voice_id = r.json()["voice_id"]
    print(f"Cloned voice_id: {voice_id}")

    # 2. Generate the 32s narration in one take
    print("Generating 32s narration...")
    r2 = requests.post(
        f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
        headers={"xi-api-key": key, "Accept": "audio/mpeg", "Content-Type": "application/json"},
        json={
            "text": SCRIPT,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {"stability": 0.55, "similarity_boost": 0.82, "style": 0.25},
        },
        timeout=90,
    )
    r2.raise_for_status()
    out = ROOT / "work" / "vo_cloned.mp3"
    out.write_bytes(r2.content)
    print(f"Saved {out}")
    print("Next: python src/voice.py vo_cloned.mp3 1.0 && python src/build.py")


def run_local_f5():
    if not SAMPLE.exists():
        sys.exit(f"Missing voice sample at {SAMPLE}")
    out_dir = ROOT / "work" / "cloned_out"
    out_dir.mkdir(parents=True, exist_ok=True)
    # Trim the cleanest 11-second segment (no cough/mic check) from My_voice.mp3 for reference audio
    clean_ref = ROOT / "work" / "ref_clean.wav"
    subprocess.run(
        ["ffmpeg", "-v", "error", "-y", "-i", str(SAMPLE), "-ss", "5", "-t", "12", "-ac", "1", "-ar", "24000", str(clean_ref)],
        check=True,
    )
    print("Running local F5-TTS voice cloning (first run downloads model weights)...")
    subprocess.run(
        [
            "f5-tts_infer-cli",
            "--model", "F5TTS_v1_Base",
            "--ref_audio", str(clean_ref),
            "--gen_text", SCRIPT,
            "--output_dir", str(out_dir),
            "--output_file", "vo_cloned.wav",
        ],
        check=True,
    )
    final_wav = ROOT / "work" / "vo_cloned.wav"
    (out_dir / "vo_cloned.wav").replace(final_wav)
    print(f"Saved {final_wav}")
    print("Next: python src/voice.py vo_cloned.wav 1.0 && python src/build.py")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--elevenlabs", action="store_true", help="Clone via ElevenLabs API (requires ELEVENLABS_API_KEY)")
    g.add_argument("--local", action="store_true", help="Clone locally on your PC using F5-TTS (pip install f5-tts)")
    args = p.parse_args()
    if args.elevenlabs:
        run_elevenlabs()
    else:
        run_local_f5()
