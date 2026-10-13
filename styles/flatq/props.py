"""道具 / 场景 / HUD"""
import math
import numpy as np
import skia
from fq import *
import people as P

PINK = '#ff5fa2'           # 粉色头盔：全片唯一的高饱和粉


# ---------------------------------------------------------------- HUD: phone status bar
def status_bar(f, time_str, battery=62, charging=False, dark=True, a=1.0):
    col = '#ffffff' if dark else INK
    f.rect(0, 0, W, 64, '#000000', a=0.18 * a)
    f.text(52, 46, time_str, 36, col, 'bold', a=a)
    # signal
    for i in range(4):
        h = 10 + i * 6
        f.rect(1520 + i * 12, 44 - h, 8, h, col, r=2, a=a)
    for i in range(3):
        r = 7 + i * 7
        p = skia.Path(); p.addArc(skia.Rect.MakeLTRB(1610 - r, 44 - r, 1610 + r, 44 + r), 225, 90)
        f.c.drawPath(p, f.stroke(col, 4, a))
    f.text(1735, 46, f'{int(battery)}%', 28, col, 'bold', 'right', a=a)
    bx, by = 1748, 22
    f.rect(bx, by, 64, 28, '#000000', col, 3, r=7, a=a * 0.25)
    f.rect(bx + 66, by + 9, 5, 10, col, r=2, a=a)
    lvl = clamp(battery / 100)
    bc = '#ff4a5a' if battery <= 10 else ('#5ad67a' if battery >= 90 or charging else col)
    f.rect(bx + 4, by + 4, 56 * lvl, 20, bc, r=4, a=a)
    if charging:
        f.poly([(bx + 34, by + 3), (bx + 24, by + 16), (bx + 32, by + 16), (bx + 28, by + 26), (bx + 40, by + 12), (bx + 32, by + 12)], '#ffe27a', INK, 2, a=a)


# ---------------------------------------------------------------- helmet
def helmet(f, x, y, s=1.0, a=1.0, glow=0.0):
    """pink scooter helmet, centre (x,y)"""
    if glow:
        f.radial(x, y, 120 * s, PINK, 0.0, a=0.35 * glow)
    p = skia.Path()
    p.moveTo(x - 62 * s, y + 30 * s)
    p.cubicTo(x - 66 * s, y - 52 * s, x + 66 * s, y - 52 * s, x + 62 * s, y + 30 * s)
    p.close()
    f.path(p, PINK, INK, 5 * s, a)
    f.rect(x - 66 * s, y + 22 * s, 132 * s, 18 * s, '#e0408a', INK, 5 * s, r=8 * s, a=a)
    f.curve([(x - 36 * s, y - 22 * s), (x - 10 * s, y - 36 * s)], '#ffb3d5', 9 * s, a)
    f.rect(x - 20 * s, y - 40 * s, 40 * s, 10 * s, '#ffffff', INK, 3 * s, r=5 * s, a=a * 0.9)   # vent stripe
    # strap
    f.curve([(x - 52 * s, y + 40 * s), (x - 40 * s, y + 70 * s), (x - 20 * s, y + 76 * s)], INK, 4 * s, a)


