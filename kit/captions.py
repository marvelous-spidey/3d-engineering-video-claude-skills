"""captions.py (kit v1.0) - burn word-synced captions into the frames and mux the voice-over.

  python captions.py video <frames_dir | master.mp4> <vo_final.wav> <out.mp4>   frames f_00001.png ... (1080x1920), or a clean master to re-caption
  python captions.py clean <frames_dir> <out.mp4>                               master without captions or sound
  python captions.py test  <frame.png> <t_seconds> <out.png>                    one captioned frame (any 9:16 size)
  python captions.py list                                                       the cards or phrases with their times

Reads, next to this file: job.env + words.json (through kitjob.py), script.txt ("S01|text" per sentence: the text as it should
appear on screen, numbers written as words) and, optionally, keywords.txt (cards style; "S01 word [nth]" per line = yellow).
CAPTION_STYLE in job.env:
  cards    one card of 1-2 words at a time, heavy rounded font, key words yellow, 3-frame pop-in (video #2)
  phrases  a phrase of 2-4 words that fills in word by word (video #1); breaks: " / " in script.txt, otherwise automatic
Env: CAP_FONT=<font file>, CAP_Y (centre as a fraction of the height), CRF, IN_MATRIX=bt601|bt709 (override a master's colour tag).
Colour: RGB is converted to YUV with the BT.709 matrix by an explicit scale filter. Tagging alone is not enough: without the
filter ffmpeg converts with BT.601, and greens come out about 10% darker (the first encode of video #2 had this fault).
"""
import json, os, re, subprocess, sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from kitjob import FPS, OFFSET, WORDS, DUR, LAST, STYLE, get
W, H = 1080, 1920
norm = lambda s: re.sub(r'[^a-z]', '', s.lower())
ROWS = [l.rstrip('\n').split('|', 1) for l in open(os.path.join(HERE, get('SCRIPT_TXT', 'script.txt')), encoding='utf8') if l.strip()]
if any(re.search(r'\d', t) for _, text in ROWS for t in text.split()): sys.exit('script.txt: write numbers as words (a digit group is one token but several spoken words)')
TOKP = [t for _, text in ROWS for t in text.split() if norm(t)]                    # as written, punctuation kept ("/" marks drop out here)
TOK = [re.sub(r'[.,:;…]', '', t) for t in TOKP]                                    # cards drop the quiet punctuation
assert len(TOK) == len(WORDS) and all(norm(a) == norm(b[1]) for a, b in zip(TOK, WORDS)), 'script.txt and words.json differ'
def idx(sid, word, nth=1): return [k for k, w in enumerate(WORDS) if w[0] == sid and norm(w[1]) == norm(word)][nth - 1]
HL = set(); _kw = os.path.join(HERE, get('KEYWORDS_TXT', 'keywords.txt'))
if os.path.exists(_kw):
    for line in open(_kw, encoding='utf8'):
        p = line.split('#')[0].split()
        if len(p) >= 2: HL.add(idx(p[0], p[1], int(p[2]) if len(p) > 2 else 1))

# ---------------------------------------------------------------- cards (1-2 words at a time)
def build_cards():
    cards, i, n = [], 0, len(WORDS)
    while i < n:
        j = i
        if i + 1 < n and WORDS[i][0] == WORDS[i + 1][0] and WORDS[i + 1][2] - WORDS[i][3] < 0.10:
            short = len(norm(TOK[i])) <= 3 or WORDS[i][3] - WORDS[i][2] < 0.13
            if short and len(norm(TOK[i])) + len(norm(TOK[i + 1])) <= 13 and not (i in HL) ^ (i + 1 in HL): j = i + 1
        cards.append([WORDS[i][2] + OFFSET, WORDS[j][3] + OFFSET, ' '.join(TOK[i:j + 1]), i in HL]); i = j + 1
    for c, nxt in zip(cards, cards[1:] + [None]):                      # a card stays up until the next one, but not through a long pause
        c[1] = min(nxt[0], c[1] + 0.5) if nxt else c[1] + 0.9
    return cards

# ---------------------------------------------------------------- phrases (2-4 words, filling in word by word)
def phrase_groups():
    """Number of words in each phrase. Manual breaks: ' / ' in script.txt. Automatic: break after punctuation, at most 4 words, no lone leftover word."""
    groups = []
    for sid, text in ROWS:
        toks = text.split()
        if '/' in toks:
            n = 0
            for t in toks + ['/']:
                if t == '/':
                    if n: groups.append(n)
                    n = 0
                elif norm(t): n += 1
        else:
            k = 0
            for t in [t for t in toks if norm(t)] + [None]:
                if t is not None: k += 1
                if t is None or re.search(r'[.,:;!?…]$', t):
                    while k > 4: g = 2 if k == 5 else 3; groups.append(g); k -= g
                    if k: groups.append(k)
                    k = 0
    return groups
