"""《蝴蝶》v3 样片：第一段副歌 0:38.41–1:15.37，5 个镜头（按乐句切）。
比喻语言：光 = 存在感。他是暗处的剪影；她带着光来；光照到哪，他就"回来"到哪。"""
import math, sys
import numpy as np
from px import Canvas, W, H, hexc, mix, clamp, ease, lerp, rng
from light import *
from hd import title_text

T0 = 38.41

# ---------------------------------------------------------------- v3.1：人物用回 Q 版，光照后再合成（保底亮度，保证看得清）
from hd import wu as _wu, die as _die, Layer as _Layer
PEND = []


def chibi(who, x, feet, Hh, pose='stand', expr='normal', t=0.0, facing=0, floor=0.9):
    L = _Layer()
    f = (_wu if who == 'wu' else _die)(L, int(x), int(feet), max(8, int(Hh)), pose, expr, t=t, facing=facing)
    m = L.mask()
    PEND.append((L, m, floor))
    return m, dict(head=(f['cx'], f['top'] + int(Hh * 0.82)), hand=f['hands'][1], top=f['top'])


def lit2(cv, lights, ambient, t=0.0, emissive=None):
    Lm = lightmap(lights, ambient, t)
    a = cv.a.astype(np.float32) / 255.0
    out = np.clip(a * Lm, 0, 1)
    if emissive is not None: out = np.where(emissive[..., None], a, out)
    for (L, m, floor) in PEND:
        sh = np.clip(Lm, floor, 1.25)
        ca = np.clip(L.a.astype(np.float32) / 255.0 * sh, 0, 1)
        out[m] = ca[m]
    PEND.clear()
    cv.a = (out * 255).astype(np.uint8)



def ground_streak(cv, x, y0, length, col, w=3, k=0.5):
    c = np.array(hexc(col), np.float32)
    for y in range(int(y0), min(H, int(y0 + length))):
        u = 1 - (y - y0) / length
        for xx in range(int(x - w), int(x + w + 1)):
            if 0 <= xx < W and DITH[y, xx] < k * u * (1 - abs(xx - x) / (w + 1)):
                a = cv.a[y, xx].astype(np.float32)
                cv.a[y, xx] = np.clip(a * 0.4 + c * 0.7, 0, 255).astype(np.uint8)


