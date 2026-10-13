"""Shared helpers for LyricFrame tools: ffmpeg lookup, audio / video decoding.
工具共用：找 ffmpeg、解码音频和视频。只依赖 numpy + ffmpeg。
"""
import json
import os
import shutil
import subprocess
import sys

import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))


def ffmpeg():
    exe = shutil.which('ffmpeg')
    if exe:
        return exe
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        sys.exit('ffmpeg not found. Install it (https://ffmpeg.org) or: pip install imageio-ffmpeg')


def duration(path):
    """Media duration in seconds (parsed from ffmpeg's banner, so ffprobe is not needed)."""
    p = subprocess.run([ffmpeg(), '-hide_banner', '-i', path], capture_output=True, text=True, errors='ignore')
    for line in p.stderr.splitlines():
        line = line.strip()
        if line.startswith('Duration:'):
            hms = line.split(',')[0].split()[1]
            if hms == 'N/A':
                return None
            h, m, s = hms.split(':')
            return int(h) * 3600 + int(m) * 60 + float(s)
    return None


def load_audio(path, sr=22050, start=None, length=None):
    """Decode to mono float32 at `sr`."""
    cmd = [ffmpeg(), '-v', 'error']
    if start is not None:
        cmd += ['-ss', f'{start:.3f}']
    if length is not None:
        cmd += ['-t', f'{length:.3f}']
    cmd += ['-i', path, '-vn', '-ac', '1', '-ar', str(sr), '-f', 'f32le', '-']
    p = subprocess.run(cmd, capture_output=True)
    if p.returncode != 0:
        sys.exit(f'could not decode audio: {path}\n{p.stderr.decode(errors="ignore")[:400]}')
    return np.frombuffer(p.stdout, np.float32).copy()


def read_frames(path, fps=6, w=160, h=90, start=None, length=None):
    """Decode video to an array (n, h, w, 3) uint8 at a low resolution for analysis."""
    cmd = [ffmpeg(), '-v', 'error']
    if start is not None:
        cmd += ['-ss', f'{start:.3f}']
    if length is not None:
        cmd += ['-t', f'{length:.3f}']
    cmd += ['-i', path, '-vf', f'fps={fps},scale={w}:{h}:flags=area', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-']
    p = subprocess.run(cmd, capture_output=True)
    if p.returncode != 0:
        sys.exit(f'could not decode video: {path}\n{p.stderr.decode(errors="ignore")[:400]}')
    return np.frombuffer(p.stdout, np.uint8).reshape(-1, h, w, 3)


def grab(path, t, w=None):
    """One full-resolution frame at time t as a PIL image."""
    from PIL import Image
    import io
    vf = ['-vf', f'scale={w}:-2'] if w else []
    p = subprocess.run([ffmpeg(), '-v', 'error', '-ss', f'{t:.3f}', '-i', path, '-frames:v', '1', *vf,
                        '-f', 'image2pipe', '-vcodec', 'png', '-'], capture_output=True)
    if not p.stdout:
        return None
    return Image.open(io.BytesIO(p.stdout)).convert('RGB')


def video_size(path):
    im = grab(path, 0.0)
    return im.size if im else (1920, 1080)


def read_timing(path):
    with open(path, encoding='utf-8') as f:
        return json.load(f)


def fmt_t(x):
    m = int(x // 60)
    return f'{m}:{x - m * 60:04.1f}'


def cjk_font(size):
    """A bundled CJK font for labels on check sheets."""
    from PIL import ImageFont
    for p in (os.path.join(ROOT, 'styles', 'pixel8bit', 'fonts', 'wqy-zenhei.ttf'),
              os.path.join(ROOT, 'styles', 'flatq', 'fonts', 'NotoSansSC-Bold.otf')):
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()
