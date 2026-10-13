"""最小示例：两个镜头 + 渲染。复制这个文件开始一首新歌。
运行：python3 example.py   → out_example.mp4（无音频）
"""
from px import *
from chars import char, head, symbol
from scenes import *
from ui import dialog, popup, icon_notice, rain_cloud, confetti
from render import render


def shot_a(t):                       # 全景：交代环境
    cv = Canvas()
    sky(cv, [hexc('6a3a6e'), hexc('a64a6a'), hexc('e0715a'), hexc('f5a65a'), hexc('ffd27a')], 0, 112)
    sun(cv, 232, 98, 16, hexc('fff0b0'))
    roofs(cv, 108, hexc('5a3a5a'), seed=5)
    rice(cv, 114, t)
    char(cv, 'boy', 140, 142, 14, 'hold_r', 'smile', t=t)
    char(cv, 'girl', 162, 142, 14, 'hold_l', 'shy', t=t, blush=True)
    if t > 1.0: symbol(cv, 'heart', 162, 116, t)
    return cv


def shot_b(t):                       # 特写：演情绪 + 游戏 UI
    cv = Canvas()
    sky(cv, STATION_EVE, 0, H)
    head(cv, 'boy', 92, 40, 76, 'hesitate' if t < 1.2 else 'sad', t=t, facing=1)
    dialog(cv, 170, 30, 120, 26, '我……'[:max(0, 3 - int(max(0, t - 1.2) / 0.4))], t=t, tail=(178, 0))
    return cv


if __name__ == '__main__':
    render([(0, 2, shot_a), (2, 4, shot_b)], 0, 4, 'out_example.mp4', audio=False)
    print('ok -> out_example.mp4')
