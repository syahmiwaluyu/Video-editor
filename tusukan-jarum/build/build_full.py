"""Build video penuh (DRAF v1) — Pencegahan & Pengurusan Kecederaan Tusukan Jarum.

Usage:
  python3 -I build_full.py prep   <video> <slides_dir> <workdir>                # audio, subs, aset
  python3 -I build_full.py render <video> <slides_dir> <workdir> <t0> <t1> <out_chunk.mp4>   # julat masa OUTPUT
Fail sumber tidak diubah.
"""
import sys, os, json, subprocess, wave, re
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

MODE, SRC, SLIDES, WORK = (sys.argv[1:5] + [None] * 4)[:4]
os.makedirs(WORK, exist_ok=True)
W, H, FPS = 1920, 1080, 30
SW, SH = 3840, 1774
TITLE = 4.0
SRC_END = 1224.75
END_AT = 1222.2            # kad penutup bermula (source)
END_LEN = 3.3
DUR = TITLE + END_AT + END_LEN

NAVY = (11, 42, 84); BLUE = (22, 92, 168); SKY = (226, 238, 250); YEL = (245, 183, 0); WHITE = (255, 255, 255); RED = (200, 40, 40)
FD = "/usr/share/fonts/opentype/inter/"
def F(w, s): return ImageFont.truetype(FD + {"r": "Inter-Regular.otf", "m": "Inter-Medium.otf", "s": "Inter-SemiBold.otf", "b": "Inter-Bold.otf", "x": "Inter-ExtraBold.otf"}[w], s)
def ease(x): x = min(max(x, 0), 1); return x * x * (3 - 2 * x)
def eout(x): x = min(max(x, 0), 1); c = 1.4; return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2

# ======================= KANDUNGAN (source time) =======================
# Slaid: (fail, mula, chip, [(rect px pada slaid 1376x768, masa reveal), ...])
def fr(x0, y0, x1, y1): return (int(x0 * 1376), int(y0 * 768), int(x1 * 1376), int(y1 * 768))
SLIDE_LIST = [
 ("image5.png", 46.6, "OBJEKTIF PEMBELAJARAN", [((40, 140, 1340, 260), 51.2)] + [((c - 133, 262, c + 133, 640), t) for c, t in zip([155, 421, 688, 954, 1220], [62.6, 67.1, 74.9, 81.4, 85.9])]),
 ("image6.png", 92.0, "DEFINISI & LALUAN PENDEDAHAN", [(fr(.52, .18, .97, .42), 125.5), (fr(.52, .43, .97, .67), 132.8), (fr(.52, .68, .97, .93), 141.5)]),
 ("image7.png", 151.9, "TIGA TONGGAK KESELAMATAN", [(fr(.03, .20, .33, .51), 161.8), (fr(.63, .20, .97, .52), 174.2), (fr(.32, .75, .69, .98), 183.1)]),
 ("image8.png", 199.9, "3 JANGKITAN BAWAAN DARAH", [(fr(.04, .18, .348, .885), 207.7), (fr(.348, .18, .65, .885), 229.6), (fr(.65, .18, .96, .885), 251.7), (fr(.04, .885, .96, .97), 272.1)]),
 ("image9.png", 282.4, "FAKTOR PENDORONG RISIKO", []),
 ("image10.png", 370.5, "PROTOKOL PENCEGAHAN", [(fr(.32, .24, .66, .90), 405.3), (fr(.62, .24, .985, .90), 420.4)]),
 ("image11.png", 447.2, "PELUPUSAN BENDA TAJAM", [(fr(0, .21, .49, 1), 460.5), (fr(.50, .21, 1, 1), 509.4)]),
 ("SLIDE9_FIXED", 548.5, "PROTOKOL KECEMASAN", [((40, 120, 480, 415), 565.4), ((490, 120, 910, 415), 580.2), ((920, 120, 1340, 415), 595.1), ((243, 425, 668, 740), 610.2), ((688, 425, 1133, 740), 628.1)]),
 ("image13.png", 646.2, "ANALISIS RISIKO", [(fr(.04, .15, .50, .50), 650.2), (fr(.50, .15, .96, .50), 668.4), (fr(.04, .50, .50, .81), 681.4), (fr(.50, .50, .96, .99), 698.1)]),
 ("image15.png", 727.0, "PEP HIV", []),
 ("image16.png", 816.0, "KES KLINIKAL & SOAL JAWAB", [(fr(.50, .29, .95, .42), 845.1), (fr(.50, .42, .95, .54), 872.7), (fr(.50, .54, .95, .66), 884.5), (fr(.50, .66, .95, .78), 897.0), (fr(.50, .78, .95, .92), 918.9)]),
 ("image17.png", 937.0, "KAJIAN KES", [(fr(.54, .26, .96, .47), 959.6), (fr(.54, .48, .96, .69), 968.5), (fr(.54, .70, .96, .97), 973.5)]),
 ("image19.png", 986.2, "RUMUSAN", [(fr(.02, .16, .35, .49), 996.5), (fr(.64, .16, .99, .49), 1006.7), (fr(.64, .49, .99, .81), 1018.2), (fr(.02, .49, .35, .81), 1027.3), (fr(.04, .82, .96, .99), 1034.9)]),
 ("image21.png", 1043.0, "RUJUKAN", []),
]
DEMO_CHIP = (1077.0, "DEMO AMALI")

