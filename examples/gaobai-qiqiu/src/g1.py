"""第 1 章：前奏（01–04）+ 主歌 1（05–11）。白天，粉彩巴黎。"""
from gbl import *
from gbl import _DITH, _poly_mask
from tl import shot


def skyline(cv, t, sky=SKY_DAY, night=0.0, tower_x=230, river=(132, 150)):
    sky_band(cv, sky, 0, river[0])
    eiffel(cv, tower_x, river[0] - 4, 110, mix(hexc('8a7a8a'), hexc('2a2a44'), night), lights=night, t=t)
    paris_row(cv, river[0] - 2, seed=11, lit=0.4 * night, night=night, hmin=26, hmax=46)
    seine(cv, river[0], river[1], t, night=night)


@shot(1)
def s01(t, D):
    cv = Canvas()
    skyline(cv, t, SKY_DAWN, 0.0)
    cv.rect(0, 150, W, 30, hexc('c8b89a')); cv.hline(0, W, 150, INK)
    # 云
    for i in range(4):
        x = (i * 90 + t * 4) % (W + 60) - 30
        cv.ellipse(x, 24 + i * 7, 18, 5, hexc('fff4ec')); cv.ellipse(x + 12, 21 + i * 7, 12, 5, hexc('fff4ec'))
    by = 190 - t * 22
    balloon(cv, 120 + math.sin(t) * 6, by, 1.6, t, str_len=20)
    k = clamp((t - 2.6) / 0.8) * (1 - clamp((t - (D - 0.6)) / 0.6))
    if k > 0:
        m = Canvas(KEY)
        title_text(m, '告 白 气 球', 160, 46, hexc('fff6e0'), size=24)
        mm = np.any(m.a != np.array(KEY, np.uint8), axis=2) & (_DITH < k)
        cv.a[mm] = m.a[mm]
        m2 = Canvas(KEY); m2.text(160, 64, '原唱 · 周杰伦', hexc('fff6e0'), outline=INK, anchor='mt')
        mm2 = np.any(m2.a != np.array(KEY, np.uint8), axis=2) & (_DITH < k)
        cv.a[mm2] = m2.a[mm2]
    return cv


def street_scene(cv, t, off=0, night=0.0, rainy=False):
    sky_band(cv, SKY_RAIN if rainy else SKY_DAY, 0, 60)
    paris_row(cv, GROUND, seed=4, hmin=110, hmax=140, night=night)
    cafe(cv, 10 - off, GROUND, 150, t, night)
    flower_shop_front(cv, 190 - off, GROUND - 6, 110, night)
    ground_band(cv, GROUND, hexc('c8b89a'))
    for x in range(0, W, 12): cv.rect(x - off % 12, GROUND + 14, 8, 2, hexc('e8dcc0'))


@shot(2)
def s02(t, D):
    cv = Canvas()
    off = int(t * 4)
    street_scene(cv, t, off)
    table(cv, 70 - off, 124); cup(cv, 64 - off, 117, 1, steam_t=t)
    HE(cv, 96 - off, GROUND, 24, 'sit', 'smile', t=t, facing=-1)
    # 气球拴在椅子上
    balloon(cv, 112 - off, 92, 1.0, t, str_len=24)
    for i in range(4):
        fly = clamp((t - 2.2 - i * 0.1) / 1.0)
        x = 150 + i * 14 - off + fly * 60; y = 158 - fly * 90 - i * 3
        pigeon(cv, x, y, t + i * 0.2, fly=fly)
    for i in range(2):
        x = W - ((t * 30 + i * 140) % (W + 40))
        npc(cv, 'npc_g' if i else 'npc', x, 172, 20, t, phone=False, facing=-1)
    return cv


