"""scan.py - frame QA for multi-process renders: finds frames where one render process disagrees with its neighbours.
  python scan.py <frames_dir> <cache_prefix> [last_frame] [procs]      (incremental; run again as frames arrive)
Per frame: (1) count of pure-black pixels (R+G+B < 12): a shading failure shows up as black;
           (2) one-frame-pop score per block = min(|F[f]-F[f-1]|, |F[f+1]-F[f]|) - |F[f+1]-F[f-1]| on 108x192 thumbnails.
A frame is a suspect when it stands out from BOTH neighbours (which other processes rendered); fast camera moves raise the score of
every frame alike and are not flagged. Suspects + an evenly spread control sample go to <prefix>_list.txt for a clean re-render
(KIT_PERSIST=0, 'list' mode); compare.py then tells real glitches from false alarms."""
import sys, os, json, numpy as np
from PIL import Image
d, pre = sys.argv[1], sys.argv[2]; N = int(sys.argv[3]) if len(sys.argv) > 3 else 2052; P = int(sys.argv[4]) if len(sys.argv) > 4 else 3
W, H = 108, 192
th = np.load(pre + '_th.npy') if os.path.exists(pre + '_th.npy') else np.zeros((0, H, W, 3), np.uint8)
bl = list(np.load(pre + '_bl.npy')) if os.path.exists(pre + '_bl.npy') else []
k = len(th); new = []
while k < N:
    p = os.path.join(d, f'f_{k + 1:05d}.png')
    if not os.path.exists(p) or (k + 1 < N and not all(os.path.exists(os.path.join(d, f'f_{j:05d}.png')) for j in range(k + 2, min(N, k + 7) + 1))): break
    try: im = Image.open(p).convert('RGB'); a = np.asarray(im)
    except Exception as ex: print('unreadable', p, ex); break
    bl.append(int((a.sum(axis=2, dtype=np.uint16) < 12).sum())); new.append(np.asarray(im.reduce(10))); k += 1
if new: th = np.concatenate([th, np.stack(new)]); np.save(pre + '_th.npy', th); np.save(pre + '_bl.npy', np.array(bl))
x = th.astype(np.float32); n = len(x); bl = np.array(bl, dtype=float); print('frames analysed:', n)
if n < 3: sys.exit()
def blocks(v): return v.reshape(v.shape[0], 8, 24, 6, 18, 3).mean(axis=(2, 4, 5))
a = blocks(np.abs(x[1:-1] - x[:-2])); b = blocks(np.abs(x[2:] - x[1:-1])); c = blocks(np.abs(x[2:] - x[:-2]))
sb = np.minimum(a, b) - c; score = np.zeros(n); score[1:-1] = sb.max(axis=(1, 2))
THR = float(os.environ.get('THR', '1.2')); sus = []
for i in range(1, n - 1):
    ns = max(score[i - 1], score[i + 1], 0.0); nb = max(bl[i - 1], bl[i + 1])
    if (score[i] > THR and score[i] > 1.8 * ns + 0.3) or (bl[i] > 150 and bl[i] > 2 * nb + 150): sus.append(i)
print(f'suspects: {len(sus)} of {n}  by process:', {q: sum(1 for i in sus if i % P == q) for q in range(P)})
runs = []
for i in sus:
    if runs and runs[-1][0] == i % P and i - runs[-1][2] <= P * 3: runs[-1][2] = i; runs[-1][3].append(i)
    else: runs.append([i % P, i, i, [i]])
for q, i0, i1, ii in runs:
    if len(ii) > 1 or score[ii[0]] > 6 or bl[ii[0]] > 2000: print(f'  p{q} f{i0 + 1:05d}-f{i1 + 1:05d} ({i0 / 30:.2f}-{i1 / 30:.2f}s) n={len(ii)} max_score={max(score[i] for i in ii):.1f} max_black={int(max(bl[i] for i in ii))}')
ctl = [i for i in range(15, n, 31) if i not in sus]
json.dump({'suspects': [i + 1 for i in sus], 'control': [i + 1 for i in ctl], 'n': n}, open(pre + '_list.json', 'w'))
open(pre + '_list.txt', 'w').write(' '.join(str(i + 1) for i in sorted(sus + ctl)))
print('control sample:', len(ctl), ' list ->', pre + '_list.txt', len(sus) + len(ctl), 'frames')
