# Runbook: short 3D engineering explainers with Claude + Higgsfield

Version 0.3, 22 November 2026. Written from two productions: video #1 (English, septic system) and video #2 (Indonesian, swimming pool). Parts that have never been run are marked **[planned]**.

This document was the raw material for the skills: it has triggers, inputs, steps, checks, limits and reference numbers. Its purpose was to let a new session repeat a production without reading the chat history.

> **Note for readers of this repo.** This document records how the work was done up to video #2, before kit v1.0. The current workflow is in `skills/` and `kit/GUIDE.md`. The commands here are from the older version, and the file names follow the original working layout (section 2 maps them to this repo). The most useful parts to read are the principles (section 3), the limits of each workplace (section 4), the credit rules (section 5) and the list of pitfalls (section 9).

## 1. When to use it

- Use it for: a short vertical video of 60 to 75 seconds that explains how a machine or engineered system works through a 3D cutaway, with AI narration and word-by-word captions.
- Do not use it for: presenter videos, videos made entirely by an AI video generator, or topics with no mechanism that has to be drawn precisely.

| Input | Required | Notes |
|---|---|---|
| Topic | yes | one mechanism, not a list of facts |
| Narration language | yes | sets the word budget and the voice model |
| Reference video | no | analysed first (step 1) |
| Hook sentence | no | if given, used as written |
| Credit limit | yes, before any paid step | per item: voice, GPU |

Output: an MP4 at 1080x1920 and 30 fps (a link), a clean master without captions or sound, the scene script, the script with its fact-check table, a production record, and an archive in the Project and the local folder.

## 2. Document map

This document was written when the files still lived in a claude.ai Project (prefix `claude/`) and in a local folder. Their equivalents in this repo:

| Called here | In this repo |
|---|---|
| `kit/...`, `kit_explainer_kit.py`, `kit_tools.md`, `tools/ref_teardown.py` | the `kit/` folder (the reference teardown tool is `kit/ref_teardown.py`) |
| `video01/...`, `video01_septic_video.py`, `script_en.md` | `examples/video01-septic-system-en/` |
| `video02/...`, `video02_pool_video.py`, `script_id.md` | `examples/video02-swimming-pool-id/` |
| `post.py` (captions and encoding, one per video) | replaced by `kit/captions.py` |
| `video01-production-record.md`, `video02-production-record.md`, `video02-reference-analysis.md` | the `docs/` folder |
| `worklog.md`, `production-plan.md`, `video02-plan.md`, `poc_scene.py` | working notes, plans and the first proof of concept; not included in the repo |

## 3. Principles

1. **Code is the source of truth.** The scene, the animation, the captions and the render all come from scripts. A revision means changing the script and rendering again.
2. **Audio first, picture follows.** Every animation cue is computed from the timing of a word in the voice-over, never typed by hand.
3. **Measure, do not guess.** Claude cannot hear, and cannot watch motion. What it reports are measurements and frames. Judgments of taste go to a human at a review gate.
4. **Cheap first, expensive last.** Low-resolution CPU stills, then a few test frames on the GPU, then the full render.
5. **Credits only with explicit approval** (section 5).
6. **Original work.** Only the format grammar is taken from a reference. The script is written from sourced facts; the order, the analogies, the set and the characters are our own.
7. **Clean stills do not prove a clean animation.** Every rendered frame is checked automatically before encoding (step 8). In video #2 that check found defects that no still had shown.

## 4. Workplaces and their limits

