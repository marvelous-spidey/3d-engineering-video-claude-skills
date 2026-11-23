# Video 01: production record of "How a Septic System Works" (EN)

21 November 2026. The first video, made before the kit existed. Its files are in `examples/video01-septic-system-en/`.

This is the repo version of the record: result links, media IDs, names and private storage locations have been removed, and the section "Findings after release" was added.

## Result

| Item | Value |
|---|---|
| Format | 1080x1920, 30 fps, 66.0 seconds, H.264 + AAC, 28.3 MB, -14.3 LUFS |
| Output | the final video with captions and sound, plus a clean master (no captions, no sound) for changing the captions or adding music without rendering again |
| Script | 171 words, 16 lines, a second-person "problem, then solution" pattern; the content and the sentences are original, and the facts were checked against the EPA |
| Voice | ElevenLabs v4 through Higgsfield, preset "Cillian" |
| Picture | a Blender scene of 710 objects from one 902-line Python file (`septic_video.py`); word-by-word captions burned in with PIL |
| Higgsfield credits | voice 4.37 + GPU 43.72 = 48.09 |

## The route actually taken

1. English script and fact check (Claude).
2. Voice from Higgsfield, then word timings with faster-whisper in the Higgsfield sandbox.
3. Scene and animation written as code in Claude's workspace. Every animation cue is computed from the word timings, not typed by hand.
4. Picture checks in Claude's workspace (CPU): about 300 low-resolution stills over several rounds of fixes, before the GPU was rented.
5. Render on a Higgsfield GPU box of kind `compute` (not Blender Studio): `bpy` 5.3.0 installed through `uv` on Python 3.13, Cycles with OptiX.
6. Word-by-word captions burned in with PIL, then encoding and muxing the voice with ffmpeg, on the same box.
7. QA of the final file: a 20-frame contact sheet, 100% crops of two consecutive frames, ffprobe, loudness, and a second transcription of the final audio to check sync.

## Measured numbers (replacing the estimates in the plan)

| Item | Measured |
|---|---|
| Box setup (apt, uv, bpy, fonts, voice) | about 80 seconds |
| Render speed at 1080x1920, 64 samples + denoise, 1 process | 1.7 to 1.9 seconds per frame (32 samples: 1.3 to 1.6) |
| 3 parallel processes on 1x L40S | 1,980 frames in 27 minutes 20 seconds; the box's CPU (4 vCPUs) was full, the GPU only about 50% busy |
| Captions + encode of 1,980 frames | about 3 minutes |
| Total box running time | 36 minutes 57 seconds = 43.72 credits (approved limit: 150) |
| Voice, about 1,000 characters | 4.37 credits (the tool's estimate: 5.5) |

## Corrections to the plan

- **Network**: Claude's workspace and the VM on the user's computer cannot reach Higgsfield's file hosts (its upload host and its CDN). So the video file cannot be sent as a chat attachment or copied to the local folder, and the result is delivered as a link. Scripts go to the box through the Higgsfield sandbox: upload there, download on the box.
- **The VM on the user's computer** runs Linux and cannot run Blender for macOS. Rendering "on your own computer" would need a local Claude Code session, not a chat session.
- **Engine**: Cycles on the GPU is fast enough. EEVEE was not needed.
- **Render route** chosen: a `compute` box with `bpy`. Blender Studio was not used.
- **An animatic as a review gate** was skipped because the user asked for the video to be made directly. Layered still checks by Claude took its place, and the first human review was of the finished video.

## Lessons for the next video

- Patterns that worked: cues from word timings, `grow/appear/show/travel` as the animation vocabulary, labels that size themselves to their text, the camera `shot()` with a move and then a drift.
- Artifacts that appeared, and why: a "growing" object showed as a thin sheet before its time (it has to be hidden), stacked transparent stains turned dark (the transparent bounce limit), tags facing the camera cast shadows (turn off `visible_shadow`), the digit "1" in Blender's built-in font looked like the letter I (use Inter).
- 4 samples with denoising is misleading about colour. Judge colour at 16 samples or more.
- A `gpu_rental_exec` call that waits more than 60 seconds can fail with Bad Gateway. Run long work with `nohup` and poll with short commands.
- The box's 4 vCPUs limit the speed. More cores raise the hourly price, so that needs new approval.

## Findings after release (22 November 2026)

- A frame-to-frame scan of the clean master found 5 suspects in 1,980 frames, all legitimate: fast motion, the overshoot of labels that had just appeared, and a small glint on a pipe.
- Some captions appear 0.3 to 0.5 seconds before their word, mostly the word "and" after a comma: the transcription engine put the start of the word inside the pause before it. `kit/audio/align.py` v1.0 snaps word boundaries to pauses to prevent this in later videos.

## Not done

- Music and sound effects (this version is narration only). They can be added on top of the clean master without a GPU.
- Claude has not listened to the audio. It was only measured.
- Channel name, watermark and cover image.
- An Indonesian or 16:9 version of the same scene.
