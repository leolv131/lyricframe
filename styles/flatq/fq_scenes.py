"""《5:20AM》共享组件：手机界面、照片、云、羊、闪电、街景、写字楼、河南地图等"""
import math
import numpy as np
import skia
from fq import *
import people as P
from props import *

BEAT = 60 / 123.047
WARM_WALL = '#f2c9a8'


# ---------------------------------------------------------------- phone (big, centred)
def phone(f, cx=960, cy=560, w=520, h=980, screen='#101225', rot=0.0, hand=True):
    """draw a phone held in hand; returns screen rect (x,y,w,h). caller draws content inside a clip."""
    f.c.save(); f.c.translate(cx, cy); f.c.rotate(rot); f.c.translate(-cx, -cy)
    x, y = cx - w / 2, cy - h / 2
    f.rect(x, y, w, h, '#1c1c24', INK, 6, r=60)
    sx, sy, sw, sh = x + 22, y + 22, w - 44, h - 44
    f.rect(sx, sy, sw, sh, screen, None, r=42)
    f.c.restore()
    if hand:
        # thumb + fingers wrapping the sides
        f.oval(cx - w / 2 - 6, cy + 220, 34, 70, P.SKIN, INK, 5)
        for k in range(3):
            f.oval(cx + w / 2 + 6, cy + 120 + k * 80, 30, 36, P.SKIN, INK, 5)
        sleeve = '#8f97ad'
        f.rect(cx - 200, cy + h / 2 - 40, 400, 400, sleeve, INK, 6, r=40)
        f.oval(cx, cy + h / 2 - 30, 210, 90, P.SKIN, INK, 6)
    return (sx, sy, sw, sh)


def clip_rect(f, r, radius=42):
    f.c.save(); f.c.clipRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(*r), radius, radius), skia.ClipOp.kIntersect, True)


def phone_status(f, r, time_str='5:20', col='#ffffff'):
    x, y, w, h = r
    f.text(x + 40, y + 50, time_str, 28, col, 'bold')
    f.rect(x + w - 80, y + 30, 44, 22, None, col, 3, r=6); f.rect(x + w - 76, y + 34, 14, 14, col, r=3)


# ---------------------------------------------------------------- photo of the two
def couple_photo(f, x, y, w, h, t=0.0, half=None, tear=0.0, mosaic=0.0, rot=0.0):
    """polaroid of the two. half='l'/'r' draws only one half (torn). tear 0..1 opens a jagged gap."""
    f.c.save(); f.c.translate(x + w / 2, y + h / 2); f.c.rotate(rot); f.c.translate(-(x + w / 2), -(y + h / 2))
    def content():
        f.rect(x, y, w, h, '#fbf7ee', INK, 5, r=6)
        px, py, pw, ph = x + w * 0.07, y + h * 0.06, w * 0.86, h * 0.7
        f.vgrad(['#ffcf9a', '#ff9f8a'], py, py + ph, px, px + pw)
        f.circle(px + pw * 0.8, py + ph * 0.25, pw * 0.08, '#fff3c0')
        sc = pw / 900
        P.draw(f, 'he', px + pw * 0.33, py + ph * 1.18, 1.25 * sc * 1.9, 'peace', 'grin', t=1)
        P.draw(f, 'she', px + pw * 0.68, py + ph * 1.18, 1.25 * sc * 1.9, 'wave', 'love', t=1)
        f.rect(px, py, pw, ph, None, INK, 4)
        f.rect(x - 5, py + ph + 2, w + 10, h, '#fbf7ee')     # cover legs below photo area
        f.rect(x, y, w, h, None, INK, 5, r=6)
        f.text(x + w / 2, y + h * 0.9, '郑州 · 那年夏天', h * 0.06, '#8a7a6a', 'sans', 'center')
        if mosaic > 0:
            blk = max(6, int(60 * mosaic))
            # mosaic overlay: coarse blocks sampled from a fixed palette pattern
            r = np.random.default_rng(3)
            for yy in np.arange(py, py + ph, blk):
                for xx in np.arange(px, px + pw, blk):
                    c = ['#ffcf9a', '#ff9f8a', '#8f97ad', '#f7ead6', '#4a2e2a', '#3a2a35', '#ffdcc4'][int(r.integers(0, 7))]
                    f.rect(float(xx), float(yy), float(blk), float(blk), c, a=min(1.0, mosaic * 1.4))
    jag = [(x + w / 2 + (10 if i % 2 else -10), y + i * h / 10) for i in range(11)]
    if half is None and tear <= 0:
        content()
    else:
        for side in (('l', 'r') if half is None else (half,)):
            f.c.save()
            p = skia.Path()
            if side == 'l':
                p.moveTo(x - 20, y - 20); [p.lineTo(*q) for q in jag]; p.lineTo(x - 20, y + h + 20)
                dx = -tear * w * 0.25
            else:
                p.moveTo(x + w + 20, y - 20); [p.lineTo(*q) for q in jag]; p.lineTo(x + w + 20, y + h + 20)
                dx = tear * w * 0.25
            p.close()
            f.c.translate(dx, tear * (12 if side == 'l' else -12))
            f.c.rotate(tear * (-4 if side == 'l' else 4))
            f.c.clipPath(p, True)
            content()
            f.c.restore()
            f.c.save(); f.c.translate(dx, tear * (12 if side == 'l' else -12)); f.c.rotate(tear * (-4 if side == 'l' else 4))
            f.curve(jag, '#e8e0d0', 6); f.curve(jag, INK, 2)
            f.c.restore()
    f.c.restore()