# ---------------------------------------------------------------- bowl of 烩面
def huimian(f, x, y, s=1.0, t=0.0, steam=True):
    # steam
    if steam:
        for k in range(3):
            ph = t * 1.6 + k * 1.3
            xs = x - 50 * s + k * 50 * s
            pts = [(xs + math.sin(ph + j * 0.9) * 12 * s, y - 70 * s - j * 30 * s) for j in range(5)]
            f.curve(pts, '#ffffff', 7 * s, a=0.55 - 0.1 * k)
    # bowl
    p = skia.Path(); p.moveTo(x - 130 * s, y - 30 * s); p.cubicTo(x - 120 * s, y + 80 * s, x + 120 * s, y + 80 * s, x + 130 * s, y - 30 * s); p.close()
    f.path(p, '#ffffff', INK, 5 * s)
    f.rect(x - 105 * s, y - 30 * s + 52 * s, 210 * s, 10 * s, '#4a86d8', None, a=0.9)  # blue rim band
    f.oval(x, y - 30 * s, 130 * s, 26 * s, '#f0c48a', INK, 5 * s)              # broth
    # wide noodles
    for k in range(6):
        xx = x - 95 * s + k * 36 * s
        f.curve([(xx, y - 36 * s), (xx + 14 * s, y - 26 * s), (xx + 4 * s, y - 18 * s)], '#fff2cc', 11 * s)
        f.curve([(xx, y - 36 * s), (xx + 14 * s, y - 26 * s), (xx + 4 * s, y - 18 * s)], '#e8c98a', 2 * s)
    # mutton slices + greens
    for k, (dx, dy) in enumerate([(-50, -38), (30, -42), (70, -30)]):
        f.oval(x + dx * s, y + dy * s, 20 * s, 9 * s, '#c27a5a', INK, 3 * s)
    for k, (dx, dy) in enumerate([(-10, -34), (-80, -28), (95, -38)]):
        f.oval(x + dx * s, y + dy * s, 9 * s, 5 * s, '#4ab05a', None)


def chopsticks(f, x, y, s=1.0, ang=-0.4):
    for k in (0, 1):
        dx = math.cos(ang) * 150 * s; dy = math.sin(ang) * 150 * s
        f.line(x + k * 10 * s, y, x + k * 10 * s + dx, y + dy, '#d9a46a', 8 * s)
        f.line(x + k * 10 * s, y, x + k * 10 * s + dx, y + dy, INK, 2 * s, a=0.3)


# ---------------------------------------------------------------- e-bike (side view) + riders
def ebike(f, x, ground, s=1.0, t=0.0, moving=True, back_rider=False, helmet_on_seat=False, rider_expr='lonely', back_expr='love', rider='he', body_col='#7fd3c6'):
    """小电驴（侧视）。x = 车身中点。"""
    wr = 40 * s
    spin = t * 12 if moving else 0
    bob = (math.sin(t * 22) * 1.5 * s) if moving else 0
    for wx in (x - 135 * s, x + 140 * s):
        f.circle(wx, ground - wr, wr, '#2e2a38', INK, 5 * s)
        f.circle(wx, ground - wr, wr * 0.48, '#c8cbd6', INK, 4 * s)
        for k in range(3):
            a = spin + k * 2.09
            f.line(wx, ground - wr, wx + math.cos(a) * wr * 0.42, ground - wr + math.sin(a) * wr * 0.42, INK, 3 * s)
    by = ground - wr + bob
    # rear cowl
    f.blob([(x - 190 * s, by - 20 * s), (x - 185 * s, by - 80 * s), (x - 30 * s, by - 92 * s), (x - 10 * s, by - 40 * s), (x - 40 * s, by - 10 * s), (x - 160 * s, by - 6 * s)], body_col, INK, 5 * s)
    # footboard
    f.rect(x - 40 * s, by - 34 * s, 120 * s, 22 * s, '#3a3a4a', INK, 5 * s, r=8 * s)
    # front shield + column
    f.blob([(x + 60 * s, by - 20 * s), (x + 110 * s, by - 30 * s), (x + 150 * s, by - 170 * s), (x + 120 * s, by - 200 * s), (x + 70 * s, by - 120 * s)], body_col, INK, 5 * s)
    f.line(x + 125 * s, by - 195 * s, x + 140 * s, by - 238 * s, INK, 8 * s)
    f.line(x + 105 * s, by - 238 * s, x + 175 * s, by - 244 * s, INK, 10 * s)          # handlebar
    f.circle(x + 150 * s, by - 160 * s, 15 * s, '#fff4c0', INK, 4 * s)                 # headlight
    f.rect(x + 150 * s, by - 290 * s, 26 * s, 44 * s, '#2b2b38', INK, 3 * s, r=5 * s)    # phone holder
    f.rect(x + 154 * s, by - 286 * s, 18 * s, 36 * s, '#7ad0ff', None, r=3 * s)
    # basket
    f.rect(x + 150 * s, by - 228 * s, 60 * s, 40 * s, None, INK, 4 * s, r=4 * s)
    for k in range(4): f.line(x + 155 * s + k * 15 * s, by - 228 * s, x + 155 * s + k * 15 * s, by - 188 * s, INK, 2.5 * s)
    # seat
    f.rect(x - 180 * s, by - 108 * s, 170 * s, 22 * s, '#2f2f3e', INK, 5 * s, r=11 * s)
    if moving:
        f.radial(x + 200 * s, by - 160 * s, 160 * s, '#fff4c0', 0.0, a=0.35)
    seat_y = by - 100 * s
    out = {}
    if back_rider:
        o = P.draw(f, 'she', x - 140 * s, seat_y, 0.9 * s, 'hug_back', back_expr, t=t)
        helmet(f, o['head'][0], o['head'][1] - 40 * s, 0.95 * s)
        out['she'] = o
    elif helmet_on_seat:
        hop = abs(math.sin(t * 7)) * 5 * s if moving else 0
        helmet(f, x - 140 * s, seat_y - 36 * s - hop, 0.85 * s)
    o = P.draw(f, rider, x - 40 * s, seat_y, 0.9 * s, 'ride', rider_expr, t=t)
    out['he'] = o
    return out


