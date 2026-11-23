"""scan_video.py - the frame scan of kit/box/scan.py, run on a finished video file instead of PNG frames.
  python3 scan_video.py <video.mp4> <cache_prefix> [procs]
Finds frames that stand out from both neighbours (one render process disagreeing with the others): pure-black pixel count and
one-frame-pop score per block on 108x192 thumbnails. Use a video WITHOUT captions (clean master); caption cards pop by design."""
import sys, os, json, subprocess, numpy as np
mp4, pre = sys.argv[1], sys.argv[2]; P = int(sys.argv[3]) if len(sys.argv) > 3 else 3
W, H = 1080, 1920
if os.path.exists(pre + '_th.npy'): th = np.load(pre + '_th.npy'); bl = np.load(pre + '_bl.npy').astype(float)
else:
    p = subprocess.Popen(['ffmpeg', '-loglevel', 'error', '-i', mp4, '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE, bufsize=W * H * 3)
    th, bl = [], []
    while True:
        buf = p.stdout.read(W * H * 3)
        if len(buf) < W * H * 3: break
        a = np.frombuffer(buf, np.uint8).reshape(H, W, 3)
        bl.append(int((a.sum(axis=2, dtype=np.uint16) < 12).sum())); th.append(a.reshape(192, 10, 108, 10, 3).mean(axis=(1, 3)).astype(np.uint8))
    th = np.stack(th); bl = np.array(bl, dtype=float); np.save(pre + '_th.npy', th); np.save(pre + '_bl.npy', bl)
x = th.astype(np.float32); n = len(x); print('frames analysed:', n)
def blocks(v): return v.reshape(v.shape[0], 8, 24, 6, 18, 3).mean(axis=(2, 4, 5))
a = blocks(np.abs(x[1:-1] - x[:-2])); b = blocks(np.abs(x[2:] - x[1:-1])); c = blocks(np.abs(x[2:] - x[:-2]))
sb = np.minimum(a, b) - c; score = np.zeros(n); score[1:-1] = sb.max(axis=(1, 2)); where = np.zeros(n, int); where[1:-1] = sb.reshape(len(sb), -1).argmax(axis=1)
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
    k = max(ii, key=lambda i: score[i]); print(f'  p{q} f{i0 + 1:05d}-f{i1 + 1:05d} ({i0 / 30:.2f}-{i1 / 30:.2f}s) n={len(ii)} max_score={score[k]:.1f} blk={divmod(int(where[k]), 6)} max_black={int(max(bl[i] for i in ii))}')
json.dump({'suspects': [i + 1 for i in sus], 'n': n}, open(pre + '_list.json', 'w'))
print('score percentiles 50/90/99/max:', [round(float(np.percentile(score[1:-1], q)), 2) for q in (50, 90, 99, 100)], ' black px percentiles 50/99/max:', [int(np.percentile(bl, q)) for q in (50, 99, 100)])