@shot(3)
def s03(t, D):
    cv = Canvas()
    cv.rect(0, 0, W, H, hexc('f4e8d0'))
    cv.rect(0, 0, W, 40, NAVY)
    for i in range(16): cv.rect(i * 20, 40, 10, 8, hexc('f4f0e8'))
    cv.rect(0, 120, W, 60, hexc('f4f0e8')); cv.hline(0, W, 120, INK)
    f = face(cv, 'he', 120, 46, 52, dict(eyes='open', mouth='flat', look=(0, 1)) if t < 1.4 else dict(eyes='happy', mouth='smile'), t=t)
    # 手表（看表）
    if t < 1.4:
        mitt(cv, 84, 112, 1, hexc('aad2f0'), (40, 190))
        cv.rect(78, 104, 12, 8, INK); cv.rect(79, 105, 10, 6, WHITE); cv.line(84, 108, 84, 106, INK); cv.line(84, 108, 86, 108, INK)
    else:
        # 汤勺当镜子
        cv.ellipse(210, 70, 14, 18, hexc('d8dce4'), INK); cv.rect(208, 86, 4, 40, hexc('b8bcc4'))
        mini = Canvas(KEY); head(mini, 'he', 210, 62, 16, 'smile', t=t)
        m = np.any(mini.a != np.array(KEY, np.uint8), axis=2)
        yy, xx = np.mgrid[0:H, 0:W]; m &= ((xx - 210) ** 2 / 169 + (yy - 70) ** 2 / 289) < 1
        cv.a[m] = mini.a[m]
        mitt(cv, 212, 128, -1, hexc('aad2f0'), (W + 20, 190))
        if int(t * 3) % 2: symbol(cv, 'sparkle', 160, 46, t)
    # 气球线
    cv.vline(260, 0, 120, hexc('5a5a6a'))
    return cv


@shot(4)
def s04(t, D):
    cv = Canvas()
    street_scene(cv, t, 0)
    table(cv, 140, 124); cup(cv, 134, 117, 1)
    stand = t > 0.9
    f = HE(cv, 112, GROUND, 28, 'stand' if stand else 'sit', 'surprise' if stand else 'normal', t=t, facing=1)
    balloon(cv, 98, 80, 1.1, t, str_len=36)
    x = int(lerp(330, 210, ease(clamp(t / 1.6))))
    SHE(cv, x, GROUND, 28, 'walk' if t < 1.6 else 'wave', 'smile', t=t, facing=-1)
    if stand: symbol(cv, 'excl', f['cx'] + 10, f['top'] - 6, t)
    return cv


# ---------------------------------------------------------------- 主歌 1
@shot(5)
def s05(t, D):
    cv = Canvas()
    sky_band(cv, SKY_DAY, 0, 96)
    eiffel(cv, 262, 94, 80, hexc('9a8a9a'))
    paris_row(cv, 96, seed=21, hmin=24, hmax=40)
    seine(cv, 96, 122, t)
    boat(cv, int(-40 + t * 40), 108, t)
    ground_band(cv, 122, hexc('d8c8a8'))
    cafe(cv, -40, 172, 120, t)
    table(cv, 140, 140, 40, cloth=True)
    cup(cv, 132, 133, 1); cup(cv, 150, 133, 1)
    HE(cv, 110, 168, 24, 'sit', 'smile', t=t, facing=1)
    SHE(cv, 172, 168, 24, 'sit', 'smile', t=t, facing=-1)
    balloon(cv, 96, 108, 1.0, t, str_len=28)
    return cv


@shot(6)
def s06(t, D):
    cv = Canvas(hexc('f4e8d0'))
    cv.rect(0, 0, W, 30, NAVY)
    cv.rect(0, 130, W, 50, hexc('f4f0e8')); cv.hline(0, W, 130, INK)
    heart = t > 0.9
    f = face(cv, 'he', 110, 40, 52, dict(eyes='happy' if heart else 'open', mouth='o', look=(1, 0), blush=heart), t=t)
    if heart:
        for sg in (-1, 1):
            heart_px(cv, 110 + sg * 11 + 1, 40 + int(52 * 0.6) + 1, 2, BAL)
    # 杯子举在嘴边，咖啡洒出
    tilt = ease(clamp(t / 0.8))
    cx, cy = 140, 92
    cup(cv, cx, cy, 3)
    if t > 0.6:
        for k in range(int((t - 0.6) * 40)):
            cv.rect(cx - 10 - k % 3, cy + 18 + k, 2, 2, hexc('8a5a3a'))
    mitt(cv, cx + 18, cy + 30, -1, hexc('aad2f0'), (W + 10, 200))
    # 右边她（虚焦色块）
    SHE(cv, 260, 170, 40, 'sit', 'smile', t=t, facing=-1)
    return cv


