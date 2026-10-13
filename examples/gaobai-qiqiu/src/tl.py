"""《告白气球》时间轴：shots.S + 各章镜头函数；统一叠"告白进度" HUD。"""
import importlib
import shots
from px import Canvas

REG = {}
NO_HUD = {1, 56}


def shot(no):
    def deco(fn):
        REG[no] = fn
        return fn
    return deco


_loaded = False


def load():
    global _loaded
    if _loaded: return
    for m in ('g1', 'g2', 'g3', 'g4', 'g5'):
        try: importlib.import_module(m)
        except ModuleNotFoundError as e:
            if e.name != m: raise
    _loaded = True


_fin = None


def finalize():
    global _fin
    load()
    if _fin is None:
        S = shots.S; out = []
        for i, s in enumerate(S):
            e = S[i + 1][1] if i + 1 < len(S) else shots.END
            out.append(dict(no=f'{s[0]:02d}', id=s[0], start=s[1], end=e, dur=e - s[1], note=s[4], fn=REG.get(s[0])))
        _fin = out
    return _fin


def run(s, t):
    from gbl import hud
    cv = s['fn'](t, s['dur']) if s['fn'] else Canvas()
    if s['id'] not in NO_HUD: hud(cv, s['start'] + t)
    return cv


def timeline():
    return [(s['start'], s['end'], (lambda s: (lambda t: run(s, t)))(s)) for s in finalize()]


def frame_at(T):
    for s in finalize():
        if s['start'] <= T < s['end']: return run(s, T - s['start'])
    return Canvas()
