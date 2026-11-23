# Video 03 — catatan produksi "Mesin CR-V tembus seribu tenaga kuda" (ID)

23 November 2026 · video ketiga, produksi pertama dengan kit v1.0 dan ketiga skill · berkasnya di `examples/video03-mesin-crv-id/`

Catatan ini versi repo: tautan hasil, ID media, sidik file, saldo akun, dan lokasi penyimpanan pribadi dihilangkan. "Plan" yang disebut di sini adalah dokumen rencana internal; naskah dan cek faktanya ada di `examples/video03-mesin-crv-id/script_id.md`.

Video ini dibuat dari video referensi berbahasa Inggris tentang mesin turbo 1.000 hp. Bedahnya ada di `video03-reference-analysis.md`. Naskahnya ditulis ulang dari fakta yang dicek, bukan diterjemahkan.

## 1. Hasil

| Hal | Nilai |
|---|---|
| Keluaran | video final (61,4 MB) dengan caption dan suara, plus master bersih (77,1 MB, tanpa caption dan suara) |
| Format | H.264 1080×1920, 30 fps, yuv420p, BT.709, 2.277 frame, 75,9 detik; AAC 48 kHz stereo; −14,4 LUFS, puncak −4,2 dBFS |
| Naskah | 22 kalimat, 199 kata, bahasa Indonesia; caption gaya `phrases`, 80 frasa dengan jeda manual |
| Kredit | suara 6,44 + GPU 110,90 = **117,34** (batas yang disetujui: suara 15, GPU 160) |

## 2. Angka terukur

| Hal | Angka |
|---|---|
| Suara | Eleven v4, preset Marcus, tag `[quick, energetic pace]`, satu take: 78,45 detik mentah → 73,98 detik setelah `vo_prep.py` (−14,3 LUFS) |
| Waktu per kata | 199 kata, tidak ada kata yang melintasi jeda. Mesin transkripsi menulis angka sebagai digit, jadi 37 kata diberi waktu lewat interpolasi; "CR-V" dibetulkan di dua tempat dengan `patch_words.py` |
| Scene | `engine_video.py`, 484 baris, 771 objek, 71 material, ±262 ribu kunci |
| Pratinjau CPU | 6 putaran: ±100 still 405×720 (11–15 detik per still), 3 still 720×1280, 42 still strip gerak di sekitar pergantian komponen; semuanya gratis |
| Still uji di GPU | 2,5 detik per still (1080×1920, 64 sampel, OptiX); tampilannya sama dengan pratinjau CPU |
| Render penuh | 2.277 frame dalam 63 menit 25 detik, 3 proses: 0,60 frame per detik (±5,0 detik per frame per proses). GPU hanya terpakai 30–50%; batasnya CPU box (4 vCPU) |
| Encode | final + master bersih + scan paralel: 2 menit 36 detik |
| Render ulang sebagian | 189 frame, lalu 37 frame |
| Box menyala | 1 jam 33 menit 43 detik |

Dari 110,9 kredit GPU, ±85 untuk jalur lurus (setup, still uji, render penuh, encode, unggah pertama) dan ±26 untuk dua putaran perbaikan beserta unggah ulangnya.

## 3. Cara scene dibangun

