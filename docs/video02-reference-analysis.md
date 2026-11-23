# Video 02: teardown of the sample video (swimming pool, English)

22 November 2026. A sample output of the `reference-short-teardown` skill. The measuring tool is `kit/ref_teardown.py`.

This is the repo version: the file name and fingerprint of the reference video have been removed. The script of the reference video was never recorded here; the structure table lists only the function of each beat.

Claude cannot watch motion or hear audio. Everything in this document comes from still frames, reading the captions (OCR) and signal measurements.

## 1. The file analysed

| Item | Value |
|---|---|
| Source | an English-language TikTok short about how a swimming pool works, uploaded by the user as a format example (no account name is recorded in the file) |
| Video | HEVC 1080x1920, native 60 fps (no duplicate frames), 3,994 frames, 66.57 seconds |
| Audio | AAC 44.1 kHz, left channel equal to right (mono), -15.7 LUFS, range 4.6 LU |

The reference video file is not included in the repo.

## 2. Measured numbers

| Item | Result | How it was measured |
|---|---|---|
| Narration | about 259 words, 21 sentences, from 0.1 to about 64.1 seconds | caption OCR at 15 fps, matched to a cleaned transcript; 5 words filled in by interpolation |
| Pace | 4.0 words per second (about 243 words per minute), roughly 5.3 to 5.7 syllables per second | word count divided by the narration span |
| Pauses | only 1 pause of 0.18 seconds or more | `silencedetect` at -38 dB. The pauses were tightened in the edit |
| Voice | median pitch about 165 to 175 Hz | autocorrelation on voiced frames; two methods gave 164 and 176 Hz |
| Music | no music bed detected under the narration | the quietest point in each 2 seconds lies between -38 and -50 dB and is not flat |
| Closing sound | about 2.5 seconds of tonal sound at about -33 dB after the narration ends | level and spectral flatness in the tail of the file |
| Captions | one word at a time, centred, at about 52% of the screen height | a crop of the band y = 905 to 1105 px |
| Caption look | heavy rounded letters, white fill, thick dark blue outline, soft shadow; capital height about 75 px; first letter capitalised | observed in a 100% crop |
| Hard cuts | none | scene detection at thresholds 0.30 and 0.12, and spikes in the frame-to-frame difference |
| Camera moves | 22 fast moves, median 0.94 seconds, starting every 2.5 seconds or so | pixel difference between frames at 90x160 |
| Share of time | 27% moving fast, 33% drifting slowly, 40% almost still | the same |

## 3. Structure

The pattern is the same as in reference #1: turns of "but..." (a problem) and "so..." (a solution), in the second person. Three components are named after their function has been explained. The table lists the function of each beat, not its sentences; the column with the gist of each beat is left out of the repo version.

| # | Seconds | Function | Words | Words/s |
|---|---|---|---|---|
| 1 | 0.1-3.6 | hook | 18 | 5.1 |
| 2 | 3.6-7.7 | problem | 17 | 4.1 |
| 3 | 7.7-12.6 | solution | 21 | 4.3 |
| 4 | 12.6-19.0 | problem | 28 | 4.4 |
| 5 | 19.0-27.1 | solution + name | 33 | 4.1 |
| 6 | 27.1-30.4 | problem | 12 | 3.7 |
| 7 | 30.4-37.1 | solution + name | 31 | 4.6 |
| 8 | 37.1-44.9 | problem + solution + name | 31 | 3.9 |
| 9 | 44.9-50.9 | continuation | 19 | 3.2 |
| 10 | 50.9-54.5 | problem + solution | 17 | 4.7 |
| 11 | 54.5-59.7 | fact | 18 | 3.4 |
| 12 | 59.7-62.0 | addition | 7 | 3.1 |
| 13 | 62.0-66.6 | payoff | 7 | n/a |

The longest beat is 8 seconds. The first half alternates problem and solution every 4 to 8 seconds; the speaking pace slows a little at the fact and at the end.

## 4. Visual language

- One location for the whole video: the back yard of a two-storey house, striped lawn, terrace, trees, small props. Only the pool changes.
- A high three-quarter camera angle. The lower half of the screen is a cut face of soil with a rock texture; the pool is seen in section.
- Semi-realistic textured assets, not low-poly.
- No signs or labels inside the 3D world. Information is carried by the captions, white 3D arrows and colour (groundwater as a blue tint on the cut face, important components in red).
- Section close-ups of components: a valve on gravel, a filter tank cut open with its sand layer, a skimmer box with its basket.
- Flow is drawn with arrows and dots moving inside the pipes, not a fluid simulation.
- Close: the finished pool with people swimming, an umbrella, chairs, floats.

## 5. Compared with reference #1 and video #1

| Item | Reference #1 (septic, Indonesian) | Reference #2 (pool, English) | Our video #1 (septic, English) |
|---|---|---|---|
| Duration | 70.7 s | 66.6 s | 66.0 s |
| Frame rate | 30 | 60 | 30 |
| Narration | 175 words, about 149 words per minute | about 259 words, about 243 words per minute | 171 words, about 156 words per minute |
| Hard cuts | 9 | 0 | 14 shot boundaries (a mix of cuts and moves) |
| Captions | cumulative phrases of 1 to 4 words, at about 65% height | one word, at about 52% height | cumulative phrases, at 67.5% height |
| Text in the 3D world | yes | no | yes |
| Characters | a wooden mannequin | people in the final scene | an engineer mascot |
| Music | none seen | none detected; there is a closing sound | none |
| Loudness | -14.2 LUFS | -15.7 LUFS | -14.3 LUFS |

Lesson: the two references use the same story recipe in different packaging. Reference #2 is almost twice as dense in words, has no hard cuts, and shows one caption word at a time. Our video #1 is closer to reference #1.

## 6. Why the format works

1. The hook offers the simplest version of something complicated, then knocks it down at once.
2. Every solution creates the next problem, so there is always a reason to watch the next beat.
3. There is no dead air: the pauses are tightened and a new word appears on screen about every 0.25 seconds.
4. The camera moves to a new framing about every 2.5 seconds without cutting, so the viewer never loses their bearings.
5. The hook sentence returns at the end, and this time it is true.

## 7. What is taken and what is not

Taken, because this is the common format grammar of the genre:
- the "simplest version" premise in the hook (at the user's request);
- turns of problem and solution, addressed to "you";
- one sentence is one change on screen; a term is named after its function is clear;
- one location that keeps developing; a camera that moves without hard cuts;
- one-word captions in the middle of the screen; a close that repeats the hook.

Not taken:
- the sentences and clause structure of its script. Our script is written from sourced facts, not translated;
- the order of beats. In our script the floating pool and the hydrostatic valve are the climax at the end, and the chain "green water, filter, chlorine" is split up to be more accurate (the filter holds back dirt; the chlorine kills algae and germs);
- the analogies and jokes. Ours: a bucket, a giant bowl, green soup, a rubber duck, the 48 tons of weight that "disappear" when the pool is drained;
- the set design and props. Ours: a tropical house, a masonry wall, local plants, the mascot;
- the shape of the arrows and overlays, the exact caption font, the closing scene (ours: dusk with underwater lights).

## 8. Limits of this analysis

- The transcript was reconstructed from the captions, so the word count can be off by a few words.
- The speaker's gender or character cannot be determined from pitch alone.
- "No music bed detected" means there is no steady sound above about -45 dB between words. Very quiet music could escape this measurement.
- The quality of the motion (smooth or not) cannot be judged from still frames.
