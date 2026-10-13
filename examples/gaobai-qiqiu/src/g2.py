"""第 2 章：导歌 1（12–18）+ 副歌 1（19–24）。"""
from gbl import *
from gbl import _DITH, _poly_mask
from tl import shot
import g1


def boulevard(cv, t, autumn=False, sky=SKY_DAY):
    sky_band(cv, sky, 0, 120)
    eiffel(cv, 270, 112, 70, hexc('a898a8'))
    paris_row(cv, 118, seed=31, hmin=40, hmax=60)
    cv.rect(0, 118, W, 22, hexc('e8dcc4')); cv.hline(0, W, 118, INK)
    trees_row(cv, 140, t, autumn=autumn, n=5)
    ground_band(cv, 140, hexc('d8c8a8'))


def stars(cv, x, y, n, lit):
    for i in range(n):
        c = GOLD if i < lit else hexc('8a8aa0')
        cx = x + i * 10
        cv.poly([(cx, y - 4), (cx + 1, y - 1), (cx + 4, y - 1), (cx + 2, y + 1), (cx + 3, y + 4), (cx, y + 2), (cx - 3, y + 4), (cx - 2, y + 1), (cx - 4, y - 1), (cx - 1, y - 1)], c)


@shot(12)
def s12(t, D):
    cv = Canvas()
    off = int(t * 14)
    boulevard(cv, t + off)
    x = 200 + int(t * 6)
    f = SHE(cv, x, 156, 28, 'walk', 'smile', t=t, facing=1)
    lit = min(5, int(t / 0.4) + 1)
    sub = cv.a[f['top'] - 26:f['top'] - 8, x - 44:x + 50].astype(np.int16)
    cv.a[f['top'] - 26:f['top'] - 8, x - 44:x + 50] = (sub * 0.3 + np.array(WHITE) * 0.7).astype(np.uint8)
    cv.text(x - 42, f['top'] - 25, '难度', NAVY)
    stars(cv, x - 6, f['top'] - 17, 5, lit)
    HE(cv, 90 + int(t * 10), 156, 26, 'run', 'happy', t=t, facing=1)
    return cv


@shot(13)
def s13(t, D):
    cv = Canvas()
    boulevard(cv, t)
    up = t > 0.4
    f = SHE(cv, 210, 160, 32, 'reach' if up else 'stand', dict(eyes='open', mouth='flat', brow='up'), t=t, facing=-1)
    if up:
        hx, hy = f['hands'][1]
        cv.vline(int(hx), int(hy), int(hy) + 4, INK)
        cv.rect(hx - 14, hy - 30, 30, 28, INK); cv.rect(hx - 13, hy - 29, 28, 26, WHITE)
        big_text(cv, hx + 1, hy - 16, '退', BAL_D, size=16, outline=WHITE)
    g = HE(cv, 110, 160, 32, 'give' if t > 1.0 else 'stand', 'joy', t=t, facing=1)
    if t > 1.0:
        hx, hy = g['hands'][1]
        cv.rect(hx - 2, hy - 7, 4, 6, PAL['skin']); cv.rect(hx - 3, hy - 8, 6, 1, INK)
        symbol(cv, 'sparkle', g['cx'] + 12, g['top'] - 4, t)
    return cv


@shot(14)
def s14(t, D):
    cv = Canvas(hexc('2a2a3a'))
    off = int(t * 18)
    cv.rect(0, 20, W, 120, hexc('f4ecd8')); cv.rect(0, 20, W, 8, hexc('c8a050'))
    for i in range(6):
        x = 20 + i * 70 - off
        cv.rect(x, 70, 40, 30, hexc('3a3a5a'))
        cv.ellipse(x + 20, 72, 10, 8, hexc('ffd35a'), INK); cv.ellipse(x + 20, 72, 4, 3, hexc('8fd6ff'))
        cv.rect(x + 4, 104, 34, 12, WHITE); cv.text(x + 6, 104, '¥9999', INK)
        if t > 0.35 + i * 0.4:
            cv.line(x, 98, x + 40, 120, BAL_D); cv.line(x + 40, 98, x, 120, BAL_D)
            cv.line(x + 1, 98, x + 41, 120, BAL_D); cv.line(x + 41, 98, x + 1, 120, BAL_D)
    cv.rect(0, 140, W, 40, hexc('d8c8a8'))
    return cv


