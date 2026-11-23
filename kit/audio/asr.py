# asr.py - word timings from a voice-over with faster-whisper, matched to the script (run in the Higgsfield sandbox).
#   python3 asr.py <audio> <out.json> [lang] [script.txt]     lang: id (default) | en; the script: one line per sentence, "S01|text"
# Output: {"asr": [[word, start, end]...], "script": [[sentence_id, word]...], "times": [[start, end] or null per script word], "diff": [...]}
# Notes: the language is always forced (never auto-detected); do NOT pass the script as initial_prompt (it garbled the first 30 s in video #2).
#        The text comes from the script; the recogniser only supplies the times. Tokens without a letter (the "/" phrase marks) are ignored.
import sys, os, json, re, difflib
from faster_whisper import WhisperModel
f, out = sys.argv[1], sys.argv[2]; LANG = sys.argv[3] if len(sys.argv) > 3 else os.environ.get("LANG_CODE", "id")
SCRIPT = sys.argv[4] if len(sys.argv) > 4 else ("script.txt" if os.path.exists("script.txt") else "script_b.txt")
rows = [l.rstrip("\n").split("|", 1) for l in open(SCRIPT, encoding="utf8") if l.strip()]
sw = [(sid, w) for sid, t in rows for w in t.split() if re.search(r"[A-Za-z]", w)]
norm = lambda s: re.sub(r"[^a-z]", "", s.lower())
m = WhisperModel(os.environ.get("ASR_MODEL", "small"), device="cpu", compute_type="int8")
segs, _ = m.transcribe(f, language=LANG, word_timestamps=True, beam_size=5, condition_on_previous_text=False)
aw = [(w.word.strip(), round(w.start, 3), round(w.end, 3)) for s in segs for w in s.words]
a = [norm(w) for w, _, _ in aw]; b = [norm(w) for _, w in sw]
sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
t = [None] * len(b)
for i, j, n in sm.get_matching_blocks():
    for k in range(n): t[j + k] = (aw[i + k][1], aw[i + k][2])
diff = [(" ".join(b[j1:j2]), " ".join(a[i1:i2])) for tag, i1, i2, j1, j2 in sm.get_opcodes() if tag != "equal"]
json.dump({"asr": aw, "script": sw, "times": t, "diff": diff}, open(out, "w"), ensure_ascii=False)
print("lang", LANG, "asr words", len(aw), "script words", len(b), "matched", sum(x is not None for x in t), "span", aw[0][1], aw[-1][2])
print("diff (script -> heard):", diff)
