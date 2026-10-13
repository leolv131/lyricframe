"""扁平 Q 版角色：他 / 她。头身比约 1:1.3，大头便于表情。
draw(f, who, x, feet_y, s, pose, expr, t, look, outfit)
s=1 → 头高 160 px（中景），全身约 380 px。"""
import math
import skia
from fq import *

SKIN, SKIN_D = '#ffdcc4', '#f2b9a0'
BLUSH = '#ff8fa0'
LOOK = {
    'he': dict(hair='#3a2a35', hair_h='#5a4652', top='#8f97ad', top_d='#737b92', bottom='#3f4259', shoe='#f4f1ea', style='spiky'),
    'he_work': dict(hair='#3a2a35', hair_h='#5a4652', top='#f4f4f8', top_d='#d4d6e4', bottom='#3f4259', shoe='#2b2b38', style='spiky', badge=True),
    'she': dict(hair='#4a2e2a', hair_h='#6e4840', top='#f7ead6', top_d='#e6d3b8', bottom='#9db6da', shoe='#ffffff', style='bob'),
    'npc': dict(hair='#45404a', hair_h='#5a5560', top='#b0a8c0', top_d='#968ea8', bottom='#4a4a5a', shoe='#e0e0e0', style='short'),
}

# ---------------------------------------------------------------- expressions
EXPR = {
    'normal':   dict(eyes='open', mouth='smile_s', brow='normal'),
    'smile':    dict(eyes='open', mouth='smile', brow='normal'),
    'happy':    dict(eyes='happy', mouth='open', brow='up'),
    'grin':     dict(eyes='happy', mouth='grin', brow='up', blush=True),
    'shy':      dict(eyes='down', mouth='smile_s', brow='normal', blush=True),
    'peek':     dict(eyes='open', mouth='smile_s', brow='normal', look=(0.6, 0), blush=True),
    'surprise': dict(eyes='wide', mouth='o', brow='up'),
    'scared':   dict(eyes='squeeze', mouth='wobble', brow='sad', sweat=True),
    'smug':     dict(eyes='half', mouth='smirk', brow='normal'),
    'stunned':  dict(eyes='dot', mouth='flat', brow='up'),
    'cold':     dict(eyes='half', mouth='flat', brow='flat'),
    'sad':      dict(eyes='sad', mouth='frown', brow='sad'),
    'lonely':   dict(eyes='down', mouth='flat', brow='sad'),
    'teary':    dict(eyes='sad', mouth='wobble', brow='sad', wet=True),
    'cry':      dict(eyes='closed_sad', mouth='wobble', brow='sad', tears=True),
    'tired':    dict(eyes='half', mouth='flat', brow='flat', circles=True),
    'insomnia': dict(eyes='open', mouth='flat', brow='flat', circles=True),
    'money':    dict(eyes='yen', mouth='grin', brow='up'),
    'determined': dict(eyes='open', mouth='smirk', brow='angry'),
    'blow':     dict(eyes='closed', mouth='o', brow='normal', blush=True),
    'love':     dict(eyes='happy', mouth='smile', brow='up', blush=True),
}


