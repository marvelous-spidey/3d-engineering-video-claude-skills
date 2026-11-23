"""trip_png.py - suspects next to their neighbours, from PNG frames: python trip_png.py <frames_dir> <cache_prefix> <out.jpg> f1 f2 ...
The block with the highest one-frame-pop score is found from the scan cache; crops are 360 x 400 px at full resolution."""
import sys, os, numpy as np
from PIL import Image, ImageDraw
d, pre, out, fs = sys.argv[1], sys.argv[2], sys.argv[3], [int(v) for v in sys.argv[4:]]
x = np.load(pre + '_th.npy').astype(np.float32)
def blocks(v): return v.reshape(v.shape[0], 8, 24, 6, 18, 3).mean(axis=(2, 4, 5))
cw, ch = 360, 400; sh = Image.new('RGB', (cw * 3 + 8, (ch + 4) * len(fs)), (16, 16, 16)); dr = ImageDraw.Draw(sh)
for k, f in enumerate(fs):
    i = f - 1; a = blocks(np.abs(x[i:i + 1] - x[i - 1:i]))[0]; b = blocks(np.abs(x[i + 1:i + 2] - x[i:i + 1]))[0]; c = blocks(np.abs(x[i + 1:i + 2] - x[i - 1:i]))[0]
    s = np.minimum(a, b) - c; r, q = np.unravel_index(np.argmax(s), s.shape); print(f'f{f} p{(f - 1) % 3} score {s.max():.1f} block {r},{q}  a={a[r, q]:.1f} b={b[r, q]:.1f} c={c[r, q]:.1f}')
    x0 = min(max(q * 180 + 90 - cw // 2, 0), 1080 - cw); y0 = min(max(r * 240 + 120 - ch // 2, 0), 1920 - ch)
    for j, g in enumerate((f - 1, f, f + 1)):
        sh.paste(Image.open(os.path.join(d, f'f_{g:05d}.png')).convert('RGB').crop((x0, y0, x0 + cw, y0 + ch)), (j * (cw + 4), k * (ch + 4))); dr.text((j * (cw + 4) + 4, k * (ch + 4) + 2), f'f{g} p{(g - 1) % 3}', fill=(255, 235, 60))
sh.save(out, quality=85); print(out, sh.size, os.path.getsize(out))
