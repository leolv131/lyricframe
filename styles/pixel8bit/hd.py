"""《蝴蝶》专用：色板、角色外观补丁、蓝蝴蝶、雨、伞、"颜色=存在感"合成、场景。
画面只由 t 决定。320x180 内部画布，x6 输出 1080p。"""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from px import *
from chars import char, head, symbol, thick_line, outline_poly, LOOK

INK = PAL['ink']
KEY = (255, 0, 255)

# ---------------------------------------------------------------- 色板（STORY 四、色板即叙事）
BLUE = hexc('2f8cff'); BLUE_H = hexc('8fd6ff'); BLUE_D = hexc('1a4fb0')
UMB = hexc('ffc94a'); UMB_D = hexc('e0a030'); UMB_H = hexc('ffe39a')
CREAM = hexc('f7ead6'); PEACH = hexc('ffb59a')
APRON = hexc('4f9a5c'); APRON_D = hexc('3a7646')

GRAY_RAMP = np.array([hexc(c) for c in
    ['171b24', '222733', '2e3441', '3a4150', '4b5363', '5b6475', '7a8394', 'a3abb8', 'c9cfd8']], np.float32)
DUSK_RAMP = np.array([hexc(c) for c in
    ['1c1a26', '2a2734', '3a3644', '4d4855', '625b66', '7d7480', '9d929a', 'c2b6b8', 'e2d6d0']], np.float32)

