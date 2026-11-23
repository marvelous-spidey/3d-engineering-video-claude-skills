# patch_words.py - video #3: "CR-V" has no vowel letters, so the syllable counter gave it one syllable and too short a share of two
# interpolated spans. Re-share those spans with the spoken count (CR-V = 3 syllables). Run once after align.py.
import json
d = json.load(open('words.json', encoding='utf8')); w = d['words']
def set_(sid, word, nth, a, b):
    k = [i for i, x in enumerate(w) if x[0] == sid and x[1] == word][nth - 1]; w[k][2], w[k][3] = a, b
set_('S01', 'CR-V', 1, 0.56, 0.99); set_('S01', 'dua', 1, 0.99, 1.28); set_('S01', 'koma', 1, 1.28, 1.57); set_('S01', 'empat', 1, 1.57, 1.86)
set_('S12', 'silinder', 1, 32.66, 33.05); set_('S12', 'CR-V', 1, 33.05, 33.44)
for a, b in zip(w, w[1:]): assert a[3] <= b[2] + 1e-9 and a[2] < a[3], (a, b)
json.dump(d, open('words.json', 'w', encoding='utf8'), ensure_ascii=False)
