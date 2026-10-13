"""第 3 章：间奏（25–29）+ 主歌 2（30–36）。"""
from gbl import *
from gbl import _DITH, _poly_mask
from tl import shot
import g1


@shot(25)
def s25(t, D):
    cv = Canvas()
    sky_band(cv, SKY_NIGHT, 0, 110)
    eiffel(cv, 270, 108, 90, hexc('2a2a44'), lights=1.0, t=t)
    paris_row(cv, 110, seed=40, hmin=30, hmax=50, lit=0.5, night=1.0)
    cv.rect(0, 110, W, 20, hexc('2a2a44'))
    # 舞台
    cv.rect(80, 110, 160, 20, hexc('6a3a4a')); cv.rect(80, 110, 160, 2, INK)
    for i in range(8): cv.ellipse(90 + i * 20, 110, 4, 2, GOLD)
    # 舞台灯
    for sx in (100, 220):
        for y in range(0, 110, 2):
            w = y * 0.25
            for x in range(int(sx + (160 - sx) * y / 110 - w), int(sx + (160 - sx) * y / 110 + w)):
                if 0 <= x < W and _DITH[y, x] < 0.18: cv.px(x, y, hexc('fff0c0'))
    f = HE(cv, 160, 110, 28, 'cheer' if t > 1.5 else 'hold_r', 'happy', t=t)
    hx, hy = f['hands'][1] if t <= 1.5 else f['hands'][1]
    cv.rect(hx - 1, hy - 6, 3, 7, INK); cv.ellipse(hx, hy - 7, 2, 2, hexc('8a8a9a'))
    cv.rect(0, 130, W, 50, hexc('1e2240'))
    # 观众 + 鸽子举荧光棒
    for i in range(12):
        x = 10 + i * 27; up = (t * 2 + i * 0.3) % 1 < 0.5 and t > 0.6
        cv.ellipse(x, 160, 9, 11, hexc('3a3a5a'), INK); cv.ellipse(x, 146, 6, 6, hexc('4a4a6a'), INK)
        if up:
            cv.line(x + 6, 150, x + 10, 136, INK)
            cv.rect(x + 9, 128, 2, 9, [hexc('ff8aa8'), hexc('8fd6ff'), hexc('ffd35a')][i % 3])
    for i in range(3): pigeon(cv, 60 + i * 100, 132, t + i)
    return cv


