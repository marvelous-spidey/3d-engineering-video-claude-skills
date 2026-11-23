# Kit v1.1 — short penjelasan teknik 3D (Claude + Higgsfield)

Kit ini adalah kode yang dipakai skill `3d-engineering-video`, `reference-short-teardown`, dan `higgsfield-blender-render` (folder `skills/` di repo ini). Skill berisi cara kerja; kit berisi alatnya. Kit lahir dari video #1 (septic system, Inggris) dan video #2 (kolam renang, Indonesia); v1.1 memuat pelajaran video #3 (mesin CR-V, Indonesia), produksi pertama yang memakai kit dan skill. Ketiganya ada di `examples/`.

## Memasang

```bash
git clone --depth 1 https://github.com/davidalfasunarna/3d-engineering-video-claude-skills ~/3dv-repo
cp -r ~/3dv-repo/kit ~/kit
pip install --break-system-packages bpy==5.3.0 pillow numpy    # Blender sebagai modul Python; butuh Python 3.13, ±1 GB
bash ~/kit/selftest.sh                                          # 3–10 menit di CPU, tanpa kredit; harus berakhir dengan SELFTEST PASSED
```

Yang dibutuhkan di mesin kerja:

| Kebutuhan | Dipakai untuk | Catatan |
|---|---|---|
| Python 3.13 + `bpy==5.3.0`, `pillow`, `numpy` | scene, preview, caption | di box GPU dipasang oleh `box/setup.sh` |
| ffmpeg dan ffprobe | encode, QA | |
| Font Inter (`fonts-inter`) | teks di dalam scene, caption gaya `phrases`, contact sheet | tanpa Inter, teks scene memakai font bawaan Blender (angka "1" mirip "I") |
| `Baloo2.ttf` (lisensi OFL) | caption gaya `cards` | diunduh `newjob.sh` dari repo Google Fonts; tidak disertakan di sini |
| tesseract + `pytesseract`, `scipy` | `ref_teardown.py captions` | hanya untuk membedah video referensi |
| faster-whisper | `audio/asr.py` | sudah ada di sandbox Higgsfield |

Kit diuji di workspace cloud Claude (Linux, 2 core CPU), di sandbox Higgsfield, dan di box GPU sewaan Higgsfield (L40S). Tempat lain belum diuji.

## Isi

| Berkas | Guna |
|---|---|
| `explainer_kit.py` | inti scene: waktu dari kata (`T`), keyframe, bentuk dasar, teks, material, kamera, mode render. Dibangkitkan `make_kit.py` dari skrip video #1; tidak berubah sejak video #2 (md5 `f66672403b57`) |
| `scene_extras.py` | tambahan dari video #2: bentuk berporos, panah, denyut, pop, air (level, badan air, material), titik aliran di pipa, proyeksi layar, maskot, pohon |
| `scene_template.py` + `demo/` | scene terkecil yang lengkap (tandon air di atap) dengan data contoh; titik awal skrip scene baru |
| `kitjob.py`, `job.env.example` | satu sumber angka untuk satu video: nama, bahasa, gaya caption, FPS, jeda awal, ekor; `DUR` dan jumlah frame dihitung dari `words.json` |
| `scene_check.py` | periksa scene tanpa render: langkah kamera, jadwal tampil benda yang menempel di layar, dan kilat 1–2 frame beserta detik puncaknya. `python3 scene_check.py <scene>.py` |
| `captions.py` | caption + encode: gaya `cards` (1–2 kata, kata kunci kuning) dan `phrases` (frasa yang terisi kata demi kata); bisa membaca frame PNG atau master bersih |
| `audio/` | `audition.py` (ukur klip audisi), `vo_prep.py` (rapatkan jeda, tempo, kenyaringan), `asr.py` + `align.py` (waktu per kata → `words.json`); bahasa `id` atau `en` |
| `box/` | `job.sh`, `setup.sh`, `vo_final.sh`, `render.sh`, `rerender.sh`, `finish.sh`, `after.sh`, `up.sh`, `scan.py`, `trip_png.py`, `compare.py`, `diffall.py`, `sheets.py`, `qa_final.py` |
| `sandbox/` | `final_check.sh`, `sync_check.py`, `scan_video.py`, `trip.py` (QA file jadi, gratis) |
| `ref_teardown.py` | ukur video referensi: `probe`, `sheets`, `captions`, `pace`, `motion`, `audio` |
| `newjob.sh` | membuat folder job datar dari kit |
| `selftest.sh` | uji ujung ke ujung skala kecil di CPU, tanpa kredit |
| `make_api.py`, `make_kit.py` | pembuat `API.md` dan `explainer_kit.py` |
| `make_bundle.py` | mengemas berkas kecil kit menjadi satu dokumen Markdown (`kit_tools.md`) dan membukanya lagi; berguna bila kit ingin disimpan sebagai dokumen di Project claude.ai |
| `GUIDE.md` | panduan kerja untuk skill: menulis scene, preview, suara per bahasa, membaca scan, jebakan, angka acuan |
| `API.md` | daftar fungsi scene dengan argumennya (buat ulang dengan `python3 make_api.py > API.md`) |

## Satu video = satu folder job

`bash newjob.sh <folder>` menyalin kode kit ke satu folder datar. Workspace, sandbox, dan box GPU semuanya bekerja di folder seperti itu. Berkas milik job:

