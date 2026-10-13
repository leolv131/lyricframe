"""副歌 2（117.52–143.27）：雨停，天亮。光从她那里扩散到整条巷子、整片废墟。"""
from w3 import *


def d14(t, D):  # 117.52–123.82 她用伞尖戳破他头顶的小乌云 → 阳光扫过巷子
    cv = Canvas()
    hit = 0.5
    b = ease(clamp((t - hit) / 2.5))
    wins = alley(cv, t, 0.15 + 0.7 * b)
    m, a = chibi('wu', 130, 168, 32, 'stand', 'sad' if t < hit else 'surprise' if t < 2 else 'smile', t, facing=1, floor=0.7)
    ms, as_ = chibi('die', 200, 168, 32, 'reach', 'smile', t, facing=-1, floor=0.95)
    f = a['f']
    tip = (150 + 6 * ease(clamp(t / hit)), f['top'] - 14)
    lit2(cv, [Light(tip[0], tip[1], 'fff0c0', 40 + 300 * b, 0.5 + 0.25 * b)], (0.22 + 0.55 * b, 0.22 + 0.53 * b, 0.32 + 0.45 * b), t)
    alley_emissive(cv, wins, 1 - b)
    cv.line(186, 126, tip[0], tip[1], INK); cv.line(187, 126, tip[0] + 1, tip[1], hexc('e0a030'))
    cv.poly([(184, 120), (174, 108), (180, 106)], hexc('ffcf5a'))
    cx, cy = f['cx'] + 2, f['top'] - 16
    if b <= 0:
        for (dx, dy, r) in [(-8, 2, 6), (0, -2, 8), (9, 2, 6)]: cv.ellipse(cx + dx, cy + dy, r, r * 0.8, hexc('4a4e5a'), INK)
        for i in range(5):
            yy = cy + 8 + int((t * 40 + i * 7) % 18); cv.vline(cx - 10 + i * 5, yy, yy + 2, hexc('8a94b0'))
    else:
        for i in range(12):
            ang = math.radians(i * 30); rr = 6 + b * 60
            cv.line(cx + math.cos(ang) * rr * 0.5, cy + math.sin(ang) * rr * 0.5, cx + math.cos(ang) * rr, cy + math.sin(ang) * rr, hexc('ffe8a0'))
        glow(cv, cx, cy, 30 + 40 * b, 'ffd070', 0.5 * (1 - b * 0.5))
    if t < hit + 2.5: rain(cv, t, n=int(160 * (1 - b)), seed=14, speed=170, col='6a7494')
    # 水滴闪光
    for i in range(10):
        if b > 0.3 and (t * 3 + i) % 2 < 0.2: cv.px(20 + i * 30, 30 + (i * 17) % 60, WHITE)
    return cv


def d15(t, D):  # 123.82–130.14 茧破，蝴蝶飞出（特写 → 飞向天空）
    cv = Canvas()
    if t < 3.4:
        sky(cv, ['ffcf8a', 'ffe8c0', 'fff4e0'], 0, H)
        cv.rect(0, 150, W, 30, hexc('a07a5a'))
        crack = clamp((t - 0.6) / 1.0)
        cx, cy = seedling(cv, 150, 172, s=5, crack=crack)
        lit2(cv, [Light(cx, cy, '8fd6ff', 60, 0.8 * crack), Light(280, 20, 'ffd080', 300, 0.6)], (0.75, 0.72, 0.68), t)
        e = clamp((t - 1.4) / 1.0)
        if e > 0:
            fl = 0.3 + 0.7 * ease(clamp((t - 2.0) / 0.8))
            bfly(cv, cx + 2, cy - e * 22, 3, t, flap=fl if t < 2.8 else None, speed=3)
            glow(cv, cx + 2, cy - e * 22, 30, '3a7aff', 0.35)
    else:
        u = t - 3.4
        emis = np.zeros((H, W), bool)
        base = ruins(cv, t, 30 + u * 8, 0.75, emis=emis)
        flat(cv)
        path = lambda tt: (120 + tt * 70, 120 - tt * 34 - math.sin(tt * 3) * 8)
        trail(cv, path, u, 1.6); x, y = path(u)
        bfly(cv, x, y, 2, t); glow(cv, x, y, 18, '3a7aff', 0.4)
        sun_y = 40
        cv.ellipse(270, sun_y, 12, 12, hexc('fff2c8')); glow(cv, 270, sun_y, 50, 'ffb060', 0.35)
    return cv


