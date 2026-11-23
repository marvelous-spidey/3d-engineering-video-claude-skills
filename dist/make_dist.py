"""make_dist.py - build one ZIP per skill for upload to Claude (Customize > Skills > + > Create skill > Upload a skill).
Run from anywhere:  python3 dist/make_dist.py
Each ZIP holds the skill folder as its root (<skill-name>/SKILL.md), which is the layout the upload expects."""
import os, zipfile
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for name in sorted(os.listdir(os.path.join(ROOT, 'skills'))):
    src = os.path.join(ROOT, 'skills', name)
    if not os.path.isfile(os.path.join(src, 'SKILL.md')): continue
    out = os.path.join(ROOT, 'dist', name + '.zip')
    with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as z:
        for base, dirs, files in os.walk(src):
            dirs.sort()
            for f in sorted(files):
                p = os.path.join(base, f); info = zipfile.ZipInfo(name + '/' + os.path.relpath(p, src).replace(os.sep, '/'), date_time=(2026, 1, 1, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED; info.external_attr = 0o644 << 16
                z.writestr(info, open(p, 'rb').read())
    print(os.path.relpath(out, ROOT), os.path.getsize(out), 'bytes')
