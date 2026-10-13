"""Subtitle-safe check: for every sung line, draw the real subtitle box on the frames at the start,
middle and end of the line, so you can see whether faces, hands or the key prop get covered.
字幕遮挡检查：按每句的真实字幕框，在开头 / 中间 / 结尾 3 帧上画出来，看人脸、手、信物有没有被挡。

    python subtitle_safe.py final.mp4 --timing work/timing.json
    python subtitle_safe.py final.mp4 --timing work/timing.json --offset 60   # video starts at song 60 s

Needs only times and character counts from timing.json — no lyric text.
If something important is covered: move it up, or lift the whole scene by 100–150 px (1080p).
"""
import argparse
import os
import sys

from PIL import Image, ImageDraw

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from lf_common import duration, grab, read_timing, cjk_font, fmt_t  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('video')
    ap.add_argument('--timing', required=True)
    ap.add_argument('--offset', type=float, default=0.0, help='song time at the first frame of the video')
    ap.add_argument('--per-sheet', type=int, default=8, help='lines per output image')
    a = ap.parse_args()
    lines = read_timing(a.timing)['lines']
    dur = duration(a.video)
    lines = [l for l in lines if l['end'] > a.offset and l['start'] < a.offset + dur]
    W0, H0 = grab(a.video, 0).size
    vertical = H0 > W0
    tw = 400
    sc = tw / W0
    th = int(H0 * sc)
    zone = (300 if vertical else 170) * H0 / (1920 if vertical else 1080)
    outs = []
    for k in range(0, len(lines), a.per_sheet):
        chunk = lines[k:k + a.per_sheet]
        S = Image.new('RGB', (3 * tw, len(chunk) * (th + 26)), (16, 16, 20))
        d = ImageDraw.Draw(S)
        for r, l in enumerate(chunk):
            y0 = r * (th + 26)
            d.text((6, y0 + 4), f"#{l['n']}  {fmt_t(l['start'])}–{fmt_t(l['end'])}  ({l['chars']} 字)",
                   font=cjk_font(16), fill=(255, 220, 140))
            for c, frac in enumerate((0.1, 0.5, 0.9)):
                t = l['start'] + (l['end'] - l['start']) * frac - a.offset
                im = grab(a.video, min(max(0.0, t), dur - 0.05), w=tw)
                if not im:
                    continue
                im = im.resize((tw, th)).convert('RGBA')
                ov = Image.new('RGBA', im.size, (0, 0, 0, 0))
                od = ImageDraw.Draw(ov)
                fs = (0.045 if not vertical else 0.035) * H0          # approximate subtitle glyph size
                bw = min(W0 * 0.92, l['chars'] * fs * 1.05 + fs) * sc
                bh = fs * 1.6 * sc
                cy = H0 - zone * 0.45
                od.rectangle([tw / 2 - bw / 2, cy * sc - bh / 2, tw / 2 + bw / 2, cy * sc + bh / 2],
                             fill=(255, 40, 80, 110), outline=(255, 60, 90, 255), width=2)
                od.line([0, (H0 - zone) * sc, tw, (H0 - zone) * sc], fill=(255, 220, 0, 200), width=1)
                im = Image.alpha_composite(im, ov).convert('RGB')
                S.paste(im, (c * tw, y0 + 24))
        out = os.path.splitext(a.video)[0] + f'_subsafe_{k // a.per_sheet + 1:02d}.jpg'
        S.save(out, quality=85)
        outs.append(out)
    for o in outs:
        print('->', o)
    print('red box = subtitle; yellow line = top of the subtitle-safe zone')


if __name__ == '__main__':
    main()
