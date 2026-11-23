# Seri POV: KELUAR DARI MESIR — "Kamu yang Pilih"

Kisah bersambung interaktif. Penonton **menjadi** seorang budak Ibrani berusia 16 tahun.
Setiap Part berakhir dengan pilihan **A atau B**, dan **pilihan terbanyak di komentar** menentukan Part berikutnya.

## Kenapa format ini berpotensi viral

| Pemicu | Cara dipakai di seri ini |
|---|---|
| **POV / orang kedua** | Penonton tidak menonton Musa, tapi *menjadi* salah satu budak. Semua narasi pakai "kamu". |
| **Komentar = algoritma** | CTA "ketik A atau B" adalah komentar yang paling gampang dibuat. Komentar dan balasan mendorong distribusi di keempat platform. |
| **Cliffhanger** | Setiap Part berhenti tepat di titik keputusan, jadi penonton punya alasan untuk follow. |
| **Rasa memiliki** | Part berikutnya dibuka dengan "Kalian memilih A…", jadi penonton melihat suaranya dipakai dan cenderung ikut lagi. |
| **Perdebatan** | Kedua pilihan masuk akal secara manusiawi, jadi penonton saling membalas di komentar. |
| **Twist besar di akhir** | Umur 16 tahun di Part 1 ternyata jadi kunci di Part terakhir (Bilangan 14:29–31). |

## Aturan setia Alkitab

- Tokoh **"kamu" adalah rekaan**. Semua peristiwa, urutan, dan kutipan ayat mengikuti Alkitab (gaya TB). Caption selalu memuat keterangan: *"Kisah POV: tokoh 'kamu' adalah rekaan. Peristiwa dan kutipan ayat mengikuti Keluaran …"*
- **Pilihan hanya mengubah pengalaman tokoh "kamu"**, tidak pernah mengubah peristiwa Alkitab. Tulah tetap datang, laut tetap terbelah, Israel tetap 40 tahun di padang gurun.
- Konsekuensi setiap cabang **diambil dari ayat** (misalnya manna yang disimpan menjadi berulat, Keluaran 16:20). Tidak ada konsekuensi karangan.
- Cabang "salah" tidak pernah berakhir dengan "kamu dihukum lalu tamat". Cabang itu selalu berujung pada **anugerah dan kesempatan berbalik**. Inilah pesan rohani seri ini.

## Mekanisme voting

1. **Komentar pertama (pinned)**: teks `first_comment` di JSON setiap Part. Pasang sebagai `firstCommentText` di Metricool, lalu sematkan manual di IG/TikTok/FB/YT bila bisa.
2. **Batas waktu:** voting ditutup **24 jam** setelah video tayang.
3. **Cara hitung:** gabungkan keempat platform. Satu akun = satu suara (suara terakhir yang dihitung). Hanya komentar yang berisi huruf A atau B yang berdiri sendiri. Pakai `python3 engine/tally_votes.py <file-komentar>...` (format file ada di skrip).
4. **Seri (sama banyak):** menang pilihan yang komentarnya mendapat *like* terbanyak. Jika masih sama, ambil pilihan yang lebih dekat dengan jalan cerita Alkitab.
5. **Buka Part berikutnya dengan hasilnya**, misalnya *"68% dari kalian memilih A."* Angka nyata membangun kepercayaan, jadi jangan dikarang.
6. **Jadwal yang disarankan:** satu Part setiap 2 hari pada slot 19.00 WIB. Hari voting → hari produksi → tayang. Jangan dua reel di hari yang sama (aturan PIPELINE.md). Selang-seling dengan reel harian biasa.
7. Balas 10–20 komentar pertama dengan pertanyaan balik ("Kenapa pilih B? 👀"). Balasan dihitung sebagai interaksi.

## Format produksi

Setiap Part memakai format JSON yang sama dengan reel harian (`stories/pov-keluar-dari-mesir-0N.json`), sehingga langkah narasi, render, dan Metricool di `PIPELINE.md` berlaku apa adanya. Perbedaannya:

