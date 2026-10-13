"""《告白气球》v3.1 甜歌版：按乐句合并成 38 镜；画面明亮粉彩，黄昏 / 夜景才布光；
每个镜头有持续环境动态；画面上几乎不放字；"告白进度"只在亮格子时出现。"""
import math
import numpy as np
from gbl import *
from gbl import _DITH, _poly_mask
from light import Light, lightmap, glow
import g1, g2, g3, g4, g5

DITH = _DITH
YY, XX = np.mgrid[0:H, 0:W].astype(np.float32)


# ================================================================ 公共：环境动态 / 布光 / HUD
def clouds(cv, t, n=4, y0=14, col='fff8f0', speed=5):
    for i in range(n):
        x = (i * 97 + t * speed * (1 + i % 2 * 0.4)) % (W + 80) - 40
        y = y0 + (i * 13) % 30
        cv.ellipse(x, y, 20, 5, hexc(col)); cv.ellipse(x + 13, y - 3, 12, 5, hexc(col))


def drift_petals(cv, t, n=14, seed=3, cols=('ffb0c8', 'ffd8e4', 'ffffff')):
    r = rng(seed)
    for i in range(n):
        x0, y0, sp = r.uniform(0, W), r.uniform(0, H), r.uniform(0.6, 1.3)
        y = (y0 + t * 14 * sp) % (H + 10) - 5; x = (x0 + math.sin(t * 1.3 + i) * 8 + t * 6) % W
        cv.rect(x, y, 2, 2 if int(t * 3 + i) % 2 else 1, hexc(cols[i % len(cols)]))


def mini_balloons(cv, t, n=3, seed=7):
    r = rng(seed)
    for i in range(n):
        x = r.uniform(20, W - 20) + math.sin(t * 0.8 + i) * 6
        y = (r.uniform(0, 200) - t * 9) % 220 - 20
        balloon(cv, x, y, 0.7, t + i, string=True, str_len=6)


def sparkle_water(cv, t, y0, y1, n=16, seed=4):
    r = rng(seed)
    for i in range(n):
        x = r.uniform(0, W); y = r.uniform(y0, y1)
        if (t * 3 + i * 0.37) % 1.4 < 0.18: cv.px(x, y, WHITE); cv.px(x - 1, y, hexc('d8ecff')); cv.px(x + 1, y, hexc('d8ecff'))


def relight(cv, lights, ambient, floor=0.55, t=0.0):
    """整帧打光（人物也在内）：最暗不低于 floor，保证人物看得清。"""
    L = lightmap(lights, ambient, t)
    a = cv.a.astype(np.float32) / 255.0
    cv.a = (np.clip(a * np.clip(L, floor, 1.35), 0, 1) * 255).astype(np.uint8)


def hud_moment(cv, T):
    """只在每次 +1 前后 2.5 秒显示告白进度"""
    from gbl import PROG, hud
    for t0, k in PROG:
        if -0.3 <= T - t0 <= 2.5:
            k_in = clamp((T - t0 + 0.3) / 0.3) * (1 - clamp((T - t0 - 2.1) / 0.4))
            tmp = Canvas(); tmp.a = cv.a.copy(); hud(tmp, T)
            m = DITH < k_in
            cv.a[m] = tmp.a[m]
            return


# ================================================================ 前奏
def i01(t, D):   # 0–8.08 清晨巴黎，红气球升起，片名
    cv = g1.s01(t, D)
    sparkle_water(cv, t, 134, 148)
    for i in range(5):   # 飞鸟
        u = (t * 0.07 + i * 0.03) % 1
        x = lerp(-20, 340, u); y = 50 - u * 20 + (i % 2) * 4
        fl = int(t * 8 + i) % 2
        cv.px(x, y, hexc('5a4a6a')); cv.px(x - 1, y - fl, hexc('5a4a6a')); cv.px(x + 1, y - fl, hexc('5a4a6a'))
    return cv


def i02(t, D):   # 8.08–15.49 左岸街景，他提前到了
    cv = g1.s02(t, D)
    clouds(cv, t, n=3, y0=6)
    drift_petals(cv, t, n=10)
    return cv


