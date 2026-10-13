"""Package the repository as an Agent Skill zip (Claude app "Upload skill", or Codex ~/.agents/skills).
把仓库打包成 skill zip：Claude 应用里上传，或解压到 Codex 的 ~/.agents/skills。

    python scripts/build_skill.py            # -> dist/lyricframe-skill.zip

The zip holds one folder `lyricframe/` with SKILL.md at its root plus everything the workflow needs.
"""
import os
import zipfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
INCLUDE = ['AGENTS.md', 'LICENSE', 'requirements.txt', 'docs', 'templates', 'styles', 'tools', 'examples', 'demo']
SKIP_DIRS = {'__pycache__', '.git', 'dist', 'media', 'projects', 'work', 'out'}
SKIP_EXT = {'.pyc', '.mp4', '.mp3', '.wav', '.gif', '.lrc'}


def main():
    os.makedirs(os.path.join(ROOT, 'dist'), exist_ok=True)
    out = os.path.join(ROOT, 'dist', 'lyricframe-skill.zip')
    n = 0
    with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        z.write(os.path.join(ROOT, 'skill', 'SKILL.md'), 'lyricframe/SKILL.md')
        for item in INCLUDE:
            p = os.path.join(ROOT, item)
            if os.path.isfile(p):
                z.write(p, f'lyricframe/{item}'); n += 1
                continue
            for dp, dns, fns in os.walk(p):
                dns[:] = [d for d in dns if d not in SKIP_DIRS]
                for fn in fns:
                    if os.path.splitext(fn)[1].lower() in SKIP_EXT:
                        continue
                    fp = os.path.join(dp, fn)
                    z.write(fp, 'lyricframe/' + os.path.relpath(fp, ROOT).replace(os.sep, '/')); n += 1
    print(f'{n + 1} files -> {out} ({os.path.getsize(out) / 1e6:.1f} MB)')


if __name__ == '__main__':
    main()