- **Satu kurva sudut engkol untuk seluruh video.** Profil kecepatan per kalimat (0 sampai 3,3 putaran per detik di layar) diintegralkan menjadi sudut per frame; kruk as, piston, setang, klep, per, noken as, nyala pembakaran, dan ngelitik dipanggang per frame dari sudut itu. Hasilnya konsisten secara mekanis pada kecepatan berapa pun. `land()` menskalakan sudut di dalam satu jendela waktu, supaya piston menyentuh klep tepat pada kata "dihantam" dan ngelitik pertama jatuh pada kata "meledak", tanpa mesin pernah berputar mundur.
- **Pertukaran komponen.** Dua set anak di bawah satu empty (piston dan setang cor ↔ tempa, per standar ↔ ganda, klep ↔ Inconel) dan dua kepala silinder utuh yang diangkat lalu dipindah ke luar set.
- **Alat ukur di layar.** Anak kamera pada kedalaman tetap dengan bayangan dan pantulan dimatikan; jalur atas layar (±8–25% tinggi) berisi jarum (boost, rpm, suhu), judul bab, nilai, dan penghitung tenaga. Titik fokus kamera ditaruh di bawah jalur itu.
- **Tag dunia berukuran menurut jarak kamera** (persen tinggi layar), supaya terbaca sama di shot jauh dan dekat.
- **Nyala pembakaran**: silinder dengan material bergradasi (terang di bawah kepala, tembus ke arah piston); kekuatan dan opasitasnya dipanggang per frame.

## 4. Temuan selama pratinjau (gratis)

- Nyala yang awalnya silinder kuning rata terbaca sebagai benda padat sewarna bidang potong. Emisi jingga dengan kekuatan di atas ±3 terpotong menjadi kuning pada view transform Standard; warna nyala dan sabuk bocor di sambungan kepala dipindah ke merah-jingga.
- Strip gerak menemukan dua hal yang tidak terlihat di still: lubang silinder kosong ±3 frame saat piston ditukar, dan cincin air pendingin yang tampil sebagai tabung biru 0,15 detik sebelum selongsong terakhir masuk. Keduanya diperbaiki: komponen baru tumbuh dulu, baru yang lama hilang.
- Pemeriksaan tanpa render: langkah kamera terbesar 0,65 unit per frame tanpa lompatan satu frame; celah klep-piston terkecil +0,133 di semua silinder kecuali klep buang silinder 1, yang memang disentuh pada 48,03 detik (kata jatuh di 48,02); mesin tidak pernah mundur.
- Putaran roda turbo dan jumlah lubang roda gila dibatasi supaya tidak tampak berputar mundur pada 30 fps.
- Suhu udara masuk tidak ada di tabel cek fakta, jadi jarum suhu hanya bertanda C dan H tanpa angka.

## 5. Pemeriksaan pada file final

- **Sidik file** di tautan sama dengan file di box.
- **Warna**: `COLOUR OK` pada final dan master bersih (selisih rata-rata 1,8–2,4 terhadap frame PNG dengan matriks BT.709; lebih buruk bila dibaca sebagai BT.601).
- **Sinkron** (transkripsi ulang file final): awal kata terhadap narasi median 0,000 detik, p95 0,020 detik; terhadap waktu caption p95 0,059 detik. 163 dari 199 kata dikenali; angka tidak ditranskripsi sebagai kata.
- **Frame kontrol**: frame 600, 1400, 1975, dan 2000 dirender ulang dengan skrip akhir dan sama dengan frame di video (selisih blok terbesar 0,03).
- **Scan semua frame**: 104 tersangka dari 2.277, tersebar di ketiga proses (41, 35, 28). Dua belas yang terkuat dilihat sebagai potongan tiga frame; sisanya digolongkan dari pola dan letaknya, tidak dilihat satu per satu:
  - nyala pembakaran dan ngelitik: berulang tiap putaran mesin, jadi selalu jatuh pada proses yang sama;
  - celah gelap antara setang dan kruk as yang muncul dua kali per putaran (lonjakan ±2.000–3.500 piksel hitam): dilihat pada tiga frame berurutan, bayangan yang sah;
  - komponen yang masuk atau keluar (turbo, kepala silinder, pertukaran kepala);
  - percikan saat klep dihantam, dan tag atau angka yang muncul.
- **Yang tidak bisa dinilai Claude**: suara belum didengar dan gerak belum ditonton. Kata yang ditulis berbeda oleh mesin transkripsi (detik video): "CR-V" 0,9 dan 33,3; "stud" 24,4; "VTEC-nya" 39,6; "noken as" 40,7; "Inconel" 51,9.

