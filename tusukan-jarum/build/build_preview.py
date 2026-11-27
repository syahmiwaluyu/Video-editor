"""Build preview (source 0:00-1:33) untuk video Tusukan Jarum.

Usage: python3 -I build_preview.py <video_sumber.mp4> <folder_slaid_png> <out.mp4> <workdir>
Fail asal tidak diubah. Semua output ditulis ke <out.mp4> / <workdir>.
"""
import sys, subprocess, json, math, os
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

SRC, SLIDES, OUT, WORK = sys.argv[1:5]
os.makedirs(WORK, exist_ok=True)
W, H, FPS = 1920, 1080, 30
SW, SH = 3840, 1774
TITLE = 4.0              # kad tajuk F1 (saat output)
S0, S1 = 0.0, 93.2       # julat source
DUR = TITLE + (S1 - S0)

# ---------- brand ----------
NAVY = (11, 42, 84); BLUE = (22, 92, 168); SKY = (226, 238, 250); YEL = (245, 183, 0); WHITE = (255, 255, 255)
FD = "/usr/share/fonts/opentype/inter/"
def F(w, s): return ImageFont.truetype(FD + {"r": "Inter-Regular.otf", "m": "Inter-Medium.otf", "s": "Inter-SemiBold.otf", "b": "Inter-Bold.otf", "x": "Inter-ExtraBold.otf"}[w], s)

def ease(x):  # ease-in-out
    x = min(max(x, 0), 1); return x * x * (3 - 2 * x)
def eout(x):  # ease-out back (overshoot kecil)
    x = min(max(x, 0), 1); c = 1.4; return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2

# ---------- kamera maya (source px: cx, cy, lebar; tinggi = lebar*9/16) ----------
CAM = {"WIDE": (1997, 887, 3154), "MED": (2360, 810, 2240), "CLOSE": (1830, 1000, 1600)}
# shot list: (src_start, src_end, cam, push) ; push = pertambahan zoom sepanjang shot
SHOTS = [(0.0, 3.6, "MED", 0.03), (3.6, 12.7, "CLOSE", 0.04), (12.7, 18.9, "MED", 0.03),
         (18.9, 30.0, "CLOSE", 0.03), (30.0, 39.9, "WIDE", 0.04), (39.9, 46.6, "MED", 0.03)]
SLIDE_FROM = 46.6   # selepas ini: layout slaid (B1) + kad penyampai

def cam_at(s):
    for a, b, c, p in SHOTS:
        if a <= s < b:
            cx, cy, w = CAM[c]; z = 1 + p * ease((s - a) / (b - a)); return cx, cy, w / z
    cx, cy, w = CAM["MED"]; return cx, cy, w

def crop_frame(fr, cx, cy, cw, outw, outh):
    ch = cw * outh / outw
    x0 = min(max(cx - cw / 2, 0), SW - cw); y0 = min(max(cy - ch / 2, 0), SH - ch)
    im = Image.fromarray(fr).crop((int(x0), int(y0), int(x0 + cw), int(y0 + ch)))
    return im.resize((outw, outh), Image.BILINEAR)

# ---------- aset statik ----------
def rounded(im, r):
    m = Image.new("L", im.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, im.size[0] - 1, im.size[1] - 1), r, fill=255)
    out = im.convert("RGBA"); out.putalpha(m); return out

def shadow(size, r, blur=18, alpha=110):
    pad = blur * 3; s = Image.new("RGBA", (size[0] + pad * 2, size[1] + pad * 2), (0, 0, 0, 0))
    ImageDraw.Draw(s).rounded_rectangle((pad, pad, pad + size[0], pad + size[1]), r, fill=(0, 0, 0, alpha))
    return s.filter(ImageFilter.GaussianBlur(blur)), pad

# latar layout slaid: gradien navy -> biru
g = np.linspace(0, 1, W)[None, :, None]
bg = (np.array(NAVY)[None, None] * (1 - g) + np.array(BLUE)[None, None] * g).repeat(H, 0).astype(np.uint8)
BG = Image.fromarray(bg).convert("RGBA")

