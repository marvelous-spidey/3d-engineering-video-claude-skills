---
name: 3d-engineering-video
description: Membuat short 3D vertikal yang menjelaskan cara kerja benda atau sistem teknik (kode Blender, narasi AI, caption per kata) dari naskah Indonesia, naskah Inggris, atau video referensi.
---

# Video 3D engineering

Hasil akhirnya: MP4 1080×1920 30 fps (link Higgsfield) dengan narasi dan caption, master bersih tanpa caption dan suara, skrip scene, naskah dengan cek fakta, dan catatan produksi. Semua gambar dibangun dari kode Blender dan semua gerak mengikuti waktu kata di narasi. Karena itu urutannya selalu: naskah → suara → waktu per kata → scene → render.

Skill ini berisi cara kerja. Alatnya ada di kit (kode, folder `kit/` di repo yang memuat skill ini) dan dua skill pendamping: `reference-short-teardown` (membedah video referensi) dan `higgsfield-blender-render` (render di GPU sewaan sampai file jadi).

Skill ini ditulis untuk Claude yang punya workspace Linux (bash dan Python) dan konektor Higgsfield MCP. Kalau salah satunya tidak ada, katakan apa yang kurang dan berhenti.

## 0. Siapkan tempat kerja

1. Pasang kit ke `~/kit`:

   ```bash
   REPO=https://github.com/davidalfasunarna/3d-engineering-video-claude-skills
   [ -f ~/kit/VERSION ] || { git clone --depth 1 "$REPO" ~/3dv-repo && cp -r ~/3dv-repo/kit ~/kit; }
   cat ~/kit/VERSION
   ```

   Kalau GitHub tidak terjangkau, pakai salinan kit dari pengguna: folder `kit/` yang ia lampirkan atau sambungkan, atau dokumen `kit_tools.md` di Project-nya (dibuka dengan `python3 make_bundle.py unpack kit_tools.md ~/kit`). Tanpa kit, skill ini tidak bisa dijalankan.
2. Cek alat di workspace: `python3 -c "import bpy, PIL, numpy; print(bpy.app.version_string)"` dan `ffmpeg -version`. Kalau `bpy` belum ada: `pip install --break-system-packages bpy==5.3.0 pillow numpy` (butuh Python 3.13, ±1 GB). Setelah pertama kali memasang, jalankan `bash ~/kit/selftest.sh` sampai `SELFTEST PASSED` (3–10 menit di CPU, tanpa kredit).
3. Cek konektor Higgsfield: alat `generate_audio`, `sandbox_exec`, `media_upload`, `gpu_list_gpus`, dan `gpu_rent` harus tersedia. Kalau tidak, minta pengguna menghubungkan Higgsfield MCP dulu.
4. Kalau pengguna punya catatan dari video sebelumnya (misalnya `worklog.md` di Project atau folder lokalnya), baca keadaan terakhir dan keputusannya: nomor video berikutnya, serta suara dan gaya yang terakhir ia setujui.
5. `~/kit/GUIDE.md` dibaca per bagian saat sampai di langkahnya. Tiga job contoh ada di `~/3dv-repo/examples/`; video #3 adalah contoh jalur video referensi dan gerak mekanis. `docs/pipeline-runbook.md` hanya latar belakang; perintah di dalamnya versi lama.
6. Buat folder job: `mkdir -p ~/jobs/videoNN && cp ~/kit/job.env.example ~/jobs/videoNN/job.env`, isi `NAME`, `SCENE`, `LANG_CODE`, `CAPTION_STYLE`, lalu `bash ~/kit/newjob.sh ~/jobs/videoNN`.

## 1. Empat jalur masuk

| Yang diberikan pengguna | Bahasa video | Mulai dari |
|---|---|---|
| Naskah bahasa Indonesia | Indonesia | 1A |
| Naskah bahasa Inggris | Inggris | 1A |
| Video referensi (Inggris atau Indonesia) | bahasa sebaliknya, kecuali diminta lain | 1B, lalu 1A |
| Hanya topik | tanyakan bahasanya | 1B langkah 2–3, lalu 1A |

### 1A. Dari naskah

