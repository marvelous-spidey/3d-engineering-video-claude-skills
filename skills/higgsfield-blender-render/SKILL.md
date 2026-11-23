---
name: higgsfield-blender-render
description: Merender animasi Blender (bpy, Cycles) di box GPU sewaan Higgsfield sampai menjadi file video, dengan scan semua frame, caption, encode, cek warna dan suara, unggah, dan aturan kredit yang ketat.
---

# Render Blender di GPU sewaan Higgsfield

Box GPU ditagih per detik selama menyala. Karena itu semua yang bisa disiapkan gratis disiapkan dulu, dan box dimatikan begitu file final terverifikasi.

Skill ini memakai kit (folder `kit/` di repo yang memuat skill ini) dan folder job yang disiapkan skill `3d-engineering-video`.

## Aturan kredit

1. Sebelum `gpu_rent`: tunjukkan harga (`gpu_list_gpus`), estimasi, dan batas keras, lalu tunggu persetujuan eksplisit. Persetujuan berlaku untuk satu pekerjaan.
2. Setelah still uji di box, hitung proyeksi dari detik per frame yang terukur, lalu hitung lagi dari jumlah frame setelah 2–3 menit render penuh: tiga proses yang berbagi CPU box bisa dua kali lebih lambat per frame daripada still uji. Kalau melewati batas, berhenti dan tanya.
3. Kalau temuan di tengah jalan memaksa kerja ulang, hitung ulang proyeksi dan kabari pengguna saat itu juga.
4. Selama box menyala, kerjakan hanya yang butuh box. Dokumen ditulis setelah box mati.
5. `gpu_rental_stop` segera setelah file final terunggah dan terverifikasi, lalu cek biaya nyata di `transactions`.

## Peta jaringan

Keadaan di workspace cloud Claude saat skill ini ditulis (November 2026):

| Dari | Bisa menjangkau | Tidak bisa |
|---|---|---|
| Workspace Claude | registry paket, GitHub | CDN dan unggahan Higgsfield |
| Sandbox Higgsfield (`sandbox_exec`, gratis) | internet, GitHub, CDN Higgsfield, URL unggah | workspace |
| Box GPU (`gpu_rental_exec`) | internet, CDN Higgsfield, URL unggah | workspace |

Akibatnya: berkas dari workspace masuk lewat sandbox sebagai teks (heredoc, paling banyak ±25 KB per panggilan, cek md5 tiap berkas; skrip yang lebih besar dikirim per bagian lalu digabung). Kode kit tidak perlu dikirim begitu: sandbox mengambilnya sendiri dari GitHub. Gambar dari box dilihat lewat sandbox (`image_paths`, paling banyak 4 gambar dan 512 KiB). Video final hanya bisa diserahkan sebagai link.

Aturan panggilan: perintah yang menunggu lebih dari ±60 detik gagal dengan "Bad Gateway". Pekerjaan panjang dijalankan dengan `nohup … &` (box) atau `background:true` (sandbox), lalu dipantau dengan perintah pendek. Jebakan lain ada di `~/kit/GUIDE.md` bagian 5.

## Langkah

1. **Paket job di sandbox.** Folder `/home/user/jobs/<nama>/` sudah berisi `vo_proc.wav` dan `words.json` dari langkah suara. Kirim ke sana berkas milik job yang belum ada atau md5-nya berbeda: `job.env`, skrip scene, `script.txt`, `keywords.txt`. Lalu tambahkan kode kit dan font:

   ```bash
   cd /home/user && { [ -d 3dv-repo ] || git clone --depth 1 https://github.com/davidalfasunarna/3d-engineering-video-claude-skills 3dv-repo; }
   bash 3dv-repo/kit/newjob.sh jobs/<nama>
   ```

   `newjob.sh` tidak pernah menimpa berkas milik job. Kalau clone gagal, kirim kode kit dari workspace dengan heredoc. Zip dengan `cd jobs/<nama> && rm -f job.zip && python3 -m zipfile -c job.zip *`, minta URL dengan `media_upload` (nama berakhiran `.zip`), PUT dari sandbox dengan header `If-None-Match: *`, lalu `media_confirm` (`type: file`).
