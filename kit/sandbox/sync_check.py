"""sync_check.py - after asr.py on the final video: do the spoken words sit where the captions are?
  python3 asr.py final.mp4 asr_final.json && python3 sync_check.py      (needs asr_proc.json and words.json from the VO step)"""
import json, os, numpy as np
a = json.load(open('asr_final.json')); p = json.load(open('asr_proc.json')); w = json.load(open('words.json'))['words']
ta, tp, n = a['times'], p['times'], len(p['times']); OFF = float(os.environ.get('OFFSET', '0.30'))
d = np.array([ta[i][0] - (tp[i][0] + OFF) for i in range(n) if ta[i] and tp[i]])
print('script words', n, '| recognised in final', sum(x is not None for x in ta), '| in processed VO', sum(x is not None for x in tp), '| in both', len(d))
print('word start, final - (VO + 0.30): median %.3f  p95 |d| %.3f  max |d| %.3f' % (np.median(d), np.percentile(np.abs(d), 95), np.abs(d).max()))
d2 = np.array([ta[i][0] - (w[i][2] + OFF) for i in range(n) if ta[i]])
print('word start, final - caption time: median %.3f  p95 |d| %.3f  max |d| %.3f  (captions use pause-snapped times)' % (np.median(d2), np.percentile(np.abs(d2), 95), np.abs(d2).max()))
print('last word ends at', round(max(t[1] for t in ta if t), 2), '| heard differently (script -> heard):', a['diff'])