def _eye(f, x, y, s, kind, look, left, girl):
    ew, eh = 15 * s, 22 * s
    lx, ly = look[0] * 4 * s, look[1] * 4 * s
    lw = 4.5 * s
    if kind in ('open', 'wide', 'sad', 'half'):
        k = 1.25 if kind == 'wide' else 1.0
        rx, ry = ew * k, eh * k
        f.oval(x, y, rx, ry, INK)
        f.oval(x + lx * 0.6, y + ly * 0.6 + 3 * s, rx * 0.62, ry * 0.62, '#5a3a48')
        f.circle(x + lx + rx * 0.35, y - ry * 0.35, 5.5 * s * k, '#ffffff')
        f.circle(x + lx - rx * 0.3, y + ry * 0.38, 2.6 * s * k, '#ffffff')
        if kind == 'half':      # heavy lid
            f.rect(x - rx - 2, y - ry - 2, 2 * rx + 4, ry * 0.95, SKIN)
            f.line(x - rx, y - ry * 0.08, x + rx, y - ry * 0.08, INK, lw)
        if kind == 'sad':       # sad lid slant
            sgn = 1 if left else -1
            f.poly([(x - rx - 2, y - ry - 3), (x + rx + 2, y - ry - 3), (x + rx + 2, y - ry * (0.25 if left else -0.4) ), (x - rx - 2, y - ry * (-0.4 if left else 0.25))], SKIN, None)
            f.line(x - rx, y - ry * (-0.35 if left else 0.25), x + rx, y - ry * (0.25 if left else -0.35), INK, lw)
        if girl and kind != 'half':
            sgn = -1 if left else 1
            f.line(x + sgn * rx * 0.8, y - ry * 0.7, x + sgn * (rx + 7 * s), y - ry * 1.05, INK, 3.5 * s)
    elif kind == 'happy':
        f.curve([(x - ew, y + 4 * s), (x, y - 12 * s), (x + ew, y + 4 * s)], INK, lw)
    elif kind == 'closed':
        f.curve([(x - ew, y - 2 * s), (x, y + 8 * s), (x + ew, y - 2 * s)], INK, lw)
    elif kind == 'closed_sad':
        f.curve([(x - ew, y), (x, y + 5 * s), (x + ew, y)], INK, lw)
    elif kind == 'down':
        f.curve([(x - ew, y), (x, y + 8 * s), (x + ew, y)], INK, lw)
        for k in (-0.6, 0, 0.6): f.line(x + k * ew, y + 6 * s, x + k * ew * 1.15, y + 11 * s, INK, 2.5 * s)
    elif kind == 'squeeze':
        sgn = 1 if left else -1
        f.curve([(x - sgn * ew, y - 9 * s), (x + sgn * ew * 0.6, y), (x - sgn * ew, y + 9 * s)], INK, lw)
    elif kind == 'dot':
        f.circle(x, y, 5 * s, INK)
    elif kind == 'yen':
        f.text(x, y + 13 * s, '¥', 40 * s, '#e0a020', 'black', 'center', outline=INK, ow=4 * s)


