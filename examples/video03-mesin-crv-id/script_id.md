# Video 03 — naskah final, gambar per baris, dan cek fakta

Naskah 22 baris, 199 kata, ±459 suku kata, bahasa Indonesia. Baris yang sama dalam format kit, dengan tanda ` / ` untuk jeda frasa caption, ada di `script.txt`.
Waktu di bawah adalah waktu video (waktu kata di `words.json` + 0,30 detik). Video berakhir di 75,90 detik.
Kolom "Gambar" adalah rancangan yang ditulis sebelum scene, disesuaikan dengan penyimpangan yang tercatat di catatan produksi; rincian persisnya ada di `engine_video.py`.

| ID | Peran | Mulai–selesai (dtk) | Narasi | Gambar |
|---|---|---|---|---|
| S01 | hook | 0.30–4.89 | Mesin Honda CR-V dua koma empat liter aslinya cuma seratus enam puluh tenaga kuda. | mesin utuh di dudukan; penghitung "160 HP" |
| S02 | hook | 5.06–7.92 | Di tangan tuner, mesin seri yang sama bisa tembus seribu. | penghitung melompat ke "1.000+" |
| S03 | janji | 8.09–11.22 | Caranya: pasang turbo raksasa, lalu kalahkan tiga musuh. | turbo turun dan terpasang; tiga kata muncul: TEKANAN, PUTARAN, PANAS |
| S04 | bab 1 | 11.41–12.74 | Musuh pertama, tekanan. | judul bab; kamera masuk ke bidang potong blok |
| S05 | masalah | 12.86–17.10 | Turbo memompa udara sampai dua bar lebih, dan ledakan di silinder makin keras. | jarum boost naik ke 2,2 bar; piston bergerak, nyala pembakaran membesar |
| S06 | masalah | 17.24–19.82 | Piston cor bawaan bisa retak, setangnya bisa bengkok. | satu piston retak, satu setang melengkung; tag merah |
| S07 | solusi | 19.98–21.74 | Jadi keduanya diganti versi tempa. | piston dan setang berwarna gelap menggantikan; tag "TEMPA" |
| S08 | masalah + solusi | 21.88–25.09 | Kepala silinder ikut terangkat, maka bautnya diganti stud baja. | kepala terangkat sedikit dan bocor di sambungan; stud masuk dan mengunci |
| S09 | masalah | 25.21–28.85 | Dinding silindernya berdiri sendiri di tengah air pendingin, tanpa penopang. | silinder dikelilingi saluran air pendingin; tag "OPEN DECK" |
| S10 | solusi | 28.97–31.05 | Solusinya, tanam selongsong besi tebal. | selongsong turun ke tiap silinder; celah tertutup |
| S11 | bab 2 | 31.23–32.55 | Musuh kedua, putaran. | judul bab; takometer |
| S12 | masalah | 32.70–37.07 | Kepala silinder CR-V dirancang irit, napasnya habis di enam ribu lima ratus rpm. | takometer tertahan di 6.500 |
| S13 | solusi | 37.23–41.41 | Tuner menukarnya dengan kepala Civic Type R, yang VTEC-nya ada di kedua noken as. | kepala lama (potongan kuning pucat) diangkat, kepala Type R (potongan merah) dipasang; dua noken as |
| S14 | penamaan | 41.54–44.43 | Blok besar, kepala galak: julukannya Frankenstein. | blok dan kepala menyatu; tag "FRANKENSTEIN" |
| S15 | masalah | 44.58–48.88 | Di atas sembilan ribu rpm, per klep kewalahan, dan klep bisa dihantam piston. | takometer lewat 9.000; gerak melambat; satu klep buang tertinggal dan dihantam piston tepat pada kata "dihantam" |
| S16 | solusi | 49.02–53.19 | Jadi per diganti yang lebih keras, dan klep buang memakai Inconel tahan panas. | per ganda menggantikan; klep buang berganti warna; tag "INCONEL" |
| S17 | bab 3 | 53.35–54.78 | Musuh ketiga, panas. | judul bab |
| S18 | masalah | 54.91–59.88 | Udara mampat itu panas, sampai bensin meledak sebelum waktunya. Mekanik menyebutnya ngelitik. | jarum suhu udara ke H ("UDARA PANAS", tanpa angka); kilat ledakan dini pada kata "meledak"; tag "NGELITIK" |
| S19 | solusi | 60.05–63.57 | Maka udara didinginkan intercooler, dan bensin diganti etanol. | intercooler terpasang di jalur udara; jarum suhu ke C; tangki di troli berganti dari "BENSIN" ke "E85" |
| S20 | hasil | 63.70–67.65 | Hasilnya, lebih dari seribu tenaga kuda di hampir sepuluh ribu rpm. | mesin lengkap berputar; penghitung naik bertahap ke 1.038 HP, takometer 9.760 |
| S21 | fakta kejutan | 67.79–71.41 | Yang tersisa dari mesin aslinya? Bloknya, dan kruk as bawaan pabrik. | komponen pengganti memudar; blok dan kruk as menonjol |
| S22 | penutup | 71.55–74.10 | Mesin mobil keluarga, enam kali lipat tenaganya. | tampak utuh; "160 → 1.000+" dan "× 6" |