- **Adegan 1 (hook):** *recap* hasil voting dalam satu kalimat dan cliffhanger. Contoh: hook `"Kalian memilih B."` + hook_accent `"Dan itu ada harganya."`
- **Adegan 2:** kartu judul `KELUAR DARI` / `MESIR` / `Kamu yang pilih · Part N`.
- **Satu adegan `KONTEKSNYA` atau `MAKNANYA`** tetap wajib, supaya ada nilai edukasi (penting untuk monetisasi).
- **Adegan kedua dari akhir:** kartu pilihan (`label` "PILIH SEKARANG" + dua `point` "A — …" / "B — …").
- **Adegan terakhir:** "Ketik A atau B di kolom komentar. Pilihan terbanyak menentukan Part N+1. Follow…"
- Panjang tetap 12–14 adegan, 160–190 kata, 61–89 detik.
- Tambahkan `first_comment` dan blok `series` (nama, part, pilihan) di JSON.

---

## Peta cerita (Season 1)

Umur tokoh "kamu": **16 tahun** di Part 1, sekitar **18 tahun** saat pengintaian Kanaan (tahun ke-2 setelah keluar dari Mesir).

### Part 1: Batu bata tanpa jerami ✅ (naskah: `stories/pov-keluar-dari-mesir-01.json`)
Keluaran 1:11–14; 5:1–21; 6:6–9. Musa menghadap Firaun, beban budak ditambah, mandor dipukuli, rakyat menyalahkan Musa.
**Pilihan:** **A** tetap percaya janji Tuhan lewat Musa · **B** ikut marah, berhenti berharap.

### Part 2: Sembilan tulah, satu malam terakhir
Keluaran 7–12:13
- **Pembuka A:** "Kalian memilih A. Semua orang mencibirmu… tapi kamu tetap menunggu."
- **Pembuka B:** "Kalian memilih B. Kamu berhenti berharap… tapi Tuhan tidak berhenti bekerja."
- Inti cerita: Sungai Nil menjadi darah (7:20). Katak, nyamuk. **Lalat tidak ada di tanah Gosyen** (8:22). Hujan es tidak turun di Gosyen (9:26). Gelap tiga hari, *"tetapi pada semua orang Israel ada terang di tempat kediaman mereka"* (10:23).
  - Cabang A: imanmu diteguhkan. Cabang B: momen "aku salah", karena Tuhan tetap setia walau kamu meragukan-Nya.
- Malam Paskah: anak domba, darah di ambang pintu (12:7, 12:13). Hook twist: *"Malam ini, setiap anak sulung di Mesir akan mati. Dan kamu… anak sulung."*
- Ada orang Mesir yang takut akan firman TUHAN (9:20), dan nanti banyak bangsa campuran ikut keluar (12:38).
- **Pilihan:** **A** kunci pintu, lindungi keluargamu saja · **B** ajak tetanggamu orang Mesir berlindung di rumahmu.
- KONTEKSNYA: darah di ambang pintu menjadi tanda, dan Tuhan "melewati" rumah itu. Dari sinilah kata *Paskah*.

### Part 3: Terjepit di tepi laut
Keluaran 12:29–14:21
- **Pembuka A:** tengah malam, ratapan besar di seluruh Mesir (12:30). Pintumu tertutup rapat dan kamu selamat. Pagi harinya kamu melihat rumah tetanggamu…
- **Pembuka B:** tetanggamu gemetar di dalam rumahmu. Pagi harinya ia ikut berjalan bersamamu, menjadi bagian dari "banyak orang dari berbagai-bagai bangsa" (12:38).
- Inti cerita: orang Mesir memberi perak dan emas (12:35–36). Tulang-tulang Yusuf dibawa (13:19). Tiang awan dan tiang api (13:21). Firaun berubah pikiran dan mengejar dengan 600 kereta pilihan (14:7). Kalian terjepit laut. *"Apakah karena tidak ada kuburan di Mesir…?"* (14:11). Musa: *"Jangan takut, berdirilah tetap… TUHAN akan berperang untuk kamu"* (14:13–14). Angin timur bertiup semalam-malaman, dan laut terbelah (14:21).
- **Pilihan:** **A** melangkah paling depan ke dasar laut · **B** tunggu di barisan belakang, menjaga keluarga.

### Part 4: Tembok air dan roti dari langit
Keluaran 14:19–16:19
- **Pembuka A:** kamu berjalan di tanah kering, *"air itu sebagai tembok bagi mereka di sebelah kanan dan di sebelah kiri"* (14:22).
- **Pembuka B:** di barisan belakang kamu melihat tiang awan **berpindah ke belakang**, berdiri di antara kamu dan tentara Mesir (14:19–20). Kamu berada paling dekat dengan perlindungan Tuhan.
- Inti cerita: Mesir tenggelam (14:28). Miryam memukul rebana (15:20). Tiga hari tanpa air, air Mara yang pahit menjadi manis (15:23–25). Rakyat lapar dan bersungut-sungut (16:3). Manna turun (16:14–15). Perintah: *"janganlah ada yang meninggalkan dari padanya sampai pagi"* (16:19).
- **Pilihan:** **A** ambil secukupnya, percaya besok ada lagi · **B** simpan sedikit untuk jaga-jaga.
- UNTUK HIDUPMU: rasa cukup untuk hari ini (bandingkan Matius 6:11).

