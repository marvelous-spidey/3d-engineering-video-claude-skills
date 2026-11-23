#!/bin/bash
# after.sh - waits for finish.sh, then uploads the final video, the clean master and the QA sheets, and builds + uploads
# crops of the strongest scan suspects. usage: nohup bash after.sh > logs/after.log 2>&1 &     (start it any time after finish.sh)
# It waits for urls.sh (U_FINAL, U_CLEAN, U_Z1, U_Z2). Presigned upload URLs stop working about one hour after they are issued, so
# ask for them and write urls.sh only when the render has about 10 minutes left. urls.sh is deleted after use: the URLs are single-use.
. "$(dirname "$0")/job.sh"; rm -f logs/after.done
while [ ! -f logs/finish.done ]; do sleep 3; done
[ -f urls.sh ] || echo "WAITING_FOR_URLS $(date -u +%H:%M:%S)"; while [ ! -f urls.sh ]; do sleep 3; done; . ./urls.sh
bash up.sh $OUT video/mp4 "$U_FINAL"
bash up.sh $CLEAN video/mp4 "$U_CLEAN"
bash up.sh $QA/sheets.zip application/octet-stream "$U_Z1"
TOP=$($PY - << 'EOF_PY'
import json, os, numpy as np
q = os.environ['QA']; x = np.load(q + '/scan_th.npy').astype(np.float32); sus = json.load(open(q + '/scan_list.json'))['suspects']
def blocks(v): return v.reshape(v.shape[0], 8, 24, 6, 18, 3).mean(axis=(2, 4, 5))
sc = {}
for f in sus:
    i = f - 1; a = blocks(np.abs(x[i:i + 1] - x[i - 1:i]))[0]; b = blocks(np.abs(x[i + 1:i + 2] - x[i:i + 1]))[0]; c = blocks(np.abs(x[i + 1:i + 2] - x[i - 1:i]))[0]; sc[f] = float((np.minimum(a, b) - c).max())
print(' '.join(str(f) for f in sorted(sorted(sc, key=lambda f: -sc[f])[:12])))
EOF_PY
)
echo "top suspects: $TOP"; set -- $TOP
if [ $# -gt 0 ]; then
  $PY trip_png.py $FR $QA/scan $QA/trip_1.jpg ${@:1:6}
  [ $# -gt 6 ] && $PY trip_png.py $FR $QA/scan $QA/trip_2.jpg ${@:7:6}
  (cd $QA && rm -f trips.zip && $PY -m zipfile -c trips.zip trip_*.jpg && ls -la trips.zip) && bash up.sh $QA/trips.zip application/octet-stream "$U_Z2"
fi
rm -f urls.sh; echo "AFTER_DONE $(date -u +%H:%M:%S)"; touch logs/after.done
