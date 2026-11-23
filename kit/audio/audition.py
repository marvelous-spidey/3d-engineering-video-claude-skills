# audition.py - compare short test clips of several TTS voices by measurement (run in the Higgsfield sandbox, in the clips' folder).
#   python3 audition.py <ref.txt> [lang]     reads a*.mp3 (every voice read the text in ref.txt), writes audition.json; lang: id (default) | en
# Per clip: duration, pause time, syllables per second, how many words the recogniser heard correctly, median pitch, loudness.
import glob, json, re, subprocess, difflib, numpy as np, wave, os, sys
LANG = sys.argv[2] if len(sys.argv) > 2 else os.environ.get("LANG_CODE", "id")
from faster_whisper import WhisperModel
REF = re.sub(r"\[[^\]]*\]", " ", open(sys.argv[1], encoding="utf8").read())      # [tags] for the voice model are not spoken
norm = lambda s: re.sub(r"[^a-z ]", "", s.lower()).split()
ref = norm(REF); SYL = sum(max(len(re.findall(r"[aeiouy]+" if LANG == "en" else r"[aiueo]", w)), 1) for w in ref)
m = WhisperModel("small", device="cpu", compute_type="int8")
out = []
for f in sorted(glob.glob("a*.mp3")):
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f], capture_output=True, text=True).stdout)
    segs, _ = m.transcribe(f, language=LANG, word_timestamps=True, beam_size=5)
    ws = [(w.word.strip(), w.start, w.end) for s in segs for w in s.words]
    hyp = norm(" ".join(w for w, _, _ in ws))
    sm = difflib.SequenceMatcher(None, ref, hyp, autojunk=False); hit = sum(b.size for b in sm.get_matching_blocks())
    wrong = [(" ".join(ref[i1:i2]), " ".join(hyp[j1:j2])) for tag, i1, i2, j1, j2 in sm.get_opcodes() if tag != "equal"]
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", f, "-ac", "1", "-ar", "16000", "t.wav"])
    w = wave.open("t.wav"); x = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(float) / 32768; hop = 160
    e = 20 * np.log10(np.array([np.sqrt((x[i:i + hop] ** 2).mean()) for i in range(0, len(x) - hop, hop)]) + 1e-9)
    act = e > (np.percentile(e, 95) - 35); first, last = np.where(act)[0][[0, -1]] / 100.0
    quiet = (~act[int(first * 100):int(last * 100)]).sum() / 100.0
    f0 = []
    for i in np.where(act)[0][::5]:
        seg = x[i * hop:i * hop + 1024]
        if len(seg) < 1024: continue
        seg = seg - seg.mean(); ac = np.correlate(seg, seg, "full")[1023:]; lo, hi = 16000 // 320, 16000 // 70
        k = lo + int(np.argmax(ac[lo:hi]))
        if ac[k] > 0.4 * ac[0]: f0.append(16000 / k)
    lufs = re.findall(r"I:\s+(-?[\d.]+) LUFS", subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", f, "-af", "ebur128", "-f", "null", "-"], capture_output=True, text=True).stderr)
    out.append(dict(file=f, dur=round(dur, 2), span=round(last - first, 2), pause=round(quiet, 2), syl_s_all=round(SYL / (last - first), 2), syl_s_speech=round(SYL / (last - first - quiet), 2), words_ok=f"{hit}/{len(ref)}", wrong=wrong[:6], f0=round(float(np.median(f0)), 0) if f0 else None, lufs=lufs[-1] if lufs else None))
json.dump(out, open("audition.json", "w"), ensure_ascii=False, indent=1)
for o in out: print(json.dumps(o, ensure_ascii=False))