def head(f, who, cx, cy, s, expr='normal', t=0.0, look=None, back=False, turn=0.0):
    """cx,cy = head centre. s=1 → head 160 tall."""
    L = LOOK[who]
    e = expr if isinstance(expr, dict) else EXPR.get(expr, EXPR['normal'])
    look = look or e.get('look', (0, 0))
    hw, hh = 88 * s, 80 * s
    lw = LINE * s
    girl = L['style'] == 'bob'
    tx = turn * 14 * s     # face features shift when turning
    # back hair
    if girl:
        f.blob([(cx - hw * 1.12, cy - hh * 0.2), (cx - hw * 0.9, cy - hh * 1.05), (cx + hw * 0.9, cy - hh * 1.05),
                (cx + hw * 1.12, cy - hh * 0.2), (cx + hw * 1.08, cy + hh * 0.85), (cx - hw * 1.08, cy + hh * 0.85)], L['hair'], INK, lw)
    # ears
    if not girl and not back:
        for sg in (-1, 1):
            f.oval(cx + sg * hw * 0.98 + tx * 0.3, cy + 6 * s, 13 * s, 17 * s, SKIN, INK, lw)
    # face
    f.blob([(cx - hw, cy - hh * 0.35), (cx - hw * 0.9, cy - hh), (cx + hw * 0.9, cy - hh), (cx + hw, cy - hh * 0.35),
            (cx + hw * 0.95, cy + hh * 0.6), (cx, cy + hh * 1.02), (cx - hw * 0.95, cy + hh * 0.6)],
           SKIN if not back else L['hair'], INK, lw)
    if back:
        f.blob([(cx - hw * 1.02, cy - hh * 0.1), (cx - hw * 0.92, cy - hh * 1.05), (cx + hw * 0.92, cy - hh * 1.05),
                (cx + hw * 1.02, cy - hh * 0.1), (cx + hw * 0.9, cy + hh * (0.9 if girl else 0.55)), (cx - hw * 0.9, cy + hh * (0.9 if girl else 0.55))], L['hair'], INK, lw)
        if not girl:
            f.oval(cx, cy + hh * 0.75, hw * 0.45, hh * 0.22, SKIN_D, None)
        f.curve([(cx - hw * 0.4, cy - hh * 0.75), (cx - hw * 0.1, cy - hh * 0.5)], L['hair_h'], 6 * s)
        return
    # front hair
    if girl:
        bangs = [(cx - hw * 1.05, cy + hh * 0.1), (cx - hw * 0.95, cy - hh * 1.08), (cx + hw * 0.95, cy - hh * 1.08), (cx + hw * 1.05, cy + hh * 0.1),
                 (cx + hw * 0.82, cy - hh * 0.25), (cx + hw * 0.45, cy - hh * 0.32), (cx + hw * 0.1, cy - hh * 0.22),
                 (cx - hw * 0.25, cy - hh * 0.36), (cx - hw * 0.6, cy - hh * 0.26), (cx - hw * 0.85, cy - hh * 0.3)]
        f.blob(bangs, L['hair'], INK, lw)
        # side locks
        for sg in (-1, 1):
            f.blob([(cx + sg * hw * 0.98, cy - hh * 0.3), (cx + sg * hw * 1.1, cy + hh * 0.2), (cx + sg * hw * 1.04, cy + hh * 0.86),
                    (cx + sg * hw * 0.82, cy + hh * 0.7), (cx + sg * hw * 0.84, cy - hh * 0.1)], L['hair'], INK, lw)
        # star clip
        sx, sy = cx + hw * 0.62, cy - hh * 0.55
        pts = [(sx + math.cos(a) * r * s, sy + math.sin(a) * r * s) for i, a in enumerate([-math.pi / 2 + k * math.pi / 5 for k in range(10)]) for r in [(13 if i % 2 == 0 else 6)]]
        f.poly(pts, '#ffcf4a', INK, 3 * s)
        f.curve([(cx - hw * 0.5, cy - hh * 0.9), (cx - hw * 0.2, cy - hh * 0.75)], L['hair_h'], 6 * s)
    else:
        spikes = [(cx - hw * 1.06, cy + hh * 0.0), (cx - hw * 1.08, cy - hh * 0.75), (cx - hw * 0.8, cy - hh * 1.18), (cx - hw * 0.45, cy - hh * 1.05),
                  (cx - hw * 0.15, cy - hh * 1.3), (cx + hw * 0.2, cy - hh * 1.1), (cx + hw * 0.55, cy - hh * 1.25), (cx + hw * 0.8, cy - hh * 1.0),
                  (cx + hw * 1.08, cy - hh * 0.85), (cx + hw * 1.06, cy + hh * 0.0),
                  (cx + hw * 0.92, cy - hh * 0.35), (cx + hw * 0.6, cy - hh * 0.42), (cx + hw * 0.4, cy - hh * 0.3), (cx + hw * 0.15, cy - hh * 0.45),
                  (cx - hw * 0.15, cy - hh * 0.3), (cx - hw * 0.45, cy - hh * 0.42), (cx - hw * 0.7, cy - hh * 0.3), (cx - hw * 0.92, cy - hh * 0.38)]
        sp = skia.Path(); sp.moveTo(*spikes[0])
        for p_ in spikes[1:]: sp.lineTo(*p_)
        sp.close()
        f.path(sp, L['hair'], INK, lw)
        f.curve([(cx - hw * 0.45, cy - hh * 0.85), (cx - hw * 0.15, cy - hh * 0.7)], L['hair_h'], 6 * s)
        f.curve([(cx + hw * 0.25, cy - hh * 0.9), (cx + hw * 0.45, cy - hh * 0.72)], L['hair_h'], 6 * s)

    # ---- features
    ey = cy + hh * 0.18
    ex = hw * 0.42
    eyes = e.get('eyes', 'open')
    if eyes in ('open',) and (t % 3.7) < 0.12: eyes = 'closed'
    if e.get('circles'):
        for sg in (-1, 1):
            f.curve([(cx + sg * ex - 16 * s + tx, ey + 26 * s), (cx + sg * ex + tx, ey + 33 * s), (cx + sg * ex + 16 * s + tx, ey + 26 * s)], '#a88ab8', 4 * s)
    for k, sg in enumerate((-1, 1)):
        _eye(f, cx + sg * ex + tx, ey, s, eyes, look, sg < 0, girl)
    # brows
    br = e.get('brow', 'normal')
    by = ey - 36 * s
    for sg in (-1, 1):
        bx = cx + sg * ex + tx
        if br == 'normal': pts = [(bx - 13 * s, by + 2 * s), (bx, by - 2 * s), (bx + 13 * s, by + 2 * s)]
        elif br == 'up': pts = [(bx - 13 * s, by - 3 * s), (bx, by - 9 * s), (bx + 13 * s, by - 3 * s)]
        elif br == 'flat': pts = [(bx - 13 * s, by + 2 * s), (bx + 13 * s, by + 2 * s)]
        elif br == 'sad': pts = [(bx - sg * 13 * s, by - 6 * s), (bx + sg * 13 * s, by + 4 * s)]
        elif br == 'angry': pts = [(bx - sg * 13 * s, by + 6 * s), (bx + sg * 13 * s, by - 4 * s)]
        pts = [(px_, py_) for px_, py_ in pts]
        if not girl or True:
            f.curve(pts, L['hair'], 5 * s)
    # blush
    if e.get('blush'):
        for sg in (-1, 1):
            f.oval(cx + sg * ex * 1.35 + tx, ey + 30 * s, 18 * s, 9 * s, BLUSH, None, a=0.75)
            for k in range(3):
                bx = cx + sg * ex * 1.35 + tx - 10 * s + k * 9 * s
                f.line(bx, ey + 34 * s, bx + 5 * s, ey + 26 * s, '#ff6f86', 2.5 * s)
    # mouth
    mx, my = cx + tx * 1.1, cy + hh * 0.62
    m = e.get('mouth', 'smile_s')
    if m == 'smile_s': f.curve([(mx - 9 * s, my - 2 * s), (mx, my + 4 * s), (mx + 9 * s, my - 2 * s)], INK, 4 * s)
    elif m == 'smile': f.curve([(mx - 15 * s, my - 4 * s), (mx, my + 7 * s), (mx + 15 * s, my - 4 * s)], INK, 4.5 * s)
    elif m == 'open':
        p = skia.Path(); p.moveTo(mx - 15 * s, my - 4 * s); p.quadTo(mx, my - 2 * s, mx + 15 * s, my - 4 * s); p.quadTo(mx, my + 26 * s, mx - 15 * s, my - 4 * s); p.close()
        f.path(p, '#c0455a', INK, 4 * s); f.oval(mx, my + 10 * s, 8 * s, 4 * s, '#ff8f9c', None)
    elif m == 'grin':
        p = skia.Path(); p.moveTo(mx - 22 * s, my - 6 * s); p.quadTo(mx, my - 2 * s, mx + 22 * s, my - 6 * s); p.quadTo(mx, my + 30 * s, mx - 22 * s, my - 6 * s); p.close()
        f.path(p, '#c0455a', INK, 4 * s); f.rect(mx - 15 * s, my - 4 * s, 30 * s, 6 * s, '#ffffff')
    elif m == 'o': f.oval(mx, my + 3 * s, 7 * s, 9 * s, '#c0455a', INK, 4 * s)
    elif m == 'flat': f.line(mx - 10 * s, my + 2 * s, mx + 10 * s, my + 2 * s, INK, 4 * s)
    elif m == 'frown': f.curve([(mx - 12 * s, my + 6 * s), (mx, my - 2 * s), (mx + 12 * s, my + 6 * s)], INK, 4.5 * s)
    elif m == 'wobble': f.curve([(mx - 14 * s, my + 3 * s), (mx - 7 * s, my - 2 * s), (mx, my + 3 * s), (mx + 7 * s, my - 2 * s), (mx + 14 * s, my + 3 * s)], INK, 4 * s)
    elif m == 'smirk': f.curve([(mx - 12 * s, my + 2 * s), (mx + 4 * s, my + 4 * s), (mx + 14 * s, my - 5 * s)], INK, 4.5 * s)
    # tears / wet / sweat
    if e.get('wet') or e.get('tears'):
        for sg in (-1, 1):
            f.oval(cx + sg * ex + tx, ey + 14 * s, 13 * s, 4 * s, '#a8e4ff', None, a=0.9)
    if e.get('tears'):
        for sg in (-1, 1):
            x0 = cx + sg * (ex + 4 * s) + tx
            L_ = 40 * s + (t * 60 % 20) * s
            f.line(x0, ey + 12 * s, x0 + sg * 3 * s, ey + 12 * s + L_, '#8fd8ff', 7 * s, a=0.95)
    if e.get('sweat'):
        sx, sy = cx + hw * 0.95, cy - hh * 0.45
        f.blob([(sx, sy - 18 * s), (sx + 9 * s, sy + 2 * s), (sx, sy + 9 * s), (sx - 9 * s, sy + 2 * s)], '#a8e4ff', INK, 3 * s)