@shot(15)
def s15(t, D):
    cv = Canvas()
    boulevard(cv, t, autumn=True)
    leaves(cv, t, n=60)
    catch = t > 0.8
    f = HE(cv, 130, 160, 34, 'give' if catch else 'reach', 'happy', t=t, facing=1)
    SHE(cv, 220, 160, 34, 'take' if t > 1.4 else 'stand', 'wonder' if t < 1.4 else 'joy', t=t, facing=-1)
    lx, ly = (f['hands'][1] if catch else (150, 40 + t * 60))
    cv.poly([(lx - 6, ly), (lx, ly - 7), (lx + 6, ly), (lx, ly + 6)], hexc('ffb84a'))
    cv.line(lx, ly - 6, lx, ly + 8, hexc('a06a2a'))
    if t > 1.6: symbol(cv, 'heart', 176, 96, t)
    return cv


@shot(16)
def s16(t, D):
    cv = Canvas(hexc('e8d8b8'))
    cv.rect(70, 14, 180, 152, INK); cv.rect(71, 15, 178, 150, hexc('fffaf0'))
    for y in range(40, 160, 14): cv.hline(78, 242, y, hexc('d8e0f0'))
    title_text(cv, '约会计划', 160, 26, NAVY, size=12, outline=WHITE)
    items = ['看河', '喝咖啡', '浪漫晚餐']
    for i, s in enumerate(items):
        y = 48 + i * 30
        cv.rect(86, y, 12, 12, INK); cv.rect(87, y + 1, 10, 10, WHITE)
        cv.text(106, y, s, INK)
        if t > 0.3 + i * 0.6:
            if i < 2:
                cv.line(88, y + 6, 91, y + 10, hexc('3a9a5a')); cv.line(91, y + 10, 97, y + 1, hexc('3a9a5a'))
            else:
                cv.line(87, y + 1, 97, y + 11, BAL_D); cv.line(97, y + 1, 87, y + 11, BAL_D)
                cv.line(88, y + 1, 98, y + 11, BAL_D); cv.line(98, y + 1, 88, y + 11, BAL_D)
    return cv


@shot(17)
def s17(t, D):
    cv = Canvas()
    g1.street_scene(cv, t)
    trip = t > 0.5
    f = HE(cv, 120, GROUND, 30, 'jump' if 0.5 < t < 0.9 else ('stand' if t < 0.5 else 'sit'), 'happy' if t > 1.2 else 'surprise', t=t, facing=1)
    if not trip:
        cv.rect(f['hands'][1][0] - 6, f['hands'][1][1] - 8, 14, 8, hexc('fff4e0')); cv.rect(f['hands'][1][0] - 6, f['hands'][1][1] - 10, 14, 3, hexc('ff9ab0'))
    else:
        # 奶油糊脸
        cx, cy = f['cx'], f['top'] + 14
        cv.ellipse(cx, cy, 12, 8, hexc('fff4e0')); cv.ellipse(cx + 4, cy - 4, 3, 3, hexc('ff9ab0'))
    SHE(cv, 210, GROUND, 30, 'clap', 'joy', t=t, facing=-1)
    return cv


