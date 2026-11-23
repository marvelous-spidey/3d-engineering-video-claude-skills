# Video 01 — catatan produksi "How a Septic System Works" (EN)

21 November 2026 · video pertama, dibuat sebelum kit ada · berkasnya di `examples/video01-septic-system-en/`

Catatan ini versi repo: tautan hasil, ID media, nama, dan lokasi penyimpanan pribadi dihilangkan, dan bagian "Temuan setelah rilis" ditambahkan.

## Hasil

| Hal | Nilai |
|---|---|
| Format | 1080×1920, 30 fps, 66,0 detik, H.264 + AAC, 28,3 MB, −14,3 LUFS |
| Keluaran | video final dengan caption dan suara, plus master bersih (tanpa caption, tanpa suara) untuk mengganti caption atau menambah musik tanpa render ulang |
| Naskah | 171 kata, 16 baris, pola "masalah → solusi" orang kedua; isi dan kalimat ditulis sendiri, fakta dicek ke EPA |
| Suara | ElevenLabs v4 lewat Higgsfield, preset "Cillian" |
| Gambar | Scene Blender 710 objek dari satu file Python 902 baris (`septic_video.py`); caption per kata dibakar dengan PIL |
| Kredit Higgsfield | suara 4,37 + GPU 43,72 = 48,09 |

## Jalur yang benar-benar dipakai

1. Naskah Inggris + cek fakta (Claude).
2. Suara di Higgsfield, lalu waktu per kata diambil dengan faster-whisper di sandbox Higgsfield.
3. Scene + animasi ditulis sebagai kode di workspace Claude. Semua cue animasi dihitung dari waktu kata, bukan diketik manual.
4. Cek gambar di workspace Claude (CPU): ±300 still resolusi rendah dalam beberapa putaran perbaikan, sebelum GPU disewa.
5. Render di box GPU Higgsfield jenis `compute` (bukan Blender Studio): `bpy` 5.3.0 dipasang lewat `uv` + Python 3.13, Cycles OptiX.
6. Caption per kata dibakar dengan PIL, encode + gabung suara dengan ffmpeg, di box yang sama.
7. QA pada file final: contact sheet 20 frame, potongan 100% dua frame berurutan, ffprobe, loudness, dan transkripsi ulang audio final untuk cek sinkron.

## Angka terukur (menggantikan estimasi di plan)

| Hal | Terukur |
|---|---|
| Setup box (apt, uv, bpy, font, suara) | ±80 detik |
| Kecepatan render 1080×1920, 64 sampel + denoise, 1 proses | 1,7–1,9 detik/frame (32 sampel: 1,3–1,6) |
| 3 proses paralel di 1× L40S | 1.980 frame dalam 27 menit 20 detik; CPU box (4 vCPU) penuh, GPU hanya ±50% |
| Caption + encode 1.980 frame | ±3 menit |
| Total box menyala | 36 menit 57 detik = 43,72 kredit (batas yang disetujui: 150) |
| Suara 1.000-an karakter | 4,37 kredit (estimasi alat: 5,5) |

## Koreksi terhadap plan

- **Jaringan**: workspace Claude dan VM di komputer pengguna tidak bisa mengakses host file Higgsfield (host unggah dan CDN-nya). Akibatnya file video tidak bisa dikirim sebagai lampiran chat atau disalin ke folder lokal; hasil diserahkan sebagai link. Skrip dikirim ke box lewat sandbox Higgsfield → upload → unduh di box.
- **VM di komputer pengguna** adalah Linux, tidak bisa menjalankan Blender macOS. Rute "render di komputer sendiri" butuh Claude Code lokal, bukan sesi chat.
- **Engine**: Cycles di GPU sudah cukup cepat; EEVEE tidak diperlukan.
- **Rute render** terpilih: box `compute` + `bpy`. Blender Studio tidak dipakai.
- **Animatic sebagai gerbang review** dilewati karena pengguna meminta videonya langsung dibuat; gantinya cek still berlapis oleh Claude. Review manusia baru terjadi pada video jadi.

## Pelajaran untuk video berikutnya

- Pola yang berhasil: cue dari waktu kata, `grow/appear/show/travel` sebagai kosakata animasi, label otomatis mengikuti lebar teks, kamera `shot()` dengan gerak lalu drift.
- Artefak yang sempat muncul dan penyebabnya: objek "tumbuh" terlihat sebagai lembaran tipis sebelum waktunya (harus disembunyikan), noda transparan bertumpuk jadi gelap (batas pantulan transparan), bayangan tag yang menghadap kamera (matikan `visible_shadow`), angka "1" font bawaan Blender mirip huruf I (pakai Inter).
- 4 sampel + denoise menipu soal warna; untuk menilai warna pakai ≥16 sampel.
- Panggilan `gpu_rental_exec` yang menunggu >60 detik bisa gagal dengan Bad Gateway; jalankan kerja panjang dengan `nohup` lalu poll dengan perintah pendek.
- Box 4 vCPU membatasi kecepatan. Menambah core menaikkan harga per jam, jadi perlu persetujuan baru.

## Temuan setelah rilis (22 November 2026)

- Scan antar-frame pada master bersih menemukan 5 tersangka dari 1.980 frame, dan kelimanya sah: gerak cepat, puncak pantulan label yang baru muncul, dan kilau kecil di pipa.
- Beberapa caption muncul 0,3–0,5 detik sebelum katanya, terutama kata "and" setelah koma: mesin transkripsi menaruh awal kata di dalam jeda sebelumnya. `kit/audio/align.py` v1.0 menempelkan batas kata ke jeda untuk mencegahnya di video berikutnya.

## Yang belum dikerjakan

- Musik dan efek suara (versi ini hanya narasi). Bisa ditambahkan di atas master bersih tanpa GPU.
- Audio belum didengarkan Claude; yang dilakukan hanya pengukuran.
- Nama channel, watermark, dan cover.
- Versi Indonesia atau 16:9 dari scene yang sama.