# ---------------------------------------------------------------- body
POSES = {   # arms: (shoulder°, elbow°) from straight down, + = outward;  legs: (hip°, knee°)
    'stand':  dict(la=(12, 0), ra=(12, 0), ll=(4, 0), rl=(4, 0)),
    'wave':   dict(la=(12, 0), ra=(150, 30), ll=(4, 0), rl=(4, 0)),
    'cheer':  dict(la=(150, -10), ra=(150, -10), ll=(8, 0), rl=(8, 0)),
    'reach':  dict(la=(12, 0), ra=(80, 0), ll=(4, 0), rl=(4, 0)),
    'chest':  dict(la=(-20, -110), ra=(-20, -110), ll=(4, 0), rl=(4, 0)),     # hands on own chest
    'eat':    dict(la=(-10, -90), ra=(-15, -100), ll=(4, 0), rl=(4, 0)),
    'sit':    dict(la=(10, -40), ra=(10, -40), ll=(-90, 90), rl=(-90, 90), sit=True),
    'ride':   dict(la=(-30, -70), ra=(75, 15), ll=(-80, 85), rl=(-80, 85), sit=True),
    'hug_back': dict(la=(-60, -70), ra=(-60, -70), ll=(-80, 85), rl=(-80, 85), sit=True),
    'arms_open': dict(la=(100, 0), ra=(100, 0), ll=(-80, 85), rl=(-80, 85), sit=True),
    'peace':  dict(la=(12, 0), ra=(140, 50), ll=(4, 0), rl=(4, 0)),
    'shrug':  dict(la=(55, -80), ra=(55, -80), ll=(4, 0), rl=(4, 0)),
    'cover_ears': dict(la=(150, 120), ra=(150, 120), ll=(4, 0), rl=(4, 0)),
    'walk':   dict(la=(18, 0), ra=(-18, 0), ll=(14, 0), rl=(-14, 0), walk=True),
}