# ---------------------------------------------------------------- weather / cute things
def cloud(f, x, y, s=1.0, col='#ffffff', face=None, line=INK, a=1.0):
    pts = [(x - 120 * s, y + 30 * s), (x - 130 * s, y - 10 * s), (x - 80 * s, y - 50 * s), (x - 20 * s, y - 75 * s), (x + 50 * s, y - 60 * s),
           (x + 110 * s, y - 30 * s), (x + 130 * s, y + 20 * s), (x + 60 * s, y + 45 * s), (x - 40 * s, y + 48 * s)]
    f.blob(pts, col, line, 5 * s if line else 0, a)
    if face:
        ex = 32 * s
        if face == 'happy':
            for sg in (-1, 1): f.curve([(x + sg * ex - 10 * s, y), (x + sg * ex, y - 10 * s), (x + sg * ex + 10 * s, y)], INK, 4 * s)
            f.curve([(x - 10 * s, y + 14 * s), (x, y + 22 * s), (x + 10 * s, y + 14 * s)], INK, 4 * s)
        elif face == 'worried':
            for sg in (-1, 1): f.circle(x + sg * ex, y, 6 * s, INK)
            f.curve([(x - 10 * s, y + 22 * s), (x, y + 15 * s), (x + 10 * s, y + 22 * s)], INK, 4 * s)
        elif face == 'sad':
            for sg in (-1, 1): f.line(x + sg * ex - 9 * s, y, x + sg * ex + 9 * s, y + 3 * s, INK, 4 * s)
            f.curve([(x - 10 * s, y + 22 * s), (x, y + 15 * s), (x + 10 * s, y + 22 * s)], INK, 4 * s)
        for sg in (-1, 1): f.oval(x + sg * ex * 1.6, y + 14 * s, 12 * s, 6 * s, '#ff9fb0', None, a=0.7 * a)


def sheep(f, x, y, s=1.0, t=0.0):
    for k in range(7):
        a = k / 7 * 6.283
        f.circle(x + math.cos(a) * 34 * s, y + math.sin(a) * 22 * s, 24 * s, '#ffffff', INK, 4 * s)
    f.oval(x, y, 44 * s, 30 * s, '#ffffff', None)
    f.oval(x + 46 * s, y - 6 * s, 20 * s, 22 * s, '#5a4652', INK, 4 * s)
    f.circle(x + 52 * s, y - 10 * s, 3.5 * s, '#ffffff')
    for k in (-1, 1):
        f.line(x + k * 18 * s, y + 24 * s, x + k * 18 * s, y + 46 * s, '#5a4652', 7 * s)


