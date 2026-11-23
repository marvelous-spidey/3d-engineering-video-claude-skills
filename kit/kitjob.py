"""kitjob.py (kit v1.0) - one source of truth for a video job. Reads job.env and words.json next to this file.

    from kitjob import FPS, OFFSET, WORDS, DUR, LAST     scene script, captions.py
    python kitjob.py                                     prints "DUR FRAMES FPS" (the box scripts read this through box/job.sh)

job.env holds KEY=VALUE lines (see job.env.example); a variable set in the environment wins over the file.
DUR = OFFSET (silence before the voice) + voice-over length ("dur" in words.json) + TAIL, rounded to 0.1 s.
"""
import json, os, re
HERE = os.path.dirname(os.path.abspath(__file__))
def _read_env(path):
    d = {}
    if os.path.exists(path):
        for line in open(path, encoding='utf8'):
            m = re.match(r'\s*([A-Za-z_][A-Za-z0-9_]*)=(.*)$', line.rstrip('\n'))
            if m: d[m.group(1)] = re.sub(r'\s+#.*$', '', m.group(2)).strip().strip('"\'')
    return d
_J = _read_env(os.path.join(HERE, 'job.env'))
def get(k, default=None): return os.environ.get(k, _J.get(k, default))
NAME = get('NAME', 'video'); LANG = get('LANG_CODE', 'id'); STYLE = get('CAPTION_STYLE', 'cards')
FPS = int(get('FPS', '30')); OFFSET = float(get('OFFSET', '0.30')); TAIL = float(get('TAIL', '1.6'))
_w = json.load(open(os.path.join(HERE, get('WORDS_JSON', 'words.json')), encoding='utf8'))
WORDS = _w['words']; DUR = round(OFFSET + _w['dur'] + TAIL, 1); LAST = int(round(DUR * FPS))
if __name__ == '__main__': print(DUR, LAST, FPS)
