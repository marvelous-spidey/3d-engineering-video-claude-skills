---
name: higgsfield-blender-render
description: Renders a Blender animation (bpy, Cycles) on a rented Higgsfield GPU through to a finished video, with a frame scan, captions, encoding, colour and audio checks, upload, and strict credit rules.
---

# Rendering Blender on a rented Higgsfield GPU

The GPU box is billed per second while it is running. So everything that can be prepared for free is prepared first, and the box is shut down as soon as the final file has been verified.

This skill uses the kit (the `kit/` folder of the repo that holds this skill) and the job folder prepared by the `3d-engineering-video` skill.

## Credit rules

1. Before `gpu_rent`: show the price (`gpu_list_gpus`), the estimate and a hard limit, then wait for explicit approval. Approval covers one job.
2. After the test stills on the box, project the cost from the measured seconds per frame. Project it again from the frame count after 2 to 3 minutes of the full render: three processes sharing the box's CPU can be twice as slow per frame as a test still. If the projection exceeds the limit, stop and ask.
3. If something you find along the way forces rework, recalculate the projection and tell the user right away.
4. While the box is running, do only work that needs the box. Write documents after it is off.
5. Call `gpu_rental_stop` as soon as the final file is uploaded and verified, then check the real cost in `transactions`.

## Network map

The situation in Claude's cloud workspace when this skill was written (November 2026):

| From | Can reach | Cannot reach |
|---|---|---|
| Claude's workspace | package registries, GitHub | Higgsfield's CDN and upload host |
| Higgsfield sandbox (`sandbox_exec`, free) | the internet, GitHub, the Higgsfield CDN, upload URLs | the workspace |
| GPU box (`gpu_rental_exec`) | the internet, the Higgsfield CDN, upload URLs | the workspace |

In practice: files from the workspace go in through the sandbox as text (heredoc, at most about 25 KB per call, md5 checked for each file; send larger scripts in parts and join them). The kit code does not need to be sent that way, because the sandbox fetches it from GitHub. Pictures from the box are viewed through the sandbox (`image_paths`, at most 4 images and 512 KiB). The final video can only be delivered as a link.

Call rule: a command that waits longer than about 60 seconds fails with "Bad Gateway". Run long jobs with `nohup ... &` (box) or `background:true` (sandbox), then poll with short commands. Other pitfalls are in `~/kit/GUIDE.md` section 5.

## Steps

1. **Package the job in the sandbox.** The folder `/home/user/jobs/<name>/` already holds `vo_proc.wav` and `words.json` from the voice step. Send the job's own files that are missing or whose md5 differs: `job.env`, the scene script, `script.txt`, `keywords.txt`. Then add the kit code and the font:

   ```bash
   cd /home/user && { [ -d 3dv-repo ] || git clone --depth 1 https://github.com/davidalfasunarna/3d-engineering-video-claude-skills 3dv-repo; }
   bash 3dv-repo/kit/newjob.sh jobs/<name>
   ```

   `newjob.sh` never overwrites a file that belongs to the job. If the clone fails, send the kit code from the workspace with heredocs. Zip with `cd jobs/<name> && rm -f job.zip && python3 -m zipfile -c job.zip *`, request a URL with `media_upload` (a name ending in `.zip`), PUT from the sandbox with the header `If-None-Match: *`, then `media_confirm` (`type: file`).
2. **Rent.** `gpu_rent`: kind `compute`, `L40S`, 1 GPU, `auto_pause_minutes` 30.
3. **Unpack on the box.** `mkdir -p /workspace/<name> && cd /workspace/<name>`, download with `curl -fsSL -o job.zip <read url>`, and unpack with `python3 -c "import zipfile; zipfile.ZipFile('job.zip').extractall('.')"` (the box has no `unzip`). The job zip already contains the kit code, so the box needs no other source.
4. **Setup.** `mkdir -p logs`, then as a separate command `nohup bash setup.sh > logs/setup.log 2>&1 &`. It is done when the log contains `SETUP_DONE` (about 80 seconds). Do not chain `nohup` after `&&`.
5. **Test stills.** `. ./job.sh; KIT_DEVICE=GPU $PY $SCENE still 1080 1920 64 /root/st <2 or 3 key seconds>`. Look at the result, note the seconds per frame, and project the cost.
6. **Render and finish.** `bash render.sh`, then `nohup bash finish.sh > logs/finish.log 2>&1 &` and `nohup bash after.sh > logs/after.log 2>&1 &`. Both wait on their own: `finish.sh` waits for the last frame, and `after.sh` waits for `finish.sh` and for the file `urls.sh`.
7. **Upload URLs, near the end of the render.** Upload URLs work for only about one hour after they are issued, so do not request them before the render. When the render has about 10 minutes left, request four URLs with `media_upload` (final video, clean master, `sheets.zip`, `trips.zip`) and write them to `urls.sh` on the box as `U_FINAL`, `U_CLEAN`, `U_Z1`, `U_Z2`. Each URL can be used once, and `after.sh` deletes `urls.sh` after uploading. These URLs are temporary secrets: never copy them into a document, a production record or a repo.
8. **Monitor.** `ls /root/frames | wc -l; tail -1 logs/render_0.log`. When a third of the frames are done, run `. ./job.sh; $PY scan.py $FR $QA/scan $FRAMES $PROCS`. If suspects pile up in one process, or the black-pixel count spikes, look at an example with `trip_png.py` first: repeating motion (a turning engine, a flame) produces legitimate periodic suspects that can pile up in one process. If it turns out to be a defect, stop the render (`pkill -f "${PAT}anim"`) before burning more credits.
9. **Read the results.** After `FINISH_DONE` in `logs/finish.log`: the frame count is complete, the probe shows h264 1080x1920 30 fps yuv420p bt709, loudness is -14 LUFS within 1, the line `COLOUR OK` is present, and the scan summary is there. Look at the contact sheets (`sheets.zip`) and the suspect crops (`trips.zip`), then classify each suspect using `GUIDE.md` section 4. Look at the peak frame of each kind of flash (explosion, spark): a defect that lasts one frame does not show on a contact sheet.
10. **Partial fix.** If the scene script is fixed: run `scene_check.py` on the new script in the workspace, send the script, then `nohup bash rerender.sh "first-last ..." "control frames" > logs/rerender.log 2>&1 &`. Control frames lie outside the ranges: one before the first range and one just after each range. If a control frame differs, the fix changed something outside the ranges (a label left on screen, for example): investigate before encoding. Then run `finish.sh` and `after.sh` again and write `urls.sh` with new URLs.
11. **Verify outside the box.** `media_confirm`, then in the sandbox `bash final_check.sh <final url> <md5 from the box> <id|en>`: same md5, format, loudness, and the offset between spoken words and captions (median about 0.00 seconds, 95th percentile under about 0.1 seconds).
12. **Shut down.** `gpu_rental_stop`, check `transactions`, record the real cost.

## What to report

The link and `media_id` of the final video and of the clean master, the md5, duration, loudness, the scan result (number of suspects and what they were), how long the box ran and what it cost, and anything that deviated from the plan.

## Test status

This workflow has rendered three videos (November 2026). The `box/` scripts of kit 1.0 rendered the third video on a rented L40S from start to upload, including two partial re-renders. The kit 1.1 changes to `after.sh` (waiting for `urls.sh`) and `rerender.sh` (sorting the control frames) have been tested on CPU only, so on first use read `logs/after.log` and `logs/rerender.log` before continuing. Fetching the kit with `git clone` in the sandbox has not been used in a production yet.
