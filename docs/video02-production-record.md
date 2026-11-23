# Video 02 — catatan produksi "Cara kerja kolam renang" (ID)

22 November 2026 · video kedua, video pertama yang memakai kit · berkasnya di `examples/video02-kolam-renang-id/` · versi 1.1 (warna dikoreksi) menggantikan versi pertama

Catatan ini versi repo: tautan hasil, ID media, nama, dan lokasi penyimpanan pribadi dihilangkan. "Plan" yang disebut di sini adalah dokumen rencana internal yang tidak disertakan di repo.

## Hasil

| Hal | Nilai |
|---|---|
| Keluaran | video final v1.1 (44,1 MB) dengan caption dan suara, plus master bersih (tanpa caption, tanpa suara) |
| Format | 1080×1920, 30 fps, 68,4 detik, H.264 (BT.709) + AAC, 44,1 MB, −14,5 LUFS (puncak −4,0 dBFS) |
| Naskah | 188 kata (422 suku kata), 11 baris, bahasa Indonesia; kalimat hook dari pengguna; fakta dicek, tabelnya di `examples/video02-kolam-renang-id/script_id.md` |
| Suara | ElevenLabs v4 lewat Higgsfield, preset "Marcus", tag tempo `[quick, energetic pace]`; jeda dirapatkan dan tempo dinaikkan 1,088× menjadi 66,48 detik |
| Gambar | Scene Blender 834 objek dari `pool_video.py` (517 baris) di atas `explainer_kit.py` (470 baris); satu gerak kamera sinambung tanpa potongan keras |
| Caption | satu kartu berisi 1–2 kata (164 kartu), Baloo 2 ExtraBold, kata kunci kuning (`post.py` video ini; sekarang `kit/captions.py`) |
| Kredit | suara 16,66 + GPU 132,29 = **148,95** (batas yang disetujui: suara 20, GPU 200) |

## Koreksi warna (versi 1.1, 22 November 2026)

**Temuan.** Saat kit dirapikan, warna caption di file final diukur: kuning yang seharusnya (255, 214, 58) terbaca (255, 207, 49). Uji dengan bidang warna menunjukkan sebabnya: perintah encode di `post.py` v2 menandai file sebagai BT.709 tetapi tidak memberi tahu ffmpeg untuk mengubah RGB ke YUV dengan matriks itu, sehingga yang dipakai BT.601. Akibatnya hijau tampil ±10% lebih gelap (140 menjadi 125) dan kuning sedikit bergeser di semua pemutar yang mematuhi tanda warna. Video #1 tidak terkena, karena `post.py` versi itu memakai filter `scale=out_color_matrix=bt709`.

**Perbaikan, tanpa kredit, di sandbox Higgsfield.** Frame dibaca dari master bersih dengan matriks BT.601 (warna asli kembali), caption yang sama dibakar ulang, lalu di-encode dengan matriks BT.709 yang benar (CRF 17). Suara disalin apa adanya dari versi pertama. Master bersih tidak di-encode ulang; hanya tanda matriksnya dibetulkan, jadi gambarnya identik.

**Pemeriksaan v1.1.** 2.052 frame, 68,4 detik, −14,5 LUFS; kuning caption terbaca (254, 213, 56); selisih rata-rata terhadap versi pertama yang dibaca sebagai BT.601 hanya 1,6 dari 255 (derau kompresi); md5 file yang diunggah sama dengan file hasil encode.

**Pencegahan.** `kit/captions.py` selalu memakai filter matriks eksplisit, dan `kit/box/qa_final.py` membandingkan frame video dengan frame PNG dalam dua matriks dan mencetak `COLOUR OK` atau `COLOUR FAILED`.

**Catatan kecil lain dari sesi yang sama.** Dengan `align.py` v1.0, dua kata ("Lima" di awal baris S10 dan "Katup" di S11) kini dimulai tepat setelah jeda; di video ini caption dan cue kedua kata itu muncul ±0,25 detik terlalu awal. Tidak dirender ulang.

## Jalur yang benar-benar dipakai

