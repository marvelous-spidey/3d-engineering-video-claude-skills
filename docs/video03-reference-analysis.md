# Video 03: teardown of the sample video (turbo engine, English)

23 November 2026. A sample output of the `reference-short-teardown` skill. The measuring tool is `kit/ref_teardown.py`.

This is the repo version: the file name and fingerprint of the reference video have been removed. The script of the reference video was never recorded here; the structure table lists only the function of each beat.

Claude cannot watch motion or hear audio. Everything in this document comes from still frames, reading the captions (OCR) and signal measurements.

## 1. Measured numbers

| Item | Value |
|---|---|
| Source | an English-language short about a turbocharged four-cylinder engine making 1,000 hp, given by the user as a format example (no creator name is recorded in the file) |
| Picture | H.264 720x1280, native 30 fps (0.5% duplicate frames), 2,371 frames, 79.0 seconds |
| Audio | AAC 44.1 kHz stereo, -14.1 LUFS, range 1.8 LU |
| Narration | about 221 words in 77.4 seconds, or about 2.9 words per second; 15 sentences; a male voice (median pitch 152 Hz) |
| Pauses | no pause of 0.18 seconds or more below -38 dB; the noise floor is about -33 dB, so there is a bed of sound (music or effects) under the narration |
| Captions | phrases of 2 or 3 words at about 78% of the screen height, rounded white letters with a dark outline; words not yet spoken are dim and then fill in |
| Camera | no hard cuts; 15 fast moves, median 3.1 seconds each; the camera moves fast 82% of the time and drifts slowly 17% of the time |

The word count comes from a working transcript made by OCR of the captions and may be off by a few words. The reference video file is not included in the repo.

## 2. Beat structure

Timings were read from a contact sheet at 1 frame per second (to about half a second). The table lists the function of each beat, not its sentences or content.

| # | Seconds | Function | Words |
|---|---|---|---|
| 1 | 0-7 | hook | 17 |
| 2 | 7-11 | problem | 12 |
| 3 | 11-16.5 | solution | 16 |
| 4 | 16.5-22 | problem | 19 |
| 5 | 22-25 | solution | 7 |
| 6 | 25-31 | problem | 16 |
| 7 | 31-38 | solution | 20 |
| 8 | 38-42.5 | naming | 9 |
| 9 | 42.5-49 | problem | 18 |
| 10 | 49-54 | solution | 15 |
| 11 | 54-61 | problem | 20 |
| 12 | 61-66 | solution | 13 |
| 13 | 66-69 | addition | 11 |
| 14 | 69-74 | result | 16 |
| 15 | 74-78 | close | 12 |

Pattern: a hook, five pairs of problem and solution with rising stakes, one naming beat in the middle, then the result and a recap. This is the same grammar as reference #2.

## 3. Visual language

- **Set**: one engine on a wheeled stand, inside a workshop.
- **Model**: very detailed and close to photographic. The inside is opened with a coloured cut face.
- **Camera**: orbits the engine, moves into the cut face for each problem and out again for each solution; there is motion blur.
- **Tags**: labels with leader lines; a different colour for danger. Numbers are shown as digital gauges.
- **Motion**: parts move and are swapped in place, with a flash at each failure.
- **No characters**, human or mascot.

## 4. Taken / not taken

Taken (format grammar):

- the topic and the length (about 75 to 80 seconds), a dense pace with no pauses;
- captions of 2 or 3 words that fill in word by word;
- one object on one set, with a continuous camera that moves into and out of the cut face;
- numbers shown as gauges on screen;
- the chain of problem and solution, and a close that returns to the opening number.

Not taken:

- the sentences, analogies and order of detail of its script; ours is reorganised around "three enemies" (pressure, revs, heat);
- the engine model, the set and its props; our engine is built from code;
- the colour palette and the tag style; we use a yellow cut face and the tags of our own series;
- footage, audio, music and text effects;
- its numbers: every number in our script was checked independently (see `examples/video03-crv-engine-id/script_id.md`).

## 5. Production implications

| Item | Choice |
|---|---|
| `CAPTION_STYLE` | `phrases` |
| Camera | one continuous move, no hard cuts (as in video #2) |
| Target duration | 73 to 78 seconds |
| Indonesian script budget | 79 x 6.3 is about 500 syllables at most; the script used has about 459 |
| New for the scene | crank and piston motion baked per frame, springs (helices), gauges and a number counter, interior lighting, metal materials |
| Biggest risk | the level of detail: the reference model is far more detailed than anything that can be built from basic shapes |

## 6. Limits of the analysis

- Music or effects under the narration were detected from the noise floor but cannot be separated or identified.
- Beat timings were read per second, not per frame.
- The caption OCR is noisy (busy background); the word count is good to about 5 words.
- Whether the content of the reference video is correct was not assessed here; see the fact-check table.
