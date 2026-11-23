#!/bin/bash
# render.sh - start the parallel render. usage: bash render.sh [first_frame] [last_frame]      (default: all frames; PROCS and SPP come from job.env)
# Process k renders first+k, first+k+PROCS, ...; frames that already exist are skipped, so it resumes. Persistent data stays off (KIT_PERSIST=0).
. "$(dirname "$0")/job.sh"; F0=${1:-1}; F1=${2:-$FRAMES}; mkdir -p "$FR"
for k in $(seq 0 $((PROCS-1))); do
  KIT_DEVICE=${KIT_DEVICE:-GPU} KIT_FMT=PNG KIT_PERSIST=${KIT_PERSIST:-0} nohup $PY $SCENE anim $RX $RY "$SPP" "$FR" $((F0+k)) "$F1" "$PROCS" > logs/render_$k.log 2>&1 &
done
sleep 1; echo "started $PROCS procs, spp=$SPP, frames $F0-$F1 of $FRAMES -> $FR"
