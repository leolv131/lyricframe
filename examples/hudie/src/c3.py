"""主歌 2 + 导歌 2（75.37–117.52）：他躲着；她一直在门外。光只有手机屏、门缝、她的东西。"""
from w3 import *


def phone_px(cv, x, y, w, h, on=1.0, flip=False):
    cv.rect(x - 1, y - 1, w + 2, h + 2, INK); cv.rect(x, y, w, h, hexc('1a1a22'))
    if not flip and on > 0:
        cv.rect(x + 2, y + 3, w - 4, h - 6, hexc('dfe8f4'))
        bfly(cv, x + 7, y + 9, 0.6, 0, flap=1.0)
        cv.rect(x + w - 12, y + 6, 9, 6, hexc('e8344a'))
        for i in range(3): cv.rect(x + 4, y + 18 + i * 7, w - 12 - i * 4, 4, hexc('b8d0e8'))


def b7(t, D):   # 75.37–80.42 未接来电，他把手机扣过去
    cv = Canvas()
    wx, wy, ww, wh = room(cv, t, 0.0)
    flip = t > 2.6
    m, a = chibi('wu', 96, 150, 32, 'sit', 'sad', t, facing=1, floor=0.55, tint=('6a7aa0', 0.3))
    buzz = int(t * 14) % 2 if not flip else 0
    lit2(cv, [Light(84 + buzz, 98, 'b8d8ff', 70, 0.0 if flip else 1.0), window_light(wx, wy, ww, wh, '6a7ab0', 0.4)], (0.24, 0.24, 0.32), t)
    phone_px(cv, 78 + buzz, 92, 22, 36 if not flip else 6, flip=flip)
    if not flip: glow(cv, 89, 108, 30, '8ab8ff', 0.45)
    rim(cv, m, 89, 108, 'b8d8ff', k=0.0 if flip else 0.9)
    return cv


def b8(t, D):   # 80.42–85.50 乱七八糟：被子里缩成一团，满墙乱线影子
    cv = Canvas()
    wx, wy, ww, wh = room(cv, t, 0.0)
    r = rng(8)
    pts = [(r.uniform(20, 300), r.uniform(10, 130)) for _ in range(40)]
    for i in range(len(pts) - 1):
        a, b = pts[i], pts[i + 1]
        cv.line(a[0] + math.sin(t + i) * 2, a[1], b[0], b[1] + math.cos(t + i) * 2, hexc('2a2420'))
    L = Layer()
    L.ellipse(264, 118, 40, 16, hexc('8a86a0'), INK)
    for i in range(3): L.hline(232 + i * 8, 296 - i * 8, 110 + i * 5, hexc('6a6680'))
    layer_obj(L, 0.5)
    lit2(cv, [window_light(wx, wy, ww, wh, '6a7ab0', 0.5), Light(250, 112, 'b8d8ff', 40, 0.6 + 0.3 * math.sin(t * 3))], (0.24, 0.24, 0.32), t)
    # 被子里露出的眼睛（手机光）
    if int(t * 1.3) % 3 != 2:
        for sg in (-1, 1): cv.rect(240 + sg * 6, 112, 3, 4, INK); cv.px(240 + sg * 6, 112, WHITE)
    symbol(cv, 'q', 250, 92, t)
    return cv


MAZE = ["###########################", "#.....#.........#.........#", "#.###.#.#######.#.#######.#", "#.#...#.#.....#...#.....#.#",
        "#.#.###.#.###.#####.###.#.#", "#.#.....#.#.......#.#...#.#", "#.#######.#.#####.#.#.###.#", "#.........#.....#...#.....#", "###########################"]


def b9(t, D):   # 85.50–93.68 俯拍：巷子迷宫，他和她两盏灯在里面错过
    cv = Canvas(hexc('1a1a26'))
    cs = 12; ox, oy = (W - 27 * cs) // 2 - int(t * 1.5), (H - 9 * cs) // 2 - 4
    emis = np.zeros((H, W), bool)
    for j, row in enumerate(MAZE):
        for i, ch in enumerate(row):
            x, y = ox + i * cs, oy + j * cs
            if ch == '#':
                cv.rect(x, y, cs, cs, hexc('6a6478')); cv.rect(x, y, cs, 2, hexc('8a849a'))
                if (i * 7 + j * 3) % 5 == 0 and 0 <= y + 4 < H and 0 <= x + 4 < W:
                    cv.rect(x + 4, y + 4, 3, 3, hexc('ffcf7a')); emis[y + 4:y + 7, max(0, x + 4):x + 7] = True
            else: cv.rect(x, y, cs, cs, hexc('24222e'))
    def walk(path, u):
        seg = u * (len(path) - 1); i = min(int(seg), len(path) - 2); f = seg - i
        (a, b), (c, d) = path[i], path[i + 1]
        return ox + (a + (c - a) * f) * cs + cs // 2, oy + (b + (d - b) * f) * cs + cs // 2
    u = clamp(t / D)
    hx, hy = walk([(1, 1), (1, 7), (9, 7), (9, 5), (9, 3), (13, 3), (11, 3), (11, 5), (16, 5), (16, 1)], u)
    sx, sy = walk([(25, 7), (21, 7), (21, 5), (23, 5), (23, 3), (25, 3), (25, 1), (17, 1), (17, 3), (19, 3)], u)
    lit2(cv, [Light(hx, hy, '8aa0ff', 18, 0.6), Light(sx, sy, 'ffb860', 34, 1.2)], (0.3, 0.3, 0.4), t, emissive=emis)
    cv.ellipse(hx, hy, 3, 3, hexc('969aa6'), INK); cv.px(hx, hy - 1, hexc('2a2233'))
    cv.ellipse(sx, sy, 3, 3, hexc('f7ead6'), INK); glow(cv, sx, sy, 14, 'ff9a40', 0.5); cv.px(sx + 1, sy - 2, hexc('2f8cff'))
    return cv


