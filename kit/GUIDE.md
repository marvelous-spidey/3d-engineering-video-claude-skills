# Kit v1.1 working guide: reference for the skills

Read one section at a time, when you need it. The commands here are for kit v1.1; what came out of video #3 is marked "v1.1". `docs/pipeline-runbook.md` (v0.3) in the repo is background and history, and its commands are from an older version.

## 1. Writing a scene

**Conventions.** Units are metres. The cut face is the plane y = 0, the camera looks along +Y, Z is up, and the ground is at z = 0. The lens is 36 mm on a 36 mm sensor, so the frame is as tall as the camera distance and 0.5625 times that wide. Keep the subject between 15% and 60% of the frame height. Captions sit at 67 to 70%, and platform buttons cover the bottom 20%. Name objects with a group prefix (`ENV_`, `PIPE_`, `TAG_`), because those names show up in the scan reports.

**Time.** Every cue is a variable `T_... = T(sentence_id, word, nth, end)`. The word must match the script exactly ("air" does not find "airnya"). No seconds are typed by hand; offsets are written relative to a cue (`T_PUMP - 0.4`).

**Picture rules.** One sentence is one change on screen. An object appears when it is named, not before. A technical term gets a tag when it is spoken. Draw cause and effect as motion: water flows, a level rises, a wall collapses, an arrow pushes.

**Vocabulary** (for arguments: `grep -n "^def " explainer_kit.py scene_extras.py`, or `API.md`):

| Need | Functions |
|---|---|
| Shapes | `box`, `cyl`, `sphere`, `prism`, `prismp`, `prism_yz`, `patch`, `patchp`, `tube`, `pipe`, `hinge`, `capsule`, `empty` |
| Appearing and disappearing | `hidden_until`, `appear`, `pop`, `vanish`, `grow`, `show`, `extend` (a pipe that draws itself) |
| Motion | `travel`, `key`, `pulse`, `key_input` (material values), `tint` (colour and alpha) |
| Water | `water_material`, `level_box` + `water_body` + `level` (a surface that rises and falls, correct even on a sloped floor) |
| Flow in a pipe | `flow(name, front(points), t0, t1)` |
| Text | `label(..., billboard=True)` for tags, `sign`, `text`; arrows: `arrow` |
| Characters | `make_char` (the series mascot: yellow helmet, orange vest), `arm`, `raise_arms`; set dressing: `tree`, `palm` |
| Camera | `orbit(azimuth, elevation, distance, target)`, `pose`, `shot(t0, t1, pose, mv=..., cut=...)`, `project(pose, point)` |
| World | `sun_d.energy` / `sun_d.color` and `sky` can be keyframed (dusk, overcast) |

