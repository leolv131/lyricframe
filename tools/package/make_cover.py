"""Covers from a frame of the finished video: 16:9, plus 3:4 and 9:16 for short-video apps.
从成片里挑一帧做封面：横版 16:9，以及短视频平台用的 3:4、9:16。

    python make_cover.py final.mp4 --t 68.0 --title "告白气球" --credit "原唱 · 周杰伦"
    python make_cover.py final.mp4 --t 130 --title "蝴蝶" --credit "原唱 · 陶喆" --style pixel --focus 0.45

--focus   horizontal centre (0–1) of the part to keep in the vertical crops (default 0.5)
--style   pixel (pixel font, hard edges) or flatq (Noto Sans SC Black, soft)
Vertical covers keep the original frame sharp in the middle and fill the rest with a blurred,
darkened copy, so nothing is stretched.
Run it from the repo or anywhere; fonts are bundled.
"""
import argparse
import os
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from lf_common import grab, ROOT  # noqa: E402

FONTS = dict(pixel=os.path.join(ROOT, 'styles', 'pixel8bit', 'fonts', 'unifont.otf'),
             flatq=os.path.join(ROOT, 'styles', 'flatq', 'fonts', 'NotoSansSC-Black.otf'))


def text(img, s, cx, y, size, style, fill=(255, 246, 224), stroke=(26, 20, 38)):
    d = ImageDraw.Draw(img)
    if style == 'pixel':                    # draw small at 16 px multiples, scale up crisp
        k = max(1, round(size / 16))
        f = ImageFont.truetype(FONTS['pixel'], 16)
        w = int(f.getlength(s)) + 8
        tmp = Image.new('RGBA', (w, 26), (0, 0, 0, 0))
        td = ImageDraw.Draw(tmp)
        td.fontmode = '1'
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                td.text((4 + dx, 4 + dy), s, font=f, fill=stroke + (255,))
        td.text((4, 4), s, font=f, fill=fill + (255,))
        tmp = tmp.resize((tmp.width * k, tmp.height * k), Image.NEAREST)
        img.paste(tmp, (int(cx - tmp.width / 2), int(y)), tmp)
    else:
        f = ImageFont.truetype(FONTS['flatq'], size)
        d.text((cx, y), s, font=f, fill=fill, anchor='mt', stroke_width=max(2, size // 14), stroke_fill=stroke)


def vertical(frame, W, H, focus):
    bg = frame.resize((int(frame.width * H / frame.height), H)).filter(ImageFilter.GaussianBlur(28))
    bg = bg.crop(((bg.width - W) // 2, 0, (bg.width - W) // 2 + W, H)).point(lambda v: int(v * 0.55))
    fw = W
    fh = int(frame.height * fw / frame.width)
    # crop around focus so the subject stays big: take a 3:4 window of the frame
    win_w = int(frame.height * 3 / 4)
    x0 = int(min(max(0, focus * frame.width - win_w / 2), frame.width - win_w))
    crop = frame.crop((x0, 0, x0 + win_w, frame.height))
    fh = int(crop.height * W / crop.width)
    crop = crop.resize((W, fh), Image.NEAREST)
    out = bg.copy()
    out.paste(crop, (0, (H - fh) // 2))
    return out, (H - fh) // 2, fh


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('video')
    ap.add_argument('--t', type=float, required=True, help='time of the frame to use (s)')
    ap.add_argument('--title', required=True)
    ap.add_argument('--credit', default='')
    ap.add_argument('--style', choices=['pixel', 'flatq'], default='pixel')
    ap.add_argument('--focus', type=float, default=0.5)
    ap.add_argument('--out', default=None, help='output prefix (default: next to the video)')
    a = ap.parse_args()
    fr = grab(a.video, a.t)
    if fr is None:
        sys.exit('could not read that frame')
    fr = fr.resize((1920, int(fr.height * 1920 / fr.width)), Image.NEAREST if a.style == 'pixel' else Image.LANCZOS)
    pre = a.out or os.path.splitext(a.video)[0]
    h = fr.copy()
    text(h, a.title, 960, 70, 112, a.style)
    if a.credit:
        text(h, a.credit, 960, h.height - 120, 48, a.style)
    h.save(pre + '_cover_16x9.png')
    for name, (W, H) in (('9x16', (1080, 1920)), ('3x4', (1080, 1440))):
        v, top, fh = vertical(fr, W, H, a.focus)
        text(v, a.title, W // 2, max(40, top - 230), 112, a.style)
        if a.credit:
            text(v, a.credit, W // 2, min(H - 110, top + fh + 50), 48, a.style)
        v.save(pre + f'_cover_{name}.png')
    print('->', pre + '_cover_16x9.png / _cover_9x16.png / _cover_3x4.png')


if __name__ == '__main__':
    main()