def fence(f, x, y, s=1.0):
    for k in range(4):
        f.rect(x + k * 40 * s, y - 70 * s, 16 * s, 80 * s, '#d9a46a', INK, 3 * s, r=4 * s)
    f.rect(x - 10 * s, y - 52 * s, 150 * s, 12 * s, '#c98a5a', INK, 3 * s)
    f.rect(x - 10 * s, y - 22 * s, 150 * s, 12 * s, '#c98a5a', INK, 3 * s)


def bolt(f, x, y, s=1.0, col='#ffe27a', a=1.0):
    pts = [(x, y), (x - 50 * s, y + 160 * s), (x - 5 * s, y + 160 * s), (x - 40 * s, y + 330 * s), (x + 70 * s, y + 120 * s), (x + 20 * s, y + 120 * s), (x + 60 * s, y)]
    f.poly(pts, col, INK, 5 * s, a)


def rain(f, x0, y0, w, h, t, n=60, col='#bfd8ff', a=0.6, seed=1, speed=900, slant=0.25):
    r = np.random.default_rng(seed)
    xs = r.uniform(0, w, n); ph = r.uniform(0, h, n)
    for xx, pp in zip(xs, ph):
        yy = (pp + t * speed) % h
        f.line(x0 + xx, y0 + yy, x0 + xx - slant * 30, y0 + yy + 30, col, 3, a)


def speed_lines(f, t, n=24, col='#ffffff', a=0.5, seed=2):
    r = np.random.default_rng(seed)
    for i in range(n):
        y = r.uniform(100, 1000); L = r.uniform(120, 400)
        x = (r.uniform(0, W) - t * 2400) % (W + 400) - 200
        f.line(x, y, x + L, y, col, 4, a)


def bubble(f, x, y, r, col='#ffffff', tail=None):
    f.circle(x, y, r, col, INK, 6)
    if tail:
        for k, (tx, ty, rr) in enumerate(tail): f.circle(tx, ty, rr, col, INK, 5)


def confetti(f, t, n=60, seed=5, y0=-100):
    r = np.random.default_rng(seed)
    cols = ['#ff5f7e', '#5ad6c8', '#4a86d8', '#ffffff', '#ffcf4a']
    for i in range(n):
        x0 = r.uniform(0, W); sp = r.uniform(250, 500); ph = r.uniform(0, 6)
        y = (y0 + t * sp + r.uniform(0, 1200)) % 1200 - 100
        x = x0 + math.sin(t * 3 + ph) * 30
        f.c.save(); f.c.translate(x, y); f.c.rotate(t * 200 + i * 37)
        f.rect(-8, -14, 16, 28, cols[i % 5], r=3); f.c.restore()


# ---------------------------------------------------------------- street corners (Zhengzhou)
def traffic_light(f, x, y, s=1.0, on='g'):
    f.rect(x - 8 * s, y, 16 * s, 360 * s, '#3a3a48', INK, 3)
    f.rect(x - 34 * s, y - 150 * s, 68 * s, 160 * s, '#2a2a34', INK, 4, r=12 * s)
    for k, c in enumerate(['r', 'y', 'g']):
        col = {'r': '#ff4a5a', 'y': '#ffcf4a', 'g': '#5ad67a'}[c] if c == on else '#4a4a58'
        f.circle(x, y - 120 * s + k * 50 * s, 18 * s, col)
        if c == on: f.radial(x, y - 120 * s + k * 50 * s, 60 * s, col, 0.0, a=0.5)


def zebra(f, y, h=140, col='#f4f1ea', a=0.9, gray_part=None):
    for k in range(10):
        x = 160 + k * 170
        c = col
        if gray_part is not None: c = '#9a9aa8' if x < gray_part else '#f4f1ea'
        f.rect(x, y, 100, h, c, r=6, a=a)


