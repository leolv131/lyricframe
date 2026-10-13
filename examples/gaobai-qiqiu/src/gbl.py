"""《告白气球》共用：色板、角色、红气球、告白进度 HUD、巴黎场景零件。"""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from px import *
from hd import Layer, solid, KEY, _DITH, sky_band, rain, title_text, umbrella, _poly_mask, radial_keep, to_ramp, GRAY_RAMP
from chars import char, head, symbol, thick_line, outline_poly
from ui import mitt, confetti
from lib import label, bubble, big_text, stamp, sat, warm, flash, fade_black, heart_bubble, snow, eyes_only, npc

INK = PAL['ink']; WHITE = PAL['white']
BAL = hexc('ff3b5c'); BAL_D = hexc('c8203e'); BAL_H = hexc('ff9aac')
CREAM = hexc('f6ecd8'); NAVY = hexc('2e3a6a'); MINT = hexc('9ad8c0'); GOLD = hexc('ffcf5a')
LIP = hexc('f08aa0')
GROUND = 150

SKY_DAY = [hexc('8cc8f0'), hexc('aed8f4'), hexc('d4ecf8'), hexc('f4f0e4')]
SKY_DUSK = [hexc('6a5a9a'), hexc('d87a9a'), hexc('ffa880'), hexc('ffd8a0')]
SKY_NIGHT = [hexc('121a3a'), hexc('1e2a5a'), hexc('34407a')]
SKY_DAWN = [hexc('8a9ad0'), hexc('f0b8c0'), hexc('ffe0b0')]
SKY_RAIN = [hexc('8a98b0'), hexc('a8b4c8'), hexc('c8d0dc')]


# ================================================================ 角色
def HE(cv, cx, feet, Hh, pose='stand', expr='normal', t=0.0, facing=0, back=False):
    return char(cv, 'he', cx, feet, Hh, pose, expr, t, facing, back)


def beret(cv, f, Hh):
    Wh = f['Wh']; cx = f['cx']; top = f['top']
    cv.ellipse(cx - Wh * 0.08, top + Hh * 0.04, Wh * 0.52, Hh * 0.2, hexc('f4ecdc'), INK)
    cv.px(cx - Wh * 0.08, top - Hh * 0.17, INK); cv.px(cx - Wh * 0.08, top - Hh * 0.17 - 1, INK)


def SHE(cv, cx, feet, Hh, pose='stand', expr='normal', t=0.0, facing=0, back=False, hat=True):
    f = char(cv, 'she', cx, feet, Hh, pose, expr, t, facing, back)
    if hat and not back: beret(cv, f, Hh)
    return f


def face(cv, who, cx, top, Hh, expr, t=0.0, hat=True):
    """近景：头 + 肩"""
    bc = hexc('aad2f0') if who == 'he' else hexc('ffb0be')
    cv.ellipse(cx, top + Hh * 1.6, Hh * 0.95, Hh * 0.62, bc, INK)
    f = head(cv, who, cx, top, Hh, expr, t=t)
    if who == 'she' and hat: beret(cv, f, Hh)
    return f


# ================================================================ 红气球（信物）
def balloon(cv, x, y, s=1.0, t=0.0, face_=False, string=True, str_len=None, sway=True, col=BAL):
    """爱心形红气球，(x,y) 为中心。s=1 约 14px 宽。"""
    if sway: x = x + math.sin(t * 2.2) * 1.2 * s
    r = 4.2 * s
    pts = []
    for i in range(0, 360, 10):
        a = math.radians(i)
        hx = 16 * math.sin(a) ** 3
        hy = -(13 * math.cos(a) - 5 * math.cos(2 * a) - 2 * math.cos(3 * a) - math.cos(4 * a))
        pts.append((x + hx * r / 16 * 1.6, y + hy * r / 16 * 1.6))
    m = _poly_mask(pts)
    cv.a[dilate(m)] = INK
    cv.a[m] = col
    cv.ellipse(x - r * 0.75, y - r * 0.7, max(1, r * 0.28), max(1, r * 0.38), BAL_H)
    by = y + r * 1.75
    cv.poly([(x - 1.5, by + 2), (x + 1.5, by + 2), (x, by - 1)], BAL_D)
    if face_:
        ey = y - r * 0.15
        cv.rect(x - r * 0.55, ey, max(1, s), max(2, s * 1.5), INK); cv.rect(x + r * 0.45, ey, max(1, s), max(2, s * 1.5), INK)
        hw = max(1, int(r * 0.5))
        for i in range(-hw, hw + 1):
            cv.px(x + i, y + r * 0.55 - (i * i) / (hw * hw) * r * 0.3, INK)
    if string:
        L = str_len if str_len is not None else 14 * s
        for k in range(int(L)):
            cv.px(x + math.sin(k * 0.35 + t * 3) * 1.2, by + 2 + k, hexc('5a5a6a'))
    return (x, by + 2 + (str_len if str_len is not None else 14 * s))


