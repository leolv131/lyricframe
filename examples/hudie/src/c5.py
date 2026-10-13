"""桥段（143.27–192.12）：黄昏天台、她的眼睛、围裙、雪夜围巾、回忆、地狱到天堂。"""
from w3 import *
from w3 import _wu, _die


def e18(t, D):  # 143.27–149.84 黄昏天台，他悄悄往她那边挪
    cv = Canvas(); emis = np.zeros((H, W), bool)
    top = rooftop(cv, t, 0.5, emis=emis, dusk=True)
    cv.ellipse(250, 118, 16, 16, hexc('ffe08a')); glow(cv, 250, 118, 60, 'ff9a60', 0.4)
    scoot = ease(clamp((t - 2.0) / 0.5)) * 10
    m, a = chibi('wu', 130 + scoot, top - 4, 30, 'sit', 'shy' if scoot > 5 else 'normal', t, facing=1, floor=0.85)
    ms, as_ = chibi('die', 176, top - 4, 30, 'sit', 'smile', t, facing=-1, floor=0.9)
    lit2(cv, [Light(250, 118, 'ffb070', 260, 0.7)], (0.55, 0.45, 0.48), t, emissive=emis)
    rim(cv, m, 250, 118, 'ffd8a0', 0.9); rim(cv, ms, 250, 118, 'ffd8a0', 0.9)
    if scoot > 8: symbol(cv, 'heart', 152, a['top'] - 8, t)
    for i in range(5):   # 鸟
        x = (i * 40 + t * 18) % (W + 40) - 20; y = 40 + (i % 3) * 8
        cv.px(x, y, hexc('3a2030')); cv.px(x - 1, y - int(t * 8 + i) % 2, hexc('3a2030')); cv.px(x + 1, y - int(t * 8 + i) % 2, hexc('3a2030'))
    return cv


