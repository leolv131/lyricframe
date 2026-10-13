"""第 1 章 · Chapter 1 — three shots showing the patterns you will use most (flatq).

Every shot is `def name(t, D):  # start–end what happens` and returns a Frame.
t = seconds since the shot started, D = shot length. Only t decides the picture.
The comment on the `def` line becomes the storyboard (make.py --shots-json).
"""
from world import *


def s01(t, D):   # 0.00–5.00 白天的小街，她走过来，看到地上一只红色纸飞机（中景）
    f = Frame()
    street(f, t, 'day')
    x = 520 + t * 90
    P.draw(f, 'she', x, P.feet_for_head(560, 0.9), 0.9, 'walk', 'smile', t=t)
    f.poly([(1180, 880), (1260, 860), (1190, 900)], PAL['token'], INK, 4)      # the token on the ground
    return f


def s02(t, D):   # 5.00–9.00 近景：她捡起纸飞机，眼睛一亮，头顶冒出"!"
    f = Frame()
    street(f, t + 5, 'dusk')
    P.draw(f, 'she', 900, P.feet_for_head(430, 1.9), 1.9, 'chest', 'surprise' if t > 1.2 else 'normal', t=t, hide_legs=True)
    if t > 1.2:
        P.symbol(f, 'excl', 1120, 230, 1.0, t)
    return f


def s03(t, D):   # 9.00–15.00 同一条街入夜：她把纸飞机扔出去，它拖着光飞过屋顶（长镜头）
    f = Frame()
    street(f, t, 'night')
    P.draw(f, 'she', 640, P.feet_for_head(560, 0.9), 0.9, 'wave' if t < 1.5 else 'stand', 'happy', t=t)
    k = clamp((t - 1.0) / 4.0)
    px, py = lerp(720, 1750, k), 520 - 260 * math.sin(k * math.pi)
    for i in range(12):                                                         # light trail
        kk = clamp(k - i * 0.015)
        f.circle(lerp(720, 1750, kk), 520 - 260 * math.sin(kk * math.pi), 8 - i * 0.5, '#ffd0dc', a=0.5 - i * 0.04)
    f.poly([(px - 40, py + 10), (px + 40, py), (px - 30, py + 26)], PAL['token'], INK, 4)
    return f


SHOTS = [(0.0, 5.0, s01), (5.0, 9.0, s02), (9.0, 15.0, s03)]