2. **Sewa.** `gpu_rent`: jenis `compute`, `L40S`, 1 GPU, `auto_pause_minutes` 30.
3. **Buka paket di box.** `mkdir -p /workspace/<nama> && cd /workspace/<nama>`, unduh dengan `curl -fsSL -o job.zip <url baca>`, buka dengan `python3 -c "import zipfile; zipfile.ZipFile('job.zip').extractall('.')"` (box tidak punya `unzip`). Zip job sudah memuat kode kit, jadi box tidak butuh sumber lain.
4. **Setup.** `mkdir -p logs` lalu, sebagai perintah tersendiri, `nohup bash setup.sh > logs/setup.log 2>&1 &`. Selesai bila log memuat `SETUP_DONE` (±80 detik). Jangan merantai `nohup` di belakang `&&`.
5. **Still uji.** `. ./job.sh; KIT_DEVICE=GPU $PY $SCENE still 1080 1920 64 /root/st <2–3 detik kunci>`. Lihat hasilnya, catat detik per frame, hitung proyeksi biaya.
6. **Render dan penyelesaian.** `bash render.sh`, lalu `nohup bash finish.sh > logs/finish.log 2>&1 &` dan `nohup bash after.sh > logs/after.log 2>&1 &`. Keduanya menunggu sendiri: `finish.sh` menunggu frame terakhir, `after.sh` menunggu `finish.sh` dan berkas `urls.sh`.
7. **URL unggah, menjelang render selesai.** URL unggah hanya hidup ±1 jam sejak diminta, jadi jangan memintanya sebelum render. Saat render tinggal ±10 menit, minta empat URL dengan `media_upload` (video final, master bersih, `sheets.zip`, `trips.zip`) dan tulis ke `urls.sh` di box sebagai `U_FINAL`, `U_CLEAN`, `U_Z1`, `U_Z2`. Tiap URL hanya bisa dipakai sekali, dan `after.sh` menghapus `urls.sh` setelah mengunggah. URL ini rahasia sementara: jangan disalin ke dokumen, catatan produksi, atau repo.
8. **Pantau.** `ls /root/frames | wc -l; tail -1 logs/render_0.log`. Saat sepertiga frame selesai, jalankan `. ./job.sh; $PY scan.py $FR $QA/scan $FRAMES $PROCS`. Kalau tersangka menumpuk di satu proses atau piksel hitam melonjak, lihat dulu contohnya dengan `trip_png.py`: gerak berulang (mesin berputar, nyala) memberi tersangka sah yang periodik dan bisa menumpuk di satu proses. Kalau ternyata cacat, hentikan render (`pkill -f "${PAT}anim"`) sebelum membakar kredit lebih jauh.
9. **Baca hasil.** Setelah `FINISH_DONE` di `logs/finish.log`: jumlah frame lengkap, probe menunjukkan h264 1080×1920 30 fps yuv420p bt709, kenyaringan −14 ±1 LUFS, baris `COLOUR OK`, dan ringkasan scan. Lihat contact sheet (`sheets.zip`) dan potongan tersangka (`trips.zip`), lalu golongkan tiap tersangka menurut `GUIDE.md` bagian 4. Lihat frame puncak tiap kelompok kilat (ledakan, percikan): cacat yang hanya hidup 1 frame lolos dari contact sheet.
10. **Perbaikan sebagian.** Bila skrip scene diperbaiki: jalankan `scene_check.py` pada skrip baru di workspace, kirim skrip itu, lalu `nohup bash rerender.sh "awal-akhir …" "frame kontrol" > logs/rerender.log 2>&1 &`. Frame kontrol berada di luar rentang: satu sebelum rentang pertama dan satu tepat sesudah tiap rentang. Kalau ada frame kontrol yang berbeda, perbaikannya mengubah sesuatu di luar rentang (misalnya label yang tertinggal): selidiki sebelum encode. Sesudah itu jalankan `finish.sh` dan `after.sh` lagi dan tulis `urls.sh` dengan URL baru.
11. **Verifikasi di luar box.** `media_confirm`, lalu di sandbox `bash final_check.sh <url final> <md5 dari box> <id|en>`: md5 sama, format, kenyaringan, dan selisih waktu kata terhadap caption (median ±0,00 detik, p95 di bawah ±0,1 detik).
12. **Matikan.** `gpu_rental_stop`, cek `transactions`, catat biaya nyata.

## Yang dilaporkan

Link dan `media_id` video final dan master bersih, md5, durasi, kenyaringan, hasil scan (jumlah tersangka dan golongannya), lama box menyala dan kreditnya, serta apa pun yang menyimpang dari rencana.

## Status uji

Alur ini merender tiga video (November 2026). Skrip `box/` kit 1.0 merender video ketiga di box L40S sewaan dari awal sampai unggah, termasuk dua render ulang sebagian. Perubahan kit 1.1 pada `after.sh` (menunggu `urls.sh`) dan `rerender.sh` (mengurutkan frame kontrol) baru diuji di CPU; pada pemakaian pertama, baca `logs/after.log` dan `logs/rerender.log` sebelum melanjutkan. Mengambil kit dengan `git clone` di sandbox belum pernah dipakai dalam produksi.