## 6. Yang menyimpang dari rencana

1. **Suhu udara tanpa angka** (lihat bagian 4).
2. **Tangki bahan bakar hanya muncul di bab 3** (merah "BENSIN" menjadi hijau "E85" di atas troli); di shot lain ia terpotong tepi layar.
3. **Kepala silinder dibedakan lewat warna potongan** (bawaan kuning pucat, Type R merah), di luar rencana tetapi membuat pertukarannya terbaca.
4. **URL unggah kedaluwarsa.** Empat URL diminta sebelum render dan dipakai 70 menit kemudian: semuanya ditolak dengan `ExpiredToken`, walau `X-Amz-Expires` 86.400 detik. URL baru diminta dan unggahan diulang (±2 menit box).
5. **Dua putaran perbaikan setelah render penuh:**
   - Scan menandai frame puncak ngelitik: bola kilat (skala 1,7) lebih besar dari silinder dan bersegi kasar, terlihat 1 frame tiap ledakan. Pratinjau CPU hanya memotret fase redupnya. Diperbaiki (skala paling besar 1,0; 24 segmen) dan 141 frame dirender ulang, bersama dua pergantian angka di layar yang sempat bertumpuk (48 frame).
   - Perbaikan pergantian angka itu sendiri membawa kesalahan: label "160" pertama di penghitung muncul kembali dan menetap, karena kunci akhir `pop()` (0,28 detik) jatuh setelah kunci `vanish()` yang dipercepat. Frame kontrol 2000 yang dirender ulang berbeda dari video, dan dari situ kesalahannya ketahuan sebelum serah terima. Diperbaiki dan 37 frame dirender ulang.
6. **Kode kit dikirim ke sandbox sebagai teks** (±123 KB, 21 berkas, semua sidik cocok), karena workspace Claude tidak bisa mengunggah ke Higgsfield dan repo publik ini belum ada.

## 7. Pelajaran (sudah masuk kit v1.1)

- **URL unggah Higgsfield hanya hidup ±1 jam.** Minta URL saat render tinggal ±10 menit. `after.sh` v1.1 menunggu `urls.sh` muncul.
- **Periksa frame puncak setiap kilat.** Efek yang hidup 1–2 frame (ledakan, percikan) harus dipotret tepat di frame puncaknya saat pratinjau, bukan di sekitar kata. `scene_check.py` mencetak detik puncaknya.
- **Jadwal label layar dicetak sebelum render.** `scene_check.py` mencetak rentang tampil tiap benda yang menempel di layar dan menandai `COMES BACK` atau `STAYS TO THE END`. `pop()` diikuti `vanish()` yang lebih cepat dari durasi `pop()` membuat label kembali.
- **Frame kontrol `rerender.sh`**: sertakan satu frame sesudah tiap rentang yang dirender ulang. Itulah yang menangkap label yang tertinggal.
- **Scan pada gerak berulang**: mesin yang berputar menghasilkan puluhan tersangka sah yang periodik dan menumpuk di satu proses bila periodenya kelipatan jumlah proses. Nilai dari periode dan letaknya, lalu lihat contohnya.
- **Kecepatan render dibatasi CPU box**, bukan GPU. Perkiraan menit box = frame ÷ 0,6 ÷ 60 + 10 untuk scene sebesar ini.
- **Emisi di atas ±3 terpotong** pada view transform Standard. Nyala diberi gradasi dan opasitas, bukan warna rata.
- **Satu kurva sudut untuk semua gerak mekanis**, dipanggang per frame, membuat kecepatan mesin bisa diubah per kalimat tanpa merusak hubungan piston, klep, dan nyala.
- **Mengirim berkas ke sandbox sebagai teks itu mahal.** Dengan repo ini, sandbox dan box cukup `git clone`, dan hanya scene serta berkas job yang dikirim.
