#!/bin/bash
# setup.sh - one-time setup on a rented GPU box: Blender as a module (bpy 5.3) on Python 3.13, ffmpeg, fonts, final voice-over track.
# usage (in the job folder; needs job.env, words.json, vo_proc.wav):  mkdir -p logs; nohup bash setup.sh > logs/setup.log 2>&1 &     done marker: SETUP_DONE
cd "$(dirname "$0")" && mkdir -p logs
export DEBIAN_FRONTEND=noninteractive
echo "== apt"; (apt-get update -qq && apt-get install -y -qq ffmpeg fonts-inter fontconfig curl ca-certificates libgl1 libegl1 libxrender1 libxxf86vm1 libxfixes3 libxi6 libxkbcommon0 libsm6 libice6 libgomp1) 2>&1 | tail -3
echo "== uv + python 3.13 + bpy"
(command -v uv >/dev/null) || (curl -LsSf https://astral.sh/uv/install.sh | sh) 2>&1 | tail -1
export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"
uv venv --python 3.13 /root/venv313 2>&1 | tail -1
uv pip install --python /root/venv313/bin/python bpy==5.3.0 pillow numpy 2>&1 | tail -2
/root/venv313/bin/python -c "import bpy; print('bpy', bpy.app.version_string)" 2>&1 | grep -v -i warn | tail -1
echo "== fonts"; fc-list | grep -i "Inter" | grep -i "Bold" | grep -v -iE "Italic|Display|Extra|Semi" | head -2
[ -f Baloo2.ttf ] || curl -fsSL -o Baloo2.ttf "https://raw.githubusercontent.com/google/fonts/main/ofl/baloo2/Baloo2%5Bwght%5D.ttf"
md5sum Baloo2.ttf | cut -c1-12
echo "== voice-over"; bash vo_final.sh
echo "SETUP_DONE"