def _limb(f, x, y, a1, a2, l1, l2, w, col, side, hand=True, s=1.0, shoe=None):
    sg = -1 if side == 'l' else 1
    r1 = math.radians(a1) * sg; r2 = math.radians(a1 + a2) * sg
    ex, ey = x + math.sin(r1) * l1, y + math.cos(r1) * l1
    hx, hy = ex + math.sin(r2) * l2, ey + math.cos(r2) * l2
    p = skia.Path(); p.moveTo(x, y); p.lineTo(ex, ey); p.lineTo(hx, hy)
    f.c.drawPath(p, f.stroke(INK, w + 2 * LINE * s))
    f.c.drawPath(p, f.stroke(col, w))
    if hand:
        f.circle(hx, hy, w * 0.62, SKIN, INK, LINE * s * 0.9)
    if shoe:
        f.oval(hx + sg * 4 * s, hy + 4 * s, w * 0.75, w * 0.45, shoe, INK, LINE * s * 0.9)
    return (hx, hy)


def draw(f, who, x, feet, s=1.0, pose='stand', expr='normal', t=0.0, look=None, back=False, turn=0.0, hide_legs=False, extra=None):
    """Full chibi. Returns dict with head centre and hand positions."""
    L = LOOK[who]
    P = POSES[pose] if isinstance(pose, str) else pose
    hh = 80 * s
    tw, th = 64 * s, 118 * s              # half torso width, torso height
    leg_l1, leg_l2, lw_ = 42 * s, 40 * s, 40 * s
    sit = P.get('sit')
    walkph = math.sin(t * 9) if P.get('walk') else 0
    legh = 0 if sit else (leg_l1 + leg_l2)
    bob = abs(walkph) * 4 * s
    hip = feet - legh - 8 * s - bob
    top = hip - th
    hcy = top - hh * 0.78
    out = {}
    # legs
    if not hide_legs:
        for side, key in (('l', 'll'), ('r', 'rl')):
            a1, a2 = P[key]
            if P.get('walk'): a1 = a1 * (walkph if side == 'l' else -walkph)
            sx = x + (-1 if side == 'l' else 1) * tw * 0.45
            _limb(f, sx, hip - 6 * s, a1, a2, leg_l1, leg_l2, lw_, L['bottom'], side, hand=False, s=s, shoe=L['shoe'])
    # torso (hoodie / sweater / shirt)
    body = [(x - tw * 0.82, top + 6 * s), (x + tw * 0.82, top + 6 * s), (x + tw * 1.02, hip), (x - tw * 1.02, hip)]
    f.blob([(x - tw * 0.85, top), (x + tw * 0.85, top), (x + tw * 1.08, hip - 18 * s), (x + tw * 1.0, hip + 4 * s),
            (x - tw * 1.0, hip + 4 * s), (x - tw * 1.08, hip - 18 * s)], L['top'], INK, LINE * s)
    if not back:
        if who == 'he':        # hoodie pocket + strings
            f.rect(x - tw * 0.55, hip - 46 * s, tw * 1.1, 32 * s, L['top_d'], INK, 3.5 * s, r=10 * s)
            f.line(x - 12 * s, top + 8 * s, x - 14 * s, top + 40 * s, '#f4f1ea', 4 * s)
            f.line(x + 12 * s, top + 8 * s, x + 14 * s, top + 40 * s, '#f4f1ea', 4 * s)
        if who == 'he_work':   # collar + lanyard badge
            f.poly([(x - 22 * s, top + 2 * s), (x, top + 26 * s), (x + 22 * s, top + 2 * s)], '#ffffff', INK, 3.5 * s, close=False)
            f.line(x - 16 * s, top + 4 * s, x, top + 60 * s, '#3a6ad4', 4 * s); f.line(x + 16 * s, top + 4 * s, x, top + 60 * s, '#3a6ad4', 4 * s)
            f.rect(x - 14 * s, top + 58 * s, 28 * s, 34 * s, '#ffffff', INK, 3 * s, r=4 * s); f.rect(x - 9 * s, top + 64 * s, 18 * s, 8 * s, '#3a6ad4')
        if who == 'she':       # sweater ribs + collar
            for k in range(-2, 3): f.line(x + k * 18 * s, hip - 14 * s, x + k * 18 * s, hip - 2 * s, L['top_d'], 3 * s)
            f.curve([(x - 26 * s, top + 4 * s), (x, top + 18 * s), (x + 26 * s, top + 4 * s)], L['top_d'], 5 * s)
    # arms
    for side, key in (('l', 'la'), ('r', 'ra')):
        a1, a2 = P[key]
        if P.get('walk'): a1 = a1 * (-walkph if side == 'l' else walkph) * 1.0 + 8
        if pose == 'wave' and side == 'r': a2 = 30 + 25 * math.sin(t * 14)
        sx = x + (-1 if side == 'l' else 1) * tw * 0.85
        out['hand_' + side] = _limb(f, sx, top + 22 * s, a1, a2, 46 * s, 42 * s, 30 * s, L['top'], side, s=s)
    if extra: extra(f, out)
    head(f, who, x, hcy, s, expr, t, look, back)
    out['head'] = (x, hcy); out['top'] = top; out['hip'] = hip
    return out