Teks yang dikirim ke mesin suara sama dengan kolom Narasi, disambung menjadi satu paragraf, dengan awalan tag `[quick, energetic pace] ` (tag itu mengatur tempo dan tidak ikut dibacakan).

## Angka di layar

Semuanya dari tabel cek fakta: `160`, `2,2 bar`, `6.500`, `9.000+`, `1.038`, `9.760`, `× 6`. Suhu udara masuk tidak ada di tabel, jadi jarum suhu hanya bertanda C dan H.

## Cek fakta

Sumber topik ini adalah media teknik otomotif, bengkel pembuat mesin, dan forum, bukan lembaga. Angka pabrik dicocokkan di lebih dari satu sumber. Sumber dikumpulkan pada 23 November 2026; cek ulang sebelum mengutipnya.

| Klaim di naskah | Yang ditemukan | Sumber |
|---|---|---|
| CR-V 2,4 liter: 160 tenaga kuda | K24A1 (CR-V 2002–2006): 2.354 cc, bore 87 mm, stroke 99 mm, 160 hp pada 6.000 rpm, redline 6.500 rpm | [1][2][3] |
| "napasnya habis di 6.500 rpm", kepala irit | kepala K24 ekonomi: VTEC hanya di sisi masuk, 12 klep bekerja di bawah 2.200 rpm; redline 6.500 | [1][4][6] |
| kepala Type R: VTEC di kedua noken as | kepala K20 performa punya VTEC di sisi masuk dan buang serta per klep ganda untuk 8.600 rpm | [5][6] |
| julukan "Frankenstein" | blok K24 + kepala K20 lazim disebut "Frankenstein" atau "K20/K24 Frankenstein" | [7] |
| piston cor retak, setang bengkok | setang standar seri K disebut bengkok di sekitar 300 hp; piston cor rusak di ring land saat detonasi; 400 hp masih lazim dengan komponen standar | [8][9][20] |
| stud baja menjepit kepala | stud ARP L-19 dipakai supaya gaya jepit kepala cukup di atas 30 psi | [10] |
| dinding silinder tanpa penopang; selongsong besi | blok open deck tidak menopang silinder dengan baik pada tenaga tinggi; selongsong besi ulet dipasang setelah blok dibubut | [10][11][12][18] |
| klep melayang di putaran tinggi | *valve float*: klep tidak lagi mengikuti nok; risikonya klep menyentuh piston; per lebih keras mencegahnya | [13] |
| klep buang Inconel | paduan nikel tinggi (Inconel) dipakai untuk klep buang mesin turbo karena panas | [14][15] |
| udara mampat panas → ngelitik; intercooler | turbo menaikkan suhu udara masuk, yang bisa memicu detonasi; intercooler mendinginkannya | [16][17] |
| etanol | mesin contoh memakai bahan bakar E85 dan intercooler udara-ke-udara | [10][18] |
| lebih dari 1.000 hp di hampir 10.000 rpm; 2 bar lebih | 4 Piston Racing K24: 1.038 hp pada 9.760 rpm dengan boost sedikit di atas 30 psi (±2,1–2,3 bar), turbo 72 mm | [10][18][19] |
| kruk as bawaan pabrik | kruk as OEM K24 99 mm tetap dipakai; hampir semua komponen lain diganti | [10] |
| enam kali lipat | 1.038 ÷ 160 = 6,5 | hitungan |