_B4 = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) / 16.0
_DITH = np.tile(_B4, (H // 4 + 1, W // 4 + 1))[:H, :W]


def to_ramp(a, ramp=GRAY_RAMP, lift=0.0, contrast=1.0):
    lum = (a[..., 0] * 0.30 + a[..., 1] * 0.55 + a[..., 2] * 0.15) / 255.0
    lum = np.clip((lum - 0.5) * contrast + 0.5 + lift, 0, 1)
    n = len(ramp) - 1
    idx = np.clip(np.floor(lum * n + _DITH * 0.95), 0, n).astype(np.int32)
    return ramp[idx]


def is_blue(a):
    r, g, b = a[..., 0].astype(np.int16), a[..., 1].astype(np.int16), a[..., 2].astype(np.int16)
    return (b > 150) & (b - r > 70) & (b - g > 25)


def grade(cv, ramp=GRAY_RAMP, keep=None, keep_blue=True, lift=0.0):
    """全画面变灰；keep = bool mask（这些像素保留原色，即"颜色回来了"）。蝴蝶蓝永远保留。"""
    g = to_ramp(cv.a, ramp, lift).astype(np.uint8)
    m = np.zeros((H, W), bool) if keep is None else keep.copy()
    if keep_blue: m |= is_blue(cv.a)
    cv.a = np.where(m[..., None], cv.a, g)
    return cv


def radial_keep(cx, cy, r, soft=6):
    """以 (cx,cy) 为中心、半径 r 的颜色圈；边缘 soft 像素做有序抖动。"""
    if r <= 0: return np.zeros((H, W), bool)
    yy, xx = np.mgrid[0:H, 0:W]
    d = np.sqrt((xx - cx) ** 2 + ((yy - cy) * 1.15) ** 2)
    f = np.clip((r - d) / soft, 0, 1)
    return f > _DITH


def warm_tint(cv, mask, k=0.18, col=CREAM):
    a = cv.a.astype(np.float32)
    t = a * (1 - k) + np.array(col, np.float32) * k
    cv.a = np.where(mask[..., None], t, a).astype(np.uint8)


# ---------------------------------------------------------------- 图层与"隐形"
class Layer(Canvas):
    def __init__(self):
        super().__init__(KEY)

    def mask(self):
        return np.any(self.a != np.array(KEY, np.uint8), axis=2)


def ghost(dst, layer, alpha=0.55, dotted=True, ramp=GRAY_RAMP, keep=None, t=0.0):
    """把角色图层以"半透明虚线人形"贴到 dst：
    alpha=1 实体，alpha→0 消失；被 keep 覆盖的像素恢复颜色和实体。"""
    m = layer.mask()
    if keep is None: keep = np.zeros((H, W), bool)
    g = to_ramp(layer.a, ramp, lift=0.12).astype(np.uint8)
    show = m & ((_DITH < alpha) | keep)
    src = np.where(keep[..., None], layer.a, g)
    dst.a[show] = src[show]
    if dotted and alpha < 0.999:
        edge = dilate(m) & ~m
        yy, xx = np.mgrid[0:H, 0:W]
        dash = ((xx + yy + int(t * 8)) // 2) % 2 == 0
        e = edge & dash & ~keep
        dst.a[e] = hexc('c9cfd8')
    return dst


def solid(dst, layer):
    m = layer.mask(); dst.a[m] = layer.a[m]; return dst


# ---------------------------------------------------------------- 角色
def bandaid(cv, x, y, s=1):
    if s == 1:
        cv.rect(x - 2, y, 5, 2, hexc('e8c08a')); cv.px(x, y, hexc('c89a6a'))
    else:
        cv.rect(x - 6, y - 1, 13, 6, INK); cv.rect(x - 5, y, 11, 4, hexc('e8c08a'))
        cv.rect(x - 2, y, 5, 4, hexc('f4d6a8'))
        for i in (-1, 1): cv.px(x + i, y + 1, hexc('c89a6a')); cv.px(x + i, y + 2, hexc('c89a6a'))


def clip(cv, x, y, Hh, t=0.0):
    """阿蝶的蓝蝴蝶发夹（头的右上方）。"""
    if Hh < 20:
        cv.px(x, y, BLUE); cv.px(x + 1, y, BLUE_H); cv.px(x - 1, y + 1, BLUE); cv.px(x + 2, y + 1, BLUE)
        cv.px(x, y + 1, INK); cv.px(x + 1, y + 1, INK)
        return
    if Hh < 40:
        butterfly(cv, x, y, 0.6, 0.0, flap=1.0, tilt=0.25)
    else:
        butterfly(cv, x, y, 0.85, 0.0, flap=1.0, tilt=0.25, sparkle=(t * 1.3) % 2 < 0.15)


def wu(cv, cx, feet, Hh, pose='stand', expr='normal', t=0.0, facing=0, back=False, apron=False, hold=None):
    f = char(cv, 'wu', cx, feet, Hh, pose, expr, t, facing, back, hold=hold)
    if Hh >= 12:
        Wh = f['Wh']; tp = f['top']; k = max(1, Hh // 12)
        for dx, h_ in ((-0.18, 2), (0.05, 3), (0.26, 2)):
            xx = int(f['cx'] + dx * Wh)
            for j in range(h_ * k):
                cv.rect(xx - 1 + (j // k) * (1 if dx > 0 else -1), tp - 2 - j, k + 2, 1, INK)
                cv.rect(xx + (j // k) * (1 if dx > 0 else -1), tp - 2 - j, k, 1, PAL['hair'])
    if not back:
        Wh = f['Wh']; s = 2 if Hh >= 36 else 1
        bandaid(cv, int(f['cx'] - Wh * 0.28), f['top'] + int(Hh * 0.72), s)
    if apron:
        tb = f['top_body']; tw = int(round(Hh * 0.70)); Tb = int(round(Hh * 0.78))
        x0 = int(cx - tw * 0.38)
        cv.rect(x0 - 1, tb + 2, int(tw * 0.76) + 2, Tb + max(2, Hh // 4), INK)
        cv.rect(x0, tb + 3, int(tw * 0.76), Tb + max(2, Hh // 4) - 2, APRON)
        cv.rect(x0, tb + 3, int(tw * 0.76), 1, APRON_D)
        fx, fy = int(cx), tb + Tb // 2 + 1
        cv.px(fx, fy, PEACH); cv.px(fx - 1, fy, hexc('ff7a8a')); cv.px(fx + 1, fy, hexc('ff7a8a')); cv.px(fx, fy - 1, hexc('ff7a8a')); cv.px(fx, fy + 1, APRON_D)
    return f


def die(cv, cx, feet, Hh, pose='stand', expr='normal', t=0.0, facing=0, back=False, hold=None):
    f = char(cv, 'die', cx, feet, Hh, pose, expr, t, facing, back, hold=hold)
    if not back:
        Wh = f['Wh']
        clip(cv, int(f['cx'] + Wh * 0.30), f['top'] + int(Hh * 0.22), Hh, t)
    return f


# ---------------------------------------------------------------- 蓝蝴蝶
def _poly_mask(pts):
    im = Image.new('1', (W, H), 0)
    ImageDraw.Draw(im).polygon([(int(round(p)), int(round(q))) for p, q in pts], fill=1)
    return np.array(im)


def butterfly(cv, x, y, s=1, t=0.0, flap=None, speed=5.0, sparkle=False, col=BLUE, hi=BLUE_H, dk=BLUE_D, tilt=0.0):
    """闪蝶。s=1 小（约 11px 宽），2 中，3+ 大。flap=None 时按 t 扇动；flap∈[0,1] 1=全开。"""
    if flap is None:
        ph = (t * speed) % 1.0
        flap = [1.0, 0.75, 0.4, 0.75][int(ph * 4)]
    f = max(0.18, flap)
    a = 4.2 * s + 1.2; b = 3.6 * s + 1.0
    edge = INK if s >= 2 else dk
    def P(pts, sg): return [(x + sg * px_ * f, y + py_ + tilt * sg * px_ * f) for px_, py_ in pts]
    fore = [(0, -0.15 * b), (0.55 * a, -0.95 * b), (1.0 * a, -1.05 * b), (1.05 * a, -0.55 * b), (0.75 * a, 0.05 * b), (0, 0.2 * b)]
    hind = [(0, 0.05 * b), (0.72 * a, 0.12 * b), (0.78 * a, 0.55 * b), (0.45 * a, 0.95 * b), (0.15 * a, 0.85 * b), (0, 0.55 * b)]
    for sg in (-1, 1):
        mh = _poly_mask(P(hind, sg)); mf = _poly_mask(P(fore, sg))
        cv.a[dilate(mh)] = edge; cv.a[mh] = mix(col, dk, 0.25)
        cv.a[dilate(mf)] = edge; cv.a[mf] = col
        if s >= 2 and f > 0.45:
            inner = [(0.12 * a, -0.1 * b), (0.5 * a, -0.7 * b), (0.78 * a, -0.62 * b), (0.55 * a, -0.05 * b)]
            cv.a[_poly_mask(P(inner, sg))] = hi
            # 翅缘白点
            for (px_, py_) in [(0.95 * a, -0.85 * b), (0.98 * a, -0.6 * b)]:
                cv.px(x + sg * px_ * f, y + py_, PAL['white'])
        elif f > 0.6:
            cv.px(x + sg * 0.5 * a * f, y - 0.5 * b, hi)
    cv.vline(x, y - int(0.35 * b), y + int(0.7 * b), INK)
    if s >= 2: cv.vline(x + 1, y - int(0.2 * b), y + int(0.5 * b), INK)
    al = 2 + s
    cv.line(x, y - int(0.35 * b), x - al // 2 - 1, y - int(0.35 * b) - al, INK)
    cv.line(x, y - int(0.35 * b), x + al // 2 + 1, y - int(0.35 * b) - al, INK)
    if sparkle:
        sx, sy = x + int(a * 1.2), y - int(b * 1.2)
        cv.px(sx, sy, PAL['white']); cv.px(sx - 1, sy, hi); cv.px(sx + 1, sy, hi); cv.px(sx, sy - 1, hi); cv.px(sx, sy + 1, hi)


def trail(cv, path, t, length=1.6, step=0.03, col=BLUE_H):
    """蝴蝶身后的亮线：path(t)->(x,y)。"""
    n = int(length / step)
    for i in range(n):
        tt = t - i * step
        if tt < 0: break
        x, y = path(tt)
        k = 1 - i / n
        if i % 2 == 0 or k > 0.6:
            cv.px(x, y + 1, col if k > 0.35 else mix(col, (90, 100, 120), 0.5))
        if k > 0.8 and i % 5 == 0:
            cv.px(x, y + 2, PAL['white'])


# ---------------------------------------------------------------- 雨 / 伞
def rain(cv, t, n=170, seed=11, speed=150, slant=0.35, col=hexc('a9b3c4'), excl=None, y_ground=H, splash=True, rect=None):
    r = rng(seed)
    x0 = r.uniform(-40, W + 20, n); y0 = r.uniform(0, H + 30, n); sp = r.uniform(0.8, 1.25, n) * speed
    L = r.integers(3, 6, n)
    x1, y1, x2, y2 = rect if rect else (0, 0, W, H)
    for i in range(n):
        y = (y0[i] + sp[i] * t) % (y_ground + 20) - 10
        x = x0[i] - slant * (sp[i] * t % (y_ground + 20))
        x = (x + 40) % (W + 60) - 40
        for k in range(L[i]):
            px_, py_ = int(x + slant * k), int(y + k)
            if not (x1 <= px_ < x2 and y1 <= py_ < y2): continue
            if excl is not None and excl(px_, py_): continue
            if py_ < y_ground: cv.px(px_, py_, col)
        if splash and y_ground - 3 <= y + L[i] < y_ground:
            gx = int(x + slant * L[i])
            if excl is None or not excl(gx, y_ground - 1):
                cv.px(gx - 1, y_ground - 1, col); cv.px(gx + 1, y_ground - 1, col)


def umbrella(cv, cx, top, rw, rh, t=0.0, col=UMB, dk=UMB_D, hi=UMB_H, handle_to=None, tilt=0):
    """暖黄伞。cx,top=伞顶；rw 半宽；rh 伞面高度。"""
    pts = []
    for i in range(0, 181, 6):
        a = math.radians(180 + i)
        pts.append((cx + math.cos(a) * rw, top + rh + math.sin(a) * rh))
    # scallop bottom
    nsc = 6
    base_y = top + rh
    for k in range(nsc, -1, -1):
        xk = cx - rw + 2 * rw * k / nsc
        pts.append((xk, base_y + (2 if k % 2 else 0)))
    im = Image.new('1', (W, H), 0)
    ImageDraw.Draw(im).polygon([(int(round(a)), int(round(b))) for a, b in pts], fill=1)
    m = np.array(im)
    cv.a[dilate(m)] = INK
    cv.a[m] = col
    # ribs
    for k in range(1, nsc):
        xk = cx - rw + 2 * rw * k / nsc
        cv.line(cx, top + 1, xk, base_y, dk)
    # highlight band
    for i in range(10, 70, 6):
        a = math.radians(180 + i)
        cv.px(cx + math.cos(a) * (rw - 3), top + rh + math.sin(a) * (rh - 3), hi)
    cv.rect(cx, top - 3, 1, 3, INK)
    if handle_to:
        cv.line(cx, base_y, handle_to[0], handle_to[1], INK)
    return m


# ---------------------------------------------------------------- 场景零件
def sky_band(cv, cols, y0=0, y1=H):
    n = len(cols)
    for y in range(y0, y1):
        f = (y - y0) / max(1, (y1 - y0 - 1)) * (n - 1)
        i = int(f); fr = f - i
        a = cols[min(i, n - 1)]; b = cols[min(i + 1, n - 1)]
        row = np.where(_DITH[y] < fr, 1, 0)
        cv.a[y, :] = np.where(row[:, None] == 1, np.array(b, np.uint8), np.array(a, np.uint8))


def buildings(cv, ground, seed=3, cols=((70, 76, 90), (88, 94, 108)), win=(150, 156, 170), lit=0.25, t=0.0, minh=40, maxh=110, wmin=18, wmax=40, laundry=True):
    r = rng(seed); x = -10
    while x < W + 10:
        w = int(r.integers(wmin, wmax)); h = int(r.integers(minh, maxh)); c = cols[int(r.integers(0, len(cols)))]
        cv.rect(x, ground - h, w, h, c)
        cv.rect(x, ground - h, w, 1, mix(c, (255, 255, 255), 0.12))
        cv.rect(x + w - 1, ground - h, 1, h, mix(c, (0, 0, 0), 0.25))
        for wy in range(ground - h + 4, ground - 6, 7):
            for wx in range(x + 3, x + w - 4, 6):
                v = r.random()
                if v < lit: cv.rect(wx, wy, 3, 4, win)
                elif v < 0.8: cv.rect(wx, wy, 3, 4, mix(c, (0, 0, 0), 0.3))
                if laundry and v > 0.97:
                    cv.hline(wx - 2, wx + 6, wy + 5, mix(c, (0, 0, 0), 0.4))
                    for k in range(3): cv.rect(wx - 1 + k * 3, wy + 6, 2, 3, mix(c, (255, 255, 255), 0.35))
        if r.random() < 0.4:   # 屋顶水箱/天线
            cv.rect(x + w // 3, ground - h - 5, 6, 5, mix(c, (0, 0, 0), 0.15)); cv.vline(x + w - 5, ground - h - 9, ground - h, mix(c, (0, 0, 0), 0.3))
        x += w + int(r.integers(0, 3))


def wires_line(cv, y, col, sag=6):
    for x in range(W):
        yy = y + int(sag * math.sin(x / W * math.pi))
        cv.px(x, yy, col)


def puddle(cv, x, y, w, col, t=0.0):
    cv.ellipse(x, y, w, max(1.5, w * 0.18), col)
    k = int(t * 6) % 4
    cv.ellipse(x + 2 - k, y, max(1, k + 1), 0.8, mix(col, (255, 255, 255), 0.4))


def bricks(cv, x, y, w, h, seed=4, col=(120, 104, 100)):
    """一堆碎砖"""
    r = rng(seed)
    pts = [(x, y + h), (x + w * 0.2, y + h * 0.3), (x + w * 0.45, y), (x + w * 0.7, y + h * 0.25), (x + w, y + h)]
    outline_poly(cv, pts, col)
    for i in range(int(w * h / 18)):
        bx = x + r.uniform(0.1, 0.9) * w; by = y + r.uniform(0.2, 1.0) * h
        if by < y + h - 1:
            c2 = mix(col, (0, 0, 0), r.uniform(0.0, 0.35)) if r.random() < 0.7 else mix(col, (200, 120, 100), 0.4)
            cv.rect(bx, by, int(r.integers(3, 6)), 2, c2); cv.px(bx, by + 2, mix(col, (0, 0, 0), 0.5))
    # 钢筋
    for i in range(3):
        bx = x + r.uniform(0.2, 0.8) * w
        cv.line(bx, y + h * 0.4, bx + r.uniform(-8, 8), y + h * 0.4 - r.uniform(8, 16), hexc('3a3036'))


def broken_wall(cv, x, ground, w, h, col=(150, 140, 130), seed=5):
    r = rng(seed)
    pts = [(x, ground), (x, ground - h)]
    n = 6
    for i in range(1, n + 1):
        pts.append((x + w * i / n, ground - h * r.uniform(0.35, 1.0)))
    pts.append((x + w, ground))
    outline_poly(cv, pts, col)
    for yy in range(int(ground - h) + 3, ground - 1, 4):
        off = 0 if (yy // 4) % 2 else 4
        for xx in range(int(x) + off, int(x + w) - 1, 8):
            if tuple(cv.a[yy, min(W - 1, max(0, xx))]) == tuple(col): cv.hline(xx, xx + 6, yy, mix(col, (0, 0, 0), 0.18))
    # 窗洞
    cv.rect(x + w * 0.3, ground - h * 0.55, 8, 10, INK)


def title_text(cv, s, x, y, col, size=24, outline=INK, anchor='mm'):
    f = ImageFont.truetype(ZH_FONT, size)
    cv.text(x, y, s, col, font=f, outline=outline, anchor=anchor)


def staff(cv, x, y, lines, col=hexc('c9cfd8'), k=1.0):
    if k <= 0: return
    for i, s in enumerate(lines):
        m = Canvas(KEY); m.text(x, y + i * 14, s, col)
        mm = np.any(m.a != np.array(KEY, np.uint8), axis=2) & (_DITH < k)
        cv.a[mm] = col
