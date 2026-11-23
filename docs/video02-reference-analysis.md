# Video 02 — bedah video contoh (kolam renang, bahasa Inggris)

22 November 2026 · contoh keluaran skill `reference-short-teardown` · alat ukurnya `kit/ref_teardown.py`

Catatan ini versi repo: nama file dan sidik file video referensi dihilangkan. Naskah video referensi tidak pernah dicatat di sini; tabel struktur hanya memuat fungsi tiap beat.

Claude tidak bisa menonton gerak atau mendengar audio. Semua isi dokumen ini berasal dari frame diam, pembacaan caption (OCR), dan pengukuran sinyal.

## 1. File yang dibedah

| Hal | Nilai |
|---|---|
| Sumber | video pendek TikTok berbahasa Inggris tentang cara kerja kolam renang, diunggah pengguna sebagai contoh format (nama akun tidak tercatat pada file yang dibedah) |
| Video | HEVC 1080×1920, 60 fps asli (tidak ada frame kembar), 3.994 frame, 66,57 detik |
| Audio | AAC 44,1 kHz, kanal kiri sama dengan kanan (mono), −15,7 LUFS, rentang 4,6 LU |

File video referensi tidak disertakan di repo.

## 2. Angka terukur

| Hal | Hasil | Cara ukur |
|---|---|---|
| Narasi | ±259 kata, 21 kalimat, dari detik 0,1 sampai ±64,1 | OCR caption di 15 fps, lalu dicocokkan ke transkrip yang dirapikan; 5 kata diisi interpolasi |
| Tempo | 4,0 kata per detik (±243 kata per menit), kira-kira 5,3–5,7 suku kata per detik | jumlah kata dibagi rentang narasi |
| Jeda | hanya 1 jeda ≥ 0,18 detik | `silencedetect` di −38 dB. Artinya jeda dirapatkan saat edit |
| Suara | nada dasar median ±165–175 Hz | autokorelasi pada frame bersuara; dua cara ukur memberi 164 dan 176 Hz |
| Musik | tidak terdeteksi music bed di bawah narasi | titik tersunyi tiap 2 detik berada di −38 s.d. −50 dB dan tidak rata |
| Bunyi penutup | setelah narasi selesai masih ada ±2,5 detik bunyi bernada di ±−33 dB | level dan kerataan spektrum di ekor file |
| Caption | satu kata per tampilan, di tengah, pusatnya di ±52% tinggi layar | potongan pita y=905–1105 px |
| Bentuk caption | huruf bulat tebal, isi putih, garis luar biru tua tebal, bayangan lembut; tinggi huruf kapital ±75 px; huruf pertama kapital | diamati di potongan 100% |
| Potongan keras | tidak ada | deteksi scene di ambang 0,30 dan 0,12, serta lonjakan beda antar-frame |
| Gerak kamera | 22 gerakan cepat, median 0,94 detik, dimulai tiap ±2,5 detik | beda piksel antar-frame di 90×160 |
| Pembagian waktu | 27% bergerak cepat, 33% drift pelan, 40% nyaris diam | sama |

## 3. Struktur

Polanya sama dengan referensi #1: giliran "tapi…" (masalah) dan "jadi…" (solusi) dengan sudut pandang orang kedua. Tiga komponen diberi nama setelah fungsinya dijelaskan. Tabel ini mencatat fungsi tiap beat, bukan kalimatnya; kolom pokok isi tiap beat tidak disertakan di versi repo.

| # | Detik | Fungsi | Kata | Kata/dtk |
|---|---|---|---|---|
| 1 | 0,1–3,6 | hook | 18 | 5,1 |
| 2 | 3,6–7,7 | masalah | 17 | 4,1 |
| 3 | 7,7–12,6 | solusi | 21 | 4,3 |
| 4 | 12,6–19,0 | masalah | 28 | 4,4 |
| 5 | 19,0–27,1 | solusi + nama | 33 | 4,1 |
| 6 | 27,1–30,4 | masalah | 12 | 3,7 |
| 7 | 30,4–37,1 | solusi + nama | 31 | 4,6 |
| 8 | 37,1–44,9 | masalah + solusi + nama | 31 | 3,9 |
| 9 | 44,9–50,9 | lanjutan | 19 | 3,2 |
| 10 | 50,9–54,5 | masalah + solusi | 17 | 4,7 |
| 11 | 54,5–59,7 | fakta | 18 | 3,4 |
| 12 | 59,7–62,0 | pelengkap | 7 | 3,1 |
| 13 | 62,0–66,6 | payoff | 7 | — |

Beat terpanjang 8 detik. Paruh pertama berganti masalah/solusi tiap 4–8 detik; tempo bicara melambat sedikit di fakta dan di akhir.