### Part 5: Emas di telingamu
Keluaran 16:20–32:6
- **Pembuka A:** besok paginya manna ada lagi, persis seperti dijanjikan.
- **Pembuka B:** *"Ada yang meninggalkan sebagian sampai pagi; tetapi berulat dan berbau busuk"* (16:20). Musa marah. Simpananmu busuk, tapi pagi itu manna tetap turun lagi untukmu.
- Inti cerita: Gunung Sinai bergemuruh, Sepuluh Firman (19–20). Musa naik ke gunung selama 40 hari 40 malam (24:18). Rakyat gelisah: *"buatlah untuk kami allah"* (32:1). Harun meminta anting-anting emas (32:2).
- **Pilihan:** **A** serahkan anting emasmu, ikut semua orang · **B** tolak, tetap menunggu Musa.

### Part 6: Siapa yang memihak TUHAN?
Keluaran 32:7–35; Bilangan 13–14:10
- **Pembuka A:** antingmu ikut dilebur. Kamu melihat orang menari di sekeliling anak lembu (32:19). Musa turun dan memecahkan loh batu.
- **Pembuka B:** kamu berdiri sendirian sementara semua orang bersorak (32:17–18).
- Inti cerita: Musa berseru: *"Siapa yang memihak kepada TUHAN datanglah kepadaku!"* (32:26).
  - Cabang A: inilah kesempatan berbalik, dan kamu berlari ke sisi Musa.
  - Cabang B: kamu termasuk yang pertama datang.
  - Kira-kira 3.000 orang tewas hari itu (32:28). Sampaikan dengan sopan, tanpa visual kekerasan. Musa berdoa syafaat bagi bangsa itu (32:31–32).
- Lompat waktu ke Kadesh. Dua belas pengintai kembali (Bil 13). Sepuluh orang: *"kami seperti belalang"* (13:33). Yosua dan Kaleb: *"Jika TUHAN berkenan kepada kita, maka Ia akan membawa kita masuk"* (14:8). Rakyat hendak melempari mereka dengan batu (14:10).
- **Pilihan:** **A** berdiri di samping Yosua dan Kaleb · **B** ikut sepuluh pengintai, kembali saja ke Mesir.

### Part 7 (FINALE): Empat puluh tahun
Bilangan 14:26–35; Yosua 3
- **Pembuka A:** kamu berdiri bersama minoritas, dan batu-batu sudah di tangan orang banyak…
- **Pembuka B:** kamu ikut menangis semalam-malaman bersama bangsa itu (14:1).
- Inti cerita: keputusan Tuhan, 40 tahun di padang gurun. Semua yang berumur **20 tahun ke atas** akan mati di padang gurun, kecuali Kaleb dan Yosua (14:29–30). *"Anak-anakmu… merekalah yang akan Kubawa masuk"* (14:31).
- **TWIST:** "Ingat umurmu? Delapan belas tahun."
- Lompat waktu: 40 tahun kemudian, umurmu 58. Kamu berdiri di tepi sungai Yordan. Para imam mengangkat tabut, dan air berhenti mengalir (Yosua 3:15–16).
  - Ending A: kesetiaan di tengah tekanan.
  - Ending B: kamu masuk bukan karena kamu benar, tetapi karena anugerah.
- Tidak ada voting di akhir. Gantinya: **teaser Season 2: Tembok Yerikho**, dan "Komen kalau mau Season 2."

---

## Ide season berikutnya (format sama)
- **POV: Kamu prajurit di barisan Saul** (Daud vs Goliat → Daud dikejar Saul). Pilihan: ikut berburu Daud, atau memperingatkannya?
- **POV: Kamu murid ke-13** (pelayanan Yesus → Getsemani → kebangkitan). Pilihan: lari bersama murid lain, atau mengikuti Petrus ke halaman Imam Besar?
- **POV: Kamu warga Niniwe** (Yunus). Pilihan: menertawakan nabi asing itu, atau berpuasa?
