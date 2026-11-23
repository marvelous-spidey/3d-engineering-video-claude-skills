#!/bin/bash
# vo_final.sh - voice-over track for the mix: OFFSET seconds of silence, then vo_proc.wav, padded to the video length (stereo, 48 kHz)
. "$(dirname "$0")/job.sh"
ffmpeg -y -loglevel error -i vo_proc.wav -af "adelay=$(awk "BEGIN{printf \"%d\", $OFFSET * 1000}"):all=1,apad=whole_dur=$DUR" -ar 48000 -ac 2 vo_final.wav
echo "vo_final.wav $(ffprobe -v error -show_entries format=duration -of csv=p=0 vo_final.wav) s (video: $DUR s, $FRAMES frames)"
