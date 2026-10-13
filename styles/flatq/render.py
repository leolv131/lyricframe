"""Render [(start, end, shot_fn)] to MP4. shot_fn(t, dur) -> Frame.
扁平 Q 版渲染：每帧只由 t 决定（确定性渲染）。

Options: song (None = silent), scale (1.0 = 1920x1080, 0.667 = 720p preview),
fade_in / fade_out, vcodec ('libx264' default; or env LF_VCODEC=h264_nvenc).
"""
import os
import shutil
import subprocess

import numpy as np

from fq import W, H, clamp

FPS = 30


def _ffmpeg():
    exe = shutil.which('ffmpeg')
    if exe:
        return exe
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        raise SystemExit('ffmpeg not found. Install it (https://ffmpeg.org) or run: pip install imageio-ffmpeg')


def render(timeline, t0, t1, out, song=None, fade_in=0.0, fade_out=0.0, crf=18, scale=1.0, vcodec=None, fps=FPS):
    vcodec = vcodec or os.environ.get('LF_VCODEC', 'libx264')
    w, h = int(W * scale) // 2 * 2, int(H * scale) // 2 * 2
    cmd = [_ffmpeg(), '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(fps), '-i', '-']
    if song:
        cmd += ['-ss', f'{t0:.3f}', '-t', f'{t1 - t0:.3f}', '-i', song]
        af = []
        if fade_in: af.append(f'afade=t=in:st=0:d={fade_in}')
        if fade_out: af.append(f'afade=t=out:st={max(0.0, t1 - t0 - fade_out):.3f}:d={fade_out}')
        if af: cmd += ['-af', ','.join(af)]
    if scale != 1.0: cmd += ['-vf', f'scale={w}:{h}']
    if vcodec == 'libx264':
        cmd += ['-c:v', 'libx264', '-crf', str(crf), '-preset', 'medium']
    else:
        cmd += ['-c:v', vcodec, '-b:v', '12M']
    cmd += ['-pix_fmt', 'yuv420p']
    if song: cmd += ['-c:a', 'aac', '-b:a', '192k', '-shortest']
    cmd += ['-movflags', '+faststart', out]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    n = int(round((t1 - t0) * fps))
    for i in range(n):
        T = t0 + i / fps
        arr = None
        for (a, b, fn) in timeline:
            if a <= T < b:
                arr = fn(T - a, b - a).array(); break
        if arr is None: arr = np.zeros((H, W, 3), np.uint8)
        k = 1.0
        if fade_in and T - t0 < fade_in: k = (T - t0) / fade_in
        if fade_out and t1 - T < fade_out: k = min(k, (t1 - T) / fade_out)
        if k < 1: arr = (arr * clamp(k)).astype(np.uint8)
        p.stdin.write(arr.tobytes())
    p.stdin.close()
    if p.wait() != 0:
        raise SystemExit(f'ffmpeg failed while writing {out}')
    return out