# Layout: (mula, tamat, kamera atau "SLIDE")
SEQ = [(0, 3.6, "MED"), (3.6, 12.7, "CLOSE"), (12.7, 18.9, "MED"), (18.9, 30, "CLOSE"), (30, 39.9, "WIDE"), (39.9, 46.6, "MED"),
 (46.6, 112.4, "SLIDE"), (112.4, 124.3, "CLOSE"), (124.3, 196.9, "SLIDE"), (196.9, 200.8, "WIDE"), (200.8, 291.9, "SLIDE"),
 (291.9, 299.9, "CLOSE"), (299.9, 316.0, "SLIDE"), (316.0, 322.5, "MED"), (322.5, 331.0, "SLIDE"), (331.0, 335.0, "CLOSE"),
 (335.0, 344.5, "SLIDE"), (344.5, 350.3, "CLOSE"), (350.3, 359.0, "SLIDE"), (359.0, 370.5, "MED"), (370.5, 392.0, "SLIDE"),
 (392.0, 404.5, "CLOSE"), (404.5, 428.6, "SLIDE"), (428.6, 446.6, "MED"), (446.6, 467.6, "SLIDE"), (467.6, 471.8, "CLOSE"),
 (471.8, 476.5, "SLIDE"), (476.5, 482.0, "CLOSE"), (482.0, 487.0, "SLIDE"), (487.0, 508.6, "DEMO"), (508.6, 515.0, "SLIDE"),
 (515.0, 535.0, "MED"), (535.0, 543.4, "SLIDE"), (543.4, 549.4, "CLOSE"), (549.4, 573.0, "SLIDE"), (573.0, 579.5, "CLOSE"),
 (579.5, 590.9, "SLIDE"), (590.9, 595.0, "CLOSE"), (595.0, 617.4, "SLIDE"), (617.4, 627.4, "MED"), (627.4, 636.3, "SLIDE"),
 (636.3, 646.2, "CLOSE"), (646.2, 655.1, "SLIDE"), (655.1, 662.2, "CLOSE"), (662.2, 675.4, "SLIDE"), (675.4, 681.0, "CLOSE"),
 (681.0, 688.0, "SLIDE"), (688.0, 698.0, "MED"), (698.0, 706.3, "SLIDE"), (706.3, 727.0, "CLOSE"), (727.0, 777.0, "SLIDE"),
 (777.0, 795.3, "MED"), (795.3, 803.2, "SLIDE"), (803.2, 816.0, "CLOSE"), (816.0, 854.5, "SLIDE"), (854.5, 872.7, "WIDE"),
 (872.7, 876.5, "SLIDE"), (876.5, 884.0, "WIDE"), (884.0, 894.1, "SLIDE"), (894.1, 897.0, "WIDE"), (897.0, 905.1, "SLIDE"),
 (905.1, 918.9, "WIDE"), (918.9, 924.0, "SLIDE"), (924.0, 937.0, "WIDE"), (937.0, 986.2, "SLIDE"), (986.2, 991.5, "MED"),
 (991.5, 1077.0, "SLIDE"), (1077.0, 1092.0, "MED"), (1092.0, 1131.0, "DEMO"), (1131.0, 1138.0, "CLOSE"), (1138.0, 1175.0, "DEMO"),
 (1175.0, 1205.0, "MED"), (1205.0, 1213.0, "MED"), (1213.0, 1300.0, "WIDE")]

# C3 kad pembetulan fakta (keputusan terkunci #1). Teks daripada slaid.
CORR = [(752.6, 758.5, "PEP dimulakan dalam 72 jam;\nregimen selama 28 hari."), (771.0, 777.0, "Regimen PEP: 28 hari berturut-turut."),
        (787.6, 793.0, "Jangkitan utama: Hepatitis B (HBV),\nHepatitis C (HCV) dan HIV."), (909.5, 915.0, "PEP: mulakan seawal mungkin,\ndalam tempoh 72 jam."),
        (980.0, 986.0, "PEP: mulakan seawal mungkin,\ndalam tempoh 72 jam."), (1192.4, 1198.6, "PEP: mulakan dalam 72 jam;\nregimen selama 28 hari.")]
# D1 label demo (ikut ayat disebut)
DEMO_LABELS = [(1131.6, 1138.5, "JANGAN recap jarum"), (1161.0, 1167.0, "Buang jarum terus ke bekas sharps"), (1179.9, 1184.5, "Basuh • Lapor")]
LT_IN, LT_OUT = 19.1, 29.6

