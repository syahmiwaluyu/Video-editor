"""VGC-AE01 — render the muted 9:16 video from one still image.

Camera move, night grade, lavender glow and the on-screen text are all done here
with Pillow + numpy, then piped to ffmpeg. Settings live in LOOK / PATH / TEXT so the
next clip can reuse the same look.

Usage (from source/): python3 -I scripts/render_video.py
"""
import math
import subprocess
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "source" / "assets" / "doctor_still.jpg"
OUT = ROOT / "out" / "video_muted.mp4"

W, H, FPS, DUR = 1080, 1920, 30, 8.0
N = int(FPS * DUR)

# ---- locked look (reuse for the next clip) ---------------------------------
LOOK = dict(
    exposure=0.66,          # overall darken toward "night corridor"
    rgb_gain=(0.90, 0.98, 1.10),
    saturation=0.82,
    highlight_knee=0.55,    # compress bright background walls/lights
    vignette=0.42,
    grain=1.5,              # 8-bit units, seeded
)
LAVENDER_IN = (201, 182, 232)    # #C9B6E8 centre of glow
LAVENDER_OUT = (122, 92, 170)    # #7A5CAA edge of glow
TEXT_COLOR = (46, 26, 71)        # #2E1A47

# ---- camera path (source-pixel crop boxes, 9:16) ---------------------------
# (centre_x, centre_y, crop_height). Width = height * 9/16.
P_WIDE = (1625.0, 666.5, 1333.0)  # right side of frame: corridor + her shoes
P_MCU = (830.0, 520.0, 860.0)     # medium close-up: face, shoulders, hands
P_END = (820.0, 505.0, 800.0)     # slow drift continues under the glow
T_MOVE = (0.0, 4.5)
T_GLOW = (4.3, 5.3)
T_TEXT = (4.6, 5.0)

TEXT_LINES = [
    ("Behind every adverse event,", "Inter-SemiBold.otf"),
    ("there may be a", "Inter-SemiBold.otf"),
    ("healthcare worker", "Inter-SemiBold.otf"),
    ("silently struggling.", "Inter-SemiBoldItalic.otf"),
]
FONT_DIR = Path("/usr/share/fonts/opentype/inter")
TEXT_MAX_W = 880


def ease_io(x):
    x = min(max(x, 0.0), 1.0)
    return 4 * x ** 3 if x < 0.5 else 1 - (-2 * x + 2) ** 3 / 2


def smooth(t, a, b):
    x = min(max((t - a) / (b - a), 0.0), 1.0)
    return x * x * (3 - 2 * x)


def lerp(a, b, k):
    return tuple(x + (y - x) * k for x, y in zip(a, b))


def grade(img):
    a = np.asarray(img, dtype=np.float32) / 255.0
    a = a * LOOK["exposure"]
    a = a * np.array(LOOK["rgb_gain"], dtype=np.float32)
    k = LOOK["highlight_knee"]
    a = np.where(a > k, k + (1 - k) * np.tanh((a - k) / (1 - k)), a)
    lum = (a * np.array([0.2126, 0.7152, 0.0722], dtype=np.float32)).sum(-1, keepdims=True)
    a = lum + (a - lum) * LOOK["saturation"]
    return Image.fromarray((np.clip(a, 0, 1) * 255 + 0.5).astype(np.uint8))


def vignette_mask():
    y, x = np.mgrid[0:H, 0:W].astype(np.float32)
    r = np.sqrt(((x - W / 2) / (W / 2)) ** 2 + ((y - H * 0.45) / (H / 2)) ** 2)
    return (1 - LOOK["vignette"] * np.clip(r - 0.35, 0, 1) ** 1.5)[..., None]


def glow_layer():
    y, x = np.mgrid[0:H, 0:W].astype(np.float32)
    r = np.clip(np.sqrt(((x - W / 2) / (W * 0.75)) ** 2 + ((y - H * 0.47) / (H * 0.6)) ** 2), 0, 1)
    c_in, c_out = np.array(LAVENDER_IN, np.float32), np.array(LAVENDER_OUT, np.float32)
    return c_in + (c_out - c_in) * (r[..., None] ** 1.6)


def text_layer():
    size = 76
    while True:
        fonts = [ImageFont.truetype(str(FONT_DIR / f), size) for _, f in TEXT_LINES]
        widths = [f.getlength(s) for (s, _), f in zip(TEXT_LINES, fonts)]
        if max(widths) <= TEXT_MAX_W:
            break
        size -= 1
    layer = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(layer)
    line_h = int(size * 1.32)
    top = int(H * 0.46 - line_h * len(TEXT_LINES) / 2)
    for i, ((s, _), f, w) in enumerate(zip(TEXT_LINES, fonts, widths)):
        d.text(((W - w) / 2, top + i * line_h), s, font=f, fill=255)
    return layer, size, max(widths)


def main():
    src = grade(Image.open(SRC).convert("RGB"))
    sw, sh = src.size
    vig = vignette_mask()
    glow = glow_layer()
    txt, tsize, twidth = text_layer()
    print(f"text size {tsize}px, widest line {twidth:.0f}px")
    rng = np.random.default_rng(20261123)

    cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-vf", "scale=out_color_matrix=bt709:out_range=tv,format=yuv420p",
           "-c:v", "libx264", "-profile:v", "high", "-preset", "slow", "-crf", "18", "-g", "60",
           "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709", "-color_range", "tv",
           str(OUT)]
    ff = subprocess.Popen(cmd, stdin=subprocess.PIPE)

    for i in range(N):
        t = i / FPS
        if t <= T_MOVE[1]:
            cx, cy, ch = lerp(P_WIDE, P_MCU, ease_io((t - T_MOVE[0]) / (T_MOVE[1] - T_MOVE[0])))
        else:
            cx, cy, ch = lerp(P_MCU, P_END, (t - T_MOVE[1]) / (DUR - T_MOVE[1]))
        cw = ch * W / H
        x0 = min(max(cx - cw / 2, 0), sw - cw)
        y0 = min(max(cy - ch / 2, 0), sh - ch)
        frame = src.resize((W, H), Image.LANCZOS, box=(x0, y0, x0 + cw, y0 + ch))

        g = smooth(t, *T_GLOW)
        if g > 0:
            frame = frame.filter(ImageFilter.GaussianBlur(14 * g))
        a = np.asarray(frame, np.float32) * vig
        if g > 0:
            # soft-light style lift: picture stays faintly visible under the glow
            a = a * (1 - 0.76 * g) + glow * (0.76 * g)
        a += rng.normal(0, LOOK["grain"], (H, W, 1)).astype(np.float32)

        k = smooth(t, *T_TEXT)
        if k > 0:
            rise = int(round(14 * (1 - k)))
            m = np.asarray(txt, np.float32)[..., None] / 255.0 * k
            if rise:
                m = np.roll(m, rise, axis=0)
            a = a * (1 - m) + np.array(TEXT_COLOR, np.float32) * m

        ff.stdin.write(np.clip(a, 0, 255).astype(np.uint8).tobytes())
        if i % 30 == 0:
            print(f"frame {i}/{N}")
    ff.stdin.close()
    ff.wait()
    print("wrote", OUT)


if __name__ == "__main__":
    main()