def stall_huilatang(f, x, ground, t=0.0, s=1.0):
    """胡辣汤早餐摊"""
    f.rect(x - 220 * s, ground - 300 * s, 440 * s, 30 * s, '#e8394f', INK, 5, r=8 * s)
    for k in range(6): f.rect(x - 220 * s + k * 73 * s, ground - 300 * s, 36 * s, 30 * s, '#ffffff', a=0.85)
    f.line(x - 200 * s, ground - 270 * s, x - 200 * s, ground, '#5a4a4a', 8 * s); f.line(x + 200 * s, ground - 270 * s, x + 200 * s, ground, '#5a4a4a', 8 * s)
    f.rect(x - 160 * s, ground - 140 * s, 320 * s, 140 * s, '#c9c9d6', INK, 5, r=6 * s)
    f.oval(x - 60 * s, ground - 150 * s, 80 * s, 26 * s, '#6a4a3a', INK, 5)                 # big pot
    f.rect(x - 140 * s, ground - 150 * s, 160 * s, 30 * s, '#9a9aa8', INK, 5, r=6 * s)
    for k in range(3):
        ph = t * 1.5 + k
        f.curve([(x - 90 * s + k * 30 * s + math.sin(ph + j) * 10 * s, ground - 180 * s - j * 40 * s) for j in range(4)], '#ffffff', 8 * s, a=0.6)
    f.rect(x + 40 * s, ground - 250 * s, 160 * s, 70 * s, '#fff4c0', INK, 4, r=6 * s)
    f.text(x + 120 * s, ground - 200 * s, '胡辣汤', 40 * s, '#c0392b', 'black', 'center')


def lantern(f, x, y, s=1.0, col='#ff5a4a', t=0.0):
    sw = math.sin(t * 2 + x) * 3 * s
    f.line(x, y - 40 * s, x + sw, y - 20 * s, INK, 3 * s)
    f.oval(x + sw, y, 26 * s, 22 * s, col, INK, 4 * s)
    f.radial(x + sw, y, 60 * s, '#ffcf4a', 0.0, a=0.35)
    f.rect(x + sw - 10 * s, y + 18 * s, 20 * s, 8 * s, '#ffcf4a', INK, 2 * s)


def night_market(f, t=0.0):
    f.vgrad(['#1e1c3a', '#3a2c5a', '#6a3f6a'], 0, 760)
    skyline(f, 760, t, col='#24223e', seed=11)
    f.rect(0, 760, W, 320, '#3a3248')
    for k in range(5):
        x = 200 + k * 380
        f.rect(x - 150, 520, 300, 240, ['#e86a5a', '#4a86d8', '#ffcf4a', '#5ad6c8', '#e86a5a'][k], INK, 5, r=10)
        f.rect(x - 150, 500, 300, 40, '#ffffff', INK, 5, r=8)
        f.rect(x - 120, 600, 240, 120, '#fff4c0', INK, 4, r=6)
    for k in range(14):
        lantern(f, 70 + k * 140, 420 + (k % 2) * 20, 1.0, t=t)
    f.line(0, 380, W, 400, INK, 3)


def crossroad(f, t=0.0, gray_part=None):
    f.vgrad(['#141634', '#2a2c5c'], 0, 640)
    skyline(f, 640, t, seed=7)
    f.rect(0, 640, W, 440, '#3a3b52')
    zebra(f, 820, 140, gray_part=gray_part)
    traffic_light(f, 200, 520, 1.0, 'g' if (t % 2) < 1.4 else 'y')
    traffic_light(f, 1720, 520, 1.0, 'r')


# ---------------------------------------------------------------- office / party
def office(f, t=0.0, mood='cold', monitor_text=None, glitch=False):
    f.vgrad(['#4a5070', '#5c6286'], 0, H)
    for k in range(6):   # window blinds / city at night behind
        f.rect(80 + k * 300, 80, 260, 360, '#22243e', INK, 4, r=4)
        for j in range(8): f.line(80 + k * 300, 100 + j * 44, 340 + k * 300, 100 + j * 44, '#3a3d60', 4)
    f.rect(0, 0, W, 60, '#e8f0ff', a=0.25)
    for k in range(4):
        f.rect(200 + k * 450, 20, 220, 16, '#f4fbff', r=8)        # ceiling lights
        f.radial(310 + k * 450, 40, 260, '#e8f4ff', 0.0, a=0.25)
    f.rect(0, 760, W, 320, '#7a7f9a', INK, 5)                       # desk
    f.rect(620, 330, 680, 420, '#2b2b38', INK, 6, r=16)              # monitor
    f.rect(640, 350, 640, 360, '#0f1f2a' if not glitch else '#101018', None, r=6)
    f.rect(920, 750, 80, 20, '#2b2b38', INK, 4)
    if monitor_text: monitor_text(f, 640, 350, 640, 360)