# panel slaid (B1): slaid 2 = image5.png (disahkan daripada frame projektor pada 01:00)
SLX, SLY, SLW = 60, 124, 1380; SLH = int(SLW * 768 / 1376)
slide2 = Image.open(os.path.join(SLIDES, "image5.png")).convert("RGB")
k = SLW / 1376
# B2 reveal: lajur ikon (pusat x dalam px slaid asal 1376) & julat y kandungan lajur
COLS = [155, 421, 688, 954, 1220]; COL_HALF = 133; COL_Y = (262, 640)
REVEAL = [62.6, 67.1, 74.9, 81.4, 85.9]   # source time kata kunci setiap objektif
INTRO_REVEAL = 51.2                        # ayat "risiko pekerjaan..." (y 100-262)

# kad penyampai potret (kanan)
PCX, PCY, PCW = 1830, 1060, 560  # source
CARD_W = 340; CARD_H = int(CARD_W * 16 / 9) if False else 600
CARD_X = W - CARD_W - 60; CARD_Y = SLY + (SLH - CARD_H) // 2
card_sh, card_pad = shadow((CARD_W, CARD_H), 22)
panel_sh, panel_pad = shadow((SLW, SLH), 18)

def text_box(lines, pad=(26, 16), radius=14, fill=(0, 0, 0, 170)):
    ws = [ImageDraw.Draw(Image.new("RGB", (1, 1))).textbbox((0, 0), t, font=f) for t, f, c in lines]
    tw = max(b[2] - b[0] for b in ws); th = sum(b[3] - b[1] for b in ws) + 10 * (len(lines) - 1)
    im = Image.new("RGBA", (tw + pad[0] * 2, th + pad[1] * 2 + 8), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, im.size[0] - 1, im.size[1] - 1), radius, fill=fill)
    y = pad[1]
    for (t, f, c), b in zip(lines, ws):
        d.text(((im.size[0] - (b[2] - b[0])) // 2 - b[0], y - b[1]), t, font=f, fill=c); y += b[3] - b[1] + 10
    return im

# C4 lower-third (ejaan daripada slaid 1)
def lower_third():
    n = F("b", 40); p = F("m", 26); t = F("m", 24)
    l1 = "Al Baatul Ridwan Bin Mohamed"; l2 = "Bachelor of Medical and Health Sciences with Honours"; l3 = "Tutor: Sir Abdul Raimi Bin Abd Kadir"
    d0 = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    w = max(d0.textlength(l1, n), d0.textlength(l2, p), d0.textlength(l3, t)) + 70
    im = Image.new("RGBA", (int(w) + 12, 170), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((12, 0, im.size[0] - 1, 169), 14, fill=(*NAVY, 235)); d.rectangle((0, 0, 11, 169), fill=YEL)
    d.text((40, 18), l1, font=n, fill=WHITE); d.text((40, 76), l2, font=p, fill=SKY); d.text((40, 118), l3, font=t, fill=(*YEL, 255))
    return im
LT = lower_third(); LT_IN, LT_OUT = 19.1, 29.6

# C2 chip bab
def chip(txt):
    f = F("x", 30); d0 = ImageDraw.Draw(Image.new("RGB", (1, 1))); w = int(d0.textlength(txt, f)) + 56
    im = Image.new("RGBA", (w, 58), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, w - 1, 57), 29, fill=(*YEL, 255)); d.text((28, 11), txt, font=f, fill=NAVY); return im
CHIP = chip("OBJEKTIF PEMBELAJARAN")

# sari kata draf (source time). "…" = perkataan belum disahkan.
SUBS = [
 (0.00, 3.40, "Assalamualaikum warahmatullahi wabarakatuh\ndan salam sejahtera."),
 (3.84, 8.70, "Hari ini saya akan … tentang\npencegahan dan pengurusan"),
 (8.74, 12.70, "kecederaan tusukan jarum dalam kalangan\nanggota penjagaan kesihatan."),
 (12.76, 18.90, "Ini bagi subjek NBMH4143, Tugasan 2,\niaitu microteaching."),
 # 18.9-29.8 disembunyikan: lower-third sudah memaparkan nama (elak dua teks bersaing)
 (30.00, 36.60, "Hari ini kita akan tengok\nlangkah-langkah"),
 (36.70, 45.00, "untuk mengatasi kecederaan tusukan jarum\ndi kawasan klinik lah."),
 (47.43, 51.20, "Ini adalah objektif pembelajaran kita\npada hari ini,"),
 (51.25, 54.70, "iaitu risiko pekerjaan semasa\nprosedur klinikal"),
 (54.75, 58.10, "yang mendedahkan kepada darah\natau cecair badan berjangkit."),
 (58.31, 60.40, "Yang pertama kita tengok…"),
 (60.47, 65.10, "Di sini kita akan tengok dari segi\ntiga jangkitan bawaan darah …"),
 (65.25, 71.20, "Kedua, kita akan pergi kepada mengenal pasti\nempat langkah pencegahan proaktif."),
 (71.41, 78.45, "Yang ketiga, kita akan dapat menerangkan\nlima tindakan awal pasca-kecederaan."),
 (78.57, 84.50, "Keempat, kita dapat mengendalikan\npelupusan jarum secara selamat"),
 (84.53, 90.00, "dan terakhir sekali, melaporkan dan menilai\nrisiko secara bertanggungjawab."),
]
SUBF = F("s", 40)
def sub_img(txt):
    lines = [(l, SUBF, WHITE) for l in txt.split("\n")]; return text_box(lines, pad=(28, 14), fill=(0, 0, 0, 175))
SUB_IMGS = [(a, b, sub_img(t)) for a, b, t in SUBS]

DRAFT = text_box([("PREVIEW DRAF — sari kata & nama belum disahkan", F("m", 20), (255, 255, 255))], pad=(14, 8), radius=8, fill=(180, 30, 30, 200))

# F1 kad tajuk: slaid 1 (image1.png)
title_img = Image.open(os.path.join(SLIDES, "image1.png")).convert("RGB")
tk = max(W / title_img.width, H / title_img.height)
TITLE_BASE = title_img.resize((int(title_img.width * tk) + 2, int(title_img.height * tk) + 2), Image.LANCZOS)

# ---------- komposisi per frame ----------
def paste(canvas, im, x, y, a=1.0):
    if a <= 0: return
    if a < 1:
        im = im.copy(); al = im.getchannel("A").point(lambda v: int(v * a)); im.putalpha(al)
    canvas.alpha_composite(im, (int(x), int(y)))

def slide_panel(s):
    sl = slide2.copy(); d = ImageDraw.Draw(sl)
    if s < INTRO_REVEAL: d.rectangle((40, 100, 1340, COL_Y[0] - 2), fill=WHITE)
    for cx, rt in zip(COLS, REVEAL):
        p = ease((s - rt) / 0.35)
        if p < 1:  # tirai putih naik (reveal dari bawah ke atas)
            y1 = COL_Y[0] + (COL_Y[1] - COL_Y[0]) * p
            d.rectangle((cx - COL_HALF, y1, cx + COL_HALF, COL_Y[1]), fill=WHITE)
    return rounded(sl.resize((SLW, SLH), Image.LANCZOS), 18)

def compose(t, fr):
    if t < TITLE:  # F1
        z = 1 + 0.04 * (t / TITLE); iw, ih = TITLE_BASE.size
        cw, ch = W / z * (iw / (W * 1.0)) / (iw / W), H / z
        im = TITLE_BASE.crop(((iw - W / z) / 2, (ih - H / z) / 2, (iw + W / z) / 2, (ih + H / z) / 2)).resize((W, H), Image.BILINEAR).convert("RGBA")
        return im
    s = t - TITLE + S0
    if s < SLIDE_FROM:
        cx, cy, cw = cam_at(s); canvas = crop_frame(fr, cx, cy, cw, W, H).convert("RGBA")
        if LT_IN <= s < LT_OUT:
            p = eout((s - LT_IN) / 0.4); q = ease((LT_OUT - s) / 0.15)
            paste(canvas, LT, 70 - (1 - p) * 120, H - 280, min(p, q) if p < 1 else q)
    else:
        canvas = BG.copy(); u = s - SLIDE_FROM; p = eout(u / 0.4)
        sc = 0.94 + 0.06 * p; pw, ph = int(SLW * sc), int(SLH * sc)
        panel = slide_panel(s).resize((pw, ph), Image.BILINEAR)
        paste(canvas, panel_sh, SLX + (SLW - pw) / 2 - panel_pad, SLY + (SLH - ph) / 2 - panel_pad + 8, min(1, u / 0.3))
        paste(canvas, panel, SLX + (SLW - pw) / 2, SLY + (SLH - ph) / 2, min(1, u / 0.25))
        card = rounded(crop_frame(fr, PCX, PCY, PCW, CARD_W, CARD_H), 22)
        cxp = CARD_X + (1 - eout((u - 0.1) / 0.4)) * 420
        paste(canvas, card_sh, cxp - card_pad, CARD_Y - card_pad + 8); paste(canvas, card, cxp, CARD_Y)
        cp = eout((u - 0.3) / 0.35); paste(canvas, CHIP, SLX, 46 - (1 - cp) * 30, min(1, max(0, (u - 0.3) / 0.2)))
    for a, b, im in SUB_IMGS:
        if a <= s < b:
            ys = (H - im.size[1] - 18) if s >= SLIDE_FROM else (H - 110 - im.size[1])
            px = (SLX + SLW / 2 - im.size[0] / 2) if s >= SLIDE_FROM else (W - im.size[0]) / 2
            paste(canvas, im, px, ys, min(1, (s - a) / 0.12)); break
    if t > DUR - 0.5:  # fade out akhir
        canvas = Image.blend(canvas, Image.new("RGBA", (W, H), (0, 0, 0, 255)), (t - (DUR - 0.5)) / 0.5)
    paste(canvas, DRAFT, W - DRAFT.size[0] - 20, 16)
    return canvas

# ---------- audio ----------
aud = os.path.join(WORK, "aud.wav"); mus = os.path.join(WORK, "music.wav"); mix = os.path.join(WORK, "mix.wav")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(S0), "-to", str(S1), "-i", SRC, "-vn", "-ac", "2", "-ar", "48000",
                "-af", "highpass=f=80,afftdn=nr=10:nf=-40,loudnorm=I=-16:TP=-1.5:LRA=11", aud], check=True)