# ---------------------------------------------------------------- 郑州夜景
def corn_tower(f, x, base, s=1.0, t=0.0, lit=1.0):
    """郑州「大玉米」：玉米形塔楼，金色鳞片灯"""
    w, h = 70 * s, 420 * s
    p = skia.Path(); p.moveTo(x - w, base); p.lineTo(x - w * 0.95, base - h * 0.75)
    p.cubicTo(x - w * 0.9, base - h * 1.05, x + w * 0.9, base - h * 1.05, x + w * 0.95, base - h * 0.75); p.lineTo(x + w, base); p.close()
    f.path(p, '#2e2a48', None)
    for j in range(22):
        yy = base - 20 * s - j * 17 * s
        if yy < base - h * 0.95: break
        for i in range(-3, 4):
            xx = x + i * 18 * s + (j % 2) * 9 * s
            if abs(xx - x) > w * 0.9: continue
            on = (math.sin(t * 2 + i + j * 0.7) > -0.6) and lit
            f.oval(xx, yy, 6 * s, 5 * s, '#ffcf4a' if on else '#5a4a3a', None, a=0.95)
    f.line(x, base - h * 1.0, x, base - h * 1.12, '#ffcf4a', 4 * s)
    f.radial(x, base - h * 0.6, 260 * s, '#ffcf4a', 0.0, a=0.18 * lit)


def skyline(f, base, t=0.0, col='#262844', win='#ffcf7a', seed=3, density=0.35):
    r = np.random.default_rng(seed)
    x = -40
    while x < W + 40:
        w = int(r.integers(70, 150)); h = int(r.integers(140, 380))
        f.rect(x, base - h, w, h + 400, col)
        for wy in range(base - h + 18, base - 20, 26):
            for wx in range(x + 12, x + w - 12, 22):
                if r.random() < density:
                    on = math.sin(t * 1.3 + wx * 0.3 + wy) > -0.8
                    f.rect(wx, wy, 10, 12, win if on else col, a=0.9)
        x += w + int(r.integers(4, 20))


def road(f, y, t=0.0, speed=600, col='#3a3b52', lane='#f4f1ea'):
    f.rect(0, y, W, H - y, col)
    f.rect(0, y, W, 6, '#56587a')
    off = (t * speed) % 160
    for x in range(-160, W + 160, 160):
        f.rect(x - off, y + 90, 80, 8, lane, a=0.8)


def streetlamps(f, y, t=0.0, speed=600, col='#ffd98a'):
    off = (t * speed * 0.8) % 420
    for x in range(-420, W + 420, 420):
        xx = x - off
        f.line(xx, y, xx, y - 300, '#20202e', 8)
        f.line(xx, y - 300, xx + 60, y - 300, '#20202e', 8)
        f.radial(xx + 60, y - 290, 120, col, 0.0, a=0.5)
        f.circle(xx + 60, y - 292, 10, '#fff4c0')


