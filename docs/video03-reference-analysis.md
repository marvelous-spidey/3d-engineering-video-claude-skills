# Video 03 — bedah video contoh (mesin turbo, bahasa Inggris)

23 November 2026 · contoh keluaran skill `reference-short-teardown` · alat ukurnya `kit/ref_teardown.py`

Catatan ini versi repo: nama file dan sidik file video referensi dihilangkan. Naskah video referensi tidak pernah dicatat di sini; tabel struktur hanya memuat fungsi tiap beat.

Claude tidak bisa menonton gerak atau mendengar audio. Semua isi dokumen ini berasal dari frame diam, pembacaan caption (OCR), dan pengukuran sinyal.

## 1. Angka terukur

| Hal | Nilai |
|---|---|
| Sumber | video pendek berbahasa Inggris tentang mesin empat silinder turbo bertenaga 1.000 hp, diberikan pengguna sebagai contoh format (nama kreator tidak tercatat pada file yang dibedah) |
| Gambar | H.264 720×1280, 30 fps asli (frame kembar 0,5%), 2.371 frame, 79,0 detik |
| Suara | AAC 44,1 kHz stereo, −14,1 LUFS, rentang 1,8 LU |
| Narasi | ±221 kata dalam 77,4 detik = ±2,9 kata per detik, 15 kalimat, suara pria (nada median 152 Hz) |
| Jeda | tidak ada jeda ≥ 0,18 detik di bawah −38 dB; lantai suara ±−33 dB, jadi ada alas suara (musik atau efek) di bawah narasi |
| Caption | frasa 2–3 kata di ±78% tinggi layar, huruf putih membulat bergaris tepi gelap; kata yang belum diucapkan tampil redup lalu terisi |
| Kamera | tanpa potongan keras; 15 gerak cepat, median 3,1 detik per gerak; 82% waktu kamera bergerak cepat, 17% hanyut pelan |

Jumlah kata dihitung dari transkrip kerja hasil OCR caption; selisih beberapa kata mungkin. File video referensi tidak disertakan di repo.

## 2. Struktur beat

Waktu dibaca dari contact sheet 1 frame per detik (±0,5 detik). Tabel mencatat fungsi tiap beat, bukan kalimat atau isinya.

| # | Detik | Fungsi | Kata |
|---|---|---|---|
| 1 | 0–7 | hook | 17 |
| 2 | 7–11 | masalah | 12 |
| 3 | 11–16,5 | solusi | 16 |
| 4 | 16,5–22 | masalah | 19 |
| 5 | 22–25 | solusi | 7 |
| 6 | 25–31 | masalah | 16 |
| 7 | 31–38 | solusi | 20 |
| 8 | 38–42,5 | penamaan | 9 |
| 9 | 42,5–49 | masalah | 18 |
| 10 | 49–54 | solusi | 15 |
| 11 | 54–61 | masalah | 20 |
| 12 | 61–66 | solusi | 13 |
| 13 | 66–69 | pelengkap | 11 |
| 14 | 69–74 | hasil | 16 |
| 15 | 74–78 | penutup | 12 |

Pola: hook, lima pasang masalah → solusi dengan taruhan yang naik, satu beat penamaan di tengah, lalu hasil dan rekap. Ini tata bahasa yang sama dengan referensi #2.

## 3. Bahasa visual

- **Set**: satu mesin di dudukan beroda, di dalam bengkel.
- **Model**: sangat rinci dan mendekati foto. Bagian dalam dibuka dengan bidang potong berwarna.
- **Kamera**: mengorbit mesin, lalu masuk ke bidang potong untuk tiap masalah, keluar lagi untuk tiap solusi; ada blur gerak.
- **Tag**: label dengan garis penunjuk; warna lain untuk bahaya. Angka tampil sebagai alat ukur digital.
- **Gerak**: komponen bergerak dan bertukar di tempat, kilat pada kegagalan.
- **Tanpa karakter** manusia atau maskot.

## 4. Diambil / tidak diambil

Diambil (tata bahasa format):

- topik dan panjang (±75–80 detik), tempo padat tanpa jeda;
- caption frasa 2–3 kata yang terisi per kata;
- satu objek di satu set, kamera sinambung yang masuk dan keluar bidang potong;
- angka sebagai alat ukur di layar;
- rantai masalah → solusi dan penutup yang kembali ke angka awal.

Tidak diambil:

- kalimat, perumpamaan, dan urutan detail naskahnya; naskah kita disusun ulang menjadi "tiga musuh" (tekanan, putaran, panas);
- model mesin, set, dan propertinya; mesin kita dibangun sendiri dari kode;
- palet warna dan gaya tag; kita memakai bidang potong kuning dan tag gaya seri sendiri;
- footage, audio, musik, dan efek teks;
- angka-angkanya: tiap angka di naskah kita dicek sendiri (lihat `examples/video03-mesin-crv-id/script_id.md`).

## 5. Implikasi produksi

| Hal | Pilihan |
|---|---|
| `CAPTION_STYLE` | `phrases` |
| Kamera | satu gerak sinambung, tanpa potongan keras (seperti video #2) |
| Target durasi | 73–78 detik |
| Anggaran naskah Indonesia | 79 × 6,3 ≈ 500 suku kata paling banyak; naskah yang dipakai ±459 suku kata |
| Hal baru untuk scene | gerak engkol-piston yang dipanggang per frame, per (heliks), alat ukur dan penghitung angka, lampu ruang dalam, material logam |
| Risiko terbesar | tingkat rincian model: model referensi jauh lebih rinci daripada yang bisa dibangun dari bentuk dasar |

## 6. Batas analisa

- Musik atau efek di bawah narasi terdeteksi dari lantai suara, tetapi tidak bisa dipisahkan atau dikenali.
- Waktu beat dibaca per detik, bukan per frame.
- OCR caption berisik (latar ramai); jumlah kata ±5.
- Kebenaran isi video referensi tidak dinilai di sini; lihat tabel cek fakta.
