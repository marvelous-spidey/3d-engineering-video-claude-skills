---
name: 3d-engineering-video
description: Makes a short vertical 3D video that explains how a machine or engineered system works (Blender code, AI narration, word-by-word captions) from a script, a topic, or a reference video.
---

# 3D engineering video

The result is an MP4 at 1080x1920 and 30 fps (delivered as a Higgsfield link) with narration and captions, a clean master without captions or sound, the scene script, the narration script with its fact check, and a production record. Every picture is built from Blender code and every motion follows the timing of a word in the narration. That fixes the order of work: script, voice, word timings, scene, render.

This skill describes the workflow. The tools are in the kit (code, in the `kit/` folder of the repo that holds this skill) and in two companion skills: `reference-short-teardown` (analysing a reference video) and `higgsfield-blender-render` (rendering on a rented GPU until the file is done).

The skill is written for Claude with a Linux workspace (bash and Python) and the Higgsfield MCP connector. If either is missing, say what is missing and stop.

Reply to the user in the language they write in. English and Indonesian narration have been tested.

## 0. Set up the workspace

1. Install the kit to `~/kit`:

   ```bash
   REPO=https://github.com/marvelous-spidey/3d-engineering-video-claude-skills
   [ -f ~/kit/VERSION ] || { git clone --depth 1 "$REPO" ~/3dv-repo && cp -r ~/3dv-repo/kit ~/kit; }
   cat ~/kit/VERSION
   ```

   If GitHub is unreachable, use a copy of the kit from the user: a `kit/` folder they attach or connect, or a `kit_tools.md` document in their Project (unpack it with `python3 make_bundle.py unpack kit_tools.md ~/kit`). The skill cannot run without the kit.
2. Check the tools in the workspace: `python3 -c "import bpy, PIL, numpy; print(bpy.app.version_string)"` and `ffmpeg -version`. If `bpy` is missing: `pip install --break-system-packages bpy==5.3.0 pillow numpy` (needs Python 3.13, about 1 GB). After the first install, run `bash ~/kit/selftest.sh` until it prints `SELFTEST PASSED` (3 to 10 minutes on CPU, no credits).
3. Check the Higgsfield connector: the tools `generate_audio`, `sandbox_exec`, `media_upload`, `gpu_list_gpus` and `gpu_rent` must be available. If they are not, ask the user to connect the Higgsfield MCP first.
4. If the user has notes from earlier videos (for example a `worklog.md` in their Project or local folder), read the latest state and decisions: the next video number, and the voice and style they last approved.
5. Read `~/kit/GUIDE.md` one section at a time, when you reach the step it covers. Three example jobs are in `~/3dv-repo/examples/`; video #3 is the example for the reference-video route and for mechanical motion. `docs/pipeline-runbook.md` is background only; its commands are from an older version.
6. Create the job folder: `mkdir -p ~/jobs/videoNN && cp ~/kit/job.env.example ~/jobs/videoNN/job.env`, fill in `NAME`, `SCENE`, `LANG_CODE` and `CAPTION_STYLE`, then run `bash ~/kit/newjob.sh ~/jobs/videoNN`.

## 1. Four ways in

| What the user gives | Language of the video | Start at |
|---|---|---|
| A script in English | English | 1A |
| A script in Indonesian | Indonesian | 1A |
| A reference video (English or Indonesian) | the other language, unless they ask otherwise | 1B, then 1A |
| Only a topic | ask which language | 1B steps 2 and 3, then 1A |

### 1A. From a script

1. Use the user's script as written. You may tidy the following without asking, as long as you show the changes: numbers written out as words ("fifty tons", "one in five"), abbreviations written the way they are read, and punctuation for pauses. The reason is technical: a group of digits is read as several words, so captions and word timings cannot be matched to it.
2. Split it into `script.txt`, one line per sentence-picture: `S01|text`. One line is one change on screen. Break long sentences at a comma.
3. Work out the duration before generating the voice: English is about words / 2.7 seconds, Indonesian about syllables / 6.3 seconds, plus about 2 seconds. The format works best at 60 to 75 seconds. If the script is much longer, tell the user the duration and the cost and suggest lines to cut, but do not cut the user's script without permission.
4. Check the facts with web search: numbers and cause-and-effect claims. Report anything doubtful with its source and propose a replacement sentence. Never change what the script says silently.
5. Draft the visuals: a table of line, what is seen and what moves, and the tag or number on screen. Use one set (location) for the whole video, with the cut face toward the camera. A number may appear on screen only if it is in the fact-check table. If you have no checked number, use a label without one.

### 1B. From a reference video

1. Run the `reference-short-teardown` skill. It gives the style numbers (pace, caption style, hard cuts or one camera move), the function of each beat, and a list of what is taken and what is not.
2. Research the topic from primary or institutional sources, then build a table of claim, source, and the simplification you chose. For topics with no institutional source (engine tuning, for example), use technical media and the builders themselves, and confirm each number in more than one source. Numbers in the reference video are leads, not sources: replace any that do not survive the check and record the difference in the plan.
3. Write a new script in the target language. Follow only the reference's format grammar: topic, length, pace, and the function of each beat (hook, problem-solution chain, surprising fact, a closing line that returns to the hook). Write your own sentences, analogies, order of detail, set and characters, and localise examples and units for the target audience. This is not a translation or a dub of someone else's video, and its footage, audio and characters are not used. If the user gives a hook sentence, use it.
4. Length budget: the reference's duration x 2.7 words (English) or x 6.3 syllables (Indonesian). The same content takes more syllables in Indonesian, so mark the lines that may be cut.
5. Continue at 1A step 2. `CAPTION_STYLE` and the camera style follow the teardown.