| Place | Used for | Important limits |
|---|---|---|
| Claude's workspace (cloud) | writing code, `bpy` 5.3.0 on Python 3.13 with Cycles on CPU, ffmpeg, OCR, documents | 2 CPU cores, no GPU. Internet access is limited to package registries, GitHub and `raw.githubusercontent.com`. It cannot reach `upload.higgsfield.ai` or the Higgsfield CDN. Working files are lost when the session ends |
| `/mnt/user-data/outputs` | files sent to the chat or committed to the local folder | media files here get a C2PA manifest added, so third-party files must not pass through |
| Higgsfield sandbox (`sandbox_exec`) | passing scripts along, faster-whisper, audio processing, downloading and uploading Higgsfield media, viewing images from the box | free. It lasts about 24 hours and can restart at any time (files stay, processes are lost). A call longer than about 60 seconds can fail with "Bad Gateway": use `background:true` and poll. Images returned to Claude are limited to 4 files and 512 KiB in total |
| Rented GPU box | rendering, captions, encoding, frame QA | billed per second. A `gpu_rental_exec` call that waits longer than about 60 seconds can fail with "Bad Gateway". `/workspace` persists between rentals (the video #1 folder was still there a day later); `/root` is lost when the box stops. By default 4 vCPUs, and no ffmpeg, uv or unzip |
| The user's computer through the desktop bridge | the archive in a connected folder | what runs there is a Linux VM, not macOS. It cannot reach the Higgsfield CDN, so the MP4 cannot be downloaded into the folder |
| claude.ai Project | documents and scripts that last across sessions | every write replaces one whole document |

Practical consequences:

- A script goes from the workspace to the box through the sandbox: paste it into the sandbox (heredoc, parts of at most 25 KB, md5 checked for each part), zip it, `media_upload`, PUT to the presigned URL from the sandbox, `media_confirm`, and the box downloads the read URL.
- A script written directly in the sandbox or on the box (audio tools, QA tools) can only come back to the workspace as text: `cat` it, write it again in the workspace, and compare the md5.
- The final video can only be delivered as a Higgsfield link. The user downloads it from the link.
- To look at frames rendered on the GPU: the box builds a JPEG contact sheet, zips it, uploads it to one presigned URL, and the sandbox unpacks the zip and returns 3 or 4 images per call.
- A presigned URL is about 1.8 KB long, must be copied exactly, and **can be used only once** (it is signed with `If-None-Match: *`, and the PUT must carry that header). Keep the URLs as variables in one file on the box (`urls.sh`) so later commands stay short.

## 5. Credit rules

1. Estimate first with the free tools (`estimate_audio_cost`, `gpu_list_gpus`, `balance`), show the numbers, then ask for explicit approval with a hard limit.
2. Approval covers one job. Renting a GPU again needs new approval of its hourly price.
3. Before the full render, measure the seconds per frame on a few test frames and project the cost. If it exceeds the limit, stop and ask.
4. Shut the box down (`gpu_rental_stop`) as soon as the final file is uploaded and verified. Check the real cost in `transactions` and record it in the worklog. The "GPU Rental" transaction keeps growing while the box is on.
5. If the user asked for "a plan first", make no generate or rent call at all.
6. If something found along the way forces rework (a re-render, for example), recalculate the projection against the limit and tell the user right away. While the box is on, do only work that needs the box; documents are written after it is off.

## 6. Steps

### Step 0: Brief

Record the topic, the language, the reference, the hook and the user's decisions. State any assumption you made (the narration language, for example) in the first line of the plan.

### Step 1: Reference teardown

Goal: a measured style specification and a list of what is taken and what is not.

```bash
T=tools/ref_teardown.py
python3 -I $T probe    ref.mp4
python3 -I $T sheets   ref.mp4 out/sheets 1 6 6        # look at the contact sheet, find the caption band
python3 -I $T captions ref.mp4 out/cap <top_px> <height_px> 15
python3 -I $T pace     out/cap/ocr_words.json transcript.txt   # transcript cleaned by hand, sentences separated by '|'
python3 -I $T motion   ref.mp4
python3 -I $T audio    ref.mp4
```

- Look at the contact sheet yourself, and at 6 to 8 larger key frames, to read the visual language.
- The transcript of the reference is a working file only. Do not archive or share it. What is documented is the function of each beat, its word count and its timing.
- Result: a teardown document with the measured numbers, the beat structure, the visual language, a comparison with your own video, and the limits of the analysis. Example: `video02-reference-analysis.md`.

### Step 2: Research and fact check

- Find primary or institutional sources (video #1: EPA; video #2: CDC, manufacturer documents, pool-industry media).
- Table: claim in the script, source, simplification chosen. Localise numbers and terms for the audience (for Indonesia, concrete that is "cast", not "sprayed").
- Your own calculations are allowed as long as they are marked as calculations and their assumptions are written down.
- The final table is saved with the script in `videoNN/script_<language>.md`, together with the list of deliberate simplifications in the pictures.

### Step 3: Script

- Structure: hook (the simplest version of something complicated), then a chain of problems and solutions, one surprising fact, and a payoff that repeats the hook.
- One sentence is one change on screen. A technical term is named after its function is clear.
- Second person.
- Numbers are written as words, with no abbreviations; an ellipsis marks a pause.
- Word budget, measured:

| Language | Voice | Script | Voice-over length | Pace |
|---|---|---|---|---|
| English | Eleven v4, preset Cillian | 171 words | 64.4 seconds raw, used as is | about 2.6 words per second |
| Indonesian | Eleven v4, preset Marcus, no tag | 188 words, 422 syllables | 92.3 seconds raw (too slow) | about 4.6 syllables per second |
| Indonesian | the same, with the tag `[quick, energetic pace]` | the same | 78.4 seconds raw, 66.5 seconds after processing | about 6.3 syllables per second in the final result |

- Indonesian needs about 2.2 syllables per word, so the same content takes longer than in English. Count in syllables.
- A modular script: mark the lines that may be cut, and in what order, so the duration can be fitted once the voice-over exists. The rule in video #2: choose the longest variant that still fits in 70 seconds with the audio sped up by at most 1.10x.
- Save the script line by line with IDs (`S01`, `S02`, ...), one line per sentence-picture, as `S01|text`.

### Step 4: Voice

- Catalogue: `models_explore` with `type: audio`. Voices: `list_voices` (names and IDs only).
- `generate_audio` with model `elevenlabs_v4`, one `dialogue` turn with `voice_type: preset` and a `voice_id`, `use_unlim: false`. The result is an MP3 on the Higgsfield CDN. Real cost: 4.37 credits for about 1,000 characters; 5.98 credits for about 1,280 characters.
- Eleven v4 has no speed control, and the Higgsfield wrapper has no language parameter; the language follows the text. Pace is set with a tag at the start of the text: `[quick, energetic pace] ` makes the reading about 15% faster and is not read aloud.
- **Audition** when the language or the voice is new: the same 2 sentences (about 215 characters) for 4 or 5 voices, measured with `kit/audio/audition.py`: syllables per second, total pause time, how many words the transcription engine recognises, pitch, loudness. Video #2: 4 Eleven v4 presets at 1.15 credits each plus one Qwen clip at 0.1 credits. The choice should still be made by the user's ear; the measurements only narrow the field.
- **Process the audio** with `kit/audio/vo_prep.py <target_seconds> <raw.mp3>`: shorten every pause above 0.12 seconds to `min(0.30, 0.12 + 0.22 x (L - 0.12))`, speed up by at most 1.10x (`atempo`), raise to -13 LUFS, then limit at 0.84 (result about -14.4 LUFS), output 48 kHz mono.
- On the box, `setup.sh` adds a 300 ms lead-in and pads the track to the video length (`vo_final.wav`, stereo).
- Do not make a new take without need: a full take costs about 6 credits. Video #2 used 16.66 voice credits of a limit of 20.

### Step 5: Word timings

Always from the processed audio, in the Higgsfield sandbox:

```bash
python3 asr.py vo_proc.wav asr_proc.json     # faster-whisper small, language="id", word_timestamps, NO initial_prompt
python3 align.py                             # -> words.json {"dur", "words": [[sentence ID, word, start, end], ...]}
```

- The transcription supplies only the timings; the text comes from the script (matched with `difflib`). Words that were not recognised share their gap by syllable count, and word starts and ends are snapped to real pauses of 0.10 seconds or more.
- Video #2: 188 words, 15 interpolated, 43 snapped to a pause. The differences the engine reported were only spelling ("katub", "50").
- Check: the word count equals the script, times always increase, and no word is shorter than about 40 ms.
- `words.json` is used as is by the scene script and the caption script. `OFFSET` is the lead-in before the voice-over in the mix (0.30 seconds).

### Step 6: Scene and animation

- One Python file builds the whole scene. Its first lines set `FPS` and `OFFSET`, load `words.json`, compute `DUR`, then `exec(open('explainer_kit.py').read())`. Its last line is `render_main()`.
- Units are metres. The cut face is at y = 0, the camera looks along +Y, Z is up.
- Camera: a 36 mm lens on a 36 mm sensor. Half the frame height is 0.5 x the distance; half the width is 0.28125 x the distance. `project(pose, point)` computes where a point lands on screen before rendering.
- Every cue is a variable `T_...` from `T(sentence_id, word, nth, end)`. Cues survive a script revision or a change of language as long as the anchor word is still there. The word must match exactly ("air", not "airnya").
- Animation vocabulary: appear, vanish, grow, show and hide, travel along a path, a pipe that extends, a material value that changes, flow dots that loop in a pipe, a water surface that rises and falls.
- Camera: `shot(t0, t1, pose, ...)` eases to a pose and then drifts slowly. Video #2 uses one continuous move with no hard cuts; `orbit(azimuth, elevation, distance, target)` gives the poses.
- 3D text: the font is loaded explicitly (Inter Bold), and a tag's plate follows the width of its text.
- Techniques proven in video #2:
  - Water on a sloped floor: a water prism with a boolean INTERSECT against an invisible "level box" that is animated up and down.
  - Groundwater: a plane in front of the soil section whose alpha depends on world height (Z) compared with one keyframed Value node.
  - Objects that move with the shell: parented to one empty with `matrix_parent_inverse`.
  - Two coplanar surfaces render black: move one of them by 4 mm.

### Step 7: Previews on CPU

```bash
python pool_video.py still 270 480 4  stills/r1 2.0 14.3 21.3 37.6    # composition and timing
python pool_video.py still 540 960 12 stills/hi 37.6 61.5             # colour and text, about 20 seconds per still
python post.py test stills/hi/t_03760.png 37.6 cap.png                # test the caption on one frame
```

- Round 1: one still per important cue, at low resolution. Check the composition, what is visible before its time, whether labels are readable, and the space for captions.
- Later rounds: only the moments with problems, then raise the resolution.
- Judge colour at 12 to 16 samples or more. 4 samples with denoising is misleading.
- Video #1 took 4 rounds and about 300 stills; video #2 took 5 rounds.
- A still tests the state at one moment only. Interpolation mistakes (an object that starts moving late, a CONSTANT key carried over) show up only when stills are taken close together around a change, and path mistakes (flow dots going the wrong way) do not show in stills at all. For looping motion, print the list of keys (section 7) before renting the GPU.

### Step 8: Render on the GPU

1. `gpu_list_gpus`, show the price, ask for approval (section 5).
2. `gpu_rent`: kind `compute`, `L40S`, 1 GPU, `auto_pause_minutes` 30. The status `working` appears within about 10 seconds.
3. Send the kit through the sandbox (section 4): the scene script, `explainer_kit.py`, `words.json`, `post.py`, the caption font, `vo_proc.wav`, `setup.sh`, `render.sh`. The box has no `unzip`: `python3 -c "import zipfile; zipfile.ZipFile('kit.zip').extractall('.')"`.
4. `nohup bash setup.sh > logs/setup.log 2>&1 &` (about 80 seconds when it runs once; about 3 minutes in video #2 because it ran twice by mistake): apt (ffmpeg, fonts, GL libraries), `uv`, a Python 3.13 venv, `bpy==5.3.0`, pillow, numpy, `vo_final.wav`. It is done when the log contains `SETUP_DONE`.
5. Test a few stills at 64 samples (`still 1080 1920 64 ...`), look at them, note the seconds per frame, and project the cost.
6. `FR=/root/frames bash render.sh 3 64`: three processes, each taking every third frame, with **persistent data off** (`KIT_PERSIST=0`, the kit default since video #2). Existing files are skipped, so the render can be resumed.
7. Monitor with short commands only: `ls /root/frames | wc -l`, `tail -2 logs/render_0.log`.
8. **Scan the frames** during the render and after it: `python scan.py /root/frames /root/qa/scan`. A healthy result is zero suspects, or suspects that turn out to be legitimate fast motion. Look at the strongest suspects with `trip_png.py` (the suspect frame between its two neighbours). In video #2 the scan caught two different things: a render defect (black objects in one process) and an animation mistake in the script (flow dots shooting across the picture). When in doubt about whether a suspect is a render defect, render it again with mode `list` into another folder and compare with `compare.py`.
9. **Partial fix**: if the scene script is fixed, move the frames of the affected range to another folder and run `render.sh` again for that range (frames that still exist are skipped). Also re-render 2 or 3 frames outside the range and compare them with `diffall.py` to prove that the fix did not change anything else. Truncate the scan cache (`*_th.npy`, `*_bl.npy`) at the last unchanged frame.
10. The render is complete when the number of files equals the number of frames and there are no small files.
11. `nohup bash finish.sh` waits for the render to end and then runs the scan, both encodes, the probe and the contact sheets together. `nohup bash after.sh` waits for `finish.sh`, then uploads the final video, the clean master, the contact sheets and crops of the strongest suspects to the presigned URLs stored in `urls.sh`. Both are started while the render is still running, so the box never waits for the next command.

The render uses Cycles with OptiX, 64 samples with an adaptive threshold of 0.05, 4 bounces, OIDN denoising, the Standard view transform, PNG output.

**Why persistent data is off.** In video #2 the first render used `use_persistent_data = True`, as video #1 had. On about 20% of the frames, one of the three processes drew an object that had just changed (appeared, been hidden, grown) as a black shape, while the other two processes drew it correctly. The result was a 10 Hz flicker. No still ever showed it, and the first contact sheet caught only one of many defects, because all of its sample frames happened to belong to the same process. A fresh process that jumped straight to the same frame drew it correctly, and a re-render without persistent data matched the healthy frames to within 0.07 out of 255. The cost in time is about 20%: on the first 1,504 frames, rendered both ways, the speed was 0.77 frames per second without persistent data and 0.94 with it.

### Step 9: Captions and encoding

```bash
python post.py video /root/frames vo_final.wav <name>.mp4      # PIL captions -> rawvideo pipe -> libx264 CRF 17, AAC 192k
python post.py clean /root/frames <name>_clean_master.mp4      # no captions, no sound, CRF 15
```

- The output is written to `.part.mp4` and renamed once ffmpeg exits without an error. Both encodes can run at the same time.
- Caption style of video #1: Inter SemiBold at 66 px, cumulative phrases, at 67.5% of the screen height.
- Caption style of video #2 (`post.py` v2): one card of one or two words, Baloo 2 ExtraBold, white with a dark blue outline and a soft shadow, key words in yellow, a 3-frame pop-in, centred at 69.5% of the screen height, shrunk automatically when wider than 960 px. A word of 3 letters or fewer, or shorter than 0.13 seconds, is joined with the next word if they are spoken without a pause. 188 words became 164 cards; the shortest card lasts 0.14 seconds.
- The script text (for punctuation) and the key-word list are inside `post.py`. The script refuses to run if the script text and `words.json` differ.

### Step 10: QA

| Check | How | Passes when |
|---|---|---|
| Frame-to-frame consistency | `scan.py` on the PNG frames before encoding | there are no real suspects (see step 8) |
| Format | `ffprobe` | H.264 1080x1920, 30 fps, yuv420p, bt709; frame count and duration as expected; AAC 48 kHz |
| Loudness | the `ebur128` filter | -14 LUFS within 1; the peak does not touch 0 dBFS |
| Picture | `qa_final.py`: 36 frames from the final file, spread over all three process phases, plus 100% crops | no object at the wrong time, no flicker, no clipped caption |
| Consistency of the finished file | `scan_video.py` on the clean master in the sandbox (free, possible after the box is off), then `trip.py` for the strongest suspects | the number of suspects is comparable to the frame scan, they are spread evenly over the three processes, and there is no black-pixel spike that lasts a single frame |
| Sync | transcribe the audio of the final file again in the sandbox | the word count equals the script; word timing is within 0.05 seconds of the captions |
| Integrity | md5 of the file on the box and of the file downloaded again from the link | identical |
| Facts | read the fact-check table again against the narration and the on-screen text | no number has changed |

The contact sheet must take frames from every process phase. A time that is a multiple of 0.1 seconds always falls on a frame numbered 3k + 1, which belongs to the first process; use frame numbers such as 10 + 58k instead.

Always report the limits: no human has listened to the audio, no one has watched the motion, and what was not made (music, sound effects).

### Step 11: Handover and archive

1. Upload the final video and the clean master (`media_upload`, PUT, `media_confirm`), and keep the links and `media_id` values.
2. Shut the box down and record the real cost from `transactions`.
3. Write the production record (result, the route actually taken, measured numbers, corrections to the plan, lessons, file locations, what is still to do).
4. Project: the scene script, the caption script, the production record. Local folder: `videoNN/` with `README.md`, the scripts, `script_<language>.md` (script and fact check), `words.json`, the `.blend`, `box/`, `audio/`, `preview/`.
5. Update `worklog.md`, and this runbook if any step went differently.

## 7. Kit: the reusable functions

`kit/explainer_kit.py` is generated by `kit/make_kit.py` from the video #1 script (`python3 make_kit.py video01/septic_video.py explainer_kit.py`): the functions are copied as they are, the parts specific to video #1 are left out, and the cue lookup `T()`, mode `list` and persistent data off by default are added. A scene script uses it through `exec()` after setting `FPS`, `DUR`, `OFFSET` and `WORDS`.

| Group | Functions | Purpose |
|---|---|---|
| Time | `T(id, word, nth, end)`, `fr(t)` | the video time of a sentence or a word (`OFFSET` included); seconds to frame number |
| Keyframes | `key(obj, path, t, value, ip, ease)` | insert a keyframe at a time in seconds and set its interpolation |
| Verbs | `hidden_until`, `appear`, `vanish`, `grow`, `show`, `travel`, `extend`, `key_input` | hidden until a cue, appear by scaling up, vanish, grow from the base, hard show and hide, travel between points, a pipe that extends, animate a node value |
| Primitives | `box`, `tube`, `pipe`, `sphere`, `cyl`, `prism`, `patch`, `smooth_path`, `empty`, `link` | a box with a choice of origin, a tube through points, a sectioned pipe, a prism from a profile, a single-sided plane |
| Text | `text`, `label`, `sign`, `screen_to_world` | 3D text in Inter, a tag whose plate follows the text width (can face the camera), a sign, screen position to world position |
| Materials | `new_mat`, `bsdf_of`, `soil_material`, `grass_material`, `gravel_material` + 15 basic materials | base colours; soil layered by depth; grass; gravel |
| World | the sun `sun_d`, the sky `sky`, the background `bg`, the camera `cam` | can be keyframed (dusk in video #2, for example) |
| Camera | `pose`, `push`, `cam_key`, `shot`, `hero_pose` | a frontal pose, a push-in, a shot with a move and then a drift, an orbit pose |
| Modes | `still`, `anim`, `list`, `blend`; `KIT_DEVICE`, `KIT_FMT`, `KIT_PERSIST`, `SEPTIC_FONT` | stills at given seconds, a frame range with a step, a list of frames from a file, save a `.blend` |

Functions that still lived in the video #2 script and deserved to move into the kit for the next video: `prismp`, `prism_yz`, `hinge`, `arrow`, `pulse`, `level_box` / `level` / `water_body`, `water_material`, `tint`, `project`, `orbit`, `make_char` (the series mascot), `pop`, `flow`, `patchp`.

| Tool | Files | Purpose |
|---|---|---|
| Voice (sandbox) | `kit/audio/audition.py`, `vo_prep.py`, `asr.py`, `align.py` | measure audition clips; process the voice-over; timed transcription; `words.json` |
| Captions | `videoNN/post.py`: `video`, `clean`, `test`, `cards` | burn captions and encode, clean master, test one frame, list the cards |
| Box | `kit/box/setup.sh`, `render.sh`, `rerender.sh`, `finish.sh`, `after.sh`, `up.sh` | install the environment; parallel render; re-render frame ranges after a script fix; finish (scan, encode, probe, sheets); upload the results and suspect crops; PUT to a presigned URL |
| Frame QA | `kit/box/scan.py`, `trip_png.py`, `compare.py`, `diffall.py`, `sheets.py`, `qa_final.py` | find frames that differ from their neighbours; show a suspect next to its neighbours; compare a re-render; compare two renders; contact sheets from frames; contact sheets from the final file |
| QA of the final file (sandbox, free) | `kit/sandbox/final_check.sh`, `sync_check.py`, `scan_video.py`, `trip.py` | md5, format, loudness and word sync from the link; frame scan of a finished video; crops of three consecutive frames for each suspect |
| Reference | `tools/ref_teardown.py` | measure a reference video |

File names (`pool_video.py`, the output name, the duration of 68.4 seconds, 2,052 frames, frame ranges) were still written into `setup.sh`, `render.sh`, `rerender.sh`, `finish.sh`, `after.sh` and `qa_final.py` at this point; kit v1.0 replaced them with `job.env`.

Blender 5.3 notes that save time:

- The old `action.fcurves` is gone. F-curves are reached through `action.layers`, then `strips`, then `channelbag(slot)`.
- `keyframe_insert` ignores the interpolation preference; set the interpolation on the keyframe point after inserting it.
- A pipe that extends: animate `bevel_factor_end` on the curve.
- Text width: call `view_layer.update()`, then read `bound_box`.
- A tag that faces the camera: a `COPY_ROTATION` constraint to the camera, and `visible_shadow = False`.
- A cavity in the soil: a boolean with the EXACT solver, then `new_from_object`.
- Stacked transparency: `transparent_max_bounces = 16` and single-sided planes.
- The third and later keys on a curve inherit the interpolation of the key before them; only the first two keys use the BEZIER default. So after `show()` or `extend()`, which leave CONSTANT keys, the next key on the same property must be given `ip` explicitly. Otherwise a smooth motion becomes a jump.
- Inserting a key on a frame that already has one **replaces** it. A looping motion that "reaches the end, then jumps to the start" must put the end key slightly before the first key of the next loop (`flow()` uses 0.004 seconds).
- An automatic BEZIER handle next to a "hidden" key delays the motion. Use `ip='SINE', ease='EASE_IN_OUT'`.
- A quick way to check: build the scene in mode `none`, then print `(frame, value, interpolation)` from `fcurves_of(object)` for one sample object of each kind of motion.

## 8. Reference numbers

| Item | Video #1 (septic system, English) | Video #2 (swimming pool, Indonesian) |
|---|---|---|
| Scene | 710 objects, 902 lines | 834 objects, 517 lines + a 470-line kit |
| Duration, frames | 66.0 seconds, 1,980 | 68.4 seconds, 2,052 |
| CPU still in the workspace | 270x480, 4 samples: 2 to 3 seconds | the same; 540x960, 12 samples: about 20 seconds |
| Box setup | about 80 seconds | about 3 minutes (disturbed by a wrong command) |
| 1 process, 1080x1920, 64 samples + denoise | 1.7 to 1.9 seconds per frame | 1.3 to 1.7 seconds per frame |
| 3 processes on 1x L40S, persistent data on | 1,980 frames in 27 minutes 20 seconds (1.2 fps) | 0.90 to 0.95 fps, but about 20% of the frames defective |
| 3 processes, persistent data off | never run | 2,052 frames in 46 minutes 25 seconds (0.74 fps on average; 0.77 on the first 1,504 frames, 0.61 in the heavy final part); GPU at 99% |
| Captions + encode | about 3 minutes | 2 minutes 38 seconds for the final video and the clean master together |
| Total box running time | 36 minutes 57 seconds = 43.72 credits | 1 hour 51 minutes 47 seconds = 132.29 credits, including one discarded render (about 33 credits) and one partial re-render (about 20 credits) |
| Voice | 4.37 credits (1 take) | 16.66 credits (audition 4.70 + 2 takes at 5.98) |
| Total | 48.09 credits | 148.95 credits |
| Final file | 28.3 MB, -14.3 LUFS | 37.5 MB, -14.5 LUFS |

Prices at the time: L40S 71 credits per hour; Eleven v4 about 0.47 credits per 100 characters.

## 9. Pitfalls we have hit

| Symptom | Cause | Fix |
|---|---|---|
| An object is black or left behind on a third of the frames (10 Hz flicker) | `use_persistent_data` in a multi-process render: Cycles keeps stale state for objects whose transform changed | turn persistent data off (the kit default); scan every frame before encoding |
| The contact sheet is clean but the animation flickers | every sample frame fell on the same process (a time that is a multiple of 0.1 seconds is frame 3k + 1) | take frames from every phase; run `scan.py` |
| `scan.py` scores are high on many consecutive frames | a fast camera move, or an object that crosses more than one block per frame | not a defect; a real suspect is a frame that stands out from both neighbours |
| One frame stands out exactly when a label or tag appears | the overshoot of the appear animation lasts one frame | legitimate; confirm by measuring the label's edge over 5 consecutive frames: it widens to a peak and comes back |
| One frame stands out in a pile of spheres or a repeating pattern as the camera starts to move | a repeating pattern that shifts by half its spacing looks as if it "came back" on the next frame at thumbnail resolution | legitimate; check the camera step per frame from the f-curve (it rises smoothly, with no single jump) |
| A three-frame crop from a video shows frames off by one | `ffmpeg -ss` returns the first frame at or after the requested time, so `(f-1)/30 + 0.001` skips frame f | ask for a time slightly before the frame: `(f-1)/30 - 0.012`. `trip.py` and `qa_final.py` were fixed on 22 Nov; sheets made before that are labelled one frame early |
| A command on the box dies with code 143 | `pkill -f "pattern"` also kills the shell whose command line contains the pattern | write the pattern with brackets: `pkill -f "[p]ool_video.py anim"` |
| Setup runs twice and apt is locked | `a && b && nohup c &` puts the whole chain in the background | run short steps one at a time; only the long command gets `nohup ... &` |
| A second PUT to a presigned URL is refused | the URL is signed with `If-None-Match: *` | request a new URL for every upload |
| The render slows down while a QA tool runs | the box has only 4 vCPUs and three render processes already use about 3.3 | one analysis tool at a time, with `nice` |
| Whisper garbles the first 30 seconds | `initial_prompt` contained the script | give no prompt; match to the script with `difflib` |
| The voice-over is too slow | Eleven v4 has no speed control | the tag `[quick, energetic pace]` at the start of the text, then tighten the pauses and use `atempo` of at most 1.10 |
| `T('S06', 'air', 2)` fails | the script says "airnya", not "air" | the anchor word must match exactly; count its occurrences |
| A black area on the cut face | two coplanar surfaces | move one by 4 mm |
| An object moves late or is left behind after `show()` | a CONSTANT key carried over; an automatic BEZIER handle next to a "hidden" key | give the next key an explicit `ip` |
| Flow dots float outside the pipe or shoot across the picture | the key of the last point and the key of the first point of the next loop fall at the same time; the second replaces the first | move the last key 0.004 seconds earlier; print the key list of one dot before rendering |
| A smooth pulse becomes a jump, with a flicker of 1 or 2 frames at its end | new keys inherit CONSTANT from the `show()` or `extend()` key | `pulse(..., ip='BEZIER')`; end the pulse on a multiple of its period |
| A sticker covers the mascot; a tag is hidden behind a pipe | the position was chosen without computing the projection | `project(pose, point)` before rendering |
| A "growing" object shows as a thin sheet before its cue | zero scale is still rendered | hide it until the cue (`hidden_until` inside `grow`) |
| A dark blob in a stack of transparent shapes | closed prisms plus the transparent bounce limit | single-sided planes, one outline per stain, hide at alpha 0, raise the bounce limit |
| A long shadow from a tag that faces the camera | the tag casts a shadow | `visible_shadow = False` |
| The digit "1" reads as "I" | Blender's built-in font | load Inter Bold |
| Colours look different from one part to another | denoising artifacts at 4 samples | judge colour at 12 to 16 samples or more |
| A hero shot cuts through an object and shows empty space | the pose was chosen by estimate | sweep poses numerically, enlarge the soil block |
| A text changes but is never shown | the object was removed before the last text cue | reorder the cues, check with a still at every change |
| `gpu_rental_exec` or `sandbox_exec` returns "Bad Gateway" | the call waited longer than about 60 seconds | `nohup` or `background:true` plus short polls; after a failure, check the state before repeating |
| `pgrep -af` prints thousands of characters | the heredoc command line is printed too | `pgrep -f "[p]attern" \| wc -l` |
| The Write tool refuses to overwrite a file | the file was changed through the shell after it was last read | write to a new name, then copy |
| `project_write` with `local_path` is refused | the file changed since it was read | read it again, change it with Edit, write again |
| A third-party file changes when committed | it went through `/mnt/user-data/outputs` (C2PA manifest) | commit it by the `fileUuid` of the original upload, or do not copy it |
| Caption OCR fails on a quote mark | the tesseract whitelist is parsed like a command line | write `\'` in the whitelist |
| Scene detection finds nothing | the video has no hard cuts | measure the frame-to-frame difference (`ref_teardown.py motion`) |

## 10. Short checklist

- [ ] Brief and assumptions written down
- [ ] Reference analysed; list of what is taken and what is not
- [ ] Fact-check table with sources
- [ ] Script line by line with IDs, cuttable lines marked, counted in syllables
- [ ] Voice credit approval, audition (if needed), voice-over, processing, word timings
- [ ] Scene from code, cues from `T(id, word)`
- [ ] Stills in layers until clean; colour checked at 12 samples or more
- [ ] User review gate before the GPU
- [ ] GPU credit approval, rent, setup, test stills, render without persistent data
- [ ] Scan every frame, with zero real suspects
- [ ] Captions, encode and clean master, then QA of the final file (sheets from every phase, loudness, sync)
- [ ] Upload, verify the md5, shut the box down, check the transactions
- [ ] Production record, archive in the Project and the local folder, worklog, runbook

## 11. Skills made from this runbook

| Skill (`skills/` folder) | Trigger | Contents |
|---|---|---|
| `3d-engineering-video` | a request for a short 3D engineering explainer from a script or a reference video | the workflow and gates of sections 3 to 10, with references to the kit |
| `reference-short-teardown` | "study this video" or "analyse this video" for a reference short | step 1, the format of the teardown document, the originality rules |
| `higgsfield-blender-render` | a scene script ready to render on a rented box | sections 4 and 5, and steps 8 to 11 |

The skills contain instructions only. The code is in `kit/`, and the skills fetch it with `git clone`. When this runbook was written the workflow had been tested on two topics and two languages (videos #1 and #2). Audience feedback on the voice, the look and the pace is not part of it yet.

## 12. Not tested yet

- The exact cause of the persistent-data defect. The guess: the transform of an object with a single-user mesh is "baked" into the geometry, and the version in the GPU's acceleration structure is not always updated with it. A trick that might restore persistent data (giving every mesh a second, hidden user so that it is always instanced) has not been tried.
- Why video #1 was not affected although it was rendered with persistent data too. A scan of its clean master (22 Nov, in the sandbox) found 5 suspects in 1,980 frames, and all five were legitimate: two fast moves, two overshoots of labels that had just appeared, and one small glint on a pipe.
- Extra CPU cores on the box (`cpu` in `gpu_rent`) to speed up rendering and encoding. The price has not been checked.
- An animatic as a review gate (skipped in both videos).
- Music and sound effects: Claude cannot judge a mix.
- Choosing the voice by the user's ear before the full voice-over (in video #2 the voice was chosen from measurements because the user asked to go straight to production).
- Higgsfield's `video_analysis_create` as a second checker for the finished video (cost unknown).
