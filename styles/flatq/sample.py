"""《5:20AM》情感样片：#36 一个人吃面 → #37 手按胸口 → #38 抓了个空 → #39 空后座夜骑（1:29.90–1:37.71）"""
import math
import skia
from fq import *
import people as P
from props import *

BEAT = 60 / 123.047


def night_ride_bg(f, t, speed=520):
    f.vgrad(['#141634', '#2a2c5c', '#5a3f7a'], 0, 700)
    for k in range(40):   # a few stars
        x = (k * 397) % W; y = (k * 131) % 380 + 70
        f.circle(x, y, 2.2, '#ffffff', a=0.4 + 0.4 * math.sin(t * 2 + k))
    f.c.save(); f.c.translate(-(t * 40) % 400, 0)
    skyline(f, 700, t, seed=4); f.c.restore()
    corn_tower(f, 1500 - t * 25, 700, 1.1, t)
    road(f, 700, t, speed); streetlamps(f, 700, t, speed)


def chair_empty(f, x, y, s=1.0, col='#d65a4e'):
    """塑料椅背：一整块圆角椅背 + 把手孔"""
    p = skia.Path()
    p.addRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x - 95 * s, y, 190 * s, 210 * s), 40 * s, 40 * s))
    f.path(p, col, INK, 5)
    f.rect(x - 95 * s + 14 * s, y + 14 * s, 190 * s - 28 * s, 60 * s, mixc(col, '#ffffff', 0.18), None, r=26 * s, a=0.6)
    f.rect(x - 40 * s, y + 30 * s, 80 * s, 26 * s, '#3d4270', INK, 4, r=13 * s)          # handle hole
    for k in range(3):
        f.rect(x - 60 * s + k * 45 * s, y + 100 * s, 30 * s, 60 * s, mixc(col, '#000000', 0.18), None, r=10 * s)


def s36(t, dur):
    """一碗面，对面空着（缓推，留白）"""
    f = Frame()
    z = 1.0 + 0.05 * ease(t / dur)
    f.push(960, 600, z)
    room(f, t, 'cold')
    chair_empty(f, 1260, 560, 1.4)
    chew = (math.sin(t * 6) > 0.6)
    o = P.draw(f, 'he', 600, 900, 1.55, 'eat', 'lonely', t=t)
    table_front(f, 800, '#6e5466')
    huimian(f, 930, 800, 1.6, t)
    lift = (math.sin(t * 2.4) + 1) / 2
    hx, hy = o['hand_r']
    tipx, tipy = lerp(860, 720, lift), lerp(740, 640, lift)
    f.line(hx + 10, hy - 10, tipx, tipy, '#d9a46a', 8); f.line(hx + 22, hy - 4, tipx + 12, tipy + 6, '#d9a46a', 8)
    f.curve([(tipx + 4, tipy + 4), (tipx + 10, tipy + 40), (lerp(900, 760, lift), lerp(780, 720, lift))], '#fff2cc', 10)
    f.rect(1500, 700, 70, 100, '#ffffff', INK, 5, r=10, a=0.85); f.rect(1505, 740, 60, 55, '#9aa0c8', None, r=8)
    f.pop()
    status_bar(f, '5:20', 20)
    return f


def s37(t, dur):
    """手按在自己胸口，心跳微弱"""
    f = Frame()
    f.vgrad(['#2a2d55', '#3d4270'], 0, H)
    f.radial(960, 520, 700, '#5a5f94', 0.0, a=0.5)
    z = 1.0 + 0.04 * ease(t / dur)
    f.push(960, 700, z)
    o = P.draw(f, 'he', 960, 1150, 2.5, 'chest', {'eyes': 'closed_sad', 'mouth': 'flat', 'brow': 'sad'}, t=t)
    # weak heartbeat: a small faint heart between his hands, pulses once per 2 beats
    ph = (t / (BEAT * 2)) % 1.0
    k = 1.0 + 0.15 * math.exp(-ph * 8)
    hx = (o['hand_l'][0] + o['hand_r'][0]) / 2; hy = (o['hand_l'][1] + o['hand_r'][1]) / 2
    f.radial(hx, hy - 10, 120, '#ff5f7e', 0.0, a=0.25 * math.exp(-ph * 6))
    heart_icon(f, hx, hy - 70, 1.5 * k, '#ff5f7e', a=0.45 + 0.35 * math.exp(-ph * 8))
    f.pop()
    # ECG line across bottom, mostly flat
    pts = []
    for i in range(0, W + 1, 12):
        x = i; base = 1010
        d = ((i / W) - ph) % 1.0
        y = base - (34 * math.exp(-((d - 0.02) * 60) ** 2) if d < 0.06 else 0)
        pts.append((x, y))
    f.curve(pts, '#ff8fa0', 4, a=0.6)
    status_bar(f, '5:24', 20)
    return f


def s38(t, dur):
    """伸手抓了个空，手心只有一点粉色光点散开"""
    f = Frame()
    room(f, t, 'cold', window=False)
    f.rect(0, 0, W, H, '#1e2040', a=0.45)
    reach = ease(t / (dur * 0.55))
    hx = lerp(560, 1020, reach); hy = 600
    closed = t > dur * 0.6
    # faint pink glow where her hand "was"
    if not closed:
        f.radial(1260, 560, 200, PINK, 0.0, a=0.5 * (1 - reach * 0.5))
        for i in range(8): f.circle(1260 + math.cos(i) * 60, 560 + math.sin(i * 1.7) * 50, 6, PINK, a=0.6)
    big_hand(f, hx, hy, -0.12, 2.3, '#8f97ad', open_=not closed)
    if closed:
        k = (t - dur * 0.6) / (dur * 0.4)
        for i in range(14):
            a = i / 14 * 6.283 + 0.3
            r = 40 + k * 260
            f.circle(1240 + math.cos(a) * r, 560 + math.sin(a) * r * 0.7, 9 * (1 - k) + 1, PINK, a=max(0, 0.9 - k))
    status_bar(f, '5:27', 20)
    return f


def s39(t, dur):
    """一个人骑车，后座的粉色头盔空着（横移，留白）"""
    f = Frame()
    night_ride_bg(f, t + 3.0)
    ebike(f, 860 + 30 * math.sin(t * 0.8), 1000, 1.15, t, moving=True, helmet_on_seat=True, rider_expr='lonely')
    status_bar(f, '5:31', 20)
    return f


TIMELINE = [(89.90, 91.85, s36), (91.85, 93.81, s37), (93.81, 95.27, s38), (95.27, 97.71, s39)]

if __name__ == '__main__':
    from render import render
    # 情感样片：4 个镜头约 8 秒。加 song='你的音频.mp3' 就会配上原曲同一段。
    render(TIMELINE, 89.90, 97.71, 'out_sample.mp4', song=None, fade_in=0.3, fade_out=0.4)
    print('done')
