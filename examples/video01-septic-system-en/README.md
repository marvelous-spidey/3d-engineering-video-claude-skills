# Contoh 01 — How a Septic System Works (EN)

Short 9:16, 1080×1920, 30 fps, 66 detik, narasi bahasa Inggris, caption frasa yang terisi kata demi kata, potongan kamera keras per beat. Ini video pertama, dibuat sebelum kit ada: `septic_video.py` berdiri sendiri (902 baris) dan menjadi sumber fungsi `kit/explainer_kit.py`.

![Contact sheet 1](preview/contact_sheet_1.jpg)
![Contact sheet 2](preview/contact_sheet_2.jpg)

## Isi

| Berkas | Isi |
|---|---|
| `septic_video.py` | seluruh scene dan animasi, 710 objek. Waktu kata narasi tertanam di daftar `WORDS` |
| `script_en.md` | naskah, gambar per baris, frasa caption dengan waktunya, cek fakta dan sumber, penyederhanaan yang disengaja |
| `job.env`, `script.txt`, `words.json` | berkas job untuk `kit/captions.py` gaya `phrases`. Tanda ` / ` di `script.txt` menandai batas frasa; hasilnya 66 frasa dengan teks dan waktu yang sama dengan video aslinya |
| `preview/` | contact sheet dari render pratinjau CPU dengan caption |

File suara tidak disertakan.

## Mencoba tanpa kredit

```bash
cp -r examples/video01-septic-system-en ~/jobs/septic && bash kit/newjob.sh ~/jobs/septic && cd ~/jobs/septic
python3 septic_video.py still 540 960 16 st 21.3 37.6 61.5       # still pada detik itu, CPU
python3 captions.py test st/t_03760.png 37.6 st/c_03760.png      # caption gaya phrases di atas still
python3 septic_video.py blend 1080 1920 64 septic.blend          # simpan scene untuk dibuka di Blender 5.3
```

Skrip ini tidak memakai `job.env` dan tidak mengenal mode `list`, jadi tidak cocok dengan skrip `kit/box/` versi 1.0. Untuk video baru, mulai dari `kit/scene_template.py` atau dari contoh 02; pakai skrip ini sebagai bacaan untuk potongan keras, label di bidang potong, dan truk.

## Angka produksi (21 November 2026)

| Hal | Nilai |
|---|---|
| Render | 1.980 frame, Cycles OptiX 64 sampel + denoise, 1× L40S sewaan, 3 proses paralel: 27 menit 20 detik |
| Suara | ElevenLabs v4 lewat Higgsfield, preset "Cillian", 171 kata, 64,4 detik |
| Kredit Higgsfield | suara 4,37 + GPU 43,72 = 48,09 |

Catatan lengkapnya ada di [`docs/video01-production-record.md`](../../docs/video01-production-record.md).

## Batas

- Hanya narasi; tanpa musik dan efek suara.
- Beberapa caption muncul 0,3–0,5 detik sebelum katanya (kata "and" setelah koma). Penyebabnya sudah diperbaiki di `kit/audio/align.py` v1.0; `words.json` di sini sengaja dibiarkan sama dengan produksi.
- Video ini dirender dengan persistent data Cycles menyala. Kit sekarang mematikannya, karena pada video kedua opsi itu merusak sebagian frame.