## 4. Bahasa visual

- Satu lokasi sepanjang video: halaman belakang rumah dua lantai, rumput bergaris, teras, pohon, properti kecil. Yang berubah hanya kolamnya.
- Sudut kamera tinggi 3/4. Separuh bawah layar adalah bidang potongan tanah bertekstur batuan; kolam terlihat sebagai penampang.
- Aset bertekstur semi-realistis, bukan low-poly.
- Tidak ada papan atau label di dalam dunia 3D. Informasi dibawa oleh caption, panah putih 3D, dan warna (air tanah sebagai rona biru di bidang potongan, komponen penting berwarna merah).
- Close-up penampang untuk komponen: katup di atas kerikil, tabung filter terbelah dengan lapisan pasir, kotak skimmer dengan keranjang.
- Aliran digambar dengan panah dan titik yang bergerak di dalam pipa, bukan simulasi fluida.
- Penutup: kolam jadi dengan orang berenang, payung, kursi, pelampung.

## 5. Dibanding referensi #1 dan video #1

| Hal | Referensi #1 (septic, ID) | Referensi #2 (kolam, EN) | Video #1 kita (septic, EN) |
|---|---|---|---|
| Durasi | 70,7 dtk | 66,6 dtk | 66,0 dtk |
| Frame rate | 30 | 60 | 30 |
| Narasi | 175 kata, ±149 kata/menit | ±259 kata, ±243 kata/menit | 171 kata, ±156 kata/menit |
| Potongan keras | 9 | 0 | 14 batas shot (campuran potongan dan gerak) |
| Caption | kumulatif per frasa 1–4 kata, ±65% tinggi | satu kata, ±52% tinggi | kumulatif per frasa, 67,5% tinggi |
| Tulisan di dunia 3D | ada | tidak ada | ada |
| Karakter | manekin kayu | orang di adegan akhir | maskot engineer |
| Musik | tidak terlihat | tidak terdeteksi; ada bunyi penutup | tidak ada |
| Kenyaringan | −14,2 LUFS | −15,7 LUFS | −14,3 LUFS |

Pelajaran: dua referensi memakai resep cerita yang sama tetapi kemasan berbeda. Referensi #2 hampir dua kali lebih padat kata, tanpa potongan keras, dan caption-nya satu kata. Video #1 kita lebih dekat ke referensi #1.

## 6. Kenapa formatnya bekerja

1. Hook menawarkan versi paling sederhana dari hal yang rumit, lalu langsung dibantah.
2. Setiap solusi melahirkan masalah berikutnya, jadi selalu ada alasan menonton beat selanjutnya.
3. Tidak ada udara kosong: jeda dirapatkan dan kata baru muncul di layar tiap ±0,25 detik.
4. Kamera berpindah bingkai tiap ±2,5 detik tanpa memotong, sehingga penonton tidak kehilangan orientasi.
5. Kalimat hook diulang di akhir, dan kali ini benar.

## 7. Yang diambil dan yang tidak

Diambil, karena ini tata bahasa format yang umum di genre ini:
- premis "versi paling sederhana" di hook (atas permintaan pengguna);
- giliran masalah → solusi dengan sudut pandang "kamu";
- satu kalimat = satu perubahan di layar; istilah disebut setelah fungsinya jelas;
- satu lokasi yang terus berkembang; kamera bergerak tanpa potongan keras;
- caption satu kata di tengah layar; penutup yang mengulang hook.

Tidak diambil:
- kalimat dan susunan klausa naskahnya. Naskah kita ditulis dari fakta bersumber, bukan diterjemahkan;
- urutan beat. Di naskah kita kolam terangkat dan katup hidrostatik menjadi klimaks di akhir, dan rantai "hijau → filter → kaporit" dipisah supaya lebih akurat (filter menahan kotoran, kaporit yang membunuh ganggang dan kuman);
- perumpamaan dan lelucon. Milik kita: ember, mangkuk raksasa, sup hijau, bebek karet, berat 48 ton yang "hilang" saat dikuras;
- desain set dan properti. Milik kita: rumah tropis, pagar tembok, tanaman lokal, maskot;
- bentuk panah dan overlay, font caption yang persis sama, adegan penutup (milik kita: senja dengan lampu bawah air).

## 8. Batas analisa ini

- Transkrip direkonstruksi dari caption, jadi jumlah kata bisa meleset beberapa kata.
- Jenis kelamin atau karakter suara tidak bisa dipastikan dari nada dasar saja.
- "Tidak terdeteksi music bed" berarti tidak ada bunyi tetap di atas ±−45 dB di sela kata; musik yang sangat pelan bisa lolos dari ukuran ini.
- Kualitas gerak (halus atau tidak) tidak bisa dinilai dari frame diam.
