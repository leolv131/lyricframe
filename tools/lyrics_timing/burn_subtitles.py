"""Burn lyric subtitles into a finished video (the text comes from your own .lrc → lyrics.srt).
给成片烧歌词字幕。字幕文字来自你自己的 .lrc（lyrics_timing 生成的 lyrics.srt），AI 不经手。

    python burn_subtitles.py final.mp4 work/lyrics.srt --style pixel
    python burn_subtitles.py final.mp4 work/lyrics.srt --style flatq --out final_lyrics.mp4

Styles follow the art style:
  pixel  Unifont pixel font + half-transparent box (BorderStyle=3)
  flatq  Noto Sans SC Bold + dark outline
Vertical videos (height > width) get a higher bottom margin automatically.
Set LF_VCODEC=h264_nvenc (NVIDIA) or h264_videotoolbox (Mac) to encode faster.
"""
import argparse
import os
import subprocess
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from lf_common import ffmpeg, video_size, ROOT  # noqa: E402

STYLES = {
    'pixel': dict(fontsdir=os.path.join(ROOT, 'styles', 'pixel8bit', 'fonts'),
                  style='FontName=Unifont,FontSize={fs},PrimaryColour=&H00F0F6FF,BackColour=&H80201010,'
                        'OutlineColour=&H80201010,BorderStyle=3,Outline=3,Shadow=0,Alignment=2,MarginV={mv}'),
    'flatq': dict(fontsdir=os.path.join(ROOT, 'styles', 'flatq', 'fonts'),
                  style='FontName=Noto Sans CJK SC,Bold=1,FontSize={fs},PrimaryColour=&H00FFFFFF,'
                        'OutlineColour=&H002E1D2B,BorderStyle=1,Outline=1.8,Shadow=0,Alignment=2,MarginV={mv}'),
}


def shifted_srt(path, delta):
    """Copy of an .srt with every time moved by delta seconds (lines before 0 are dropped)."""
    import re
    import tempfile
    def p(t):
        h, m, r = t.split(':'); s, ms = r.split(',')
        return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000
    def f(x):
        x = max(0.0, x); h, m = int(x // 3600), int(x % 3600 // 60); s = x % 60
        return f'{h:02d}:{m:02d}:{int(s):02d},{min(999, int(round((s - int(s)) * 1000))):03d}'
    blocks = re.split(r'\n\s*\n', open(path, encoding='utf-8-sig').read().replace('\r', '').strip())
    out = []
    for b in blocks:
        ls = b.split('\n')
        if len(ls) < 3 or '-->' not in ls[1]:
            continue
        a_, b_ = [p(x.strip()) + delta for x in ls[1].split('-->')]
        if b_ <= 0:
            continue
        out.append(f'{len(out) + 1}\n{f(a_)} --> {f(b_)}\n' + '\n'.join(ls[2:]))
    fd, tmp = tempfile.mkstemp(suffix='.srt')
    with os.fdopen(fd, 'w', encoding='utf-8') as fh:
        fh.write('\n\n'.join(out) + '\n')
    return tmp


def esc(p):
    return os.path.abspath(p).replace('\\', '/').replace(':', '\\:').replace("'", r"\'")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('video')
    ap.add_argument('srt')
    ap.add_argument('--style', choices=list(STYLES), default='pixel')
    ap.add_argument('--out', default=None)
    ap.add_argument('--offset', type=float, default=0.0,
                    help='song time at the first frame of the video (for clips that do not start at 0)')
    a = ap.parse_args()
    srt = a.srt
    if a.offset:
        srt = shifted_srt(a.srt, -a.offset)
    w, h = video_size(a.video)
    vertical = h > w
    # libass sizes are relative to a 288-line script height by default
    fs, mv = (13, 34) if vertical else (16, 14)
    st = STYLES[a.style]
    style = st['style'].format(fs=fs, mv=mv)
    out = a.out or os.path.splitext(a.video)[0] + '_lyrics.mp4'
    vcodec = os.environ.get('LF_VCODEC', 'libx264')
    vargs = ['-c:v', 'libx264', '-crf', '18', '-preset', 'medium'] if vcodec == 'libx264' else ['-c:v', vcodec, '-b:v', '12M']
    vf = f"subtitles='{esc(srt)}':fontsdir='{esc(st['fontsdir'])}':force_style='{style}'"
    cmd = [ffmpeg(), '-v', 'error', '-y', '-i', a.video, '-vf', vf, *vargs, '-pix_fmt', 'yuv420p',
           '-c:a', 'copy', '-movflags', '+faststart', out]
    r = subprocess.run(cmd)
    if r.returncode:
        sys.exit('ffmpeg failed')
    print('->', out)


if __name__ == '__main__':
    main()
