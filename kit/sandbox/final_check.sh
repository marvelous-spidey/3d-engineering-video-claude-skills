#!/bin/bash
# final_check.sh <url of final mp4> <md5 from the box> [lang]: independent check of the uploaded file, run in the sandbox job folder
# (next to asr.py, sync_check.py, script.txt, asr_proc.json and words.json from the voice-over step)
cd "$(dirname "$0")" && rm -f final.mp4 asr_final.json
curl -fsSL -o final.mp4 "$1" && ls -la final.mp4 && m=$(md5sum final.mp4 | cut -d' ' -f1) && echo "md5 $m $([ "$m" = "$2" ] && echo MATCH || echo DIFFERENT)"
ffprobe -v error -show_entries stream=codec_name,width,height,r_frame_rate,pix_fmt,color_space,nb_frames,sample_rate,channels:format=duration,size -of compact=p=0:nk=0 final.mp4 | tr '\n' ' '; echo
ffmpeg -hide_banner -nostats -i final.mp4 -af ebur128=peak=true -f null - 2>&1 | grep -E "^\s+I:|Peak:" | tr -s ' ' | tr '\n' ' '; echo
python3 asr.py final.mp4 asr_final.json ${3:-id} && python3 sync_check.py
echo FINAL_CHECK_DONE
