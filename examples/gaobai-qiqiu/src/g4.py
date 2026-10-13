"""第 4 章：导歌 2（37–43）+ 副歌 2（44–48）。"""
from gbl import *
from gbl import _DITH, _poly_mask
from tl import shot
import g1, g2


@shot(37)
def s37(t, D):
    cv = Canvas()
    sky_band(cv, SKY_DAY, 0, H)
    pan = int(ease(clamp(t / D)) * 60)
    # 台阶（9 级，数字 1→9）
    for i in range(9):
        x = 40 + i * 26; y = 170 - i * 16 + pan
        cv.rect(x, y, 30, 200, hexc('f0e2c8')); cv.rect(x, y, 30, 2, INK); cv.vline(x, y, H, INK)
        cv.text(x + 10, y + 3, str(i + 1), NAVY)
    SHE(cv, 40 + 8 * 26 + 18, 170 - 8 * 16 + pan, 24, 'stand', 'smile', t=t, facing=-1)
    lvl = min(7, int(t / 0.67))
    hop = abs(math.sin(t / 0.67 * math.pi)) * 4
    HE(cv, 40 + lvl * 26 + 14, 170 - lvl * 16 + pan - hop, 24, 'jump' if hop > 2 else 'stand', 'happy', t=t, facing=1)
    sub = cv.a[4:20, 6:70].astype(np.int16); cv.a[4:20, 6:70] = (sub * 0.3 + np.array(WHITE) * 0.7).astype(np.uint8)
    cv.text(8, 5, '难度', NAVY); g2.stars(cv, 40, 12, 3, 3)
    return cv


@shot(38)
def s38(t, D):
    cv = Canvas()
    sky_band(cv, SKY_DAY, 0, H)
    cv.rect(0, 140, W, 40, hexc('f0e2c8')); cv.hline(0, W, 140, INK)
    back = ease(clamp(t / 0.4)) * 14
    f = SHE(cv, 200 + back, 140, 34, 'reach', 'smile' if t < 1.2 else 'joy', t=t, facing=-1)
    hx, hy = f['hands'][1]
    cv.rect(hx - 14, hy - 30, 30, 28, INK); cv.rect(hx - 13, hy - 29, 28, 26, WHITE)
    big_text(cv, hx + 1, hy - 16, '退', BAL_D, size=16, outline=WHITE)
    HE(cv, 120, 140, 34, 'cheer', 'joy', t=t, facing=1)
    if t > 1.2: big_text(cv, f['cx'] - 24, f['top'] - 6, '噗', NAVY, size=12, outline=WHITE)
    return cv


@shot(39)
def s39(t, D):
    cv = Canvas()
    g2.boulevard(cv, t, autumn=True)
    leaves(cv, t, n=90, speed=26)
    jump = abs(math.sin(clamp(t / 1.2) * math.pi)) * 18
    f = HE(cv, 160, 160 - jump, 34, 'point_up' if jump > 2 else 'stand', 'happy', t=t)
    hx, hy = f['hands'][1]
    lx, ly = (hx, hy - 4) if t > 0.6 else (hx + 20 - t * 30, hy - 40 + t * 50)
    cv.poly([(lx - 8, ly), (lx, ly - 9), (lx + 8, ly), (lx, ly + 8)], hexc('ffc84a'))
    cv.line(lx, ly - 8, lx, ly + 10, hexc('a06a2a'))
    if t > 0.7: symbol(cv, 'sparkle', lx + 10, ly - 8, t)
    return cv


@shot(40)
def s40(t, D):
    cv = Canvas(hexc('c8a888'))
    close = ease(clamp((t - 1.6) / 0.6))
    cv.rect(50, 20, 220, 140, INK)
    lw = int(110 * (1 - close))
    cv.rect(51 + (110 - lw), 21, lw, 138, hexc('fffaf0')); cv.rect(161, 21, 108, 138, hexc('fffaf0'))
    for y in range(36, 156, 12):
        cv.hline(170, 260, y, hexc('d8e0f0'))
        if lw > 10: cv.hline(60 + (110 - lw), 150, y, hexc('d8e0f0'))
    if close < 0.9:
        lx, ly = 105, 88
        cv.poly([(lx - 18, ly), (lx, ly - 22), (lx + 18, ly), (lx, ly + 18)], hexc('ffc84a'))
        cv.line(lx, ly - 20, lx, ly + 26, hexc('a06a2a'))
        for k in range(4): cv.line(lx, ly - 10 + k * 8, lx - 10 + k * 2, ly - 16 + k * 8, hexc('e0a030'))
    if t > 0.8: heart_px(cv, 220, 120, 2, BAL)
    cv.vline(160, 20, 160, INK)
    return cv