def build_phrases():
    ph, i = [], 0
    for g in phrase_groups():
        ph.append({'words': TOKP[i:i + g], 'starts': [WORDS[i + j][2] + OFFSET for j in range(g)], 'end': WORDS[i + g - 1][3] + OFFSET}); i += g
    assert i == len(WORDS), (i, len(WORDS))
    for a, b in zip(ph, ph[1:] + [None]):
        a['t0'] = a['starts'][0]; a['t1'] = min(b['starts'][0], a['end'] + 0.5) if b else a['end'] + 0.9
    return ph
ITEMS = build_cards() if STYLE == 'cards' else build_phrases()

def find_font(cands):
    for c in cands:
        if c and os.path.exists(c): return c
    sys.exit('no caption font found; set CAP_FONT=/path/to/font')
if STYLE == 'cards':
    FONT_PATH = find_font([os.environ.get('CAP_FONT', ''), os.path.join(HERE, 'Baloo2.ttf')]); CAP_Y = float(os.environ.get('CAP_Y', '0.695'))
else:
    FONT_PATH = find_font([os.environ.get('CAP_FONT', ''), '/usr/share/fonts/opentype/inter/Inter-SemiBold.otf', '/usr/share/fonts/truetype/inter/Inter-SemiBold.ttf',
                           os.path.join(HERE, 'Inter-SemiBold.otf'), '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf']); CAP_Y = float(os.environ.get('CAP_Y', '0.675'))
NAVY, WHITE, YELLOW = (13, 24, 58), (255, 255, 255), (255, 214, 58)
_sprites = {}
def sprite(text, hi, scale=1.0):
    """RGBA picture of one card at 1080-wide scale * `scale` (cached)."""
    k = (text, hi, round(scale, 3))
    if k in _sprites: return _sprites[k]
    size = 124
    while True:
        font = ImageFont.truetype(FONT_PATH, int(size * scale))
        try: font.set_variation_by_axes([800])
        except Exception: pass
        sw = max(2, int(round(size * scale * 0.085))); l, t, r, b = font.getbbox(text, stroke_width=sw)
        if (r - l) <= 960 * scale or size <= 70: break
        size -= 6
    pad = int(26 * scale); im = Image.new('RGBA', (r - l + 2 * pad, b - t + 2 * pad), (0, 0, 0, 0))
    sh = Image.new('RGBA', im.size, (0, 0, 0, 0)); ImageDraw.Draw(sh).text((pad - l, pad - t + int(8 * scale)), text, font=font, fill=(0, 0, 0, 150), stroke_width=sw, stroke_fill=(0, 0, 0, 150))
    im = Image.alpha_composite(im, sh.filter(ImageFilter.GaussianBlur(7 * scale)))
    ImageDraw.Draw(im).text((pad - l, pad - t), text, font=font, fill=YELLOW if hi else WHITE, stroke_width=sw, stroke_fill=NAVY)
    _sprites[k] = im; return im
POP = (0.84, 0.96, 1.05)                                               # scale during the first frames of a card
SIZE, BAND = 66, 110                                                   # phrases: font px and half-height of the overlay band at 1080 wide
_pf = []; _pcache = {}
def phrase_overlay(t):
    """RGBA band (W x 2*BAND) with the part of the phrase that has been spoken at time t, or None."""
    if not _pf: _pf.append(ImageFont.truetype(FONT_PATH, SIZE))
    font = _pf[0]
    for pi, p in enumerate(ITEMS):
        if p['t0'] <= t < p['t1']:
            n = sum(1 for s in p['starts'] if s <= t + 1e-6); k = (pi, n)
            if k not in _pcache:
                full = ' '.join(p['words']); shown = ' '.join(p['words'][:n]); x0 = (W - font.getlength(full)) / 2; y = BAND
                sh = Image.new('RGBA', (W, 2 * BAND), (0, 0, 0, 0)); d = ImageDraw.Draw(sh)
                d.text((x0, y + 4), shown, font=font, fill=(0, 0, 0, 255), anchor='lm', stroke_width=4, stroke_fill=(0, 0, 0, 255))
                sh = sh.filter(ImageFilter.GaussianBlur(7)); sh.putalpha(sh.getchannel('A').point(lambda v: min(255, int(v * 1.35))))
                d = ImageDraw.Draw(sh); d.text((x0, y), shown, font=font, fill=(255, 255, 255, 255), anchor='lm', stroke_width=2, stroke_fill=(18, 18, 22, 235))
                _pcache[k] = sh
            return _pcache[k]
    return None