@shot(18)
def s18(t, D):
    cv = Canvas()
    sky_band(cv, [hexc('1a1e44'), hexc('3a3a7a'), hexc('6a5a9a')], 0, H)
    r = rng(18)
    for i in range(80):
        x, y = r.uniform(0, W), r.uniform(0, H)
        if (t * 3 + i) % 4 > 0.6: cv.px(x, y, hexc('fff4c0'))
    k = ease(clamp(t / 2.2))
    R = int(lerp(220, 54, k))
    cy = 100 + R
    cv.ellipse(160, cy, R, R, hexc('8ad07a'), INK)
    cv.ellipse(160 - R * 0.3, cy - R * 0.5, R * 0.25, R * 0.12, hexc('a8e08a'))
    top = cy - R
    eiffel(cv, 200, top + 3, max(16, int(70 * (54 / R) * 0.9)), hexc('8a7a8a'))
    s = max(12, int(28 * 54 / R * 0.8))
    HE(cv, 146, top + 4, s, 'sit', 'smile', t=t)
    SHE(cv, 166, top + 4, s, 'sit', 'joy', t=t)
    balloon(cv, 132, top - s * 2.2, max(0.8, s / 20), t, str_len=s * 1.6)
    return cv


# ---------------------------------------------------------------- 副歌 1
@shot(19)
def s19(t, D):
    cv = Canvas(hexc('f4ecd8'))
    cv.rect(90, 16, 140, 150, INK); cv.rect(91, 17, 138, 148, WHITE)
    cv.rect(91, 17, 138, 26, BAL_D)
    pages = 6
    k = clamp(t / 1.8)
    n = int(k * pages)
    days = ['5', '4', '3', '2', '1', '14']
    day = days[min(n, pages - 1)]
    title_text(cv, '那一天' if n >= pages - 1 else 'MAY', 160, 30, WHITE, size=12, outline=BAL_D)
    title_text(cv, day, 160, 100, INK, size=48, outline=WHITE)
    if k < 1:
        fl = (k * pages) % 1
        cv.poly([(91, 43), (229, 43), (229, 43 + int(120 * (1 - fl))), (91, 43 + int(120 * (1 - fl)) + 6)], hexc('f4f0e8'))
    else:
        for a in range(0, 360, 8):
            cv.rect(160 + math.cos(math.radians(a)) * 36, 100 + math.sin(math.radians(a)) * 30, 2, 2, BAL)
    return cv


@shot(20)
def s20(t, D):
    cv = Canvas()
    sky_band(cv, SKY_DUSK, 0, 140)
    eiffel(cv, 200, 140, 130, hexc('6a4a6a'))
    paris_row(cv, 140, seed=8, hmin=24, hmax=40, cols=[hexc('e8b8a8'), hexc('d8a8a0')])
    ground_band(cv, 140, hexc('c8a898'))
    look = t > 1.2
    HE(cv, 128, 166, 30, 'stand', 'shy' if look else 'normal', t=t, facing=1 if look else 0)
    SHE(cv, 160, 166, 30, 'stand', 'smile', t=t)
    balloon(cv, 110, 108, 1.1, t, str_len=26)
    if look: symbol(cv, 'heart', 140, 110, t)
    return cv


@shot(21)
def s21(t, D):
    cv = Canvas(hexc('f4ecd8'))
    cv.ellipse(160, 120, 90, 30, hexc('e8e0d0'), INK)
    cv.ellipse(160, 112, 70, 22, WHITE, INK)
    cv.ellipse(160, 110, 58, 16, hexc('7a4a2a'))
    beat = 0.673
    n = int(t / beat)
    for i in range(n + 1):
        tt = t - i * beat
        if tt < 0: continue
        x = 130 + (i * 23) % 60
        if tt < 0.35:
            y = lerp(-10, 104, tt / 0.35)
            cv.rect(x - 5, y - 5, 10, 10, INK); cv.rect(x - 4, y - 4, 8, 8, WHITE)
        elif tt < 1.4:
            u = (tt - 0.35) / 1.05
            heart_px(cv, x, 96 - u * 30, 2, mix(BAL_H, hexc('f4ecd8'), u))
            for a in (-1, 1): cv.px(x + a * (4 + u * 10), 104 - u * 6, hexc('a8784a'))
    return cv


