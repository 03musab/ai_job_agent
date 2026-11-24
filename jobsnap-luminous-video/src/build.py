#!/usr/bin/env python3
"""Assemble the 32.0s JobSnap Luminous Glass HyperFrames film with all audio stems."""
import json, pathlib

root = pathlib.Path(__file__).resolve().parent.parent
cfg = json.load(open(root / "project.json", encoding="utf-8"))
words = json.load(open(root / "work" / "words.json", encoding="utf-8"))
W, H = cfg["size"]
DUR = 32.0
data = (
    "const WORDS=" + json.dumps(words, separators=(",", ":"), ensure_ascii=False) + ";\n"
    "      const DUR=" + str(DUR) + ";\n"
    "      const SIZE=" + json.dumps([W, H]) + ";\n"
    "      const THEME=" + json.dumps(cfg["theme"]) + ";\n"
    "      const HANDLE=" + json.dumps(cfg.get("handle", "jobsnap.me")) + ";"
)
src = (root / "src" / "film.src.html").read_text(encoding="utf-8")
scenes = "\n".join(f.read_text(encoding="utf-8") for f in sorted((root / "src" / "scenes").glob("*.js")))
assert "/*__DATA__*/" in src and "/*__SCENES__*/" in src
src = src.replace("/*__DATA__*/", data).replace("/*__SCENES__*/", scenes)
for k, v in {"W": W, "H": H, "FONT_TEXT": cfg.get("fonts", {}).get("text", "Plus Jakarta Sans")}.items():
    src = src.replace("{{" + k + "}}", str(v))
(root / "compositions").mkdir(exist_ok=True)
(root / "compositions" / "film.html").write_text(src, encoding="utf-8")

tracks = []
mounted = []
for i, name in enumerate(("vo", "music", "sfx")):
    if (root / "assets" / "audio" / f"{name}.wav").exists():
        mounted.append(name)
        tracks.append(
            f'      <audio id="{name}" class="clip" src="assets/audio/{name}.wav" data-start="0" data-duration="{DUR}" data-track-index="{i + 2}" data-volume="1"></audio>'
        )

ae_dst = root / "assets" / "ae-motion.js"
ae_tag = '    <script src="assets/ae-motion.js"></script>' if ae_dst.exists() else ""
idx = (root / "src" / "index.src.html").read_text(encoding="utf-8")
for k, v in {"W": W, "H": H, "DUR": DUR, "AUDIO": "\n".join(tracks), "AE_MOTION": ae_tag}.items():
    idx = idx.replace("{{" + k + "}}", str(v))
(root / "index.html").write_text(idx, encoding="utf-8")
print(f"built luminous: {DUR}s, {W}x{H}, audio mounted: {mounted or 'none'}")