# ================================================================ 告白进度 HUD
PROG = [(39.87, 1), (59.85, 2), (87.95, 3), (145.21, 4), (201.51, 5)]


def prog_at(T):
    n = 0
    for t0, k in PROG:
        if T >= t0: n = k
    return n


def hud(cv, T):
    n = prog_at(T)
    x0 = W - 6 - 5 * 11
    sub = cv.a[3:19, x0 - 54:W - 3].astype(np.int16)
    cv.a[3:19, x0 - 54:W - 3] = (sub * 0.4 + np.array(hexc('2a2440')) * 0.6).astype(np.uint8)
    cv.text(x0 - 51, 4, '告白进度', WHITE)
    for i in range(5):
        on = i < n
        bx = x0 + 4 + i * 11; by = 9
        flash_new = on and any(abs(T - t0) < 0.6 and k == i + 1 for t0, k in PROG)
        col = BAL if on else hexc('6a6480')
        if flash_new and int(T * 10) % 2: col = WHITE
        balloon(cv, bx, by, 0.75, T, string=False, sway=False, col=col)
    for t0, k in PROG:
        if 0 <= T - t0 < 1.2:
            big_text(cv, x0 + 20, 26 - int((T - t0) * 6), '+1', BAL, size=12, outline=WHITE)


