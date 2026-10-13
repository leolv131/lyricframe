"""v3 引擎：先布光再画物。暗调 + 点光源 + 像素光晕 + 倒影 + 小号写实比例人物（剪影 + 轮廓光）。"""
import math
import numpy as np
from PIL import Image, ImageDraw
from px import Canvas, W, H, hexc, mix, clamp, ease, lerp, rng, dilate, PAL

_B4 = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) / 16.0
DITH = np.tile(_B4, (H // 4 + 1, W // 4 + 1))[:H, :W]
YY, XX = np.mgrid[0:H, 0:W].astype(np.float32)
INK = hexc('0c0a14')


def C(h): return np.array(hexc(h), np.float32) / 255.0


# ---------------------------------------------------------------- 光
class Light:
    def __init__(self, x, y, col, r, i=1.0, flick=0.0):
        self.x, self.y, self.col, self.r, self.i, self.flick = x, y, C(col) if isinstance(col, str) else np.array(col, np.float32), r, i, flick


def lightmap(lights, ambient, t=0.0, steps=7):
    L = np.zeros((H, W, 3), np.float32) + np.array(ambient, np.float32)
    for l in lights:
        if l.i <= 0: continue
        inten = l.i * (1 - l.flick * (0.5 + 0.5 * math.sin(t * 23 + l.x)) * (math.sin(t * 7.3 + l.y) > 0.6))
        d = np.sqrt((XX - l.x) ** 2 + ((YY - l.y) * 1.1) ** 2) / l.r
        f = np.clip(1 - d, 0, 1) ** 1.7 * inten
        L += f[..., None] * l.col
    # 量化成几档 + 有序抖动 → 像素感的光
    q = np.floor(L * steps + DITH[..., None] * 0.95) / steps
    return q


def lit(cv, lights, ambient, t=0.0, steps=7, emissive=None):
    """cv.a 视为固有色；乘以光照。emissive: bool mask，这些像素自己发光不受光照影响。"""
    L = lightmap(lights, ambient, t, steps)
    a = cv.a.astype(np.float32) / 255.0
    out = np.clip(a * L, 0, 1)
    if emissive is not None:
        out = np.where(emissive[..., None], a, out)
    cv.a = (out * 255).astype(np.uint8)


def glow(cv, x, y, r, col, k=0.55):
    """像素光晕：向外三圈台阶式衰减，叠加。"""
    if r <= 0.5 or k <= 0: return
    c = np.array(hexc(col) if isinstance(col, str) else col, np.float32)
    d = np.sqrt((XX - x) ** 2 + (YY - y) ** 2) / r
    f = np.clip(1 - d, 0, 1) ** 2 * k
    f = np.floor(f * 4 + DITH * 0.9) / 4
    a = cv.a.astype(np.float32)
    cv.a = np.clip(a + f[..., None] * c, 0, 255).astype(np.uint8)


def reflect(cv, horizon, y0, y1, t, k=0.55, tint='1a2440', x0=0, x1=W):
    """把 horizon 以上的画面倒映到 [y0,y1) 的湿地面上（带水波）。"""
    src = cv.a.copy()
    tc = np.array(hexc(tint), np.float32)
    for y in range(y0, min(y1, H)):
        sy = horizon - (y - horizon) - 1
        if sy < 0: continue
        off = int(round(math.sin(y * 0.9 + t * 4) * (1 + (y - horizon) * 0.03)))
        row = np.roll(src[sy], off, axis=0).astype(np.float32)
        base = cv.a[y].astype(np.float32)
        m = (DITH[y] < k * (1 - (y - y0) / max(1, (y1 - y0)) * 0.5))
        mixed = row * 0.6 + tc * 0.4
        r = np.where(m[:, None], mixed, base)
        cv.a[y, x0:x1] = r[x0:x1].astype(np.uint8)


def sky(cv, cols, y0=0, y1=H):
    n = len(cols)
    for y in range(y0, y1):
        f = (y - y0) / max(1, (y1 - y0 - 1)) * (n - 1)
        i = int(f); fr = f - i
        a = np.array(hexc(cols[min(i, n - 1)]), np.uint8); b = np.array(hexc(cols[min(i + 1, n - 1)]), np.uint8)
        cv.a[y, :] = np.where((DITH[y] < fr)[:, None], b, a)


# ---------------------------------------------------------------- 小号写实比例人物（1:5.5）
def person(cv, x, feet, h, pose='stand', body='3a3e52', hair='1a1622', skin='d8a888', facing=1, t=0.0, style='he', walk_ph=0.0):
    """在 cv 上画人物，返回 (mask, anchors)。h=身高像素。"""
    L = Canvas((255, 0, 255))
    hr = max(2, h * 0.095)
    def P(pts, col): L.poly([(x + px_ * facing, feet - py_) for px_, py_ in pts], hexc(col))
    def E(cx, cy, rx, ry, col): L.ellipse(x + cx * facing, feet - cy, rx, ry, hexc(col))
    leg = h * 0.46; torso = h * 0.32; sh = h * 0.12
    hip_y = leg; neck_y = leg + torso
    if pose in ('stand', 'walk', 'hold', 'arms_open', 'look_up'):
        sw = math.sin(walk_ph * math.pi * 2) * h * 0.12 if pose == 'walk' else 0
        for s in (-1, 1):
            P([(s * h * 0.03 - 1, hip_y), (s * h * 0.03 + 1.5, hip_y), (s * h * 0.05 + s * sw * (1 if s > 0 else -1) + 1.2, 0), (s * h * 0.05 + s * sw * (1 if s > 0 else -1) - 1.2, 0)], body if style == 'he' else '3a3a48')
        top_y = feet
    elif pose == 'sit':   # 坐在台阶 / 边沿上，腿往前
        P([(-h * 0.04, hip_y * 0.55), (h * 0.22, hip_y * 0.55), (h * 0.22, hip_y * 0.45), (-h * 0.04, hip_y * 0.42)], body)
        P([(h * 0.18, hip_y * 0.55), (h * 0.23, hip_y * 0.55), (h * 0.24, 0), (h * 0.18, 0)], body)
        hip_y = hip_y * 0.5; neck_y = hip_y + torso
    elif pose == 'kneel':
        P([(-h * 0.06, hip_y * 0.5), (h * 0.04, hip_y * 0.5), (h * 0.02, 0), (-h * 0.18, 0), (-h * 0.18, h * 0.04)], body)
        hip_y = hip_y * 0.5; neck_y = hip_y + torso
    # 躯干（衣服）
    tw = h * 0.13
    if style == 'she':
        P([(-tw * 0.7, neck_y - 1), (tw * 0.7, neck_y - 1), (tw * 1.25, hip_y - h * 0.08), (-tw * 1.25, hip_y - h * 0.08)], body)   # 外套下摆
    else:
        P([(-tw, neck_y - 1), (tw, neck_y - 1), (tw * 0.85, hip_y), (-tw * 0.85, hip_y)], body)
    # 手臂
    ay = neck_y - 2
    if pose == 'arms_open':
        for s in (-1, 1): L.line(x + s * tw, feet - ay, x + s * (tw + h * 0.2), feet - ay - h * 0.14, hexc(body)); L.line(x + s * tw, feet - ay + 1, x + s * (tw + h * 0.2), feet - ay - h * 0.13, hexc(body))
    elif pose in ('hold', 'sit', 'kneel'):
        L.line(x + tw * facing, feet - ay, x + (tw + h * 0.16) * facing, feet - ay + h * 0.1, hexc(body))
        L.line(x + tw * facing, feet - ay + 1, x + (tw + h * 0.16) * facing, feet - ay + h * 0.1 + 1, hexc(body))
        L.line(x - tw * facing, feet - ay, x - (tw - 1) * facing, feet - ay + torso * 0.8, hexc(body))
    else:
        sw = math.sin(walk_ph * math.pi * 2) * 2 if pose == 'walk' else 0
        for s in (-1, 1): L.line(x + s * tw, feet - ay, x + s * tw + s * 1 + sw * s, feet - ay + torso * 0.85, hexc(body))
    # 头
    hy = neck_y + hr * 1.05 + (1 if pose == 'look_up' else 0)
    E(0, hy, hr, hr * 1.1, skin)
    if style == 'she':
        E(-0.4, hy + hr * 0.3, hr * 1.15, hr * 0.9, hair); L.rect(x - hr * 1.15, feet - hy - hr * 0.2, hr * 2.3, hr * 1.1, hexc(hair))
    else:
        E(-0.6, hy + hr * 0.45, hr * 1.05, hr * 0.75, hair)
        L.px(x + hr * 0.3, feet - hy - hr * 1.15, hexc(hair)); L.px(x - hr * 0.5, feet - hy - hr * 1.2, hexc(hair))
    m = np.any(L.a != np.array([255, 0, 255], np.uint8), axis=2)
    cv.a[m] = L.a[m]
    return m, dict(head=(x, feet - hy), hand=(x + (tw + h * 0.16) * facing, feet - ay + h * 0.1), neck=(x, feet - neck_y))


def rim(cv, mask, lx, ly, col='ffcf8a', k=1.0, maxd=None):
    """轮廓光：人物边缘朝向光源的那一侧亮起来。"""
    if k <= 0: return
    dx = np.sign(lx - XX); dy = np.sign(ly - YY)
    sx = np.roll(mask, -1, axis=1); sx2 = np.roll(mask, 1, axis=1)
    sy = np.roll(mask, -1, axis=0); sy2 = np.roll(mask, 1, axis=0)
    edge_r = mask & ~sx; edge_l = mask & ~sx2; edge_d = mask & ~sy; edge_u = mask & ~sy2
    e = (edge_r & (dx > 0)) | (edge_l & (dx < 0)) | (edge_u & (dy < 0)) | (edge_d & (dy > 0))
    if maxd:
        e &= np.sqrt((XX - lx) ** 2 + (YY - ly) ** 2) < maxd
    e &= DITH < k
    cv.a[e] = hexc(col)


# ---------------------------------------------------------------- 场景零件
def skyline(cv, base, seed, col, win_col, lit_p, off=0.0, hmin=20, hmax=60, wmin=10, wmax=26, t=0.0, emis=None):
    r = rng(seed); x = -40 - int(off)
    xs = []
    while x < W + 40:
        w = int(r.integers(wmin, wmax)); h = int(r.integers(hmin, hmax))
        xs.append((x, w, h, r.integers(0, 1 << 30)))
        x += w + int(r.integers(0, 3))
    for (x, w, h, s) in xs:
        cv.rect(x, base - h, w, h, hexc(col))
        rr = rng(int(s))
        if rr.random() < 0.3: cv.rect(x + w // 3, base - h - 4, 2, 4, hexc(col))
        for wy in range(base - h + 3, base - 3, 5):
            for wx in range(x + 2, x + w - 2, 4):
                v = rr.random()
                if v < lit_p:
                    on = not ((t * 0.3 + v * 50) % 9 < 0.15)
                    if on:
                        cv.rect(wx, wy, 2, 2, hexc(win_col))
                        if emis is not None and 0 <= wy < H:
                            emis[max(0, wy):wy + 2, max(0, wx):max(0, wx + 2)] = True


def rain(cv, t, n=150, seed=1, speed=150, slant=0.3, col='8a94b0', y_ground=H, excl=None, length=(3, 6)):
    r = rng(seed)
    x0 = r.uniform(-40, W + 20, n); y0 = r.uniform(0, H + 30, n); sp = r.uniform(0.8, 1.25, n) * speed
    Ls = r.integers(length[0], length[1], n); c = hexc(col)
    for i in range(n):
        y = (y0[i] + sp[i] * t) % (y_ground + 20) - 10
        x = (x0[i] - slant * (sp[i] * t % (y_ground + 20)) + 40) % (W + 60) - 40
        for k in range(Ls[i]):
            px_, py_ = int(x + slant * k), int(y + k)
            if 0 <= px_ < W and 0 <= py_ < min(H, y_ground):
                if excl is None or not excl(px_, py_): cv.a[py_, px_] = c


def fireflies(cv, t, n=14, seed=3, box=(0, 0, W, H), col='ffe08a', emis=None):
    r = rng(seed)
    for i in range(n):
        bx = r.uniform(box[0], box[2]); by = r.uniform(box[1], box[3])
        x = bx + math.sin(t * 0.7 + i) * 8; y = by - (t * r.uniform(2, 5)) % 30 + math.cos(t * 1.1 + i * 2) * 3
        on = (math.sin(t * 2.3 + i * 1.7) > -0.3)
        if on and 0 <= int(y) < H and 0 <= int(x) < W:
            cv.px(x, y, hexc(col))
            if emis is not None: emis[int(y), int(x)] = True


def butterfly_glow(cv, x, y, s, t, col='2f8cff', hi='8fd6ff', emis=None):
    ph = (t * 5) % 1.0
    f = [1.0, 0.7, 0.35, 0.7][int(ph * 4)]
    a = 2.6 * s + 1; b = 2.2 * s + 1
    pts = []
    for sg in (-1, 1):
        fore = [(0, -0.15 * b), (0.55 * a, -0.95 * b), (1.0 * a, -1.05 * b), (1.05 * a, -0.55 * b), (0.75 * a, 0.05 * b), (0, 0.2 * b)]
        hind = [(0, 0.05 * b), (0.72 * a, 0.12 * b), (0.78 * a, 0.55 * b), (0.45 * a, 0.95 * b), (0, 0.55 * b)]
        for poly, c in ((hind, mix(hexc(col), (20, 40, 90), 0.3)), (fore, hexc(col))):
            P = [(x + sg * px_ * max(0.2, f), y + py_) for px_, py_ in poly]
            im = Image.new('1', (W, H), 0); ImageDraw.Draw(im).polygon([(int(round(p)), int(round(q))) for p, q in P], fill=1)
            m = np.array(im); cv.a[m] = c
            if emis is not None: emis |= m
        cv.px(x + sg * 0.5 * a * f, y - 0.5 * b, hexc(hi))
    cv.px(x, y, INK); cv.px(x, y + 1, INK)


def trail(cv, path, t, length=2.0, step=0.04, col='8fd6ff', emis=None):
    n = int(length / step)
    for i in range(n):
        tt = t - i * step
        if tt < 0: break
        x, y = path(tt)
        k = 1 - i / n
        if (i % 2 == 0 or k > 0.6) and 0 <= int(y + 1) < H and 0 <= int(x) < W:
            cv.px(x, y + 1, hexc(col) if k > 0.4 else mix(hexc(col), (30, 40, 70), 0.6))
            if emis is not None and k > 0.4: emis[int(y + 1), int(x)] = True


def umbrella(cv, cx, top, rw, rh, col='ffc94a', dk='c88a20'):
    pts = []
    for i in range(0, 181, 10):
        a = math.radians(180 + i)
        pts.append((cx + math.cos(a) * rw, top + rh + math.sin(a) * rh))
    im = Image.new('1', (W, H), 0); ImageDraw.Draw(im).polygon([(int(round(a)), int(round(b))) for a, b in pts], fill=1)
    m = np.array(im); cv.a[m] = hexc(col)
    for k in range(1, 4):
        cv.line(cx, top + 1, cx - rw + 2 * rw * k / 4, top + rh, hexc(dk))
    return m


def mist(cv, t, y, h, col='9aa8c8', k=0.35, speed=4, seed=2):
    c = np.array(hexc(col), np.float32)
    for yy in range(max(0, y), min(H, y + h)):
        u = 1 - abs((yy - y) / h * 2 - 1)
        dens = k * u
        xs = np.arange(W)
        wave = 0.5 + 0.5 * np.sin(xs * 0.05 + t * speed * 0.1 + yy * 0.3 + seed)
        m = DITH[yy] < dens * wave
        row = cv.a[yy].astype(np.float32)
        row[m] = row[m] * 0.4 + c * 0.6
        cv.a[yy] = row.astype(np.uint8)