def eye(cv, cx, cy, w, h, refl_k=0.0, t=0.0):
    from px import rrect_mask
    from px import ell_mask
    m = ell_mask(w / 2, h / 2)
    cv.mask_fill(dilate(m), INK, cx - w // 2 - 1, cy - h // 2 - 1); cv.mask_fill(m, WHITE, cx - w // 2, cy - h // 2)
    ir = h * 0.46
    cv.ellipse(cx, cy + 2, ir, ir, hexc('6a3a2a'), INK); cv.ellipse(cx, cy + 2, ir * 0.62, ir * 0.62, hexc('2a1410'))
    if refl_k > 0 and ir > 18:
        L = Canvas((255, 0, 255)); Hh = int(ir * 0.5)
        _wu(L, int(cx), int(cy + 2 + ir * 0.55), Hh, 'wave', 'joy', t=t)
        mk = np.any(L.a != np.array([255, 0, 255], np.uint8), axis=2)
        mk &= ((XX - cx) ** 2 + (YY - cy - 2) ** 2) < (ir * 0.58) ** 2
        mk &= DITH < refl_k
        cv.a[mk] = L.a[mk]
    cv.ellipse(cx + ir * 0.4, cy - ir * 0.3, ir * 0.2, ir * 0.2, WHITE)
    cv.rect(cx - w // 2 + 2, cy - h // 2 - 4, w - 4, 5, INK)


def e19(t, D):  # 149.84–156.36 她的眼睛 → 推进瞳孔，里面是完整、彩色、在笑的他
    cv = Canvas(PAL['skin'])
    k = ease(clamp((t - 1.6) / (D - 2.0)))
    if t < 1.6:
        cv.rect(0, 0, W, 26, PAL['hair'])
        for x in range(0, W, 18): cv.rect(x, 22, 10, 10, PAL['hair'])
        eye(cv, 90, 96, 90, 70); eye(cv, 236, 96, 90, 70)
        bfly(cv, 300, 14, 3, 0, flap=1.0, tilt=0.25)
    else:
        w = int(110 + k * 380); h = int(w * 0.78)
        eye(cv, 160, 90, w, h, refl_k=clamp((k - 0.2) / 0.4), t=t)
    cv.tint(hexc('ff9e6b'), 0.12)
    return cv


def e20(t, D):  # 156.36–163.16 她递回旧围裙，他系上 → 夕阳把他的影子投成一对翅膀
    cv = Canvas(); emis = np.zeros((H, W), bool)
    top = rooftop(cv, t, 0.5, emis=emis, dusk=True)
    cv.rect(70, top - 80, 180, 74, hexc('8a6a6a'))   # 水箱房的墙
    for y in range(top - 76, top - 6, 8): cv.hline(70, 250, y, hexc('7a5a5a'))
    tie = t > 2.4
    k = ease(clamp((t - 2.6) / 1.2))
    if k > 0:   # 墙上的翅膀影子
        S = Canvas((255, 0, 255)); bfly(S, 150, top - 46, 8, 0, flap=max(0.2, k), col=(0, 0, 0), hi=(0, 0, 0), dk=(0, 0, 0))
        mk = np.any(S.a != np.array([255, 0, 255], np.uint8), axis=2) & (DITH < 0.65)
        mk[:top - 80] = False
        cv.a[mk] = (np.array(cv.a[mk], np.float32) * 0.55).astype(np.uint8)
    m, a = chibi('wu', 150, top, 34, 'arms_down' if tie else 'take', 'smile' if tie else 'wonder', t, facing=1, floor=0.9, apron=t > 2.2)
    ms, as_ = chibi('die', 200, top, 32, 'give' if t < 2.2 else 'clap', 'smile' if t < 2.2 else 'joy', t, facing=-1, floor=0.9)
    lit2(cv, [Light(300, 110, 'ffb070', 260, 0.7)], (0.55, 0.45, 0.48), t, emissive=emis)
    if t < 2.2:
        k2 = ease(clamp(t / 1.4)); ax = int(lerp(186, 164, k2))
        cv.rect(ax - 1, 112, 18, 10, INK); cv.rect(ax, 113, 16, 8, hexc('4f9a5c')); cv.px(ax + 8, 116, hexc('ff8aa8'))
    rim(cv, m, 300, 110, 'ffd8a0', 0.9)
    return cv


def e21(t, D):  # 163.16–169.74 雪夜，路人都缩着，他俩共用一条长围巾
    cv = Canvas()
    wins = alley(cv, t, 0.0, snow_=True)
    x = 110 + t * 8
    from lib import npc, snow, scarf_between
    for i in range(3):
        nx = W + 20 - ((t * 26 + i * 120) % (W + 60))
        L = Layer(); npc(L, 'npc' if i % 2 else 'npc_g', nx, 178, 22, t + i, phone=False, facing=-1); layer_obj(L, 0.3)
    m, a = chibi('wu', x, 170, 30, 'walk', 'smile', t, facing=1, floor=0.9)
    ms, as_ = chibi('die', x + 34, 170, 30, 'walk', 'joy', t + 0.06, facing=1, floor=0.95)
    lit2(cv, [Light(x + 17, 128, 'ffcf8a', 70, 1.1), Light(170, 100, 'ffb870', 40, 0.6)], (0.24, 0.25, 0.36), t)
    alley_emissive(cv, wins, 1.0)
    fa, fb = a['f'], as_['f']
    scarf_between(cv, (fa['cx'] + 4, fa['top_body'] + 1), (fb['cx'] - 4, fb['top_body'] + 1))
    cv.rect(fa['cx'] - 6, fa['top_body'], 12, 3, hexc('e8344a')); cv.rect(fb['cx'] - 6, fb['top_body'], 12, 3, hexc('e8344a'))
    glow(cv, x + 17, 140, 40, 'ff9a40', 0.3)
    snow(cv, t, n=170, col=(232, 236, 248))
    return cv


def e22(t, D):  # 169.74–172.12 十指相扣（特写）
    cv = Canvas()
    sky(cv, ['2a3050', '3a4060'], 0, H)
    from lib import snow
    k = ease(clamp(t / 0.8))
    L = Layer()
    mitt(L, int(lerp(60, 140, k)), 100, 1, hexc('969aa6'), (-30, 170))
    mitt(L, int(lerp(260, 180, k)), 96, -1, hexc('f7ead6'), (W + 30, 170))
    layer_obj(L, 0.9)
    lit2(cv, [Light(160, 100, 'ffcf8a', 100, 0.9)], (0.4, 0.4, 0.5), t)
    if k >= 1:
        for i in range(3): cv.rect(150 + i * 8, 86, 4, 18, PAL['skin'] if i % 2 else hexc('f0b890'))
        glow(cv, 160, 96, 50, 'ff9a40', 0.3)
    cv.rect(220, 140, 60, 18, hexc('e8344a'))
    snow(cv, t, n=60, speed=10, col=(232, 236, 248))
    return cv


def e23(t, D):  # 172.12–178.56 回忆（灰）：他喝醉了，她背着他一步一步走
    cv = Canvas()
    wins = alley(cv, t, 0.0)
    step = int(t / 0.82); bob = step % 2
    x = 230 - t * 16
    m1, a1 = chibi('wu', x + 8, 168 - 20 - bob, 28, 'reach', 'closed', t, facing=-1, floor=0.7, tint=('8a8a90', 0.7))
    m2, a2 = chibi('die', x, 168 - bob, 30, 'hand_chest', dict(eyes='open', mouth='flat', brow='worry'), t, floor=0.8, tint=('8a8a90', 0.7))
    lit2(cv, [Light(150, 74, 'e0e0e8', 90, 0.9)], (0.22, 0.22, 0.26), t)
    streetlamp(cv, 150, 70, 168, True, t, col='e8e8e8')
    symbol(cv, 'sweat', a2['cx'] + 14, a2['top'] - 6, t)
    g = cv.a.astype(np.float32).mean(2, keepdims=True)
    cv.a = (cv.a * 0.25 + g * 0.75).astype(np.uint8)    # 回忆：去色
    return cv


def e24(t, D):  # 178.56–182.02 同一把破伞下，两个人都淋湿了，脸上同款创可贴
    cv = Canvas()
    sky(cv, ['2a2e40', '3a3e52'], 0, H)
    m1, f1 = face('wu', 112, 66, 56, dict(eyes='happy', mouth='smile'), t, floor=0.85)
    m2, f2 = face('die', 210, 68, 56, dict(eyes='happy', mouth='smile', blush=True), t, floor=0.9)
    lit2(cv, [Light(160, 40, 'ffcf8a', 160, 0.7)], (0.35, 0.36, 0.46), t)
    bandaid(cv, int(210 + f2['Wh'] * 0.26), 68 + int(56 * 0.74), 2)
    umbrella(cv, 160, 4, 124, 34, col='8a8e9a', dk='6a6e7a')
    cv.poly([(110, 28), (140, 38), (120, 42)], hexc('2a2e40')); cv.poly([(200, 24), (226, 32), (210, 38)], hexc('2a2e40'))
    rain(cv, t, n=70, seed=24, speed=150, col='8a94b0', excl=lambda x, y: 36 < x < 284 and y < 120 and not (110 < x < 140 or 200 < x < 226))
    for (x, y) in [(100, 80), (128, 90), (200, 84), (226, 92)]:
        cv.rect(x, y + int(t * 20) % 20, 1, 3, hexc('8fd8ff'))
    return cv


def e25(t, D):  # 182.02–187.00 老电梯从暗红地底往上升，每拍掠过一层
    cv = Canvas()
    k = clamp(t / D)
    sky(cv, [lerpc('1a0408', '3a1a18', k), lerpc('5a1e2a', 'a86a4a', k)], 0, H)
    off = int((t / 0.405) * 40) % 60
    for y in range(-60, H + 60, 60):
        yy = y + off
        cv.rect(0, yy, W, 6, hexc(lerpc('3a1018', '8a5a4a', k))); cv.rect(0, yy + 6, W, 2, INK)
        for x in range(20, W, 70): cv.rect(x, yy - 30, 16, 20, hexc(lerpc('ff5a3a', 'ffcf8a', k)))
    cv.rect(100, 30, 120, 130, INK); cv.rect(102, 32, 116, 126, hexc(lerpc('2a1418', '5a4038', k)))
    m1, a1 = chibi('wu', 140, 150, 30, 'stand', 'normal', t, floor=0.85, apron=True)
    m2, a2 = chibi('die', 180, 150, 30, 'stand', 'smile', t, floor=0.9)
    lit2(cv, [Light(160, 20, 'ff7a4a', 140, 0.8), Light(160, 170, 'ff4a2a', 100, 0.6 * (1 - k))], (0.35, 0.25, 0.25), t)
    for x in range(104, 218, 8): cv.vline(x, 32, 158, hexc(lerpc('6a4a3a', 'c8a070', k)))
    cv.rect(156, 100, 8, 4, PAL['skin'])
    return cv


def e26(t, D):  # 187.00–192.12 冲出云层：金色云海，两人站在天台边
    cv = Canvas()
    sky(cv, ['ffb86a', 'ffe08a', 'fff4d0'], 0, H)
    cv.ellipse(160, 60, 30, 30, hexc('fff8e0')); glow(cv, 160, 60, 90, 'ffd070', 0.4)
    for i in range(16):
        ang = math.radians(i * 22.5 + t * 10)
        for r_ in range(34, 200, 2):
            x = 160 + math.cos(ang) * r_; y = 60 + math.sin(ang) * r_
            if 0 <= int(y) < H and 0 <= int(x) < W and DITH[int(y), int(x)] < 0.15: cv.px(x, y, hexc('fff0b0'))
    up = ease(clamp(t / 1.2)); cy = int(200 - up * 70)
    r = rng(2)
    for i in range(18):
        x = i * 20 - 10; rr = r.uniform(18, 30)
        cv.ellipse(x, cy - r.uniform(0, 10), rr, rr * 0.6, hexc('fff4e0'), hexc('f0d8a8'))
    cv.rect(0, cy, W, H - cy, hexc('fff4e0'))
    ry = cy - 6
    cv.rect(90, ry, 140, 8, hexc('c8a880'))
    m1, a1 = chibi('wu', 140, ry, 28, 'stand' if t < 2 else 'cheer', 'joy', t, floor=1.0, apron=True)
    m2, a2 = chibi('die', 180, ry, 28, 'stand' if t < 2 else 'cheer', 'joy', t, floor=1.0)
    flat(cv)
    for i in range(4):
        bx = 60 + i * 60 + math.sin(t + i) * 10; by = 40 + (i * 17) % 40
        bfly(cv, bx, by, 1, t + i * 0.2)
    return cv


SHOTS = [(143.27, 149.84, e18), (149.84, 156.36, e19), (156.36, 163.16, e20), (163.16, 169.74, e21), (169.74, 172.12, e22),
         (172.12, 178.56, e23), (178.56, 182.02, e24), (182.02, 187.00, e25), (187.00, 192.12, e26)]
