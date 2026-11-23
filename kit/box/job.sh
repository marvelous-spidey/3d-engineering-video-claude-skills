# job.sh - sourced by the box scripts: job.env, defaults, and the numbers kitjob.py derives from words.json (DUR, FRAMES)
cd "$(dirname "${BASH_SOURCE[0]}")"
while IFS= read -r line; do                 # KEY=VALUE lines of job.env; a variable that is already set in the environment wins
  [[ "$line" =~ ^[A-Za-z_][A-Za-z0-9_]*= ]] || continue
  k=${line%%=*}; [ -n "${!k+x}" ] && continue
  v=${line#*=}; v=${v%%[[:space:]]#*}; v="${v%"${v##*[![:space:]]}"}"; export "$k=$v"
done < job.env
PY=${PY:-/root/venv313/bin/python}; FR=${FR:-/root/frames}; QA=${QA:-/root/qa}; PROCS=${PROCS:-3}; SPP=${SPP:-64}; RX=${RX:-1080}; RY=${RY:-1920}; OFFSET=${OFFSET:-0.30}
KPY=$PY; [ -x "$KPY" ] || command -v "$KPY" > /dev/null || KPY=python3
read DUR FRAMES FPS <<< "$($KPY kitjob.py)"
OUT=$NAME.mp4; CLEAN=${NAME}_clean_master.mp4
PAT="[${SCENE:0:1}]${SCENE:1} "            # pgrep/pkill pattern that never matches the shell that runs it
export PY FR QA PROCS SPP RX RY OFFSET DUR FRAMES FPS OUT CLEAN
mkdir -p logs