@shot(22)
def s22(t, D):
    cv = Canvas()
    g1.street_scene(cv, t)
    f = SHE(cv, 200, GROUND, 32, 'hand_chest', dict(eyes='closed', mouth='flat', blush=True), t=t, facing=1)
    cv.ellipse(f['cx'] - 6, f['top'] + 26, 4, 3, hexc('ffb0b8'))
    cv.ellipse(f['cx'] + 8, f['top'] + 26, 4, 3, hexc('ffb0b8'))
    big_text(cv, f['cx'] + 24, f['top'] - 4, '哼', NAVY, size=12, outline=WHITE)
    g = HE(cv, 120, GROUND, 32, 'give', 'smile', t=t, facing=1)
    hx, hy = g['hands'][1]
    for i, c in enumerate([hexc('ffb0c8'), hexc('b8e8c8'), hexc('f8e0a0')]):
        cv.ellipse(hx + 4 + i * 2, hy - 4 - i * 5, 5, 2.5, c, INK)
    return cv


def eye2(cv, cx, cy, w, h, look=0, heart=False, tear=False):
    m = ell_mask(w / 2, h / 2)
    cv.mask_fill(dilate(m), INK, cx - w // 2 - 1, cy - h // 2 - 1)
    cv.mask_fill(m, WHITE, cx - w // 2, cy - h // 2)
    ir = h * 0.46
    ix = cx + look * w * 0.22
    cv.ellipse(ix, cy + 2, ir, ir, hexc('6a3a2a'), INK)
    cv.ellipse(ix, cy + 2, ir * 0.6, ir * 0.6, hexc('3a1a14'))
    if heart: heart_px(cv, ix + ir * 0.3, cy - ir * 0.2, max(1, int(ir / 7)), WHITE)
    else: cv.ellipse(ix + ir * 0.4, cy - ir * 0.3, ir * 0.22, ir * 0.22, WHITE)
    cv.rect(cx - w // 2 + 2, cy - h // 2 - 4, w - 4, 5, INK)
    if tear:
        cv.rect(cx - w // 2 + 4, cy + h // 2 - 2, w - 8, 2, hexc('8fd8ff'))


def eyes_close(cv, t, look=0, heart=False, tear=False):
    cv.a[:] = PAL['skin']
    cv.rect(0, 0, W, 30, PAL['hair'])
    for x in range(0, W, 18): cv.rect(x, 26, 10, 10, PAL['hair'])
    eye2(cv, 92, 100, 92, 72, look, heart, tear)
    eye2(cv, 232, 100, 92, 72, look, heart, tear)
    for x0 in (92, 232): cv.rect(x0 - 40, 50, 80, 5, PAL['hair'])
    cv.ellipse(70, 150, 16, 6, hexc('ffb0b8')); cv.ellipse(254, 150, 16, 6, hexc('ffb0b8'))


@shot(23)
def s23(t, D):
    cv = Canvas()
    look = -1 + ease(clamp((t - 0.8) / 0.8)) * 2
    eyes_close(cv, t, look=look)
    return cv


@shot(24)
def s24(t, D):
    cv = Canvas()
    g1.street_scene(cv, t)
    nod = int(abs(math.sin(t * 6)) * 2) if 0.4 < t < 1.6 else 0
    f = SHE(cv, 190, GROUND + nod, 32, 'take', 'joy', t=t, facing=-1)
    HE(cv, 130, GROUND, 32, 'give', 'happy', t=t, facing=1)
    for i in range(3):
        u = ((t - 0.4) * 0.8 + i * 0.3) % 1.2
        if t > 0.4: heart_px(cv, f['cx'] - 10 + i * 10, f['top'] - 6 - u * 30, 1, BAL_H)
    balloon(cv, 104, 92, 1.0, t, str_len=30)
    return cv