1. Naskah varian B dari plan dipakai tanpa perubahan kata; tabel cek fakta ada di `script_id.md`.
2. Audisi lima suara dengan dua kalimat yang sama, diukur di sandbox Higgsfield, lalu VO penuh. Take 1 terlalu lambat (92,3 detik); take 2 memakai tag tempo di awal teks (78,4 detik).
3. Olah audio (`kit/audio/vo_prep.py`): 75 jeda dirapatkan dari 15,5 menjadi 9,5 detik, tempo 1,088×, kenyaringan −14,4 LUFS.
4. Waktu per kata (`asr.py` + `align.py`): 188 kata, 15 di antaranya diinterpolasi, 43 ditempel ke jeda nyata.
5. Kit fungsi dipisah dari skrip video #1 (`kit/make_kit.py`), ditambah pencarian cue lewat ID kalimat dan kata.
6. Scene ditulis sebagai kode dan diperiksa lewat lima putaran still CPU di workspace Claude.
7. Box GPU `compute` 1× L40S: setup, 6 still uji 64 sampel, render 3 proses paralel.
8. Pemeriksaan otomatis antar-frame menemukan cacat di render pertama; semua frame dirender ulang tanpa persistent data dan diperiksa lagi.
9. Pemeriksaan yang sama pada render kedua menemukan kesalahan animasi titik aliran air; skrip diperbaiki dan dua rentang frame yang kena dirender ulang.
10. Caption + encode, master bersih, QA file final, unggah, box dimatikan.

## Cacat render pertama dan perbaikannya

**Gejala.** Pada render pertama, salah satu dari tiga proses menggambar objek yang baru berubah sebagai bentuk hitam pekat, sementara dua proses lain menggambarnya benar. Karena frame dibagi berselang ke tiga proses, hasilnya kedip 10 Hz. Contoh yang dilihat langsung: longsoran lumpur di lubang tampil hitam di frame 229–250 milik proses pertama (sampai 185.395 piksel hitam per frame), sedangkan frame 249, 251, 253 di sekitarnya normal.

**Cara ketemu.** Bukan dari still. Enam still uji di box bersih. Contact sheet pertama dari frame hasil render hanya memperlihatkan satu segitiga hitam kecil dan melewatkan rentetan cacat di proses lain, karena semua frame contohnya (waktu kelipatan 0,1 detik) milik proses yang sama. Yang menangkap seluruhnya adalah skor "frame yang berbeda dari kedua tetangganya" pada thumbnail semua frame (`kit/box/scan.py`), ditambah hitungan piksel hitam pekat.

**Ukuran masalah.** Dari 1.218 frame pertama, 239 ditandai tersangka (proses 0: 23, proses 1: 43, proses 2: 173), berupa rentetan panjang pada satu proses, misalnya proses 2 dari detik 2,97 sampai 7,47 dan dari 9,47 sampai 17,17. Pembanding langsung untuk frame 1–180: 31 frame render pertama berbeda dari render ulang, semuanya milik proses 2; frame yang lain sama sampai selisih 0,07 dari 255 per blok.

**Sebab.** Opsi `use_persistent_data` Cycles, yang menyimpan data scene antar-frame di tiap proses. Proses baru yang langsung melompat ke frame bermasalah menggambarnya dengan benar, jadi kesalahannya ada di keadaan yang terbawa, bukan di scene. Mekanisme pastinya belum dibuktikan (dugaan ada di `pipeline-runbook.md` bagian 12).

**Perbaikan.** Persistent data dimatikan (`KIT_PERSIST=0`; sekarang bawaan kit) dan semua 2.052 frame dirender ulang. Render pertama dihentikan di frame 1.504 dan tidak dipakai. Scan pada render ulang: tidak ada lagi rentetan tersangka pada satu proses dan tidak ada objek hitam. Yang tersisa, 64 tersangka yang tersebar rata di ketiga proses, ternyata berasal dari kesalahan animasi di bagian berikut.

**Biaya.** Render pertama memakan ±28 menit box (±33 kredit) yang terbuang. Tanpa persistent data kecepatannya 0,74 frame per detik (2.052 frame dalam 46 menit 25 detik), dibanding 0,90–0,95 dengan persistent data.

**Video #1.** Dirender dengan persistent data juga. Scan pada master bersihnya (di sandbox, gratis) menemukan 5 tersangka dari 1.980 frame, dan kelimanya gerak cepat yang sah (ayunan sekop, papan nama saat kamera bergerak, truk melintas). Video #1 tidak terkena.

## Kesalahan animasi yang ikut tertangkap

Setelah render kedua bersih dari cacat di atas, scan masih menandai 64 frame, tersebar rata di ketiga proses. Potongan tiga frame berurutan untuk 12 tersangka terkuat memperlihatkan sebabnya, dan kali ini sebabnya ada di skrip scene:

