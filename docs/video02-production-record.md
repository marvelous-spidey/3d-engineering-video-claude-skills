# Video 02: production record of "Cara kerja kolam renang" (how a swimming pool works, ID)

22 November 2026. The second video, and the first to use the kit. Its files are in `examples/video02-swimming-pool-id/`. Version 1.1 (colour corrected) replaces the first version.

This is the repo version of the record: result links, media IDs, names and private storage locations have been removed. The "plan" mentioned here is an internal planning document that is not included in the repo.

## Result

| Item | Value |
|---|---|
| Output | final video v1.1 (44.1 MB) with captions and sound, plus a clean master (no captions, no sound) |
| Format | 1080x1920, 30 fps, 68.4 seconds, H.264 (BT.709) + AAC, 44.1 MB, -14.5 LUFS (peak -4.0 dBFS) |
| Script | 188 words (422 syllables), 11 lines, Indonesian; the hook sentence came from the user; the facts were checked, and the table is in `examples/video02-swimming-pool-id/script_id.md` |
| Voice | ElevenLabs v4 through Higgsfield, preset "Marcus", pace tag `[quick, energetic pace]`; pauses tightened and tempo raised by 1.088x to 66.48 seconds |
| Picture | a Blender scene of 834 objects from `pool_video.py` (517 lines) on top of `explainer_kit.py` (470 lines); one continuous camera move with no hard cuts |
| Captions | one card of one or two words (164 cards), Baloo 2 ExtraBold, key words in yellow (this video's `post.py`; now `kit/captions.py`) |
| Credits | voice 16.66 + GPU 132.29 = **148.95** (approved limits: voice 20, GPU 200) |

## Colour correction (version 1.1, 22 November 2026)

**Finding.** While the kit was being tidied up, the caption colour in the final file was measured: a yellow that should be (255, 214, 58) read as (255, 207, 49). A test with colour patches showed why. The encode command in `post.py` v2 tagged the file as BT.709 but did not tell ffmpeg to convert RGB to YUV with that matrix, so BT.601 was used. As a result green was about 10% darker (140 became 125) and yellow was slightly off in every player that honours the colour tag. Video #1 was not affected, because its version of `post.py` used the filter `scale=out_color_matrix=bt709`.

**Fix, without credits, in the Higgsfield sandbox.** The frames were read from the clean master with the BT.601 matrix (which restores the original colours), the same captions were burned in again, and the result was encoded with the correct BT.709 matrix (CRF 17). The audio was copied unchanged from the first version. The clean master was not re-encoded; only its matrix tag was corrected, so its picture is identical.

**Checks on v1.1.** 2,052 frames, 68.4 seconds, -14.5 LUFS; the caption yellow reads (254, 213, 56); the mean difference from the first version read as BT.601 is only 1.6 out of 255 (compression noise); the md5 of the uploaded file equals that of the encoded file.

**Prevention.** `kit/captions.py` always uses an explicit matrix filter, and `kit/box/qa_final.py` compares video frames with the PNG frames under both matrices and prints `COLOUR OK` or `COLOUR FAILED`.

**Another small note from the same session.** With `align.py` v1.0, two words ("Lima" at the start of line S10 and "Katup" in S11) now start right after a pause. In this video the captions and cues of those two words come about 0.25 seconds early. It was not re-rendered.

## The route actually taken

1. Script variant B from the plan was used without changing a word; the fact-check table is in `script_id.md`.
2. An audition of five voices with the same two sentences, measured in the Higgsfield sandbox, then the full voice-over. Take 1 was too slow (92.3 seconds); take 2 used a pace tag at the start of the text (78.4 seconds).
3. Audio processing (`kit/audio/vo_prep.py`): 75 pauses tightened from 15.5 to 9.5 seconds, tempo 1.088x, loudness -14.4 LUFS.
4. Word timings (`asr.py` + `align.py`): 188 words, 15 of them interpolated, 43 snapped to a real pause.
5. The function kit was split off from the video #1 script (`kit/make_kit.py`), with cue lookup by sentence ID and word added.
6. The scene was written as code and checked over five rounds of CPU stills in Claude's workspace.
7. A `compute` GPU box with 1x L40S: setup, 6 test stills at 64 samples, a render with 3 parallel processes.
8. An automatic frame-to-frame check found defects in the first render. Every frame was rendered again without persistent data and checked again.
9. The same check on the second render found an animation mistake in the water flow dots. The script was fixed and the two affected frame ranges were rendered again.
10. Captions and encoding, clean master, QA of the final file, upload, box shut down.

## The defect in the first render, and its fix

**Symptom.** In the first render, one of the three processes drew objects that had just changed as solid black shapes, while the other two drew them correctly. Because frames are dealt out to the three processes in turn, the result was a 10 Hz flicker. An example that was looked at directly: the mud slide in the pit was black on frames 229 to 250 of the first process (up to 185,395 black pixels per frame), while frames 249, 251 and 253 around them were normal.

**How it was found.** Not from stills. The six test stills on the box were clean. The first contact sheet from the rendered frames showed only one small black triangle and missed the runs of defects in the other processes, because all of its sample frames (times that are multiples of 0.1 seconds) belonged to the same process. What caught all of it was a score for "a frame that differs from both of its neighbours" on thumbnails of every frame (`kit/box/scan.py`), together with a count of pure black pixels.

**Size of the problem.** Of the first 1,218 frames, 239 were flagged as suspects (process 0: 23, process 1: 43, process 2: 173), in long runs within one process, for example process 2 from 2.97 to 7.47 seconds and from 9.47 to 17.17 seconds. A direct comparison of frames 1 to 180: 31 frames of the first render differed from the re-render, all of them from process 2, and the other frames matched to within 0.07 out of 255 per block.

**Cause.** The Cycles option `use_persistent_data`, which keeps scene data between frames in each process. A fresh process that jumps straight to a problem frame draws it correctly, so the fault is in the state that is carried over, not in the scene. The exact mechanism has not been proven (a guess is in `pipeline-runbook.md` section 12).

**Fix.** Persistent data was turned off (`KIT_PERSIST=0`, now the kit default) and all 2,052 frames were rendered again. The first render was stopped at frame 1,504 and not used. The scan of the re-render shows no more runs of suspects within one process and no black objects. What remained, 64 suspects spread evenly over the three processes, turned out to come from the animation mistake described in the next section.

**Cost.** The first render used about 28 minutes of box time (about 33 credits) that were wasted. Without persistent data the speed is 0.74 frames per second (2,052 frames in 46 minutes 25 seconds), compared with 0.90 to 0.95 with it.

**Video #1.** It was rendered with persistent data too. A scan of its clean master (in the sandbox, free) found 5 suspects in 1,980 frames, all of them legitimate fast motion (a swinging shovel, a sign while the camera moves, a truck passing). Video #1 was not affected.

## An animation mistake that was caught as well

After the second render was free of the defect above, the scan still flagged 64 frames, spread evenly over the three processes. Crops of three consecutive frames for the 12 strongest suspects showed the cause, and this time the cause was in the scene script.

**Water flow dots.** Each dot travels along the pipe path and then jumps back to the start. The key for "the last point" and the key for "the first point of the next loop" fell at exactly the same time, and Blender replaces the old key when a new one lands on the same frame. So the last segment of every path was never travelled: the dot flew straight from the second-to-last point to the start. On screen, water dots floated outside the pipe (from the bottom of the pump riser to the skimmer), shot across the pool (the return line), and the water from the hydrostatic valve bobbed up and down in its hole instead of spreading into the pool. Fix: the key of the last point was moved 0.004 seconds earlier.

**Odour lines.** A key added after `show()` or `extend()` inherits CONSTANT interpolation from the key before it, so the pulse of the odour lines became a square wave with one flicker 1.5 frames long at 41.6 seconds. Fix: BEZIER interpolation is passed explicitly, and the pulse ends on a multiple of its period.

Both mistakes got through five rounds of stills because a still shows only a position at one moment, and a floating dot looks like any other dot. Only the affected frames were rendered again: 695 to 1262 and 1680 to 1849 (738 frames). Three frames outside those ranges were re-rendered as controls, to make sure the fix did not change anything else. The result: all three control frames matched the old frames (largest block difference 0.06 out of 255), the suspects fell from 64 to 24, and the 12 strongest were all legitimate motion (fast camera moves, tags appearing with overshoot, moving germs and splashes).

The version from before the fix had already been uploaded. It was replaced and is not used.

## Measured numbers

| Item | Measured |
|---|---|
| Box setup | about 3 minutes (it ran twice because of a wrong command; normally about 80 seconds) |
| Test still at 1080x1920, 64 samples + denoise, 1 process | 1.3 to 1.7 seconds per frame |
| First render, 3 processes, persistent data on | 0.90 to 0.95 frames per second; GPU 94% busy |
| Re-render, 3 processes, persistent data off | 2,052 frames in 46 minutes 25 seconds (0.74 frames per second); GPU 99% busy |
| Partial re-render after the animation fix | 738 frames in 17 minutes 18 seconds |
| Captions + encode + clean master + scan (together) | 2 minutes 38 seconds for both encodes; about 3 minutes until the contact sheets were done |
| Total box running time | 1 hour 51 minutes 47 seconds = 132.29 credits (approved limit: 200) |
| Voice | audition 4.70 (4 x 1.15 + 0.10) + take 1 at 5.98 + take 2 at 5.98 = 16.66 credits |

## Voice audition

The same two sentences (33 words) for each voice, measured with `kit/audio/audition.py`.

| Voice | Clip length | Total pauses | Syllables per second while speaking | Words recognised | Pitch | Loudness |
|---|---|---|---|---|---|---|
| Cillian (Eleven v4) | 15.8 s | 3.4 s | 6.3 | 29 of 33 | 140 Hz | -18.4 LUFS |
| **Marcus (Eleven v4)** | 16.1 s | 3.8 s | 6.3 | 32 of 33 | 140 Hz | -21.3 LUFS |
| Julian (Eleven v4) | 15.7 s | 3.1 s | 6.2 | 31 of 33 | 136 Hz | -19.5 LUFS |
| Maya (Eleven v4) | 16.0 s | 3.8 s | 6.4 | 32 of 33 | 211 Hz | -17.9 LUFS |
| Qwen Audio 3.0 TTS Flash | 21.5 s | 6.0 s | 5.0 | 31 of 33 | 123 Hz | -12.4 LUFS |

Marcus was chosen because the transcription engine recognised the most words among the male voices (the only miss, "pompa" heard as "pompah", occurred with every voice). This is a choice made from measurements, not by ear. A choice by a human ear is still better; the measurements only narrow the field.

## Corrections to the plan

- **Review gates were skipped.** The plan had G1 (the user chooses the voice), G2 (stills in the chat) and G3 (an animatic). The user asked to go straight to production, so the plan's defaults were used and the first review was of the finished video.
- **GPU cost.** The plan estimated 65 to 100 credits for the final render. The real figure was 132.29, because one render was wasted and a third of the frames were rendered again after the animation fix. This scene is about 25% heavier than video #1 (0.95 against 1.2 frames per second with 3 processes and persistent data), far below the plan's guess of 1.5 to 2.5 times.
- **Voice pace.** The plan estimated 6.0 to 7.0 syllables per second. Without a pace tag the preset reads at about 4.6; with the tag and processing the final result is about 6.3.
- **On-screen text.** The plan named four tags; seven kinds were made (`HARI 1/3/5` and `KAPORIT` were added).
- **Kit.** The plan to "split off the kit, then run a regression test on video #1" is half done: video #2 uses the kit fully, but the re-test against the video #1 stills has not been run.

## Lessons for the next video

- Scan every frame before encoding, and do not judge an animation from stills alone. The same scan caught two kinds of problem: a render defect and an animation mistake.
- Look at crops of three consecutive frames for the strongest suspects (`trip_png.py`). A score alone does not say what is wrong.
- For every looping motion, print the key list of one sample object before rendering. Two keys at the same time replace each other, and a new key inherits the interpolation of the key before it.
- The contact sheet must take frames from all three process phases.
- Render without persistent data. It costs little.
- While the box is on, do only what needs the box. A heavy analysis tool slows the render because the box has only 4 vCPUs.
- A pace tag at the start of the text is cheaper than another take. Tighten the pauses before raising the tempo.
- Cues through `T(sentence id, word)` let the script change without touching any timing number.
- Other technical details (key interpolation, coplanar surfaces, shell commands that trip you up) are in `pipeline-runbook.md` section 9.

## Where the files are in this repo

- `examples/video02-swimming-pool-id/`: the scene script (already in the form of a kit v1.0 job), `job.env`, `script.txt`, `keywords.txt`, `words.json`, `script_id.md` (script, picture per line, fact check, sources), and preview contact sheets.
- `kit/`: the code that was used (version 1.0 is the tidied-up version of this video's tools).
- Video files, audio, PNG frames and the `.blend` are not included.

## Not done

- Music and sound effects. They can be added on top of the clean master without a GPU.
- No human has listened to the audio or watched the motion; Claude only measured and looked at frames. Measured on the final file: 2,052 frames, 68.4 seconds, -14.5 LUFS; the md5 of the file at the link equals the file on the box; a second transcription recognised 172 of 188 words, and for the 170 words that could be compared, word starts are off by a median of 0.00 seconds (95% within 0.02 seconds) from their planned position, and 95% within 0.08 seconds of the caption timing. The transcription engine heard three words slightly differently ("diam" as "biam" at about 21 seconds, "mangkuk" as "mangku" at about 48 seconds, "karet" as "karep" at about 63 seconds). Those are the parts most worth listening to.
- The voice was chosen from measurements. If the voice changes, the voice-over, the word timings and the render must all be redone.
- Channel name, watermark, cover image.
- Human review of the look, the mascot, the caption pace and the pronunciation.
