"""Turn the three supplied stills into 8 s 1080x1920 clips with slow camera moves (no AI, no new pixels).

Each frame shows a source rectangle (x, y, w, h). If the rectangle is 9:16 it fills the frame; if it is wider,
it is shown full-width over a blurred, darkened copy of the same image. Rectangles are eased between keyframes.
Run from the project folder: python3 -I scripts/render_stills.py   -> clips/clip1.mp4, clip2.mp4, clip3.mp4 (no audio)
"""
import os
import subprocess
from PIL import Image, ImageEnhance, ImageFilter

W, H, FPS, DUR = 1080, 1920, 30, 8.0
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SHOTS = {
    # clip: (still, start rect, end rect, grade, seconds the move takes)  rects in source pixels; coordinates read from the stills
    "clip1": ("still1_alone.jpg", (250, 0, 1750, 1333), (580, 40, 520, 925), "night", 8.0),  # wide -> MCU on her face
    "clip2": ("still2_support.jpg", (300, 0, 1700, 1055), (720, 0, 800, 1055), "soft", 8.0),  # side shot -> closer two-shot
    "clip3": ("still3_team.jpg", (377, 300, 270, 480), (0, 0, 1024, 1024), "none", 4.3),   # face -> whole team, done before lavender fill
}


def ease(t):
    return 4 * t ** 3 if t < 0.5 else 1 - (-2 * t + 2) ** 3 / 2


def grade(im, kind):
    if kind == "night":  # darker, cooler, less saturated: the still is daytime, this only suggests night
        im = ImageEnhance.Brightness(im).enhance(0.72)
        im = ImageEnhance.Color(im).enhance(0.8)
        r, g, b = im.split()
        im = Image.merge("RGB", (r.point(lambda v: v * 0.93), g, b.point(lambda v: min(255, v * 1.06 + 4))))
    elif kind == "soft":
        im = ImageEnhance.Contrast(im).enhance(0.95)
    return im


def render(name, still, a, b, kind, move_s):
    src = grade(Image.open(os.path.join(ROOT, "assets", still)).convert("RGB"), kind)
    # blurred backdrop for letterbox areas (cover-fit, blurred, darkened)
    sw, sh = src.size
    s = max(W / sw, H / sh)
    bg = src.resize((int(sw * s), int(sh * s)), Image.BILINEAR)
    bg = bg.crop(((bg.width - W) // 2, (bg.height - H) // 2, (bg.width - W) // 2 + W, (bg.height - H) // 2 + H))
    bg = ImageEnhance.Brightness(bg.filter(ImageFilter.GaussianBlur(60))).enhance(0.55)
    out = os.path.join(ROOT, "clips", f"{name}.mp4")
    ff = subprocess.Popen(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                           "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium",
                           "-crf", "14", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
    n = int(DUR * FPS)
    for i in range(n):
        k = ease(min(1.0, i / (move_s * FPS - 1)))
        x, y, w, h = (a[j] + (b[j] - a[j]) * k for j in range(4))
        if w / h <= W / H + 1e-6:  # fills the frame (trim width to exact 9:16)
            w2 = h * W / H
            region = src.resize((W, H), Image.LANCZOS, box=(x + (w - w2) / 2, y, x + (w + w2) / 2, y + h))
            frame = region
        else:
            bh = round(W * h / w)
            region = src.resize((W, bh), Image.LANCZOS, box=(x, y, x + w, y + h))
            frame = bg.copy()
            frame.paste(region, (0, (H - bh) // 2))
        ff.stdin.write(frame.tobytes())
    ff.stdin.close()
    ff.wait()
    print("wrote", out)


if __name__ == "__main__":
    os.makedirs(os.path.join(ROOT, "clips"), exist_ok=True)
    for name, args in SHOTS.items():
        render(name, *args)
