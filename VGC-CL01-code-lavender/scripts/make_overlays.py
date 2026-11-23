"""Text overlays + lavender layers for VGC-CL01 Code Lavender (1080x1920, RGBA PNG).

All on-screen text is set here, so spelling is exact and does not depend on the video generator.
Run from the project folder:  python3 -I scripts/make_overlays.py
Font: Inter / Inter Display (SIL OFL 1.1, system copy in this container). Check the licence before commercial use.
"""
import os
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1080, 1920
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "overlays")
FD = "/usr/share/fonts/opentype/inter/"
BOLD = FD + "InterDisplay-Bold.otf"
SEMI = FD + "Inter-SemiBold.otf"
MED = FD + "Inter-Medium.otf"

# Brand tokens (assumed: no brand file supplied)
LAV_DEEP = (74, 48, 120)      # deep lavender-purple
LAV = (181, 154, 222)         # lavender
LAV_LIGHT = (240, 232, 252)   # near-white lavender
WHITE = (255, 255, 255)

COPY = {
    "c1": ["Behind every adverse event,", "there may be a healthcare worker", "silently struggling."],
    "c2": "YOU ARE NOT ALONE.",
    "title": "CODE LAVENDER",
    "sub": ["PEER SUPPORT AFTER", "ADVERSE EVENTS"],
    "tag": "WE CARE. WE SUPPORT. WE HEAL TOGETHER.",
    "cta": ["Jangan berdiam diri.", "Hulurkan sokongan.", "Dapatkan bantuan."],
}
MAX_W = 860  # keeps text inside x ~110-970 (VGC 9:16 safe area)


def font(path, size):
    return ImageFont.truetype(path, size)


def fit(path, text, size, max_w=MAX_W, tracking=0):
    while size > 26:
        f = font(path, size)
        if text_w(f, text, tracking) <= max_w:
            return f
        size -= 2
    raise SystemExit(f"text does not fit: {text!r}")


def text_w(f, text, tracking=0):
    return f.getlength(text) + tracking * (len(text) - 1)


def draw_center(d, y, text, f, fill, tracking=0):
    """Centre one line at baseline-top y, measuring with the loaded font."""
    w = text_w(f, text, tracking)
    x = (W - w) / 2
    if tracking == 0:
        d.text((x, y), text, font=f, fill=fill)
    else:
        for ch in text:
            d.text((x, y), ch, font=f, fill=fill)
            x += f.getlength(ch) + tracking
    return f.getbbox("Hg")[3]


def shadowed(layer, radius=18, alpha=150):
    """Soft dark halo behind text for legibility on live footage."""
    a = layer.split()[3]
    sh = Image.new("RGBA", layer.size, (20, 10, 40, 0))
    sh.putalpha(a.filter(ImageFilter.GaussianBlur(radius)).point(lambda v: min(255, int(v * alpha / 255 * 2))))
    return Image.alpha_composite(sh, layer)


def radial_glow(color, inner_alpha, outer_alpha, cy=0.5):
    """Lavender glow: stronger at centre, used as a wash over footage."""
    small = Image.new("RGBA", (108, 192))
    px = small.load()
    for y in range(192):
        for x in range(108):
            dx, dy = (x - 54) / 54, (y - 192 * cy) / 96
            r = min(1.0, (dx * dx + dy * dy) ** 0.5 / 1.3)
            a = int(inner_alpha + (outer_alpha - inner_alpha) * r)
            px[x, y] = (*color, a)
    return small.resize((W, H), Image.BICUBIC).filter(ImageFilter.GaussianBlur(40))


def vertical_bg():
    """Opaque title-card background: deep lavender to lavender, soft centre light."""
    img = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(img)
    for y in range(H):
        t = y / (H - 1)
        k = max(0.0, 1 - abs(t - 0.42) / 0.62)  # lightest just above centre
        c = tuple(int(LAV_DEEP[i] + (LAV[i] - LAV_DEEP[i]) * k) for i in range(3))
        d.line([(0, y), (W, y)], fill=c)
    glow = radial_glow(LAV_LIGHT, 55, 0, cy=0.42)
    return Image.alpha_composite(img.convert("RGBA"), glow)


def save(img, name):
    img.save(os.path.join(OUT, name))
    print("wrote", name)


def main():
    os.makedirs(OUT, exist_ok=True)

    # Clip 1: awareness line, lower-middle (face is upper-middle in the MCU)
    l = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(l)
    f = fit(SEMI, max(COPY["c1"], key=len), 56)
    y = 1130
    for line in COPY["c1"]:
        draw_center(d, y, line, f, WHITE); y += int(f.size * 1.3)
    save(shadowed(l), "c1_text.png")
    save(radial_glow(LAV, 150, 60, cy=0.55), "c1_glow.png")

    # Clip 2: YOU ARE NOT ALONE.
    l = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(l)
    f = fit(BOLD, COPY["c2"], 96, tracking=2)
    draw_center(d, 1260, COPY["c2"], f, WHITE, tracking=2)
    save(shadowed(l, 22, 170), "c2_text.png")
    save(radial_glow(LAV, 90, 20, cy=0.45), "c2_glow.png")

    # Clip 3: title card, split into layers so they can be staggered
    save(vertical_bg(), "c3_bg.png")
    l = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(l)
    f = fit(BOLD, COPY["title"], 128, tracking=4)
    draw_center(d, 520, COPY["title"], f, WHITE, tracking=4)
    rule_y = 520 + int(f.size * 1.25)
    d.line([(W / 2 - 120, rule_y), (W / 2 + 120, rule_y)], fill=LAV_LIGHT, width=4)
    save(shadowed(l, 14, 90), "c3_title.png")

    l = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(l)
    f = fit(SEMI, COPY["sub"][0], 50, tracking=3)
    y = rule_y + 50
    for line in COPY["sub"]:
        draw_center(d, y, line, f, WHITE, tracking=3); y += int(f.size * 1.3)
    save(shadowed(l, 14, 90), "c3_sub.png")

    l = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(l)
    f = fit(SEMI, COPY["tag"], 40, tracking=1)
    draw_center(d, y + 70, COPY["tag"], f, WHITE, tracking=1)
    tag_bottom = y + 70 + int(f.size * 1.3)
    save(shadowed(l, 14, 90), "c3_tag.png")

    l = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(l)
    f = fit(MED, max(COPY["cta"], key=len), 46)
    y = max(tag_bottom + 130, 1230)
    box_top = y - 40
    box_h = int(len(COPY["cta"]) * f.size * 1.32) + 60
    d.rounded_rectangle([(110, box_top), (W - 110, box_top + box_h)], radius=28, fill=(255, 255, 255, 46),
                        outline=(255, 255, 255, 120), width=2)
    for line in COPY["cta"]:
        draw_center(d, y, line, f, WHITE); y += int(f.size * 1.32)
    assert box_top + box_h <= 1520, "CTA leaves the safe area"
    save(shadowed(l, 14, 90), "c3_cta.png")


if __name__ == "__main__":
    main()
