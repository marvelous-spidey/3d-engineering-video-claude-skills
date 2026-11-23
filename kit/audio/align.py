# align.py - final word timings for the processed voice-over (run in the Higgsfield sandbox after asr.py on vo_proc.wav).
#   python3 asr.py vo_proc.wav asr_proc.json <lang> && python3 align.py [lang]      -> words.json {"dur", "words": [[sentence_id, word, start, end]...]}
# Words the recogniser missed are spread over the gap by syllable count; word starts and ends are snapped to real pauses >= 0.10 s.
import json, os, re, sys, numpy as np, subprocess
LANG = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("LANG_CODE", "id")
SR = 48000; HOP = 480
d = json.load(open("asr_proc.json")); sw = d["script"]; t = d["times"]; n = len(sw)
raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", "vo_proc.wav", "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True).stdout
x = np.frombuffer(raw, dtype=np.float32).astype(np.float64); m = len(x) // HOP
e = 20 * np.log10(np.sqrt((x[:m * HOP].reshape(m, HOP) ** 2).mean(axis=1)) + 1e-9); act = e > (np.percentile(e, 95) - 38)
runs, i = [], 0
while i < m:
    j = i
    while j < m and act[j] == act[i]: j += 1
    runs.append((bool(act[i]), i / 100, j / 100)); i = j
sp = [r for r in runs if r[0]]; T0, T1 = sp[0][1], sp[-1][2]
syl = lambda w: max(len(re.findall(r"[aeiouy]+" if LANG == "en" else r"[aiueo]", re.sub(r"[^a-z]", "", w.lower()))), 1)     # rough syllable count, only used to share out a gap
st = [a[0] if a else None for a in t]; en = [a[1] if a else None for a in t]; interp = sum(a is None for a in t)
i = 0
while i < n:
    if st[i] is None:
        j = i
        while j < n and st[j] is None: j += 1
        a0 = en[i - 1] if i > 0 else T0; a1 = st[j] if j < n else T1; w = [syl(sw[k][1]) for k in range(i, j)]; tot = sum(w); acc = 0
        for k in range(i, j):
            st[k] = a0 + (a1 - a0) * acc / tot; acc += w[k - i]; en[k] = a0 + (a1 - a0) * acc / tot
        i = j
    else: i += 1
sil = [(a, b) for v, a, b in runs if not v and b - a >= 0.10 and a > T0 and b < T1]
# Every real pause is a word boundary: the word before it ends at a, the word after it starts at b. The recogniser often puts the first
# word after a full stop far too early (inside the previous word), so a boundary after . ! ? may claim a pause from up to 0.9 s away and
# one after , : ; from up to 0.5 s, and both win over a boundary without punctuation, which must be within 0.22 s.
# The longest pauses choose first; a boundary is used once.
strong = {k for k in range(1, n) if re.search(r"[.!?\u2026]$", sw[k - 1][1])}; weak = {k for k in range(1, n) if re.search(r"[,:;]$", sw[k - 1][1])}; taken = {}
for a, b in sorted(sil, key=lambda p: p[0] - p[1]):
    mid = (a + b) / 2; cand = []
    for j in range(1, n):
        if j in taken: continue
        dist = abs((en[j - 1] + st[j]) / 2 - mid)
        bonus, reach = (0.45, 0.9) if j in strong else (0.2, 0.5) if j in weak else (0.0, 0.0)
        if dist < reach or abs(st[j] - b) < 0.22 or abs(en[j - 1] - a) < 0.22: cand.append((dist - bonus, j))
    if cand: taken[min(cand)[1]] = (a, b)
for j, (a, b) in taken.items(): en[j - 1] = a; st[j] = b
snapped = len(taken)
st[0] = min(st[0], T0 + 0.02) if abs(st[0] - T0) < 0.3 else st[0]
for k in range(1, n):
    if st[k] < st[k - 1] + 0.05: st[k] = st[k - 1] + 0.05
for k in range(n - 1):
    en[k] = min(max(en[k], st[k] + 0.04), st[k + 1])
en[-1] = max(en[-1], st[-1] + 0.08)
words = [[sw[k][0], re.sub(r"[^A-Za-z-]", "", sw[k][1]), round(st[k], 2), round(en[k], 2)] for k in range(n)]
json.dump({"dur": round(len(x) / SR, 3), "words": words, "raw_words": [w for _, w in sw]}, open("words.json", "w"), ensure_ascii=False)
print("dur", round(len(x) / SR, 2), "words", n, "interpolated", interp, "snapped", snapped, "pauses>=0.10:", len(sil), "min word dur", round(min(b - a for _, _, a, b in words), 2))
print("diff:", d["diff"])
print("words that span a pause >= 0.12 s (should be none):", [(w[1], w[2]) for w in words for a, b in sil if b - a >= 0.12 and w[2] + 0.02 < a and b < w[3] - 0.02])
first = {}
for k, (sid, w) in enumerate(sw): first.setdefault(sid, k)
ks = sorted(first.values()) + [n]
print("sentences:", [(sw[a][0], words[a][2], words[b - 1][3]) for a, b in zip(ks, ks[1:])])