def keyboard(f, x, y, s=1.0):
    f.rect(x - 300 * s, y, 600 * s, 110 * s, '#d9dbe6', INK, 5, r=12 * s)
    for j in range(4):
        for i in range(14):
            f.rect(x - 280 * s + i * 40 * s, y + 12 * s + j * 24 * s, 32 * s, 18 * s, '#f4f5fa', INK, 2, r=4 * s)


def coffee(f, x, y, s=1.0, steam=False, t=0.0):
    p = skia.Path(); p.moveTo(x - 32 * s, y - 60 * s); p.lineTo(x + 32 * s, y - 60 * s); p.lineTo(x + 26 * s, y); p.lineTo(x - 26 * s, y); p.close()
    f.path(p, '#ffffff', INK, 4 * s)
    f.rect(x - 34 * s, y - 72 * s, 68 * s, 14 * s, '#6a4a3a', INK, 4 * s, r=4 * s)
    f.rect(x - 30 * s, y - 40 * s, 60 * s, 18 * s, '#c27a5a', None)


# ---------------------------------------------------------------- 河南地图
HENAN = [(110.4, 34.6), (111.0, 35.0), (112.0, 35.1), (112.8, 35.25), (113.5, 35.9), (114.0, 36.3), (114.6, 36.35), (114.9, 36.0), (115.4, 36.1),
         (116.0, 35.9), (115.6, 35.2), (116.1, 34.9), (116.6, 34.4), (115.9, 33.9), (115.6, 33.4), (115.9, 32.8), (115.3, 32.4), (114.9, 31.9),
         (114.2, 31.6), (113.7, 31.8), (113.0, 32.4), (112.3, 32.4), (111.6, 32.8), (111.0, 33.3), (110.6, 33.6), (110.8, 34.2)]
CITY = {'郑州': (113.65, 34.76), '洛阳': (112.45, 34.62), '开封': (114.31, 34.80), '平顶山': (113.19, 33.77), '许昌': (113.85, 34.04),
        '新乡': (113.93, 35.30), '信阳': (114.09, 32.15), '南阳': (112.53, 33.00), '濮阳': (115.03, 35.76), '安阳': (114.39, 36.10),
        '鹤壁': (114.30, 35.75), '焦作': (113.24, 35.22), '三门峡': (111.20, 34.77), '驻马店': (114.02, 33.01), '漯河': (114.02, 33.58),
        '周口': (114.70, 33.63), '商丘': (115.66, 34.41)}
ROUTE = ['洛阳', '平顶山', '许昌', '开封', '新乡', '信阳', '南阳', '濮阳', '安阳', '鹤壁', '焦作', '三门峡', '驻马店', '漯河', '周口', '商丘']


def map_xy(lon, lat, cx=960, cy=570, sc=175):
    return (cx + (lon - 113.5) * sc, cy - (lat - 34.0) * sc * 1.18)


