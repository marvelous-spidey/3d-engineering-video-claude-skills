# Runbook — short penjelasan teknik 3D dengan Claude + Higgsfield

Versi 0.3 · 22 November 2026 · disusun dari dua produksi: video #1 (Inggris, septic tank) dan video #2 (Indonesia, kolam renang). Bagian yang belum pernah dijalankan ditandai **[rencana]**.

Dokumen ini adalah bahan baku skill: ada pemicu, masukan, langkah, pemeriksaan, batasan, dan angka acuan. Tujuannya, sesi baru bisa mengulang produksi tanpa membaca riwayat chat.

> **Catatan untuk pembaca repo.** Dokumen ini riwayat cara kerja sampai video #2, sebelum kit v1.0. Cara kerja yang berlaku sekarang ada di `skills/` dan `kit/GUIDE.md`; perintah di sini versi lama dan nama berkasnya mengikuti susunan kerja semula (padanannya di bagian 2). Yang paling berguna untuk dibaca: prinsip (bagian 3), batasan tempat kerja (bagian 4), aturan kredit (bagian 5), dan daftar jebakan (bagian 9).

## 1. Kapan dipakai

- Dipakai untuk: video pendek vertikal 60–75 detik yang menjelaskan cara kerja benda atau sistem teknik lewat potongan 3D, dengan narasi AI dan caption per kata.
- Tidak dipakai untuk: video presenter, video yang seluruhnya dari AI video generator, atau topik tanpa mekanisme yang harus digambar presisi.

| Masukan | Wajib | Catatan |
|---|---|---|
| Topik | ya | satu mekanisme, bukan daftar fakta |
| Bahasa narasi | ya | menentukan anggaran kata dan model suara |
| Video referensi | tidak | dibedah dulu (langkah 1) |
| Kalimat hook | tidak | kalau ada, dipakai apa adanya |
| Batas kredit | ya, sebelum langkah berbayar | per pos: suara, GPU |

Keluaran: MP4 1080×1920 30 fps (link), master bersih tanpa caption dan suara, skrip scene, naskah + tabel cek fakta, catatan produksi, arsip di Project dan folder lokal.

## 2. Peta dokumen

Dokumen ini ditulis saat berkas masih tersimpan di Project claude.ai (awalan `claude/`) dan di folder lokal. Padanannya di repo:

| Di dokumen ini disebut | Di repo ini |
|---|---|
| `kit/…`, `kit_explainer_kit.py`, `kit_tools.md`, `tools/ref_teardown.py` | folder `kit/` (alat bedah referensi: `kit/ref_teardown.py`) |
| `video01/…`, `video01_septic_video.py`, `script_en.md` | `examples/video01-septic-system-en/` |
| `video02/…`, `video02_pool_video.py`, `script_id.md` | `examples/video02-kolam-renang-id/` |
| `post.py` (caption dan encode per video) | digantikan `kit/captions.py` |
| `video01-production-record.md`, `video02-production-record.md`, `video02-reference-analysis.md` | folder `docs/` |
| `worklog.md`, `production-plan.md`, `video02-plan.md`, `poc_scene.py` | catatan kerja, plan, dan uji awal; tidak disertakan di repo |

## 3. Prinsip

1. **Kode adalah sumber kebenaran.** Scene, animasi, caption, dan render lahir dari skrip. Revisi berarti ubah skrip lalu render ulang.
2. **Audio dulu, gambar mengikuti.** Semua cue animasi dihitung dari waktu kata di VO, tidak diketik manual.
3. **Ukur, jangan menebak.** Claude tidak bisa mendengar atau menonton gerak. Yang dilaporkan adalah hasil ukur dan frame; penilaian rasa diserahkan ke manusia lewat gerbang review.
4. **Murah dulu, mahal belakangan.** Still CPU resolusi rendah → uji beberapa frame di GPU → render penuh.
5. **Kredit hanya dengan persetujuan eksplisit** (bagian 5).
6. **Orisinal.** Dari referensi hanya diambil tata bahasa formatnya. Naskah ditulis dari fakta bersumber; urutan, perumpamaan, set, dan karakter dibuat sendiri.
7. **Still yang bersih tidak membuktikan animasinya bersih.** Semua frame hasil render diperiksa otomatis sebelum encode (langkah 8). Di video #2 pemeriksaan ini menemukan cacat yang tidak terlihat di still mana pun.

## 4. Tempat kerja dan batasannya