# ======================= KAMERA =======================
CAM = {"WIDE": (1997, 887, 3154, False), "MED": (2360, 810, 2240, True), "CLOSE": (1830, 980, 1500, True), "DEMO": (2130, 1010, 1300, False)}
TRACK = None
tp = os.path.join(WORK, "track.json")
if os.path.exists(tp):
    TRACK = json.load(open(tp))
def presenter_x(s):
    if not TRACK: return None
    ts = TRACK["t"]; xs = TRACK["x"]
    return float(np.interp(s, ts, xs))

def seq_at(s):
    for i, (a, b, c) in enumerate(SEQ):
        if a <= s < b: return i, a, b, c
    return len(SEQ) - 1, *SEQ[-1]

def cam_window(s, c, a, b):
    cx, cy, w, follow = CAM[c]
    px = presenter_x(s)
    if follow and px is not None:
        if c == "CLOSE": cx = px
        else: cx = min(max(cx, px + 250), px + 700) if False else max(px + 300, min(cx, px + 650))
    z = 1 + 0.035 * ease((s - a) / max(b - a, 0.1))
    return cx, cy, w / z

def crop_frame(fr_, cx, cy, cw, outw, outh):
    ch = cw * outh / outw
    x0 = min(max(cx - cw / 2, 0), SW - cw); y0 = min(max(cy - ch / 2, 0), SH - ch)
    return Image.fromarray(fr_).crop((int(x0), int(y0), int(x0 + cw), int(y0 + ch))).resize((outw, outh), Image.BILINEAR)

# ======================= ASET =======================
def rounded(im, r):
    m = Image.new("L", im.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, im.size[0] - 1, im.size[1] - 1), r, fill=255)
    out = im.convert("RGBA"); out.putalpha(m); return out
def shadow(size, r, blur=18, alpha=110):
    pad = blur * 3; s = Image.new("RGBA", (size[0] + pad * 2, size[1] + pad * 2), (0, 0, 0, 0))
    ImageDraw.Draw(s).rounded_rectangle((pad, pad, pad + size[0], pad + size[1]), r, fill=(0, 0, 0, alpha))
    return s.filter(ImageFilter.GaussianBlur(blur)), pad
def text_box(lines, pad=(26, 16), radius=14, fill=(0, 0, 0, 170), align="c"):
    d0 = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    ws = [d0.textbbox((0, 0), t, font=f) for t, f, c in lines]
    tw = max(b[2] - b[0] for b in ws); th = sum(b[3] - b[1] for b in ws) + 10 * (len(lines) - 1)
    im = Image.new("RGBA", (tw + pad[0] * 2, th + pad[1] * 2 + 8), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, im.size[0] - 1, im.size[1] - 1), radius, fill=fill)
    y = pad[1]
    for (t, f, c), b in zip(lines, ws):
        x = (im.size[0] - (b[2] - b[0])) // 2 - b[0] if align == "c" else pad[0] - b[0]
        d.text((x, y - b[1]), t, font=f, fill=c); y += b[3] - b[1] + 10
    return im

def fixed_slide9():
    im = Image.open(os.path.join(SLIDES, "image12.png")).convert("RGB")
    band = im.crop((0, 420, 1376, 768)).filter(ImageFilter.GaussianBlur(40))
    out = im.copy(); out.paste(band, (0, 420))
    lap = im.crop((470, 425, 895, 740)); nil = im.crop((900, 425, 1345, 740))
    out.paste(lap, (243, 425)); out.paste(nil, (688, 425))
    return out

g = np.linspace(0, 1, W)[None, :, None]
BG = Image.fromarray((np.array(NAVY)[None, None] * (1 - g) + np.array(BLUE)[None, None] * g).repeat(H, 0).astype(np.uint8)).convert("RGBA")
SLX, SLY, SLW = 60, 124, 1380; SLH = int(SLW * 768 / 1376)
CARD_W, CARD_H = 340, 600; CARD_X = W - CARD_W - 60; CARD_Y = SLY + (SLH - CARD_H) // 2
card_sh, card_pad = shadow((CARD_W, CARD_H), 22)
panel_sh, panel_pad = shadow((SLW, SLH), 18)

SL = []  # (start, chip_img, sharp, frost, reveals)
for f, st, chip, rv in SLIDE_LIST:
    im = fixed_slide9() if f == "SLIDE9_FIXED" else Image.open(os.path.join(SLIDES, f)).convert("RGB")
    if im.size != (1376, 768): im = im.resize((1376, 768), Image.LANCZOS)
    frost = Image.blend(im.filter(ImageFilter.GaussianBlur(12)), Image.new("RGB", im.size, (245, 248, 252)), 0.55)
    SL.append((st, chip, im, frost, rv))