FLOWERS = [(30, 158), (96, 150), (140, 160), (196, 152), (250, 158), (60, 168), (290, 166), (170, 170), (226, 146), (120, 172)]
FCOL = ['ff6a8a', 'ffd35a', 'ff9a4a', 'f6f2e6', 'c87aff', 'ff8aa8']


def flower(cv, x, y, s, col, k=1.0):
    if k <= 0: return
    h = int(8 * s * k)
    cv.vline(x, y - h, y, hexc('4a9a4a'))
    r = 2.5 * s * k
    for ang in range(0, 360, 72):
        cv.ellipse(x + math.cos(math.radians(ang)) * r, y - h + math.sin(math.radians(ang)) * r, r * 0.7 + 0.5, r * 0.7 + 0.5, hexc(col))
    cv.ellipse(x, y - h, r * 0.5 + 0.5, r * 0.5 + 0.5, hexc('ffd35a'))


def d16(t, D):  # 130.14–136.96 废墟砖缝开花；两人蹲着看，他惊得张大嘴
    cv = Canvas()
    emis = np.zeros((H, W), bool)
    base = ruins(cv, t, 40 + t * 3, 0.85, near=True, emis=emis)
    beat = 0.405
    for i, (x, y) in enumerate(FLOWERS):
        flower(cv, x, y, 1.5, FCOL[i % len(FCOL)], ease(clamp((t - i * beat) / 0.25)))
    m, a = chibi('wu', 120, 162, 32, 'sit', 'surprise' if t > 0.8 else 'wonder', t, facing=1, floor=0.95)
    ms, as_ = chibi('die', 210, 162, 32, 'sit', 'joy', t, facing=-1, floor=0.95)
    flat(cv)
    cv.ellipse(280, 34, 12, 12, hexc('fff2c8')); glow(cv, 280, 34, 50, 'ffb060', 0.3)
    if t > 0.8: symbol(cv, 'excl', a['cx'] + 12, a['top'] - 4, t)
    for i in range(6):   # 花瓣飘
        x = (i * 53 + t * 20) % W; y = (i * 31 + t * 12) % 120 + 20
        cv.rect(x, y, 2, 2, hexc(FCOL[i % 6]))
    return cv


def chalk(cv, cx, cy, sx, sy, col='e8e8e0'):
    pts = [(-6, -40), (6, -40), (8, -30), (22, -22), (26, -14), (10, -16), (10, 4), (16, 30), (8, 32), (0, 10), (-8, 32), (-16, 30), (-10, 4), (-10, -16), (-26, -14), (-22, -22), (-8, -30)]
    P = [(cx + x * sx, cy + y * sy) for x, y in pts]
    for i in range(len(P)):
        a, b = P[i], P[(i + 1) % len(P)]; cv.line(a[0], a[1], b[0], b[1], hexc(col))
    for ang in range(0, 360, 12):
        cv.px(cx + math.cos(math.radians(ang)) * 9 * sx, cy - 48 * sy + math.sin(math.radians(ang)) * 8 * sy, hexc(col))


def d17(t, D):  # 136.96–143.27 从地上的粉笔轮廓里站起来，她拉着他的手
    cv = Canvas()
    emis = np.zeros((H, W), bool)
    base = ruins(cv, t, 60, 0.9, near=True, emis=emis)
    for i, (x, y) in enumerate(FLOWERS): flower(cv, x, y, 1.3, FCOL[i % 6])
    chalk(cv, 150, 168, 2.2, 0.32)
    up = ease(clamp(t / 1.6))
    m, a = chibi('wu', 150, 170, 32, 'sit' if up < 1 else 'give', 'wonder' if up < 1 else 'smile', t, facing=1, floor=0.95)
    ms, as_ = chibi('die', 206, 170, 32, 'take', 'joy', t, facing=-1, floor=0.95)
    flat(cv)
    cv.ellipse(280, 30, 12, 12, hexc('fff2c8')); glow(cv, 280, 30, 50, 'ffb060', 0.3)
    return cv


SHOTS = [(117.52, 123.82, d14), (123.82, 130.14, d15), (130.14, 136.96, d16), (136.96, 143.27, d17)]
