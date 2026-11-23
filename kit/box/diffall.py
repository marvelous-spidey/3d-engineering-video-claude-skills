"""diffall.py - compare two renders of the same frames (e.g. persistent vs non-persistent): which frames differ, and by which process.
  python diffall.py <dir_a> <dir_b> <first> <last> [cache.json]"""
import sys, os, json, numpy as np
from PIL import Image
da, db, f0, f1 = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]); cache = sys.argv[5] if len(sys.argv) > 5 else None
res = json.load(open(cache)) if cache and os.path.exists(cache) else {}
for f in range(f0, f1 + 1):
    if str(f) in res: continue
    pa, pb = (os.path.join(d, f'f_{f:05d}.png') for d in (da, db))
    if not (os.path.exists(pa) and os.path.exists(pb)): continue
    try: a = np.asarray(Image.open(pa).convert('RGB').reduce(4)).astype(np.float32); b = np.asarray(Image.open(pb).convert('RGB').reduce(4)).astype(np.float32)
    except Exception as ex: continue
    dd = np.abs(a - b).mean(axis=2); res[str(f)] = [round(float(dd.mean()), 3), round(float(dd.reshape(16, 30, 9, 30).mean(axis=(1, 3)).max()), 2)]
if cache: json.dump(res, open(cache, 'w'))
fs = sorted(int(k) for k in res); TH = float(os.environ.get('DIFF', '1.0')); bad = [f for f in fs if res[str(f)][1] > TH]
print(f'compared {len(fs)} frames ({fs[0]}-{fs[-1]}); differ (block max > {TH}): {len(bad)}  by process:', {q: sum(1 for f in bad if (f - 1) % 3 == q) for q in range(3)})
runs = []
for f in bad:
    q = (f - 1) % 3
    if runs and runs[-1][0] == q and f - runs[-1][2] <= 9: runs[-1][2] = f; runs[-1][3] += 1
    else: runs.append([q, f, f, 1])
for q, a, b, n in runs: print(f'  p{q} f{a:05d}-f{b:05d} ({(a - 1) / 30:.2f}-{(b - 1) / 30:.2f}s) n={n} max_block={max(res[str(f)][1] for f in range(a, b + 1) if str(f) in res and (f - 1) % 3 == q):.1f}')
good = [res[str(f)][1] for f in fs if f not in set(bad)]
if good: print('frames that agree: block-max percentiles 50/90/99/max:', [round(float(np.percentile(good, q)), 2) for q in (50, 90, 99, 100)])