1. Naskah pengguna dipakai apa adanya. Yang boleh dirapikan tanpa bertanya, asal ditunjukkan: angka ditulis dengan huruf ("lima puluh ton", "one in five"), singkatan ditulis seperti dibaca, dan tanda baca untuk jeda. Alasannya teknis: satu kelompok angka dibaca sebagai beberapa kata, sehingga caption dan waktu per kata tidak bisa dicocokkan.
2. Pecah menjadi `script.txt`, satu baris per kalimat-gambar: `S01|teks`. Satu baris = satu perubahan di layar; kalimat panjang dipecah di koma.
3. Hitung durasi sebelum suara dibuat: Indonesia ≈ suku kata ÷ 6,3 detik, Inggris ≈ kata ÷ 2,7 detik, ditambah ±2 detik. Format ini paling nyaman di 60–75 detik. Kalau naskah jauh lebih panjang, katakan durasi dan biayanya dan usulkan baris yang bisa dipotong, tetapi jangan memotong naskah pengguna tanpa izin.
4. Cek fakta dengan pencarian web: angka dan klaim sebab-akibat. Laporkan yang meragukan beserta sumbernya dan usulkan kalimat pengganti. Isi naskah tidak diubah diam-diam.
5. Buat rancangan gambar: tabel baris → apa yang terlihat dan bergerak → tag atau angka di layar. Satu set (lokasi) untuk seluruh video, dengan bidang potong menghadap kamera. Angka yang tampil di layar hanya yang ada di tabel cek fakta; kalau angkanya tidak ada, pakai label tanpa angka.

### 1B. Dari video referensi

1. Jalankan skill `reference-short-teardown`. Hasilnya: angka gaya (tempo, gaya caption, potongan atau gerak kamera), fungsi tiap beat, dan daftar "diambil / tidak diambil".
2. Riset topiknya dari sumber primer atau lembaga, lalu susun tabel klaim → sumber → penyederhanaan. Untuk topik tanpa sumber lembaga (misalnya modifikasi mesin), pakai media teknik dan pembuatnya, dan cocokkan tiap angka di lebih dari satu sumber. Angka di video referensi hanya petunjuk: yang tidak cocok dengan hasil cek diganti, dan perbedaannya dicatat di plan.
3. Tulis naskah baru dalam bahasa tujuan. Yang diikuti dari referensi hanya tata bahasa formatnya: topik, panjang, tempo, dan fungsi beat (hook, rantai masalah-solusi, fakta kejutan, penutup yang mengulang hook). Kalimat, perumpamaan, urutan detail, set, dan karakter dibuat sendiri; contoh dan satuan dilokalkan untuk penonton bahasa tujuan. Ini bukan terjemahan atau sulih suara video orang lain, dan footage, audio, serta karakternya tidak dipakai. Kalau pengguna memberi kalimat hook, pakai kalimat itu.
4. Anggaran panjang: durasi referensi × 6,3 suku kata (Indonesia) atau × 2,7 kata (Inggris). Isi yang sama butuh lebih banyak suku kata dalam bahasa Indonesia, jadi tandai baris yang boleh dipotong.
5. Lanjut ke 1A langkah 2. `CAPTION_STYLE` dan gaya kamera mengikuti hasil bedah.

Kalau referensinya video milik pengguna sendiri dan ia meminta terjemahan setia, naskahnya boleh diterjemahkan; tanyakan dulu.

## 2. Gerbang sebelum kredit dipakai

Kirim satu pesan berisi: naskah final per baris, rancangan gambar singkat, suara yang diusulkan, estimasi durasi, estimasi kredit suara dan GPU, dan batas kredit yang diminta. Lanjut hanya setelah pengguna menyetujui batasnya secara eksplisit. Kalau pengguna sudah berkata "langsung eksekusi" dan batasnya sudah ia sebut atau setujui, jalan terus dan tulis asumsi yang diambil di baris pertama laporan.

- Harga berubah; cek dulu dengan alat gratis `estimate_audio_cost` dan `gpu_list_gpus`. Angka di bawah terukur pada November 2026.
- Suara: ±0,47 kredit per 100 karakter per take. Siapkan dua take, plus ±5 kredit bila ada audisi.
- GPU (L40S, 71 kredit per jam): menit box ≈ jumlah frame ÷ 0,74 ÷ 60 + 15; untuk scene dengan gerak yang dipanggang per frame atau banyak objek berkurva, bagi dengan 0,6. Minta batas ±1,6 × estimasi: dari tiga video, dua butuh render ulang sebagian.
- Kredit tidak pernah dipakai di luar batas. Kalau proyeksi melewati batas, berhenti dan tanya.

## 3. Suara dan waktu per kata (sandbox Higgsfield, gratis)

Workspace cloud Claude tidak bisa menjangkau CDN Higgsfield, jadi audio diolah di sandbox (`sandbox_exec`), di folder `/home/user/jobs/<nama>/`. Siapkan folder itu di sandbox:

```bash
cd /home/user && { [ -d 3dv-repo ] || git clone --depth 1 https://github.com/davidalfasunarna/3d-engineering-video-claude-skills 3dv-repo; }
mkdir -p jobs/<nama> && cp 3dv-repo/kit/audio/*.py jobs/<nama>/
```

Lalu kirim `script.txt` dengan heredoc dan cocokkan md5-nya. Kalau clone gagal, kirim juga `audio/*.py` dengan heredoc.

