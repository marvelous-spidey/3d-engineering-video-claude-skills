# 3D Engineering Video: Claude skills for short 3D engineering explainers

Three skills for Claude and a code kit that produce short vertical videos (9:16, 60 to 75 seconds) explaining how a machine or an engineered system works. The 3D cutaway is built from Blender code, the narration is an AI voice, captions appear word by word, and every motion is timed to the words of the narration.

Three videos have been made this way so far: "How a Septic System Works" (English), "Cara kerja kolam renang" (how a swimming pool works, Indonesian), and "Mesin CR-V tembus seribu tenaga kuda" (how a CR-V engine reaches 1,000 hp, Indonesian, made from an English reference video).

![How a CR-V engine reaches 1,000 hp](examples/video03-crv-engine-id/preview/contact_sheet_1.jpg)
![How a swimming pool works](examples/video02-swimming-pool-id/preview/contact_sheet_1.jpg)
![How a Septic System Works](examples/video01-septic-system-en/preview/contact_sheet_1.jpg)

## What you can make

| You give Claude | Claude makes |
|---|---|
| A script in English | a video in English; your script is used as written |
| A script in Indonesian | a video in Indonesian |
| A reference video (English or Indonesian) | a new video in the other language, with a script rewritten from facts that were checked independently |
| Only a topic | Claude researches it, writes the script, then makes the video |

English and Indonesian are the two languages that have been tested.

## What you need

1. **Claude with skills and code execution turned on.** The skills run in Claude's own Linux workspace. You do not need Blender or a GPU on your computer. See [Use skills in Claude](https://support.claude.com/en/articles/12512180).
2. **A paid Higgsfield account with credits, connected to Claude as an MCP connector.** Higgsfield provides the voice (ElevenLabs v4), a sandbox for audio processing, and a rented GPU for rendering. Setup is described on the [Higgsfield MCP page](https://higgsfield.ai/mcp) and in its [help center](https://higgsfield.ai/creator-hub/help-center/integrations/how-do-i-connect-higgsfield-to-claude).

There is no API key to install. Higgsfield is connected through the connector, with your own account login.

## Install

1. Connect Higgsfield to Claude (links above).
2. Download the three ZIP files in [`dist/`](dist/), one per skill.
3. In Claude, open **Customize > Skills**, choose **+**, then **Create skill > Upload a skill**, and upload the ZIP files one at a time. Turn all three on. The [Claude help article](https://support.claude.com/en/articles/12512180) has the details.

You do not install the kit yourself. On first use, the skill clones this repo and installs Blender as a Python module in Claude's workspace (about 1 GB, a few minutes).

If you fork this repo, replace the repo address in the three `SKILL.md` files and in `kit/README.md` with your fork's address, then rebuild the ZIP files with `python3 dist/make_dist.py`.

## Use

Ask in plain words, for example:

- "Make a 3D engineering video from this script: ..."
- "Buat video 3D engineering dari naskah ini: ..." (the same request in Indonesian)
- (with a video attached) "Study this video, then make a similar one in Indonesian."

What happens next:

1. Claude tidies the script, checks its facts, and drafts what each line will show.
2. Claude stops and asks you to approve a credit limit. No credits are spent before this point.
3. The voice is generated, the timing of every word is measured, and the scene is written as code and checked with CPU stills and a render-free scene checker.
4. A GPU is rented, every frame is rendered and checked automatically, captions are burned in, the result is uploaded, and the GPU is shut down.
5. You get a link to the final video, a clean master without captions or sound, and a cost report.

## Cost

In Higgsfield credits, measured in November 2026. Prices change, so Claude checks them again before asking for approval.

| Video | Voice | GPU | Total | Notes |
|---|---|---|---|---|
| #1, 66 s | 4.37 | 43.72 | 48.09 | rendered once |
| #2, 68.4 s | 16.66 | 132.29 | 148.95 | includes a voice audition, one discarded render (about 33) and one partial re-render (about 20) |
| #3, 75.9 s | 6.44 | 110.90 | 117.34 | one voice take; includes two partial re-renders (about 26) |

A video of about 70 seconds with no rework costs 75 to 85 GPU credits (L40S at 71 credits per hour) plus about 6 credits per voice take. Two of the three videos needed a partial re-render, so set the limit at about 1.6 times the estimate.

## What is in this repo

| Folder | Contents |
|---|---|
| [`skills/`](skills/) | three `SKILL.md` files: `3d-engineering-video` (the main workflow), `reference-short-teardown` (analysing a reference video), `higgsfield-blender-render` (rendering on a rented GPU) |
| [`dist/`](dist/) | one ZIP per skill, ready to upload to Claude |
| [`kit/`](kit/) | the code: Blender scene builder, captions, audio tools, render and QA scripts. Start with [`kit/README.md`](kit/README.md) and [`kit/GUIDE.md`](kit/GUIDE.md) |
| [`examples/`](examples/) | three real jobs: scene script, narration script, word timings, fact check |
| [`docs/`](docs/) | production records of the three videos, two sample reference teardowns, and the runbook (how the workflow evolved, with a list of pitfalls) |

## Before you rely on it

- **It is young.** Only three videos have been made with this workflow, and only the third used the kit and the skills from start to finish. Kit 1.1 contains the lessons from that video. The two scripts changed in 1.1 have been tested on CPU only, and fetching the kit with `git clone` from this repo has not been used in a production yet.
- **Rework is normal.** Two of the three videos needed a partial re-render because of animation mistakes that only showed up after the full render. The scene checker in kit 1.1 exists to catch that kind of mistake before the GPU is rented.
- **Claude cannot hear or watch.** It checks still frames and measurements (format, loudness, word sync). Listen to the result and watch it yourself before you publish.
- **Narration only.** Music and sound effects are not made. The clean master is there so you can add them.
- **The reference video is not copied.** Only its format is followed: length, pace, caption style, camera pattern. The script is written from scratch using facts that were checked independently, and the reference's footage, audio and characters are not used.
- **One format.** 1080x1920 at 30 fps.
- **Tested environment.** The Claude app with a cloud workspace and the Higgsfield MCP connector. Claude Code and the API have not been tested.
- **Narration and on-screen text of the Indonesian examples are in Indonesian.** They are the content of those videos. Everything else in the repo is in English.

## Security

This repo contains no credentials, tokens or account data. During a production, Claude creates single-use upload URLs in your Higgsfield account. Those URLs live only on the render box and must never be saved in the repo or in a document (`.gitignore` already excludes `urls.sh`).

## License and credits

Licensed under [GPL-3.0-or-later](LICENSE). © 2026 David Alfa Sunarna. Code and documents were written together with Claude (Anthropic).

GPL was chosen because the scene scripts call Blender's Python API, and Blender asks that such scripts be shared under a GPL-compatible license ([Blender license](https://www.blender.org/about/license/)). The license covers the code and documents in this repo, not the videos you make with them. The voice and the rendering are subject to Higgsfield's terms of service.

Blender (`bpy`), ffmpeg, faster-whisper, and the Inter and Baloo 2 fonts are installed or downloaded when needed and are not included in this repo. Higgsfield and ElevenLabs are third-party services with their own terms. This project is not affiliated with Anthropic, Higgsfield, ElevenLabs or the Blender Foundation.