**Titik aliran air.** Tiap titik berjalan di sepanjang lintasan pipa lalu melompat kembali ke awal. Kunci "titik terakhir" dan kunci "titik pertama putaran berikutnya" jatuh pada waktu yang persis sama, dan Blender mengganti kunci yang lama bila ada kunci baru di frame yang sama. Akibatnya ruas terakhir tiap lintasan tidak pernah dilalui: titik terbang lurus dari titik kedua-terakhir ke titik awal. Di layar, titik air melayang di luar pipa (dari dasar pipa naik pompa ke skimmer), melesat melintasi kolam (jalur balik), dan air dari katup hidrostatik naik-turun di lubangnya alih-alih menyebar ke kolam. Perbaikan: kunci titik terakhir dimajukan 0,004 detik.

**Garis bau.** Kunci yang ditambahkan setelah `show()` atau `extend()` mewarisi interpolasi CONSTANT dari kunci sebelumnya, jadi denyut garis bau menjadi gelombang kotak dengan satu kedipan sepanjang 1,5 frame di detik 41,6. Perbaikan: interpolasi BEZIER diberikan eksplisit dan denyut diakhiri di kelipatan periode.

Kedua kesalahan ini lolos dari lima putaran still karena still hanya memperlihatkan posisi di satu waktu; titik yang melayang terlihat seperti titik biasa. Yang dirender ulang hanya frame yang terpengaruh: 695–1262 dan 1680–1849 (738 frame). Tiga frame di luar rentang itu dirender ulang sebagai pembanding untuk memastikan perbaikan tidak mengubah bagian lain. Hasilnya: ketiga frame pembanding sama dengan frame lama (selisih blok terbesar 0,06 dari 255), tersangka turun dari 64 menjadi 24, dan 12 yang terkuat semuanya gerak yang sah (gerak kamera cepat, tag yang muncul dengan pantulan, kuman dan cipratan yang bergerak).

Versi sebelum perbaikan sempat terunggah; sudah digantikan dan tidak dipakai.

## Angka terukur

| Hal | Terukur |
|---|---|
| Setup box | ±3 menit (sempat berjalan dobel karena salah perintah; normalnya ±80 detik) |
| Still uji 1080×1920, 64 sampel + denoise, 1 proses | 1,3–1,7 detik per frame |
| Render pertama, 3 proses, persistent data hidup | 0,90–0,95 frame per detik; GPU 94% terpakai |
| Render ulang, 3 proses, persistent data mati | 2.052 frame dalam 46 menit 25 detik (0,74 frame per detik); GPU 99% terpakai |
| Render ulang sebagian setelah perbaikan animasi | 738 frame dalam 17 menit 18 detik |
| Caption + encode + master bersih + scan (bersamaan) | 2 menit 38 detik untuk kedua encode; ±3 menit sampai contact sheet selesai |
| Total box menyala | 1 jam 51 menit 47 detik = 132,29 kredit (batas yang disetujui: 200) |
| Suara | audisi 4,70 (4 × 1,15 + 0,10) + take 1 5,98 + take 2 5,98 = 16,66 kredit |

## Audisi suara

Dua kalimat yang sama (33 kata) untuk tiap suara, diukur dengan `kit/audio/audition.py`.

| Suara | Durasi klip | Total jeda | Suku kata per detik saat bicara | Kata dikenali | Nada dasar | Kenyaringan |
|---|---|---|---|---|---|---|
| Cillian (Eleven v4) | 15,8 dtk | 3,4 dtk | 6,3 | 29 dari 33 | 140 Hz | −18,4 LUFS |
| **Marcus (Eleven v4)** | 16,1 dtk | 3,8 dtk | 6,3 | 32 dari 33 | 140 Hz | −21,3 LUFS |
| Julian (Eleven v4) | 15,7 dtk | 3,1 dtk | 6,2 | 31 dari 33 | 136 Hz | −19,5 LUFS |
| Maya (Eleven v4) | 16,0 dtk | 3,8 dtk | 6,4 | 32 dari 33 | 211 Hz | −17,9 LUFS |
| Qwen Audio 3.0 TTS Flash | 21,5 dtk | 6,0 dtk | 5,0 | 31 dari 33 | 123 Hz | −12,4 LUFS |

