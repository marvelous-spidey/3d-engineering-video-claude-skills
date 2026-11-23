"""trip.py - show suspect frames next to their neighbours: python3 trip.py <video.mp4> <out.jpg> f:row:col ...  (row/col = block from the scan, 8 x 6 grid)"""
import sys, subprocess, numpy as np
from PIL import Image, ImageDraw
mp4, out, items = sys.argv[1], sys.argv[2], [tuple(int(v) for v in a.split(':')) for a in sys.argv[3:]]
W, H = 1080, 1920
def frame(f):
    raw = subprocess.run(['ffmpeg', '-loglevel', 'error', '-ss', f'{max((f - 1) / 30 - 0.012, 0):.4f}', '-i', mp4, '-frames:v', '1', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], capture_output=True).stdout   # seek 12 ms BEFORE the frame: ffmpeg returns the first frame at or after -ss (a later -ss shows frame f+1)
    return Image.frombuffer('RGB', (W, H), raw, 'raw', 'RGB', 0, 1)
cw, ch = 360, 400; sh = Image.new('RGB', (cw * 3 + 8, (ch + 4) * len(items)), (16, 16, 16)); d = ImageDraw.Draw(sh)
for k, (f, r, c) in enumerate(items):
    x0 = min(max(c * 180 + 90 - cw // 2, 0), W - cw); y0 = min(max(r * 240 + 120 - ch // 2, 0), H - ch)
    for j, g in enumerate((f - 1, f, f + 1)):
        sh.paste(frame(g).crop((x0, y0, x0 + cw, y0 + ch)), (j * (cw + 4), k * (ch + 4))); d.text((j * (cw + 4) + 4, k * (ch + 4) + 2), f'f{g} {(g - 1) / 30:.2f}s', fill=(255, 235, 60))
sh.save(out, quality=86); print(out, sh.size)
