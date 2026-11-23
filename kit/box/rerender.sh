#!/bin/bash
# rerender.sh - re-render frame ranges after a scene fix, then prove that frames outside the ranges did not change.
# usage: nohup bash rerender.sh "695-1262 1680-1849" "600 1400 2000" > logs/rerender.log 2>&1 &
#   1st argument: ranges to render again (their PNG files are moved to $FR.old first); 2nd: control frames outside the ranges
#   (any order). Pick one frame before the first range and one shortly after each range: a frame after a range is what shows a label
#   or part that the fix left on screen. Control frames are rendered with the new scene and must equal the frames already on disk.
# The scan cache is removed, so the next scan.py run reads every frame again.
. "$(dirname "$0")/job.sh"; mkdir -p "$FR.old"; rm -f "$QA"/scan_th.npy "$QA"/scan_bl.npy
for r in $1; do for f in $(seq ${r%-*} ${r#*-}); do p=$(printf "%s/f_%05d.png" "$FR" $f); [ -f "$p" ] && mv "$p" "$FR.old/"; done; done
i=0
for r in $1; do
  bash render.sh ${r%-*} ${r#*-}; sleep 5; while pgrep -f "${PAT}anim" > /dev/null; do sleep 3; done
  i=$((i+1)); mkdir -p logs/r$i && mv logs/render_*.log logs/r$i/
done
echo "RERENDER_DONE $(date -u +%H:%M:%S) files=$(ls $FR | wc -l)"
if [ -n "$2" ]; then
  C=$(echo $2 | tr ' ' '\n' | sort -n | tr '\n' ' '); rm -rf "$FR.chk"; mkdir -p "$FR.chk" && echo "$C" > "$FR.chk/list.txt"
  KIT_DEVICE=${KIT_DEVICE:-GPU} KIT_FMT=PNG $PY $SCENE list $RX $RY $SPP "$FR.chk" "$FR.chk/list.txt" > logs/chk.log 2>&1
  set -- $C; $PY diffall.py "$FR" "$FR.chk" $1 ${@: -1}
fi
echo "CHECK_DONE $(date -u +%H:%M:%S)"
