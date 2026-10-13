"""Chibi pixel characters, procedurally drawn at any head size (pixel size stays 1).
who: 'boy' (少年他), 'girl' (她), 'man' (成年他), 'post' (邮差)
"""
import math
import numpy as np
from px import PAL, rrect_mask, ell_mask, dilate, mix

INK = PAL['ink']

LOOK = {
    'boy':  dict(hair='boy',  top=PAL['shirt'], top_d=PAL['shirt_d'], bottom=PAL['pants'], bottom_d=PAL['pants_d'], dress=False, coat=False),
    'girl': dict(hair='bob',  top=PAL['dress'], top_d=PAL['dress_d'], bottom=PAL['dress'], bottom_d=PAL['dress_d'], dress=True,  coat=False),
    'man':  dict(hair='boy',  top=PAL['coat'],  top_d=PAL['coat_d'],  bottom=PAL['pants_d'], bottom_d=PAL['ink2'],  dress=False, coat=True),
    'woman': dict(hair='long', top=(200, 148, 106), top_d=(160, 112, 80), bottom=(60, 52, 70), bottom_d=(40, 34, 50), dress=False, coat=True),
    'kid':  dict(hair='bob',  top=(255, 160, 176), top_d=(220, 120, 140), bottom=(255, 160, 176), bottom_d=(220, 120, 140), dress=True, coat=False),
    'boy_w': dict(hair='boy', top=(70, 110, 90), top_d=(50, 84, 68), bottom=PAL['pants'], bottom_d=PAL['pants_d'], dress=False, coat=False),
    'npc':  dict(hair='boy',  top=(110, 116, 130), top_d=(84, 90, 104), bottom=(70, 74, 86), bottom_d=(54, 58, 70), dress=False, coat=True),
    'npc_g': dict(hair='bob', top=(130, 120, 130), top_d=(100, 92, 104), bottom=(70, 74, 86), bottom_d=(54, 58, 70), dress=False, coat=True),
    'wu':   dict(hair='boy',  top=(150, 154, 166), top_d=(118, 122, 136), bottom=(64, 76, 108), bottom_d=(48, 58, 86), dress=False, coat=False),
    'wu_ap': dict(hair='boy', top=(150, 154, 166), top_d=(118, 122, 136), bottom=(64, 76, 108), bottom_d=(48, 58, 86), dress=False, coat=False),
    'die':  dict(hair='bob',  top=(247, 234, 214), top_d=(222, 204, 180), bottom=(150, 190, 228), bottom_d=(118, 158, 204), dress=False, coat=False),
    'he':   dict(hair='boy',  top=(170, 210, 240), top_d=(130, 176, 216), bottom=(196, 170, 120), bottom_d=(166, 140, 96), dress=False, coat=False),
    'she':  dict(hair='long', top=(255, 176, 190), top_d=(232, 140, 160), bottom=(255, 176, 190), bottom_d=(232, 140, 160), dress=True, coat=False),
    'post': dict(hair='cap',  top=(70, 120, 90), top_d=(50, 92, 70), bottom=(60, 70, 90), bottom_d=(44, 52, 70), dress=False, coat=False),
}


def thick_line(cv, x0, y0, x1, y1, w, c, outline=None):
    n = int(max(abs(x1 - x0), abs(y1 - y0))) + 1
    pts = [(x0 + (x1 - x0) * i / max(n - 1, 1), y0 + (y1 - y0) * i / max(n - 1, 1)) for i in range(n)]
    r = w / 2
    if outline is not None:
        for x, y in pts: cv.rect(round(x - r) - 1, round(y - r) - 1, w + 2, w + 2, outline)
    for x, y in pts: cv.rect(round(x - r), round(y - r), w, w, c)


def back_hair(cv, who, cx, top, Hh):
    L = LOOK[who]
    Wh = int(round(Hh * 1.04))
    bw = Wh + 2 * max(1, round(Hh * (0.10 if L['hair'] == 'bob' else 0.07)))
    bh = int(round(Hh * (1.12 if L['hair'] == 'bob' else 1.70)))
    bm = rrect_mask(bw, bh, max(2, int(round(Hh * 0.45))))
    bx = int(round(cx - bw / 2))
    cv.mask_fill(dilate(bm), INK, bx - 1, top - 2)
    cv.mask_fill(bm, PAL['hair'], bx, top - 1)