def henan_map(f, lit=0, t=0.0, heart=0.0, cx=960, cy=570, sc=175, labels=True, highlight=None):
    """lit = number of route segments lit (float). heart 0..1 morphs lit route into a heart."""
    f.vgrad(['#bfe8ff', '#e8f6ff'], 0, H)
    for k in range(6): cloud(f, 150 + k * 330, 140 + (k % 2) * 80, 0.6, '#ffffff', line=None, a=0.8)
    pts = [map_xy(a, b, cx, cy, sc) for a, b in HENAN]
    f.blob([(x + 12, y + 16) for x, y in pts], '#9fc8a0', None)        # shadow
    f.blob(pts, '#c8ecb0', INK, 6)
    # route
    rp = [map_xy(*CITY[c], cx, cy, sc) for c in ROUTE]
    if heart > 0:
        n = len(rp)
        hp = []
        for i in range(n):
            a = i / n * 2 * math.pi
            hx = 16 * math.sin(a) ** 3; hy = -(13 * math.cos(a) - 5 * math.cos(2 * a) - 2 * math.cos(3 * a) - math.cos(4 * a))
            hp.append((cx + hx * 17, cy + hy * 17 - 20))
        rp = [(lerp(x, hx, ease(heart)), lerp(y, hy, ease(heart))) for (x, y), (hx, hy) in zip(rp, hp)]
        rp = rp + [rp[0]] if heart > 0.95 else rp
    full = int(lit); frac = lit - full
    seg = rp[:full + 1]
    if frac > 0 and full + 1 < len(rp):
        a, b = rp[full], rp[full + 1]; seg = seg + [(lerp(a[0], b[0], frac), lerp(a[1], b[1], frac))]
    if heart > 0: seg = rp
    if len(seg) > 1:
        p = skia.Path(); p.moveTo(*seg[0]); [p.lineTo(*q) for q in seg[1:]]
        f.c.drawPath(p, f.stroke('#ffffff', 22)); f.c.drawPath(p, f.stroke('#ff5fa2' if heart > 0 else '#ff8a3a', 12))
    # cities
    for name, (lo, la) in CITY.items():
        x, y = map_xy(lo, la, cx, cy, sc)
        big = name in ('洛阳', '郑州')
        col = '#ff5f7e' if name == '洛阳' else ('#4a86d8' if name == '郑州' else '#ffffff')
        if heart > 0.5 and name not in ('洛阳', '郑州'): continue
        f.circle(x, y, 13 if big else 9, col, INK, 4)
        if labels:
            f.text(x + 16, y - 10, name, 34 if big else 28, INK, 'bold', outline='#ffffff', ow=6)
    if highlight:
        x, y = map_xy(*CITY[highlight], cx, cy, sc)
        k = 1 + 0.2 * math.sin(t * 8)
        f.circle(x, y, 30 * k, None, '#ff5f7e', 6)
    return rp


# ---------------------------------------------------------------- city landmark icons (for road signs)
def ic_buddha(f, x, y, s):         # 平顶山 中原大佛
    f.poly([(x - 30 * s, y + 40 * s), (x + 30 * s, y + 40 * s), (x + 22 * s, y), (x - 22 * s, y)], '#e0a030', INK, 3 * s)
    f.circle(x, y - 12 * s, 18 * s, '#f0c040', INK, 3 * s); f.circle(x, y - 34 * s, 8 * s, '#e0a030', INK, 3 * s)
def ic_tower(f, x, y, s):          # 许昌 曹魏城楼
    f.rect(x - 34 * s, y + 4 * s, 68 * s, 34 * s, '#c8a070', INK, 3 * s); f.rect(x - 10 * s, y + 18 * s, 20 * s, 20 * s, INK)
    f.poly([(x - 44 * s, y + 6 * s), (x, y - 28 * s), (x + 44 * s, y + 6 * s)], '#8a3a2a', INK, 3 * s)
    f.poly([(x - 30 * s, y - 16 * s), (x, y - 42 * s), (x + 30 * s, y - 16 * s)], '#8a3a2a', INK, 3 * s)
def ic_wall(f, x, y, s):           # 开封 城墙 + 小笼包
    f.rect(x - 44 * s, y - 14 * s, 88 * s, 40 * s, '#b08a6a', INK, 3 * s)
    for k in range(5): f.rect(x - 44 * s + k * 20 * s, y - 26 * s, 12 * s, 14 * s, '#b08a6a', INK, 2 * s)
    f.oval(x, y + 30 * s, 18 * s, 12 * s, '#fff4e0', INK, 3 * s)
def ic_mountain(f, x, y, s):       # 新乡 太行山
    f.poly([(x - 48 * s, y + 34 * s), (x - 12 * s, y - 30 * s), (x + 8 * s, y + 4 * s), (x + 22 * s, y - 14 * s), (x + 48 * s, y + 34 * s)], '#6aa060', INK, 3 * s)
    f.poly([(x - 20 * s, y - 16 * s), (x - 12 * s, y - 30 * s), (x - 4 * s, y - 16 * s)], '#ffffff', None)
