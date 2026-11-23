#!/bin/bash
# newjob.sh - make a flat job folder from the kit: bash newjob.sh <job_dir>
# Copies the kit code (scene kit, captions, audio, box and sandbox tools) into one folder; the workspace, the sandbox and the GPU box
# all work in a folder like this. Adds job.env (from the example) and a scene script (from the template) when they are missing.
# Files that belong to the job (job.env, scene, words.json, script.txt, keywords.txt, audio) are never overwritten.
set -e; K="$(cd "$(dirname "$0")" && pwd)"; J="$1"; [ -n "$J" ] || { echo "usage: bash newjob.sh <job_dir>"; exit 1; }; mkdir -p "$J"
cp "$K"/explainer_kit.py "$K"/scene_extras.py "$K"/kitjob.py "$K"/captions.py "$K"/scene_check.py "$K"/audio/*.py "$K"/box/* "$K"/sandbox/* "$J"/
[ -f "$J/job.env" ] || cp "$K/job.env.example" "$J/job.env"
S=$(grep -E '^SCENE=' "$J/job.env" | head -1 | cut -d= -f2 | cut -d' ' -f1); [ -f "$J/$S" ] || cp "$K/scene_template.py" "$J/$S"
[ -f "$J/Baloo2.ttf" ] || { [ -f "$K/Baloo2.ttf" ] && cp "$K/Baloo2.ttf" "$J/"; } || curl -fsSL -o "$J/Baloo2.ttf" "https://raw.githubusercontent.com/google/fonts/main/ofl/baloo2/Baloo2%5Bwght%5D.ttf" || echo "Baloo2.ttf missing (needed for the cards caption style)"
echo "job folder: $J   scene: $S   kit: $(cat "$K/VERSION" 2>/dev/null)"
