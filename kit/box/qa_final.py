"""qa_final.py - contact sheets and 100% crops from the finished video, plus a colour check against the rendered frames.
  python qa_final.py <video.mp4> <out_prefix> [frames_dir] [clean_master.mp4]        env: FRAMES, FPS, PROCS (set by job.sh)
  -> <prefix>_1.jpg .. _3.jpg (36 frames that walk through every render process), <prefix>_crops.jpg (caption band at 100%)
Colour check (when frames_dir is given): three frames of each video are decoded twice, with the colour matrix the file is tagged with
and with the other common one (BT.601), and compared with their PNG frames above the caption band. The tagged matrix must be the closer
one; if BT.601 fits better, the encode converted RGB with the wrong matrix (see the note in captions.py)."""
import subprocess, sys, os
import numpy as np
from PIL import Image, ImageDraw, ImageFont
mp4, pre = sys.argv[1], sys.argv[2]; frames_dir = sys.argv[3] if len(sys.argv) > 3 else None; clean = sys.argv[4] if len(sys.argv) > 4 else None
N = int(os.environ.get('FRAMES', '0')) or int(subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=nb_frames', '-of', 'csv=p=0', mp4], capture_output=True, text=True).stdout.strip())
FPS = int(os.environ.get('FPS', '30')); P = int(os.environ.get('PROCS', '3')); tmp = pre + '_tmp.png'
font = next((ImageFont.truetype(c, 18) for c in ('/usr/share/fonts/opentype/inter/Inter-Bold.otf', '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf') if os.path.exists(c)), ImageFont.load_default())
def grab(f, src=None, vf=None):
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-ss', f'{max((f - 1) / FPS - 0.012, 0):.3f}', '-i', src or mp4, '-frames:v', '1'] + (['-vf', vf] if vf else []) + [tmp], check=True); return Image.open(tmp).convert('RGB')   # seek 12 ms BEFORE the frame: ffmpeg returns the first frame at or after -ss (a later -ss shows frame f+1)
step = max(1, (N - 22) // 35); step -= (step - 1) % P                 # step = 1 (mod PROCS): the sample walks through every render process
frames = [f for f in [10 + step * k for k in range(35)] + [N - 12] if 1 <= f <= N]
for s in range(0, len(frames), 12):
    sh = Image.new('RGB', (6 * 270 + 20, 2 * 480 + 4), (16, 16, 16))
    for k, f in enumerate(frames[s:s + 12]):
        im = grab(f).resize((270, 480), Image.LANCZOS); d = ImageDraw.Draw(im); lab = f'{(f - 1) / FPS:.1f}s'
        d.rectangle([0, 0, d.textlength(lab, font=font) + 10, 26], fill=(0, 0, 0)); d.text((5, 2), lab, font=font, fill=(255, 235, 60)); sh.paste(im, ((k % 6) * 274, (k // 6) * 484))
    out = f'{pre}_{s // 12 + 1}.jpg'; sh.save(out, quality=80); print(out, sh.size, os.path.getsize(out))
crops = [grab(max(2, int(N * q))).crop((90, 1090, 990, 1560)) for q in (0.064, 0.39, 0.726)]
sh = Image.new('RGB', (900, 470 * 3 + 8), (16, 16, 16))
for k, c in enumerate(crops): sh.paste(c, (0, k * 474))
sh.save(pre + '_crops.jpg', quality=86); print(pre + '_crops.jpg', sh.size, os.path.getsize(pre + '_crops.jpg'))
if frames_dir:
    bad = 0
    for name, src in (('final', mp4), ('clean master', clean)):
        if not src: continue
        for f in (frames[len(frames) // 10], frames[len(frames) // 2], frames[-3]):
            png = np.asarray(Image.open(os.path.join(frames_dir, f'f_{f:05d}.png')).convert('RGB').crop((0, 0, 1080, 1000))).astype(np.float32)
            d = [float(np.abs(np.asarray(grab(f, src, vf).crop((0, 0, 1080, 1000))).astype(np.float32) - png).mean()) for vf in (None, 'scale=in_color_matrix=bt601')]
            bad += d[0] > d[1] or d[0] > 4.0; print(f'colour check, {name}, frame {f}: mean |video - png| = {d[0]:.2f} as tagged, {d[1]:.2f} if read as BT.601')
    print('COLOUR OK' if not bad else 'COLOUR FAILED: the video does not match the rendered frames (RGB->YUV matrix or range)')
if os.path.exists(tmp): os.remove(tmp)
