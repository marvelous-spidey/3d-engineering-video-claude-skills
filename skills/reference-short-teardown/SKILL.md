---
name: reference-short-teardown
description: Breaks a reference short (TikTok, Reels, Shorts) down into measured style numbers (pace, captions, camera, beat structure, audio) and a list of what may be borrowed from its format.
---

# Reference video teardown

There are two goals: numbers you can use to make your own video in a similar style, and a clear line between the format (which may be followed) and someone else's work (which is not copied).

## Files

- The reference is usually an upload in the chat (`/mnt/user-data/uploads/...`) or a file in a folder the user has connected. Work from a copy in a working folder, for example `~/ref/src.mp4`. In the Claude app, do not pass third-party files through `/mnt/user-data/outputs`, because media files there are modified (a C2PA manifest is added).
- The tool is `~/kit/ref_teardown.py`. Install the kit as in step 0 of the `3d-engineering-video` skill (`git clone` the repo that holds this skill, then copy its `kit/` folder). It needs ffmpeg, tesseract, and the Python packages numpy, pillow, scipy and pytesseract.

## Steps

```bash
T=~/kit/ref_teardown.py; cd ~/ref
python3 -I $T probe    src.mp4                                    # size, fps, duration, audio
python3 -I $T sheets   src.mp4 out/sheets 1 6 6                   # contact sheets, 1 frame per second
python3 -I $T captions src.mp4 out/cap <top_px> <height_px> 15    # OCR of the caption band -> out/cap/ocr_words.json
python3 -I $T pace     out/cap/ocr_words.json transcript.txt      # words per second, length of the caption cards
python3 -I $T motion   src.mp4                                    # hard cuts or continuous camera motion
python3 -I $T audio    src.mp4                                    # loudness, pauses, whether there is music
```

1. Look at the contact sheets yourself to find the caption band (`top_px`, `height_px`), then at 6 to 8 larger key frames to read the visual language: set, camera angle, colour, characters, how tags appear.
2. Before `pace`, clean the OCR output into `transcript.txt` (sentences separated by `|`). This is a working file for measuring pace and understanding the content. It is not archived and not shared.
3. For a video without burned-in captions, ask the user to upload it through Higgsfield's `media_upload_widget` so its audio can be transcribed in the sandbox, or ask for a summary of what it says.
4. If `motion` finds no cuts, the camera moves continuously. That is a finding, not a tool failure.
5. A busy background makes the caption OCR noisy. Use the result to measure pace, state the uncertainty (for example plus or minus 5 words) under "Limits of the analysis", and read beat timings from the contact sheet (to about half a second).
6. If `audio` finds no pauses and the noise floor stays high (about -33 dB in reference #3), there is music or effects under the narration. Record it as a finding. What it is cannot be identified from here.

## Output document

Write `videoNN-reference-analysis.md` where the user keeps their archive (a claude.ai Project, a local folder, or their own repo) with the sections below. Finished examples: `docs/video02-reference-analysis.md` and `docs/video03-reference-analysis.md` in the repo.

1. **Measured numbers**: size, fps, duration, word count, words per second, number and length of caption cards, number of cuts, loudness, whether there is music.
2. **Beat structure**: each beat with its timing, its word count and its function (hook, problem, solution, surprising fact, close). Describe the function in your own words, not as a quote.
3. **Visual language**: set, camera, colour, characters, tags, caption style.
4. **Taken / not taken**: only the format grammar is taken (length, pace, caption style, camera pattern, beat functions). Not taken: sentences, distinctive analogies, characters, footage, audio, set layout.
5. **Production implications**: `CAPTION_STYLE` (`cards` for one or two words per card, `phrases` for phrases), hard cuts or one camera move, target duration, and the script length budget in the target language (English: duration x 2.7 words; Indonesian: duration x 6.3 syllables).
6. **Limits of the analysis**: what could not be measured (for example music hidden under narration) and what is only an estimate.

## Rules

- The creator may be named as the source of the reference. Their script is not written out in any document. A quote, if needed at all, is a few words.
- Facts in the reference video are leads, not sources. The new video uses facts that were checked independently.
- If the user asked only for an analysis, stop at the output document and its summary. Production belongs to the `3d-engineering-video` skill.
