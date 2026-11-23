"""sheets.py - numbered contact sheets from rendered frames (or any images).
  python sheets.py <frames_dir> <out_prefix> <cols> <cell_w> <quality> <frame numbers...>     -> out_prefix_1.jpg, _2.jpg ... (2 rows each)"""
import sys, os
from PIL import Image, ImageDraw, ImageFont
d, pre, cols, cw, q = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5]); fs = [int(v) for v in sys.argv[6:]]
font = ImageFont.truetype('/usr/share/fonts/opentype/inter/Inter-Bold.otf', max(14, cw // 15)); per = cols * 2
for s in range(0, len(fs), per):
    grp = fs[s:s + per]; ch = round(cw * 1920 / 1080); rows = (len(grp) + cols - 1) // cols
    sh = Image.new('RGB', (cols * cw + 4 * (cols - 1), rows * ch + 4 * (rows - 1)), (16, 16, 16))
    for k, f in enumerate(grp):
        p = os.path.join(d, f'f_{f:05d}.png')
        if not os.path.exists(p): continue
        im = Image.open(p).convert('RGB').resize((cw, ch), Image.LANCZOS); dr = ImageDraw.Draw(im); lab = f'{(f - 1) / 30:.1f}s'
        dr.rectangle([0, 0, dr.textlength(lab, font=font) + 10, font.size + 8], fill=(0, 0, 0)); dr.text((5, 2), lab, font=font, fill=(255, 235, 60))
        sh.paste(im, ((k % cols) * (cw + 4), (k // cols) * (ch + 4)))
    out = f'{pre}_{s // per + 1}.jpg'; sh.save(out, quality=q); print(out, sh.size, os.path.getsize(out))