def chip_img(txt):
    f = F("x", 28); d0 = ImageDraw.Draw(Image.new("RGB", (1, 1))); w = int(d0.textlength(txt, f)) + 52
    im = Image.new("RGBA", (w, 54), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, w - 1, 53), 27, fill=(*YEL, 255)); d.text((26, 10), txt, font=f, fill=NAVY); return im
CHIPS = {c: chip_img(c) for _, _, c, _ in SLIDE_LIST}; CHIPS[DEMO_CHIP[1]] = chip_img(DEMO_CHIP[1])

def lower_third():
    n = F("b", 40); p = F("m", 26); t = F("m", 24)
    l1 = "Al Baatul Ridwan Bin Mohamed"; l2 = "Bachelor of Medical and Health Sciences with Honours"; l3 = "Tutor: Sir Abdul Raimi Bin Abd Kadir"
    d0 = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    w = max(d0.textlength(l1, n), d0.textlength(l2, p), d0.textlength(l3, t)) + 70
    im = Image.new("RGBA", (int(w) + 12, 170), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((12, 0, im.size[0] - 1, 169), 14, fill=(*NAVY, 235)); d.rectangle((0, 0, 11, 169), fill=YEL)
    d.text((40, 18), l1, font=n, fill=WHITE); d.text((40, 76), l2, font=p, fill=SKY); d.text((40, 118), l3, font=t, fill=YEL)
    return im
LT = lower_third()

def corr_img(txt):
    head = ("PEMBETULAN FAKTA", F("x", 24), YEL)
    lines = [head] + [(l, F("s", 30), WHITE) for l in txt.split("\n")]
    im = text_box(lines, pad=(28, 18), radius=16, fill=(*NAVY, 238), align="l")
    d = ImageDraw.Draw(im); d.rounded_rectangle((0, 0, 9, im.size[1] - 1), 4, fill=YEL); return im
CORR_IMGS = [(a, b, corr_img(t)) for a, b, t in CORR]
def label_img(txt):
    return text_box([(txt, F("x", 40), NAVY)], pad=(30, 16), radius=16, fill=(*YEL, 245))
DEMO_IMGS = [(a, b, label_img(t)) for a, b, t in DEMO_LABELS]
DRAFT = text_box([("DRAF v1 — sari kata & pembetulan belum disahkan", F("m", 20), WHITE)], pad=(14, 8), radius=8, fill=(180, 30, 30, 200))

title_img = Image.open(os.path.join(SLIDES, "image1.png")).convert("RGB")
tk = max(W / title_img.width, H / title_img.height)
TITLE_BASE = title_img.resize((int(title_img.width * tk) + 2, int(title_img.height * tk) + 2), Image.LANCZOS)

def end_card():
    im = BG.copy(); d = ImageDraw.Draw(im)
    f1 = F("x", 92); f2 = F("s", 40); f3 = F("m", 28)
    t1 = "CEGAH • LAPOR • NILAI • SUSUL"; t2 = "Keselamatan anggota penjagaan kesihatan ialah tanggungjawab bersama."; t3 = "Terima kasih"
    for t, f, c, y in [(t3, f2, SKY, 330), (t1, f1, YEL, 420), (t2, f3, WHITE, 580)]:
        w = d.textlength(t, font=f); d.text(((W - w) / 2, y), t, font=f, fill=c)
    return im
ENDC = end_card()

# ======================= SARI KATA =======================
FIX = [("MDMH", "NBMH"), ("berjagin", "berjangkit"), ("klinika ", "klinikal "), ("klinika.", "klinikal."), ("perusahaan jarum", "pelupusan jarum"), ("Lain kedua", "Kedua"),
 ("tercebar", "tercemar"), ("mucosa", "mukosa"), ("membran mucos", "membran mukus"), ("eczema", "ekzema"), ("Ektosisnya", "Ekosistem"), ("memenimumkan", "meminimumkan"),
 ("pesen kandung", "pesakit"), ("pesen", "pesakit"), ("passion", "pesakit"), ("Cuali", "troli"), ("story", "troli"), ("Jauh yang terpakai", "Jarum yang terpakai"),
 ("penutup jauh", "penutup jarum"), ("Kunci paling tamu", "Punca paling utama"), ("tercuti tangan", "tercucuk tangan"), ("beli kek balik", "recap balik"),
 ("Serta mata", "serta-merta"), ("serta mata", "serta-merta"), ("keadaan pemindahan", "kaedah pemindahan"), ("Tanpa setuk", "tanpa sentuh"), ("Prinsip setelah", "Prinsip mutlak"),
 ("Lupusan benda", "pelupusan benda"), ("Usupkan", "tusukan"), ("bekas terangnya", "bekas berada"), ("Lima langkah segala", "Lima langkah segera"), ("Pasca kecemasan", "pasca-kecederaan"),
 ("kesukaan jarum", "tusukan jarum"), ("Kuas tip keras", "kaustik keras"), ("agent", "agen"), ("Itu lapu", "Itu lapor"), ("lapu", "lapor"), ("Sista", "sister"), ("resiko", "risiko"),
 ("perawatan", "rawatan"), ("analisis jini", "analisis jenis"), ("Alat pengusup", "alat yang menusuk"), ("cecaiman", "cecair"), ("Berdarah lain", "bendalir lain"),
 ("Digital antibody", "titer antibodi"), ("Titel", "Titer"), ("Sejarah imunisasian", "sejarah imunisasi"), ("Prolapsi", "Profilaksis"), ("penjelahan", "pendedahan"),
 ("Namakan ubat antiviral", "Rawatan ubat antiviral"), ("Jakitan", "jangkitan"), ("Menggunakan keputusan", "memerlukan keputusan"), ("Intervention curve", "Activation curve"),
 ("Regulaman", "regimen"), ("Pemerhatian klinikal", "Amaran klinikal"), ("Jangan tambahkan", "Jangan tangguhkan"), ("Kujian", "ujian"), ("kesempatan terpahaman", "semakan kefahaman"),
 ("Soalan anggota", "Seorang anggota"), ("Tentang jarum", "tercucuk jarum"), ("coli", "troli"), ("Kesakit", "pesakit"), ("Singgi", "sinki"), ("singgi", "sinki"),
 ("mengicik muka", "memicit luka"), ("muka tu", "luka tu"), ("dimaklukan", "dimaklumkan"), ("PIP", "PEP"), ("dit김kan", "ditangguhkan"), ("dililai", "dinilai"),
 ("berumusan", "pelupusan"), ("setiap pasaran", "setiap masa"), ("Lampukan setiap kecegahan", "Laporkan setiap kecederaan"), ("penyelahan", "pendedahan"), ("Terus lampu", "Terus lapor"),
 ("susu balik", "susul balik"), ("profilat", "profilaksis"), ("Message", "Mesej"), ("perjalanan kesihatan", "penjagaan kesihatan"), ("Bukalah tudahan individu", "bukanlah pilihan individu"),
 ("Progression", "Prevention"), ("Hep A", "Hep …"), ("BD BD", "…"), ("center for", "Centers for"), ("US public health service guideline", "US Public Health Service guideline"), ("Kucuk", "Cucuk"), ("hypertitis", "hepatitis"), ("immunisasi", "imunisasi"), ("human imunisasi virus", "human immunodeficiency virus"),
 ("hadiah virus", "hati; virus"), ("profil aktif", "profilaksis"), ("Terlepas pembelahan", "selepas pendedahan"), ("Risiko akhir transmisi bergantung kepada jenis penyakit alat", "Risiko akhir transmisi bergantung kepada jenis pendedahan"),
 ("Kedalaman buka", "kedalaman luka"), ("tetap jangkitan semua", "status jangkitan sumber"), ("tersutkan jarum", "tusukan jarum"), ("kerjaan berlebihan", "keletihan berlebihan"),
 ("perhampiran bekas prosedur", "berhampiran lokasi prosedur"), ("dijadikan secara", "ditinggalkan secara"), ("Terganggalan mengatuhi arahan pengaktifan", "Kegagalan mematuhi arahan pengaktifan"),
 ("Perhenti keselamatan", "peranti keselamatan"), ("Sedia berhenti", "Sedia peranti"), ("Susungkan kerja sepaling teratur", "Susun ruang kerja supaya teratur"),
 ("bekas sistem mulai cepat", "bekas sisa mudah dicapai"), ("Spectrum procedure", "spektrum prosedur"), ("Kedalam bekas khas", "ke dalam bekas khas"), ("Jadikan bekas", "Gantikan bekas"),
 ("Jangan melolak", "Jangan menolak"), ("memasang jarum masuk", "memaksa jarum masuk"), ("bekas perhubungan", "bekas pelupusan"), ("jarum terjemah", "jarum tercemar"), ("gulau", "dulang"),
 ("Terlepas.", "selepas"), ("penilaian terang", "penilaian susulan"), ("Ia diakses tau", "…"), ("tiraian botol", "…"), ("Sedangkan klinikal", "Tindakan klinikal"),
 ("Melapung", "Melapor"), ("Menghilang risiko", "Menilai risiko"), ("meminum daya kekerusan", "membina budaya ketelusan"), ("membangunkan amalan", "membudayakan amalan"),
 ("Dan menggalakkan kesan trauma.", "Dan menggalakkan"), ("Dan mengurangkan penjagaan alat tajam", "pengendalian alat tajam"), ("penjagaan tersuka lah", "kejadian tusukan lah"),
 ("Dapat idiotik", "…"), ("Kita terus abu", "…"), ("Pakai gila", "…"), ("Recycling ni", "…"), ("Repat", "…"), ("Penyakit isteri", "penyakit …"), ("Toko", "…"),
 ("Jambi ke", "… ke"), ("Juka", "fizikal luka"), ("Scamper", "scalpel"), ("kejam", "tajam"), ("Bleak", "blade"), ("cuti action", "cucuk pesakit"), ("Dahangkan langsung", "…"),
 ("Syafi'i", "sharps bin"), ("Pancat balik eh", "…"), ("Pancat", "…"), ("Kena hangat", "…"), ("Mark.", "Mask,"), ("Yang makan tangan", "sarung tangan"), ("mengikut prosedur eh", "mengikut prosedur"),
 ("Jika kita unik", "jika diketahui"), ("Pertahanan fisik", "…"), ("Bagaimana pekerja", "…"), ("Status semua", "Status sumber"), ("status semua", "status sumber"),
 ("Kecepatan.", "…"), ("diperkankan", "…"), ("Kita susu", "Kita susul"), ("Cik Simi", "Cik …"), ("HipD", "Hep …"), ("Hib", "…"), ("HIB", "…"), ("Be.", "…"),
 ("Terima kasih.", None)]
# nombor yang ditanda isu fakta -> "…" (kad pembetulan memaparkan fakta slaid)
FLAG_NUM = [(753.0, 754.5), (771.4, 776.0), (788.9, 789.8), (910.5, 913.4), (981.3, 982.4), (1184.9, 1192.0), (1192.7, 1193.7)]
HIDE = [(18.9, 29.8), (1145.0, 1161.0)]
HALLU = re.compile(r"terima kasih|menonton|subscribe|like, komen", re.I)

def build_subs():
    lt = json.load(open(os.path.join(WORK, "transcript_large.json")))
    gp = json.load(open(os.path.join(WORK, "gaps_novad.json")))
    words = []
    for s in lt:
        for w in s["words"]: words.append([w["s"], w["e"], w["w"].strip(), w["p"]])
    for g_ in gp:
        for a, b, txt, nsp, lp in g_["asr"]:
            if HALLU.search(txt) or nsp > 0.5 or b - a > 8: continue
            ws = txt.split(); dt = (b - a) / max(len(ws), 1)
            for i, w in enumerate(ws): words.append([a + i * dt, a + (i + 1) * dt, w, 0.6])
    words.sort(key=lambda x: x[0])
    for w in words:
        if any(a <= w[0] < b for a, b in FLAG_NUM) and re.search(r"\d", w[2]): w[2] = "…"
        elif w[3] < 0.2: w[2] = "…"
    # chunk: gabung frasa pendek; pecah pada jeda > 0.6 s, > 84 aksara, atau hujung ayat bila sudah >= 30 aksara
    chunks = []; cur = []
    def flush():
        if cur:
            toks = []
            for j, x in enumerate(cur):
                w_ = x[2]
                if j > 0 and w_[:1].isupper() and not w_.isupper() and w_ not in ("Hepatitis", "Sir", "Encik", "Cik", "SOP"): w_ = w_[0].lower() + w_[1:]
                if j < len(cur) - 1: w_ = w_.rstrip(".")
                toks.append(w_)
            low = sum(1 for x in cur if x[2] == "…") / len(cur)
            txt = "[kurang jelas]" if low >= 0.4 and len(cur) >= 3 else " ".join(toks)
            chunks.append([cur[0][0], cur[-1][1], txt]); cur.clear()
    for i, w in enumerate(words):
        if any(a <= w[0] < b for a, b in HIDE): flush(); continue
        if cur:
            cl = len(" ".join(x[2] for x in cur))
            if w[0] - cur[-1][1] > 0.6 or cl + len(w[2]) > 84 or (cur[-1][2].endswith((".", "?", "!")) and cl >= 30): flush()
        cur.append(w)
    flush()
    out = []
    for a, b, t in chunks:
        for o, n in FIX:
            t = re.sub(re.escape(o), "" if n is None else n.replace("\\", "\\\\"), t, flags=re.I)
        t = re.sub(r"(…\s*){2,}", "… ", t); t = re.sub(r"\s+", " ", t).strip(); t = re.sub(r"\s+-", "-", t)
        if not t or HALLU.search(t) or t in ("…", ".", "Haa.", "Okey.", "Okay"): continue
        t = t[0].upper() + t[1:]
        out.append([a, max(b, a + 1.0), t])
    for i in range(len(out) - 1): out[i][1] = min(out[i][1] + 0.3, out[i + 1][0])
    return out

def wrap(t, n=44):
    if len(t) <= n: return t
    ws = t.split(); best = None
    for i in range(1, len(ws)):
        a, b = " ".join(ws[:i]), " ".join(ws[i:])
        sc = max(len(a), len(b))
        if best is None or sc < best[0]: best = (sc, a + "\n" + b)
    return best[1]

def srt_time(x):
    h = int(x // 3600); m = int(x % 3600 // 60); s = x % 60
    return f"{h:02d}:{m:02d}:{int(s):02d},{int(round((s - int(s)) * 1000)):03d}"

# ======================= PREP =======================
if MODE == "prep":
    subs = build_subs(); json.dump(subs, open(os.path.join(WORK, "subs.json"), "w"), ensure_ascii=False, indent=0)
    with open(os.path.join(WORK, "subs_output_timeline.srt"), "w") as f:  # timecode OUTPUT (tambah kad tajuk)
        for i, (a, b, t) in enumerate(subs, 1): f.write(f"{i}\n{srt_time(a + TITLE)} --> {srt_time(b + TITLE)}\n{wrap(t)}\n\n")
    aud = os.path.join(WORK, "aud.wav"); mus = os.path.join(WORK, "music.wav"); mix = os.path.join(WORK, "mix.wav")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", SRC, "-vn", "-ac", "2", "-ar", "48000",
                    "-af", "highpass=f=80,afftdn=nr=10:nf=-40,loudnorm=I=-16:TP=-1.5:LRA=11", aud], check=True)
    sr = 48000
    def pad(sec, fin, fout):
        n = int(sec * sr); tt = np.arange(n) / sr
        env = np.minimum(1, tt / fin) * np.clip((sec - tt) / fout, 0, 1)
        sig = sum(np.sin(2 * np.pi * f * tt) * a for f, a in [(220, .5), (277.18, .35), (329.63, .35), (415.3, .2), (110, .4)])
        sig += 0.15 * np.sin(2 * np.pi * 659.26 * tt) * (0.5 + 0.5 * np.sin(2 * np.pi * 2 * tt))
        return sig / np.abs(sig).max() * 10 ** (-20 / 20) * env
    total = int((DUR + 0.5) * sr); m = np.zeros(total)
    a1 = pad(TITLE + 0.6, 0.8, 1.0); m[:len(a1)] += a1
    a2 = pad(END_LEN + 0.2, 0.6, 1.2); st = int((TITLE + END_AT) * sr); m[st:st + len(a2)] += a2[:total - st]
    with wave.open(mus, "wb") as w_:
        w_.setnchannels(2); w_.setsampwidth(2); w_.setframerate(sr); w_.writeframes((np.stack([m, m], 1) * 32767).astype(np.int16).tobytes())
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", mus, "-i", aud, "-filter_complex",
                    f"[1]adelay={int(TITLE*1000)}|{int(TITLE*1000)},atrim=0:{TITLE+END_AT+0.3},afade=t=out:st={TITLE+END_AT}:d=0.3[d];[0][d]amix=inputs=2:duration=first:normalize=0",
                    "-t", str(DUR), mix], check=True)
    print("PREP DONE", len(subs), "subs", flush=True); sys.exit(0)