def ic_fan(f, x, y, s):            # 南阳 羽扇
    f.blob([(x, y - 40 * s), (x + 30 * s, y - 20 * s), (x + 26 * s, y + 10 * s), (x, y + 18 * s), (x - 26 * s, y + 10 * s), (x - 30 * s, y - 20 * s)], '#f4f4f0', INK, 3 * s)
    f.rect(x - 4 * s, y + 16 * s, 8 * s, 24 * s, '#8a5a3a', INK, 2 * s)
def ic_bowls(f, x, y, s):          # 濮阳 杂技顶碗
    f.circle(x, y + 22 * s, 12 * s, P.SKIN, INK, 3 * s)
    for k in range(3): f.oval(x, y + 2 * s - k * 16 * s, 22 * s - k * 3 * s, 7 * s, '#4a86d8', INK, 3 * s)
def ic_oracle(f, x, y, s):         # 安阳 甲骨文
    f.blob([(x - 34 * s, y - 30 * s), (x + 30 * s, y - 34 * s), (x + 36 * s, y + 30 * s), (x - 30 * s, y + 34 * s)], '#e8dcc0', INK, 3 * s)
    f.text(x, y + 14 * s, '人', 40 * s, '#8a3a2a', 'black', 'center')
def ic_crane(f, x, y, s):          # 鹤壁 鹤
    f.blob([(x - 30 * s, y), (x, y - 14 * s), (x + 30 * s, y - 4 * s), (x + 4 * s, y + 10 * s)], '#ffffff', INK, 3 * s)
    f.line(x + 22 * s, y - 8 * s, x + 30 * s, y - 34 * s, INK, 3 * s); f.circle(x + 30 * s, y - 36 * s, 5 * s, '#ff4a5a')
    f.line(x - 4 * s, y + 8 * s, x - 10 * s, y + 36 * s, INK, 3 * s)
def ic_fall(f, x, y, s):           # 焦作 云台山瀑布
    f.poly([(x - 44 * s, y + 36 * s), (x - 30 * s, y - 36 * s), (x - 6 * s, y - 36 * s), (x - 8 * s, y + 36 * s)], '#6aa060', INK, 3 * s)
    f.poly([(x + 44 * s, y + 36 * s), (x + 30 * s, y - 36 * s), (x + 8 * s, y - 36 * s), (x + 8 * s, y + 36 * s)], '#6aa060', INK, 3 * s)
    f.rect(x - 7 * s, y - 36 * s, 14 * s, 72 * s, '#bfe8ff', INK, 2 * s)
def ic_dam(f, x, y, s):            # 三门峡 大坝 + 天鹅
    f.rect(x - 44 * s, y - 10 * s, 88 * s, 30 * s, '#c8c8d0', INK, 3 * s)
    f.rect(x - 44 * s, y + 20 * s, 88 * s, 16 * s, '#7ab8e0', None)
    f.oval(x + 10 * s, y - 24 * s, 14 * s, 8 * s, '#ffffff', INK, 2 * s); f.curve([(x + 20 * s, y - 26 * s), (x + 24 * s, y - 40 * s), (x + 30 * s, y - 40 * s)], INK, 3 * s)
def ic_horse(f, x, y, s):          # 驻马店 马
    f.oval(x - 4 * s, y, 30 * s, 16 * s, '#a0623a', INK, 3 * s)
    f.poly([(x + 18 * s, y - 6 * s), (x + 30 * s, y - 34 * s), (x + 42 * s, y - 28 * s), (x + 28 * s, y + 2 * s)], '#a0623a', INK, 3 * s)
    for k in (-20, -6, 10, 22): f.line(x + k * s, y + 12 * s, x + k * s, y + 36 * s, INK, 4 * s)
def ic_sausage(f, x, y, s):        # 漯河 火腿肠 + 辣条
    f.c.save(); f.c.translate(x, y); f.c.rotate(-25)
    f.rect(-40 * s, -10 * s, 80 * s, 20 * s, '#e8394f', INK, 3 * s, r=10 * s); f.c.restore()
    f.rect(x - 30 * s, y + 18 * s, 60 * s, 12 * s, '#c0392b', INK, 2 * s, r=4 * s)