# ================================================================ S1 巷子：她带着光走过来（38.41–45.37）
def s1(t, D):   # 38.41–45.37 雨夜巷子尽头，她撑着暖黄的伞走来 —— 全片第一块颜色
    cv = Canvas()
    VX, VY = 170, 96
    sky(cv, ['07080f', '0d1020', '161a30'], 0, 80)
    # 两侧墙（透视）
    cv.poly([(0, 0), (150, 70), (150, 108), (0, H)], hexc('7a7482'))
    cv.line(0, 0, 150, 70, hexc('0c0a14')); cv.line(0, 1, 150, 71, hexc('9a94a2'))
    cv.poly([(W, 0), (192, 70), (192, 108), (W, H)], hexc('847a88'))
    cv.line(W, 0, 192, 70, hexc('0c0a14'))
    cv.rect(150, 70, 42, 38, hexc('3a3644'))
    cv.rect(162, 82, 16, 26, hexc('201c24'))   # 巷子尽头的门洞
    cv.poly([(0, H), (150, 108), (192, 108), (W, H)], hexc('3a3a46'))
    # 墙上的窗、空调、电线（沿透视）
    win = []
    for u in (0.12, 0.3, 0.48, 0.64, 0.78):
        for side in (0, 1):
            if side == 0:
                x = lerp(0, 150, u); top = lerp(0, 70, u); bot = lerp(H, 108, u)
                xw = x - 14 * (1 - u) - 2
            else:
                x = lerp(W, 192, u); top = lerp(0, 70, u); bot = lerp(H, 108, u)
                xw = x + 4 * (1 - u)
            hgt = bot - top
            for j, fy in enumerate((0.18, 0.45)):
                wy = top + hgt * fy; ww = max(2, 10 * (1 - u) + 2); wh = max(2, hgt * 0.14)
                cv.rect(xw, wy, ww, wh, hexc('1c1a24'))
                win.append((xw, wy, ww, wh, (int(u * 100) + side * 7 + j * 3) % 5 == 0))
    for k in range(3):
        cv.line(0, 20 + k * 9, W, 26 + k * 7, hexc('101018'))
    # 人物：他坐在左前方台阶上，她从巷子深处走来
    k = ease(clamp(t / (D - 1.2)))
    hs = lerp(9, 26, k) * 2.3; sx = lerp(176, 214, k); sf = lerp(108, 168, k)
    cv.rect(30, 166, 80, 14, hexc('4a4652'))   # 台阶
    reach = clamp((k - 0.3) / 0.6)
    mh, ah = chibi('wu', 82, 170, 30, 'sit', 'sad' if reach < 0.8 else 'wonder', t, facing=1, floor=0.5 + 0.45 * reach)
    ms, as_ = chibi('die', sx, sf, hs / 2.3, 'walk', 'smile', t, facing=-1, floor=1.0)
    # 光
    ux, uy = sx + hs * 0.05, sf - hs * 1.05
    lights = [Light(170, 100, 'ffb870', 46, 0.9),
              Light(ux, uy + hs * 0.35, 'ffbe6a', 20 + hs * 2.4, 1.3),
              Light(64, 40, '8aa0ff', 60, 0.5, flick=1.0)]
    lit2(cv, lights, (0.2, 0.21, 0.32), t)
    # 发光的东西
    for (xw, wy, ww, wh, on) in win:
        if on: cv.rect(xw, wy, ww, wh, hexc('ffcf7a')); glow(cv, xw + ww / 2, wy + wh / 2, ww * 1.6, 'ff9a40', 0.35)
    cv.rect(162, 82, 16, 26, hexc('ffd08a')); glow(cv, 170, 95, 30, 'ff9a40', 0.5)
    um = umbrella(cv, ux, uy - hs * 0.32, hs * 0.55, hs * 0.3, col='ffcf5a', dk='e0a030')
    glow(cv, ux, uy, 8 + hs * 1.1, 'ffaa40', 0.55)
    # 路灯（坏的，闪）
    cv.rect(62, 36, 2, 130, hexc('16161e')); cv.rect(56, 34, 12, 3, hexc('16161e'))
    if math.sin(t * 7.3 + 40) <= 0.6: cv.rect(58, 37, 6, 2, hexc('c8d0ff')); glow(cv, 61, 38, 14, '6a7ad0', 0.4)
    # 他被照到的那一侧亮起来（存在感回来）
    rim(cv, mh, ux, uy, 'ffcf8a', k=clamp((k - 0.35) / 0.5), maxd=None)
    rim(cv, ms, 170, 100, 'ffd8a0', k=0.8)
    rim(cv, mh, 64, 40, '8a9ad8', k=0.6)
    # 地面倒影光带
    ground_streak(cv, ux, sf + 1, 8 + hs * 0.6, 'ffb860', w=2 + hs * 0.15, k=0.35)
    ground_streak(cv, 170, 109, 18, 'ff9a40', w=6, k=0.3)
    # 雨（伞下不下）
    def ex(x, y): return um[y, x] or (abs(x - ux) < hs * 0.55 and uy - hs * 0.3 < y < sf)
    rain(cv, t, n=170, seed=2, speed=170, col='6a7494', y_ground=H, excl=ex)
    return cv