@shot(7)
def s07(t, D):
    cv = Canvas(hexc('f4f0e8'))
    for x in range(0, W, 20): cv.vline(x, 0, H, hexc('ece6da'))
    k = ease(clamp(t / 0.5))
    y = int(lerp(10, 70, k))
    cup(cv, 160, y, 8, lip=True)
    cv.ellipse(160, y + 58, 60, 6, hexc('e0d8c8'))
    return cv


@shot(8)
def s08(t, D):
    cv = Canvas(hexc('f4e8d0'))
    cv.rect(0, 0, W, 30, NAVY)
    red = clamp(t / 0.5)
    f = face(cv, 'he', 160, 34, 64, dict(eyes='wide', mouth='o', blush=red > 0.5), t=t)
    if red > 0.5:
        for i in range(3):
            ph = (t * 1.5 + i * 0.33) % 1
            cv.ellipse(140 + i * 20, 30 - ph * 26, 4 + ph * 4, 3 + ph * 3, hexc('f4f0f4'))
    return cv


@shot(9)
def s09(t, D):
    cv = Canvas(hexc('f4e8d0'))
    # 玫瑰花束
    for j in range(9):
        x = 90 + (j % 3) * 18; y = 40 + (j // 3) * 16
        cv.ellipse(x, y, 9, 8, hexc('e8506a'), INK); cv.ellipse(x - 1, y - 1, 4, 3, hexc('ff8aa0'))
    cv.poly([(80, 80), (150, 80), (130, 160), (100, 160)], hexc('f4f0e8'))
    cv.line(80, 80, 100, 160, INK); cv.line(150, 80, 130, 160, INK)
    # 卡片
    cv.rect(170, 70, 100, 60, INK); cv.rect(171, 71, 98, 58, WHITE)
    cv.text(178, 80, 'To: 小语', INK)
    if t > 0.5:
        cv.line(198, 86, 236, 86, BAL_D); cv.line(198, 87, 236, 87, BAL_D)
        cv.text(196, 98, '小雨 ?', INK)
    # 她挑眉 + 他冒汗
    if t > 1.0:
        big_text(cv, 290, 40, '?', NAVY, size=24)
        symbol(cv, 'sweat', 60, 40, t)
    return cv


@shot(10)
def s10(t, D):
    cv = Canvas()
    off = int(t * 30)
    street_scene(cv, t, min(off, 80))
    # 风线
    for i in range(6):
        y = 40 + i * 16; x = (t * 160 + i * 50) % (W + 60) - 30
        cv.hline(x, x + 24, y, WHITE); cv.hline(x + 6, x + 18, y + 2, hexc('e0f0ff'))
    k = ease(clamp(t / D))
    bx = 80 + k * 210 - min(off, 80) * 0; by = 110 - k * 60 - math.sin(t * 5) * 6
    balloon(cv, bx, by, 1.3, t, str_len=24)
    HE(cv, 90 - min(off, 80), GROUND, 26, 'reach', 'surprise', t=t, facing=1)
    return cv


@shot(11)
def s11(t, D):
    cv = Canvas()
    sky_band(cv, SKY_DAY, 0, H)
    for i in range(5):
        x = (i * 80 + t * 5) % (W + 60) - 30
        cv.ellipse(x, 30 + i * 14, 20, 6, hexc('fff8f0')); cv.ellipse(x + 14, 26 + i * 14, 12, 6, hexc('fff8f0'))
    paris_row(cv, H + 10 - int(t * 6), seed=6)
    by = 120 - t * 18
    balloon(cv, 170, by, 3.0, t, face_=True, str_len=30)
    # 她在屋顶边抬头笑
    SHE(cv, 70, H + 6 - int(t * 6), 30, 'wave', 'joy', t=t)
    return cv
