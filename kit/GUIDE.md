# Panduan kerja kit v1.1 — rujukan untuk skill

Dibaca per bagian saat dibutuhkan. Perintah di sini berlaku untuk kit v1.1 (yang baru dari video #3 ditandai "v1.1"). `docs/pipeline-runbook.md` (v0.3) di repo adalah latar belakang dan riwayat; perintah di dalamnya versi lama.

## 1. Menulis scene

**Konvensi.** Satuan meter. Bidang potong di y = 0, kamera melihat ke arah +Y, Z ke atas, tanah di z = 0. Lensa 36 mm pada sensor 36 mm: tinggi bingkai = jarak kamera, lebar = 0,5625 × jarak. Subjek di 15–60% tinggi layar; caption di 67–70%; 20% terbawah tertutup tombol aplikasi. Nama objek berawalan kelompok (`ENV_`, `PIPE_`, `TAG_`), karena nama itu muncul di laporan scan.

**Waktu.** Semua cue berupa variabel `T_… = T(id_kalimat, kata, ke, end)`. Kata harus persis seperti di naskah ("air" tidak menemukan "airnya"). Tidak ada detik yang diketik tangan; pergeseran ditulis relatif (`T_PUMP - 0.4`).

**Aturan gambar.** Satu kalimat = satu perubahan di layar. Benda muncul saat disebut, tidak sebelumnya. Istilah teknis diberi tag saat diucapkan. Rantai sebab-akibat digambar sebagai gerak: air mengalir, level naik, dinding ambruk, panah menekan.

**Kosakata** (argumen: `grep -n "^def " explainer_kit.py scene_extras.py` atau `API.md`):

| Kebutuhan | Fungsi |
|---|---|
| Bentuk | `box`, `cyl`, `sphere`, `prism`, `prismp`, `prism_yz`, `patch`, `patchp`, `tube`, `pipe`, `hinge`, `capsule`, `empty` |
| Muncul dan hilang | `hidden_until`, `appear`, `pop`, `vanish`, `grow`, `show`, `extend` (pipa menggambar dirinya) |
| Gerak | `travel`, `key`, `pulse`, `key_input` (nilai material), `tint` (warna + alpha) |
| Air | `water_material`, `level_box` + `water_body` + `level` (permukaan naik-turun, lantai miring pun benar) |
| Aliran di pipa | `flow(nama, front(titik), t0, t1)` |
| Teks | `label(..., billboard=True)` untuk tag, `sign`, `text`; panah: `arrow` |
| Karakter | `make_char` (maskot seri: helm kuning, rompi oranye), `arm`, `raise_arms`; hiasan: `tree`, `palm` |
| Kamera | `orbit(azimut, elevasi, jarak, target)`, `pose`, `shot(t0, t1, pose, mv=…, cut=…)`, `project(pose, titik)` |
| Dunia | `sun_d.energy` / `sun_d.color` dan `sky` bisa di-keyframe (senja, mendung) |

**Kamera.** `shot()` bergerak mulus dari pose sebelumnya lalu drift pelan; `cut=True` memotong keras. Ikuti gaya referensi: potongan keras per beat (video #1) atau satu gerak sinambung (video #2). Hitung posisi layar dengan `project()` sebelum merender, supaya tag tidak menutupi subjek dan subjek tidak jatuh ke daerah caption.

**Aturan keyframe Blender 5.3 yang pernah merusak render:**

1. Menyisipkan kunci pada frame yang sudah punya kunci **mengganti** kunci itu. Gerak berulang "sampai di ujung lalu lompat ke awal" menaruh kunci ujung 0,004 detik sebelum putaran berikutnya (`flow()` sudah begitu).
2. Kunci ketiga dan seterusnya mewarisi interpolasi kunci sebelumnya. Setelah `show()` atau `extend()` (kunci CONSTANT), beri `ip` eksplisit: `pulse(o, t0, t1, ip='BEZIER')`.
3. BEZIER otomatis di samping kunci "sembunyi" menunda gerak. Pakai `ip='SINE', ease='EASE_IN_OUT'`.
4. Dua permukaan sebidang tampil hitam: geser salah satunya 4 mm. Transparansi bertumpuk: bidang satu sisi.
5. Objek "tumbuh" dari skala nol tetap terlihat sebagai lembaran: sembunyikan sampai cue (`grow` dan `pop` sudah melakukannya).
6. (v1.1) `pop(o, t)` menaruh kunci terakhirnya di `t + dur` (bawaan 0,28 detik). `vanish()` yang selesai sebelum itu kalah: benda muncul lagi dan menetap. Untuk benda yang tampil kurang dari ±0,4 detik (angka penghitung yang berganti cepat), pendekkan `dur` pada `pop` dan `vanish`, lalu baca jadwalnya di `scene_check.py`.

**Pola dari video #3 (v1.1).** Contoh kodenya ada di `examples/video03-mesin-crv-id/engine_video.py`; fungsi yang disebut di bawah didefinisikan di skrip itu, belum di kit.

- **Gerak mekanis berulang** (mesin, pompa, roda gigi): buat satu kurva sudut untuk seluruh video, yaitu integral profil kecepatan per kalimat, lalu hitung posisi semua komponen dari sudut itu dan tulis satu kunci linear per frame (`bake`, `bake_input`). Kecepatan bisa berubah per kalimat tanpa merusak hubungan antar-komponen. Untuk menjatuhkan satu kejadian tepat pada sebuah kata, skalakan sudut yang ditempuh dalam satu jendela waktu (`land`), jangan menggeser fase: mesin tidak boleh terlihat mundur.
- **Benda berputar pada 30 fps** tampak diam atau mundur bila sudut per frame mendekati jarak antar-jeruji. Batasi putaran per detik atau kurangi jumlah jeruji dan lubang.
- **Alat ukur dan angka yang menempel di layar**: jadikan anak kamera pada kedalaman tetap, matikan bayangan dan pantulannya, dan beri nama berawalan sama (misalnya `HUD_`). Sisihkan satu jalur layar untuknya (video #3: 8–25% dari atas) dan taruh titik fokus kamera di bawah jalur itu (`frame`). Tag di dunia diberi ukuran menurut jarak kamera supaya terbaca sama di shot jauh dan dekat (`tag`).
- **Menukar komponen**: komponen baru tumbuh dulu, baru yang lama hilang. Urutan sebaliknya meninggalkan lubang kosong beberapa frame, dan itu hanya terlihat di strip gerak.
- **Api dan kilat**: emisi di atas ±3 terpotong pada view transform Standard (jingga menjadi kuning, kuning menjadi putih) dan warna rata terbaca sebagai benda padat. Pakai gradasi dan opasitas, dengan kekuatan yang dipanggang per frame. Kilat harus lebih kecil dari ruang yang memuatnya pada frame puncaknya.
- **Angka di layar hanya dari tabel cek fakta.** Kalau angkanya tidak ada, pakai label tanpa angka (video #3: jarum suhu bertanda C dan H).

**Periksa sebelum GPU.** Bangun scene dengan mode `none` dan cetak kunci satu objek contoh tiap jenis gerak: `[(k.co.x, k.co.y, k.interpolation) for c in fcurves_of(obj) for k in c.keyframe_points]`. Untuk kamera, langkah posisi per frame harus naik-turun mulus tanpa lompatan tunggal. Still tidak bisa menunjukkan lintasan yang salah.

(v1.1) `python3 scene_check.py <scene>.py` mencetak semua itu dalam ±30 detik tanpa render: ukuran scene, langkah kamera terbesar dan lompatan satu frame, jadwal tampil tiap benda yang menempel di layar (`COMES BACK`, `STAYS TO THE END`), dan daftar kilat, yaitu benda yang ukurannya memuncak hanya 1–2 frame, beserta detik puncaknya. Jalankan setiap kali skrip scene berubah, juga setelah perbaikan kecil di tengah render: di video #3 satu perbaikan membawa label yang tertinggal, dan satu kilat yang terlalu besar lolos dari semua still.

**Contoh lengkap** di folder `examples/` repo (baca bagiannya saja dengan `grep`, jangan seluruh berkas): `video02-kolam-renang-id/pool_video.py` (air, pipa, aliran, senja, satu gerak kamera), `video03-mesin-crv-id/engine_video.py` (mesin berputar yang dipanggang per frame, potongan boolean, alat ukur di layar, pertukaran komponen), dan `video01-septic-system-en/septic_video.py` (potongan keras, label di bidang potong, truk; skrip mandiri dari sebelum kit ada).

## 2. Preview di CPU

```bash
python3 <scene>.py still 270 480 4 st/r1 <detik tiap cue>        # 2–3 detik per still
python3 captions.py test st/r1/t_00360.png 3.6 st/r1/c_00360.png # caption di atas still
python3 <scene>.py still 540 960 12 st/hi <detik kunci>          # warna dan teks, ±20 detik per still
```

Susun contact sheet dan lihat sendiri: komposisi, benda yang muncul sebelum waktunya, label terbaca, caption tidak menutupi subjek. Putaran berikutnya hanya untuk waktu yang bermasalah. Warna dinilai di ≥ 12 sampel; 4 sampel + denoise menipu. Dua video pertama butuh 4–5 putaran; video #3 butuh 6.

(v1.1) Dua jenis still tambahan sebelum GPU:

- **Strip gerak**: 5–7 frame berurutan (270×480) di sekitar tiap pertukaran komponen dan tiap benda yang masuk atau keluar. Lubang kosong dan benda yang tampil sekejap sebelum waktunya hanya terlihat di sini.
- **Frame puncak**: satu still ukuran penuh tepat pada detik puncak tiap jenis kilat yang dicetak `scene_check.py`. Still "di sekitar kata" memotret fase redupnya.

Mode `list` merender nomor frame tertentu: `python3 <scene>.py list 270 480 4 st/mo frames.txt` (berkas berisi nomor frame dipisah spasi).

## 3. Suara per bahasa

| Bahasa | Suara bawaan | Tempo terukur | Catatan |
|---|---|---|---|
| Inggris | Eleven v4, preset Cillian | ±2,7 kata per detik | 171 kata = 64 detik, dipakai tanpa tag |
| Indonesia | Eleven v4, preset Marcus, teks diawali `[quick, energetic pace] ` | ±6,3 suku kata per detik setelah diolah | tanpa tag hanya 4,6; bahasa Indonesia ±2,2 suku kata per kata |

Eleven v4 tidak punya pengatur kecepatan atau parameter bahasa; bahasa mengikuti teks. Biaya ±0,47 kredit per 100 karakter per take. `vo_prep.py` merapatkan jeda dan mempercepat paling banyak 1,10×. Audisi (opsional): dua kalimat yang sama untuk 4 suara, `audition.py ref.txt <lang>`, lalu pengguna memilih dengan telinga.

(v1.1) Catatan bahasa Indonesia dari video #3 (199 kata, satu take: 78,5 detik mentah, 74,0 setelah diolah):

- Mesin transkripsi menulis angka sebagai digit, jadi kata-kata angka ("seribu tiga puluh delapan") mendapat waktu lewat interpolasi di `align.py`. Itu cukup untuk caption; cue yang harus tepat jangan digantungkan pada kata di tengah rangkaian angka.
- Singkatan yang dieja tanpa huruf vokal ("CR-V") dihitung satu suku kata dan mendapat jatah waktu terlalu pendek. Bandingkan dengan waktu mentah di `asr_proc.json` dan betulkan `words.json` dengan skrip kecil yang disimpan di folder job (contoh: `examples/video03-mesin-crv-id/patch_words.py`), sebelum scene mulai ditulis.
- `estimate_audio_cost` untuk `elevenlabs_v4` meminta bidang `dialogue`; kalau ditolak, pakai tarif terukur di atas.

## 4. Membaca hasil scan frame

`scan.py` menandai frame yang menonjol dari kedua tetangganya. Yang sah: kamera berpindah cepat, benda kecil yang melintas cepat (titik aliran, percikan), puncak pantulan tag yang baru muncul (satu frame lebih besar), pola berulang saat kamera mulai bergerak. Yang cacat: objek hitam atau tertinggal pada frame milik satu proses saja (keadaan basi: pastikan `KIT_PERSIST=0`), benda melesat keluar lintasannya (bug animasi: lihat aturan keyframe). Tanda bahaya di ringkasan: tersangka menumpuk di satu proses, atau piksel hitam melonjak pada satu frame. Lihat tersangka terkuat dengan `trip_png.py` (frame PNG) atau `sandbox/trip.py` (video jadi).

(v1.1) **Gerak berulang** (mesin berputar, nyala pembakaran) menghasilkan puluhan tersangka sah yang periodik: 104 dari 2.277 frame di video #3. Bila periodenya kelipatan jumlah proses, tersangka itu menumpuk di satu proses dan tampak seperti cacat keadaan basi. Bedakan dari periodenya dan letaknya di layar, lalu lihat satu contoh tiap kelompok. Lonjakan piksel hitam yang berulang dua kali per putaran di tempat yang sama adalah celah gelap yang sah. Sebaliknya, satu kilat yang menembus dinding wadahnya selama 1 frame memang cacat, dan scan menandainya: lihat frame puncak tiap kelompok kilat.

## 5. Jebakan operasional

| Gejala | Sebab | Perbaikan |
|---|---|---|
| Panggilan sandbox atau box "Bad Gateway" | menunggu lebih dari ±60 detik | `background:true` atau `nohup … &`, lalu poll pendek; cek keadaan sebelum mengulang |
| Perintah mati dengan kode 143 | `pkill -f "pola"` membunuh shell sendiri | pola berkurung siku: `pkill -f "[p]ool_video.py anim"` (`job.sh` menyediakan `$PAT`) |
| Setup jalan dua kali | `a && b && nohup c &` menaruh seluruh rantai di latar | langkah pendek satu per satu; hanya perintah panjang yang diberi `nohup` |
| PUT kedua ke URL presigned ditolak | URL sekali pakai, wajib header `If-None-Match: *` | minta URL baru untuk tiap unggahan (`up.sh` sudah membawa header) |
| Warna video lebih gelap dari frame | RGB→YUV memakai BT.601 padahal ditandai BT.709 | `captions.py` memakai filter `scale=out_color_matrix=bt709`; `qa_final.py` mencetak `COLOUR OK` |
| Kedip 10 Hz, objek hitam di sepertiga frame | `use_persistent_data` pada render multi-proses | biarkan `KIT_PERSIST=0`; scan semua frame |
| Contact sheet bersih padahal berkedip | semua contoh jatuh di proses yang sama | `qa_final.py` mengambil frame dari semua proses |
| Whisper mengacaukan awal audio | naskah dijadikan `initial_prompt` | jangan beri prompt; teks selalu dari naskah |
| Kata pertama setelah titik muncul terlalu awal | Whisper menaruh awal kata di dalam kata sebelumnya | `align.py` v1.0 menempelkannya ke akhir jeda; pastikan baris "words that span a pause" kosong |
| Potongan tiga frame bergeser satu | `ffmpeg -ss` memberi frame pertama pada atau sesudah waktu | minta `(f−1)/fps − 0,012` (alat kit sudah begitu) |
| Render melambat saat alat QA jalan | box 4 vCPU, tiga proses render memakai ±3,3 | satu alat analisa pada satu waktu, dengan `nice` |
| (v1.1) Unggah ditolak `ExpiredToken` | URL unggah hanya hidup ±1 jam sejak diminta, walau `X-Amz-Expires` lebih panjang | minta URL saat render tinggal ±10 menit; `after.sh` menunggu `urls.sh` muncul |
| (v1.1) Frame kontrol berbeda setelah render ulang sebagian | perbaikan mengubah sesuatu di luar rentang yang dirender ulang (label tertinggal, benda yang kembali) | pilih frame kontrol tepat sesudah tiap rentang; jalankan `scene_check.py` sebelum `rerender.sh` |
| (v1.1) Mengetik ulang seluruh kit ke sandbox | workspace tidak bisa mengunggah ke Higgsfield | sandbox dan box mengambil kit dengan `git clone` dari repo publik; hanya berkas job yang dikirim sebagai teks |
| File referensi berubah saat disalin | lewat `/mnt/user-data/outputs` (manifest C2PA) | jangan lewatkan file pihak ketiga di sana |

## 6. Angka acuan

| Hal | Video #1 (66 detik, 710 objek) | Video #2 (68,4 detik, 834 objek) | Video #3 (75,9 detik, 771 objek) |
|---|---|---|---|
| Still CPU 270×480, 4 sampel | 2–3 detik | 2–3 detik | 11–15 detik pada 405×720 (logam, boolean, lampu area) |
| Setup box | ±80 detik | ±3 menit (sempat dobel) | ±2 menit |
| Render 3 proses di 1× L40S | 1,2 fps (persistent data hidup) | 0,74 fps (persistent data mati, bawaan sekarang) | 0,60 fps; ±262 ribu kunci yang dipanggang per frame |
| Caption + encode + master bersih | ±3 menit | 2 menit 38 detik | 2 menit 36 detik |
| Box menyala | 37 menit = 43,72 kredit | 1 jam 52 menit = 132,29 kredit, termasuk satu render terbuang dan satu render ulang sebagian | 1 jam 34 menit = 110,90 kredit, termasuk dua render ulang sebagian (±26) |
| Suara | 4,37 kredit | 16,66 kredit (audisi + 2 take) | 6,44 kredit (1 take) |

Perkiraan bersih: menit box ≈ jumlah frame ÷ 0,74 ÷ 60 + 15. Dengan L40S 71 kredit per jam, 68 detik video ≈ 75 kredit. Scene dengan banyak kunci per frame atau banyak objek berkurva lebih lambat: pakai ÷ 0,6. Kecepatan render dibatasi CPU box (4 vCPU); GPU hanya terpakai 30–50%, jadi GPU yang lebih mahal tidak mempercepat. Still uji di box (±2,5 detik, satu proses) tidak mewakili kecepatan render penuh (±5 detik per frame per proses saat tiga proses berjalan bersama); proyeksikan ulang dari 2–3 menit pertama render.