# ================================================================ 废墟（S2、S3 共用的地方）
def ruins_layers(cv, t, pan, emis, near=False):
    sky(cv, ['05060f', '0b0e22', '151a3a', '262a52', '3a3456'], 0, 130)
    # 月亮 + 云
    mx, my = 252, 38
    cv.ellipse(mx, my, 9, 9, hexc('e8ecff')); emis[int(my) - 9:int(my) + 9, mx - 9:mx + 9] |= ((XX[int(my) - 9:int(my) + 9, mx - 9:mx + 9] - mx) ** 2 + (YY[int(my) - 9:int(my) + 9, mx - 9:mx + 9] - my) ** 2) < 81
    for i in range(4):
        x = (i * 100 + t * 3) % (W + 80) - 40
        cv.ellipse(x, 30 + i * 9, 30, 4, hexc('1a1e3a'))
    # 远景楼（视差 0.2）
    skyline(cv, 124 if not near else 110, 7, '161a32', 'ffc870', 0.06, off=pan * 0.2, hmin=20, hmax=60, t=t, emis=emis)
    # 中景：残墙剪影（视差 0.5）
    o = pan * 0.5
    base = 140 if not near else 132
    for (x, w, h, s) in [(10, 60, 50, 1), (110, 40, 34, 2), (190, 70, 58, 3), (290, 50, 40, 4)]:
        xx = x - o
        r = rng(s)
        pts = [(xx, base), (xx, base - h)]
        for k in range(1, 6): pts.append((xx + w * k / 6, base - h * r.uniform(0.4, 1.0)))
        pts.append((xx + w, base))
        cv.poly(pts, hexc('22223a'))
        cv.rect(xx + w * 0.4, base - h * 0.5, 5, 7, hexc('0a0a14'))
    cv.rect(0, base, W, H - base, hexc('1a1a2a'))
    # 积水
    for (x, y, w) in [(70, 156, 26), (200, 150, 36), (290, 166, 20)]:
        cv.ellipse(x - o * 0.8, y, w, 3, hexc('20263e'))
    return base


def rubble_fg(cv, t, pan, seed=5):
    o = pan * 1.0
    r = rng(seed)
    pts = [(-20 - o % 40, H)]
    for k in range(0, 18):
        pts.append((k * 22 - o, H - 10 - r.uniform(0, 16)))
    pts.append((W + 40, H))
    cv.poly(pts, hexc('08080e'))


def s2(t, D):   # 45.37–51.55 夜里的废墟，第一只蓝蝴蝶拖着亮线飞过，片名浮现
    cv = Canvas()
    emis = np.zeros((H, W), bool)
    pan = t * 6
    base = ruins_layers(cv, t, pan, emis)
    mh, a = chibi('wu', 236 - pan * 0.5, base, 12, 'stand', 'wonder', t, facing=-1, floor=0.75)
    rubble_fg(cv, t, pan)
    path = lambda tt: (10 + tt * 52, 92 - 22 * math.sin(tt * 1.1) - tt * 2)
    bx, by = path(t)
    lit2(cv, [Light(252, 38, 'b8c4ff', 160, 0.35), Light(bx, by, '5a9aff', 46, 1.1)], (0.2, 0.22, 0.36), t, emissive=emis)
    # 发光的东西（不受光照）
    sky_band = None
    cv.ellipse(252, 38, 9, 9, hexc('eef0ff')); glow(cv, 252, 38, 34, '8a9aff', 0.45)
    skyline_em = emis.copy()
    trail(cv, path, t, 2.4, col='8fd6ff')
    butterfly_glow(cv, bx, by, 1.3, t)
    glow(cv, bx, by, 22, '3a7aff', 0.6)
    rim(cv, mh, bx, by, '8fd6ff', k=clamp(1 - abs(bx - (236 - pan * 0.5)) / 90))
    # 倒影：水洼里的蝴蝶
    for (x, y, w) in [(70, 156, 26), (200, 150, 36)]:
        xx = x - pan * 0.4
        if abs(bx - xx) < w: cv.rect(bx, y - 1, 3, 2, hexc('6aaeff'))
        if abs(252 - xx) < w: cv.rect(252 - 2, y - 1, 4, 2, hexc('c8d0ff'))
    # 片名（小，居中偏上）
    k = clamp((t - 1.4) / 1.0) * (1 - clamp((t - (D - 1.0)) / 0.8))
    if k > 0:
        m = Canvas((255, 0, 255)); title_text(m, '蝴  蝶', 160, 24, hexc('e8ecff'), size=16, outline=hexc('0a0c1e'))
        mm = np.any(m.a != np.array([255, 0, 255], np.uint8), axis=2) & (DITH < k)
        cv.a[mm] = m.a[mm]
    return cv