def i03(t, D):   # 15.49–23.15 他用汤勺照头发 → 她来了，他噌地站起来
    cv = Canvas()
    g1.street_scene(cv, t)
    clouds(cv, t, n=3, y0=6)
    table(cv, 140, 124); cup(cv, 134, 117, 1, steam_t=t)
    arrive = 4.0
    stand = t > arrive + 0.9
    f = HE(cv, 112, GROUND, 30, 'stand' if stand else 'hold_r', 'surprise' if stand else ('happy' if t > 1.5 else 'normal'), t=t, facing=1)
    if not stand:
        hx, hy = f['hands'][1]
        cv.ellipse(hx + 2, hy - 8, 4, 5, hexc('d8dce4'), INK); cv.vline(int(hx + 2), int(hy - 3), int(hy + 2), hexc('b8bcc4'))
        if int(t * 3) % 2 and t > 1.5: symbol(cv, 'sparkle', f['cx'] + 12, f['top'] - 2, t)
    balloon(cv, 96, 80, 1.1, t, str_len=36)
    if t > arrive:
        x = int(lerp(330, 206, ease(clamp((t - arrive) / 1.8))))
        SHE(cv, x, GROUND, 30, 'walk' if t < arrive + 1.8 else 'wave', 'smile', t=t, facing=-1)
    if stand: symbol(cv, 'excl', f['cx'] + 10, f['top'] - 6, t)
    drift_petals(cv, t, n=8)
    return cv


# ================================================================ 主歌 1
def v04(t, D):   # 23.15–29.10 河畔咖啡座：他端杯只顾看她，咖啡洒了
    cv = Canvas()
    sky_band(cv, SKY_DAY, 0, 96)
    clouds(cv, t, n=3, y0=8)
    eiffel(cv, 268, 94, 80, hexc('9a8a9a'))
    paris_row(cv, 96, seed=21, hmin=24, hmax=40)
    seine(cv, 96, 116, t); sparkle_water(cv, t, 98, 114)
    boat(cv, int(-40 + t * 36), 106, t)
    ground_band(cv, 116, hexc('d8c8a8'))
    table(cv, 160, 136, 44, cloth=True)
    cup(cv, 170, 129, 1)
    heart = t > 2.4
    f = HE(cv, 126, 168, 34, 'hold_r', dict(eyes='happy' if heart else 'open', mouth='o', blush=heart, look=(1, 0)), t=t, facing=1)
    hx, hy = f['hands'][1]
    cup(cv, int(hx) + 2, int(hy) - 8, 1)
    if t > 1.6:
        for k in range(min(14, int((t - 1.6) * 10))): cv.rect(hx - 1, hy + k, 1, 1, hexc('8a5a3a'))
    SHE(cv, 204, 168, 34, 'sit', 'smile', t=t, facing=-1)
    if heart:
        for sg in (-1, 1): heart_px(cv, f['cx'] + sg * 6 + 1, f['top'] + int(34 * 0.6), 1, BAL)
    balloon(cv, 96, 104, 1.0, t, str_len=40)
    for i in range(2): pigeon(cv, 40 + i * 16 + int(math.sin(t * 2 + i) * 2), 166, t + i)
    return cv


def v05(t, D):   # 29.10–34.16 杯沿上的粉色唇印 → 他脸红冒烟
    cv = Canvas(hexc('f4e8d0'))
    cv.rect(0, 0, W, 26, NAVY)
    for i in range(16): cv.rect(i * 20, 26, 10, 6, hexc('f4f0e8'))
    cv.rect(0, 130, W, 50, hexc('f4f0e8')); cv.hline(0, W, 130, INK)
    cup(cv, 90, 98, 5, lip=True, steam_t=t)
    red = clamp((t - 1.6) / 0.5)
    f = face(cv, 'he', 226, 34, 58, dict(eyes='wide' if red < 0.5 else 'happy', mouth='o', blush=red > 0.5), t=t)
    if red > 0.5:
        for i in range(4):
            ph = (t * 1.5 + i * 0.25) % 1
            cv.ellipse(206 + i * 14, 30 - ph * 26, 3 + ph * 4, 3 + ph * 3, hexc('f4f0f4'))
    drift_petals(cv, t, n=6)
    return cv