| Tempat | Dipakai untuk | Batas penting |
|---|---|---|
| Workspace Claude (cloud) | menulis kode, `bpy` 5.3.0 di Python 3.13 dengan Cycles CPU, ffmpeg, OCR, dokumen | 2 core CPU, tanpa GPU. Internet hanya registry paket, GitHub, dan `raw.githubusercontent.com`. Tidak bisa menjangkau `upload.higgsfield.ai` maupun CDN Higgsfield. File kerja hilang saat sesi berakhir |
| `/mnt/user-data/outputs` | file yang dikirim ke chat atau di-commit ke folder lokal | file media di sini disisipi manifest C2PA, jadi file milik pihak ketiga jangan dilewatkan sini |
| Sandbox Higgsfield (`sandbox_exec`) | transit skrip, faster-whisper, olah audio, unduh dan unggah media Higgsfield, melihat gambar dari box | gratis. Bertahan ±24 jam dan bisa restart kapan saja (file tetap, proses hilang). Panggilan lebih dari ±60 detik bisa gagal "Bad Gateway": pakai `background:true` lalu poll. Gambar yang kembali ke Claude maksimum 4 file dan 512 KiB total |
| Box GPU sewaan | render, caption, encode, QA frame | berbayar per detik. `gpu_rental_exec` yang menunggu lebih dari ±60 detik bisa gagal "Bad Gateway". `/workspace` persisten antar-sewa (folder video #1 masih ada sehari kemudian), `/root` hilang saat box berhenti. Bawaan 4 vCPU, tanpa ffmpeg, uv, unzip |
| Komputer pengguna lewat jembatan desktop | arsip di folder terhubung | yang jalan adalah VM Linux, bukan macOS. Tidak menjangkau CDN Higgsfield, jadi MP4 tidak bisa diunduhkan ke folder |
| Project claude.ai | dokumen dan skrip yang awet lintas sesi | setiap tulis mengganti satu dokumen penuh |

Akibat praktis:

- Skrip dari workspace ke box harus lewat sandbox: tempel ke sandbox (heredoc per bagian ≤ 25 KB, cek md5 tiap bagian) → zip → `media_upload` → PUT ke URL presigned dari sandbox → `media_confirm` → box mengunduh URL baca.
- Skrip yang ditulis langsung di sandbox atau di box (alat audio, alat QA) hanya bisa kembali ke workspace sebagai teks: `cat`, tulis ulang di workspace, lalu cocokkan md5.
- Video final hanya bisa diserahkan sebagai link Higgsfield. Pengguna mengunduhnya sendiri dari link.
- Melihat frame hasil GPU: box membuat contact sheet JPEG → zip → satu URL presigned → sandbox membuka zip dan mengembalikan 3–4 gambar per panggilan.
- URL presigned panjangnya ±1,8 KB, harus disalin persis, dan **hanya bisa dipakai sekali** (ditandatangani dengan `If-None-Match: *`; PUT wajib membawa header itu). Simpan URL sebagai variabel di satu file di box (`urls.sh`) supaya perintah berikutnya pendek.

## 5. Aturan kredit

1. Estimasi dulu dengan alat gratis (`estimate_audio_cost`, `gpu_list_gpus`, `balance`), tampilkan angkanya, lalu minta persetujuan eksplisit beserta batas keras.
2. Persetujuan berlaku untuk satu pekerjaan. Sewa GPU baru berarti persetujuan baru atas harga per jamnya.
3. Sebelum render penuh, ukur detik per frame dari beberapa frame uji dan hitung proyeksi biaya. Kalau melewati batas, berhenti dan tanya.
4. Box dimatikan (`gpu_rental_stop`) segera setelah file final terunggah dan terverifikasi. Biaya nyata dicek di `transactions` dan dicatat di worklog. Transaksi "GPU Rental" bertambah terus selama box menyala.
5. Kalau pengguna meminta "plan dulu", tidak ada panggilan generate atau rent sama sekali.
6. Kalau temuan di tengah jalan memaksa kerja ulang (contoh: render ulang), hitung ulang proyeksi terhadap batas dan kabari pengguna saat itu juga. Selama box menyala, kerjakan hanya hal yang butuh box; dokumen ditulis setelah box mati.

## 6. Langkah-langkah

### Langkah 0 — Brief

Catat topik, bahasa, referensi, hook, dan keputusan pengguna. Nyatakan asumsi yang diambil (contoh: bahasa narasi) di baris pertama plan.

### Langkah 1 — Bedah referensi

Tujuan: spesifikasi gaya yang terukur dan daftar "diambil / tidak diambil".

```bash
T=tools/ref_teardown.py
python3 -I $T probe    ref.mp4
python3 -I $T sheets   ref.mp4 out/sheets 1 6 6        # lihat contact sheet, tentukan pita caption
python3 -I $T captions ref.mp4 out/cap <atas_px> <tinggi_px> 15
python3 -I $T pace     out/cap/ocr_words.json transkrip.txt   # transkrip dirapikan tangan, kalimat dipisah '|'
python3 -I $T motion   ref.mp4
python3 -I $T audio    ref.mp4
```

- Lihat sendiri contact sheet dan 6–8 frame kunci berukuran lebih besar untuk membaca bahasa visualnya.
- Transkrip referensi hanya file kerja. Jangan disimpan di arsip atau dibagikan; yang didokumentasikan adalah fungsi tiap beat, jumlah kata, dan waktunya.
- Hasil: dokumen bedah berisi angka terukur, struktur beat, bahasa visual, perbandingan dengan video sendiri, dan batas analisa. Contoh: `video02-reference-analysis.md`.

### Langkah 2 — Riset dan cek fakta

- Cari sumber primer atau lembaga (contoh video #1: EPA; video #2: CDC, dokumen produsen, media industri kolam).
- Tabel: klaim di naskah → sumber → penyederhanaan yang diambil. Angka dilokalkan ke penonton (contoh: "dicor" untuk Indonesia, bukan "disemprot").
- Hitungan sendiri boleh, asal ditandai sebagai hitungan dan asumsinya ditulis.
- Tabel final disimpan bersama naskah di `videoNN/script_<bahasa>.md`, ditambah daftar penyederhanaan yang sengaja diambil di gambar.

### Langkah 3 — Naskah

- Struktur: hook (versi paling sederhana dari hal yang rumit) → rantai masalah/solusi → satu fakta kejutan → payoff yang mengulang hook.
- Satu kalimat = satu perubahan di layar. Istilah teknis disebut setelah fungsinya jelas.
- Sudut pandang orang kedua.
- Angka ditulis dengan huruf, tanpa singkatan; elipsis untuk jeda.
- Anggaran kata, terukur:

| Bahasa | Suara | Naskah | Durasi VO | Tempo |
|---|---|---|---|---|
| Inggris | Eleven v4, preset Cillian | 171 kata | 64,4 detik mentah, dipakai apa adanya | ±2,6 kata per detik |
| Indonesia | Eleven v4, preset Marcus, tanpa tag | 188 kata, 422 suku kata | 92,3 detik mentah (terlalu lambat) | ±4,6 suku kata per detik |
| Indonesia | sama, dengan tag `[quick, energetic pace]` | sama | 78,4 detik mentah → 66,5 detik setelah diolah | ±6,3 suku kata per detik di hasil akhir |

- Bahasa Indonesia butuh ±2,2 suku kata per kata, jadi isi yang sama makan waktu lebih lama daripada bahasa Inggris. Hitung dalam suku kata.
- Naskah modular: tandai baris yang boleh dipotong beserta urutan potongnya, supaya durasi bisa dipaskan setelah VO ada. Aturan video #2: pilih varian terpanjang yang masih ≤ 70 detik dengan percepatan audio maksimum 1,10×.
- Simpan naskah per baris dengan ID (`S01`, `S02`, …), satu baris per kalimat-gambar, format `S01|teks`.

### Langkah 4 — Suara

- Katalog: `models_explore` dengan `type: audio`. Suara: `list_voices` (hanya nama dan ID).
- `generate_audio` model `elevenlabs_v4`, satu giliran `dialogue` dengan `voice_type: preset` dan `voice_id`, `use_unlim: false`. Hasilnya MP3 di CDN Higgsfield. Biaya nyata: 4,37 kredit untuk ±1.000 karakter; 5,98 kredit untuk ±1.280 karakter.
- Eleven v4 tidak punya pengatur kecepatan dan pembungkus Higgsfield tidak punya parameter bahasa; bahasa mengikuti teks. Tempo diatur dengan tag di awal teks: `[quick, energetic pace] ` membuat bacaan ±15% lebih cepat dan tidak ikut dibacakan.
- **Audisi** bila bahasa atau suaranya baru: 2 kalimat yang sama (±215 karakter) untuk 4–5 suara, lalu ukur dengan `kit/audio/audition.py`: suku kata per detik, total jeda, jumlah kata yang dikenali mesin transkripsi, nada dasar, kenyaringan. Video #2: 4 preset Eleven v4 × 1,15 kredit + 1 klip Qwen 0,1 kredit. Pilihan tetap sebaiknya dengan telinga pengguna; ukuran hanya menyaring.
- **Olah audio** dengan `kit/audio/vo_prep.py <target_detik> <mentah.mp3>`: rapatkan setiap jeda di atas 0,12 detik menjadi `min(0,30; 0,12 + 0,22 × (L − 0,12))`, percepat maksimum 1,10× (`atempo`), naikkan ke −13 LUFS lalu limiter 0,84 (hasil ±−14,4 LUFS), keluaran 48 kHz mono.
- Di box, `setup.sh` menambah jeda awal 300 ms dan mengisi sampai durasi video (`vo_final.wav`, stereo).
- Jangan buat take baru tanpa perlu: tiap take penuh ±6 kredit. Video #2 memakai 16,66 kredit suara dari batas 20.

### Langkah 5 — Waktu per kata

Selalu dari audio yang sudah diolah, di sandbox Higgsfield:

```bash
python3 asr.py vo_proc.wav asr_proc.json     # faster-whisper small, language="id", word_timestamps, TANPA initial_prompt
python3 align.py                             # -> words.json {"dur", "words": [[ID kalimat, kata, mulai, selesai], ...]}
```

- Transkripsi hanya memberi waktu; teksnya dari naskah (`difflib` mencocokkan). Kata yang tidak dikenali dibagi rata menurut suku kata di celahnya; awal dan akhir kata ditempel ke jeda nyata ≥ 0,10 detik.
- Video #2: 188 kata, 15 diinterpolasi, 43 ditempel ke jeda. Selisih yang dilaporkan mesin hanya soal ejaan ("katub", "50").
- Periksa: jumlah kata sama dengan naskah, waktu naik terus, tidak ada kata lebih pendek dari ±40 ms.
- `words.json` dipakai apa adanya oleh skrip scene dan skrip caption. `OFFSET` = jeda awal VO di mix (0,30 detik).

### Langkah 6 — Scene dan animasi

- Satu file Python membangun seluruh scene. Baris awalnya menetapkan `FPS`, `OFFSET`, memuat `words.json`, menghitung `DUR`, lalu `exec(open('explainer_kit.py').read())`; baris akhirnya `render_main()`.
- Satuan meter. Bidang potongan di y = 0, kamera melihat ke arah +Y, Z ke atas.
- Kamera: lensa 36 mm dengan sensor 36 mm. Setengah tinggi bingkai = 0,5 × jarak; setengah lebar = 0,28125 × jarak. `project(pose, titik)` menghitung posisi layar sebuah titik sebelum render.
- Semua cue berupa variabel `T_…` dari `T(id_kalimat, kata, ke, end)`. Cue tahan revisi naskah dan ganti bahasa selama kata jangkarnya masih ada. Kata harus persis ("air" bukan "airnya").
- Kosakata animasi: muncul, hilang, tumbuh, tampil/sembunyi, berjalan di lintasan, pipa memanjang, nilai material berubah, titik aliran berulang di pipa, permukaan air naik-turun.
- Kamera: `shot(t0, t1, pose, …)` = gerak mulus ke pose lalu drift pelan. Video #2 memakai satu gerak sinambung tanpa potongan keras; `orbit(azimut, elevasi, jarak, target)` untuk pose.
- Teks 3D: font dimuat sendiri (Inter Bold), ukuran papan mengikuti lebar teks.
- Teknik yang terbukti di video #2:
  - Air di lantai miring: prisma air + boolean INTERSECT dengan "kotak level" tak terlihat yang dianimasikan naik-turun.
  - Air tanah: bidang di depan penampang tanah dengan alpha dari tinggi dunia (Z) dibanding satu node Value yang di-keyframe.
  - Benda yang ikut bergerak dengan cangkang: di-parent ke satu empty dengan `matrix_parent_inverse`.
  - Dua permukaan sebidang tampil hitam: geser salah satunya 4 mm.

### Langkah 7 — Preview di CPU

```bash
python pool_video.py still 270 480 4  stills/r1 2.0 14.3 21.3 37.6    # komposisi dan waktu
python pool_video.py still 540 960 12 stills/hi 37.6 61.5             # warna dan teks, ±20 detik per still
python post.py test stills/hi/t_03760.png 37.6 cap.png                # uji caption di satu frame
```

- Putaran 1: satu still per cue penting, resolusi kecil. Cek komposisi, apa yang terlihat sebelum waktunya, keterbacaan label, ruang caption.
- Putaran berikutnya: hanya waktu yang bermasalah, lalu naikkan resolusi.
- Warna dinilai di ≥ 12–16 sampel. 4 sampel + denoise menipu.
- Video #1 butuh 4 putaran dan ±300 still; video #2 butuh 5 putaran.
- Still hanya menguji keadaan di satu waktu. Kesalahan interpolasi (objek terlambat bergerak, kunci CONSTANT yang terbawa) baru terlihat bila still diambil rapat di sekitar perubahan, dan kesalahan lintasan (titik aliran yang salah jalan) tidak terlihat sama sekali di still. Untuk gerak berulang, cetak daftar kuncinya (bagian 7) sebelum menyewa GPU.

### Langkah 8 — Render di GPU

1. `gpu_list_gpus` → tampilkan harga → minta persetujuan (bagian 5).
2. `gpu_rent`: jenis `compute`, `L40S`, 1 GPU, `auto_pause_minutes` 30. Status `working` muncul dalam ±10 detik.
3. Kirim kit lewat sandbox (bagian 4): skrip scene, `explainer_kit.py`, `words.json`, `post.py`, font caption, `vo_proc.wav`, `setup.sh`, `render.sh`. Box tanpa `unzip`: `python3 -c "import zipfile; zipfile.ZipFile('kit.zip').extractall('.')"`.
4. `nohup bash setup.sh > logs/setup.log 2>&1 &` (±80 detik bila berjalan sekali; di video #2 ±3 menit karena sempat berjalan dobel): apt (ffmpeg, font, pustaka GL), `uv`, venv Python 3.13, `bpy==5.3.0`, pillow, numpy, `vo_final.wav`. Selesai bila log memuat `SETUP_DONE`.
5. Uji beberapa still di 64 sampel (`still 1080 1920 64 …`), lihat hasilnya, catat detik per frame, hitung proyeksi biaya.
6. `FR=/root/frames bash render.sh 3 64`: tiga proses, tiap proses mengambil frame berselang, **persistent data mati** (`KIT_PERSIST=0`, bawaan kit sejak video #2). File yang sudah ada dilewati, jadi bisa dilanjutkan.
7. Pantau dengan perintah pendek saja: `ls /root/frames | wc -l`, `tail -2 logs/render_0.log`.
8. **Scan frame** saat render berjalan dan sesudahnya: `python scan.py /root/frames /root/qa/scan`. Hasil yang sehat: nol tersangka, atau tersangka yang ternyata gerak cepat yang sah. Lihat tersangka terkuat dengan `trip_png.py` (frame tersangka di antara dua tetangganya). Di video #2 scan menangkap dua hal berbeda: cacat render (objek hitam di satu proses) dan kesalahan animasi di skrip (titik aliran yang melesat). Bila ragu apakah sebuah tersangka cacat render, render ulang dengan mode `list` ke folder lain dan bandingkan dengan `compare.py`.
9. **Perbaikan sebagian**: bila skrip scene diperbaiki, pindahkan frame di rentang yang terpengaruh ke folder lain lalu jalankan `render.sh` lagi untuk rentang itu (frame yang masih ada dilewati). Render ulang juga 2–3 frame di luar rentang dan bandingkan dengan `diffall.py` untuk membuktikan perbaikan tidak mengubah bagian lain. Potong cache scan (`*_th.npy`, `*_bl.npy`) sampai frame terakhir yang tidak berubah.
10. Lengkap bila jumlah file sama dengan jumlah frame dan tidak ada file kecil.
11. `nohup bash finish.sh` menunggu render selesai lalu menjalankan scan, dua encode, probe, dan contact sheet sekaligus. `nohup bash after.sh` menunggu `finish.sh`, lalu mengunggah video final, master bersih, contact sheet, dan potongan tersangka terkuat ke URL presigned yang sudah disimpan di `urls.sh`. Keduanya dijalankan saat render masih berjalan supaya box tidak menunggu perintah berikutnya.

Render memakai Cycles OptiX, 64 sampel dengan adaptive threshold 0,05, 4 pantulan, denoise OIDN, view transform Standard, PNG.

**Kenapa persistent data dimatikan.** Di video #2, render pertama memakai `use_persistent_data = True` seperti video #1. Pada ±20% frame, satu dari tiga proses menggambar objek yang baru berubah (muncul, disembunyikan, membesar) sebagai bentuk hitam, sedangkan dua proses lain menggambarnya benar. Hasilnya kedip 10 Hz. Still tidak pernah menunjukkannya, dan contact sheet pertama hanya menangkap satu dari sekian cacat, karena semua frame contohnya kebetulan milik proses yang sama. Proses baru yang langsung melompat ke frame yang sama menggambar dengan benar, dan render ulang tanpa persistent data cocok dengan frame sehat sampai selisih 0,07 dari 255. Biaya waktunya ±20%: pada 1.504 frame pertama yang dirender dengan kedua cara, 0,77 frame per detik tanpa persistent data dibanding 0,94 dengan.

### Langkah 9 — Caption dan encode

```bash
python post.py video /root/frames vo_final.wav <nama>.mp4      # caption PIL → pipa rawvideo → libx264 CRF 17, AAC 192k
python post.py clean /root/frames <nama>_clean_master.mp4      # tanpa caption dan suara, CRF 15
```

- Ditulis ke `.part.mp4` lalu diganti nama setelah ffmpeg selesai tanpa error. Kedua encode bisa jalan bersamaan.
- Gaya caption video #1: Inter SemiBold 66 px, frasa kumulatif, 67,5% tinggi layar.
- Gaya caption video #2 (`post.py` v2): satu kartu 1–2 kata, Baloo 2 ExtraBold, putih dengan garis luar biru tua dan bayangan lembut, kata kunci kuning, pop-in 3 frame, pusat di 69,5% tinggi layar, mengecil otomatis bila lebih lebar dari 960 px. Kata ≤ 3 huruf atau lebih pendek dari 0,13 detik digabung dengan kata berikutnya bila diucapkan tanpa jeda. 188 kata menjadi 164 kartu; kartu terpendek 0,14 detik.
- Teks naskah (untuk tanda baca) dan daftar kata kunci ada di dalam `post.py`; skrip menolak jalan bila naskah dan `words.json` berbeda.

### Langkah 10 — QA

| Cek | Cara | Lulus bila |
|---|---|---|
| Konsistensi antar-frame | `scan.py` pada frame PNG sebelum encode | tidak ada tersangka nyata (lihat langkah 8) |
| Format | `ffprobe` | H.264 1080×1920, 30 fps, yuv420p, bt709; jumlah frame dan durasi sesuai; AAC 48 kHz |
| Kenyaringan | filter `ebur128` | −14 LUFS ±1; puncak tidak menyentuh 0 dBFS |
| Gambar | `qa_final.py`: 36 frame dari file final yang tersebar di ketiga fase proses + potongan 100% | tidak ada objek salah waktu, kedip, atau caption terpotong |
| Konsistensi pada file jadi | `scan_video.py` pada master bersih di sandbox (gratis, bisa setelah box mati), lalu `trip.py` untuk tersangka terkuat | jumlah tersangka sebanding dengan scan frame, tersebar merata di ketiga proses, dan tidak ada lonjakan piksel hitam yang hanya satu frame |
| Sinkron | transkripsi ulang audio file final di sandbox | jumlah kata sama dengan naskah; selisih waktu kata terhadap caption ≤ 0,05 detik |
| Keutuhan | md5 file di box dan file hasil unduh ulang dari link | sama |
| Fakta | baca ulang tabel cek fakta terhadap narasi dan teks di layar | tidak ada angka yang berubah |

Contact sheet harus mengambil frame dari semua fase proses. Waktu kelipatan 0,1 detik selalu jatuh di frame bernomor 3k + 1, yaitu proses pertama; pakai nomor frame seperti 10 + 58k.

Selalu laporkan batasnya: audio belum didengar manusia, gerak belum ditonton, dan apa yang tidak dibuat (musik, SFX).

### Langkah 11 — Serah terima dan arsip

1. Unggah final dan master bersih (`media_upload` → PUT → `media_confirm`), simpan link dan `media_id`.
2. Matikan box, catat biaya nyata dari `transactions`.
3. Tulis catatan produksi (hasil, jalur yang dipakai, angka terukur, koreksi terhadap plan, pelajaran, lokasi file, yang belum dikerjakan).
4. Project: skrip scene, skrip caption, catatan produksi. Folder lokal: `videoNN/` berisi `README.md`, skrip, `script_<bahasa>.md` (naskah + cek fakta), `words.json`, `.blend`, `box/`, `audio/`, `preview/`.
5. Perbarui `worklog.md` dan runbook ini bila ada langkah yang meleset.

## 7. Kit: fungsi yang dipakai ulang

`kit/explainer_kit.py` dibangkitkan oleh `kit/make_kit.py` dari skrip video #1 (`python3 make_kit.py video01/septic_video.py explainer_kit.py`): fungsi disalin apa adanya, bagian khusus video #1 ditinggalkan, lalu ditambah pencarian cue `T()`, mode `list`, dan persistent data mati secara bawaan. Skrip scene memakainya lewat `exec()` setelah menetapkan `FPS`, `DUR`, `OFFSET`, `WORDS`.

| Kelompok | Fungsi | Guna |
|---|---|---|
| Waktu | `T(id, kata, ke, end)`, `fr(t)` | waktu video sebuah kalimat atau kata (sudah termasuk `OFFSET`); detik ke nomor frame |
| Keyframe | `key(obj, path, t, value, ip, ease)` | sisipkan keyframe dalam detik dan atur interpolasinya |
| Kata kerja | `hidden_until`, `appear`, `vanish`, `grow`, `show`, `travel`, `extend`, `key_input` | sembunyi sampai cue, muncul membesar, hilang, tumbuh dari pangkal, tampil/sembunyi keras, berjalan antar-titik, pipa memanjang, animasi nilai node |
| Primitif | `box`, `tube`, `pipe`, `sphere`, `cyl`, `prism`, `patch`, `smooth_path`, `empty`, `link` | kotak dengan pilihan titik pangkal, tabung dari titik, pipa terbelah, prisma dari profil, bidang satu sisi |
| Teks | `text`, `label`, `sign`, `screen_to_world` | teks 3D Inter, tag dengan papan mengikuti lebar teks (bisa menghadap kamera), papan nama, posisi layar ke dunia |
| Material | `new_mat`, `bsdf_of`, `soil_material`, `grass_material`, `gravel_material` + 15 material dasar | warna dasar; tanah berlapis menurut kedalaman; rumput; kerikil |
| Dunia | matahari `sun_d`, langit `sky`, latar `bg`, kamera `cam` | bisa di-keyframe (contoh: senja di video #2) |
| Kamera | `pose`, `push`, `cam_key`, `shot`, `hero_pose` | pose frontal, dorong, shot dengan gerak lalu drift, pose orbit |
| Mode | `still`, `anim`, `list`, `blend`; `KIT_DEVICE`, `KIT_FMT`, `KIT_PERSIST`, `SEPTIC_FONT` | still pada detik tertentu, rentang frame dengan langkah, daftar frame dari berkas, simpan `.blend` |

Fungsi yang masih tinggal di skrip video #2 dan layak naik ke kit pada video berikutnya: `prismp`, `prism_yz`, `hinge`, `arrow`, `pulse`, `level_box` / `level` / `water_body`, `water_material`, `tint`, `project`, `orbit`, `make_char` (maskot seri), `pop`, `flow`, `patchp`.

| Alat | Berkas | Guna |
|---|---|---|
| Suara (sandbox) | `kit/audio/audition.py`, `vo_prep.py`, `asr.py`, `align.py` | ukur klip audisi; olah VO; transkripsi berwaktu; `words.json` |
| Caption | `videoNN/post.py`: `video`, `clean`, `test`, `cards` | bakar caption + encode, master bersih, uji satu frame, daftar kartu |
| Box | `kit/box/setup.sh`, `render.sh`, `rerender.sh`, `finish.sh`, `after.sh`, `up.sh` | pasang lingkungan; render paralel; render ulang rentang frame setelah perbaikan skrip; selesaikan (scan, encode, probe, sheet); unggah hasil + potongan tersangka; PUT ke URL presigned |
| QA frame | `kit/box/scan.py`, `trip_png.py`, `compare.py`, `diffall.py`, `sheets.py`, `qa_final.py` | cari frame yang menyimpang dari tetangganya; tampilkan tersangka di samping tetangganya; bandingkan render ulang; bandingkan dua render; contact sheet dari frame; contact sheet dari file final |
| QA file final (sandbox, gratis) | `kit/sandbox/final_check.sh`, `sync_check.py`, `scan_video.py`, `trip.py` | md5, format, kenyaringan, dan sinkron kata dari link; scan antar-frame pada video jadi; potongan tiga frame berurutan untuk tiap tersangka |
| Referensi | `tools/ref_teardown.py` | ukur video referensi |

Nama berkas (`pool_video.py`, nama keluaran, durasi 68,4 detik, 2.052 frame, rentang frame) masih tertulis di `setup.sh`, `render.sh`, `rerender.sh`, `finish.sh`, `after.sh`, dan `qa_final.py`; ganti saat dipakai untuk video lain.

Catatan Blender 5.3 yang menghemat waktu:

- Tidak ada `action.fcurves` lama. F-curve diambil lewat `action.layers → strips → channelbag(slot)`.
- `keyframe_insert` mengabaikan preferensi interpolasi; interpolasi diset pada titik keyframe setelah disisipkan.
- Pipa memanjang: animasi `bevel_factor_end` pada kurva.
- Lebar teks: `view_layer.update()` lalu baca `bound_box`.
- Tag menghadap kamera: constraint `COPY_ROTATION` ke kamera dan `visible_shadow = False`.
- Rongga di tanah: boolean solver EXACT, lalu `new_from_object`.
- Transparansi bertumpuk: `transparent_max_bounces = 16` dan bidang satu sisi.
- Kunci ketiga dan seterusnya pada sebuah kurva mewarisi interpolasi kunci sebelumnya; hanya dua kunci pertama yang memakai bawaan BEZIER. Jadi setelah `show()` atau `extend()`, yang meninggalkan kunci CONSTANT, kunci berikutnya pada properti yang sama harus diberi `ip` eksplisit. Kalau tidak, gerak halus menjadi lompatan.
- Menyisipkan kunci pada frame yang sudah punya kunci **mengganti** kunci itu. Gerak berulang "sampai di ujung, lalu lompat ke awal" harus menaruh kunci ujung sedikit sebelum kunci awal putaran berikutnya (`flow()` memakai 0,004 detik).
- Handle BEZIER otomatis di sebelah kunci "sembunyi" menunda gerak. Pakai `ip='SINE', ease='EASE_IN_OUT'`.
- Cara cepat memeriksa: bangun scene dengan mode `none`, lalu cetak `(frame, nilai, interpolasi)` dari `fcurves_of(objek)` untuk satu objek contoh tiap jenis gerak.

## 8. Angka acuan

| Hal | Video #1 (septic, Inggris) | Video #2 (kolam renang, Indonesia) |
|---|---|---|
| Scene | 710 objek, 902 baris | 834 objek, 517 baris + kit 470 baris |
| Durasi, frame | 66,0 detik, 1.980 | 68,4 detik, 2.052 |
| Still CPU di workspace | 270×480, 4 sampel: 2–3 detik | sama; 540×960, 12 sampel: ±20 detik |
| Setup box | ±80 detik | ±3 menit (terganggu salah perintah) |
| 1 proses, 1080×1920, 64 sampel + denoise | 1,7–1,9 detik per frame | 1,3–1,7 detik per frame |
| 3 proses di 1× L40S, persistent data hidup | 1.980 frame dalam 27 menit 20 detik (1,2 fps) | 0,90–0,95 fps, tetapi ±20% frame cacat |
| 3 proses, persistent data mati | belum pernah | 2.052 frame dalam 46 menit 25 detik (0,74 fps rata-rata; 0,77 pada 1.504 frame pertama, 0,61 di bagian akhir yang berat); GPU 99% |
| Caption + encode | ±3 menit | 2 menit 38 detik untuk final dan master bersih bersamaan |
| Box menyala total | 36 menit 57 detik = 43,72 kredit | 1 jam 51 menit 47 detik = 132,29 kredit, termasuk satu render terbuang (±33 kredit) dan satu render ulang sebagian (±20 kredit) |
| Suara | 4,37 kredit (1 take) | 16,66 kredit (audisi 4,70 + 2 take × 5,98) |
| Total | 48,09 kredit | 148,95 kredit |
| File final | 28,3 MB, −14,3 LUFS | 37,5 MB, −14,5 LUFS |

Harga saat itu: L40S 71 kredit per jam; Eleven v4 ±0,47 kredit per 100 karakter.

## 9. Jebakan yang sudah ditemui

| Gejala | Sebab | Perbaikan |
|---|---|---|
| Objek tampil hitam atau tertinggal di sepertiga frame (kedip 10 Hz) | `use_persistent_data` pada render multi-proses: Cycles menyimpan keadaan basi untuk objek yang transform-nya berubah | matikan persistent data (bawaan kit); scan semua frame sebelum encode |
| Contact sheet bersih padahal animasi berkedip | semua frame contoh jatuh di proses yang sama (waktu kelipatan 0,1 detik = frame 3k + 1) | ambil frame dari semua fase; jalankan `scan.py` |
| Skor `scan.py` tinggi di banyak frame berurutan | gerak kamera cepat atau benda yang melintas lebih dari satu blok per frame | bukan cacat; tersangka nyata hanya frame yang menonjol dari kedua tetangganya |
| Satu frame menonjol tepat saat label atau tag muncul | puncak pantulan (overshoot) animasi muncul hanya berlangsung satu frame | sah; pastikan dengan mengukur tepi label di 5 frame berurutan: melebar ke puncak lalu kembali |
| Satu frame menonjol di tumpukan bola atau pola berulang saat kamera mulai bergerak | pola berulang yang bergeser setengah jarak antar-bola terlihat "kembali" di frame berikutnya pada resolusi thumbnail | sah; cek langkah kamera per frame dari f-curve (naik mulus, tidak ada lompatan tunggal) |
| Potongan tiga frame dari video menampilkan frame yang bergeser satu | `ffmpeg -ss` mengembalikan frame pertama pada atau sesudah waktu yang diminta, jadi `(f−1)/30 + 0,001` melompati frame f | minta waktu sedikit sebelum frame: `(f−1)/30 − 0,012`. `trip.py` dan `qa_final.py` diperbaiki 22 Nov; lembar yang dibuat sebelumnya berlabel satu frame terlalu awal |
| Perintah di box mati dengan kode 143 | `pkill -f "pola"` ikut membunuh shell yang baris perintahnya memuat pola itu | tulis pola dengan kurung siku: `pkill -f "[p]ool_video.py anim"` |
| Setup jalan dua kali dan apt terkunci | `a && b && nohup c &` menaruh seluruh rantai di latar belakang | jalankan langkah pendek satu per satu; hanya perintah panjang yang diberi `nohup … &` |
| PUT kedua ke URL presigned ditolak | URL ditandatangani dengan `If-None-Match: *` | minta URL baru untuk tiap unggahan |
| Render melambat saat alat QA berjalan | box hanya 4 vCPU dan tiga proses render sudah memakai ±3,3 | satu alat analisa saja pada satu waktu, dengan `nice` |
| Whisper mengacaukan 30 detik pertama | `initial_prompt` berisi naskah | jangan beri prompt; cocokkan ke naskah dengan `difflib` |
| VO terlalu lambat | Eleven v4 tanpa pengatur kecepatan | tag `[quick, energetic pace]` di awal teks, lalu rapatkan jeda dan `atempo` ≤ 1,10 |
| `T('S06', 'air', 2)` gagal | "airnya" bukan "air" | kata jangkar harus persis; hitung kemunculannya |
| Bidang hitam di bidang potong | dua permukaan sebidang | geser 4 mm |
| Benda terlambat bergerak atau tertinggal setelah `show()` | kunci CONSTANT terbawa; handle BEZIER otomatis di sebelah kunci "sembunyi" | beri `ip` eksplisit pada kunci berikutnya |
| Titik aliran melayang di luar pipa atau melesat melintasi gambar | kunci titik terakhir dan kunci titik pertama putaran berikutnya jatuh di waktu yang sama; yang kedua mengganti yang pertama | majukan kunci terakhir 0,004 detik; cetak daftar kunci satu titik sebelum render |
| Denyut halus menjadi lompatan, dengan kedipan 1–2 frame di ujungnya | kunci baru mewarisi CONSTANT dari kunci `show()` / `extend()` | `pulse(..., ip='BEZIER')`; akhiri denyut di kelipatan periode |
| Stiker menutupi maskot; tag tertutup pipa | posisi dipilih tanpa menghitung proyeksi | `project(pose, titik)` sebelum render |
| Objek "tumbuh" terlihat sebagai lembaran tipis sebelum cue | skala nol tetap dirender | sembunyikan sampai cue (`hidden_until` di dalam `grow`) |
| Gumpalan gelap di tumpukan bentuk transparan | prisma tertutup + batas pantulan transparan | bidang satu sisi, satu garis luar per noda, sembunyikan saat alpha 0, naikkan batas pantulan |
| Bayangan memanjang dari tag yang menghadap kamera | tag ikut menjatuhkan bayangan | `visible_shadow = False` |
| Angka "1" terbaca "I" | font bawaan Blender | muat Inter Bold |
| Warna terlihat berbeda antar-bagian | artefak denoise di 4 sampel | nilai warna di ≥ 12–16 sampel |
| Hero shot memotong objek dan memperlihatkan ruang kosong | pose dipilih dengan perkiraan | sapu pose secara numerik, perbesar blok tanah |
| Teks berubah tapi tidak pernah tampil | objek dihilangkan sebelum cue teks terakhir | urutkan ulang cue, cek dengan still di tiap perubahan |
| `gpu_rental_exec` atau `sandbox_exec` "Bad Gateway" | panggilan menunggu > ±60 detik | `nohup` atau `background:true` + poll pendek; setelah gagal, cek keadaan dulu sebelum mengulang |
| `pgrep -af` mencetak ribuan karakter | baris perintah heredoc ikut tercetak | `pgrep -f "[p]ola" \| wc -l` |
| Tool Write menolak menimpa file | file diubah lewat shell setelah terakhir dibaca | tulis ke nama baru lalu salin |
| `project_write` dengan `local_path` ditolak | file berubah sejak dibaca | baca ulang, ubah dengan Edit, tulis lagi |
| File pihak ketiga berubah saat di-commit | lewat `/mnt/user-data/outputs` (manifest C2PA) | commit dengan `fileUuid` unggahan aslinya, atau jangan disalin |
| OCR caption gagal karena tanda petik | whitelist tesseract diproses seperti baris perintah | tulis `\'` di whitelist |
| Deteksi scene tidak menemukan apa pun | video tanpa potongan keras | ukur beda antar-frame (`ref_teardown.py motion`) |

## 10. Checklist ringkas

- [ ] Brief dan asumsi tertulis
- [ ] Referensi dibedah; daftar "diambil / tidak diambil"
- [ ] Tabel cek fakta dengan sumber
- [ ] Naskah per baris ber-ID, baris potong ditandai, dihitung dalam suku kata
- [ ] Persetujuan kredit suara → audisi (bila perlu) → VO → olah → waktu per kata
- [ ] Scene dari kode, cue dari `T(id, kata)`
- [ ] Still berlapis sampai bersih; warna dicek di ≥ 12 sampel
- [ ] Gerbang review pengguna sebelum GPU
- [ ] Persetujuan kredit GPU → sewa → setup → still uji → render tanpa persistent data
- [ ] Scan semua frame → nol tersangka nyata
- [ ] Caption + encode + master bersih → QA file final (sheet dari semua fase, kenyaringan, sinkron)
- [ ] Unggah, verifikasi md5, matikan box, cek transaksi
- [ ] Catatan produksi, arsip Project + folder lokal, worklog, runbook

## 11. Skill yang dibuat dari runbook ini

| Skill (folder `skills/`) | Pemicu | Isi |
|---|---|---|
| `3d-engineering-video` | permintaan membuat short penjelasan teknik 3D dari naskah atau video referensi | alur dan gerbang dari bagian 3–10, dengan rujukan ke kit |
| `reference-short-teardown` | "pelajari / analisa video ini" untuk short referensi | langkah 1, format dokumen bedah, aturan orisinalitas |
| `higgsfield-blender-render` | skrip scene siap dirender di box sewaan | bagian 4, 5, dan langkah 8–11 |

Skill berisi instruksi saja; kodenya ada di `kit/` dan diambil skill lewat `git clone`. Alur ini teruji pada dua topik dan dua bahasa (video #1 dan #2). Tanggapan penonton atas suara, look, dan tempo belum masuk ke dalamnya.

## 12. Belum teruji

- Penyebab pasti cacat persistent data. Dugaan: transform objek ber-mesh tunggal "dipanggang" ke geometri, dan versi di struktur percepatan GPU tidak selalu ikut diperbarui. Trik yang mungkin memulihkan persistent data (memberi tiap mesh pengguna kedua yang tersembunyi supaya selalu di-instance) belum dicoba.
- Kenapa video #1 tidak terkena cacat itu padahal dirender dengan persistent data juga. Scan pada master bersihnya (22 Nov, di sandbox) menemukan 5 tersangka dari 1.980 frame dan kelimanya sah: dua gerak cepat, dua puncak pantulan label yang baru muncul, dan satu kilau pantulan kecil di pipa.
- Core CPU tambahan pada box (`cpu` di `gpu_rent`) untuk mempercepat render dan encode; harganya belum dicek.
- Animatic sebagai gerbang review (dilewati di kedua video).
- Musik dan SFX: Claude tidak bisa menilai mix.
- Pilihan suara dengan telinga pengguna sebelum VO penuh (di video #2 suara dipilih dari ukuran karena pengguna meminta langsung eksekusi).
- `video_analysis_create` Higgsfield sebagai pemeriksa kedua untuk video hasil (biaya belum diketahui).
