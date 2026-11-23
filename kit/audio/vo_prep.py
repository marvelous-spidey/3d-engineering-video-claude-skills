# vo_prep.py - turn a raw TTS take into the final voice-over track (run in the Higgsfield sandbox; needs ffmpeg + numpy).
#   python3 vo_prep.py <target_seconds> <raw.mp3>      -> vo_tight.wav, vo_tempo.wav, vo_proc.wav (48 kHz mono) + one JSON line of numbers
# Steps: find speech (10 ms frames louder than p95 - 38 dB); shorten every pause > 0.12 s to min(0.30, 0.12 + 0.22 * (L - 0.12));
#        speed up by at most 1.10x to reach the target; gain to -13 LUFS, then limiter at 0.84 (true result about -14.4 LUFS).
import numpy as np, subprocess, json, re, sys, difflib, math
SR = 48000; HOP = SR // 100
def sh(*a): return subprocess.run(list(a), capture_output=True, text=True)
def load(f):
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", f, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True).stdout
    return np.frombuffer(raw, dtype=np.float32).astype(np.float64)
def save(x, f):
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "-", "-c:a", "pcm_s16le", f], stdin=subprocess.PIPE)
    p.communicate(x.astype(np.float32).tobytes())
def activity(x):
    n = len(x) // HOP; e = 20 * np.log10(np.sqrt((x[:n * HOP].reshape(n, HOP) ** 2).mean(axis=1)) + 1e-9)
    act = e > (np.percentile(e, 95) - 38)
    def runs(a):
        out, i = [], 0
        while i < len(a):
            j = i
            while j < len(a) and a[j] == a[i]: j += 1
            out.append([bool(a[i]), i, j]); i = j
        return out
    for v, i, j in runs(act):                     # drop speech blips < 30 ms
        if v and j - i < 3: act[i:j] = False
    for v, i, j in runs(act):                     # close silences < 60 ms
        if not v and j - i < 6 and i > 0 and j < len(act): act[i:j] = True
    return act, runs(act)
def lufs(f):
    r = re.findall(r"I:\s+(-?[\d.]+) LUFS", sh("ffmpeg", "-hide_banner", "-nostats", "-i", f, "-af", "ebur128", "-f", "null", "-").stderr)
    return float(r[-1])
x = load(sys.argv[2] if len(sys.argv) > 2 else "vo_raw.mp3"); act, rr = activity(x)
sp = [r for r in rr if r[0]]; first, last = sp[0][1], sp[-1][2]
pieces, pauses, fade = [], [], int(SR * 0.004)
for v, i, j in rr:
    if j <= first or i >= last: continue
    if v: pieces.append(x[i * HOP:j * HOP]); continue
    L = (j - i) / 100.0; new = L if L <= 0.12 else min(0.30, 0.12 + 0.22 * (L - 0.12)); pauses.append((round(L, 2), round(new, 2)))
    k = int(new * SR / 2); a = x[i * HOP:i * HOP + k].copy(); b = x[j * HOP - k:j * HOP].copy()
    if k > fade: a[-fade:] *= np.linspace(1, 0, fade); b[:fade] *= np.linspace(0, 1, fade)
    pieces += [a, b]
y = np.concatenate([np.zeros(int(SR * 0.02))] + pieces + [np.zeros(int(SR * 0.10))]); save(y, "vo_tight.wav")
D1 = len(y) / SR; TARGET = float(sys.argv[1]) if len(sys.argv) > 1 else 65.0; tempo = min(1.10, max(1.0, D1 / TARGET))
sh("ffmpeg", "-y", "-loglevel", "error", "-i", "vo_tight.wav", "-af", f"atempo={tempo:.4f}", "-ar", str(SR), "vo_tempo.wav")
gain = -13.0 - lufs("vo_tempo.wav")
sh("ffmpeg", "-y", "-loglevel", "error", "-i", "vo_tempo.wav", "-af", f"volume={gain:.2f}dB,alimiter=limit=0.84:attack=5:release=50:level=false", "-ar", str(SR), "-c:a", "pcm_s16le", "vo_proc.wav")
z = load("vo_proc.wav"); D = len(z) / SR
long_raw = sorted([p[0] for p in pauses], reverse=True)[:6]
print(json.dumps(dict(raw=round(len(x) / SR, 2), speech_start=first / 100, speech_end=last / 100, n_pauses=len(pauses), pause_raw_total=round(sum(p[0] for p in pauses), 2), pause_new_total=round(sum(p[1] for p in pauses), 2), longest_raw=long_raw, tight=round(D1, 2), tempo=round(tempo, 4), proc=round(D, 2), gain_db=round(gain, 2), lufs_out=lufs("vo_proc.wav"))))
