"""《蝴蝶》全片共用：调色模式、场景、角色便捷函数、小道具。"""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from px import *
from hd import *
from hd import _DITH, _poly_mask
from chars import head, symbol, char
from ui import mitt, confetti

GROUND = 150
SAFE_Y = 152          # 有人声时，画布 y>152 不放文字/关键道具（1080p 底部 170px）
WHITE = PAL['white']
SIGN_RED = hexc('c8283a')


# ================================================================ 调色
def sat(cv, k, ramp=GRAY_RAMP, keep=None):
    """k=0 全灰，1 全彩；中间用有序抖动混合（像素感）。蓝蝴蝶永远彩色。"""
    if k >= 1 and keep is None: return cv
    g = to_ramp(cv.a, ramp).astype(np.uint8)
    m = _DITH < k
    m |= is_blue(cv.a)
    if keep is not None: m |= keep
    cv.a = np.where(m[..., None], cv.a, g)
    return cv


def warm(cv, k=0.18, col=hexc('ff9e6b')):
    cv.a = (cv.a.astype(np.float32) * (1 - k) + np.array(col, np.float32) * k).astype(np.uint8)


def flash(cv, k, col=(255, 255, 255)):
    if k <= 0: return
    m = _DITH < k
    cv.a[m] = col


def fade_black(cv, k):
    if k <= 0: return
    cv.a[_DITH < k] = (8, 8, 12)


# ================================================================ 角色便捷函数
def WU(cv, cx, feet, Hh, pose='stand', expr='normal', t=0.0, facing=0, alpha=1.0, keep=None, apron=False, back=False, hold=None):
    L = Layer(); f = wu(L, cx, feet, Hh, pose, expr, t, facing, back, apron, hold)
    if alpha >= 1 and keep is None: solid(cv, L)
    else: ghost(cv, L, alpha, keep=keep, t=t, dotted=alpha < 1)
    return f


def DIE(cv, cx, feet, Hh, pose='stand', expr='normal', t=0.0, facing=0, back=False, hold=None):
    return die(cv, cx, feet, Hh, pose, expr, t, facing, back, hold)


def npc(cv, who, cx, feet, Hh, t, phone=True, facing=0, pose='walk'):
    f = char(cv, who, cx, feet, Hh, pose, 'stunned', t, facing)
    if phone:
        hx, hy = f['hands'][1]
        cv.rect(hx - 2, hy - 4, 3, 5, INK); cv.px(hx - 1, hy - 3, hexc('a8c8e8'))
    return f


def bigface(cv, who, cx, top, Hh, expr, t=0.0, body_col=None):
    """近景 / 特写：头 + 肩膀"""
    bc = body_col or (hexc('969aa6') if who == 'wu' else CREAM)
    cv.ellipse(cx, top + Hh * 1.6, Hh * 0.95, Hh * 0.62, bc, INK)
    f = head(cv, who, cx, top, Hh, expr, t=t)
    if who == 'wu': bandaid(cv, int(cx - f['Wh'] * 0.28), top + int(Hh * 0.74), 2)
    else: clip(cv, int(cx + f['Wh'] * 0.30), top + int(Hh * 0.22), Hh, t)
    return f


