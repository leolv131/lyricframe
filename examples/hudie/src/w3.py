"""《蝴蝶》v3.1 全片共用：Q 版人物（光照后合成、保底亮度）、四个核心场景（巷子 / 废墟 / 天台 / 房间）、
以及少量专用场景（井、电梯、云上、花店）。所有场景都先画固有色，再 lit2() 打光，最后画发光物。"""
import math
import numpy as np
from PIL import Image, ImageDraw
from px import Canvas, W, H, hexc, mix, clamp, ease, lerp, rng, dilate, PAL
from light import (Light, lightmap, glow, sky, skyline, rain, fireflies, butterfly_glow, trail, umbrella, mist, rim, DITH, XX, YY)
from hd import wu as _wu, die as _die, Layer, title_text, bandaid, clip as _clip, butterfly as _bfly
from chars import head as _head, symbol
from ui import mitt

INK = hexc('0c0a14')
WHITE = PAL['white']
PEND = []


# ================================================================ 人物
def chibi(who, x, feet, Hh, pose='stand', expr='normal', t=0.0, facing=0, floor=0.9, alpha=1.0, tint=None, apron=False, back=False):
    """Q 版人物。floor=光照后保底亮度；alpha<1 时按抖动半透明（被忽视）；tint=(颜色, 强度) 冷色 / 回忆色。"""
    L = Layer()
    if who == 'wu': f = _wu(L, int(x), int(feet), max(8, int(Hh)), pose, expr, t=t, facing=facing, apron=apron, back=back)
    else: f = _die(L, int(x), int(feet), max(8, int(Hh)), pose, expr, t=t, facing=facing, back=back)
    m = L.mask()
    PEND.append((L, m, floor, alpha, tint))
    return m, dict(head=(f['cx'], f['top'] + int(Hh * 0.82)), hand=f['hands'][1], hand_l=f['hands'][0], top=f['top'], cx=f['cx'], f=f)


def face(who, cx, top, Hh, expr, t=0.0, floor=0.9, tint=None, body=None):
    """近景 / 特写：头 + 肩（光照后合成）"""
    L = Layer()
    bc = body or (hexc('969aa6') if who == 'wu' else hexc('f7ead6'))
    L.ellipse(cx, top + Hh * 1.6, Hh * 0.95, Hh * 0.62, bc, INK)
    f = _head(L, who, cx, top, Hh, expr, t=t)
    if who == 'wu': bandaid(L, int(cx - f['Wh'] * 0.28), top + int(Hh * 0.74), 2)
    else: _clip(L, int(cx + f['Wh'] * 0.30), top + int(Hh * 0.22), Hh, t)
    m = L.mask(); PEND.append((L, m, floor, 1.0, tint))
    return m, f


def layer_obj(L, floor=0.9):
    m = L.mask(); PEND.append((L, m, floor, 1.0, None)); return m