def s3(t, D):   # 51.55–58.12 废墟碎砖堆上，她提着灯坐到他身边，他抬起头笑了
    cv = Canvas()
    emis = np.zeros((H, W), bool)
    pan = 40 + t * 2
    base = ruins_layers(cv, t, pan, emis, near=True)
    # 碎砖堆（中景，人物坐在上面）
    cv.poly([(70, H), (110, 150), (160, 142), (215, 150), (260, H)], hexc('2a2636'))
    up = clamp((t - 1.2) / 2.5)
    mh, ah = chibi('wu', 124, 156, 30, 'sit', 'sad' if up < 0.6 else 'smile', t, facing=1, floor=0.5 + 0.45 * up)
    ms, as_ = chibi('die', 196, 156, 30, 'sit', 'smile', t, facing=-1, floor=0.95)
    # 小苗剪影 + 茧
    sx, sy = 160, 146
    cv.rect(sx - 4, sy, 8, 5, hexc('3a2a2a')); cv.vline(sx, sy - 12, sy, hexc('2a3a2a'))
    cv.ellipse(sx + 4, sy - 10, 4, 1.5, hexc('2a3a2a')); cv.ellipse(sx - 4, sy - 7, 3, 1.3, hexc('2a3a2a'))
    lk = ease(clamp((t - 0.6) / 1.2))
    lx, ly = 172, 147
    rubble_fg(cv, t, pan, seed=9)
    lit2(cv, [Light(lx, ly - 4, 'ffb860', 30 + 60 * lk, 1.3 * lk + 0.05), Light(252, 38, 'b8c4ff', 160, 0.3)], (0.16, 0.17, 0.3), t, emissive=emis)
    # 发光：灯笼、茧
    cv.ellipse(252, 38, 9, 9, hexc('eef0ff')); glow(cv, 252, 38, 30, '8a9aff', 0.4)
    cv.rect(lx - 3, ly - 8, 6, 8, hexc('2a1a10')); cv.rect(lx - 2, ly - 7, 4, 6, mix(hexc('5a3a20'), hexc('ffd890'), lk))
    glow(cv, lx, ly - 4, 10 + 30 * lk, 'ff9a40', 0.6 * lk)
    cg = 0.3 + 0.7 * (0.5 + 0.5 * math.sin(t * 2.4))
    cv.ellipse(sx + 6, sy - 6, 1.5, 2.5, mix(hexc('5a6a8a'), hexc('a8d8ff'), cg * lk))
    # 他慢慢被点亮
    rim(cv, mh, lx, ly - 4, 'ffcf8a', k=clamp((t - 1.2) / 2.5))
    rim(cv, ms, lx, ly - 4, 'ffd8a0', k=lk)
    fireflies(cv, t - 1.8, n=int(18 * clamp((t - 1.8) / 2)), seed=4, box=(90, 90, 240, 150))
    return cv


# ================================================================ 天台（S4、S5 共用的地方）
def rooftop(cv, t, dawn, emis, small=False):
    a = ['0e1430', '1c2a58', '3a4a80', '6a6a98']
    b = ['3a4a8a', '8a7ab0', 'f0a08a', 'ffd8a0']
    cols = ['%02x%02x%02x' % tuple(int(lerp(int(x[i:i + 2], 16), int(y[i:i + 2], 16), dawn)) for i in (0, 2, 4)) for x, y in zip(a, b)]
    sky(cv, cols, 0, 132)
    if dawn > 0.05:   # 太阳
        sy = lerp(140, 104, dawn)
        cv.ellipse(220, sy, 12, 12, hexc('fff2c8'))
        glow(cv, 220, sy, 70, 'ffb060', 0.45 * dawn)
        for i in range(9):
            ang = math.radians(200 + i * 16 + math.sin(t * 0.3) * 2)
            for r_ in range(16, 160, 2):
                x = 220 + math.cos(ang) * r_; y = sy + math.sin(ang) * r_
                if 0 <= int(y) < H and 0 <= int(x) < W and DITH[int(y), int(x)] < 0.12 * dawn * (1 - r_ / 160):
                    cv.px(x, y, hexc('ffe0a0'))
    lp = 0.35 * (1 - dawn)
    skyline(cv, 132, 21, mix(hexc('1a2040'), hexc('6a5a7a'), dawn), 'ffcf7a', lp, hmin=8, hmax=30, wmin=8, wmax=18, t=t, emis=emis)
    skyline(cv, 146, 22, mix(hexc('121630'), hexc('4a3a5a'), dawn), 'ffcf7a', lp * 1.2, hmin=10, hmax=34, wmin=12, wmax=24, t=t, emis=emis)
    # 天台
    top = 150 if not small else 156
    cv.rect(0, top, W, H - top, mix(hexc('22222e'), hexc('4a3a44'), dawn))
    cv.rect(0, top - 6, W, 2, mix(hexc('2a2a38'), hexc('5a4a54'), dawn))
    for x in range(4, W, 14): cv.rect(x, top - 6, 2, 6, mix(hexc('2a2a38'), hexc('5a4a54'), dawn))
    cv.rect(18, top - 34, 30, 28, mix(hexc('1a1a26'), hexc('3a2e3a'), dawn)); cv.rect(14, top - 37, 38, 4, mix(hexc('1a1a26'), hexc('3a2e3a'), dawn))
    return top