1. Suara bawaan dan tag tempo per bahasa ada di `GUIDE.md` bagian 3. Kalau pengguna ingin memilih suara, lakukan audisi seperti di sana dan biarkan ia memilih dengan telinga.
2. `generate_audio` model `elevenlabs_v4`, satu giliran, `voice_type: preset`. Teksnya isi `script.txt` tanpa ID baris dan tanpa tanda ` / `.
3. `python3 vo_prep.py <target_detik> vo_raw.mp3` → `vo_proc.wav`. Kalau hasilnya masih lebih dari 5 detik di atas target, pilih bersama pengguna: terima lebih panjang, take baru, atau potong baris. Jangan membuat lebih dari dua take tanpa bertanya.
4. `python3 asr.py vo_proc.wav asr_proc.json <id|en> && python3 align.py <id|en>` → `words.json`. Periksa keluarannya: jumlah kata sama dengan naskah, baris "words that span a pause" kosong, dan daftar `diff` hanya berisi selisih ejaan. Kata yang terdengar berbeda dicatat untuk laporan akhir. Angka dan singkatan yang dieja (misalnya "CR-V") mendapat waktu lewat interpolasi dan bisa meleset: periksa dan betulkan seperti di `GUIDE.md` bagian 3 sebelum scene ditulis.
5. Bawa `words.json` ke folder job di workspace (cetak, tulis ulang, cocokkan md5). Setelah scene mulai dibuat, jangan jalankan ASR lagi: hasilnya bisa bergeser ±0,2 detik antar-jalan.

## 4. Scene dan preview (workspace, gratis)

1. Mulai dari `scene_template.py`, yang sudah disalin sebagai `$SCENE`. Aturan menulis scene, kosakata fungsi, dan aturan keyframe ada di `GUIDE.md` bagian 1; baca sebelum menulis.
2. Tulis `keywords.txt` (gaya `cards`): 1–2 kata kunci per kalimat, format `S01 kata [ke]`.
3. Preview berlapis seperti di `GUIDE.md` bagian 2 sampai contact sheet bersih. Lihat sendiri gambarnya; jangan menilai dari log. Tambahkan strip gerak (5–7 frame berurutan) di sekitar tiap pertukaran komponen dan tiap benda yang masuk atau keluar.
4. Jalankan `python3 scene_check.py <scene>.py` setiap kali skrip scene berubah. Ia mencetak, tanpa render, apa yang tidak terlihat di still: lompatan kamera, benda di layar yang kembali atau tidak pernah hilang, dan kilat yang hanya hidup 1–2 frame beserta detik puncaknya. Ambil still ukuran penuh tepat di tiap detik puncak itu. Untuk gerak yang punya syarat fisik (klep tidak boleh menembus piston, mesin tidak boleh mundur), tulis pemeriksa kecil di folder job. Memperbaiki kesalahan seperti ini setelah render berarti membayar render ulang.
5. Kirim contact sheet ber-caption sebelum menyewa GPU bila pengguna meminta gerbang review, atau bila tampilan adalah risiko terbesar video itu (model baru, gaya baru).

## 5. Render sampai file jadi

Jalankan skill `higgsfield-blender-render`. Ia mengurus kiriman berkas ke box, render tiga proses, scan semua frame, caption dan encode, cek warna dan kenyaringan, unggah, dan mematikan box.

## 6. Laporan dan arsip

Laporan ke pengguna, kesimpulan dulu:

- Link video final dan master bersih; durasi; suara yang dipakai.
- Kredit terpakai per pos terhadap batas, dan sebabnya bila melewati estimasi; kredit untuk perbaikan setelah render disebut terpisah.
- Yang sudah dicek: scan frame, warna, format, kenyaringan, md5, sinkron.
- Yang tidak bisa dicek Claude: audio belum didengar dan gerak belum ditonton. Sebutkan kata yang terdengar berbeda bagi mesin transkripsi beserta detiknya, supaya pengguna tahu di mana harus mendengarkan.
- Yang tidak dibuat: musik dan efek suara. Master bersih ada untuk itu.

Arsip, di tempat yang dipakai pengguna (Project claude.ai, folder lokal, atau repo miliknya):

- Catatan produksi `videoNN-production-record.md`: hasil, angka terukur, penyimpangan dari rencana, pelajaran. Contoh: `docs/video03-production-record.md` di repo.
- Folder `videoNN/`: `job.env`, `script.txt`, `keywords.txt`, `words.json`, skrip scene, `.blend` (mode `blend`), contact sheet preview, `README.md`.
- Catatan kerja pengguna diperbarui: keadaan, biaya, keputusan.
- Pelajaran baru yang berlaku umum diusulkan masuk ke `GUIDE.md`; perubahan kode kit dirilis menurut `kit/README.md`.