Marcus dipilih karena paling banyak kata yang dikenali mesin transkripsi di antara suara pria (satu-satunya selisih, "pompa" terdengar "pompah", muncul di semua suara). Ini pilihan dari ukuran, bukan dari telinga. Pilihan dengan telinga manusia tetap lebih baik; ukuran hanya menyaring.

## Koreksi terhadap plan

- **Gerbang review dilewati.** Plan menyediakan G1 (pengguna memilih suara), G2 (still di chat), dan G3 (animatic). Pengguna meminta langsung dieksekusi, jadi pilihan bawaan plan dipakai dan review baru terjadi pada video jadi.
- **Biaya GPU.** Plan memperkirakan ±65–100 kredit untuk render final; kenyataannya 132,29 karena satu render terbuang dan sepertiga frame dirender ulang setelah perbaikan animasi. Scene ini ±25% lebih berat daripada video #1 (0,95 dibanding 1,2 frame per detik pada 3 proses dengan persistent data), jauh di bawah dugaan plan 1,5–2,5×.
- **Tempo suara.** Plan memperkirakan 6,0–7,0 suku kata per detik. Tanpa tag tempo, preset membaca ±4,6; dengan tag dan pengolahan, hasil akhirnya ±6,3.
- **Teks di layar.** Plan menyebut empat tag; yang dibuat tujuh jenis (`HARI 1/3/5` dan `KAPORIT` ditambahkan).
- **Kit.** Rencana "pisahkan kit lalu uji regresi pada video #1" baru separuh jalan: kit dipakai penuh oleh video #2, uji ulang pada still video #1 belum dijalankan.

## Pelajaran untuk video berikutnya

- Scan semua frame sebelum encode, dan jangan menilai animasi dari still saja. Scan yang sama menangkap dua jenis masalah: cacat render dan kesalahan animasi.
- Lihat potongan tiga frame berurutan untuk tersangka terkuat (`trip_png.py`); angka skor saja tidak menjelaskan apa yang salah.
- Untuk tiap gerak berulang, cetak daftar kunci satu objek contoh sebelum render. Dua kunci di waktu yang sama saling mengganti, dan kunci baru mewarisi interpolasi kunci sebelumnya.
- Contact sheet harus mengambil frame dari ketiga fase proses.
- Render tanpa persistent data; harganya kecil.
- Selama box menyala, kerjakan hanya yang butuh box. Alat analisa yang berat memperlambat render karena box hanya 4 vCPU.
- Tag tempo di awal teks lebih murah daripada take ulang; rapatkan jeda sebelum menaikkan tempo.
- Cue lewat `T(id kalimat, kata)` membuat naskah bisa diganti tanpa menyentuh angka waktu.
- Rincian teknis lain (interpolasi kunci, permukaan sebidang, perintah shell yang menjebak) ada di `pipeline-runbook.md` bagian 9.

## Lokasi file di repo

- `examples/video02-kolam-renang-id/`: skrip scene (sudah dalam bentuk job kit v1.0), `job.env`, `script.txt`, `keywords.txt`, `words.json`, `script_id.md` (naskah, gambar per baris, cek fakta, sumber), dan contact sheet preview.
- `kit/`: kode yang dipakai (versi 1.0, hasil merapikan alat video ini).
- File video, suara, frame PNG, dan `.blend` tidak disertakan.

## Yang belum dikerjakan

- Musik dan efek suara. Bisa ditambahkan di atas master bersih tanpa GPU.
- Audio belum didengarkan manusia, dan gerak belum ditonton; Claude hanya mengukur dan melihat frame. Yang diukur pada file final: 2.052 frame, 68,4 detik, −14,5 LUFS; md5 file di link sama dengan file di box; transkripsi ulang mengenali 172 dari 188 kata, dan pada 170 kata yang bisa dibandingkan awal kata bergeser median 0,00 detik (95% ≤ 0,02 detik) dari posisi yang direncanakan, 95% ≤ 0,08 detik terhadap waktu caption. Mesin transkripsi mendengar tiga kata sedikit berbeda ("diam" → "biam" di detik ±21, "mangkuk" → "mangku" di detik ±48, "karet" → "karep" di detik ±63); itu bagian yang paling layak didengarkan.
- Suara dipilih dari ukuran. Bila suara diganti, VO, waktu per kata, dan render harus diulang.
- Nama channel, watermark, cover.
- Review manusia atas look, maskot, tempo caption, dan pelafalan.
