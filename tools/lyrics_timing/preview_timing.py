"""A quick check video for step 1: line numbers and beats over the song. 第 1 步核对用的预览。

    python preview_timing.py song.mp3 work/timing.json --out work/timing_check.mp4
    python preview_timing.py song.mp3 work/timing.json --srt work/lyrics.srt   # also burn the lyric text

Shows a big "#n" for each line while it is sung, a progress bar per line and a dot on every beat
(if work/music.json exists). Low resolution (640x360) so it renders in seconds.
"""
import argparse
import json
import os
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from lf_common import ffmpeg, duration, read_timing, cjk_font, ROOT  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('audio')
    ap.add_argument('timing')
    ap.add_argument('--srt', default=None)
    ap.add_argument('--out', default=None)
    ap.add_argument('--fps', type=int, default=10)
    a = ap.parse_args()
    lines = read_timing(a.timing)['lines']
    mj = os.path.join(os.path.dirname(a.timing), 'music.json')
    beats = np.array(json.load(open(mj, encoding='utf-8'))['beats']) if os.path.exists(mj) else np.array([])
    total = duration(a.audio)
    W, H = 640, 360
    big, small = cjk_font(96), cjk_font(18)
    out = a.out or os.path.join(os.path.dirname(a.timing), 'timing_check.mp4')
    vf = []
    if a.srt:
        fd = os.path.join(ROOT, 'styles', 'flatq', 'fonts').replace('\\', '/').replace(':', '\\:')
        sp = os.path.abspath(a.srt).replace('\\', '/').replace(':', '\\:')
        vf = ['-vf', f"subtitles='{sp}':fontsdir='{fd}':force_style='FontName=Noto Sans CJK SC,FontSize=20,MarginV=20'"]
    cmd = [ffmpeg(), '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(a.fps),
           '-i', '-', '-i', a.audio, *vf, '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '26', '-pix_fmt', 'yuv420p',
           '-c:a', 'aac', '-shortest', out]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for i in range(int(total * a.fps)):
        t = i / a.fps
        im = Image.new('RGB', (W, H), (18, 20, 32))
        d = ImageDraw.Draw(im)
        cur = next((l for l in lines if l['start'] <= t < l['end']), None)
        if cur:
            k = (t - cur['start']) / max(0.01, cur['end'] - cur['start'])
            d.text((W // 2, 140), f"#{cur['n']}", font=big, fill=(255, 214, 120), anchor='mm')
            d.rectangle([80, 230, 80 + int(480 * k), 240], fill=(255, 214, 120))
            d.text((W // 2, 262), f"{cur['start']:.2f} – {cur['end']:.2f} s", font=small, fill=(200, 200, 220), anchor='mm')
        else:
            d.text((W // 2, 140), '♪', font=big, fill=(90, 96, 130), anchor='mm')
        if len(beats) and np.abs(beats - t).min() < 0.5 / a.fps + 0.03:
            d.ellipse([W - 40, 20, W - 20, 40], fill=(255, 120, 140))
        d.text((16, 16), f'{int(t // 60)}:{t % 60:04.1f}', font=small, fill=(150, 150, 170))
        p.stdin.write(im.tobytes())
    p.stdin.close()
    p.wait()
    print('->', out)


if __name__ == '__main__':
    main()