def breath(cv, x, y, t, period=2.0, strength=1.0, phase=0.0):
    u = ((t + phase) % period) / period
    if u < 0.75:
        k = u / 0.75
        for i in range(10):
            a = i * 0.7
            px_ = x + 3 + k * 10 + math.cos(a + t) * k * 4 * strength
            py_ = y - 1 - k * 6 + math.sin(a * 1.3) * k * 3 * strength
            if 0 <= int(py_) < H and 0 <= int(px_) < W and DITH[int(py_), int(px_)] < (1 - k) * 0.9 * strength:
                cv.px(px_, py_, hexc('e8eeff'))


def s4(t, D):   # 58.12–65.90 夜里的天台，两人并肩，她拉他的手指向城市的灯
    cv = Canvas()
    emis = np.zeros((H, W), bool)
    top = rooftop(cv, t, 0.0, emis)
    r = rng(44)
    for i in range(60):
        x, y = r.uniform(0, W), r.uniform(0, 90)
        if (t * 2 + i) % 5 > 0.4: cv.px(x, y, hexc('c8d0ff') if i % 4 else hexc('fff4d0')); emis[int(y), int(x)] = True
    mist(cv, t, 118, 30, col='3a4a7a', k=0.45, speed=6)
    mh, ah = chibi('wu', 128, top, 34, 'stand', 'closed' if int(t / 1.2) % 2 else 'normal', t, facing=1, floor=0.85)
    ms, as_ = chibi('die', 172, top, 34, 'hold_l', 'smile', t, facing=-1, floor=0.95)
    lx, ly = as_['hand']
    lit2(cv, [Light(lx, ly + 4, 'ffb860', 60, 1.2), Light(220, 140, 'ff9a80', 160, 0.15)], (0.2, 0.24, 0.42), t, emissive=emis)
    cv.rect(lx - 2, ly, 5, 7, hexc('2a1a10')); cv.rect(lx - 1, ly + 1, 3, 5, hexc('ffd890'))
    glow(cv, lx, ly + 4, 34, 'ff9a40', 0.55)
    rim(cv, mh, lx, ly + 4, 'ffcf8a', k=0.85)
    rim(cv, ms, lx, ly + 4, 'ffd8a0', k=0.9)
    hx, hy = ah['head']
    strength = 0.4 + 0.6 * clamp(t / D)
    breath(cv, hx, hy + 2, t, 2.4, strength * 1.3)
    breath(cv, as_['head'][0] - 6, as_['head'][1] + 2, t, 2.4, 0.6, phase=1.2)
    mist(cv, t + 3, 150, 26, col='4a5a8a', k=0.25, speed=9)
    return cv


