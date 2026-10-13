"""Put the shared pixel8bit toolkit on sys.path. 把共用的像素工具包加入搜索路径。"""
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
TOOLKIT = os.path.join(ROOT, 'styles', 'pixel8bit')
if TOOLKIT not in sys.path:
    sys.path.insert(1, TOOLKIT)
