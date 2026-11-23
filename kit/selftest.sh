#!/bin/bash
# selftest.sh - end-to-end check of the kit at small scale, on CPU, without Higgsfield credits (3 to 10 minutes in the Claude workspace, where three processes share two CPU cores and limited memory).
# Makes a job folder from the demo, renders a 0.4 s video (12 frames, 1080x1920, 4 samples) with three interleaved processes, then runs
# the same finish.sh as a real job: frame scan, captions + final video, clean master, probes, QA sheets, colour check.
# usage: bash selftest.sh [work_dir]        needs python3 with bpy, pillow, numpy and ffmpeg. Ends with SELFTEST PASSED or the failed check.
K="$(cd "$(dirname "$0")" && pwd)"; J=${1:-/tmp/kit_selftest}; rm -rf "$J"
mkdir -p "$J" && cp "$K"/demo/* "$J"/ && bash "$K/newjob.sh" "$J" > /dev/null && cd "$J" || { echo "SELFTEST FAILED: job folder"; exit 1; }
export PY=${PY:-python3} FR=$J/frames QA=$J/qa KIT_DEVICE=${KIT_DEVICE:-CPU} SPP=4 WORDS_JSON=words_fast.json TAIL=0.0
ffmpeg -y -loglevel error -f lavfi -i "sine=frequency=330:duration=0.1" -ar 48000 -ac 1 vo_proc.wav && bash vo_final.sh || { echo "SELFTEST FAILED: voice-over track"; exit 1; }
. ./job.sh; echo "job $NAME: $DUR s, $FRAMES frames, $PROCS processes on $KIT_DEVICE"; t0=$(date +%s)
bash render.sh > /dev/null
for try in 1 2 3; do                       # a small workspace can kill one render process for memory: resume the missing frames one process at a time
  sleep 2; while pgrep -f "${PAT}anim" > /dev/null; do sleep 3; done
  [ "$(ls $FR | wc -l)" -ge "$FRAMES" ] && break
  echo "a render process stopped early ($(ls $FR | wc -l) of $FRAMES frames); resuming with one process"; PROCS=1 bash render.sh > /dev/null
done
bash finish.sh > logs/finish.log 2>&1
grep -E "RENDER_DONE|^wrote|codec_name|I:|colour check|COLOUR|frames analysed|suspects" logs/finish.log logs/post_video.log logs/post_clean.log | cut -c1-230
fail=""
[ "$(ls $FR | wc -l)" = "$FRAMES" ] || fail="$fail frames"
for f in $OUT $CLEAN; do [ "$(ffprobe -v error -select_streams v:0 -show_entries stream=nb_frames -of csv=p=0 $f 2>/dev/null)" = "$FRAMES" ] || fail="$fail $f"; done
grep -q "COLOUR OK" logs/finish.log || fail="$fail colour"
grep -q "frames analysed: $FRAMES" logs/finish.log || fail="$fail scan"
[ -s $QA/final_1.jpg ] && [ -s $QA/final_crops.jpg ] || fail="$fail sheets"
echo "took $(( $(date +%s) - t0 )) s; results in $J"
[ -z "$fail" ] && echo "SELFTEST PASSED" || { echo "SELFTEST FAILED:$fail"; tail -5 logs/render_0.log; exit 1; }