**Camera.** `shot()` eases from the previous pose and then drifts slowly; `cut=True` makes a hard cut. Follow the style of the reference: a hard cut per beat (video #1) or one continuous move (video #2). Compute screen positions with `project()` before rendering, so that tags do not cover the subject and the subject does not fall into the caption area.

**Blender 5.3 keyframe rules that have ruined a render:**

1. Inserting a key on a frame that already has one **replaces** it. A looping motion that "reaches the end, then jumps to the start" must put the end key 0.004 seconds before the next loop (`flow()` already does).
2. The third and later keys inherit the interpolation of the key before them. After `show()` or `extend()` (CONSTANT keys), pass `ip` explicitly: `pulse(o, t0, t1, ip='BEZIER')`.
3. An automatic BEZIER handle next to a "hidden" key delays the motion. Use `ip='SINE', ease='EASE_IN_OUT'`.
4. Two coplanar surfaces render black: move one of them by 4 mm. For stacked transparency, use single-sided planes.
5. An object "growing" from zero scale is still visible as a thin sheet: hide it until its cue (`grow` and `pop` already do).
6. (v1.1) `pop(o, t)` puts its last key at `t + dur` (0.28 seconds by default). A `vanish()` that finishes before that loses: the object comes back and stays. For anything on screen for less than about 0.4 seconds (a counter that changes quickly), shorten `dur` on both `pop` and `vanish`, then read the timetable in `scene_check.py`.

**Patterns from video #3 (v1.1).** The code is in `examples/video03-crv-engine-id/engine_video.py`. The functions named below are defined in that script and are not in the kit yet.

- **Repeating mechanical motion** (an engine, a pump, gears): build one angle curve for the whole video, the integral of a speed profile per sentence, then compute every part's position from that angle and write one linear key per frame (`bake`, `bake_input`). The speed can change from sentence to sentence without breaking the relationship between parts. To make an event land exactly on a word, scale the angle travelled inside a time window (`land`); do not shift the phase. The engine must never be seen running backwards.
- **Rotating things at 30 fps** look frozen or reversed when the angle per frame approaches the spacing between spokes. Limit the revolutions per second, or use fewer spokes and holes.
- **Gauges and numbers fixed to the screen**: make them children of the camera at a fixed depth, turn off their shadows and reflections, and give them a common name prefix (for example `HUD_`). Reserve a strip of the screen for them (video #3: 8 to 25% from the top) and put the camera's focus point below that strip (`frame`). Size tags in the world by camera distance so they read the same in wide and close shots (`tag`).
- **Swapping parts**: the new part grows first, then the old one disappears. The other order leaves an empty hole for a few frames, and only a motion strip shows it.
- **Flames and flashes**: emission above about 3 clips in the Standard view transform (orange becomes yellow, yellow becomes white), and a flat colour reads as a solid object. Use a gradient and opacity, with the strength baked per frame. At its peak frame, a flash must be smaller than the space that contains it.
- **Numbers on screen come only from the fact-check table.** If there is no checked number, use a label without one (video #3: a temperature needle marked C and H).

**Check before the GPU.** Build the scene in mode `none` and print the keys of one sample object for each kind of motion: `[(k.co.x, k.co.y, k.interpolation) for c in fcurves_of(obj) for k in c.keyframe_points]`. For the camera, the position step per frame should rise and fall smoothly, with no single jump. Stills cannot show a wrong path.

(v1.1) `python3 scene_check.py <scene>.py` prints all of that in about 30 seconds without rendering: the size of the scene, the largest camera steps and any single-frame jumps, when each object fixed to the screen is visible (`COMES BACK`, `STAYS TO THE END`), and a list of flashes, meaning objects whose size peaks for only one or two frames, with the second of each peak. Run it every time the scene script changes, including after a small fix in the middle of a render. In video #3, one fix left a label on screen, and one oversized flash got past every still.

**Complete examples** are in the repo's `examples/` folder (read the part you need with `grep`, not the whole file): `video02-swimming-pool-id/pool_video.py` (water, pipes, flow, dusk, one camera move), `video03-crv-engine-id/engine_video.py` (a turning engine baked per frame, boolean cuts, on-screen gauges, part swaps), and `video01-septic-system-en/septic_video.py` (hard cuts, labels on the cut face, a truck; a standalone script from before the kit existed).

## 2. Previews on CPU

```bash
python3 <scene>.py still 270 480 4 st/r1 <second of each cue>      # 2 to 3 seconds per still
python3 captions.py test st/r1/t_00360.png 3.6 st/r1/c_00360.png   # caption on top of a still
python3 <scene>.py still 540 960 12 st/hi <key seconds>            # colour and text, about 20 seconds per still
```

Build a contact sheet and look at it yourself: composition, objects that appear too early, readable labels, captions that do not cover the subject. Later rounds cover only the moments that had problems. Judge colour at 12 samples or more; 4 samples with denoising is misleading. The first two videos took 4 to 5 rounds, and video #3 took 6.

(v1.1) Two more kinds of still before the GPU:

- **Motion strips**: 5 to 7 consecutive frames (270x480) around every part swap and every object that enters or leaves. An empty hole, or an object that shows for an instant before its time, is visible only here.
- **Peak frames**: one full-size still at the exact peak second of each kind of flash that `scene_check.py` prints. A still taken "around the word" shows the dim phase.

Mode `list` renders specific frame numbers: `python3 <scene>.py list 270 480 4 st/mo frames.txt` (a file of frame numbers separated by spaces).

## 3. Voice, per language

| Language | Default voice | Measured pace | Notes |
|---|---|---|---|
| English | Eleven v4, preset Cillian | about 2.7 words per second | 171 words = 64 seconds, used without a tag |
| Indonesian | Eleven v4, preset Marcus, text prefixed with `[quick, energetic pace] ` | about 6.3 syllables per second after processing | only 4.6 without the tag; Indonesian runs at about 2.2 syllables per word |

Eleven v4 has no speed control and no language parameter; the language follows the text. It costs about 0.47 credits per 100 characters per take. `vo_prep.py` tightens the pauses and speeds the audio up by at most 1.10x. Audition (optional): the same two sentences for 4 voices, `audition.py ref.txt <lang>`, then the user chooses by ear.

(v1.1) Notes on Indonesian from video #3 (199 words, one take: 78.5 seconds raw, 74.0 after processing):

- The transcription engine writes numbers as digits, so number words ("seribu tiga puluh delapan") get their timing by interpolation in `align.py`. That is good enough for captions. Do not hang a cue that must be exact on a word in the middle of a run of numbers.
- An abbreviation spelled without vowels ("CR-V") is counted as one syllable and gets too short a share of the time. Compare it with the raw timings in `asr_proc.json` and correct `words.json` with a small script kept in the job folder (example: `examples/video03-crv-engine-id/patch_words.py`), before you start writing the scene.
- `estimate_audio_cost` for `elevenlabs_v4` asks for a `dialogue` field. If it rejects the call, use the measured rate above.

## 4. Reading the frame scan

`scan.py` flags frames that stand out from both of their neighbours. Legitimate: a fast camera move, a small object crossing quickly (flow dots, splashes), the overshoot of a tag that has just appeared (larger for one frame), a repeating pattern as the camera starts to move. Defects: an object that is black or left behind on the frames of one process only (stale state: make sure `KIT_PERSIST=0`), or an object that shoots off its path (an animation bug: see the keyframe rules). Warning signs in the summary: suspects piling up in one process, or a black-pixel spike on a single frame. Look at the strongest suspects with `trip_png.py` (PNG frames) or `sandbox/trip.py` (a finished video).

(v1.1) **Repeating motion** (a turning engine, combustion flames) produces dozens of legitimate periodic suspects: 104 of 2,277 frames in video #3. When the period is a multiple of the number of processes, those suspects pile up in one process and look like a stale-state defect. Tell them apart by their period and their position on screen, then look at one example of each group. A black-pixel spike that repeats twice per revolution in the same place is a legitimate dark gap. A flash that pokes through the wall of its container for one frame, on the other hand, is a real defect, and the scan flags it: look at the peak frame of each group of flashes.

## 5. Operational pitfalls

| Symptom | Cause | Fix |
|---|---|---|
| A sandbox or box call returns "Bad Gateway" | it waited longer than about 60 seconds | `background:true` or `nohup ... &`, then short polls; check the state before repeating |
| A command dies with code 143 | `pkill -f "pattern"` killed its own shell | bracket the pattern: `pkill -f "[p]ool_video.py anim"` (`job.sh` provides `$PAT`) |
| Setup runs twice | `a && b && nohup c &` puts the whole chain in the background | run short steps one at a time; use `nohup` only for the long command |
| A second PUT to a presigned URL is refused | the URL is single-use and needs the header `If-None-Match: *` | request a new URL for every upload (`up.sh` already sends the header) |
| The video is darker than the frames | RGB to YUV used BT.601 although the file is tagged BT.709 | `captions.py` uses the filter `scale=out_color_matrix=bt709`; `qa_final.py` prints `COLOUR OK` |
| 10 Hz flicker, black objects on a third of the frames | `use_persistent_data` in a multi-process render | leave `KIT_PERSIST=0`; scan every frame |
| The contact sheet is clean but the video flickers | every sample fell on the same process | `qa_final.py` takes frames from all processes |
| Whisper garbles the start of the audio | the script was passed as `initial_prompt` | give no prompt; the text always comes from the script |
| The first word after a full stop appears too early | Whisper puts the start of the word inside the previous one | `align.py` v1.0 snaps it to the end of the pause; make sure the line "words that span a pause" is empty |
| A three-frame crop is off by one frame | `ffmpeg -ss` returns the first frame at or after the time | ask for `(f-1)/fps - 0.012` (the kit tools already do) |
| The render slows down while a QA tool runs | the box has 4 vCPUs and three render processes use about 3.3 | one analysis tool at a time, with `nice` |
| (v1.1) Upload refused with `ExpiredToken` | upload URLs work for only about one hour after they are issued, even though `X-Amz-Expires` is longer | request the URLs when the render has about 10 minutes left; `after.sh` waits for `urls.sh` to appear |
| (v1.1) A control frame differs after a partial re-render | the fix changed something outside the re-rendered ranges (a label left behind, an object that comes back) | pick control frames just after each range; run `scene_check.py` before `rerender.sh` |
| (v1.1) The whole kit had to be retyped into the sandbox | the workspace cannot upload to Higgsfield | the sandbox and the box fetch the kit with `git clone` from the public repo; only job files are sent as text |
| A reference file changes when copied | it went through `/mnt/user-data/outputs` (C2PA manifest) | do not pass third-party files through there |

## 6. Reference numbers

| Item | Video #1 (66 s, 710 objects) | Video #2 (68.4 s, 834 objects) | Video #3 (75.9 s, 771 objects) |
|---|---|---|---|
| CPU still, 270x480, 4 samples | 2 to 3 seconds | 2 to 3 seconds | 11 to 15 seconds at 405x720 (metal, booleans, area lights) |
| Box setup | about 80 seconds | about 3 minutes (ran twice by mistake) | about 2 minutes |
| Render, 3 processes on 1x L40S | 1.2 fps (persistent data on) | 0.74 fps (persistent data off, now the default) | 0.60 fps; about 262,000 keys, one per frame for every moving part |
| Captions + encode + clean master | about 3 minutes | 2 minutes 38 seconds | 2 minutes 36 seconds |
| Box running time | 37 minutes = 43.72 credits | 1 hour 52 minutes = 132.29 credits, including one discarded render and one partial re-render | 1 hour 34 minutes = 110.90 credits, including two partial re-renders (about 26) |
| Voice | 4.37 credits | 16.66 credits (audition + 2 takes) | 6.44 credits (1 take) |

Net estimate: box minutes are roughly frames / 0.74 / 60 + 15. With an L40S at 71 credits per hour, a 68-second video costs about 75 credits. A scene with many keys per frame or many curve objects is slower: divide by 0.6. Render speed is limited by the box's CPU (4 vCPUs). The GPU is only 30 to 50% busy, so a more expensive GPU does not make it faster. A test still on the box (about 2.5 seconds, one process) does not represent the speed of the full render (about 5 seconds per frame per process when three run together), so project again from the first 2 to 3 minutes of the render.