def meadow(cv, t, sky=SKY_DAY):
    sky_band(cv, sky, 0, 100)
    eiffel(cv, 250, 98, 80, hexc('9a8a9a'))
    paris_row(cv, 100, seed=9, hmin=20, hmax=36)
    cv.rect(0, 100, W, 80, hexc('8ad07a')); cv.hline(0, W, 100, INK)
    r = rng(4)
    for i in range(60): cv.px(r.uniform(0, W), r.uniform(104, H), hexc('6aba5a'))


@shot(41)
def s41(t, D):
    cv = Canvas()
    meadow(cv, t)
    # 格子布
    for j in range(5):
        for i in range(10):
            cv.rect(100 + i * 12, 130 + j * 6, 12, 6, hexc('e86a6a') if (i + j) % 2 else WHITE)
    cv.rect(160, 118, 20, 14, hexc('b88a5a'), ); cv.rect(160, 118, 20, 2, INK)
    balloon(cv, 172, 86, 1.1, t, str_len=28)
    cv.rect(124, 128, 12, 6, hexc('f4d8a0')); cv.rect(126, 129, 8, 2, hexc('8ad07a'))
    HE(cv, 110, 150, 26, 'sit', 'happy', t=t, facing=1)
    SHE(cv, 200, 150, 26, 'sit', 'joy', t=t, facing=-1)
    for i in range(2):
        x = (t * 20 + i * 150) % W; cv.ellipse(x, 30 + i * 12, 16, 5, WHITE)
    return cv


@shot(42)
def s42(t, D):
    cv = Canvas()
    meadow(cv, t, sky=SKY_RAIN)
    cv.tint(hexc('8a98b0'), 0.15)
    for j in range(5):
        for i in range(10):
            cv.rect(100 + i * 12, 150 + j * 5, 12, 5, hexc('c86a6a') if (i + j) % 2 else hexc('e8e8e8'))
    HE(cv, 150, 150, 34, 'cheer', 'joy', t=t, facing=1)
    SHE(cv, 176, 150, 30, 'clap', 'joy', t=t, facing=-1)
    # 外套撑在两人头上
    cv.poly([(124, 90), (200, 84), (206, 96), (128, 102)], hexc('aad2f0'))
    cv.line(124, 90, 200, 84, INK); cv.line(128, 102, 206, 96, INK)
    rain(cv, t, n=160, seed=42, speed=160, col=hexc('e0e8f4'), excl=lambda x, y: 124 < x < 206 and y > 92, y_ground=176)
    return cv


@shot(43)
def s43(t, D):
    cv = Canvas(hexc('2a2e5a'))
    r = rng(43)
    for i in range(40): cv.px(r.uniform(0, W), r.uniform(0, H), hexc('6a6aa0'))
    # 双手捧水晶球
    cx, cy, R = 160, 80, 56
    cv.ellipse(cx, cy, R, R, hexc('cfe8f8'), INK)
    sky_band_sub = Canvas(KEY)
    sky_band(sky_band_sub, [hexc('8ab8e0'), hexc('d8ecf8')], 0, H)
    eiffel(sky_band_sub, cx + 20, cy + 40, 60, hexc('8a7a8a'))
    sky_band_sub.rect(0, cy + 40, W, 40, WHITE)
    HE(sky_band_sub, cx - 16, cy + 42, 16, 'stand', 'joy', t=t)
    SHE(sky_band_sub, cx - 2, cy + 42, 16, 'stand', 'joy', t=t)
    snow(sky_band_sub, t, n=80, speed=12, col=WHITE)
    yy, xx = np.mgrid[0:H, 0:W]
    m = ((xx - cx) ** 2 + (yy - cy) ** 2) < (R - 2) ** 2
    cv.a[m] = sky_band_sub.a[m]
    cv.ellipse(cx - R * 0.5, cy - R * 0.5, 8, 5, WHITE)
    cv.poly([(cx - 40, cy + R - 4), (cx + 40, cy + R - 4), (cx + 50, cy + R + 18), (cx - 50, cy + R + 18)], hexc('b07a4a'))
    mitt(cv, cx - 70, cy + 62, 1, hexc('ffb0be'), (-20, 200))
    mitt(cv, cx + 70, cy + 62, -1, hexc('ffb0be'), (W + 20, 200))
    return cv


# ---------------------------------------------------------------- 副歌 2
POLA = ['cafe', 'leaf', 'balloon', 'rain', 'planet', 'tower', 'cake', 'globe']