# ======================= RENDER =======================
T0, T1, OUT = float(sys.argv[5]), float(sys.argv[6]), sys.argv[7]
SUBS = json.load(open(os.path.join(WORK, "subs.json")))
SUBF = F("s", 40); _subcache = {}
def sub_im(i):
    if i not in _subcache: _subcache[i] = text_box([(l, SUBF, WHITE) for l in wrap(SUBS[i][2]).split("\n")], pad=(28, 14), fill=(0, 0, 0, 175))
    return _subcache[i]

def paste(canvas, im, x, y, a=1.0):
    if a <= 0: return
    if a < 1:
        im = im.copy(); im.putalpha(im.getchannel("A").point(lambda v: int(v * a)))
    canvas.alpha_composite(im, (int(x), int(y)))

def slide_at(s):
    cur = None
    for e in SL:
        if s >= e[1 - 1]: cur = e
    return cur
_panel_cache = {}
def slide_panel(e, s):
    st, chip, sharp, frost, rv = e
    state = tuple(min(1.0, round(ease((s - t) / 0.4), 2)) if s >= t else 0.0 for _, t in rv)
    key = (st, state)
    if key in _panel_cache: return _panel_cache[key]
    im = sharp.copy()
    for (r, t), p in zip(rv, state):
        if p < 1:
            fz = frost.crop(r); sh = sharp.crop(r); im.paste(Image.blend(fz, sh, p), r[:2])
    pim = rounded(im.resize((SLW, SLH), Image.LANCZOS), 18)
    if len(_panel_cache) > 64: _panel_cache.clear()
    _panel_cache[key] = pim; return pim