def symbol(f, kind, x, y, s=1.0, t=0.0):
    y += math.sin(t * 6) * 4 * s
    if kind == 'heart':
        p = skia.Path(); p.moveTo(x, y + 14 * s)
        p.cubicTo(x - 30 * s, y - 8 * s, x - 14 * s, y - 26 * s, x, y - 10 * s)
        p.cubicTo(x + 14 * s, y - 26 * s, x + 30 * s, y - 8 * s, x, y + 14 * s); p.close()
        f.path(p, '#ff5f7e', INK, 4 * s)
        f.oval(x - 9 * s, y - 9 * s, 4 * s, 3 * s, '#ffffff', None)
    elif kind == 'excl':
        f.text(x, y, '!', 64 * s, '#ffcf4a', 'black', 'center', outline=INK, ow=6 * s)
    elif kind == 'q':
        f.text(x, y, '?', 64 * s, '#ffffff', 'black', 'center', outline=INK, ow=6 * s)
    elif kind == 'zzz':
        for k in range(3):
            f.text(x + k * 22 * s, y - k * 22 * s, 'z', (30 + k * 8) * s, '#ffffff', 'black', 'center', outline=INK, ow=5 * s)
    elif kind == 'sparkle':
        for a in range(4):
            r = math.radians(a * 90)
            f.line(x, y, x + math.cos(r) * 16 * s, y + math.sin(r) * 16 * s, '#ffe27a', 5 * s)
        f.circle(x, y, 5 * s, '#ffffff')
