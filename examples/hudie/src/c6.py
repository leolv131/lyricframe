"""终副歌（192.12–246.68）+ 尾奏（246.68–279.2）：全彩白天 → 黄昏收摊 → 夜 → 谢幕。"""
from w3 import *
from w3 import _wu, _die
from lib import flower_shop, flower_tree, confetti


def rainbow(cv, cx=160, cy=130, rx=150, ry=90, k=1.0):
    for i, c in enumerate(['ff6a6a', 'ffa24a', 'ffe06a', '7ad46a', '6ab4ff', '9a7aff']):
        for a in range(0, 181):
            if a > 180 * k: break
            ar = math.radians(180 - a)
            x = cx + math.cos(ar) * (rx - i * 3); y = cy - math.sin(ar) * (ry - i * 3)
            if 0 <= y < H and 0 <= x < W and DITH[int(y), int(x)] < 0.6: cv.px(x, y, hexc(c))


def f26(t, D):  # 192.12–198.92 天台：雨停，彩虹，全城一下子亮成彩色
    cv = Canvas(); emis = np.zeros((H, W), bool)
    k = ease(clamp(t / 1.2))
    top = rooftop(cv, t, 0.35 + 0.65 * k, emis=emis)
    rainbow(cv, k=ease(clamp((t - 0.6) / 1.8)))
    m1, a1 = chibi('wu', 146, top, 32, 'cheer' if t > 1.0 else 'stand', 'joy', t, floor=0.95, apron=True)
    m2, a2 = chibi('die', 180, top, 32, 'cheer' if t > 1.0 else 'stand', 'joy', t, floor=0.95)
    lit2(cv, [], (0.5 + 0.5 * k, 0.5 + 0.5 * k, 0.55 + 0.45 * k), t, emissive=emis)
    if t < 1.2: rain(cv, t, n=int(140 * (1 - k)), seed=26, speed=170, col='8a94b0')
    for i in range(6):
        bx = (i * 61 + t * 30) % W; by = 40 + (i * 23) % 50
        bfly(cv, bx, by, 1, t + i * 0.2)
    return cv


def f27(t, D):  # 198.92–205.14 和片头同一个废墟：清出空地，上百只蓝蝴蝶飞过
    cv = Canvas()
    base = ruins(cv, t, 20 + t * 4, 1.0, cleared=1.0)
    cv.rect(70, base - 2, 180, 14, hexc('a8c870'))
    for i in range(20): cv.vline(76 + i * 9, base - 4, base - 2, hexc('6aba5a'))
    m1, a1 = chibi('wu', 140, base + 14, 22, 'cheer', 'joy', t, floor=1.0, apron=True)
    m2, a2 = chibi('die', 166, base + 14, 22, 'wave', 'joy', t, floor=1.0)
    flat(cv)
    cv.ellipse(280, 30, 12, 12, hexc('fff2c8')); glow(cv, 280, 30, 50, 'ffb060', 0.3)
    r = rng(59)
    for i in range(55):
        ph = r.uniform(0, 1); sp = r.uniform(0.7, 1.3); yy = r.uniform(14, 120)
        x = ((ph * (W + 80) + t * 40 * sp) % (W + 80)) - 40
        y = yy + math.sin(t * 2 * sp + i) * 6
        bfly(cv, x, y, 1 if i % 7 else 2, t * sp + i * 0.1, speed=4 + (i % 3))
    return cv


