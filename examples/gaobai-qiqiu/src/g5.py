"""第 5 章：终副歌（49–55）+ 谢幕（56）。"""
from gbl import *
from gbl import _DITH, _poly_mask
from tl import shot
import g1, g2, g4


DOODLES = ['cafe', 'balloon', 'leaf', 'rain', 'cake', 'tower', 'globe', 'planet']


@shot(49)
def s49(t, D):
    cv = Canvas(hexc('c8a888'))
    cv.rect(40, 16, 240, 150, INK); cv.rect(41, 17, 238, 148, hexc('fffaf0'))
    cv.vline(160, 16, 166, INK)
    beat = 0.673
    n = int(t / beat)
    k = (t / beat) % 1
    left = DOODLES[(2 * n) % len(DOODLES)]; right = DOODLES[(2 * n + 1) % len(DOODLES)]
    for y in range(34, 160, 12):
        cv.hline(48, 152, y, hexc('d8e0f0')); cv.hline(168, 272, y, hexc('d8e0f0'))
    for kind, x in ((left, 78), (right, 196)):
        g4.polaroid(cv, x, 56, kind, t)
    cv.text(60, 24, f'DAY {n * 7 + 1}', NAVY); cv.text(180, 24, f'DAY {n * 7 + 4}', NAVY)
    if k < 0.3:   # 翻页
        u = k / 0.3
        w = int(118 * (1 - u))
        cv.poly([(160, 17), (160 + w, 17 + int(u * 6)), (160 + w, 165 - int(u * 6)), (160, 165)], hexc('f4f0e4'))
        cv.line(160 + w, 17, 160 + w, 165, INK)
    heart_px(cv, 260, 150, 1, BAL)
    return cv


@shot(50)
def s50(t, D):
    cv = Canvas(hexc('f8e8f0'))
    # 香水瓶
    bx, by = 70, 110
    cv.rect(bx - 22, by - 30, 44, 56, INK); cv.rect(bx - 21, by - 29, 42, 54, hexc('ffc8dc'))
    cv.rect(bx - 15, by - 22, 8, 40, hexc('ffe8f0'))
    cv.rect(bx - 6, by - 42, 12, 12, INK); cv.rect(bx - 5, by - 41, 10, 10, GOLD)
    cv.ellipse(bx + 4, by - 50, 10, 8, hexc('e88aa8'), INK)
    spray = t > 0.4
    if spray:
        r = rng(50)
        for i in range(60):
            u = clamp((t - 0.4) / 1.6)
            x = bx + 14 + r.uniform(0, 1) * 200 * u; y = by - 46 + r.uniform(-1, 1) * 40 * u
            if _DITH[int(y) % H, int(x) % W] < 0.7: cv.px(x, y, hexc('ffd0e0'))
    memories = ['cafe', 'leaf', 'balloon', 'rain', 'cake']
    for i, kind in enumerate(memories):
        u = clamp((t - 0.8 - i * 0.6) / 1.2)
        if u <= 0: continue
        x = 140 + i * 36; y = 110 - u * 60 + math.sin(t * 2 + i) * 4
        R = 18
        cv.ellipse(x, y, R, R, hexc('fff4f8'), hexc('e8b8c8'))
        sub = Canvas(KEY); g4.polaroid(sub, int(x - 22), int(y - 21), kind, t)
        m = np.any(sub.a != np.array(KEY, np.uint8), axis=2)
        yy, xx = np.mgrid[0:H, 0:W]; m &= ((xx - x) ** 2 + (yy - y) ** 2) < (R - 3) ** 2
        cv.a[m] = sub.a[m]
        cv.px(x - 8, y - 9, WHITE); cv.px(x - 7, y - 10, WHITE)
    return cv


@shot(51)
def s51(t, D):
    cv = Canvas(hexc('1e2448'))
    r = rng(51)
    for i in range(40):
        if (t * 2 + i) % 3 > 0.5: cv.px(r.uniform(0, W), r.uniform(0, H), hexc('8a8ac0'))
    # 玻璃瓶
    cx, cy = 160, 100
    bm = _poly_mask([(cx - 46, cy - 40), (cx - 16, cy - 56), (cx - 16, cy - 76), (cx + 16, cy - 76), (cx + 16, cy - 56), (cx + 46, cy - 40), (cx + 52, cy + 50), (cx - 52, cy + 50)])
    cv.a[dilate(bm)] = hexc('cfe8f8'); cv.a[bm] = hexc('2a3466')
    cv.rect(cx - 18, cy - 84, 36, 10, hexc('b07a4a'))
    for i in range(50):
        x = r.uniform(cx - 44, cx + 44); y = r.uniform(cy - 36, cy + 46)
        if bm[int(y), int(x)] and (t * 3 + i) % 2 > 0.4:
            cv.px(x, y, GOLD)
            if i % 5 == 0: cv.px(x + 1, y, GOLD); cv.px(x - 1, y, GOLD); cv.px(x, y + 1, GOLD); cv.px(x, y - 1, GOLD)
    SHE(cv, cx, cy + 36, 22, 'wave', 'joy', t=t)
    cv.line(cx - 40, cy - 30, cx - 44, cy + 30, WHITE)
    return cv