def head(cv, who, cx, top, Hh, expr='normal', facing=0, t=0.0, back=False, blush=None, skip_back=False):
    """Draw head with hair + face. cx = center x, top = y of head top. Returns face anchor dict."""
    cx, top = int(round(cx)), int(round(top))
    L = LOOK[who]
    Wh = int(round(Hh * 1.04))
    x0 = int(round(cx - Wh / 2))
    r = max(2, int(round(Hh * 0.42)))
    hm = rrect_mask(Wh, Hh, r)

    # back hair (bob)
    if L['hair'] in ('bob', 'long') and not skip_back:
        back_hair(cv, who, cx, top, Hh)

    # head
    cv.mask_fill(dilate(hm), INK, x0 - 1, top - 1)
    cv.mask_fill(hm, PAL['skin'], x0, top)

    # hair cap
    hair_c = PAL['hair']
    if back:
        cv.mask_fill(hm, hair_c, x0, top)
        if L['hair'] in ('bob', 'long'):
            cv.rect(x0, top + int(Hh * 0.9), Wh, max(1, Hh // 8) + (int(Hh * 0.6) if L['hair'] == 'long' else 0), hair_c)
        else:
            # nape skin
            nh = max(1, int(Hh * 0.18)); cv.rect(x0 + Wh // 4, top + Hh - nh, Wh // 2, nh, PAL['skin_d'])
        hl = max(1, Hh // 10)
        cv.rect(x0 + Wh // 4, top + max(1, Hh // 8), max(1, Wh // 5), hl, PAL['hair_h'])
        return dict(cx=cx, top=top, Hh=Hh, Wh=Wh)

    hmp = dilate(hm)            # head incl. outline, offset (x0-1, top-1)
    Whp = Wh + 2
    if L['hair'] in ('boy', 'cap'):
        cut = int(round(Hh * ((0.40 if Hh < 36 else 0.34) if L['hair'] == 'boy' else 0.36))) + 1
        hm, Wh_save = hmp, Wh
        Wh = Whp
        m = hm.copy(); m[cut:, :] = False
        # side burns
        sb = max(1, int(round(Wh * 0.10))); sh = int(round(Hh * 0.56))
        m[cut:sh, :sb] = hm[cut:sh, :sb]; m[cut:sh, Wh - sb:] = hm[cut:sh, Wh - sb:]
        # fringe jag
        if Hh >= 12:
            step = max(2, Wh // 6)
            for i in range(0, Wh, step):
                d = (i // step) % 2 + (1 if Hh >= 24 else 0)
                m[cut:cut + d, i:i + step // 2 + 1] = hm[cut:cut + d, i:i + step // 2 + 1]
        Wh = Wh_save
        if L['hair'] == 'cap':
            capc = (70, 120, 90)
            cv.mask_fill(dilate(m), INK, x0 - 2, top - 3)
            cv.mask_fill(m, capc, x0 - 1, top - 2)
            br = max(2, Wh // 2); cv.rect(x0 + (Wh - br) // 2 + facing * Wh // 3, top + cut - 2, br, max(1, Hh // 10), (50, 92, 70))
        else:
            cv.mask_fill(dilate(m), INK, x0 - 2, top - 3)
            cv.mask_fill(m, hair_c, x0 - 1, top - 2)
            if 14 <= Hh < 36:
                cv.rect(x0 + Wh // 4 - facing * 2, top + max(1, Hh // 9), max(1, Wh // 5), max(1, Hh // 14), PAL['hair_h'])
            if Hh >= 36:  # strand lines
                for k in range(3):
                    sx_ = x0 + Wh // 3 + k * Wh // 6 - facing * 2
                    cv.line(sx_, top + Hh // 10, sx_ - 2, top + Hh // 4, PAL['hair_h'])
    elif L['hair'] in ('bob', 'long'):
        cut = int(round(Hh * (0.36 if Hh < 36 else 0.31))) + 1
        m = hmp.copy(); m[cut:, :] = False
        # straight bangs line, side locks
        sl = max(1, int(round(Wh * 0.16))) + 1
        lo = int(round(Hh * 0.98)) + 1
        m[cut:lo, :sl] = hmp[cut:lo, :sl]; m[cut:lo, Whp - sl:] = hmp[cut:lo, Whp - sl:]
        if Hh >= 36:  # bang notches
            for i in range(sl + 2, Whp - sl - 2, max(3, Wh // 7)):
                m[cut:cut + 2, i] = True
        dm = dilate(m)
        hgt, wid = dm.shape
        ox, oy = x0 - 2, top - 2
        for yy in range(hgt):
            for xx in range(wid):
                if dm[yy, xx]:
                    X, Y = ox + xx, oy + yy
                    if 0 <= X < cv.a.shape[1] and 0 <= Y < cv.a.shape[0] and tuple(cv.a[Y, X]) == PAL['skin']:
                        cv.a[Y, X] = INK
        cv.mask_fill(m, hair_c, x0 - 1, top - 1)
        if 14 <= Hh < 36:
            cv.rect(x0 + Wh // 4 - facing * 2, top + max(1, Hh // 9), max(1, Wh // 4), max(1, Hh // 14), PAL['hair_h'])
        elif Hh >= 36:
            for k in range(3):
                sx_ = x0 + Wh // 3 + k * Wh // 6 - facing * 2
                cv.line(sx_, top + Hh // 12, sx_ - 2, top + Hh // 5, PAL['hair_h'])

    # ---- face
    ey = top + int(round(Hh * 0.60))
    edx = max(2, int(round(Wh * 0.21)))
    fsh = int(round(facing * Wh * 0.09))
    ew = max(1, int(round(Hh * 0.10)))
    eh = max(2, int(round(Hh * 0.16)))
    exs = [int(round(cx - edx + fsh - ew / 2)), int(round(cx + edx + fsh - ew / 2))]
    my = top + int(round(Hh * 0.82))
    mx = int(round(cx + fsh))

    e = expr if isinstance(expr, dict) else EXPR.get(expr, EXPR['normal'])
    eyes = e.get('eyes', 'open'); mouth = e.get('mouth', 'none')
    if Hh >= 36:
        bl = blush if blush is not None else e.get('blush', False)
        return face_big(cv, who, cx, top, Hh, Wh, e, eyes, mouth, facing, t, bl)

    # blink every ~3.3s unless overridden
    if eyes == 'open' and (t % 3.3) < 0.12: eyes = 'closed'

    for ex in exs:
        if eyes == 'open' or eyes == 'wide':
            hh = eh + (max(1, eh // 3) if eyes == 'wide' else 0)
            ww = ew + (1 if eyes == 'wide' and Hh >= 20 else 0)
            cv.rect(ex, ey - hh // 2, ww, hh, INK)
            if ww >= 2 and hh >= 3:
                cv.px(ex + ww - 1 - (ww >= 4), ey - hh // 2 + (hh >= 5), PAL['white'])
            if ww >= 4 and hh >= 6:
                cv.rect(ex + 1, ey - hh // 2 + 2, max(1, ww // 3), max(1, hh // 4), PAL['white'])
        elif eyes == 'down':
            hh = max(1, eh // 2)
            cv.rect(ex, ey - hh // 2 + 1, ew, hh, INK)
        elif eyes == 'closed':
            cv.rect(ex - (ew > 1), ey, ew + 2 * (ew > 1), max(1, Hh // 20), INK)
        elif eyes == 'happy':  # ^ ^
            w = ew + 2
            cv.px(ex - 1, ey + 1, INK); cv.rect(ex, ey, ew, 1, INK); cv.px(ex + ew, ey + 1, INK)
            if Hh >= 24: cv.px(ex - 2, ey + 2, INK); cv.px(ex + ew + 1, ey + 2, INK)
        elif eyes == 'dot':
            cv.rect(ex + ew // 2 - (ew >= 3) // 2, ey - 1, max(1, ew // 2), max(1, eh // 2), INK)
        elif eyes == 'sad':
            hh = max(1, eh - 1)
            cv.rect(ex, ey - hh // 2 + 1, ew, hh, INK)
            if ew >= 2: cv.px(ex + ew - 1, ey - hh // 2 + 1, PAL['white'])

    # brows
    br = e.get('brow')
    if br and Hh >= 14:
        by = ey - eh // 2 - max(2, Hh // 9)
        for k, ex in enumerate(exs):
            bw = ew + 2
            inner = (k == 0)
            for i in range(bw):
                yy = by
                if br == 'sad':
                    yy += (-(i * 2) // bw) if inner else (-((bw - 1 - i) * 2) // bw)
                    yy += 1
                elif br == 'worry':
                    yy += 0 if inner else 0
                cv.px(ex - 1 + i, yy, INK)

    # blush
    bl = blush if blush is not None else e.get('blush', False)
    if bl:
        bw = max(1, int(round(Hh * 0.14))); bhh = max(1, int(round(Hh * 0.06)))
        for k, ex in enumerate(exs):
            bx = ex - bw if k == 0 else ex + ew
            bx = ex + ew // 2 - bw // 2 + (-1 if k == 0 else 1) * max(1, ew // 2 + 1)
            cv.rect(bx, ey + eh // 2 + 1, bw, bhh, PAL['blush'])

    # mouth
    if mouth == 'smile':
        w = max(2, int(round(Hh * 0.16)))
        cv.rect(mx - w // 2, my, w, 1, INK)
        cv.px(mx - w // 2 - 1, my - 1, INK); cv.px(mx - w // 2 + w, my - 1, INK)
    elif mouth == 'open':
        w = max(2, int(round(Hh * 0.16))); h = max(2, int(round(Hh * 0.12)))
        cv.rect(mx - w // 2, my - 1, w, h, INK)
        if w >= 3 and h >= 3: cv.rect(mx - w // 2 + 1, my - 1 + h // 2, w - 2, h - h // 2 - 1 or 1, PAL['red'])
    elif mouth == 'flat':
        w = max(2, int(round(Hh * 0.12))); cv.rect(mx - w // 2, my, w, 1, INK)
    elif mouth == 'o':
        w = max(1, int(round(Hh * 0.07))); cv.rect(mx - w // 2, my - 1, w, max(1, w + 1), INK)
    elif mouth == 'frown':
        w = max(2, int(round(Hh * 0.14)))
        cv.rect(mx - w // 2, my - 1, w, 1, INK); cv.px(mx - w // 2 - 1, my, INK); cv.px(mx - w // 2 + w, my, INK)
    elif mouth == 'wobble':
        w = max(3, int(round(Hh * 0.18)))
        for i in range(w): cv.px(mx - w // 2 + i, my + (i % 2), INK)

    # tears
    if e.get('tear'):
        tl = max(1, int(Hh * 0.12))
        for k, ex in enumerate(exs):
            cv.rect(ex + (ew // 2 if k else 0), ey + eh // 2 + 1, max(1, ew // 2), tl, PAL['tear'])

    return dict(cx=cx, top=top, Hh=Hh, Wh=Wh, ey=ey, exs=exs, my=my)


IRIS = (70, 40, 52)

def face_big(cv, who, cx, top, Hh, Wh, e, eyes, mouth, facing, t, bl):
    girl = (who in ('girl', 'woman', 'kid', 'npc_g', 'die', 'she'))
    fsh = int(round(facing * Wh * 0.08))
    ey = top + int(round(Hh * 0.60))
    edx = int(round(Wh * 0.22))
    ew = int(round(Hh * 0.15)); eh = int(round(Hh * 0.22))
    if girl: eh += 1
    exs = [int(round(cx - edx + fsh - ew / 2)), int(round(cx + edx + fsh - ew / 2))]
    look = e.get('look', (0, 0))
    if eyes == 'open' and (t % 3.3) < 0.12: eyes = 'closed'
    # ears (boy/man)
    if who not in ('girl', 'woman', 'kid', 'npc_g', 'die', 'she'):
        for k, sgn in enumerate((-1, 1)):
            exx = int(cx + sgn * (Wh / 2 + 1)) - (2 if sgn < 0 else 0)
            cv.rect(exx - 1, ey - 3, 4, 7, INK); cv.rect(exx, ey - 2, 2, 5, PAL['skin'])
    for k, ex in enumerate(exs):
        top_e = ey - eh // 2
        if eyes == 'down':
            for i in range(ew + 2):
                yy = ey + 1 + (1 if 1 < i < ew else 0)
                cv.rect(ex - 1 + i, yy, 1, 2, INK)
            for i in (1, ew // 2, ew - 1):
                cv.px(ex + i, ey + 4, INK)
            continue
        if eyes in ('open', 'wide', 'sad', 'look_up'):
            hh = eh + (2 if eyes == 'wide' else 0)
            ty = top_e - (1 if eyes == 'wide' else 0)
            if eyes == 'down':  # lowered lids
                ty = top_e + eh // 2; hh = eh - eh // 2
            m = rrect_mask(ew, hh, max(1, ew // 3))
            cv.mask_fill(m, INK, ex, ty)
            # iris
            iw, ih = max(1, ew - 2), max(1, hh - 3)
            ix = ex + 1 + look[0]; iy = ty + 2 + look[1]
            cv.mask_fill(rrect_mask(iw, ih, max(1, iw // 3)), IRIS, ix, iy)
            cv.rect(ix + iw // 2 - 1, iy + ih // 3, max(1, iw // 2), max(1, ih // 2), INK)  # pupil
            # highlights
            if eyes != 'down':
                cv.rect(ex + ew - 3 - (ew >= 7), ty + 2, 2, 2, PAL['white'])
                cv.px(ex + 1 + (ew >= 7), ty + hh - 3, PAL['white'])
            # lash line (thicker top) + outer flick
            cv.rect(ex - 1, ty - 1, ew + 2, 2, INK)
            if girl:
                if k == 0: cv.px(ex - 2, ty - 2, INK); cv.px(ex - 1, ty - 2, INK)
                else: cv.px(ex + ew + 1, ty - 2, INK); cv.px(ex + ew, ty - 2, INK)
            if e.get('tear') or e.get('wet'):
                cv.rect(ex, ty + hh - 2, ew, 1, PAL['tear'])  # welled shine
                cv.px(ex + 1, ty + 3, PAL['tear'])
        elif eyes == 'happy':
            for i in range(ew + 2):
                yy = ey + 1 - (2 if 1 < i < ew else (1 if i in (1, ew) else 0))
                cv.rect(ex - 1 + i, yy, 1, 2, INK)
        elif eyes == 'closed':
            for i in range(ew + 2):
                yy = ey + (1 if 1 < i < ew else 0)
                cv.rect(ex - 1 + i, yy, 1, 2, INK)
        elif eyes == 'dot':
            cv.rect(ex + ew // 2 - 1, ey - 2, 3, 4, INK)
        elif eyes == 'squeeze':  # > <
            for i in range(ew // 2 + 1):
                cv.rect(ex + (i if k == 0 else ew - i), ey - ew // 2 + i, 2, 1, INK)
                cv.rect(ex + (i if k == 0 else ew - i), ey + ew // 2 - i, 2, 1, INK)
    # brows
    br = e.get('brow', 'normal')
    bwid = ew + 2
    by = ey - eh // 2 - 5 - (2 if br == 'up' else 0)
    for k, ex in enumerate(exs):
        for i in range(bwid):
            inner = (i >= bwid // 2) if k == 0 else (i < bwid // 2)
            yy = by
            d = i if k == 1 else bwid - 1 - i   # distance from inner end
            if br == 'sad': yy = by + d * 3 // bwid - 2 + 2
            elif br == 'normal': yy = by + (0 if 1 < i < bwid - 2 else 1)
            elif br == 'up': yy = by + (0 if 1 < i < bwid - 2 else 1)
            elif br == 'worry': yy = by + d * 2 // bwid
            cv.rect(ex - 1 + i, yy, 1, 2, PAL['hair'])
    # nose
    cv.px(int(cx + fsh), ey + eh // 2 + 2, PAL['skin_d']); cv.px(int(cx + fsh) + 1, ey + eh // 2 + 3, PAL['skin_d'])
    # blush hatch
    if bl:
        for k, ex in enumerate(exs):
            bx = ex - 2 if k == 0 else ex + 1
            byy = ey + eh // 2 + 2
            cv.rect(bx, byy, ew + 1, 3, PAL['blush'])
            for j in range(3):
                cv.line(bx + 1 + j * 2, byy + 2, bx + 2 + j * 2, byy, mix(PAL['blush'], PAL['white'], 0.4))
    # mouth
    my = top + int(round(Hh * 0.84)); mx = int(round(cx + fsh))
    w = int(round(Hh * 0.16))
    if mouth == 'smile':
        cv.rect(mx - w // 2, my, w, 1, INK); cv.px(mx - w // 2 - 1, my - 1, INK); cv.px(mx + w // 2 + (w % 2), my - 1, INK)
    elif mouth == 'open':
        m = rrect_mask(w, w * 2 // 3 + 1, 2)
        cv.mask_fill(dilate(m), INK, mx - w // 2 - 1, my - 2); cv.mask_fill(m, PAL['red_d'], mx - w // 2, my - 1)
        cv.rect(mx - w // 2 + 1, my - 1 + w // 3, w - 2, max(1, w // 3), PAL['pink'])
    elif mouth == 'flat':
        cv.rect(mx - w // 2 + 1, my, w - 2, 1, INK)
    elif mouth == 'o':
        cv.rect(mx - 1, my - 1, 3, 3, INK); cv.px(mx, my, PAL['red_d'])
    elif mouth == 'frown':
        cv.rect(mx - w // 2 + 1, my - 1, w - 2, 1, INK); cv.px(mx - w // 2, my, INK); cv.px(mx + w // 2 - 1 + (w % 2), my, INK)
    elif mouth == 'wobble':
        for i in range(w + 2): cv.px(mx - w // 2 - 1 + i, my + ((i // 2) % 2), INK)
    elif mouth == 'part':   # about to speak
        cv.rect(mx - w // 4, my - 1, max(2, w // 2), 2, INK)
    # tears streaming
    if e.get('tear'):
        for k, ex in enumerate(exs):
            tx = ex + (1 if k == 0 else ew - 2)
            L = int(Hh * 0.18) + int((t * 10) % 3)
            cv.rect(tx, ey + eh // 2, 2, L, PAL['tear'])
            cv.rect(tx, ey + eh // 2 + L, 2, 2, mix(PAL['tear'], PAL['white'], 0.5))
    return dict(cx=cx, top=top, Hh=Hh, Wh=Wh, ey=ey, exs=exs, my=my)


EXPR = {
    'normal': dict(eyes='open', mouth='none'),
    'smile': dict(eyes='open', mouth='smile'),
    'happy': dict(eyes='happy', mouth='open'),
    'joy': dict(eyes='happy', mouth='open', blush=True),
    'shy': dict(eyes='down', mouth='smile', blush=True),
    'peek': dict(eyes='open', mouth='smile', blush=False),
    'wonder': dict(eyes='wide', mouth='o'),
    'surprise': dict(eyes='wide', mouth='open'),
    'stunned': dict(eyes='dot', mouth='flat'),
    'forced': dict(eyes='happy', mouth='flat', brow='sad'),
    'sad': dict(eyes='sad', mouth='frown', brow='sad'),
    'hesitate': dict(eyes='open', mouth='part', brow='worry', wet=True),
    'swallow': dict(eyes='down', mouth='flat', brow='sad', wet=True),
    'wave_smile': dict(eyes='happy', mouth='open', blush=False),
    'cry': dict(eyes='sad', mouth='wobble', brow='sad', tear=True),
    'closed': dict(eyes='closed', mouth='smile'),
    'look_up': dict(eyes='open', mouth='smile', look=(0, -1)),
}


def body(cv, who, cx, top_body, Hh, pose='stand', t=0.0, facing=0, back=False, hold=None):
    """top_body = y where torso starts (just under chin). Returns hand positions."""
    L = LOOK[who]
    Tb = int(round(Hh * (0.78 if not L['coat'] else 1.10)))
    Lg = int(round(Hh * (0.46 if not L['coat'] else 0.80)))
    tw = int(round(Hh * (0.70 if not L['coat'] else 0.80)))
    aw = max(1, int(round(Hh * 0.13)))  # arm width
    phase = math.floor(t * 8) % 2 if pose in ('walk', 'run') else 0
    hands = {}

    y_leg = top_body + Tb
    # legs
    lw = max(1, int(round(Hh * 0.13)))
    lx = [cx - tw // 4 - lw // 2, cx + tw // 4 - lw // 2]
    if pose == 'sit':
        for i, x in enumerate(lx):
            cv.rect(x - 1, y_leg - 1, lw + 2, Lg // 2 + 2, INK)
            cv.rect(x, y_leg, lw, Lg // 2, PAL['skin'] if L['dress'] else L['bottom'])
            cv.rect(x - 1, y_leg + Lg // 2, lw + 2, max(1, Hh // 10), PAL['shoe'] if who != 'man' else INK)
    else:
        for i, x in enumerate(lx):
            off = 0
            if pose in ('walk', 'run'):
                off = (1 if (i + phase) % 2 else -1) * max(1, Hh // 12)
            lift = 0
            if pose in ('walk', 'run') and (i + phase) % 2: lift = max(1, Hh // 14)
            leg_c = PAL['skin'] if L['dress'] else L['bottom']
            cv.rect(x - 1 + off, y_leg - 1, lw + 2, Lg + 1 - lift, INK)
            cv.rect(x + off, y_leg, lw, Lg - 1 - lift, leg_c)
            sh_c = PAL['shoe'] if who in ('girl', 'boy', 'kid', 'boy_w', 'wu', 'wu_ap', 'die', 'he', 'she') else INK
            sw = lw + max(1, Hh // 14)
            cv.rect(x - 1 + off, y_leg + Lg - 1 - lift - max(1, Hh // 12), sw + 2, max(2, Hh // 12) + 1, INK)
            cv.rect(x + off, y_leg + Lg - 1 - lift - max(1, Hh // 12) + 0, sw, max(1, Hh // 12), sh_c)

    # torso
    if L['dress']:
        flare = max(2, int(round(Hh * 0.22)))
        pts = [(cx - tw / 2 + 1, top_body), (cx + tw / 2 - 1, top_body), (cx + tw / 2 + flare, top_body + Tb + 1), (cx - tw / 2 - flare, top_body + Tb + 1)]
        outline_poly(cv, pts, L['top'])
        # dots
        if Hh >= 12:
            sp = max(3, Hh // 4)
            for yy in range(top_body + 2, top_body + Tb, sp):
                for xx in range(int(cx - tw / 2 - flare) + 2 + (yy // sp) % 2 * (sp // 2), int(cx + tw / 2 + flare) - 1, sp):
                    if 0 <= yy < cv.a.shape[0] and 0 <= xx < cv.a.shape[1] and tuple(cv.a[yy, xx]) == L['top']: cv.px(xx, yy, PAL['white'])
        cv.rect(int(cx - tw / 2 - flare) + 1, top_body + Tb - max(1, Hh // 12), tw + 2 * flare - 1, max(1, Hh // 12), L['top_d'])
    else:
        pts = [(cx - tw / 2, top_body), (cx + tw / 2, top_body), (cx + tw / 2 + (1 if L['coat'] else 0), top_body + Tb), (cx - tw / 2 - (1 if L['coat'] else 0), top_body + Tb)]
        outline_poly(cv, pts, L['top'])
        if not L['coat']:
            # pants band
            ph = max(1, int(round(Tb * 0.30)))
            cv.rect(int(cx - tw / 2), top_body + Tb - ph, tw, ph, L['bottom'])
            # collar
            if not back and Hh >= 10:
                cv.px(cx - 1, top_body, L['top_d']); cv.px(cx, top_body + 1, L['top_d']); cv.px(cx + 1, top_body, L['top_d'])
        else:
            if not back:
                cv.vline(int(cx), top_body + 1, top_body + Tb - 1, L['top_d'])
                cv.rect(int(cx - tw / 2) + 1, top_body, max(1, tw // 4), max(1, Hh // 10), PAL['red'] if False else L['top_d'])
        # shading side
        cv.rect(int(cx + tw / 2) - max(1, tw // 6), top_body + 1, max(1, tw // 6), Tb - 1, L['top_d'])

    # arms: pose -> (angle_left, angle_right) in degrees from straight down; positive = outward
    sx = [cx - tw / 2 - aw / 2 + 0.5, cx + tw / 2 + aw / 2 - 0.5]
    sy = top_body + max(1, aw // 2) + 1
    al = int(round(Hh * (0.62 if not L['coat'] else 0.85)))
    A = {
        'stand': (8, 8), 'walk': (18 * (1 if phase else -1), 18 * (-1 if phase else 1)), 'run': (40 * (1 if phase else -1), 40 * (-1 if phase else 1)),
        'jump': (150, 150), 'clap': None, 'wave': (10, 150 + 20 * math.sin(t * 12)), 'hold_r': (8, 55), 'hold_l': (55, 8),
        'sit': (25, 25), 'reach': (8, 115), 'arms_down': (3, 3), 'point_up': (8, 160), 'hand_chest': None,
        'give': (8, 95), 'take': (95, 8), 'cheer': (130, 130),
    }
    if pose in ('clap', 'hand_chest', 'hold_box'):
        ty = sy + al // 2
        gap = (0 if (math.floor(t * 6) % 2 == 0) else max(1, Hh // 8)) if pose == 'clap' else 0
        for k, s in enumerate(sx):
            ex = cx + (-1 if k == 0 else 1) * (gap + aw // 2 + (1 if pose == 'clap' else 0))
            thick_line(cv, s, sy, ex, ty, aw, L['top'], INK)
            hands[k] = (ex, ty)
        for k in (0, 1):
            hx, hy = hands[k]; cv.ellipse(hx, hy, max(1, aw * 0.75), max(1, aw * 0.75), PAL['skin'], INK)
    else:
        ang = A.get(pose, (8, 8))
        for k, s in enumerate(sx):
            a = math.radians(ang[k]) * (-1 if k == 0 else 1)
            ex = s + math.sin(a) * al
            ey = sy + math.cos(a) * al
            thick_line(cv, s, sy, ex, ey, aw, L['top'], INK)
            hands[k] = (ex, ey)
        for k in (0, 1):
            hx, hy = hands[k]
            cv.ellipse(hx, hy, max(1, aw * 0.75), max(1, aw * 0.75), PAL['skin'], INK)
            # red hair tie on girl's right wrist
            if who in ('girl',) and k == 1 and hold != 'no_tie' and Hh >= 10:
                cv.px(hx - 1, hy - aw, PAL['red']); cv.px(hx, hy - aw, PAL['red'])
    return hands, Tb + Lg


def outline_poly(cv, pts, c):
    from PIL import Image, ImageDraw
    from px import W, H
    im = Image.new('1', (W, H), 0)
    ImageDraw.Draw(im).polygon([(int(round(a)), int(round(b))) for a, b in pts], fill=1)
    m = np.array(im)
    cv.a[dilate(m)] = INK
    cv.a[m] = c


def char(cv, who, cx, feet, Hh, pose='stand', expr='normal', t=0.0, facing=0, back=False, blush=None, bob=True, hold=None):
    """Full chibi. feet = y of ground contact. Returns dict with head/hands."""
    cx, feet = int(round(cx)), int(round(feet))
    L = LOOK[who]
    Tb = int(round(Hh * (0.78 if not L['coat'] else 1.10)))
    Lg = int(round(Hh * (0.46 if not L['coat'] else 0.80)))
    lift = 0
    if pose == 'jump':
        lift = int(round(abs(math.sin(t * math.pi * 2.5)) * Hh * 0.9))
    if pose == 'sit': Lg = Lg // 2 + max(1, Hh // 10)
    by = 1 if (bob and pose in ('walk', 'run') and math.floor(t * 8) % 2) else 0
    top_body = feet - Lg - Tb - lift - by
    htop = top_body - Hh + max(1, Hh // 10)
    sb = False
    if L['hair'] == 'long' and not back:
        back_hair(cv, who, cx, htop, Hh); sb = True
    hands, _ = body(cv, who, cx, top_body, Hh, pose, t, facing, back, hold)
    f = head(cv, who, cx, htop, Hh, expr, facing, t, back, blush, skip_back=sb)
    f['hands'] = hands; f['top_body'] = top_body
    return f


def symbol(cv, kind, x, y, t=0.0, s=1):
    """Floating 8bit emotion symbols above heads."""
    bobv = int(round(math.sin(t * 6) * 1))
    y = y + bobv
    if kind == 'heart':
        rows = ['.RR.RR.', 'RRRRRRR', 'RRRRRRR', '.RRRRR.', '..RRR..', '...R...']
        cv.sprite(rows, {'R': PAL['red']}, x - 3, y - 6)
        cv.px(x - 2, y - 5, PAL['pink'])
    elif kind == 'q':
        rows = ['.KKK.', 'K...K', '....K', '..KK.', '..K..', '.....', '..K..']
        cv.sprite(rows, {'K': PAL['white']}, x - 2, y - 7)
    elif kind == 'excl':
        rows = ['KK', 'KK', 'KK', 'KK', '..', 'KK']
        cv.sprite(rows, {'K': PAL['gold']}, x - 1, y - 6)
    elif kind == 'note':
        rows = ['..KK', '..KK', '..K.', '..K.', 'KKK.', 'KKK.']
        cv.sprite(rows, {'K': PAL['gold']}, x - 2, y - 6)
    elif kind == 'sparkle':
        cv.px(x, y - 2, PAL['white']); cv.px(x, y + 2, PAL['white']); cv.px(x - 2, y, PAL['white']); cv.px(x + 2, y, PAL['white'])
        cv.px(x, y, PAL['gold']); cv.px(x, y - 1, PAL['gold']); cv.px(x, y + 1, PAL['gold']); cv.px(x - 1, y, PAL['gold']); cv.px(x + 1, y, PAL['gold'])
    elif kind == 'sweat':
        rows = ['.T.', 'TTT', 'TTT', '.T.']
        cv.sprite(rows, {'T': PAL['tear']}, x - 1, y - 4)