def wu_tufts(cv, f, Hh):
    Wh = f['Wh']; tp = f['top']; k = max(1, Hh // 12)
    for dx, h_ in ((-0.18, 2), (0.05, 3), (0.26, 2)):
        xx = int(f['cx'] + dx * Wh)
        for j in range(h_ * k):
            cv.rect(xx - 1 + (j // k) * (1 if dx > 0 else -1), tp - 2 - j, k + 2, 1, INK)
            cv.rect(xx + (j // k) * (1 if dx > 0 else -1), tp - 2 - j, k, 1, PAL['hair'])


# ================================================================ 文字小件
FONT_S = ImageFont.truetype(ZH_MONO, 12)


def label(cv, x, y, s, fg=INK, bg=hexc('f0ead8'), pad=2, font=None):
    font = font or FONT12
    w = cv.text_w(s, font)
    cv.rect(x - pad - 1, y - pad - 1, w + 2 * pad + 2, 12 + 2 * pad + 2, INK)
    cv.rect(x - pad, y - pad, w + 2 * pad, 12 + 2 * pad, bg)
    cv.text(x, y - 1, s, fg, font=font)
    return w


def bubble(cv, x, y, s, fg=INK, bg=WHITE, right=False):
    w = cv.text_w(s) + 8
    x0 = x - w if right else x
    cv.rrect(x0, y, w, 16, 4, bg, INK)
    cv.text(x0 + 4, y + 1, s, fg)
    tx = x0 + w - 8 if right else x0 + 6
    cv.poly([(tx, y + 15), (tx + 4, y + 15), (tx + (6 if right else -2), y + 20)], bg)
    return w


def stamp(cv, cx, cy, s, k=1.0, col=SIGN_RED, size=28):
    if k <= 0: return
    f = ImageFont.truetype(ZH_FONT, size)
    m = Canvas(KEY)
    w = int(f.getlength(s)) + 12; h = size + 10
    m.rect(cx - w // 2, cy - h // 2, w, h, col); m.rect(cx - w // 2 + 2, cy - h // 2 + 2, w - 4, h - 4, KEY)
    m.text(cx, cy, s, col, font=f, anchor='mm')
    mm = np.any(m.a != np.array(KEY, np.uint8), axis=2)
    if k < 1: mm &= _DITH < k
    cv.a[mm] = col


def big_text(cv, x, y, s, col, size=16, outline=INK, anchor='mm'):
    f = ImageFont.truetype(ZH_FONT, size)
    cv.text(x, y, s, col, font=f, outline=outline, anchor=anchor)


# ================================================================ 场景
def street(cv, t, ground=132, seed=2, lamp_x=206, lit=0.12):
    sky_band(cv, [hexc('141824'), hexc('1e2432'), hexc('2c3444')], 0, ground)
    buildings(cv, ground, seed=seed, cols=((40, 46, 58), (50, 56, 70)), win=(150, 140, 110), lit=lit, minh=60, maxh=128)
    wires_line(cv, 30, hexc('101218'), 8); wires_line(cv, 40, hexc('101218'), 5)
    cv.rect(0, ground, W, H - ground, hexc('3a3c44')); cv.hline(0, W, ground, INK)
    cv.rect(0, ground + 18, W, 2, hexc('4a4c54'))
    if lamp_x is not None:
        cv.rect(lamp_x, 40, 3, ground - 40, hexc('2a2c34')); cv.rect(lamp_x - 10, 38, 16, 4, hexc('2a2c34')); cv.rect(lamp_x - 10, 42, 6, 2, hexc('f0e8c8'))
        for y in range(44, ground + 18):
            w = (y - 44) * 0.45
            for x in range(max(0, int(lamp_x - 7 - w)), min(W, int(lamp_x - 7 + w))):
                if _DITH[y, x] < 0.22: cv.px(x, y, mix(tuple(cv.a[y, x]), (230, 225, 200), 0.35))


def ruins(cv, t, sky=None, sign=True, cleared=0.0, ground=118):
    sky_band(cv, sky or [hexc('6a6e84'), hexc('8a8aa0'), hexc('b0a8b0'), hexc('c8b8b0')], 0, ground + 2)
    buildings(cv, ground, seed=13, cols=((96, 98, 112), (106, 108, 122)), win=(140, 140, 150), lit=0.1, minh=30, maxh=70, laundry=False)
    cv.rect(0, ground, W, H - ground, hexc('7a7072'))
    broken_wall(cv, 10, 140, 70, 60, col=(150, 132, 124), seed=5)
    broken_wall(cv, 230, 136, 60, 44, col=(140, 124, 118), seed=9)
    if cleared < 1:
        bricks(cv, 70, 120 + int(cleared * 20), 120, int(30 * (1 - cleared)) + 1, seed=3)
        bricks(cv, 180, 128 + int(cleared * 20), 90, int(26 * (1 - cleared)) + 1, seed=6)
    bricks(cv, -10, 150, 120, 30, seed=7, col=(110, 96, 94))
    if sign:
        cv.poly([(112, 130), (176, 124), (178, 136), (114, 142)], APRON_D)
        cv.text(120, 126, '小伍花店', hexc('c8d8b8'))


def room(cv, t, rain_on=True, light=0.0, mess=True):
    """他的出租屋（侧面）：左门、窗、床、书桌。"""
    cv.rect(0, 0, W, 140, hexc('8a7f74'))
    for x in range(0, W, 24): cv.vline(x, 0, 140, hexc('827769'))
    cv.rect(0, 140, W, H - 140, hexc('6a5a4c')); cv.hline(0, W, 140, INK)
    for x in range(0, W, 30): cv.vline(x, 141, H, hexc('5e5044'))
    # 窗
    wx, wy, ww, wh = 150, 24, 70, 54
    cv.rect(wx - 2, wy - 2, ww + 4, wh + 4, INK); cv.rect(wx, wy, ww, wh, hexc('2a3244') if light < 0.5 else hexc('a8d0f0'))
    if rain_on:
        rain(cv, t, n=40, seed=31, speed=110, col=hexc('5a6a84'), rect=(wx, wy, wx + ww, wy + wh), splash=False)
    cv.rect(wx + ww // 2, wy, 2, wh, INK); cv.rect(wx, wy + wh // 2, ww, 2, INK)
    cv.rect(wx - 6, wy - 6, 14, wh + 14, hexc('b0a090')); cv.rect(wx + ww - 8, wy - 6, 14, wh + 14, hexc('b0a090'))  # 窗帘
    # 门
    cv.rect(14, 40, 40, 100, INK); cv.rect(16, 42, 36, 98, hexc('6a5248')); cv.rect(44, 90, 3, 5, hexc('c0b080'))
    # 床
    cv.rect(220, 112, 96, 28, INK); cv.rect(222, 114, 92, 20, hexc('c8c0b8')); cv.rect(222, 108, 22, 10, hexc('e8e0d8'))
    cv.rect(222, 134, 92, 6, hexc('6a5040'))
    # 书桌 + 台灯
    cv.rect(66, 104, 60, 4, INK); cv.rect(67, 105, 58, 2, hexc('9a7a5a')); cv.rect(70, 108, 3, 32, INK); cv.rect(118, 108, 3, 32, INK)
    cv.rect(108, 92, 2, 12, INK); cv.rect(102, 88, 12, 5, hexc('d8c070'))
    # 墙上：花店开业照、日历
    cv.rect(80, 40, 30, 22, INK); cv.rect(81, 41, 28, 20, hexc('d8d0c0')); cv.rect(84, 44, 22, 12, hexc('5a9a6a'))
    if mess:
        for i, (x, y) in enumerate([(84, 144), (128, 150), (160, 146), (196, 156)]):
            cv.rect(x, y, 12, 8, INK); cv.rect(x + 1, y + 1, 10, 6, hexc('e8e2d4')); cv.hline(x + 2, x + 8, y + 3, hexc('b0a898'))
        cv.rect(180, 130, 14, 10, hexc('a07a50')); cv.rect(182, 126, 3, 4, hexc('d0c8b0'))  # 泡面碗


def alley(cv, t, ground=150, seed=41, wet=True):
    sky_band(cv, [hexc('7a8494'), hexc('9aa4b4')], 0, 40)
    r = rng(seed)
    x = 0
    cols = [hexc('b8a890'), hexc('a89a88'), hexc('c4b8a4'), hexc('9a9488')]
    while x < W:
        w = int(r.integers(50, 80)); c = cols[int(r.integers(0, 4))]
        cv.rect(x, 18, w, ground - 18, c); cv.vline(x, 18, ground, mix(c, INK, 0.4))
        for wy in (34, 70, 106):
            cv.rect(x + 10, wy, 16, 20, INK); cv.rect(x + 11, wy + 1, 14, 18, hexc('3a4250'))
            cv.rect(x + 9, wy + 20, 18, 2, mix(c, INK, 0.3))
            if r.random() < 0.5:
                cv.rect(x + w - 24, wy + 4, 14, 10, INK); cv.rect(x + w - 23, wy + 5, 12, 8, hexc('d8d8d0'))  # 空调外机
                cv.rect(x + w - 21, wy + 7, 8, 1, hexc('a0a0a0'))
        if r.random() < 0.6:
            sy = int(r.integers(56, 96)); cv.rect(x + 30, sy, 18, 8, SIGN_RED); cv.rect(x + 31, sy + 1, 16, 6, hexc('e8d8b0'))
        x += w
    cv.hline(0, W, 60, hexc('4a4a50')); cv.hline(0, W, 62, hexc('4a4a50'))
    for i in range(6):
        cx = 20 + i * 52 + int(math.sin(t * 2 + i) * 1)
        cv.rect(cx, 61, 10, 12, INK); cv.rect(cx + 1, 62, 8, 10, [hexc('d86a6a'), hexc('6a9ad8'), hexc('e8d86a'), hexc('f0f0f0')][i % 4])
    cv.rect(0, ground, W, H - ground, hexc('6a6a6e')); cv.hline(0, W, ground, INK)
    if wet:
        puddle(cv, 90, 162, 20, hexc('8a8e9a'), t); puddle(cv, 250, 168, 16, hexc('8a8e9a'), t + 0.4)


def rooftop(cv, t, sky, city_cols=((90, 98, 116), (104, 112, 130)), win=(200, 190, 150), ground=128):
    sky_band(cv, sky, 0, ground)
    buildings(cv, ground, seed=17, cols=city_cols, win=win, lit=0.2, minh=20, maxh=70, wmin=14, wmax=30)
    cv.rect(0, ground, W, H - ground, hexc('8a8a8e')); cv.hline(0, W, ground, INK)
    cv.rect(0, ground - 8, W, 3, hexc('6a6a70'));
    for x in range(0, W, 12): cv.rect(x, ground - 8, 2, 8, hexc('6a6a70'))
    cv.rect(16, 86, 30, 34, INK); cv.rect(17, 87, 28, 32, hexc('b0b4bc')); cv.rect(14, 84, 34, 4, INK)   # 水箱
    cv.rect(24, 120, 3, 8, INK); cv.rect(36, 120, 3, 8, INK)


def flower_shop(cv, t, sx=90, sw=140, top=52, ground=120, night=0.0):
    cv.rect(sx - 1, top - 1, sw + 2, ground - top + 1, INK); cv.rect(sx, top, sw, ground - top, hexc('f4ead8'))
    cv.rect(sx - 6, top - 12, sw + 12, 14, INK); cv.rect(sx - 5, top - 11, sw + 10, 12, APRON)
    title_text(cv, '小伍花店', sx + sw // 2, top - 5, hexc('fff6e0'), size=12, outline=APRON_D)
    for i in range(sw // 15 + 1):
        cv.rect(sx - 4 + i * 15, top + 1, min(15, sx + sw + 4 - (sx - 4 + i * 15)), 8, WHITE if i % 2 else APRON)
    win_c = hexc('cfe8f0') if night < 0.5 else hexc('ffe08a')
    cv.rect(sx + sw // 2 - 18, top + 24, 36, ground - top - 24, hexc('8a6a50')); cv.rect(sx + sw // 2 - 14, top + 28, 28, 30, win_c)
    for side in (sx + 8, sx + sw - 42):
        cv.rect(side, top + 26, 34, 28, win_c); cv.rect(side, top + 26, 34, 1, INK)
        if night >= 0.5:
            for j in range(4): cv.ellipse(side + 6 + j * 8, top + 48, 3, 3, hexc('ff8aa8') if j % 2 else hexc('ffd35a'))
    r = rng(4)
    for i in range(12):
        x = sx - 28 + i * 13 if i < 3 else sx + sw - 14 + (i - 3) * 9
        if x > W - 6 or (sx + 4 < x < sx + sw - 12): continue
        cv.rect(x, ground - 12, 10, 12, hexc('6a7a8a'))
        for j in range(5):
            cv.ellipse(x + r.integers(1, 9), ground - 16 + r.integers(-3, 3), 2.5, 2.5, hexc(['ff6a8a', 'ffd35a', 'ff9a4a', 'f6f2e6', 'c87aff'][int(r.integers(0, 5))]))


def flower_tree(cv, tx, ground, size=1.0, seed=4, bloom=1.0):
    r = rng(seed)
    cv.rect(tx - 2, ground - 40 * size, 4, 40 * size, hexc('7a5a3a'))
    cy = ground - 48 * size
    for j in range(40):
        a = r.uniform(0, 6.28); rr = r.uniform(0, 18 * size)
        cv.ellipse(tx + math.cos(a) * rr, cy + math.sin(a) * rr * 0.8, 4 * size, 4 * size, hexc('6aba5a') if j % 3 else hexc('4a9a4a'))
    for j in range(int(16 * bloom)):
        a = r.uniform(0, 6.28); rr = r.uniform(0, 18 * size)
        cv.ellipse(tx + math.cos(a) * rr, cy + math.sin(a) * rr * 0.8, 1.6, 1.6, hexc('ff8aa8'))
    cv.rect(tx - 9, ground - 10, 18, 10, hexc('b86a4a'))


def seedling(cv, x, ground, s=1, t=0.0, cocoon=True, droop=0.0, crack=0.0):
    """破花盆里的小苗（叶子下挂着茧）。s 放大倍数（整数）"""
    pw, ph = 14 * s, 10 * s
    cv.poly([(x - pw // 2, ground - ph), (x + pw // 2, ground - ph), (x + pw // 2 - 2 * s, ground), (x - pw // 2 + 2 * s, ground)], hexc('b86a4a'))
    cv.line(x - pw // 2 + 3 * s, ground - ph, x - pw // 2 + 5 * s, ground - ph + 4 * s, INK)  # 裂纹
    cv.rect(x - pw // 2, ground - ph - s, pw, 2 * s, hexc('5a4030'))
    sh = 18 * s
    cv.rect(x, ground - ph - sh, s, sh, hexc('5a9a4a'))
    d = int(droop * 4 * s)
    lx, ly = x + s, ground - ph - sh + 4 * s
    cv.ellipse(lx + 5 * s, ly + d, 6 * s, 2.5 * s, hexc('6aba5a'), INK)
    cv.ellipse(x - 5 * s, ground - ph - sh + 9 * s + d // 2, 5 * s, 2.2 * s, hexc('6aba5a'), INK)
    if cocoon:
        cx, cy = lx + 7 * s, ly + d + 5 * s
        cv.line(cx, ly + d + 1, cx, cy - 2 * s, hexc('d8d0c0'))
        cv.ellipse(cx, cy, 2 * s, 3.5 * s, hexc('c8b890'), INK)
        cv.rect(cx - s, cy - s, s, s, hexc('e0d4b0'))
        if crack > 0:
            cv.line(cx - 2 * s, cy - 2 * s, cx + s, cy, INK)
            if crack > 0.5: cv.ellipse(cx, cy, 1.5 * s, 2.5 * s, BLUE)
    return (lx + 7 * s, ly + d + 5 * s)


def cardboard(cv, bx, by, w=42, h=34, text='遗弃', flat=0.0):
    if flat > 0:
        h2 = max(4, int(h * (1 - flat))); by = by + h - h2; h = h2
    cv.rect(bx - 1, by - 1, w + 2, h + 2, INK); cv.rect(bx, by, w, h, hexc('b0906a'))
    cv.rect(bx, by, w, min(4, h), hexc('8a6e50'))
    if flat == 0:
        cv.poly([(bx, by), (bx - 8, by - 9), (bx + 14, by - 6), (bx + 14, by)], hexc('9a7c5a'))
        cv.poly([(bx + w, by), (bx + w + 8, by - 8), (bx + w - 12, by - 6), (bx + w - 12, by)], hexc('9a7c5a'))
    if text and h > 16:
        tw = cv.text_w(text) + 6
        cv.rect(bx + (w - tw) // 2, by + h // 2 - 7, tw, 14, hexc('e8e0d0')); cv.text(bx + (w - tw) // 2 + 3, by + h // 2 - 7, text, SIGN_RED)


def phone(cv, x, y, w=60, h=104, screen=hexc('e8eef6')):
    cv.rrect(x, y, w, h, 6, hexc('2a2a30'), INK); cv.rect(x + 4, y + 10, w - 8, h - 20, screen)
    cv.rect(x + w // 2 - 6, y + 4, 12, 2, hexc('4a4a50'))


def eyes_only(cv, cx, cy, t, wet=False):
    for sg in (-1, 1):
        ex = cx + sg * 10
        cv.rect(ex - 3, cy - 4, 7, 9, INK); cv.rect(ex - 2, cy - 3, 5, 7, hexc('5a3a2a'))
        cv.rect(ex - 1, cy - 2, 2, 2, WHITE)
        if wet: cv.rect(ex - 2, cy + 3, 5, 1, PAL['tear'])
        if (t % 2.7) < 0.12: cv.rect(ex - 3, cy - 4, 7, 9, hexc('e0d4b0')); cv.hline(ex - 3, ex + 3, cy + 1, INK)


def snow(cv, t, n=120, seed=8, speed=18, col=(240, 244, 250)):
    r = rng(seed)
    x0 = r.uniform(0, W, n); y0 = r.uniform(0, H, n); sp = r.uniform(0.6, 1.4, n)
    for i in range(n):
        y = (y0[i] + t * speed * sp[i]) % H; x = (x0[i] + math.sin(t * 1.5 + i) * 3) % W
        cv.px(x, y, col)
        if i % 4 == 0: cv.px(x + 1, y, col)


def scarf_between(cv, a, b, col=hexc('e8344a')):
    """两个人之间的长围巾"""
    for i in range(0, 101, 4):
        u = i / 100
        x = lerp(a[0], b[0], u); y = lerp(a[1], b[1], u) + math.sin(u * math.pi) * 4
        cv.rect(x - 1, y - 1, 4, 4, INK)
    for i in range(0, 101, 2):
        u = i / 100
        x = lerp(a[0], b[0], u); y = lerp(a[1], b[1], u) + math.sin(u * math.pi) * 4
        cv.rect(x, y, 2, 2, col)


def heart_bubble(cv, x, y, r, col=hexc('e8f4ff')):
    cv.ellipse(x - r * 0.5, y, r * 0.6, r * 0.6, col, INK)
    cv.ellipse(x + r * 0.5, y, r * 0.6, r * 0.6, col, INK)
    cv.poly([(x - r * 1.05, y + r * 0.2), (x + r * 1.05, y + r * 0.2), (x, y + r * 1.2)], col)
    cv.ellipse(x - r * 0.5, y, r * 0.6 - 1, r * 0.6 - 1, col); cv.ellipse(x + r * 0.5, y, r * 0.6 - 1, r * 0.6 - 1, col)
    cv.px(x - r * 0.6, y - r * 0.3, WHITE); cv.px(x - r * 0.5, y - r * 0.35, WHITE)
