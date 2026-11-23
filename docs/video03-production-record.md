# Video 03: production record of "Mesin CR-V tembus seribu tenaga kuda" (how a CR-V engine reaches 1,000 hp, ID)

23 November 2026. The third video, and the first production with kit v1.0 and all three skills. Its files are in `examples/video03-crv-engine-id/`.

This is the repo version of the record: result links, media IDs, file fingerprints, the account balance and private storage locations have been removed. The "plan" mentioned here is an internal planning document; the script and its fact check are in `examples/video03-crv-engine-id/script_id.md`.

The video was made from an English reference video about a 1,000 hp turbo engine. Its teardown is in `video03-reference-analysis.md`. The script was rewritten from checked facts, not translated.

## 1. Result

| Item | Value |
|---|---|
| Output | the final video (61.4 MB) with captions and sound, plus a clean master (77.1 MB, no captions or sound) |
| Format | H.264 1080x1920, 30 fps, yuv420p, BT.709, 2,277 frames, 75.9 seconds; AAC 48 kHz stereo; -14.4 LUFS, peak -4.2 dBFS |
| Script | 22 sentences, 199 words, Indonesian; `phrases` captions, 80 phrases with manual breaks |
| Credits | voice 6.44 + GPU 110.90 = **117.34** (approved limits: voice 15, GPU 160) |

## 2. Measured numbers

| Item | Number |
|---|---|
| Voice | Eleven v4, preset Marcus, tag `[quick, energetic pace]`, one take: 78.45 seconds raw, 73.98 seconds after `vo_prep.py` (-14.3 LUFS) |
| Word timings | 199 words, none spanning a pause. The transcription engine writes numbers as digits, so 37 words got their timing by interpolation; "CR-V" was corrected in two places with `patch_words.py` |
| Scene | `engine_video.py`, 484 lines, 771 objects, 71 materials, about 262,000 keys |
| CPU previews | 6 rounds: about 100 stills at 405x720 (11 to 15 seconds each), 3 stills at 720x1280, 42 motion-strip stills around the part swaps; all free |
| Test stills on the GPU | 2.5 seconds per still (1080x1920, 64 samples, OptiX); they look the same as the CPU previews |
| Full render | 2,277 frames in 63 minutes 25 seconds with 3 processes: 0.60 frames per second (about 5.0 seconds per frame per process). The GPU was only 30 to 50% busy; the limit is the box's CPU (4 vCPUs) |
| Encoding | final video, clean master and scan in parallel: 2 minutes 36 seconds |
| Partial re-renders | 189 frames, then 37 frames |
| Box running time | 1 hour 33 minutes 43 seconds |

Of the 110.9 GPU credits, about 85 went to the straight path (setup, test stills, full render, encoding, first upload) and about 26 to two rounds of fixes and their uploads.

## 3. How the scene is built

- **One crank-angle curve for the whole video.** A speed profile per sentence (0 to 3.3 revolutions per second on screen) is integrated into an angle per frame. The crankshaft, pistons, connecting rods, valves, springs, camshafts, combustion flames and knock are all baked per frame from that angle, so they stay mechanically consistent at any speed. `land()` scales the angle inside a time window so that the piston touches the valve exactly on the word "dihantam" (struck) and the first knock falls on the word "meledak" (explodes), without the engine ever turning backwards.
- **Part swaps.** Two sets of children under one empty (cast pistons and rods against forged ones, standard springs against dual springs, valves against Inconel valves) and two complete cylinder heads that are lifted off and moved outside the set.
- **Gauges on screen.** Children of the camera at a fixed depth, with shadows and reflections turned off. A strip at the top of the screen (about 8 to 25% of the height) holds the needles (boost, rpm, temperature), the chapter titles, the values and the horsepower counter. The camera's focus point is placed below that strip.
- **Tags in the world are sized by camera distance** (a percentage of the screen height), so they read the same in wide and close shots.
- **Combustion flame**: a cylinder with a gradient material (bright under the head, transparent toward the piston); its strength and opacity are baked per frame.

## 4. Findings during the previews (free)

- The flame, at first a flat yellow cylinder, read as a solid object in the colour of the cut face. Orange emission with a strength above about 3 clips to yellow in the Standard view transform. The flame and the leak band at the head joint were moved to red-orange.
- Motion strips found two things that no still showed: an empty cylinder bore for about 3 frames while the pistons were swapped, and the coolant ring appearing as a blue tube 0.15 seconds before the last sleeve went in. Both were fixed: the new part grows first, then the old one disappears.
- Checks without rendering: the largest camera step is 0.65 units per frame with no single-frame jump; the smallest valve-to-piston gap is +0.133 in every cylinder except the exhaust valve of cylinder 1, which is meant to be touched at 48.03 seconds (the word falls at 48.02); the engine never runs backwards.
- The speed of the turbo wheel and the number of holes in the flywheel were limited so that they do not appear to turn backwards at 30 fps.
- The intake air temperature is not in the fact-check table, so the temperature needle is marked only C and H, with no number.