@shot(52)
def s52(t, D):
    cv = Canvas(hexc('f4ecd8'))
    pour = ease(clamp(t / 1.2))
    # 中间的大杯（俯视）
    cv.ellipse(160, 100, 66, 54, WHITE, INK)
    cv.ellipse(160, 100, 54, 44, hexc('7a4a2a'))
    if t < 1.4:
        for sx, col in ((60, hexc('7a4a2a')), (260, hexc('f4e8d8'))):
            cv.ellipse(sx, 40, 26, 20, WHITE, INK); cv.ellipse(sx, 40, 20, 15, col)
            for k in range(int(pour * 20)):
                x = lerp(sx, 160 + (sx - 160) * 0.2, k / 20); y = 40 + k * 2.6
                cv.rect(x - 2, y, 4, 3, col)
        cv.ellipse(160 + 20, 100, 20, 14, hexc('f4e8d8'))
    else:
        u = t - 1.4
        for i in range(260):
            a = i * 0.18 + u * 6
            rr = 4 + i * 0.16
            x = 160 + math.cos(a) * rr; y = 100 + math.sin(a) * rr * 0.8
            if rr < 44: cv.rect(x, y, 2, 2, hexc('f4e8d8') if (i // 20) % 2 else hexc('a06a40'))
        if u > 1.2:
            heart_px(cv, 160, 100, 4, hexc('f4e8d8'))
        cv.line(160, 100, 220, 20, hexc('c8ccd4')); cv.line(161, 100, 221, 20, hexc('c8ccd4'))
    return cv


def tower_night(cv, t):
    sky_band(cv, SKY_NIGHT, 0, 150)
    eiffel(cv, 160, 150, 150, hexc('3a3050'), lights=1.0, t=t)
    paris_row(cv, 150, seed=61, hmin=20, hmax=34, lit=0.6, night=1.0)
    ground_band(cv, 150, hexc('4a4a5a'))
    for i in range(3):
        x = 40 + i * 120; cv.rect(x, 110, 2, 40, INK); cv.ellipse(x, 108, 4, 4, hexc('fff0b0'))


@shot(53)
def s53(t, D):
    cv = Canvas()
    tower_night(cv, t)
    kneel = t > 0.6
    f = HE(cv, 130, 172, 34, 'sit' if kneel else 'stand', 'smile', t=t, facing=1)
    hx = f['cx'] + 18
    balloon(cv, hx + 4, f['top'] - 18, 2.0, t, str_len=24)
    cv.line(f['cx'] + 6, f['top_body'] + 6, hx + 4, f['top'] + 10, INK)
    g = SHE(cv, 210, 172, 34, 'hand_chest' if kneel else 'stand', dict(eyes='wide', mouth='o', blush=True) if kneel else 'normal', t=t, facing=-1)
    if kneel: symbol(cv, 'excl', g['cx'] + 12, g['top'] - 6, t)
    return cv


@shot(54)
def s54(t, D):
    cv = Canvas()
    g2.eyes_close(cv, t, look=-0.3, heart=True, tear=True)
    for x0 in (92, 232):
        for a in range(0, 360, 45):
            if int(t * 6 + a) % 3 == 0: cv.px(x0 + math.cos(math.radians(a)) * 56, 100 + math.sin(math.radians(a)) * 44, WHITE)
    if t > 1.6:
        for sg in (92, 232):
            L = int((t - 1.6) * 30)
            cv.rect(sg - 30, 136, 3, min(40, L), hexc('8fd8ff'))
    return cv


@shot(55)
def s55(t, D):
    cv = Canvas()
    tower_night(cv, t)
    fireworks(cv, t, seed=3, n=7)
    k = ease(clamp(t / D))
    HE(cv, 140, 172, 30, 'cheer' if t > 1.2 else 'stand', 'joy', t=t, facing=1)
    f = SHE(cv, 178, 172, 30, 'cheer' if t > 1.2 else 'take', 'joy', t=t, facing=-1)
    balloon(cv, 196, f['top'] - 24, 1.8, t, face_=True, str_len=24)
    if t < 1.6:
        bubble(cv, f['cx'] + 6, f['top'] - 46, '我愿意', BAL_D, WHITE)
    if t > 0.3:
        u = clamp((t - 0.3) / 0.5)
        m = Canvas(KEY); title_text(m, '告白成功！', 160, 44, GOLD, size=20, outline=BAL_D)
        mm = np.any(m.a != np.array(KEY, np.uint8), axis=2) & (_DITH < u)
        cv.a[mm] = m.a[mm]
    confetti(cv, t, seed=5, n=40)
    return cv


@shot(56)
def s56(t, D):
    cv = Canvas()
    tower_night(cv, t)
    fireworks(cv, t + 3, seed=8, n=4)
    bow = abs(math.sin(clamp((t - 0.4) / 1.2) * math.pi))
    e = 'closed' if bow > 0.4 else 'joy'
    HE(cv, 138, 172 + int(bow * 3), 30, 'hand_chest' if bow > 0.4 else 'wave', e, t=t)
    SHE(cv, 182, 172 + int(bow * 3), 30, 'hand_chest' if bow > 0.4 else 'wave', e, t=t)
    # 红幕布合上
    c = ease(clamp((t - 2.0) / 1.6))
    if c > 0:
        w = int(c * 162)
        for side in (0, 1):
            x0 = 0 if side == 0 else W - w
            cv.rect(x0, 0, w, H, hexc('a8203a'))
            for x in range(x0, x0 + w, 10): cv.vline(x, 0, H, hexc('80182c'))
        cv.rect(0, 0, W, 14, hexc('80182c')); cv.rect(0, 14, W, 2, GOLD)
    k = clamp((t - 3.8) / 0.8) * (1 - clamp((t - (D - 1.2)) / 1.2))
    if k > 0:
        m = Canvas(KEY)
        title_text(m, 'THANKS FOR WATCHING', 160, 76, hexc('fff6e0'), size=16)
        m.text(160, 98, '原唱 · 周杰伦', hexc('fff6e0'), outline=INK, anchor='mt')
        mm = np.any(m.a != np.array(KEY, np.uint8), axis=2) & (_DITH < k)
        cv.a[mm] = m.a[mm]
    fade_black(cv, clamp((t - (D - 1.5)) / 1.5))
    return cv