# ---------------------------------------------------------------- 出租屋
def room(f, t=0.0, mood='cold', window=True, neon=True):
    pal = {'cold': ('#3d4270', '#323660', '#2a2c4c', '#5a5f94'),
           'warm': ('#f2c9a8', '#e4b08e', '#c98f72', '#fff0dc')}[mood]
    wall, wall_d, floor, light = pal
    f.rect(0, 0, W, H, wall)
    f.rect(0, 760, W, H - 760, floor)
    f.line(0, 760, W, 760, INK, 5)
    # window
    if window:
        wx, wy, ww, wh = 1180, 150, 520, 380
        f.rect(wx - 14, wy - 14, ww + 28, wh + 28, wall_d, INK, 5, r=6)
        sky_cols = ['#1a1c3a', '#2c2f5a'] if mood == 'cold' else ['#ffd9a8', '#ffb98a']
        f.vgrad(sky_cols, wy, wy + wh, wx, wx + ww)
        f.c.save(); f.c.clipRect(skia.Rect.MakeXYWH(wx, wy, ww, wh))
        f.c.translate(wx - 300, wy + wh - 760)
        skyline(f, 760, t, col='#20223e' if mood == 'cold' else '#d9906e', win='#ffcf7a' if mood == 'cold' else '#fff2c8', seed=9)
        corn_tower(f, 600, 760, 0.8, t, lit=1.0 if mood == 'cold' else 0.3)
        f.c.restore()
        f.line(wx + ww / 2, wy, wx + ww / 2, wy + wh, wall_d, 10)
        f.line(wx, wy + wh / 2, wx + ww, wy + wh / 2, wall_d, 10)
        f.rect(wx - 14, wy - 14, ww + 28, wh + 28, None, INK, 5, r=6)
        if neon and mood == 'cold':
            k = 0.5 + 0.5 * math.sin(t * 3)
            f.radial(wx + ww / 2, wy + wh, 500, '#7a6aff', 0.0, a=0.18 + 0.08 * k)


def table(f, x, y, w=560, s=1.0, col='#c98a5a'):
    f.rect(x - w / 2, y, w, 30 * s, col, INK, 5, r=8)
    f.rect(x - w / 2 + 30, y + 30 * s, 26, 180 * s, mixc(col, '#000000', 0.25), INK, 4)
    f.rect(x + w / 2 - 56, y + 30 * s, 26, 180 * s, mixc(col, '#000000', 0.25), INK, 4)


def stool(f, x, y, s=1.0, col='#e86a5a'):
    f.oval(x, y, 80 * s, 18 * s, col, INK, 5)
    f.rect(x - 60 * s, y + 10, 16 * s, 150 * s, mixc(col, '#000000', 0.3), INK, 4)
    f.rect(x + 44 * s, y + 10, 16 * s, 150 * s, mixc(col, '#000000', 0.3), INK, 4)


def heart_icon(f, x, y, s=1.0, col='#ff5f7e', a=1.0, line=INK):
    p = skia.Path(); p.moveTo(x, y + 14 * s)
    p.cubicTo(x - 30 * s, y - 8 * s, x - 14 * s, y - 26 * s, x, y - 10 * s)
    p.cubicTo(x + 14 * s, y - 26 * s, x + 30 * s, y - 8 * s, x, y + 14 * s); p.close()
    f.path(p, col, line, 4 * s, a)


def big_hand(f, x, y, ang=0.0, s=1.0, sleeve='#8f97ad', open_=True):
    """Q 版圆手 + 袖子，从 (x,y) 伸出，方向 ang（弧度，0=向右）"""
    L = 520 * s
    sx, sy = x - math.cos(ang) * L, y - math.sin(ang) * L
    p = skia.Path(); p.moveTo(sx, sy); p.lineTo(x - math.cos(ang) * 60 * s, y - math.sin(ang) * 60 * s)
    f.c.drawPath(p, f.stroke(INK, 120 * s + 10)); f.c.drawPath(p, f.stroke(sleeve, 120 * s))
    f.c.save(); f.c.translate(x, y); f.c.rotate(math.degrees(ang))
    f.oval(0, 0, 70 * s, 56 * s, P.SKIN, INK, 5 * s)
    if open_:
        for k in range(4):
            f.oval(64 * s, -36 * s + k * 24 * s, 30 * s, 13 * s, P.SKIN, INK, 5 * s)
        f.oval(0, 0, 66 * s, 52 * s, P.SKIN, None)
    else:
        for k in range(4):
            f.oval(52 * s, -30 * s + k * 20 * s, 18 * s, 12 * s, P.SKIN, INK, 4 * s)
    f.oval(-6 * s, -58 * s, 26 * s, 16 * s, P.SKIN, INK, 5 * s)
    f.c.restore()


