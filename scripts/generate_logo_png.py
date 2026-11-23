"""Generate a crisp 120x120 PNG AI JobSnap logo for Google OAuth Consent Screen.

Zero external dependencies (uses only Python stdlib: math, os, struct, zlib).
Run:
    python scripts/generate_logo_png.py
Output:
    static/assets/jobsnap-logo-120.png
"""
import math
import os
import struct
import zlib

SIZE = 120
SUPERSAMPLE = 4  # 4x4 anti-aliasing

# Symmetric lightning bolt polygon in normalized [0, 1] space (safe inside circle crop)
BOLT = [
    (0.57, 0.16),
    (0.29, 0.54),
    (0.49, 0.54),
    (0.43, 0.84),
    (0.71, 0.46),
    (0.51, 0.46),
]

BOLT_SHADOW = [(x, y + 0.025) for (x, y) in BOLT]


def _point_in_poly(x: float, y: float, poly) -> bool:
    inside = False
    n = len(poly)
    j = n - 1
    for i in range(n):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / ((yj - yi) or 1e-12) + xi):
            inside = not inside
        j = i
    return inside


def _sample_pixel(nx: float, ny: float):
    # Diagonal emerald gradient (#10b981 -> #047857)
    t = max(0.0, min(1.0, (nx + ny) * 0.5))
    r = 16.0 + (4.0 - 16.0) * t
    g = 185.0 + (120.0 - 185.0) * t
    b = 129.0 + (87.0 - 129.0) * t

    # Subtle top-left luminous glow
    dist = math.hypot(nx - 0.25, ny - 0.20)
    glow = max(0.0, 1.0 - dist / 0.70) ** 2 * 0.28
    r += (110.0 - r) * glow
    g += (231.0 - g) * glow
    b += (183.0 - b) * glow

    # Soft bolt shadow
    if _point_in_poly(nx, ny, BOLT_SHADOW):
        alpha = 0.18
        r = r * (1.0 - alpha) + 2.0 * alpha
        g = g * (1.0 - alpha) + 44.0 * alpha
        b = b * (1.0 - alpha) + 34.0 * alpha

    # Crisp white lightning bolt
    if _point_in_poly(nx, ny, BOLT):
        return 255.0, 255.0, 255.0

    return r, g, b


def _png_chunk(chunk_type: bytes, data: bytes) -> bytes:
    chunk = chunk_type + data
    return struct.pack(">I", len(data)) + chunk + struct.pack(">I", zlib.crc32(chunk) & 0xFFFFFFFF)


def generate_png(output_path: str, size: int = SIZE) -> None:
    raw_rows = bytearray()
    inv = 1.0 / (size * SUPERSAMPLE)
    samples_sq = SUPERSAMPLE * SUPERSAMPLE

    for y in range(size):
        raw_rows.append(0)  # Filter type 0 (None)
        for x in range(size):
            sr = sg = sb = 0.0
            for sy in range(SUPERSAMPLE):
                ny = (y * SUPERSAMPLE + sy + 0.5) * inv
                for sx in range(SUPERSAMPLE):
                    nx = (x * SUPERSAMPLE + sx + 0.5) * inv
                    r, g, b = _sample_pixel(nx, ny)
                    sr += r
                    sg += g
                    sb += b
            raw_rows.append(int(round(sr / samples_sq)))
            raw_rows.append(int(round(sg / samples_sq)))
            raw_rows.append(int(round(sb / samples_sq)))

    ihdr = struct.pack(">IIBBBBB", size, size, 8, 2, 0, 0, 0)  # 8-bit RGB
    idat = zlib.compress(bytes(raw_rows), level=9)
    png_bytes = (
        b"\x89PNG\r\n\x1a\n"
        + _png_chunk(b"IHDR", ihdr)
        + _png_chunk(b"IDAT", idat)
        + _png_chunk(b"IEND", b"")
    )

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "wb") as fh:
        fh.write(png_bytes)


if __name__ == "__main__":
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out = os.path.join(root, "static", "assets", "jobsnap-logo-120.png")
    generate_png(out, size=SIZE)
    print(f"Generated {SIZE}x{SIZE} PNG logo ({os.path.getsize(out)} bytes): {out}")
