"""主歌 1 + 导歌 1（0–38.41）：深夜、冷光，他一个人；越往后越暗、越透明。"""
from w3 import *


def a1(t, D):   # 0.00–6.44 雨夜巷子，纸箱，坏路灯；片头署名
    cv = Canvas()
    wins = alley(cv, t, 0.0)
    cv.rect(30, 150, 50, 30, hexc('3a3644'))
    # 纸箱
    bx, by = 70, 134
    cv.rect(bx - 1, by - 1, 44, 34, INK); cv.rect(bx, by, 42, 32, hexc('b0906a')); cv.rect(bx, by, 42, 4, hexc('8a6e50'))
    cv.poly([(bx, by), (bx - 8, by - 9), (bx + 14, by - 6), (bx + 14, by)], hexc('9a7c5a'))
    m, a = chibi('wu', bx + 22, by + 12, 24, 'sit', 'sad', t, floor=0.6, tint=('6a7aa0', 0.45), alpha=0.85)
    cv.rect(bx - 1, by + 10, 44, 23, INK); cv.rect(bx, by + 11, 42, 21, hexc('b0906a'))
    lamp_on = math.sin(t * 7.3 + 60) <= 0.6
    lit2(cv, [Light(60, 40, '8aa0ff', 70, 0.55 if lamp_on else 0.1), Light(170, 100, 'ffb870', 40, 0.6)], (0.16, 0.17, 0.27), t)
    alley_emissive(cv, wins, 1.0)
    streetlamp(cv, 60, 36, 150, True, t, flick=True, col='c8d0ff')
    rim(cv, m, 60, 40, '8a9ad8', k=0.5 if lamp_on else 0.1)
    rain(cv, t, n=190, seed=11, speed=170, col='6a7494')
    fade_in_text(cv, 40, 6, '原唱 · 陶喆', clamp((t - 0.4) / 0.8) * (1 - clamp((t - (D - 0.8)) / 0.8)))
    return cv