@shot(26)
def s26(t, D):
    cv = Canvas()
    g1.skyline(cv, t + 20, SKY_NIGHT, 1.0, tower_x=200, river=(120, 160))
    cv.rect(0, 160, W, 20, hexc('2a2a3a')); cv.hline(0, W, 160, INK)
    boat(cv, int(W + 40 - t * 40), 140, t, lights=True)
    for k in range(int(t * 40 % 80)):
        cv.px(W + 74 - t * 40 + k, 147, mix(hexc('ffe08a'), hexc('1a2448'), k / 80))
    # 塔灯倒影
    for y in range(124, 160, 2):
        if int(t * 8 + y) % 3: cv.hline(196 - (y - 120) // 6, 204 + (y - 120) // 6, y, hexc('d8c070'))
    return cv


@shot(27)
def s27(t, D):
    cv = Canvas(hexc('f0d8c0'))
    cv.rect(0, 140, W, 40, hexc('c8a888')); cv.hline(0, W, 140, INK)
    cv.rect(220, 30, 70, 50, INK); cv.rect(222, 32, 66, 46, hexc('2a3060'))
    for i in range(6): cv.px(230 + i * 10, 40 + (i * 7) % 30, hexc('fff4c0'))
    n = int(lerp(12, 99, ease(clamp(t / (D - 0.6)))))
    r = rng(27)
    for i in range(min(40, n // 2)):
        balloon(cv, r.uniform(20, 300), r.uniform(20, 120), 1.0, t + i, string=False, sway=False)
    f = HE(cv, 150, 160, 32, 'hold_r', dict(eyes='squeeze', mouth='o') if t > 2 else dict(eyes='closed', mouth='o'), t=t)
    # 正在吹的气球（变大）
    gr = 0.6 + ((t * 1.3) % 1) * 1.4
    balloon(cv, f['cx'] + 22, f['top'] + 14, gr, t, string=False, sway=False)
    label(cv, 14, 28, f'×{n}', BAL_D, WHITE)
    if t > 2.6:
        for i in range(3): cv.px(f['cx'] - 6 + i * 6, f['top'] - 6 - int(math.sin(t * 8 + i) * 2), GOLD)
    return cv


@shot(28)
def s28(t, D):
    cv = Canvas()
    sky_band(cv, SKY_NIGHT, 0, H)
    r = rng(28)
    for i in range(50):
        x, y = r.uniform(0, W), r.uniform(0, 80)
        if (t * 3 + i) % 4 > 0.6: cv.px(x, y, hexc('fff4c0'))
    cv.rect(70, 30, 180, 150, hexc('e8d8c0')); cv.rect(70, 30, 180, 1, INK)
    wx, wy, ww, wh = 110, 60, 100, 90
    cv.rect(wx - 3, wy - 3, ww + 6, wh + 6, INK); cv.rect(wx, wy, ww, wh, hexc('ffe8b0'))
    op = ease(clamp((t - 0.9) / 0.6))
    cv.rect(wx, wy, int(ww / 2 * (1 - op * 0.7)), wh, hexc('8ab0d0')); cv.rect(wx + ww - int(ww / 2 * (1 - op * 0.7)), wy, int(ww / 2 * (1 - op * 0.7)), wh, hexc('8ab0d0'))
    if op > 0.3:
        SHE(cv, 160, wy + wh + 4, 34, 'wonder' if False else 'hand_chest', 'wonder' if t < 2.2 else 'joy', t=t, hat=False)
    # 窗外的气球 + 纸条
    bx, by = 240, 70
    end = balloon(cv, bx, by, 1.6, t, str_len=50)
    cv.rect(bx - 20, by + 54, 42, 16, INK); cv.rect(bx - 19, by + 55, 40, 14, WHITE)
    cv.text(bx - 17, by + 55, '明天见', INK, font=FONT12)
    cv.rect(66, wy + wh + 2, 188, 4, hexc('c8b8a0'))
    return cv


@shot(29)
def s29(t, D):
    cv = Canvas()
    sky_band(cv, SKY_DAWN, 0, 120)
    cv.ellipse(70, 118, 22, 22, hexc('fff0c0'))
    paris_row(cv, 118, seed=41, hmin=24, hmax=44)
    seine(cv, 118, 140, t)
    ground_band(cv, 140, hexc('d8c8a8'))
    lift = max(0, math.sin(t * 3)) * 6 if t > 1.5 else 0
    x = 60 + t * 34
    f = HE(cv, x, 166 - lift, 28, 'reach', 'surprise' if lift > 3 else 'happy', t=t, facing=1)
    hx, hy = f['hands'][1]
    for i in range(9):
        a = -1.2 + i * 0.3
        bx = hx + 20 + math.cos(a) * 18 + (i % 3) * 6; by = hy - 50 + math.sin(a) * 14 + (i // 3) * 6
        cv.line(hx, hy, bx, by + 6, hexc('6a6a7a'))
        balloon(cv, bx, by, 1.0, t + i * 0.3, string=False)
    return cv


# ---------------------------------------------------------------- 主歌 2（雨天，换画面）
@shot(30)
def s30(t, D):
    cv = Canvas()
    g1.street_scene(cv, t, 0, rainy=True)
    table(cv, 100, 124, 40, cloth=True); cup(cv, 92, 117, 1, steam_t=t); cup(cv, 110, 117, 1, steam_t=t + 1)
    HE(cv, 70, GROUND, 26, 'sit', 'smile', t=t, facing=1)
    SHE(cv, 130, GROUND, 26, 'sit', 'joy', t=t, facing=-1)
    def excl(x, y): return x < 160 and 76 < y
    rain(cv, t, n=160, seed=30, speed=150, col=hexc('e0e8f4'), excl=excl, y_ground=176)
    return cv


@shot(31)
def s31(t, D):
    cv = Canvas(hexc('f4e8d0'))
    cv.rect(0, 0, W, 24, NAVY)
    cv.rect(0, 130, W, 50, hexc('f4f0e8')); cv.hline(0, W, 130, INK)
    sip = t > 1.0
    f = face(cv, 'she', 200, 36, 54, dict(eyes='happy' if sip else 'open', mouth='smile'), t=t)
    if sip:
        my = f['top'] + int(54 * 0.84)
        cv.ellipse(f['cx'], my - 3, 14, 3, WHITE, INK)
    # 拉花咖啡（俯视）
    cv.ellipse(86, 120, 40, 18, WHITE, INK); cv.ellipse(86, 116, 32, 12, hexc('b07a4a'))
    heart_px(cv, 86, 116, 2, hexc('f4ecd8'))
    if sip:
        g = Canvas();
        big_text(cv, 60, 70, '噗', NAVY, size=12, outline=WHITE)
    return cv


@shot(32)
def s32(t, D):
    cv = Canvas()
    g1.street_scene(cv, t, 0, rainy=True)
    k = ease(clamp(t / 0.9))
    HE(cv, 150, GROUND, 34, 'stand', 'normal' if t < 1.2 else 'stunned', t=t, facing=1)
    f = SHE(cv, int(lerp(220, 178, k)), GROUND - int(k * 4), 34, 'stand', dict(eyes='closed', mouth='o', blush=True), t=t, facing=-1)
    if t > 1.0: symbol(cv, 'heart', 166, 70, t)
    rain(cv, t, n=120, seed=32, speed=150, col=hexc('e0e8f4'), excl=lambda x, y: x < 160 and y > 76, y_ground=176)
    return cv


@shot(33)
def s33(t, D):
    cv = Canvas(hexc('f4e8d0'))
    k = ease(clamp(t / 2.0))
    Hh = int(lerp(70, 86, k))
    f = face(cv, 'he', 160, 30, Hh, dict(eyes='dot', mouth='flat', blush=True), t=t)
    # 粉色唇印
    lx, ly = int(160 + f['Wh'] * 0.26), 30 + int(Hh * 0.72)
    cv.ellipse(lx - 3, ly, 5, 3, LIP); cv.ellipse(lx + 4, ly, 5, 3, LIP); cv.ellipse(lx, ly + 4, 7, 3, LIP)
    cv.hline(lx - 6, lx + 8, ly + 2, hexc('d06a80'))
    for i in range(4):
        ph = (t * 1.4 + i * 0.25) % 1
        cv.ellipse(140 + i * 14 + math.sin(ph * 6) * 3, 30 - ph * 30, 3 + ph * 5, 3 + ph * 4, hexc('d8d8e0'))
    return cv


@shot(34)
def s34(t, D):
    cv = Canvas(hexc('e8f4ec'))
    cv.rect(0, 0, W, 30, hexc('4a9a6a')); title_text(cv, 'FLEURS', 160, 14, WHITE, size=12, outline=hexc('2a6a4a'))
    cv.rect(0, 120, W, 60, hexc('c8a888')); cv.hline(0, W, 120, INK)
    # 卡片（大）
    cv.rect(110, 54, 110, 64, INK); cv.rect(111, 55, 108, 62, WHITE)
    cv.text(118, 62, 'To:', INK)
    n = min(2, int(t / 0.8))
    cv.text(140, 62, '小语'[:n], INK)
    if t > 2.0: heart_px(cv, 196, 96, 2, BAL)
    # 店员核对（右）+ 他（左）写字
    char(cv, 'npc_g', 270, 150, 28, 'point_up' if t > 1.6 else 'stand', 'smile' if t > 1.6 else 'normal', t)
    if t > 1.6: big_text(cv, 270, 60, '✓', hexc('3a9a5a'), size=16, outline=WHITE) if False else cv.text(258, 56, 'OK!', hexc('3a9a5a'), outline=WHITE)
    f = HE(cv, 60, 160, 32, 'reach', 'normal', t=t, facing=1)
    for j in range(5):
        cv.ellipse(30 + (j % 3) * 10, 100 + (j // 3) * 8, 5, 5, hexc('e8506a'), INK)
    return cv


@shot(35)
def s35(t, D):
    cv = Canvas()
    sky_band(cv, SKY_RAIN, 0, H)
    paris_row(cv, 160, seed=55, hmin=110, hmax=140)
    # 她的阳台（右）
    cv.rect(220, 96, 90, 6, INK);
    for x in range(222, 308, 6): cv.vline(x, 102, 120, INK)
    cv.rect(220, 120, 90, 3, INK)
    SHE(cv, 266, 102, 22, 'wonder' if False else 'stand', 'surprise', t=t, facing=-1, hat=False)
    k = ease(clamp(t / D))
    for i in range(7):
        bx = lerp(-20, 230, k) + (i % 3) * 12 - 10; by = lerp(70, 70, k) - (i // 3) * 12 + math.sin(t * 3 + i) * 3
        balloon(cv, bx, by, 1.0, t + i * 0.2, string=False)
        cv.line(bx, by + 8, lerp(-20, 240, k), 110, hexc('5a5a6a'))
    for i in range(5):
        y = 30 + i * 22; x = (t * 160 + i * 60) % (W + 60) - 30
        cv.hline(x, x + 22, y, WHITE)
    return cv


@shot(36)
def s36(t, D):
    cv = Canvas()
    sky_band(cv, SKY_DAY, 0, H)
    paris_row(cv, H + 30 - int(t * 6), seed=6, hmin=80, hmax=110)
    r = rng(36)
    for i in range(26):
        x = r.uniform(0, W); y0 = r.uniform(20, 200)
        y = y0 - t * r.uniform(8, 18)
        balloon(cv, x, y, r.uniform(0.8, 1.5), t + i, face_=True, string=True, str_len=10)
    f = SHE(cv, 160, 176 - int(t * 6), 30, 'reach', 'joy', t=t, hat=False)
    return cv
