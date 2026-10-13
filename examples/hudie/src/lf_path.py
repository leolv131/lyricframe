"""Find the LyricFrame repo and put the style toolkit and tools on sys.path.
找到 LyricFrame 仓库，把画风工具包和 tools 加入搜索路径。

Works wherever the project lives (inside the repo or anywhere else, as long as the repo can be
found by walking up from here, or via the LYRICFRAME_HOME environment variable).
The style comes from STYLE below, else project.json "style", else pixel8bit.
"""
import json
import os
import sys

STYLE = 'pixel8bit'

HERE = os.path.dirname(os.path.abspath(__file__))


def _find_root():
    env = os.environ.get('LYRICFRAME_HOME')
    if env and os.path.isdir(os.path.join(env, 'styles')):
        return env
    d = HERE
    for _ in range(8):
        if os.path.isdir(os.path.join(d, 'styles')) and os.path.isdir(os.path.join(d, 'tools')):
            return d
        d = os.path.dirname(d)
    raise SystemExit('LyricFrame repo not found: set LYRICFRAME_HOME=/path/to/lyricframe')


def _style():
    if STYLE:
        return STYLE
    p = os.path.join(os.path.dirname(HERE), 'project.json')
    if os.path.exists(p):
        with open(p, encoding='utf-8') as f:
            return json.load(f).get('style', 'pixel8bit')
    return 'pixel8bit'


ROOT = _find_root()
STYLE = _style()
os.environ.setdefault('LF_STYLE', STYLE)
for p in (os.path.join(ROOT, 'tools'), os.path.join(ROOT, 'styles', STYLE), HERE):
    if p in sys.path:
        sys.path.remove(p)
    sys.path.insert(0, p)
