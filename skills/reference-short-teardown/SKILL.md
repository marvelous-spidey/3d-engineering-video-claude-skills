---
name: reference-short-teardown
description: Membedah video pendek referensi (TikTok, Reels, Shorts) menjadi angka gaya yang terukur, yaitu tempo, caption, kamera, struktur beat, dan audio, plus daftar apa yang boleh diambil dari formatnya.
---

# Bedah video referensi

Tujuannya dua: angka yang bisa dipakai untuk membuat video sendiri dengan gaya serupa, dan batas yang jelas antara format (boleh diikuti) dan karya orang lain (tidak disalin).

## Berkas

- Referensi biasanya unggahan di chat (`/mnt/user-data/uploads/…`) atau berkas di folder pengguna yang tersambung. Kerjakan dari salinan di folder kerja, misalnya `~/ref/src.mp4`. Di aplikasi Claude, jangan lewatkan file pihak ketiga melalui `/mnt/user-data/outputs`, karena file media di sana diubah (manifest C2PA).
- Alatnya `~/kit/ref_teardown.py`. Pasang kit seperti di skill `3d-engineering-video` langkah 0 (`git clone` repo yang memuat skill ini, lalu salin folder `kit/`). Butuh ffmpeg, tesseract, dan paket Python numpy, pillow, scipy, pytesseract.

## Langkah

```bash
T=~/kit/ref_teardown.py; cd ~/ref
python3 -I $T probe    src.mp4                                    # ukuran, fps, durasi, audio
python3 -I $T sheets   src.mp4 out/sheets 1 6 6                   # contact sheet, 1 frame per detik
python3 -I $T captions src.mp4 out/cap <atas_px> <tinggi_px> 15   # OCR pita caption -> out/cap/ocr_words.json
python3 -I $T pace     out/cap/ocr_words.json transkrip.txt       # kata per detik, panjang kartu caption
python3 -I $T motion   src.mp4                                    # potongan keras atau gerak sinambung
python3 -I $T audio    src.mp4                                    # kenyaringan, jeda, ada tidaknya musik
```

1. Lihat sendiri contact sheet untuk menentukan pita caption (`atas_px`, `tinggi_px`), lalu 6–8 frame kunci berukuran lebih besar untuk membaca bahasa visualnya: set, sudut kamera, warna, karakter, cara tag muncul.
2. Sebelum `pace`, rapikan hasil OCR menjadi `transkrip.txt` (kalimat dipisah `|`). Ini berkas kerja untuk menghitung tempo dan memahami isi; tidak diarsipkan dan tidak dibagikan.
3. Video tanpa caption terbakar: minta pengguna mengunggahnya lewat `media_upload_widget` Higgsfield supaya audionya bisa ditranskripsi di sandbox, atau minta ringkasan isinya.
4. `motion` yang tidak menemukan potongan berarti kamera bergerak sinambung. Itu temuan, bukan kegagalan alat.
5. Latar yang ramai membuat OCR caption berisik. Pakai hasilnya untuk menghitung tempo, tulis ketidakpastiannya (misalnya ±5 kata) di "Batas analisa", dan baca waktu beat dari contact sheet (±0,5 detik).
6. `audio` yang tidak menemukan jeda dengan lantai suara yang tetap tinggi (±−33 dB pada referensi #3) berarti ada musik atau efek di bawah narasi. Catat sebagai temuan; isinya tidak bisa dikenali dari sini.

## Dokumen hasil

Tulis `videoNN-reference-analysis.md` di tempat arsip pengguna (Project claude.ai, folder lokal, atau repo miliknya) dengan bagian berikut. Contoh jadi: `docs/video02-reference-analysis.md` dan `docs/video03-reference-analysis.md` di repo.

1. **Angka terukur**: ukuran, fps, durasi, jumlah kata, kata per detik, jumlah dan panjang kartu caption, jumlah potongan, kenyaringan, ada tidaknya musik.
2. **Struktur beat**: tiap beat dengan waktunya, jumlah katanya, dan fungsinya (hook, masalah, solusi, fakta kejutan, penutup). Fungsi ditulis dengan kata sendiri, bukan kutipan.
3. **Bahasa visual**: set, kamera, warna, karakter, tag, gaya caption.
4. **Diambil / tidak diambil**: yang diambil hanya tata bahasa format (durasi, tempo, gaya caption, pola kamera, fungsi beat). Yang tidak diambil: kalimat, perumpamaan khas, karakter, footage, audio, susunan set.
5. **Implikasi produksi**: `CAPTION_STYLE` (`cards` untuk 1–2 kata per kartu, `phrases` untuk frasa), potongan keras atau satu gerak kamera, target durasi, dan anggaran panjang naskah dalam bahasa tujuan (Indonesia: durasi × 6,3 suku kata; Inggris: durasi × 2,7 kata).
6. **Batas analisa**: apa yang tidak terukur (misalnya musik yang tertutup narasi) dan apa yang hanya perkiraan.

## Aturan

- Nama kreator boleh disebut sebagai sumber referensi. Naskahnya tidak ditulis ulang di dokumen mana pun; kutipan, kalau perlu, hanya beberapa kata.
- Fakta di video referensi diperlakukan sebagai petunjuk, bukan sumber. Video baru memakai fakta yang dicek sendiri.
- Kalau pengguna hanya meminta analisa, berhenti di dokumen hasil dan ringkasannya. Produksi adalah urusan skill `3d-engineering-video`.
