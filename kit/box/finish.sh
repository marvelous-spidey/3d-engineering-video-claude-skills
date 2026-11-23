#!/bin/bash
# finish.sh - waits for all frames, then: frame scan + final video + clean master (in parallel), probe, loudness, QA sheets, colour check.
# usage: nohup bash finish.sh > logs/finish.log 2>&1 &        done marker: logs/finish.done      (start it while the render is still running)
. "$(dirname "$0")/job.sh"; rm -f logs/finish.done; mkdir -p "$QA"
while [ "$(ls $FR 2>/dev/null | wc -l)" -lt "$FRAMES" ] || pgrep -f "${PAT}anim" > /dev/null; do sleep 5; done
echo "RENDER_DONE $(date -u +%H:%M:%S) files=$(ls $FR | wc -l) small=$(find $FR -name 'f_*.png' -size -200k | wc -l)"
grep -h "ANIM" logs/render_*.log
$PY captions.py video $FR vo_final.wav $OUT > logs/post_video.log 2>&1 &
$PY captions.py clean $FR $CLEAN > logs/post_clean.log 2>&1 &
nice -n 5 $PY scan.py $FR $QA/scan $FRAMES $PROCS > logs/scan_final.log 2>&1 &
wait
echo "ENCODE_DONE $(date -u +%H:%M:%S)"; tail -1 logs/post_video.log; tail -1 logs/post_clean.log
for f in $OUT $CLEAN; do ffprobe -v error -show_entries stream=codec_name,width,height,r_frame_rate,pix_fmt,color_space,color_range,nb_frames,sample_rate,channels:format=duration,size -of compact=p=0:nk=0 $f | tr '\n' ' '; echo; done
ffmpeg -hide_banner -nostats -i $OUT -af ebur128=peak=true -f null - 2>&1 | grep -E "^\s+I:|Peak:" | tr -s ' ' | tr '\n' ' '; echo
md5sum $OUT $CLEAN
$PY qa_final.py $OUT $QA/final $FR $CLEAN && (cd $QA && rm -f sheets.zip && $PY -m zipfile -c sheets.zip final_1.jpg final_2.jpg final_3.jpg final_crops.jpg && ls -la sheets.zip)
cat logs/scan_final.log
echo "FINISH_DONE $(date -u +%H:%M:%S)"; touch logs/finish.done