def a2(t, D):   # 6.44–14.74 废墟荒野，伤兵独行
    cv = Canvas(); emis = np.zeros((H, W), bool)
    pan = t * 5
    base = ruins(cv, t, pan, 0.0, emis=emis)
    x = 70 + t * 14
    m, a = chibi('wu', x, base + 6, 30, 'walk', 'sad', t * 0.6, facing=1, floor=0.6, tint=('6a7aa0', 0.35))
    f = a['f']
    # 断伞拄地 + 头上绷带
    tw = Layer(); tw.line(a['hand'][0], a['hand'][1], a['hand'][0] + 5, base + 8, INK); tw.rect(f['cx'] - f['Wh'] // 2, f['top'] + 3, f['Wh'], 3, hexc('e8e4dc'))
    layer_obj(tw, 0.5)
    # 风滚草
    tx = -20 + t * 46; ty = base + 6 - abs(math.sin(t * 5)) * 6
    for ang in range(0, 360, 30):
        cv.line(tx, ty, tx + math.cos(math.radians(ang + t * 300)) * 6, ty + math.sin(math.radians(ang + t * 300)) * 5, hexc('5a4a40'))
    rubble_fg(cv, pan * 1.0, seed=5)
    lit2(cv, [Light(252, 38, 'b8c4ff', 200, 0.5)], (0.26, 0.28, 0.42), t, emissive=emis)
    for i in range(4):
        x0 = (i * 100 + t * 3) % (W + 80) - 40
        cv.ellipse(x0, 30 + i * 9, 30, 4, hexc('1a1e3a'))
    moon(cv, 252, 38)
    rim(cv, m, 252, 38, 'b8c4ff', k=0.6)
    rain(cv, t, n=80, seed=12, speed=150, col='4a5474')
    return cv


def a3(t, D):   # 14.74–19.70 房间窗前：玻璃里照不出他
    cv = Canvas()
    wx, wy, ww, wh = room(cv, t, 0.0)
    m, a = chibi('wu', 186, 150, 32, 'stand', 'wonder' if t > 1.2 else 'sad', t, facing=1, floor=0.65, back=False, tint=('6a7aa0', 0.45), alpha=0.85 - 0.2 * clamp(t / D))
    lit2(cv, [window_light(wx, wy, ww, wh, '8aa0d0', 0.8)], (0.24, 0.24, 0.32), t)
    # 窗上的倒影：只有房间，没有他
    sub = Canvas(); sub.a = cv.a.copy()
    for y in range(wy, wy + wh):
        for x in range(wx, wx + ww):
            if DITH[y, x] < 0.25: cv.a[y, x] = np.clip(cv.a[y, x].astype(np.int16) + 18, 0, 255)
    for i in range(16):
        y = (wy + (i * 7 + t * 30) % wh); x = wx + (i * 13) % ww
        cv.vline(int(x), int(y), int(y) + 2, hexc('6a7aa0'))
    if t > 1.4: symbol(cv, 'q', wx + ww // 2, wy + 12, t)
    return cv


def a4(t, D):   # 19.70–27.94 夜里的斑马线：人群从他身上穿过去
    cv = Canvas(); emis = np.zeros((H, W), bool)
    sky(cv, ['07080f', '10142a', '1a2040'], 0, 96)
    skyline(cv, 98, 31, '1a1e34', 'ffcf7a', 0.25, hmin=30, hmax=80, t=t, emis=emis)
    cv.rect(0, 98, W, H - 98, hexc('2a2a34'))
    for i in range(10): cv.rect(i * 34 - 6, 120, 22, 40, hexc('8a8c94'))
    alpha = 0.8 - 0.25 * clamp(t / D)
    from lib import npc
    for i in range(8):
        d = 1 if i % 2 else -1
        x = (t * 46 * (1 + (i % 3) * 0.2) + i * 50) % (W + 40) - 20
        if d < 0: x = W - x
        L = Layer(); f2 = npc(L, ['npc', 'npc_g'][i % 2], x, 142 + (i % 3) * 8, 20, t + i * 0.2, facing=d)
        L.ellipse(x, f2['top'] - 5, 15, 6, hexc('3a3e4a'), INK); L.rect(x - 15, f2['top'] - 5, 31, 6, hexc('3a3e4a'))
        layer_obj(L, 0.25)
    m, a = chibi('wu', 160, 154, 32, 'stand', 'sad', t, floor=0.7, alpha=alpha, tint=('6a7aa0', 0.35))
    # 车灯 / 路灯
    lit2(cv, [Light(40, 90, 'ffcf8a', 70, 0.6), Light(290, 90, 'ffcf8a', 70, 0.6), Light(W + 20 - (t * 120) % (W + 80), 130, 'fff0c0', 50, 0.8), Light(160, 70, 'c8d0ff', 70, 0.7)], (0.18, 0.19, 0.28), t, emissive=emis)
    streetlamp(cv, 40, 60, 120, True, t); streetlamp(cv, 290, 60, 120, True, t)
    rim(cv, m, 160, 60, 'c8d0ff', k=0.8)
    rain(cv, t, n=150, seed=14, speed=170, col='6a7494')
    return cv


def a5(t, D):   # 27.94–33.02 房间里：翻不了身，台灯灭了
    cv = Canvas()
    wx, wy, ww, wh = room(cv, t, 0.0)
    flail = int(t * 5) % 2
    L = Layer()
    from hd import wu as w_
    f = w_(L, 266, 128, 24, 'jump' if flail else 'cheer', 'surprise', t=t)
    # 侧躺：旋转图层
    a = L.a; mk = L.mask(); ys, xs = np.where(mk)
    if len(xs):
        y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
        sub = np.rot90(a[y0:y1, x0:x1], 1); sm = np.rot90(mk[y0:y1, x0:x1], 1)
        L2 = Layer(); hh, ww_ = sm.shape; oy, ox = 118 - hh // 2, 266 - ww_ // 2
        for j in range(hh):
            for i in range(ww_):
                if sm[j, i] and 0 <= oy + j < H and 0 <= ox + i < W: L2.a[oy + j, ox + i] = sub[j, i]
        mm = layer_obj(L2, 0.45)
    lamp = clamp(1 - t / 2.0)
    lit2(cv, [window_light(wx, wy, ww, wh, '7a8ac0', 0.45), Light(108, 96, 'ffcf7a', 70, 0.9 * lamp, flick=0.6 if lamp > 0 else 0)], (0.22, 0.22, 0.3), t)
    if lamp > 0.1: glow(cv, 108, 92, 16, 'ff9a40', 0.4 * lamp)
    symbol(cv, 'sweat', 300, 96, t)
    return cv


def a6(t, D):   # 33.02–38.41 往下坠；井口出现一点蓝光和一点暖光
    cv = Canvas(hexc('0a0a16'))
    off = int(t * 70) % 16
    for y in range(-16, H + 16, 8):
        for x in range(0, 80, 14): cv.rect(x + (y // 8 % 2) * 7, y + off, 12, 6, hexc('1a1a2c'))
        for x in range(240, W, 14): cv.rect(x + (y // 8 % 2) * 7, y + off, 12, 6, hexc('1a1a2c'))
    m, a = chibi('wu', 160 + math.sin(t * 2) * 6, 120 + t * 4, 26, 'cheer', 'sad', t, floor=0.5, tint=('5a6a9a', 0.5))
    k = clamp((t - 2.2) / 2.0)
    bx, by = 160 + math.sin(t * 2) * 20, -10 + k * 40
    lit2(cv, [Light(bx, by, '5a9aff', 60, 1.0 * k), Light(160, -20, 'ffb860', 80, 0.8 * k)], (0.14, 0.14, 0.22), t)
    if k > 0:
        glow(cv, 160, -6, 50, 'ff9a40', 0.5 * k)
        butterfly_glow(cv, bx, by, 1.0, t); glow(cv, bx, by, 16, '3a7aff', 0.6)
    rim(cv, m, bx, by, '8fd6ff', k=k)
    # 往上飘走的小魂
    sx, sy = 172 + math.sin(t * 3) * 6, 70 - t * 18
    cv.ellipse(sx, sy, 4, 5, hexc('8a90b0'))
    return cv


SHOTS = [(0.00, 6.44, a1), (6.44, 14.74, a2), (14.74, 19.70, a3), (19.70, 27.94, a4), (27.94, 33.02, a5), (33.02, 38.41, a6)]