**Fakta di video referensi diperlakukan sebagai petunjuk, bukan sumber.** Tiga hal di naskah ini berbeda dari video referensinya karena hasil cek:

- Tenaga standar: naskah memakai 160 hp, angka K24A1 CR-V generasi kedua, yang satu keluarga dengan blok yang dipakai para pembuat mesin.
- Mesin 1.038 hp yang terdokumentasi memakai blok dan kepala K24 dari Acura TSX, bukan dari CR-V. Karena itu naskah berkata "mesin seri yang sama", bukan "mesin CR-V itu sendiri".
- Bahan bakar: mesin yang terdokumentasi memakai etanol (E85), jadi naskah menyebut etanol.

## Penyederhanaan yang disengaja

- Kepala silinder pada mesin contoh adalah kepala K24 TSX (VTEC di dua noken as, sejenis kepala K20 performa). Naskah menyebut kepala Civic Type R karena itulah resep "Frankenstein" yang umum.
- "Dua bar lebih" adalah tekanan boost, bukan tekanan di dalam silinder.
- Angka batas (300 hp, 9.000 rpm) adalah kisaran dari pengalaman bengkel, bukan batas pasti.
- Angka 160 hp adalah spesifikasi pasar AS dan Jepang; varian Indonesia belum dicek.
- Mesin digambar ±7,5 kali ukuran asli dan bergaya diagram; putaran di layar paling cepat 3,3 putaran per detik supaya geraknya terbaca.

## Sumber

1. Honda-Tech, daftar spesifikasi seri K: https://honda-tech.com/forums/sitemap/t-2426669.html
2. Autofiles, K24A1: https://autofiles.com/engine-type/honda/k-series/k24a1/
3. ThinkTuning, Honda K24: https://thinktuning.com/honda-k24-engine/
4. Hybrid Racing, K20/K24 Hybrid Engine Build Guide: https://www.hybrid-racing.com/blogs/hybrid-racing/k20-k24-hybrid-engine-build-guide
5. Honda-Tech, "Hybrid How-To No. 15" (kutipan artikel): https://honda-tech.com/zerothread?id=1512836
6. Fast Car, K24 Civic: https://www.fastcar.co.uk/cars/k24-civic-civic-disobediance/
7. Drifted, Ultimate Honda K24 Guide: https://www.drifted.com/honda-k24/
8. Three Piece, forged pistons for K-series turbo builds: https://www.threepiece.us/blog/are-forged-pistons-worth-it-for-k-series-turbo-builds-street-reality-check
9. 8020 Automotive, Honda K24 turbo upgrade guide: https://8020automotive.com/honda-k24-turbo-upgrade-guide/
10. EngineLabs, "A Look At What Goes Into A 1,000 Horsepower 2.4-Liter Honda Engine": https://www.enginelabs.com/?p=247727 dan https://www.enginelabs.com/?p=6646
11. EngineLabs, Darton MID sleeves: https://www.enginelabs.com/?p=6846
12. DSPORT, Engine Block Tech 101: https://dsportmag.com/the-tech/engine-block-tech-101-go-bigger-or-go-stronger-the-right-way/
13. Wikipedia, Valve float: https://en.wikipedia.org/wiki/Valve_float
14. DSPORT, Valvetrain 201: https://dsportmag.com/?p=9690
15. Performance Racing Industry, "Rock Steady": https://performanceracing.com/magazine/featured/04-01-2023/rock-steady
16. Paten AS (latar belakang intercooler dan detonasi): https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/9987903
17. HP Academy, forum suhu udara masuk dan knock: https://www.hpacademy.com/forum/efi-tuning/show/intakteair-temperatur-and-knock/
18. Engine Swap Depot, 4 Piston Racing K24: https://engineswapdepot.com/?p=79962
19. BangShift, 1.000 hp K24: https://bangshift.com/bangshift1320/watch-4-piston-racing-build-a-1000hp-honda-k24/
20. Three Piece, K24 high-compression turbo builds: https://www.threepiece.us/blog/k24-high-compression-turbo-builds-why-they-grenade-and-fixes-that-work/
