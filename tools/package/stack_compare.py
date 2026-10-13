"""Stack two versions of the same MV top / bottom (1920x2160) with one audio track.
两个版本上下拼接对比（1920×2160），只保留一条音轨。

    python stack_compare.py top.mp4 bottom.mp4 compare.mp4
    python stack_compare.py top.mp4 bottom.mp4 compare.mp4 --labels "Claude" "GPT" --audio top

Both inputs are scaled to 1920x1080 (letterboxed if needed); the shorter one decides the length.
Labels are drawn in the top-left corner of each half (optional).
"""
import argparse
import os
import subprocess
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from lf_common import ffmpeg, ROOT  # noqa: E402

FONT = os.path.join(ROOT, 'styles', 'flatq', 'fonts', 'NotoSansSC-Bold.otf')


def esc(p):
    return p.replace('\\', '/').replace(':', '\\:')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('top')
    ap.add_argument('bottom')
    ap.add_argument('out')
    ap.add_argument('--labels', nargs=2, default=None)
    ap.add_argument('--audio', choices=['top', 'bottom'], default='top')
    a = ap.parse_args()
    fit = 'scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=30'
    parts = [f'[0:v]{fit}[a]', f'[1:v]{fit}[b]']
    if a.labels:
        for tag, text in (('a', a.labels[0]), ('b', a.labels[1])):
            t = text.replace("'", r"\'").replace(':', r'\:')
            parts.append(f"[{tag}]drawtext=fontfile='{esc(FONT)}':text='{t}':x=36:y=30:fontsize=46:"
                         f"fontcolor=white:borderw=4:bordercolor=black@0.8[{tag}2]")
        parts.append('[a2][b2]vstack=inputs=2[v]')
    else:
        parts.append('[a][b]vstack=inputs=2[v]')
    vcodec = os.environ.get('LF_VCODEC', 'libx264')
    vargs = ['-c:v', 'libx264', '-crf', '20', '-preset', 'medium'] if vcodec == 'libx264' else ['-c:v', vcodec, '-b:v', '16M']
    cmd = [ffmpeg(), '-v', 'error', '-y', '-i', a.top, '-i', a.bottom, '-filter_complex', ';'.join(parts),
           '-map', '[v]', '-map', f"{0 if a.audio == 'top' else 1}:a?", *vargs, '-pix_fmt', 'yuv420p',
           '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', a.out]
    if subprocess.run(cmd).returncode:
        sys.exit('ffmpeg failed')
    print('->', a.out)


if __name__ == '__main__':
    main()