def ic_laozi(f, x, y, s):          # 周口 老子骑青牛
    f.oval(x, y + 12 * s, 34 * s, 16 * s, '#4a8a7a', INK, 3 * s)
    f.circle(x + 30 * s, y + 4 * s, 10 * s, '#4a8a7a', INK, 3 * s)
    f.circle(x - 4 * s, y - 20 * s, 10 * s, P.SKIN, INK, 3 * s); f.rect(x - 12 * s, y - 12 * s, 16 * s, 18 * s, '#e8e0c8', INK, 2 * s)
    f.line(x - 10 * s, y - 14 * s, x - 16 * s, y - 2 * s, '#ffffff', 3 * s)
def ic_gate(f, x, y, s):           # 商丘 古城门
    f.rect(x - 44 * s, y - 14 * s, 88 * s, 50 * s, '#b08a6a', INK, 3 * s)
    p = skia.Path(); p.addArc(skia.Rect.MakeLTRB(x - 16 * s, y + 4 * s, x + 16 * s, y + 36 * s), 180, 180); p.lineTo(x + 16 * s, y + 36 * s); p.lineTo(x - 16 * s, y + 36 * s); p.close()
    f.path(p, INK, None)
    f.poly([(x - 40 * s, y - 14 * s), (x, y - 40 * s), (x + 40 * s, y - 14 * s)], '#8a3a2a', INK, 3 * s)

CITY_ICON = {'平顶山': ic_buddha, '许昌': ic_tower, '开封': ic_wall, '新乡': ic_mountain, '信阳': icon_tea, '南阳': ic_fan,
             '濮阳': ic_bowls, '安阳': ic_oracle, '鹤壁': ic_crane, '焦作': ic_fall, '三门峡': ic_dam, '驻马店': ic_horse,
             '漯河': ic_sausage, '周口': ic_laozi, '商丘': ic_gate}
CITY_KM = {'平顶山': 128, '许昌': 86, '开封': 72, '新乡': 79, '信阳': 310, '南阳': 268, '濮阳': 212, '安阳': 190, '鹤壁': 148,
           '焦作': 92, '三门峡': 236, '驻马店': 188, '漯河': 140, '周口': 172, '商丘': 196}


def highway_bg(f, t, hour='day'):
    if hour == 'day': f.vgrad(['#7ccfff', '#bfe8ff', '#fff3c8'], 0, 640)
    else: f.vgrad(['#ffb07a', '#ffd9a0', '#fff3c8'], 0, 640)
    for k in range(5):
        cloud(f, (200 + k * 420 - t * 60) % (W + 300) - 150, 140 + (k % 2) * 60, 0.7, '#ffffff', line=None, a=0.9)
    f.rect(0, 640, W, 440, '#8ac46a')
    f.poly([(900, 640), (1020, 640), (1760, H), (160, H)], '#4a4b62', None)
    off = (t * 900) % 120
    for k in range(8):
        yy = 660 + ((k * 120 + off) % 480) * (1 + ((k * 120 + off) % 480) / 480)
        if yy > H: continue
        wid = 6 + (yy - 640) / 18
        f.rect(960 - wid / 2, yy, wid, 10 + (yy - 640) / 10, '#ffffff')


def city_sign_shot(f, t, dur, city, hour='day', idx=0):
    """路牌镜头：路牌从远处冲到眼前；两人骑车从前景驶过。左右交替，天色随时间变暖。"""
    highway_bg(f, t, hour)
    side = -1 if idx % 2 else 1
    k = ease_out(t / max(dur, 0.01))
    s = lerp(0.75, 1.12, k)
    sx = 960 + side * lerp(260, 420, k)
    name = '  '.join(city) if len(city) == 2 else city
    road_sign(f, sx, lerp(420, 380, k), name, CITY_KM.get(city), CITY_ICON.get(city), s, t)
    # the two of them ride past in the foreground
    bx = lerp(-200 if side > 0 else W + 200, W / 2 + side * -380, ease(t / max(dur, 0.01)))
    from props import ebike
    import people as P
    ebike(f, bx, 1060, 0.7, t * 2, moving=True, back_rider=True, rider_expr='grin', back_expr='love')