def caption(frame, t):
    """Composite the caption that is up at time t onto a PIL RGB frame (any 9:16 size)."""
    sc = frame.width / W
    if STYLE == 'cards':
        for t0, t1, text, hi in ITEMS:
            if t0 <= t < t1:
                im = sprite(text, hi, sc); n = int((t - t0) * FPS + 1e-6)
                if n < len(POP): im = im.resize((max(2, int(im.width * POP[n])), max(2, int(im.height * POP[n]))), Image.LANCZOS)
                x = (frame.width - im.width) // 2; y = int(frame.height * CAP_Y) - im.height // 2
                frame.paste(im, (x, y), im); break
    else:
        ov = phrase_overlay(t)
        if ov is not None:
            if frame.width != W: ov = ov.resize((frame.width, max(2, int(round(ov.height * sc)))), Image.LANCZOS)
            frame.paste(ov, (0, int(frame.height * CAP_Y) - ov.height // 2), ov)
    return frame

def frames_from(src):
    """PIL RGB frames from a folder of f_00001.png ... or from a video file (a clean master)."""
    if os.path.isdir(src):
        for f in range(1, LAST + 1): yield Image.open(os.path.join(src, f'f_{f:05d}.png')).convert('RGB')
        return
    tag = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=color_space', '-of', 'csv=p=0', src], capture_output=True, text=True).stdout.strip()
    m = os.environ.get('IN_MATRIX') or {'bt709': 'bt709', 'smpte170m': 'bt601', 'bt470bg': 'bt601'}.get(tag, 'bt709')
    p = subprocess.Popen(['ffmpeg', '-loglevel', 'error', '-i', src, '-vf', f'scale=in_color_matrix={m},format=rgb24', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE, bufsize=W * H * 3)
    for f in range(1, LAST + 1):
        buf = p.stdout.read(W * H * 3)
        if len(buf) < W * H * 3: sys.exit(f'{src}: only {f - 1} frames of {W}x{H}, expected {LAST}')
        yield Image.frombuffer('RGB', (W, H), buf, 'raw', 'RGB', 0, 1).copy()
    p.stdout.close(); p.wait()
def encode(src, out, audio=None, captions=True):
    crf = os.environ.get('CRF', '17' if captions else '15'); part = out[:-4] + '.part.mp4'
    cmd = ['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-']
    if audio: cmd += ['-i', audio, '-map', '0:v', '-map', '1:a']
    cmd += ['-vf', 'scale=out_color_matrix=bt709:out_range=tv,format=yuv420p', '-c:v', 'libx264', '-preset', 'medium', '-crf', crf,
            '-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709', '-color_range', 'tv', '-movflags', '+faststart']
    if audio: cmd += ['-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-t', f'{DUR:.3f}']
    p = subprocess.Popen(cmd + [part], stdin=subprocess.PIPE)
    for f, im in enumerate(frames_from(src), 1):
        if im.size != (W, H): sys.exit(f'frame {f} is {im.size}, expected {(W, H)}')
        if captions: caption(im, (f - 1) / FPS)
        p.stdin.write(im.tobytes())
        if f % 300 == 0: print('frame', f, flush=True)
    p.stdin.close()
    if p.wait() != 0: sys.exit('ffmpeg failed')
    os.replace(part, out); print('wrote', out, os.path.getsize(out))

if __name__ == '__main__':
    mode = sys.argv[1]
    if mode == 'video': encode(sys.argv[2], sys.argv[4], audio=sys.argv[3])
    elif mode == 'clean': encode(sys.argv[2], sys.argv[3], captions=False)
    elif mode == 'test':
        im = Image.open(sys.argv[2]).convert('RGB'); caption(im, float(sys.argv[3])).save(sys.argv[4])
    elif mode in ('list', 'cards') and STYLE == 'cards':
        d = [c[1] - c[0] for c in ITEMS]
        print(len(ITEMS), 'cards; shortest', round(min(d), 2), 's; under 0.17 s:', sum(x < 0.17 for x in d), '; DUR', DUR, 'frames', LAST)
        print(' | '.join(f"{c[0]:.2f} {'*' if c[3] else ''}{c[2]}" for c in ITEMS))
    elif mode in ('list', 'phrases'):
        print(len(ITEMS), 'phrases; DUR', DUR, 'frames', LAST)
        for p in ITEMS: print(f"{p['t0']:6.2f}-{p['t1']:6.2f}  {' '.join(p['words'])}")