def polaroid(cv, x, y, kind, t):
    cv.rect(x - 1, y - 1, 46, 52, INK); cv.rect(x, y, 44, 50, WHITE)
    cv.rect(x + 3, y + 3, 38, 36, hexc('c8e0ec'))
    cx, cy = x + 22, y + 21
    if kind == 'cafe': cup(cv, cx, cy - 2, 2, lip=True)
    elif kind == 'leaf':
        cv.poly([(cx - 8, cy), (cx, cy - 10), (cx + 8, cy), (cx, cy + 8)], hexc('ffc84a'))
    elif kind == 'balloon': balloon(cv, cx, cy - 4, 1.0, t, face_=True, str_len=8)
    elif kind == 'rain':
        for i in range(10): cv.vline(x + 5 + i * 4, y + 6 + (i * 5) % 10, y + 10 + (i * 5) % 10, hexc('6a8ab0'))
        cv.poly([(cx - 12, cy), (cx + 12, cy - 2), (cx + 12, cy + 3), (cx - 12, cy + 5)], hexc('aad2f0'))
    elif kind == 'planet': cv.ellipse(cx, cy + 8, 14, 10, hexc('8ad07a'), INK)
    elif kind == 'tower': eiffel(cv, cx, cy + 16, 30, hexc('8a7a8a'))
    elif kind == 'cake': cv.rect(cx - 8, cy - 2, 16, 10, hexc('fff4e0')); cv.rect(cx - 8, cy - 4, 16, 3, hexc('ff9ab0'))
    else: cv.ellipse(cx, cy, 12, 12, hexc('e8f4ff'), INK)


@shot(44)
def s44(t, D):
    cv = Canvas(hexc('f0e2c8'))
    for x in range(0, W, 24): cv.vline(x, 0, H, hexc('e8d8bc'))
    cv.hline(0, W, 18, hexc('8a6a50')); cv.hline(0, W, 92, hexc('8a6a50'))
    beat = 0.673
    n = min(len(POLA), int(t / beat) + 1)
    for i in range(n):
        x = 14 + (i % 4) * 76; y = 24 + (i // 4) * 76
        k = ease(clamp((t - i * beat) / 0.25))
        if k > 0.1:
            polaroid(cv, x, int(y - (1 - k) * 10), POLA[i], t)
            cv.rect(x + 18, y - 4, 8, 6, hexc('ffd35a'))
    return cv


@shot(45)
def s45(t, D):
    cv = Canvas()
    g2.boulevard(cv, t)
    k = ease(clamp(t / 1.4))
    HE(cv, int(lerp(90, 128, k)), 166, 34, 'stand', 'happy', t=t, facing=1)
    SHE(cv, int(lerp(230, 192, k)), 166, 34, 'stand', 'joy', t=t, facing=-1)
    cv.vline(160, 70, 116, hexc('d8c8a0'))
    for i in range(14):
        a = i * 0.45
        cv.ellipse(160 + math.cos(a) * 10, 62 + math.sin(a) * 8, 7, 6, hexc('ffb8d0'))
    cv.ellipse(160, 62, 12, 10, hexc('ffc8dc'))
    if k >= 1: symbol(cv, 'heart', 160, 40, t)
    return cv


@shot(46)
def s46(t, D):
    cv = Canvas()
    g1.street_scene(cv, t)
    f = SHE(cv, 200, GROUND, 32, 'hand_chest', dict(eyes='closed', mouth='flat', blush=True), t=t, facing=1)
    cv.ellipse(f['cx'] - 6, f['top'] + 26, 4, 3, hexc('ffb0b8')); cv.ellipse(f['cx'] + 8, f['top'] + 26, 4, 3, hexc('ffb0b8'))
    funny = int(t * 3) % 3
    exs = [dict(eyes='squeeze', mouth='open'), dict(eyes='wide', mouth='o'), dict(eyes='happy', mouth='wobble')]
    HE(cv, 150, GROUND, 26, 'sit', exs[funny], t=t, facing=1)
    if t > 1.6: big_text(cv, f['cx'] + 22, f['top'] - 6, '噗', NAVY, size=12, outline=WHITE)
    return cv


@shot(47)
def s47(t, D):
    cv = Canvas()
    g2.eyes_close(cv, t, look=0, heart=t > 0.6)
    if t > 0.6:
        k = clamp((t - 0.6) / 0.4)
        for x0 in (92, 232):
            for a in range(0, 360, 30):
                cv.px(x0 + math.cos(math.radians(a)) * (40 + k * 16), 100 + math.sin(math.radians(a)) * (32 + k * 12), BAL_H)
    return cv


@shot(48)
def s48(t, D):
    cv = Canvas()
    off = int(t * 12)
    g2.boulevard(cv, t + off)
    x = 140 + int(t * 6)
    HE(cv, x, 162, 32, 'walk', 'shy', t=t, facing=1)
    SHE(cv, x + 34, 162, 32, 'walk', 'joy', t=t + 0.05, facing=1)
    cv.rect(x + 14, 134, 8, 3, PAL['skin'])
    balloon(cv, x + 54, 96, 1.2, t, str_len=40)
    symbol(cv, 'heart', x + 17, 100, t)
    return cv