## 5. Checks on the final file

- **Fingerprint**: the file at the link equals the file on the box.
- **Colour**: `COLOUR OK` for the final video and the clean master (mean difference 1.8 to 2.4 against the PNG frames with the BT.709 matrix; worse when read as BT.601).
- **Sync** (a second transcription of the final file): word starts against the narration have a median offset of 0.000 seconds and a 95th percentile of 0.020 seconds; against the caption timing the 95th percentile is 0.059 seconds. 163 of 199 words were recognised; numbers are not transcribed as words.
- **Control frames**: frames 600, 1400, 1975 and 2000 were rendered again with the final script and equal the frames in the video (largest block difference 0.03).
- **Scan of every frame**: 104 suspects in 2,277 frames, spread over the three processes (41, 35, 28). The twelve strongest were looked at as three-frame crops. The rest were classified by their pattern and position, not looked at one by one:
  - combustion flames and knock: they repeat with every revolution of the engine, so they always fall on the same process;
  - the dark gap between a connecting rod and the crankshaft, which appears twice per revolution (a spike of about 2,000 to 3,500 black pixels): looked at on three consecutive frames, a legitimate shadow;
  - parts that enter or leave (the turbo, the cylinder head, the head swap);
  - the sparks when the valve is struck, and tags or numbers appearing.
- **What Claude could not judge**: the audio has not been listened to and the motion has not been watched. Words the transcription engine wrote differently (seconds in the video): "CR-V" at 0.9 and 33.3; "stud" at 24.4; "VTEC-nya" at 39.6; "noken as" at 40.7; "Inconel" at 51.9.

## 6. Deviations from the plan

1. **Air temperature without a number** (see section 4).
2. **The fuel can appears only in chapter 3** (a red can marked "BENSIN" turns into a green one marked "E85" on a cart); in other shots it was cut off by the edge of the frame.
3. **The cylinder heads are told apart by the colour of their cut face** (pale yellow for the stock head, red for the Type R head). This was not planned, but it makes the swap readable.
4. **The upload URLs expired.** Four URLs were requested before the render and used 70 minutes later. All were refused with `ExpiredToken`, even though `X-Amz-Expires` was 86,400 seconds. New URLs were requested and the upload was repeated (about 2 minutes of box time).
5. **Two rounds of fixes after the full render:**
   - The scan flagged the peak frames of the knock: the flash sphere (scale 1.7) was larger than the cylinder and coarsely faceted, and visible for 1 frame at each explosion. The CPU previews had only captured its dim phase. It was fixed (maximum scale 1.0, 24 segments) and 141 frames were rendered again, together with two changes of the on-screen number that had overlapped (48 frames).
   - The fix for those number changes introduced a mistake of its own: the first "160" label of the counter came back and stayed, because the last key of `pop()` (at 0.28 seconds) fell after the key of the shortened `vanish()`. The re-rendered control frame 2000 differed from the video, and that is how the mistake was caught before handover. It was fixed and 37 frames were rendered again.
6. **The kit code was sent to the sandbox as text** (about 123 KB, 21 files, every fingerprint matched), because Claude's workspace cannot upload to Higgsfield and this public repo did not exist yet.

## 7. Lessons (now in kit v1.1)

- **Higgsfield upload URLs work for only about one hour.** Request them when the render has about 10 minutes left. `after.sh` v1.1 waits for `urls.sh` to appear.
- **Check the peak frame of every flash.** An effect that lasts one or two frames (an explosion, a spark) must be captured at its exact peak frame during the previews, not somewhere near the word. `scene_check.py` prints the peak second.
- **Print the timetable of on-screen labels before rendering.** `scene_check.py` prints when each object fixed to the screen is visible and flags `COMES BACK` or `STAYS TO THE END`. A `pop()` followed by a `vanish()` that is faster than the `pop()` makes the label come back.
- **Control frames for `rerender.sh`**: include one frame just after each re-rendered range. That is what catches a label left behind.
- **Scanning repeating motion**: a turning engine produces dozens of legitimate periodic suspects, and they pile up in one process when the period is a multiple of the number of processes. Judge them by their period and position, then look at an example.
- **Render speed is limited by the box's CPU**, not the GPU. For a scene this size, box minutes are about frames / 0.6 / 60 + 10.
- **Emission above about 3 clips** in the Standard view transform. Give a flame a gradient and opacity, not a flat colour.
- **One angle curve for all mechanical motion**, baked per frame, lets the engine speed change from sentence to sentence without breaking the relationship between piston, valve and flame.
- **Sending files to the sandbox as text is expensive.** With this repo, the sandbox and the box can simply `git clone`, and only the scene and the job files need to be sent.