| Berkas | Dari mana |
|---|---|
| `job.env` | diisi di awal: `NAME`, `SCENE`, `LANG_CODE`, `CAPTION_STYLE`, `TAIL` |
| `script.txt` | naskah, satu baris per kalimat-gambar: `S01\|teks`. Angka ditulis dengan huruf. Jeda frasa untuk gaya `phrases`: ` / ` |
| `keywords.txt` | kata kunci kuning untuk gaya `cards`: `S01 kata [ke]` |
| `vo_raw.mp3` → `vo_proc.wav` | suara dari Higgsfield, diolah `vo_prep.py` |
| `words.json` | `asr.py` + `align.py` di sandbox |
| `<scene>.py` | skrip scene, mulai dari `scene_template.py` |
| `urls.sh` | URL unggah presigned, ditulis menjelang render selesai dan dihapus `after.sh` setelah dipakai (hanya di box; sekali pakai, jangan disimpan di repo atau dokumen) |

Mencoba job contoh tanpa kredit:

```bash
cp -r ~/3dv-repo/examples/video02-kolam-renang-id ~/jobs/kolam && bash ~/kit/newjob.sh ~/jobs/kolam && cd ~/jobs/kolam
python3 pool_video.py still 270 480 4 st 3.6 27.2 47.6          # tiga still kecil, beberapa detik per still
python3 captions.py test st/t_02720.png 27.2 st/c_02720.png     # caption di atas still
```

## Uji yang sudah lulus (22–23 November 2026, tanpa kredit)

- `selftest.sh`: render 3 proses → scan → caption + encode → master bersih → probe → contact sheet → cek warna. LULUS di workspace (CPU), juga dari clone baru repo ini.
- `scene_extras.py`: scene video #2 yang dibangun dengan kit + extras sama persis dengan aslinya (834 objek, 14.240 kunci). Job contoh di `examples/video02-kolam-renang-id/` lulus uji yang sama.
- `captions.py`: gaya `cards` sama persis dengan caption video #2 (164 kartu, piksel identik); gaya `phrases` sama persis dengan video #1 (66 frasa, piksel identik).
- `asr.py` + `align.py` bahasa Inggris: 171 dari 171 kata VO video #1 dikenali; tidak ada kata yang melintasi jeda. Bahasa Indonesia: 188 kata VO video #2, hasil sama dengan produksi kecuali 2 kata yang kini dimulai tepat setelah jeda.
- Cek warna di `qa_final.py`: lolos pada encode yang benar, gagal pada encode dengan matriks yang salah.

Uji v1.1 (23 November 2026, tanpa kredit):

- `selftest.sh` lulus dengan kit v1.1 (459 detik di workspace yang sedang sibuk).
- `scene_check.py` pada scene video #3: angkanya sama dengan pemeriksa khusus video itu (771 objek, 262.404 kunci, 26 label layar). Pada dua versi scene sebelum perbaikan ia menandai kedua kesalahan yang dulu baru ketahuan setelah render: kilat berskala 1,70 pada 57,13 detik, dan label penghitung yang tidak pernah hilang.
- `after.sh` dan `rerender.sh` yang baru diuji di CPU pada job selftest (unggahan diganti tiruan). Keduanya belum dijalankan di box GPU sewaan.

## Batas yang diketahui

- Hanya 1080×1920, 30 fps.
- Skrip `box/` v1.0 merender video #3 di box GPU sewaan (L40S) dari awal sampai unggah, termasuk dua render ulang sebagian. Perubahan v1.1 pada `after.sh` dan `rerender.sh` baru diuji di CPU.
- Fungsi scene baru dari video #3 (`bake`, `land`, `hud_label`, `dial`, `frame`, `tag`, `carve`) masih berada di skrip scene video itu, belum di `scene_extras.py`.
- `selftest.sh` butuh 3–10 menit di workspace Claude (tiga proses berbagi dua core). Kalau satu proses render dimatikan karena memori, `selftest.sh` v1.1 melanjutkan frame yang tersisa dengan satu proses.
- Suara, gerak, dan rasa tidak bisa dinilai Claude; itu tetap tugas manusia.

## Merilis perubahan kit

1. Ubah berkas, jalankan `bash selftest.sh` sampai `SELFTEST PASSED`.
2. Naikkan `VERSION`, tambahkan baris di "Riwayat". Bila `explainer_kit.py` berubah, perbarui md5 di tabel "Isi".
3. `python3 make_api.py > API.md` bila fungsi scene berubah.
4. Commit ke repo. Skill mengambil kit dari cabang utama, jadi perubahan langsung dipakai sesi berikutnya.

## Riwayat

- **1.1.0 (23 Nov 2026, setelah video #3)** — `scene_check.py` baru; `after.sh` menunggu `urls.sh` dan menghapusnya setelah dipakai (URL unggah hanya hidup ±1 jam, jadi diminta menjelang render selesai); `rerender.sh` mengurutkan frame kontrol dan mengosongkan folder pembanding lama; `newjob.sh` ikut menyalin `scene_check.py`; `selftest.sh` melanjutkan sendiri bila satu proses render mati; `GUIDE.md` memuat pelajaran video #3 (ditandai "v1.1"). `explainer_kit.py` dan `scene_extras.py` tidak berubah.
- **1.0.0 (22 Nov 2026)** — satu berkas `job.env` menggantikan nama video yang tertanam di skrip box; alat suara menerima bahasa `id`/`en`; `align.py` menempelkan batas kata ke jeda dengan memakai tanda baca (kata pertama setelah titik tidak lagi muncul terlalu awal); `captions.py` generik dengan dua gaya, bisa membaca master bersih, dan memakai matriks warna BT.709 yang benar; cek warna di `qa_final.py`; `scene_extras.py`, `scene_template.py`, `newjob.sh`, `selftest.sh`.
- **0.2 (22 Nov 2026, video #2)** — pencarian cue `T(id, kata)`, mode `list`, persistent data mati secara bawaan, scan frame.
- **0.1 (21 Nov 2026, video #1)** — fungsi scene di dalam skrip video #1.
