"""compare.py - compare clean re-renders with the original frames; real glitches differ, false alarms and controls do not.
  python compare.py <frames_dir> <fix_dir> <list.json> [apply]     apply: copy the differing re-renders over the originals (originals kept in <fix_dir>/orig)"""
import sys, os, json, shutil, numpy as np
from PIL import Image
fr, fx, lj = sys.argv[1], sys.argv[2], json.load(open(sys.argv[3])); apply = len(sys.argv) > 4 and sys.argv[4] == 'apply'
TH = float(os.environ.get('DIFF', '1.0')); rows = []
for kind in ('suspects', 'control'):
    for f in lj[kind]:
        p = os.path.join(fx, f'f_{f:05d}.png')
        if not os.path.exists(p): continue
        a = np.asarray(Image.open(os.path.join(fr, f'f_{f:05d}.png')).convert('RGB').reduce(4)).astype(np.float32); b = np.asarray(Image.open(p).convert('RGB').reduce(4)).astype(np.float32)
        dd = np.abs(a - b).mean(axis=2); blk = dd.reshape(16, 30, 9, 30).mean(axis=(1, 3)); rows.append((kind, f, float(dd.mean()), float(blk.max())))
for kind in ('suspects', 'control'):
    r = [x for x in rows if x[0] == kind]; real = [x for x in r if x[3] > TH]
    print(f'{kind}: {len(r)} compared, {len(real)} differ (largest block diff > {TH})')
    if kind == 'control' or len(real) < 60:
        for x in real: print(f'   f{x[1]:05d} p{(x[1] - 1) % 3} t={(x[1] - 1) / 30:.2f}s mean={x[2]:.2f} block_max={x[3]:.1f}')
    if r: print('   block_max percentiles 50/90/max:', [round(float(np.percentile([x[3] for x in r], q)), 2) for q in (50, 90, 100)])
real = sorted(x[1] for x in rows if x[3] > TH); json.dump(real, open(os.path.join(fx, 'real.json'), 'w')); print('real glitch frames:', len(real), ' by process:', {q: sum(1 for f in real if (f - 1) % 3 == q) for q in range(3)})
if apply:
    os.makedirs(os.path.join(fx, 'orig'), exist_ok=True)
    for f in real:
        n = f'f_{f:05d}.png'; shutil.copy2(os.path.join(fr, n), os.path.join(fx, 'orig', n)); shutil.copy2(os.path.join(fx, n), os.path.join(fr, n))
    print('applied', len(real), 'frames')