def chip_for(s):
    if s >= DEMO_CHIP[0]: return CHIPS[DEMO_CHIP[1]]
    e = slide_at(s); return CHIPS[e[1]] if e and s >= 46.6 else None

def compose(t, fr_):
    if t < TITLE:
        z = 1 + 0.04 * (t / TITLE); iw, ih = TITLE_BASE.size
        im = TITLE_BASE.crop(((iw - W / z) / 2, (ih - H / z) / 2, (iw + W / z) / 2, (ih + H / z) / 2)).resize((W, H), Image.BILINEAR).convert("RGBA")
        return im
    s = t - TITLE
    if s >= END_AT:
        u = s - END_AT; c = ENDC.copy()
        if u < 0.4: c = Image.blend(BG, ENDC, ease(u / 0.4))
        if t > DUR - 0.6: c = Image.blend(c, Image.new("RGBA", (W, H), (0, 0, 0, 255)), (t - (DUR - 0.6)) / 0.6)
        return c
    i, a, b, c = seq_at(s)
    slide_mode = c == "SLIDE"
    if not slide_mode:
        cx, cy, cw = cam_window(s, c, a, b); canvas = crop_frame(fr_, cx, cy, cw, W, H).convert("RGBA")
        if LT_IN <= s < LT_OUT:
            p = eout((s - LT_IN) / 0.4); q = ease((LT_OUT - s) / 0.15)
            paste(canvas, LT, 70 - (1 - p) * 120, H - 280, min(p, q) if p < 1 else q)
        ch = chip_for(s)
        if ch is not None: paste(canvas, ch, 40, 30)
        for a2, b2, im in DEMO_IMGS:
            if a2 <= s < b2: pp = eout((s - a2) / 0.35); paste(canvas, im, 40 - (1 - pp) * 60, 100, min(1, (s - a2) / 0.15))
        cx_corr, cy_corr = W - 40, 80
    else:
        canvas = BG.copy(); u = s - a; e = slide_at(s)
        p = eout(u / 0.4); sc = 0.94 + 0.06 * p; panel = slide_panel(e, s)
        if p < 1: panel = panel.resize((int(SLW * sc), int(SLH * sc)), Image.BILINEAR)
        pw, ph = panel.size
        paste(canvas, panel_sh, SLX + (SLW - pw) / 2 - panel_pad, SLY + (SLH - ph) / 2 - panel_pad + 8, min(1, 0.6 + u / 0.75))
        paste(canvas, panel, SLX + (SLW - pw) / 2, SLY + (SLH - ph) / 2, min(1, 0.6 + u / 0.6))
        px = presenter_x(s) or 1800
        card = rounded(crop_frame(fr_, px, 1060, 760, CARD_W, CARD_H), 22)
        cxp = CARD_X + (1 - eout((u - 0.1) / 0.4)) * 420
        paste(canvas, card_sh, cxp - card_pad, CARD_Y - card_pad + 8); paste(canvas, card, cxp, CARD_Y)
        ch = chip_for(s)
        if ch is not None: paste(canvas, ch, SLX, 44)
        cx_corr, cy_corr = W - 40, CARD_Y + CARD_H + 16
    for a2, b2, im in CORR_IMGS:
        if a2 <= s < b2:
            pp = eout((s - a2) / 0.35); q = ease((b2 - s) / 0.2)
            x = cx_corr - im.size[0] + (1 - pp) * 80
            y = cy_corr if not slide_mode else min(cy_corr, H - im.size[1] - 140)
            if slide_mode: x = W - im.size[0] - 30
            paste(canvas, im, x, y, min(1, (s - a2) / 0.15) * q)
    for k, (a2, b2, txt) in enumerate(SUBS):
        if a2 <= s < b2:
            im = sub_im(k)
            ys = (H - im.size[1] - 18) if slide_mode else (H - 110 - im.size[1])
            xs = (SLX + SLW / 2 - im.size[0] / 2) if slide_mode else (W - im.size[0]) / 2
            paste(canvas, im, xs, ys, min(1, (s - a2) / 0.12)); break
    paste(canvas, DRAFT, W - DRAFT.size[0] - 20, 16)
    return canvas

f0 = int(round(T0 * FPS)); f1 = int(round(min(T1, DUR) * FPS))
src_start = max(0.0, f0 / FPS - TITLE)
dec = subprocess.Popen(["ffmpeg", "-v", "error", "-ss", f"{src_start:.4f}", "-i", SRC, "-vf", f"fps={FPS}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                       stdout=subprocess.PIPE, bufsize=SW * SH * 3 * 2)
enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                        "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", "-g", "60", OUT], stdin=subprocess.PIPE)
fsz = SW * SH * 3; fr_ = np.zeros((SH, SW, 3), np.uint8)
for i in range(f0, f1):
    t = i / FPS
    if TITLE <= t < TITLE + SRC_END:
        buf = dec.stdout.read(fsz)
        if len(buf) == fsz: fr_ = np.frombuffer(buf, np.uint8).reshape(SH, SW, 3)
    enc.stdin.write(compose(t, fr_).convert("RGB").tobytes())
    if (i - f0) % 900 == 0: print(f"{OUT}: frame {i - f0}/{f1 - f0}", flush=True)
enc.stdin.close(); enc.wait(); dec.kill()
print("CHUNK DONE", OUT, flush=True)