def corridor(cv, t, night=1.0):
    sky(cv, ['07080f', '10142a', '1a2040'], 0, 118)
    skyline(cv, 118, 8, '1a1e34', 'ffcf7a', 0.2, hmin=40, hmax=90, t=t)
    cv.rect(0, 0, W, 12, hexc('2a2e38')); cv.rect(0, 12, W, 2, INK)
    cv.rect(0, 14, 150, 136, hexc('6a6670'))
    for y in range(18, 150, 6):
        for x in range((y // 6) % 2 * 8, 150, 16): cv.hline(x, x + 12, y, hexc('605c66'))
    cv.vline(150, 14, 150, INK)
    cv.rect(150, 116, W - 150, 3, hexc('7a7a80'))
    for x in range(154, W, 9): cv.rect(x, 119, 2, 31, hexc('5a5a62'))
    cv.rect(0, 150, W, H - 150, hexc('4a4a52')); cv.hline(0, W, 150, INK)
    # 他的门
    dx, dy, dw, dh = 60, 60, 44, 90
    cv.rect(dx - 3, dy - 3, dw + 6, dh + 3, INK); cv.rect(dx, dy, dw, dh, hexc('5a4a46'))
    cv.rect(dx + dw - 6, dy + 46, 3, 5, hexc('b0a080'))
    return (dx, dy, dw, dh)


def b10(t, D):  # 93.68–98.56 她在门外敲门
    cv = Canvas()
    dx, dy, dw, dh = corridor(cv, t)
    m, a = chibi('die', 150, 150, 32, 'reach', 'hesitate' if t > 2.4 else 'smile', t, facing=-1, floor=0.95)
    knock = (t % 1.0) < 0.15 and t < 3.0
    lit2(cv, [Light(150, 110, 'ffb860', 60, 1.1), Light(dx + dw / 2, 156, 'ffcf8a', 30, 0.3)], (0.2, 0.2, 0.3), t)
    cv.rect(dx, dy + dh - 1, dw, 2, hexc('ffd890')); glow(cv, dx + dw / 2, dy + dh, 18, 'ff9a40', 0.3)
    um = umbrella(cv, 168, 60, 18, 9, col='ffcf5a', dk='e0a030'); cv.line(168, 69, 160, 112, INK)
    glow(cv, 166, 80, 30, 'ffaa40', 0.35)
    if knock:
        for i in range(3): cv.line(dx + dw + 4 + i * 3, dy + 30 - i * 4, dx + dw + 8 + i * 3, dy + 26 - i * 4, WHITE)
    rain(cv, t, n=90, seed=10, speed=160, col='6a7494', excl=lambda x, y: x < 150 and y > 14)
    return cv


def b11(t, D):  # 98.56–106.49 门上一张张便利贴、门把手上的饭；最后门缝塞进纸蝴蝶
    cv = Canvas()
    dx, dy, dw, dh = corridor(cv, t)
    k = ease(clamp(t / (D - 1.6)))
    n = int(1 + k * 26)
    lit2(cv, [Light(dx + dw / 2, dy + dh - 10, 'ffcf8a', 50, 0.4 + 0.4 * k)], (0.2, 0.2, 0.3), t)
    r = rng(5)
    cols = ['ffe08a', 'ffd0a0', 'ffc94a', 'f7ead6']
    for i in range(n):
        x = dx + 2 + r.integers(0, dw - 12); y = dy + 4 + r.integers(0, 56)
        cv.rect(x, y, 10, 9, INK); cv.rect(x + 1, y + 1, 8, 7, hexc(cols[i % 4]))
        cv.hline(x + 2, x + 6, y + 3, hexc('a08050'))
    for i in range(min(5, n // 5 + 1)):
        x = dx + dw - 10 - i * 6; y = dy + 52 + (i % 2) * 5
        cv.line(x + 3, dy + 48, x + 3, y, INK); cv.rect(x, y, 7, 10, INK); cv.rect(x + 1, y + 1, 5, 8, hexc('f0ece0'))
    glow(cv, dx + dw / 2, dy + 30, 30 + 20 * k, 'ffb050', 0.25 * k)
    # 时间：天色和天气循环（雨 → 雪 → 雨）
    if (t * 0.6) % 2 < 1: rain(cv, t, n=70, seed=11, speed=160, col='6a7494', excl=lambda x, y: x < 150 and y > 14)
    else:
        from lib import snow
        snow(cv, t, n=60, col=(220, 226, 240))
    # 门缝里的纸蝴蝶
    if t > D - 1.6:
        u = ease(clamp((t - (D - 1.6)) / 1.2))
        px_ = lerp(150, dx + dw / 2, u)
        paper_butterfly(cv, px_, dy + dh + 4, 0.8); glow(cv, px_, dy + dh + 2, 14, '3a7aff', 0.5)
    return cv


def b12(t, D):  # 106.49–112.00 他打开她的铁盒（近景）
    cv = Canvas()
    wx, wy, ww, wh = room(cv, t, 0.0)
    m, f = face('wu', 120, 34, 56, dict(eyes='down', mouth='flat', brow='sad', wet=t > 2.5), t, floor=0.6, tint=('6a7aa0', 0.25))
    k = ease(clamp((t - 0.6) / 0.8))
    bx, by = 200, 110
    lit2(cv, [Light(bx, by, 'ffcf8a', 80, 1.1 * k + 0.1), window_light(wx, wy, ww, wh, '6a7ab0', 0.3)], (0.24, 0.24, 0.32), t)
    cv.rect(bx - 30, by, 60, 30, INK); cv.rect(bx - 29, by + 1, 58, 28, hexc('8a9aa8'))
    cv.rect(bx - 26, by + 3, 52, 24, hexc('ffe8b0') if k > 0.3 else hexc('5a6a7a'))
    for i in range(3):
        cv.line(bx - 16 + i * 12, by + 24, bx - 12 + i * 10, by + 8, hexc('8a7a50')); cv.ellipse(bx - 12 + i * 10, by + 7, 3, 3, hexc('d87a8a'))
    lid = int(30 * (1 - k)); cv.rect(bx - 31, by - lid, 62, 4, hexc('a8b8c4'))
    glow(cv, bx, by + 10, 40 * k, 'ffb050', 0.5 * k)
    paper_butterfly(cv, 250, 150, 1.0); glow(cv, 250, 150, 16, '3a7aff', 0.5)
    rim(cv, m, bx, by, 'ffcf8a', k=k)
    if t > 2.0: symbol(cv, 'q', 150, 22, t)
    return cv


def b13(t, D):  # 112.00–117.52 窗外吊下来：一碗面、一条围巾、一盏小灯 → 灯把房间照亮
    cv = Canvas()
    wx, wy, ww, wh = room(cv, t, 0.0)
    m, a = chibi('wu', 190, 150, 30, 'sit', 'wonder' if t > 1 else 'sad', t, facing=-1, floor=0.6)
    step = D / 3.0
    items = []
    for i in range(3):
        if t >= i * step:
            k = ease(clamp((t - i * step) / 0.7))
            items.append((i, wx + 12 + i * 22, int(wy - 10 + k * (40 + i * 6))))
    lampk = clamp((t - 2 * step) / 0.6)
    lit2(cv, [window_light(wx, wy, ww, wh, '6a7ab0', 0.45), Light(wx + 56, wy + 50, 'ffcf8a', 120, 1.2 * lampk)], (0.18 + 0.15 * lampk, 0.17 + 0.12 * lampk, 0.22), t)
    for (i, bx, by) in items:
        cv.vline(bx + 7, 0, by, INK); cv.rect(bx, by, 16, 10, INK); cv.rect(bx + 1, by + 1, 14, 8, hexc('d8a860'))
        if i == 0:
            cv.ellipse(bx + 8, by - 1, 7, 3, hexc('f0ece0'), INK)
            for j in range(3): cv.px(bx + 4 + j * 3, by - 5 - int(math.sin(t * 6 + j)), WHITE)
        elif i == 1: cv.rect(bx + 2, by - 4, 12, 4, hexc('e8344a')); cv.rect(bx + 12, by - 4, 3, 12, hexc('e8344a'))
        else:
            cv.ellipse(bx + 8, by - 3, 4, 4, hexc('ffe39a'), INK); glow(cv, bx + 8, by - 3, 30 * lampk + 4, 'ffb050', 0.6)
    rim(cv, m, wx + 56, wy + 50, 'ffcf8a', k=lampk)
    return cv


SHOTS = [(75.37, 80.42, b7), (80.42, 85.50, b8), (85.50, 93.68, b9), (93.68, 98.56, b10), (98.56, 106.49, b11), (106.49, 112.00, b12), (112.00, 117.52, b13)]