# ================================================================ 巴黎场景零件
def eiffel(cv, x, ground, h, col=hexc('5a4a5a'), lights=0.0, t=0.0):
    """原创简笔铁塔（剪影）。x=中心，h=高度"""
    w = h * 0.42
    top = ground - h
    pts = [(x - w / 2, ground), (x - w * 0.12, top + h * 0.35), (x - 1.5, top), (x + 1.5, top), (x + w * 0.12, top + h * 0.35), (x + w / 2, ground),
           (x + w * 0.28, ground), (x, ground - h * 0.18), (x - w * 0.28, ground)]
    cv.poly(pts, col)
    # 平台
    for fy, fw in ((0.62, 0.22), (0.35, 0.12)):
        y = top + h * fy
        cv.rect(x - w * fw - 2, y, w * fw * 2 + 4, max(2, h // 40), col)
    # 交叉格
    for i in range(6):
        y = ground - h * (0.1 + i * 0.1)
        ww = w / 2 * (1 - (ground - y) / h) * 1.1
        cv.line(x - ww, y, x + ww * 0.3, y - h * 0.08, mix(col, (255, 255, 255), 0.15))
    cv.vline(x, top - h * 0.06, top, col)
    if lights > 0:
        r = rng(7)
        for i in range(int(40 * lights)):
            yy = r.uniform(top, ground); ww = w / 2 * (1 - (ground - yy) / h)
            xx = x + r.uniform(-ww, ww)
            if (t * 6 + i) % 3 < 1.2: cv.px(xx, yy, hexc('fff4b0'))
        cv.px(x, top - h * 0.06, hexc('fff8d0'))


def paris_row(cv, ground, seed=3, x0=-10, x1=None, cols=None, roof=hexc('7a88a8'), lit=0.0, night=0.0, hmin=54, hmax=86):
    """奥斯曼式楼房：奶白立面 + 灰蓝斜屋顶 + 小阳台"""
    x1 = W + 10 if x1 is None else x1
    cols = cols or [hexc('f0e2c8'), hexc('e8d4b8'), hexc('f4e8d4'), hexc('e0ccb0')]
    r = rng(seed); x = x0
    while x < x1:
        w = int(r.integers(34, 54)); h = int(r.integers(hmin, hmax)); c = mix(cols[int(r.integers(0, len(cols)))], hexc('2a2a4a'), night * 0.55)
        rf = mix(roof, hexc('1a1e34'), night * 0.5)
        cv.rect(x, ground - h, w, h, c); cv.vline(x, ground - h, ground, mix(c, INK, 0.3))
        cv.poly([(x - 1, ground - h), (x + 4, ground - h - 12), (x + w - 4, ground - h - 12), (x + w + 1, ground - h)], rf)
        for k in range(2): cv.rect(x + 8 + k * (w - 22), ground - h - 10, 5, 6, mix(rf, WHITE, 0.3))   # 老虎窗
        cv.rect(x + w // 2 - 1, ground - h - 18, 3, 7, hexc('b06a5a'))   # 烟囱
        for wy in range(ground - h + 6, ground - 14, 13):
            for wx in range(x + 4, x + w - 7, 10):
                lit_on = r.random() < lit
                cv.rect(wx, wy, 5, 8, hexc('ffe08a') if lit_on else mix(hexc('6a7a98'), INK, night * 0.4))
                cv.rect(wx - 1, wy + 8, 7, 1, INK)                        # 小阳台栏杆
                cv.px(wx, wy + 7, INK); cv.px(wx + 4, wy + 7, INK)
        x += w


def seine(cv, y0, y1, t, col=hexc('6aa0c8'), night=0.0):
    c = mix(col, hexc('1a2448'), night)
    cv.rect(0, y0, W, y1 - y0, c)
    for i in range(14):
        x = (i * 37 + t * 8 * (1 + i % 3)) % (W + 20) - 10
        y = y0 + 3 + (i * 7) % max(1, (y1 - y0 - 4))
        cv.hline(x, x + 6 + i % 4, y, mix(c, WHITE, 0.35 if night < 0.5 else 0.15))
    cv.rect(0, y0 - 3, W, 3, hexc('c8b89a') if night < 0.5 else hexc('4a4a5a'))
    cv.hline(0, W, y0 - 3, INK)


def boat(cv, x, y, t, lights=False):
    cv.poly([(x - 30, y), (x + 34, y), (x + 28, y + 7), (x - 26, y + 7)], hexc('f4f0e8'))
    cv.hline(x - 30, x + 34, y, INK); cv.rect(x - 22, y - 7, 40, 7, hexc('d8e8f4')); cv.rect(x - 22, y - 8, 40, 1, INK)
    for i in range(6): cv.rect(x - 19 + i * 6, y - 5, 4, 3, hexc('ffe08a') if lights else hexc('8ab0d0'))


def cafe(cv, x, ground, w=150, t=0.0, night=0.0, rainy=False):
    """咖啡馆立面：海军蓝条纹遮阳棚 + CAFÉ 招牌 + 室外桌椅"""
    c = mix(hexc('f4e8d0'), hexc('3a3a5a'), night * 0.5)
    cv.rect(x, ground - 96, w, 96, c); cv.rect(x, ground - 96, w, 1, INK)
    cv.rect(x, ground - 96, w, 14, NAVY); title_text(cv, 'CAFÉ', x + w // 2, ground - 89, hexc('fff4dc'), size=12, outline=NAVY)
    # 大窗
    for i in range(3):
        wx = x + 8 + i * (w - 16) // 3
        cv.rect(wx, ground - 72, (w - 16) // 3 - 6, 44, INK); cv.rect(wx + 1, ground - 71, (w - 16) // 3 - 8, 42, hexc('ffe8b0') if night > 0.3 else hexc('c8e0ec'))
    # 遮阳棚（条纹）
    ay = ground - 74
    for i in range(w // 10 + 2):
        cx_ = x - 6 + i * 10
        cv.poly([(cx_, ay), (cx_ + 10, ay), (cx_ + 12, ay + 14), (cx_ + 2, ay + 14)], NAVY if i % 2 else hexc('f4f0e8'))
    cv.hline(x - 6, x + w + 8, ay + 14, INK)
    for i in range(w // 10 + 2):
        cv.ellipse(x - 1 + i * 10, ay + 15, 5, 2, NAVY if i % 2 else hexc('f4f0e8'))


def table(cv, x, y, w=36, cloth=False):
    cv.rect(x - w // 2, y, w, 3, INK); cv.rect(x - w // 2 + 1, y + 1, w - 2, 1, hexc('f4f0e8') if cloth else hexc('c8b8a0'))
    cv.rect(x - 1, y + 3, 2, GROUND - y - 3, INK); cv.rect(x - 6, GROUND - 2, 12, 2, INK)


def cup(cv, x, y, s=1, lip=False, steam_t=None):
    w, h = 8 * s, 6 * s
    cv.rect(x - w // 2 - 1, y - 1, w + 2, h + 2, INK); cv.rect(x - w // 2, y, w, h, WHITE)
    cv.rect(x - w // 2, y, w, max(1, s), hexc('6a4030'))
    cv.rect(x + w // 2, y + s, 2 * s, 3 * s, INK); cv.rect(x + w // 2 + s // 2, y + s + s // 2, max(1, s), 2 * s, WHITE)
    cv.rect(x - w // 2 - 2 * s, y + h + 1, w + 4 * s, max(1, s), INK)
    if lip:
        cv.ellipse(x - w // 4, y + s, 1.6 * s, 0.9 * s, LIP)
    if steam_t is not None:
        for k in range(2):
            for j in range(4 * s):
                cv.px(x - 2 * s + k * 4 * s + math.sin(j * 0.6 + steam_t * 4 + k) * s, y - 2 - j, hexc('e8e8f0'))


def flower_shop_front(cv, x, ground, w=110, night=0.0):
    c = mix(hexc('e8f4ec'), hexc('3a4a5a'), night * 0.5)
    cv.rect(x, ground - 84, w, 84, c); cv.rect(x, ground - 84, w, 14, hexc('4a9a6a'))
    title_text(cv, 'FLEURS', x + w // 2, ground - 77, hexc('fff6e0'), size=12, outline=hexc('2a6a4a'))
    cv.rect(x + 10, ground - 62, w - 20, 36, INK); cv.rect(x + 11, ground - 61, w - 22, 34, hexc('dceef0'))
    r = rng(5)
    for i in range(10):
        bx = x + 4 + i * (w - 8) // 10
        cv.rect(bx, ground - 12, 8, 12, hexc('8a9aa8'))
        for j in range(3):
            cv.ellipse(bx + 4 + r.integers(-2, 3), ground - 15 + r.integers(-2, 2), 2.5, 2.5, [hexc('ff8aa8'), hexc('ffd35a'), hexc('f6f2e6'), hexc('c87aff'), hexc('ff9a4a')][int(r.integers(0, 5))])


def pigeon(cv, x, y, t, fly=0.0, flip=False):
    if fly <= 0:
        cv.ellipse(x, y, 4, 3, hexc('9aa0b0'), INK); cv.ellipse(x + (3 if not flip else -3), y - 3, 2, 2, hexc('9aa0b0'), INK)
        cv.px(x + (5 if not flip else -5), y - 3, hexc('e0a040'))
    else:
        fl = int(t * 10) % 2
        cv.rect(x - 2, y, 5, 3, hexc('9aa0b0'))
        cv.line(x - 2, y, x - 7, y - (4 if fl else -2), INK); cv.line(x + 2, y, x + 7, y - (4 if fl else -2), INK)


def leaves(cv, t, n=40, seed=5, speed=22, cols=None):
    cols = cols or [hexc('ffb84a'), hexc('f08a3a'), hexc('ffd36a'), hexc('d8703a')]
    r = rng(seed)
    for i in range(n):
        x0, y0, sp = r.uniform(0, W), r.uniform(0, H), r.uniform(0.6, 1.4)
        y = (y0 + t * speed * sp) % (H + 10) - 5
        x = (x0 + math.sin(t * 1.5 + i) * 8 - t * 6) % W
        c = cols[i % len(cols)]
        if int(t * 4 + i) % 2: cv.rect(x, y, 3, 2, c)
        else: cv.rect(x, y, 2, 3, c)


def trees_row(cv, ground, t, autumn=False, seed=9, n=6):
    r = rng(seed)
    for i in range(n):
        x = 20 + i * (W // n) + int(r.integers(-6, 6))
        cv.rect(x - 2, ground - 40, 4, 40, hexc('6a4a3a'))
        for j in range(20):
            a = r.uniform(0, 6.28); rr = r.uniform(0, 16)
            c = ([hexc('ffb84a'), hexc('f08a3a'), hexc('ffd36a')] if autumn else [hexc('6aba6a'), hexc('4a9a5a'), hexc('8ad07a')])[j % 3]
            cv.ellipse(x + math.cos(a) * rr, ground - 50 + math.sin(a) * rr * 0.7, 5, 5, c)


def fireworks(cv, t, seed=1, n=5, cols=None):
    cols = cols or [hexc('ffd35a'), hexc('ff8aa8'), hexc('8fd6ff'), hexc('c8a0ff'), WHITE]
    r = rng(seed)
    for i in range(n):
        t0 = r.uniform(0, 1.6); cx, cy = r.uniform(30, W - 30), r.uniform(20, 80)
        period = 2.0
        u = ((t - t0) % period) / period
        if t < t0: continue
        if u < 0.2:
            cv.px(cx, cy + (0.2 - u) * 300, WHITE)
        else:
            k = (u - 0.2) / 0.8
            R = 4 + k * 26
            c = cols[i % len(cols)]
            for a in range(0, 360, 20):
                px_, py_ = cx + math.cos(math.radians(a)) * R, cy + math.sin(math.radians(a)) * R + k * k * 6
                if k < 0.85 or int(t * 12 + a) % 2: cv.px(px_, py_, c)
                if k < 0.5: cv.px(cx + math.cos(math.radians(a)) * R * 0.6, cy + math.sin(math.radians(a)) * R * 0.6, WHITE)


def ground_band(cv, y, col=hexc('d8c8a8'), line=True):
    cv.rect(0, y, W, H - y, col)
    if line: cv.hline(0, W, y, INK)
    for x in range(0, W, 16): cv.vline(x, y + 1, H, mix(col, INK, 0.12))


def heart_px(cv, x, y, s=1, col=BAL):
    rows = ['.RR.RR.', 'RRRRRRR', 'RRRRRRR', '.RRRRR.', '..RRR..', '...R...']
    for j, row in enumerate(rows):
        for i, ch in enumerate(row):
            if ch == 'R': cv.rect(x + i * s - 3 * s, y + j * s - 3 * s, s, s, col)