def f28(t, D):  # 205.14–211.52 白天的巷子：他把"遗弃"纸箱压扁扔进回收箱，撕下的旧告示变成蝴蝶
    cv = Canvas()
    alley(cv, t, 1.0)
    cv.rect(236, 128, 40, 40, INK); cv.rect(237, 129, 38, 38, hexc('3a8a5a')); cv.rect(234, 124, 44, 6, hexc('2a6a4a'))
    throw = ease(clamp((t - 1.6) / 0.8))
    m, a = chibi('wu', 150, 170, 32, 'clap' if throw <= 0 else 'reach', 'happy', t, facing=1, floor=1.0, apron=True)
    flat(cv)
    if throw < 1:
        flatk = ease(clamp(t / 1.2))
        bx = int(lerp(158, 244, throw)); by = int(lerp(140, 112, math.sin(throw * math.pi) * 0.6 + throw * 0.4))
        h = max(4, int(26 * (1 - flatk)))
        cv.rect(bx - 1, by + 26 - h - 1, 36, h + 2, INK); cv.rect(bx, by + 26 - h, 34, h, hexc('b0906a'))
    # 墙上的旧告示 → 撕下变蝴蝶
    r = rng(28)
    for i in range(8):
        u = clamp((t - 3.0 - i * 0.12) / 2.5)
        x0, y0 = 40 + (i % 4) * 18, 70 + (i // 4) * 16
        if u <= 0: cv.rect(x0, y0, 12, 10, hexc('e8e2d4')); cv.hline(x0 + 2, x0 + 9, y0 + 3, hexc('a0a0a0'))
        else: bfly(cv, x0 + u * 120 + r.uniform(-10, 10) * u, y0 - u * 60, 1, t + i * 0.2)
    return cv


def shop_scene(cv, t, night=0.0, sky_cols=None):
    sky(cv, sky_cols or ['6ab4f0', '8ccaf6', 'b8e0fa', 'e8f4fa'], 0, 120)
    skyline(cv, 120, 13, lerpc('c8b8c8', '2a2a48', night), 'ffe08a', 0.2 + 0.4 * night, hmin=30, hmax=70, t=t)
    cv.rect(0, 120, W, H - 120, hexc(lerpc('d8c8b0', '4a4452', night))); cv.hline(0, W, 120, INK)
    for x in range(0, W, 12): cv.vline(x, 121, H, hexc(lerpc('c8b8a0', '3e3a46', night)))
    flower_shop(cv, t, night=1.0 if night > 0.3 else 0.0)
    flower_tree(cv, 64, 120)


def f29(t, D):  # 211.58–218.32 小伍花店在废墟原址重新开张（长镜头，礼花）
    cv = Canvas()
    shop_scene(cv, t)
    m1, a1 = chibi('wu', 140, 150, 26, 'cheer', 'joy', t, floor=1.0, apron=True)
    m2, a2 = chibi('die', 178, 150, 26, 'clap', 'joy', t, floor=1.0)
    flat(cv)
    confetti(cv, t, seed=3, n=60)
    for i in range(9):
        bx = (30 + i * 37 + t * 20 * (1 + i % 3)) % (W + 20) - 10; by = 30 + (i * 23) % 60 + math.sin(t * 2 + i) * 6
        bfly(cv, bx, by, 1 if i % 3 else 2, t + i * 0.13, speed=4 + i % 3)
    return cv


def f30(t, D):  # 218.32–224.60 他双手递花鞠躬，她接过笑了，他脸红
    cv = Canvas()
    shop_scene(cv, t)
    bow = ease(clamp((t - 0.8) / 0.5)) * (1 - ease(clamp((t - 2.6) / 0.5)))
    m1, a1 = chibi('wu', 140, 170, 36, 'give', 'closed' if bow > 0.5 else ('shy' if t > 3 else 'smile'), t, facing=1, floor=1.0, apron=True)
    m2, a2 = chibi('die', 200, 170, 36, 'take', 'joy' if t > 1.6 else 'surprise', t, facing=-1, floor=1.0)
    flat(cv)
    bx, by = 170, 128 + int(bow * 6)
    cv.poly([(bx - 6, by + 10), (bx + 6, by + 10), (bx + 2, by + 24), (bx - 2, by + 24)], hexc('f0e0c0'))
    for j, c in enumerate(['ff6a8a', 'ffd35a', 'ff9a4a', 'f6f2e6', 'c87aff', 'ff8aa8']):
        cv.ellipse(bx - 8 + (j % 3) * 8, by + 2 + (j // 3) * 6, 4, 4, hexc(c), INK)
    if t > 3: symbol(cv, 'heart', a1['cx'] + 12, a1['top'] - 6, t)
    return cv


def f31(t, D):  # 224.60–231.10 店里的镜子：镜中完整、彩色的他，对自己点点头
    cv = Canvas(hexc('f4ead8'))
    for i in range(6): cv.rect(10 + i * 50, 20, 30, 140, hexc('e8dcc8'))
    mx, my, mw, mh = 170, 16, 120, 150
    cv.rrect(mx - 4, my - 4, mw + 8, mh + 8, 10, hexc('b08a5a'), INK); cv.rrect(mx, my, mw, mh, 8, hexc('dceef4'))
    nod = int(math.sin(clamp((t - 2.0) / 0.6) * math.pi) * 3) if t > 2.0 else 0
    sub = Canvas((255, 0, 255))
    from w3 import face as _f
    L = Layer(); L.ellipse(mx + mw // 2, my + 34 + nod + 52 * 1.6, 52 * 0.95, 52 * 0.62, hexc('969aa6'), INK)
    from chars import head
    f = head(L, 'wu', mx + mw // 2, my + 34 + nod, 52, dict(eyes='happy' if t > 2.0 else 'open', mouth='smile'), t=t)
    L.rect(mx + mw // 2 - 22, my + 34 + nod + 66, 44, 40, hexc('4f9a5c'))
    mk = L.mask() & (XX > mx) & (XX < mx + mw) & (YY > my) & (YY < my + mh)
    cv.a[mk] = L.a[mk]
    for i in range(3): cv.line(mx + 10 + i * 30, my + 6, mx + 30 + i * 30, my + 40, WHITE)
    m, a = chibi('wu', 100, 200, 60, 'arms_down', 'normal', t, back=True, floor=1.0)
    flat(cv)
    if t > 2.6: symbol(cv, 'sparkle', mx + mw // 2 + 30, my + 30, t)
    return cv


def f32(t, D):  # 231.10–237.68 蓝蝴蝶戒指，她捂嘴点头
    cv = Canvas()
    sky(cv, ['ffcf8a', 'ffe8c0'], 0, H)
    nod = int(abs(math.sin(clamp((t - 1.6) / 1.2) * math.pi * 2)) * 3) if t > 1.6 else 0
    m, f = face('die', 200, 30 + nod, 70, dict(eyes='happy' if t > 1.4 else 'wide', mouth='none', blush=True, tear=t > 2.0), t, floor=1.0)
    flat(cv)
    cv.ellipse(200, 30 + nod + 62, 12, 9, PAL['skin'], INK)
    mitt(cv, 90, 120, 1, hexc('969aa6'), (-30, 190))
    cv.rect(96, 100, 30, 18, INK); cv.rect(97, 101, 28, 16, hexc('a8283a')); cv.rect(97, 92, 28, 9, hexc('8a1e2a'))
    cv.ellipse(111, 104, 5, 3, hexc('d8d8e0'), INK)
    bfly(cv, 111, 100, 1, 0, flap=1.0, sparkle=int(t * 3) % 2 == 0)
    glow(cv, 111, 100, 20, '3a7aff', 0.4)
    return cv


def f33(t, D):  # 237.68–246.68 傍晚，花店亮灯，两人坐在窗边；镜头慢慢拉远到整条街
    cv = Canvas()
    night = ease(clamp(t / D)) * 0.5
    shop_scene(cv, t, night=night + 0.3, sky_cols=['8a6aa0', 'ff9e6b', 'ffcf8a'])
    m1, a1 = chibi('wu', 150, 112, 18, 'sit', 'smile', t, floor=0.95, apron=True)
    m2, a2 = chibi('die', 170, 112, 18, 'sit', 'joy', t, floor=0.95)
    lit2(cv, [Light(160, 90, 'ffd890', 120, 1.0), Light(250, 60, 'ffb070', 200, 0.4)], (0.6 - night * 0.3, 0.5 - night * 0.25, 0.55 - night * 0.2), t)
    glow(cv, 160, 90, 60, 'ffb050', 0.35)
    for i in range(4):
        ang = t * 1.5 + i * 1.57
        bfly(cv, 250 + math.cos(ang) * 14, 70 + math.sin(ang * 1.3) * 8, 1, t + i * 0.2)
    return cv


# ---------------------------------------------------------------- 尾奏
def g34(t, D):  # 246.68–256.00 黄昏收摊，灯亮了，蝴蝶在灯下飞
    cv = Canvas()
    night = 0.4 + 0.4 * ease(clamp(t / D))
    shop_scene(cv, t, night=night, sky_cols=[lerpc('8a6aa0', '1e2240', night), lerpc('ff9e6b', '3a3a6a', night), lerpc('ffcf8a', '5a4a7a', night)])
    x = 110 + int(math.sin(t * 0.7) * 20)
    m1, a1 = chibi('wu', x, 140, 24, 'clap', 'smile', t, floor=0.95, apron=True)
    m2, a2 = chibi('die', 196, 140, 24, 'reach', 'smile', t, floor=0.95)
    lit2(cv, [Light(160, 90, 'ffd890', 110, 1.0), Light(250, 60, 'ffd890', 70, 0.8)], (0.5 - 0.25 * night, 0.45 - 0.2 * night, 0.55 - 0.15 * night), t)
    cv.rect(250, 60, 3, 60, INK); cv.ellipse(251, 58, 5, 4, hexc('ffe39a'), INK); glow(cv, 251, 60, 30, 'ffb050', 0.5)
    glow(cv, 160, 90, 50, 'ffb050', 0.3)
    for i in range(4):
        ang = t * 1.5 + i * 1.57
        bfly(cv, 251 + math.cos(ang) * 14, 66 + math.sin(ang * 1.3) * 8, 1, t + i * 0.2)
    return cv


def g35(t, D):  # 256.00–268.00 入夜，片尾署名
    cv = Canvas(); emis = np.zeros((H, W), bool)
    shop_scene(cv, t, night=1.0, sky_cols=['10142a', '1e2240', '34304a'])
    stars(cv, t, n=50, y1=60, emis=emis)
    m1, a1 = chibi('wu', 150, 140, 24, 'stand', 'smile', t, floor=0.9, apron=True)
    m2, a2 = chibi('die', 176, 140, 24, 'stand', 'joy', t, floor=0.9)
    lit2(cv, [Light(160, 90, 'ffd890', 110, 1.0), Light(250, 60, 'ffd890', 70, 0.8)], (0.3, 0.3, 0.42), t, emissive=emis)
    cv.rect(250, 60, 3, 60, INK); cv.ellipse(251, 58, 5, 4, hexc('ffe39a'), INK); glow(cv, 251, 60, 30, 'ffb050', 0.5)
    glow(cv, 160, 90, 50, 'ffb050', 0.3)
    cv.rect(160, 120, 6, 3, PAL['skin'])
    fade_in_text(cv, 160, 4, '原唱 · 陶喆', clamp((t - 1.0) / 1.5) * (1 - clamp((t - (D - 1.0)) / 1.0)), col='fff6e0')
    return cv


def g36(t, D):  # 268.00–279.20 一只蓝蝴蝶飞向镜头，翅膀铺满画面 → THANKS FOR WATCHING → 淡出
    cv = Canvas(hexc('10142a'))
    r = rng(72)
    for i in range(60):
        x, y = r.uniform(0, W), r.uniform(0, H)
        if (t * 2 + i) % 3 > 0.5: cv.px(x, y, hexc('fff4c0'))
    k = ease(clamp(t / 3.0))
    s = 1 + k * 18
    bfly(cv, 160, 90 + (1 - k) * 30, s, t, speed=1.2 if k < 1 else 0.6)
    glow(cv, 160, 90, 30 + 120 * k, '3a7aff', 0.25)
    w = clamp((t - 3.0) / 1.0)
    if w > 0:
        m = Canvas((255, 0, 255))
        title_text(m, 'THANKS FOR WATCHING', 160, 84, hexc('fff6e0'), size=16, outline=INK)
        title_text(m, '蝴 蝶', 160, 106, hexc('8fd6ff'), size=12, outline=INK)
        mm = np.any(m.a != np.array([255, 0, 255], np.uint8), axis=2)
        cv.a[mm & (DITH < w)] = m.a[mm & (DITH < w)]
    fk = clamp((t - (D - 2.0)) / 2.0)
    if fk > 0: cv.a[DITH < fk] = (8, 8, 12)
    return cv


SHOTS = [(192.12, 198.92, f26), (198.92, 205.14, f27), (205.14, 211.58, f28), (211.58, 218.32, f29), (218.32, 224.60, f30),
         (224.60, 231.10, f31), (231.10, 237.68, f32), (237.68, 246.68, f33), (246.68, 256.00, g34), (256.00, 268.00, g35), (268.00, 279.20, g36)]