def v06(t, D):   # 34.16–39.87 花卡名字写错（她挑眉）→ 一阵风，气球被吹过马路
    cv = Canvas()
    off = int(max(0, t - 2.4) * 20)
    g1.street_scene(cv, t, min(off, 60))
    gust = t > 2.4
    f = HE(cv, 100 - min(off, 60), GROUND, 30, 'reach' if gust else 'give', 'surprise' if gust else 'shy', t=t, facing=1)
    g = SHE(cv, 160 - min(off, 60), GROUND, 30, 'take', dict(eyes='open', mouth='flat', brow='up') if not gust else 'surprise', t=t, facing=-1)
    # 花束（她手里）
    hx, hy = g['hands'][0]
    for j in range(5): cv.ellipse(hx - 4 + (j % 3) * 4, hy - 6 - (j // 3) * 4, 3, 3, hexc('e8506a'), INK)
    # 小卡片：名字被划掉（只画线条，不写字）
    cv.rect(hx + 2, hy - 2, 12, 8, INK); cv.rect(hx + 3, hy - 1, 10, 6, WHITE)
    cv.hline(hx + 4, hx + 11, hy + 1, INK); cv.hline(hx + 4, hx + 11, hy + 2, BAL_D)
    if not gust and t > 0.8: symbol(cv, 'q', g['cx'] + 10, g['top'] - 4, t)
    if not gust and t > 1.2: symbol(cv, 'sweat', f['cx'] + 12, f['top'] - 2, t)
    if gust:
        for i in range(6):
            y = 40 + i * 16; x = ((t - 2.4) * 170 + i * 50) % (W + 60) - 30
            cv.hline(x, x + 24, y, WHITE)
        k = ease(clamp((t - 2.4) / (D - 2.4)))
        balloon(cv, 110 + k * 190, 90 - k * 60 - math.sin(t * 5) * 6, 1.3, t, str_len=24)
    else:
        balloon(cv, f['cx'] - 10, f['top'] - 30, 1.2, t, str_len=24)
    return cv


def v07(t, D):   # 39.87–43.84 气球上的笑脸飘上天，她笑了（告白进度 +1）
    cv = g1.s11(t, D)
    mini_balloons(cv, t, n=2, seed=11)
    return cv


# ================================================================ 导歌 1
def p08(t, D):   # 43.84–49.29 她轻快地往前走、回头摇手指"不行哦"，他笑着继续追
    cv = Canvas()
    off = int(t * 12)
    g2.boulevard(cv, t + off)
    leaves(cv, t, n=20, speed=14)
    turn = t > 2.6
    x = 196 + int(t * 6)
    g = SHE(cv, x, 158, 30, 'reach' if turn else 'walk', dict(eyes='closed', mouth='smile') if turn else 'smile', t=t, facing=-1 if turn else 1)
    if turn:
        hx, hy = g['hands'][1]
        sw = int(math.sin(t * 14) * 2)
        cv.rect(hx - 1 + sw, hy - 8, 2, 7, PAL['skin']); cv.rect(hx - 2 + sw, hy - 9, 4, 1, INK)
    HE(cv, 100 + int(t * 12), 158, 30, 'run', 'happy', t=t, facing=1)
    return cv


def p09(t, D):   # 49.29–54.32 路过闪闪的珠宝橱窗他摇头，接住一片落叶双手递给她
    cv = Canvas()
    g2.boulevard(cv, t, autumn=True)
    leaves(cv, t, n=60)
    # 左侧珠宝橱窗
    cv.rect(0, 70, 70, 70, INK); cv.rect(2, 72, 66, 66, hexc('3a3a5a'))
    for i in range(3):
        if (t * 3 + i) % 1.5 < 0.4: symbol(cv, 'sparkle', 14 + i * 20, 96, t)
        cv.ellipse(14 + i * 20, 104, 5, 4, GOLD, INK)
    catch = t > 1.6
    f = HE(cv, 130, 160, 34, 'give' if catch else 'stand', 'happy' if catch else dict(eyes='closed', mouth='flat'), t=t, facing=1)
    SHE(cv, 220, 160, 34, 'take' if t > 2.6 else 'stand', 'joy' if t > 2.6 else 'wonder', t=t, facing=-1)
    lx, ly = (f['hands'][1] if catch else (150, 40 + t * 50))
    cv.poly([(lx - 6, ly), (lx, ly - 7), (lx + 6, ly), (lx, ly + 6)], hexc('ffb84a')); cv.line(lx, ly - 6, lx, ly + 8, hexc('a06a2a'))
    if t > 3.0: symbol(cv, 'heart', 176, 96, t)
    return cv


def p10(t, D):   # 54.32–59.85 端蛋糕绊倒，奶油糊一脸，两个人笑成一团
    cv = g2.s17(t * 0.75 + 0.2, D)
    drift_petals(cv, t, n=8)
    return cv


def p11(t, D):   # 59.85–64.83 镜头拉远：两个人坐在一颗小星球上（告白进度 +1）
    return g2.s18(t, D)


# ================================================================ 副歌 1（黄昏，布光）
def tower_dusk(cv, t):
    sky_band(cv, SKY_DUSK, 0, 140)
    cv.ellipse(70, 112, 16, 16, hexc('ffe8a0'))
    clouds(cv, t, n=3, y0=30, col='ffc8b8', speed=3)
    eiffel(cv, 200, 140, 130, hexc('6a4a6a'))
    paris_row(cv, 140, seed=8, hmin=24, hmax=40, cols=[hexc('e8b8a8'), hexc('d8a8a0')])
    ground_band(cv, 140, hexc('c8a898'))


def c12(t, D):   # 64.83–71.11 黄昏的铁塔下，两人并肩，他偷偷看她
    cv = Canvas()
    tower_dusk(cv, t)
    look = t > 2.4
    HE(cv, 126, 168, 32, 'stand', 'shy' if look else 'normal', t=t, facing=1 if look else 0)
    SHE(cv, 160, 168, 32, 'stand', 'smile', t=t)
    balloon(cv, 108, 104, 1.1, t, str_len=30)
    relight(cv, [Light(70, 112, 'ffc890', 260, 0.7)], (0.85, 0.72, 0.78), floor=0.8, t=t)
    glow(cv, 70, 112, 40, 'ffb070', 0.45)
    if look: symbol(cv, 'heart', 140, 112, t)
    drift_petals(cv, t, n=10)
    return cv


def c13(t, D):   # 71.11–75.76 方糖一颗颗掉进咖啡，每颗溅起一个小爱心
    cv = g2.s21(t, D)
    for i in range(3):
        y = 60 - ((t * 10 + i * 9) % 30); cv.px(150 + i * 10 + math.sin(t * 3 + i) * 2, y, hexc('e8e0d8'))
    return cv


def c14(t, D):   # 75.76–81.86 她鼓着腮帮子扭过头，又偷偷瞄他手里的马卡龙
    cv = Canvas()
    tower_dusk(cv, t)
    peek = t > 2.8
    f = SHE(cv, 200, 168, 36, 'hand_chest', dict(eyes='closed', mouth='flat', blush=True) if not peek else dict(eyes='open', mouth='flat', blush=True, look=(-1, 0)), t=t, facing=1 if not peek else -1)
    cv.ellipse(f['cx'] - 7, f['top'] + 28, 4, 3, hexc('ffb0b8')); cv.ellipse(f['cx'] + 8, f['top'] + 28, 4, 3, hexc('ffb0b8'))
    g = HE(cv, 120, 168, 36, 'give', 'smile', t=t, facing=1)
    hx, hy = g['hands'][1]
    for i, c in enumerate([hexc('ffb0c8'), hexc('b8e8c8'), hexc('f8e0a0')]):
        cv.ellipse(hx + 4 + i * 2, hy - 4 - i * 5, 5, 2.5, c, INK)
    relight(cv, [Light(70, 112, 'ffc890', 260, 0.7)], (0.85, 0.72, 0.78), floor=0.8, t=t)
    return cv


def c15(t, D):   # 81.86–87.95 她噗嗤笑了，点头接过马卡龙，小爱心往上飘
    cv = Canvas()
    tower_dusk(cv, t)
    nod = int(abs(math.sin(t * 6)) * 2) if 0.4 < t < 1.8 else 0
    f = SHE(cv, 186, 168 + nod, 36, 'take', 'joy', t=t, facing=-1)
    HE(cv, 136, 168, 36, 'give', 'happy', t=t, facing=1)
    for i in range(4):
        u = ((t - 0.4) * 0.7 + i * 0.27) % 1.2
        if t > 0.4: heart_px(cv, f['cx'] - 14 + i * 9, f['top'] - 6 - u * 34, 1, BAL_H)
    balloon(cv, 112, 100, 1.1, t, str_len=36)
    relight(cv, [Light(70, 112, 'ffc890', 260, 0.7), Light(160, 130, 'ffd8a0', 80, 0.3)], (0.8, 0.66, 0.72), floor=0.8, t=t)
    glow(cv, 70, 112, 40, 'ffb070', 0.45)
    return cv


# ================================================================ 间奏（夜，布光）
def n16(t, D):   # 87.95–96.05 河边小舞台，他拿着话筒，台下荧光棒挥起来（告白进度 +1）
    cv = g3.s25(t, D)
    relight(cv, [Light(160, 70, 'fff0c0', 120, 0.9)], (0.7, 0.7, 0.85), floor=0.7, t=t)
    return cv


def n17(t, D):   # 96.05–100.09 夜里他在房间吹了一屋子红气球
    cv = Canvas(hexc('f0d8c0'))
    cv.rect(0, 140, W, 40, hexc('c8a888')); cv.hline(0, W, 140, INK)
    cv.rect(220, 30, 70, 50, INK); cv.rect(222, 32, 66, 46, hexc('2a3060'))
    for i in range(6): cv.px(230 + i * 10, 40 + (i * 7) % 30, hexc('fff4c0'))
    n = int(lerp(10, 40, ease(clamp(t / (D - 0.4)))))
    r = rng(27)
    for i in range(n):
        balloon(cv, r.uniform(16, 304), r.uniform(18, 124), 1.0, t + i, string=False, sway=True)
    f = HE(cv, 150, 160, 32, 'hold_r', dict(eyes='squeeze', mouth='o') if t > 2 else dict(eyes='closed', mouth='o'), t=t)
    gr = 0.6 + ((t * 1.3) % 1) * 1.4
    balloon(cv, f['cx'] + 22, f['top'] + 14, gr, t, string=False, sway=False)
    relight(cv, [Light(110, 50, 'ffd890', 160, 0.8)], (0.75, 0.68, 0.7), floor=0.75, t=t)
    glow(cv, 110, 50, 20, 'ffb050', 0.4)
    return cv


def n18(t, D):   # 100.09–104.13 她推开窗：窗外系着一只红气球，挂着画了爱心的纸条
    cv = Canvas()
    sky_band(cv, SKY_NIGHT, 0, H)
    r = rng(28)
    for i in range(50):
        x, y = r.uniform(0, W), r.uniform(0, 80)
        if (t * 3 + i) % 4 > 0.6: cv.px(x, y, hexc('fff4c0'))
    cv.rect(70, 30, 180, 150, hexc('e8d8c0')); cv.rect(70, 30, 180, 1, INK)
    wx, wy, ww, wh = 110, 60, 100, 90
    cv.rect(wx - 3, wy - 3, ww + 6, wh + 6, INK); cv.rect(wx, wy, ww, wh, hexc('ffe8b0'))
    op = ease(clamp((t - 0.6) / 0.6))
    cv.rect(wx, wy, int(ww / 2 * (1 - op * 0.7)), wh, hexc('8ab0d0')); cv.rect(wx + ww - int(ww / 2 * (1 - op * 0.7)), wy, int(ww / 2 * (1 - op * 0.7)), wh, hexc('8ab0d0'))
    if op > 0.3: SHE(cv, 160, wy + wh + 4, 34, 'hand_chest', 'wonder' if t < 2.2 else 'joy', t=t, hat=False)
    bx, by = 240, 70
    balloon(cv, bx, by, 1.6, t, str_len=50)
    cv.rect(bx - 10, by + 54, 22, 16, INK); cv.rect(bx - 9, by + 55, 20, 14, WHITE); heart_px(cv, bx + 1, by + 62, 1, BAL)
    cv.rect(66, wy + wh + 2, 188, 4, hexc('c8b8a0'))
    relight(cv, [Light(160, 100, 'ffe0a0', 110, 1.0), Light(bx, by, 'ff8aa0', 40, 0.4)], (0.45, 0.45, 0.62), floor=0.55, t=t)
    glow(cv, 160, 100, 50, 'ffb050', 0.3)
    return cv


def n19(t, D):   # 104.13–108.61 日出，他拽着一大串红气球走在河边，差点被拽飞
    cv = g3.s29(t, D)
    sparkle_water(cv, t, 120, 138)
    return cv


# ================================================================ 主歌 2（换画面）
def v20(t, D):   # 108.61–114.62 下雨的咖啡座：爱心拉花，她喝出一圈奶泡胡子
    cv = Canvas()
    g1.street_scene(cv, t, 0, rainy=True)
    table(cv, 150, 124, 44, cloth=True)
    cv.ellipse(150, 120, 10, 4, WHITE, INK); cv.ellipse(150, 119, 8, 3, hexc('b07a4a')); heart_px(cv, 150, 119, 1, hexc('f4ecd8'))
    sip = t > 2.6
    HE(cv, 112, GROUND, 30, 'sit', 'joy' if sip else 'smile', t=t, facing=1)
    g = SHE(cv, 190, GROUND, 30, 'sit', 'happy' if sip else 'smile', t=t, facing=-1)
    if sip:
        my = g['top'] + int(30 * 0.84); cv.ellipse(g['cx'], my - 1, 6, 2, WHITE, INK)
    rain(cv, t, n=150, seed=30, speed=150, col=hexc('e0e8f4'), excl=lambda x, y: x < 160 and y > 76, y_ground=176)
    return cv


def v21(t, D):   # 114.62–119.39 她亲了他的脸颊 → 他石化，脸上一个唇印
    if t < 1.8: return g3.s32(t, 2.0)
    cv = g3.s33((t - 1.8) * 1.2, D)
    return cv


def v22(t, D):   # 119.39–125.22 一整串红气球被风吹过街，落到她的阳台
    cv = g3.s35(t, D)
    return cv


def v23(t, D):   # 125.22–129.17 屋顶上空飘满笑脸气球，她在阳台上抓住一只
    return g3.s36(t, D)


# ================================================================ 导歌 2（换画面）
def p24(t, D):   # 129.17–134.39 她站在高高的台阶顶上，他一级一级爬上去
    cv = Canvas()
    sky_band(cv, SKY_DAY, 0, H)
    clouds(cv, t, n=4, y0=10)
    pan = int(ease(clamp(t / D)) * 60)
    for i in range(9):
        x = 40 + i * 26; y = 170 - i * 16 + pan
        cv.rect(x, y, 30, 200, hexc('f0e2c8')); cv.rect(x, y, 30, 2, INK); cv.vline(x, y, H, INK)
        for k in range(3): cv.px(x + 6 + k * 8, y + 6, hexc('e0d0b4'))
    top_y = 170 - 8 * 16 + pan
    SHE(cv, 40 + 8 * 26 + 16, top_y, 24, 'clap' if t > 3.6 else 'stand', 'joy' if t > 3.6 else 'smile', t=t, facing=-1)
    lvl = min(7, int(t / 0.62))
    hop = abs(math.sin(t / 0.62 * math.pi)) * 3
    HE(cv, 40 + lvl * 26 + 15, 170 - lvl * 16 + pan - hop, 24, 'stand', 'happy', t=t, facing=1)
    drift_petals(cv, t, n=8)
    return cv


def p25(t, D):   # 134.39–139.70 满天落叶，他跳起来接住最漂亮的一片 → 她夹进日记本
    if t < 2.6:
        cv = g4.s39(t, 2.6)
        return cv
    return g4.s40(t - 2.6 + 0.6, D)


def p26(t, D):   # 139.70–145.21 河边野餐 → 突然下雨，他脱外套挡在她头上，两人在雨里笑
    if t < 2.6: return g4.s41(t, D)
    return g4.s42(t - 2.6, D)


def p27(t, D):   # 145.21–150.22 水晶球里的铁塔和他们俩（告白进度 +1）
    return g4.s43(t, D)


# ================================================================ 副歌 2
def c28(t, D):   # 150.22–156.52 拍立得照片墙，一拍一张
    return g4.s44(t, D)


def c29(t, D):   # 156.52–161.11 两个人从两边一起咬一团粉色棉花糖
    cv = Canvas()
    g2.boulevard(cv, t)
    k = ease(clamp(t / 1.6))
    HE(cv, int(lerp(90, 142, k)), 166, 34, 'stand', 'happy', t=t, facing=1)
    SHE(cv, int(lerp(230, 178, k)), 166, 34, 'stand', 'joy', t=t, facing=-1)
    cy = 120
    cv.vline(160, cy + 6, cy + 30, hexc('d8c8a0'))
    for i in range(14):
        a = i * 0.45
        cv.ellipse(160 + math.cos(a) * 9, cy + math.sin(a) * 7, 7, 6, hexc('ffb8d0'))
    cv.ellipse(160, cy, 11, 9, hexc('ffc8dc'))
    if k >= 1: symbol(cv, 'heart', 160, 94, t)
    drift_petals(cv, t, n=8)
    return cv


def c30(t, D):   # 161.11–167.09 她又任性鼓腮，他做鬼脸 → 她眼睛里的高光变成爱心
    if t < 3.2:
        cv = g4.s46(t, 3.2)
        drift_petals(cv, t, n=6)
        return cv
    return g4.s47(t - 3.2, D)


def c31(t, D):   # 167.09–171.66 黄金时刻，她挽着他的胳膊往前走
    cv = Canvas()
    off = int(t * 12)
    g2.boulevard(cv, t + off, sky=SKY_DUSK)
    x = 130 + int(t * 6)
    HE(cv, x, 162, 32, 'walk', 'shy', t=t, facing=1)
    SHE(cv, x + 34, 162, 32, 'walk', 'joy', t=t + 0.05, facing=1)
    cv.rect(x + 14, 134, 8, 3, PAL['skin'])
    balloon(cv, x + 54, 96, 1.2, t, str_len=40)
    symbol(cv, 'heart', x + 17, 100, t)
    relight(cv, [Light(300, 90, 'ffc890', 260, 0.7)], (0.85, 0.72, 0.76), floor=0.8, t=t)
    drift_petals(cv, t, n=10)
    return cv


# ================================================================ 终副歌
def f32(t, D):   # 171.66–177.86 恋爱日记一页页翻，每页都是我们的涂鸦
    cv = Canvas(hexc('c8a888'))
    cv.rect(40, 16, 240, 150, INK); cv.rect(41, 17, 238, 148, hexc('fffaf0')); cv.vline(160, 16, 166, INK)
    beat = 0.673
    n = int(t / beat); k = (t / beat) % 1
    D_ = ['cafe', 'balloon', 'leaf', 'rain', 'cake', 'tower', 'globe', 'planet']
    for y in range(34, 160, 12): cv.hline(48, 152, y, hexc('d8e0f0')); cv.hline(168, 272, y, hexc('d8e0f0'))
    for kind, x in ((D_[(2 * n) % 8], 78), (D_[(2 * n + 1) % 8], 196)): g4.polaroid(cv, x, 56, kind, t)
    for x in (70, 190): heart_px(cv, x, 32, 1, BAL)
    if k < 0.3:
        u = k / 0.3; w = int(118 * (1 - u))
        cv.poly([(160, 17), (160 + w, 17 + int(u * 6)), (160 + w, 165 - int(u * 6)), (160, 165)], hexc('f4f0e4')); cv.line(160 + w, 17, 160 + w, 165, INK)
    return cv


def f33(t, D):   # 177.86–182.45 香水一喷，雾里浮出一个个回忆泡泡
    return g5.s50(t, D)


def f34(t, D):   # 182.45–188.52 一整瓶星星，瓶子里是小小的她
    cv = g5.s51(t, D)
    glow(cv, 160, 110, 50, 'ffd060', 0.25)
    return cv


def f35(t, D):   # 188.52–193.18 两杯咖啡倒进一杯，一搅，转成一个爱心
    return g5.s52(t, D)


def tower_night_lit(cv, t):
    g5.tower_night(cv, t)


def f36(t, D):   # 193.18–201.51 夜里铁塔下，他单膝跪地举起红气球；她捂住脸，眼里闪着泪光
    if t < 5.2:
        cv = Canvas()
        tower_night_lit(cv, t)
        kneel = t > 0.8
        f = HE(cv, 130, 172, 36, 'sit' if kneel else 'stand', 'smile', t=t, facing=1)
        balloon(cv, f['cx'] + 22, f['top'] - 20, 2.2, t, str_len=24)
        g = SHE(cv, 210, 172, 36, 'hand_chest' if kneel else 'stand', dict(eyes='wide', mouth='o', blush=True) if kneel else 'normal', t=t, facing=-1)
        relight(cv, [Light(170, 120, 'ffe0b0', 110, 0.9), Light(160, 60, 'fff0c0', 120, 0.5)], (0.55, 0.55, 0.72), floor=0.7, t=t)
        glow(cv, f['cx'] + 22, f['top'] - 20, 24, 'ff5a7a', 0.35)
        if kneel and t > 1.6: symbol(cv, 'excl', g['cx'] + 12, g['top'] - 6, t)
        return cv
    return g5.s54(t - 5.2 + 1.0, D)


def f37(t, D):   # 201.51–207.52 她点头接过气球——告白成功，铁塔上空烟花
    cv = Canvas()
    tower_night_lit(cv, t)
    fireworks(cv, t, seed=3, n=7)
    nod = int(abs(math.sin(t * 6)) * 2) if t < 1.2 else 0
    HE(cv, 140, 172, 32, 'cheer' if t > 1.4 else 'stand', 'joy', t=t, facing=1)
    f = SHE(cv, 178, 172 + nod, 32, 'cheer' if t > 1.4 else 'take', 'joy', t=t, facing=-1)
    balloon(cv, 196, f['top'] - 24, 1.8, t, face_=True, str_len=24)
    relight(cv, [Light(160, 50, 'fff0d0', 200, 0.8)], (0.6, 0.6, 0.78), floor=0.75, t=t)
    if t > 0.4:
        u = clamp((t - 0.4) / 0.5) * (1 - clamp((t - (D - 0.8)) / 0.8))
        m = Canvas(KEY); title_text(m, '告白成功！', 160, 40, GOLD, size=20, outline=BAL_D)
        mm = np.any(m.a != np.array(KEY, np.uint8), axis=2) & (DITH < u)
        cv.a[mm] = m.a[mm]
    confetti(cv, t, seed=5, n=40)
    return cv


def e38(t, D):   # 207.52–215.60 谢幕：两人鞠躬，红幕布合上，THANKS FOR WATCHING
    return g5.s56(t, D)


SHOTS = [
    (0.00, 8.08, i01), (8.08, 15.49, i02), (15.49, 23.15, i03),
    (23.15, 29.10, v04), (29.10, 34.16, v05), (34.16, 39.87, v06), (39.87, 43.84, v07),
    (43.84, 49.29, p08), (49.29, 54.32, p09), (54.32, 59.85, p10), (59.85, 64.83, p11),
    (64.83, 71.11, c12), (71.11, 75.76, c13), (75.76, 81.86, c14), (81.86, 87.95, c15),
    (87.95, 96.05, n16), (96.05, 100.09, n17), (100.09, 104.13, n18), (104.13, 108.61, n19),
    (108.61, 114.62, v20), (114.62, 119.39, v21), (119.39, 125.22, v22), (125.22, 129.17, v23),
    (129.17, 134.39, p24), (134.39, 139.70, p25), (139.70, 145.21, p26), (145.21, 150.22, p27),
    (150.22, 156.52, c28), (156.52, 161.11, c29), (161.11, 167.09, c30), (167.09, 171.66, c31),
    (171.66, 177.86, f32), (177.86, 182.45, f33), (182.45, 188.52, f34), (188.52, 193.18, f35),
    (193.18, 201.51, f36), (201.51, 207.52, f37), (207.52, 215.60, e38),
]
NO_HUD = {'i01', 'e38'}


def frame(T):
    for a, b, fn in SHOTS:
        if a <= T < b:
            cv = fn(T - a, b - a)
            if fn.__name__ not in NO_HUD: hud_moment(cv, T)
            return cv
    return Canvas()


def timeline():
    return [(a, b, (lambda fn, a, D: (lambda t: (lambda cv: (hud_moment(cv, a + t) if fn.__name__ not in NO_HUD else None, cv)[1])(fn(t, D))))(fn, a, b - a)) for a, b, fn in SHOTS]