# E3: muzik procedural pendek untuk kad tajuk sahaja (pad lembut)
sr = 48000; n = int((TITLE + 0.6) * sr); tt = np.arange(n) / sr
env = np.minimum(1, tt / 0.8) * np.clip((TITLE + 0.6 - tt) / 1.0, 0, 1)
sig = sum(np.sin(2 * np.pi * f * tt) * a for f, a in [(220, .5), (277.18, .35), (329.63, .35), (415.3, .2), (110, .4)])
sig += 0.15 * np.sin(2 * np.pi * 659.26 * tt) * (0.5 + 0.5 * np.sin(2 * np.pi * 2 * tt))
sig = sig / np.abs(sig).max() * 10 ** (-20 / 20) * env
import wave
with wave.open(mus, "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr)
    st = (np.stack([sig, sig], 1) * 32767).astype(np.int16); w.writeframes(st.tobytes())
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", mus, "-i", aud, "-filter_complex",
                f"[1]adelay={int(TITLE*1000)}|{int(TITLE*1000)}[d];[0][d]amix=inputs=2:duration=longest:normalize=0,afade=t=out:st={DUR-0.5}:d=0.5",
                "-t", str(DUR), mix], check=True)

# ---------- video ----------
dec = subprocess.Popen(["ffmpeg", "-v", "error", "-ss", str(S0), "-t", str(S1 - S0 + 0.2), "-i", SRC, "-vf", f"fps={FPS}",
                        "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE, bufsize=SW * SH * 3 * 2)
enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                        "-i", mix, "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p",
                        "-c:a", "aac", "-b:a", "192k", "-shortest", OUT], stdin=subprocess.PIPE)
nframes = int(round(DUR * FPS)); fsz = SW * SH * 3; fr = None
for i in range(nframes):
    t = i / FPS
    if t >= TITLE:
        buf = dec.stdout.read(fsz)
        if len(buf) == fsz: fr = np.frombuffer(buf, np.uint8).reshape(SH, SW, 3)
    elif fr is None:
        fr = np.zeros((SH, SW, 3), np.uint8)
    enc.stdin.write(compose(t, fr).convert("RGB").tobytes())
    if i % 300 == 0: print(f"frame {i}/{nframes}", flush=True)
enc.stdin.close(); enc.wait(); dec.kill()
print("DONE", OUT, flush=True)