def s5(t, D):   # 65.90–75.37 长镜头：天台上天亮了，两个人张开手深呼吸
    """长镜头：天台上天亮了，两个人张开手深呼吸。"""
    cv = Canvas()
    emis = np.zeros((H, W), bool)
    dawn = ease(clamp(t / (D - 1.0)))
    top = rooftop(cv, t, dawn, emis, small=True)
    skym = np.zeros((H, W), bool); skym[:132] = True
    bm = Canvas(); sky(bm, ['000000'], 0, H); skyline(bm, 132, 21, 'ffffff', 'ffffff', 0, hmin=8, hmax=30, wmin=8, wmax=18); skyline(bm, 146, 22, 'ffffff', 'ffffff', 0, hmin=10, hmax=34, wmin=12, wmax=24)
    skym &= bm.a[..., 0] == 0
    mist(cv, t, 124, 26, col=mix(hexc('3a4a7a'), hexc('ffc8a0'), dawn) and '%02x%02x%02x' % mix(hexc('3a4a7a'), hexc('ffc8a0'), dawn), k=0.4, speed=6)
    pose = 'cheer' if t > 3.1 else 'stand'
    mh, ah = chibi('wu', 140, top, 24, pose, 'closed' if t > 3.1 else 'smile', t, facing=0, floor=0.85)
    ms, as_ = chibi('die', 174, top, 24, pose, 'joy' if t > 3.1 else 'smile', t, facing=0, floor=0.9)
    sy = lerp(140, 104, dawn)
    lit2(cv, [Light(220, sy, 'ffb070', 260, 0.9 * dawn), Light(158, top - 6, 'ffb860', 40, 0.6 * (1 - dawn))], (0.2 + 0.25 * dawn, 0.22 + 0.2 * dawn, 0.4 + 0.1 * dawn), t, emissive=emis)
    # 太阳是发光体，重画
    if dawn > 0.05:
        sun = Canvas(); sun.a = cv.a.copy(); sun.ellipse(220, sy, 12, 12, hexc('fff2c8')); glow(sun, 220, sy, 50, 'ffb060', 0.5 * dawn)
        cv.a = np.where(skym[..., None], sun.a, cv.a)
    rim(cv, mh, 220, sy, 'ffd8a0', k=dawn)
    rim(cv, ms, 220, sy, 'ffe0b0', k=dawn)
    if t > 3.1:
        breath(cv, ah['head'][0], ah['head'][1] + 2, t, 2.2, 1.0)
        breath(cv, as_['head'][0], as_['head'][1] + 2, t, 2.2, 0.9, phase=0.3)
    # 鸟群
    for i in range(7):
        u = (t - 2.0) * 0.12 + i * 0.015
        if 0 < u < 1.2:
            x = lerp(-20, 340, u) + (i % 3) * 6; y = 60 - u * 20 + (i % 2) * 5 + math.sin(t * 6 + i) * 1
            fl = int(t * 8 + i) % 2
            cv.px(x, y, hexc('2a2030')); cv.px(x - 1, y - fl, hexc('2a2030')); cv.px(x + 1, y - fl, hexc('2a2030'))
    # 蝴蝶最后飞进画面
    if t > D - 3.2:
        u = t - (D - 3.2)
        bx = 300 - u * 40; by = 120 - math.sin(u * 2) * 10
        butterfly_glow(cv, bx, by, 0.9, t); glow(cv, bx, by, 12, '3a7aff', 0.5)
    return cv


SHOTS = [(38.41, 45.37, s1), (45.37, 51.55, s2), (51.55, 58.12, s3), (58.12, 65.90, s4), (65.90, 75.37, s5)]


def timeline():
    return [(a, b, (lambda fn, D: (lambda t: fn(t, D)))(fn, b - a)) for a, b, fn in SHOTS]


if __name__ == '__main__':
    from PIL import Image
    tiles = []
    for a, b, fn in SHOTS:
        for fr in (0.15, 0.6, 0.95):
            cv = fn((b - a) * fr, b - a)
            tiles.append(Image.fromarray(np.repeat(np.repeat(cv.a, 2, 0), 2, 1)))
    c = Image.new('RGB', (640 * 3, 360 * len(SHOTS)))
    for i, im in enumerate(tiles): c.paste(im, ((i % 3) * 640, (i // 3) * 360))
    c.save('v3_chk.png'); print('ok')
