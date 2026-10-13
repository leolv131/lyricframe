"""Render a timeline to MP4. 把时间轴渲染成 MP4。

    render([(start, end, shot_fn), ...], t0, t1, 'out.mp4', song='song.mp3')

shot_fn(t) returns a Canvas; t is seconds since the shot started. Every frame is
decided only by t, so any range can be re-rendered and the result is identical.
每帧只由 t 决定（确定性渲染），任意片段都能单独重渲。

Options
  song      audio file to mux (the same time range is cut from it). None = silent.
  scale     6 = 1920x1080 (default), 4 = 1280x720 preview, 1 = raw 320x180.
  srt       burn an .srt in (preview only — final videos stay clean).
  fade_out  seconds of fade to black (and audio fade) at the end.
  vcodec    'libx264' (default, works everywhere) or 'h264_nvenc' / 'h264_videotoolbox'.
            Can also be set with the environment variable LF_VCODEC.
"""
import os
import shutil
import subprocess

import numpy as np

from px import Canvas, W, H, SCALE, clamp, FONT_DIR

FPS = 30


def _ffmpeg():
    exe = shutil.which('ffmpeg')
    if exe:
        return exe
    try:                                   # pip install imageio-ffmpeg
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        raise SystemExit('ffmpeg not found. Install it (https://ffmpeg.org) or run: pip install imageio-ffmpeg')


def _sub_filter(srt):
    p = os.path.abspath(srt).replace('\\', '/').replace(':', '\\:')
    fd = FONT_DIR.replace('\\', '/').replace(':', '\\:')
    return (f"subtitles='{p}':fontsdir='{fd}':force_style='FontName=WenQuanYi Zen Hei,"
            f"FontSize=18,Alignment=2,MarginV=20,Outline=2'")


def render(timeline, t0, t1, out, audio=True, scale=SCALE, srt=None, fade_out=None, song=None,
           vcodec=None, crf=18, fps=FPS):
    vcodec = vcodec or os.environ.get('LF_VCODEC', 'libx264')
    audio = bool(audio and song)
    w, h = W * scale, H * scale
    cmd = [_ffmpeg(), '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24',
           '-s', f'{w}x{h}', '-r', str(fps), '-i', '-']
    if audio:
        cmd += ['-ss', f'{t0:.3f}', '-t', f'{t1 - t0:.3f}', '-i', song]
        if fade_out:
            cmd += ['-af', f'afade=t=out:st={max(0.0, t1 - t0 - fade_out):.3f}:d={fade_out}']
    if srt:
        cmd += ['-vf', _sub_filter(srt)]
    if vcodec == 'libx264':
        cmd += ['-c:v', 'libx264', '-crf', str(crf), '-preset', 'medium', '-tune', 'animation']
    else:
        cmd += ['-c:v', vcodec, '-b:v', '12M']
    cmd += ['-pix_fmt', 'yuv420p']
    if audio:
        cmd += ['-c:a', 'aac', '-b:a', '192k', '-shortest']
    cmd += ['-movflags', '+faststart', out]

    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    n = int(round((t1 - t0) * fps))
    for i in range(n):
        T = t0 + i / fps
        cv = None
        for (a, b, fn) in timeline:
            if a <= T < b:
                cv = fn(T - a)
                break
        if cv is None:
            cv = Canvas()
        if fade_out and T > t1 - fade_out:
            cv.darken(clamp((t1 - T) / fade_out))
        frame = cv.a if scale == 1 else np.repeat(np.repeat(cv.a, scale, 0), scale, 1)
        p.stdin.write(frame.tobytes())
    p.stdin.close()
    if p.wait() != 0:
        raise SystemExit(f'ffmpeg failed while writing {out}')
    return out


def frame_at(timeline, T):
    """Return the Canvas at absolute time T (for stills and checks). 取某一时刻的画面。"""
    for (a, b, fn) in timeline:
        if a <= T < b:
            return fn(T - a)
    return Canvas()
