#!/usr/bin/env python3
"""ref_teardown.py - measure a reference short without watching or hearing it.

Every number in a reference analysis should come from here (frames, burned-in
captions, pixel change, audio signal), because the agent cannot play the video.

usage:
  ref_teardown.py probe    <video>
  ref_teardown.py sheets   <video> <out_dir> [fps=1] [cols=5] [rows=4]
  ref_teardown.py captions <video> <out_dir> <band_top_px> <band_height_px> [fps=15]
  ref_teardown.py pace     <ocr_words.json> <transcript.txt>
  ref_teardown.py motion   <video>
  ref_teardown.py audio    <video>

notes:
  captions  works for white caption text with a dark outline (the common shorts style).
            Find the band first by looking at a contact sheet; it writes ocr_words.json
            ([[time_s, token], ...]), which is noisy by design.
  pace      wants a transcript you cleaned by hand from the OCR tokens, sentences
            separated by '|'. It aligns tokens to that text and prints timing per sentence.
needs: ffmpeg, ffprobe, numpy, pillow; captions also needs scipy and pytesseract.
"""
import difflib, glob, json, os, re, subprocess, sys, wave

import numpy as np


def run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, **kw)


def ffprobe(video):
    out = run(['ffprobe', '-v', 'error', '-show_streams', '-show_format', '-of', 'json', video]).stdout
    return json.loads(out)


def video_info(video):
    info = ffprobe(video)
    v = next(s for s in info['streams'] if s['codec_type'] == 'video')
    a = next((s for s in info['streams'] if s['codec_type'] == 'audio'), None)
    num, den = v['r_frame_rate'].split('/')
    return info, v, a, float(num) / float(den)


def cmd_probe(video):
    info, v, a, fps = video_info(video)
    print(f"file      {os.path.basename(video)}  {int(info['format']['size']):,} bytes")
    print(f"video     {v['codec_name']} {v['width']}x{v['height']}  {fps:.3f} fps  "
          f"{v.get('nb_frames', '?')} frames  {float(info['format']['duration']):.2f} s")
    if a:
        print(f"audio     {a['codec_name']} {a['sample_rate']} Hz  {a['channels']} ch")
    print("next      run `motion` to learn whether the frame rate is real (duplicate frames) and how the camera moves")