If the reference is the user's own video and they ask for a faithful translation, the script may be translated. Ask first.

## 2. Gate before any credits are spent

Send one message with: the final script line by line, a short visual plan, the proposed voice, the estimated duration, the estimated voice and GPU credits, and the credit limits you are asking for. Continue only after the user explicitly approves the limits. If the user has already said "just make it" and has named or approved the limits, go ahead and state the assumptions you made in the first line of the report.

- Prices change. Check them first with the free tools `estimate_audio_cost` and `gpu_list_gpus`. The numbers below were measured in November 2026.
- Voice: about 0.47 credits per 100 characters per take. Allow for two takes, plus about 5 credits if there is an audition.
- GPU (L40S at 71 credits per hour): box minutes are roughly frames / 0.74 / 60 + 15. For a scene with motion baked per frame, or with many curve objects, divide by 0.6 instead. Ask for a limit of about 1.6 times the estimate: two of the first three videos needed a partial re-render.
- Never spend credits beyond the limit. If the projection exceeds it, stop and ask.

## 3. Voice and word timings (Higgsfield sandbox, free)

Claude's cloud workspace cannot reach the Higgsfield CDN, so audio is processed in the sandbox (`sandbox_exec`), in `/home/user/jobs/<name>/`. Prepare that folder in the sandbox:

```bash
cd /home/user && { [ -d 3dv-repo ] || git clone --depth 1 https://github.com/davidalfasunarna/3d-engineering-video-claude-skills 3dv-repo; }
mkdir -p jobs/<name> && cp 3dv-repo/kit/audio/*.py jobs/<name>/
```

Then send `script.txt` with a heredoc and compare its md5. If the clone fails, send `audio/*.py` with a heredoc as well.

1. The default voice and pace tag for each language are in `GUIDE.md` section 3. If the user wants to choose the voice, run an audition as described there and let them choose by ear.
2. `generate_audio` with model `elevenlabs_v4`, one turn, `voice_type: preset`. The text is `script.txt` without the line IDs and without the ` / ` marks.
3. `python3 vo_prep.py <target_seconds> vo_raw.mp3` gives `vo_proc.wav`. If the result is still more than 5 seconds over the target, decide with the user: accept the longer video, make a new take, or cut lines. Do not make more than two takes without asking.
4. `python3 asr.py vo_proc.wav asr_proc.json <id|en> && python3 align.py <id|en>` gives `words.json`. Check the output: the word count equals the script, the line "words that span a pause" is empty, and the `diff` list contains only spelling differences. Note the words that were heard differently for the final report. Numbers and spelled-out abbreviations (for example "CR-V") get their timing by interpolation and can be off: check them and correct them as described in `GUIDE.md` section 3 before you write the scene.
5. Bring `words.json` to the job folder in the workspace (print it, write it again, compare the md5). Once you have started on the scene, do not run the transcription again: its results can shift by up to 0.2 seconds between runs.

## 4. Scene and previews (workspace, free)

1. Start from `scene_template.py`, which has already been copied as `$SCENE`. The rules for writing a scene, the function vocabulary and the keyframe rules are in `GUIDE.md` section 1. Read it before you write.
2. Write `keywords.txt` (for the `cards` style): one or two key words per sentence, as `S01 word [nth]`.
3. Preview in layers as described in `GUIDE.md` section 2 until the contact sheet is clean. Look at the pictures yourself; do not judge from the log. Add motion strips (5 to 7 consecutive frames) around every part swap and every object that enters or leaves.
4. Run `python3 scene_check.py <scene>.py` every time the scene script changes. Without rendering, it prints what stills cannot show: camera jumps, on-screen objects that come back or never leave, and flashes that last only one or two frames, with the second each one peaks. Take a full-size still at each of those peak seconds. For motion with a physical constraint (a valve must not pass through a piston, an engine must not run backwards), write a small checker in the job folder. Fixing this kind of mistake after the render means paying for a re-render.
5. Send a captioned contact sheet before renting the GPU if the user asked for a review gate, or if the look is the biggest risk of this video (a new kind of model, a new style).

## 5. Render to a finished file

Run the `higgsfield-blender-render` skill. It handles sending the files to the box, the three-process render, the scan of every frame, captions and encoding, the colour and loudness checks, the upload, and shutting the box down.

## 6. Report and archive

Report to the user, conclusion first:

- Links to the final video and the clean master, the duration, and the voice used.
- Credits spent per item against the limit, and the reason if the estimate was exceeded. State credits spent on fixes after the render separately.
- What was checked: frame scan, colour, format, loudness, md5, sync.
- What Claude could not check: the audio has not been listened to and the motion has not been watched. List the words the transcription engine heard differently, with their seconds, so the user knows where to listen.
- What was not made: music and sound effects. The clean master is there for that.

Archive, wherever the user keeps things (a claude.ai Project, a local folder, or their own repo):

- A production record `videoNN-production-record.md`: result, measured numbers, deviations from the plan, lessons. Example: `docs/video03-production-record.md` in the repo.
- A folder `videoNN/`: `job.env`, `script.txt`, `keywords.txt`, `words.json`, the scene script, the `.blend` (mode `blend`), preview contact sheets, `README.md`.
- The user's working notes, updated with the current state, costs and decisions.
- Propose new lessons that apply generally for `GUIDE.md`. Changes to kit code are released as described in `kit/README.md`.