def lit2(cv, lights, ambient, t=0.0, emissive=None):
    Lm = lightmap(lights, ambient, t)
    a = cv.a.astype(np.float32) / 255.0
    out = np.clip(a * Lm, 0, 1)
    if emissive is not None: out = np.where(emissive[..., None], a, out)
    for (L, m, floor, alpha, tint) in PEND:
        sh = np.clip(Lm, floor, 1.25)
        ca = np.clip(L.a.astype(np.float32) / 255.0 * sh, 0, 1)
        if tint is not None:
            c = np.array(hexc(tint[0]), np.float32) / 255.0
            g = ca.mean(2, keepdims=True)
            ca = ca * (1 - tint[1]) + (g * 0.6 + c * 0.4) * tint[1]
        mm = m & (DITH < alpha) if alpha < 1 else m
        out[mm] = ca[mm]
        if alpha < 1:   # 虚线轮廓
            e = dilate(m) & ~m & (((XX + YY + int(t * 8)) // 2) % 2 == 0)
            out[e] = np.array([0.55, 0.6, 0.7])
    PEND.clear()
    cv.a = (out * 255).astype(np.uint8)


def flat(cv):
    """白天：不压暗，直接合成人物"""
    lit2(cv, [], (1.0, 1.0, 1.0))


def ground_streak(cv, x, y0, length, col, w=3, k=0.5):
    c = np.array(hexc(col), np.float32)
    for y in range(int(y0), min(H, int(y0 + length))):
        u = 1 - (y - y0) / length
        for xx in range(int(x - w), int(x + w + 1)):
            if 0 <= xx < W and DITH[y, xx] < k * u * (1 - abs(xx - x) / (w + 1)):
                cv.a[y, xx] = np.clip(cv.a[y, xx].astype(np.float32) * 0.4 + c * 0.7, 0, 255).astype(np.uint8)


def fade_in_text(cv, x, y, s, k, col='e8ecff', size=12, outline='0a0c1e'):
    if k <= 0: return
    m = Canvas((255, 0, 255))
    if size == 12: m.text(x, y, s, hexc(col), outline=hexc(outline), anchor='mt')
    else: title_text(m, s, x, y, hexc(col), size=size, outline=hexc(outline))
    mm = np.any(m.a != np.array([255, 0, 255], np.uint8), axis=2) & (DITH < k)
    cv.a[mm] = m.a[mm]


def lerpc(a, b, k):
    a, b = hexc(a), hexc(b)
    return '%02x%02x%02x' % tuple(int(lerp(x, y, k)) for x, y in zip(a, b))


# ================================================================ 场景 1：巷子（透视）
def alley(cv, t, tod=0.0, snow_=False):
    """tod: 0=深夜 1=白天。返回 (窗户列表, 是否夜)。"""
    sky(cv, [lerpc('07080f', '8cc8f0', tod), lerpc('0d1020', 'aed8f4', tod), lerpc('161a30', 'd4ecf8', tod)], 0, 80)
    wl = lerpc('7a7482', 'd8ccb8', tod); wr = lerpc('847a88', 'e4d8c4', tod)
    cv.poly([(0, 0), (150, 70), (150, 108), (0, H)], hexc(wl)); cv.line(0, 0, 150, 70, INK)
    cv.poly([(W, 0), (192, 70), (192, 108), (W, H)], hexc(wr)); cv.line(W, 0, 192, 70, INK)
    cv.rect(150, 70, 42, 38, hexc(lerpc('3a3644', 'b8a890', tod)))
    cv.rect(162, 82, 16, 26, hexc('201c24'))
    cv.poly([(0, H), (150, 108), (192, 108), (W, H)], hexc(lerpc('3a3a46', '9a9a9e', tod) if not snow_ else lerpc('7a8090', 'e8ecf4', tod)))
    wins = []
    for u in (0.12, 0.3, 0.48, 0.64, 0.78):
        for side in (0, 1):
            x = lerp(0, 150, u) if side == 0 else lerp(W, 192, u)
            top = lerp(0, 70, u); bot = lerp(H, 108, u); hgt = bot - top
            xw = x - 14 * (1 - u) - 2 if side == 0 else x + 4 * (1 - u)
            for j, fy in enumerate((0.18, 0.45)):
                wy = top + hgt * fy; ww = max(2, 10 * (1 - u) + 2); wh = max(2, hgt * 0.14)
                cv.rect(xw, wy, ww, wh, hexc(lerpc('1c1a24', '5a6a80', tod)))
                wins.append((xw, wy, ww, wh, (int(u * 100) + side * 7 + j * 3) % 5 == 0))
            if u in (0.3, 0.64):   # 空调外机 / 晾衣
                cv.rect(xw + (12 if side == 0 else -12) * (1 - u), top + hgt * 0.32, 8 * (1 - u) + 2, 5 * (1 - u) + 2, hexc(lerpc('2a2a34', 'c8c8c0', tod)))
    for k in range(3): cv.line(0, 20 + k * 9, W, 26 + k * 7, hexc(lerpc('101018', '4a4a50', tod)))
    return wins


def alley_emissive(cv, wins, k=1.0):
    for (xw, wy, ww, wh, on) in wins:
        if on and k > 0:
            cv.rect(xw, wy, ww, wh, hexc('ffcf7a')); glow(cv, xw + ww / 2, wy + wh / 2, ww * 1.6, 'ff9a40', 0.35 * k)
    if k > 0:
        cv.rect(162, 82, 16, 26, hexc('ffd08a')); glow(cv, 170, 95, 30, 'ff9a40', 0.5 * k)


def streetlamp(cv, x, top, ground, on=True, t=0.0, flick=False, col='ffe0a0'):
    cv.rect(x, top, 2, ground - top, hexc('16161e')); cv.rect(x - 6, top - 2, 12, 3, hexc('16161e'))
    lit_ = on and (not flick or math.sin(t * 7.3 + x) <= 0.6)
    if lit_: cv.rect(x - 4, top + 1, 8, 2, hexc(col)); glow(cv, x, top + 2, 20, 'ffb060' if col != 'c8d0ff' else '6a7ad0', 0.45)
    return lit_


# ================================================================ 场景 2：废墟（三层视差）
def ruins(cv, t, pan, tod=0.0, near=False, cleared=0.0, emis=None):
    sky(cv, [lerpc('05060f', '6ab4f0', tod), lerpc('0b0e22', '8ccaf6', tod), lerpc('151a3a', 'b8e0fa', tod), lerpc('262a52', 'e8f4fa', tod)], 0, 130)
    skyline(cv, 124 if not near else 110, 7, lerpc('161a32', '9aa8c0', tod), 'ffc870', 0.06 * (1 - tod), off=pan * 0.2, hmin=20, hmax=60, t=t, emis=emis)
    o = pan * 0.5
    base = 140 if not near else 132
    for (x, w, h, s) in [(10, 60, 50, 1), (110, 40, 34, 2), (190, 70, 58, 3), (290, 50, 40, 4)]:
        xx = x - o; r = rng(s)
        pts = [(xx, base), (xx, base - h)]
        for k in range(1, 6): pts.append((xx + w * k / 6, base - h * r.uniform(0.4, 1.0)))
        pts.append((xx + w, base))
        cv.poly(pts, hexc(lerpc('22223a', 'b0a49c', tod)))
        cv.rect(xx + w * 0.4, base - h * 0.5, 5, 7, hexc(lerpc('0a0a14', '6a5a54', tod)))
    cv.rect(0, base, W, H - base, hexc(lerpc('1a1a2a', 'a89a90', tod)))
    if cleared < 1:
        r = rng(9)
        for i in range(int(60 * (1 - cleared))):
            x = r.uniform(0, W) - o * 0.8; y = r.uniform(base + 2, H)
            cv.rect(x, y, int(r.integers(3, 7)), 2, hexc(lerpc('2a2636', 'c08070', tod)))
    for (x, y, w) in [(70, 156, 26), (200, 150, 36)]:
        cv.ellipse(x - o * 0.8, y, w, 3, hexc(lerpc('20263e', '9ab8d8', tod)))
    return base


def moon(cv, x=252, y=38, k=1.0):
    if k <= 0: return
    cv.ellipse(x, y, 9, 9, hexc('eef0ff')); glow(cv, x, y, 32, '8a9aff', 0.45 * k)


def rubble_fg(cv, pan, seed=5, col='08080e'):
    o = pan; r = rng(seed)
    pts = [(-20, H)] + [(k * 22 - o % 22, H - 10 - r.uniform(0, 16)) for k in range(0, 18)] + [(W + 40, H)]
    cv.poly(pts, hexc(col))


# ================================================================ 场景 3：天台
def rooftop(cv, t, tod, small=False, emis=None, cols=None, sun=True, dusk=False):
    """tod 0 深夜 → 1 白天；dusk=True 用黄昏色"""
    if dusk:
        cs = ['6a4a7a', 'c86a7a', 'ff9e6b', 'ffcf8a']
    else:
        a = ['0e1430', '1c2a58', '3a4a80', '6a6a98']; b = ['6ab4f0', '8ccaf6', 'b8e0fa', 'fff0d0']
        cs = [lerpc(x, y, tod) for x, y in zip(a, b)]
    sky(cv, cols or cs, 0, 132)
    lp = 0.35 * (1 - tod) * (0 if dusk else 1) + (0.15 if dusk else 0)
    skyline(cv, 132, 21, lerpc('1a2040', '9aa8c8', tod) if not dusk else '6a4a5a', 'ffcf7a', lp, hmin=8, hmax=30, wmin=8, wmax=18, t=t, emis=emis)
    skyline(cv, 146, 22, lerpc('121630', '7a88a8', tod) if not dusk else '4a3442', 'ffcf7a', lp * 1.2, hmin=10, hmax=34, wmin=12, wmax=24, t=t, emis=emis)
    top = 150 if not small else 156
    c = lerpc('22222e', '8a8a8e', tod) if not dusk else '5a3a44'
    cv.rect(0, top, W, H - top, hexc(c))
    cv.rect(0, top - 6, W, 2, hexc(lerpc(c, '000000', 0.2)))
    for x in range(4, W, 14): cv.rect(x, top - 6, 2, 6, hexc(lerpc(c, '000000', 0.2)))
    cv.rect(18, top - 34, 30, 28, hexc(lerpc(c, '000000', 0.3))); cv.rect(14, top - 37, 38, 4, hexc(lerpc(c, '000000', 0.3)))
    return top


def stars(cv, t, n=60, seed=44, y1=90, emis=None):
    r = rng(seed)
    for i in range(n):
        x, y = r.uniform(0, W), r.uniform(0, y1)
        if (t * 2 + i) % 5 > 0.4:
            cv.px(x, y, hexc('c8d0ff') if i % 4 else hexc('fff4d0'))
            if emis is not None: emis[int(y), int(x)] = True


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


# ================================================================ 场景 4：他的房间（暗，侧面）
def room(cv, t, tod=0.0):
    wall = lerpc('5a5248', 'c8b8a4', tod)
    cv.rect(0, 0, W, 140, hexc(wall))
    for x in range(0, W, 24): cv.vline(x, 0, 140, hexc(lerpc(wall, '000000', 0.08)))
    cv.rect(0, 140, W, H - 140, hexc(lerpc('3a3028', '8a7a64', tod))); cv.hline(0, W, 140, INK)
    # 窗（外面是路灯 / 天光）
    wx, wy, ww, wh = 150, 24, 70, 54
    cv.rect(wx - 2, wy - 2, ww + 4, wh + 4, INK); cv.rect(wx, wy, ww, wh, hexc(lerpc('141a2c', 'a8d0f0', tod)))
    cv.rect(wx + ww // 2, wy, 2, wh, INK); cv.rect(wx, wy + wh // 2, ww, 2, INK)
    cv.rect(wx - 6, wy - 6, 14, wh + 14, hexc(lerpc('4a4440', 'b0a090', tod))); cv.rect(wx + ww - 8, wy - 6, 14, wh + 14, hexc(lerpc('4a4440', 'b0a090', tod)))
    # 门
    cv.rect(14, 40, 40, 100, INK); cv.rect(16, 42, 36, 98, hexc(lerpc('3a2c28', '6a5248', tod))); cv.rect(44, 90, 3, 5, hexc('a09070'))
    # 床
    cv.rect(220, 112, 96, 28, INK); cv.rect(222, 114, 92, 20, hexc(lerpc('6a6670', 'c8c0b8', tod))); cv.rect(222, 108, 22, 10, hexc(lerpc('7a7680', 'e8e0d8', tod)))
    cv.rect(222, 134, 92, 6, hexc('3a2a20'))
    # 书桌 + 台灯
    cv.rect(66, 104, 60, 4, INK); cv.rect(67, 105, 58, 2, hexc('6a4a34'))
    cv.rect(70, 108, 3, 32, INK); cv.rect(118, 108, 3, 32, INK)
    cv.rect(108, 92, 2, 12, INK); cv.rect(102, 88, 12, 5, hexc('8a7a40'))
    return (wx, wy, ww, wh)


def window_light(wx, wy, ww, wh, col='8aa0d0', i=0.6):
    return Light(wx + ww / 2, wy + wh / 2 + 20, col, 110, i)


# ================================================================ 小道具
def seedling(cv, x, ground, s=1, cocoon=True, crack=0.0, bloom=0.0):
    pw, ph = 14 * s, 10 * s
    cv.poly([(x - pw // 2, ground - ph), (x + pw // 2, ground - ph), (x + pw // 2 - 2 * s, ground), (x - pw // 2 + 2 * s, ground)], hexc('b86a4a'))
    cv.rect(x - pw // 2, ground - ph - s, pw, 2 * s, hexc('5a4030'))
    sh = 18 * s
    cv.rect(x, ground - ph - sh, s, sh, hexc('5a9a4a'))
    lx, ly = x + s, ground - ph - sh + 4 * s
    cv.ellipse(lx + 5 * s, ly, 6 * s, 2.5 * s, hexc('6aba5a'), INK)
    cv.ellipse(x - 5 * s, ground - ph - sh + 9 * s, 5 * s, 2.2 * s, hexc('6aba5a'), INK)
    cx, cy = lx + 7 * s, ly + 5 * s
    if cocoon:
        cv.line(cx, ly + 1, cx, cy - 2 * s, hexc('d8d0c0'))
        cv.ellipse(cx, cy, 2 * s, 3.5 * s, hexc('c8b890'), INK)
        if crack > 0:
            cv.line(cx - 2 * s, cy - 2 * s, cx + s, cy, INK)
    if bloom > 0:
        for i in range(int(5 * bloom)):
            a = i * 1.3
            cv.ellipse(x + math.cos(a) * 6 * s, ground - ph - sh + math.sin(a) * 3 * s, 2 * s, 2 * s, hexc('ff8aa8'))
    return (cx, cy)


def paper_butterfly(cv, x, y, s=1):
    w = 14 * s; h = 10 * s
    cv.poly([(x, y), (x - w, y - h), (x - w * 0.7, y + h * 0.2)], hexc('2f8cff'))
    cv.poly([(x, y), (x + w, y - h), (x + w * 0.7, y + h * 0.2)], hexc('2f8cff'))
    cv.poly([(x, y), (x - w * 0.7, y + h * 0.2), (x - w * 0.4, y + h)], hexc('1a4fb0'))
    cv.poly([(x, y), (x + w * 0.7, y + h * 0.2), (x + w * 0.4, y + h)], hexc('1a4fb0'))
    cv.line(x - w, y - h, x, y, hexc('8fd6ff')); cv.line(x + w, y - h, x, y, hexc('8fd6ff'))


def lantern(cv, x, y, k=1.0, s=1):
    cv.rect(x - 3 * s, y - 8 * s, 6 * s, 8 * s, hexc('2a1a10')); cv.rect(x - 2 * s, y - 7 * s, 4 * s, 6 * s, mix(hexc('5a3a20'), hexc('ffd890'), k))
    cv.rect(x - s, y - 10 * s, 2 * s, 2 * s, hexc('2a1a10'))
    if k > 0: glow(cv, x, y - 4 * s, 10 + 26 * k * s, 'ff9a40', 0.6 * k)
bfly = _bfly