def cmd_sheets(video, out_dir, fps=1, cols=5, rows=4):
    from PIL import Image, ImageDraw
    fps, cols, rows = float(fps), int(cols), int(rows)
    os.makedirs(out_dir, exist_ok=True)
    run(['ffmpeg', '-y', '-loglevel', 'error', '-i', video, '-vf', f'fps={fps},scale=216:-2',
         '-q:v', '4', os.path.join(out_dir, 's_%04d.jpg')])
    files = sorted(glob.glob(os.path.join(out_dir, 's_*.jpg')))
    per = cols * rows
    for n in range(0, len(files), per):
        tiles = [Image.open(f) for f in files[n:n + per]]
        w, h = tiles[0].size
        sheet = Image.new('RGB', (cols * w, rows * h), (20, 20, 20))
        for i, im in enumerate(tiles):
            x, y = (i % cols) * w, (i // cols) * h
            sheet.paste(im, (x, y))
            ImageDraw.Draw(sheet).text((x + 6, y + 4), f"{(n + i) / fps:.0f}s", fill=(255, 255, 0))
        name = os.path.join(out_dir, f"sheet_{n // per + 1:02d}.jpg")
        sheet.save(name, quality=85)
        print('wrote', name)
    print(len(files), 'frames at', fps, 'fps')


def caption_mask(path):
    """White glyph pixels that sit next to a dark outline."""
    from PIL import Image
    from scipy import ndimage
    a = np.asarray(Image.open(path).convert('RGB')).astype(int)
    white = a.min(axis=2) > 228
    near_dark = ndimage.binary_dilation(a.max(axis=2) < 70, iterations=7)
    lab, n = ndimage.label(white)
    keep = np.zeros_like(white)
    for i in range(1, n + 1):
        blob = lab == i
        size = blob.sum()
        if size >= 60 and (blob & near_dark).sum() / size > 0.25:
            keep |= blob
    return keep


def cmd_captions(video, out_dir, band_top, band_height, fps=15):
    import pytesseract
    from PIL import Image
    fps = float(fps)
    os.makedirs(out_dir, exist_ok=True)
    _, v, _, _ = video_info(video)
    run(['ffmpeg', '-y', '-loglevel', 'error', '-i', video, '-vf',
         f"fps={fps},crop={v['width']}:{int(band_height)}:0:{int(band_top)}", os.path.join(out_dir, 'c_%05d.png')])
    files = sorted(glob.glob(os.path.join(out_dir, 'c_*.png')))
    prev, segs = None, []
    for k, f in enumerate(files):                      # a new segment starts when the glyph mask changes
        m = caption_mask(f)
        if prev is None or (m ^ prev).sum() > 0.18 * max(1, (m | prev).sum()):
            segs.append((k, m))
            prev = m
    allowed = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789\\'.,!?-"   # \' survives shlex
    words = []
    for k, m in segs:
        if m.sum() < 300:
            continue
        ys, xs = np.where(m)
        crop = m[max(0, ys.min() - 14):ys.max() + 15, max(0, xs.min() - 20):xs.max() + 21]
        im = Image.fromarray(np.where(crop, 0, 255).astype(np.uint8))
        im = im.resize((crop.shape[1] * 2, crop.shape[0] * 2), Image.LANCZOS)
        t = pytesseract.image_to_string(im, config=f'--psm 7 -c tessedit_char_whitelist={allowed}').strip()
        if t and (not words or words[-1][1] != t):
            words.append((round(k / fps, 2), t))
    out = os.path.join(out_dir, 'ocr_words.json')
    json.dump(words, open(out, 'w'))
    print(len(files), 'crops ->', len(segs), 'segments ->', len(words), 'tokens; wrote', out)
    print(' '.join(w for _, w in words))


def cmd_pace(ocr_json, transcript_txt):
    ocr = json.load(open(ocr_json))
    sents = [s.split() for s in open(transcript_txt, encoding='utf8').read().split('|') if s.strip()]
    flat = [w for s in sents for w in s]
    norm = lambda w: re.sub(r'[^a-z0-9]', '', w.lower())
    a, b = [norm(w) for _, w in ocr], [norm(w) for w in flat]
    t = [None] * len(b)
    for i, j, n in difflib.SequenceMatcher(None, a, b, autojunk=False).get_matching_blocks():
        for k in range(n):
            if t[j + k] is None:
                t[j + k] = ocr[i + k][0]
    missing = sum(x is None for x in t)
    known = [k for k, x in enumerate(t) if x is not None]
    for i in range(len(t)):                            # fill unmatched words by interpolation
        if t[i] is None:
            p = max((k for k in known if k < i), default=None)
            q = min((k for k in known if k > i), default=None)
            t[i] = t[p] if q is None else t[q] if p is None else t[p] + (t[q] - t[p]) * (i - p) / (q - p)
    print(f"{len(b)} words, {len(sents)} sentences, {missing} words timed by interpolation")
    k, starts = 0, []
    for s in sents:
        starts.append(t[k])
        k += len(s)
    ends = starts[1:] + [t[-1] + 0.4]
    for s, t0, t1 in zip(sents, starts, ends):
        print(f"{t0:6.2f}-{t1:6.2f}  {len(s):3d} w  {len(s) / max(t1 - t0, 1e-6):4.2f} w/s  {' '.join(s[:3])} ...")
    dur = t[-1] - t[0] + 0.4
    print(f"overall {len(b) / dur:.2f} words/s = {60 * len(b) / dur:.0f} words/min over {dur:.1f} s of narration")


def cmd_motion(video):
    _, v, _, fps = video_info(video)
    raw = subprocess.run(['ffmpeg', '-loglevel', 'error', '-i', video, '-vf', 'scale=90:160,format=gray',
                          '-f', 'rawvideo', '-'], capture_output=True).stdout
    a = np.frombuffer(raw, dtype=np.uint8).reshape(-1, 160, 90).astype(float)
    d = np.abs(a[1:] - a[:-1]).mean(axis=(1, 2))
    print(f"{len(a)} frames at {fps:.2f} fps; picture change per frame: median {np.median(d):.2f}, p95 {np.percentile(d, 95):.2f}")
    print(f"near-duplicate frames: {100 * (d < 0.05).mean():.1f}%  (about 50% would mean 30 fps content in a 60 fps file)")
    spikes = [i for i in range(1, len(d) - 1) if d[i] > 12 and d[i] > 3 * max(d[i - 1], d[i + 1])]
    print('hard-cut candidates (s):', [round((i + 1) / fps, 2) for i in spikes] or 'none')
    s = np.convolve(d, np.ones(9) / 9, 'same')
    hot, eps, i = s > 3.0, [], 0
    while i < len(hot):                                # runs of strong change = fast camera moves or transitions
        if hot[i]:
            j = i
            while j < len(hot) and hot[j]:
                j += 1
            if j - i >= fps / 10:
                eps.append((i / fps, (j - i) / fps))
            i = j
        else:
            i += 1
    if eps:
        print(f"fast moves: {len(eps)}, median length {np.median([e[1] for e in eps]):.2f} s, "
              f"median gap between starts {np.median(np.diff([e[0] for e in eps])) if len(eps) > 1 else 0:.2f} s")
        print('  starts (s):', [round(e[0], 1) for e in eps])
    print(f"time split: fast {100 * hot.mean():.0f}%, slow drift {100 * ((s >= 0.6) & ~hot).mean():.0f}%, nearly still {100 * (s < 0.6).mean():.0f}%")


def cmd_audio(video):
    tmp = video + '.teardown.wav'
    run(['ffmpeg', '-y', '-loglevel', 'error', '-i', video, '-ac', '2', '-ar', '22050', tmp])
    log = run(['ffmpeg', '-hide_banner', '-nostats', '-i', video, '-af', 'ebur128', '-f', 'null', '-']).stderr
    lufs = re.findall(r'I:\s+(-?[\d.]+) LUFS', log)
    lra = re.findall(r'LRA:\s+(-?[\d.]+) LU', log)
    sil = run(['ffmpeg', '-hide_banner', '-nostats', '-i', video, '-af', 'silencedetect=noise=-38dB:d=0.18',
               '-f', 'null', '-']).stderr.count('silence_end')
    w = wave.open(tmp)
    sr = w.getframerate()
    x = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).reshape(-1, 2).astype(float) / 32768
    os.remove(tmp)
    mid, side = (x[:, 0] + x[:, 1]) / 2, (x[:, 0] - x[:, 1]) / 2
    db = lambda v: 20 * np.log10(np.sqrt((v ** 2).mean()) + 1e-9)
    print(f"loudness {lufs[-1] if lufs else '?'} LUFS, range {lra[-1] if lra else '?'} LU; pauses >= 0.18 s below -38 dB: {sil}")
    print(f"stereo: mid {db(mid):.1f} dB, side {db(side):.1f} dB  (side near -180 dB = mono)")
    hop = int(sr * 0.05)
    e = np.array([db(mid[i:i + hop]) for i in range(0, len(mid) - hop, hop)])
    print('level percentiles 5/25/50/90 (dB):', [round(float(np.percentile(e, p)), 1) for p in (5, 25, 50, 90)])
    floors = [round(float(e[i:i + 40].min()), 1) for i in range(0, len(e) - 40, 40)]
    print('quietest 50 ms in each 2 s window (dB):', floors, '-> a steady music bed would keep these high and even')
    loud = np.where(e > np.percentile(e, 50))[0]
    f0 = []
    for i in loud[::3]:                                # pitch of the voice by autocorrelation
        seg = mid[i * hop:i * hop + 2048]
        if len(seg) < 2048:
            continue
        seg = seg - seg.mean()
        ac = np.correlate(seg, seg, 'full')[2047:]
        lo, hi = int(sr / 320), int(sr / 70)
        k = lo + int(np.argmax(ac[lo:hi]))
        if ac[k] > 0.35 * ac[0]:
            f0.append(sr / k)
    if f0:
        print(f"median voice pitch {np.median(f0):.0f} Hz from {len(f0)} voiced frames")
    last = int(np.where(e > np.percentile(e, 50))[0][-1])
    tail = e[last + 6:]
    if len(tail) > 4:
        floor = float(np.percentile(e, 5))
        verdict = ('above the floor: an end sound or music tail' if np.median(tail) > floor + 6
                   else 'at the floor: silence')
        print(f"after the last loud frame ({last * 0.05:.1f} s): {len(tail) * 0.05:.1f} s left at about {np.median(tail):.1f} dB; "
              f"floor {floor:.1f} dB -> {verdict}")


if __name__ == '__main__':
    cmds = {'probe': cmd_probe, 'sheets': cmd_sheets, 'captions': cmd_captions, 'pace': cmd_pace,
            'motion': cmd_motion, 'audio': cmd_audio}
    if len(sys.argv) < 3 or sys.argv[1] not in cmds:
        sys.exit(__doc__)
    cmds[sys.argv[1]](*sys.argv[2:])