def chair_back(f, x, y, s=1.0, col='#e86a5a'):
    """椅背（从桌子后面露出来）"""
    f.rect(x - 80 * s, y, 160 * s, 120 * s, col, INK, 5, r=18 * s)
    f.rect(x - 60 * s, y + 20 * s, 120 * s, 12 * s, mixc(col, '#000000', 0.2), None, r=6 * s)


def table_front(f, y, col='#c98a5a', x0=0, x1=W):
    """正面看的桌子：桌面 + 前沿，遮住人物下半身"""
    f.rect(x0 - 10, y, x1 - x0 + 20, 26, mixc(col, '#ffffff', 0.15), INK, 5, r=6)
    f.rect(x0 - 10, y + 26, x1 - x0 + 20, H - y, col, INK, 5)
    f.rect(x0 - 10, y + 26, x1 - x0 + 20, 14, mixc(col, '#000000', 0.18), None)


# ---------------------------------------------------------------- 河南高速路牌
def road_sign(f, x, y, city, km=None, icon=None, s=1.0, t=0.0):
    """绿色高速路牌（城市名 + 地标小图）。x,y = 牌子中心。"""
    w, h = 560 * s, 300 * s
    for px_ in (x - w * 0.32, x + w * 0.32):
        f.rect(px_ - 14 * s, y, 28 * s, 900 * s, '#9aa0aa', INK, 5 * s)
    f.rect(x - w / 2, y - h / 2, w, h, '#1e7a46', INK, 6 * s, r=18 * s)
    f.rect(x - w / 2 + 12 * s, y - h / 2 + 12 * s, w - 24 * s, h - 24 * s, None, '#ffffff', 6 * s, r=12 * s)
    fs = 128 if len(city.replace(' ', '')) <= 2 else 104
    f.text(x - 46 * s, y + 38 * s, city, fs * s, '#ffffff', 'black', 'center')
    if km is not None:
        f.text(x + w / 2 - 36 * s, y + h / 2 - 34 * s, f'{km} km', 40 * s, '#ffffff', 'bold', 'right')
    if icon:
        cx, cy = x + w / 2 - 80 * s, y - h / 2 + 80 * s
        f.circle(cx, cy, 62 * s, '#ffffff', INK, 5 * s)
        icon(f, cx, cy, s)


def icon_tea(f, x, y, s=1.0):       # 信阳毛尖
    f.rect(x - 26 * s, y - 20 * s, 52 * s, 50 * s, '#e8f4e8', INK, 4 * s, r=8 * s)
    f.rect(x - 22 * s, y - 6 * s, 44 * s, 32 * s, '#9ccc6a', None, r=6 * s)
    for k in range(3):
        f.oval(x - 12 * s + k * 12 * s, y + 4 * s, 4 * s, 9 * s, '#3f8f3a', None)
    f.curve([(x - 8 * s, y - 28 * s), (x - 2 * s, y - 40 * s), (x + 4 * s, y - 30 * s)], '#a0a0b0', 3 * s)


def icon_corn(f, x, y, s=1.0):      # 郑州大玉米
    corn_tower(f, x, y + 45 * s, 0.22 * s, 0.0)


def sunburst(f, x, y, t, cols=('#ffcf4a', '#ffb02e'), n=18, r=2600):
    a0 = t * 0.25
    for i in range(n):
        a = a0 + i * 2 * math.pi / n
        p = skia.Path(); p.moveTo(x, y)
        p.lineTo(x + math.cos(a) * r, y + math.sin(a) * r)
        p.lineTo(x + math.cos(a + math.pi / n) * r, y + math.sin(a + math.pi / n) * r); p.close()
        f.c.drawPath(p, f.fill(cols[i % 2]))
