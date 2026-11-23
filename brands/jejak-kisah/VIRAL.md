# Playbook viral Jejak Kisah

Tujuan: setiap video ditonton sampai habis, dikomentari, dibagikan, dan membuat penonton **follow**.
Algoritma TikTok, Reels dan Shorts menilai hal yang sama: berapa lama orang menonton, apakah mereka menonton ulang,
berkomentar, membagikan, dan mengikuti akun setelah menonton. Semua aturan di bawah ini mengejar sinyal-sinyal itu.
Setiap naskah di `stories/` wajib lolos checklist di bagian paling bawah.

## 1. Pilih topik yang "layak diceritakan ulang"

Video yang viral adalah video yang membuat penonton ingin berkata "eh, kamu tahu nggak…" kepada temannya. Topik yang bagus
punya paling tidak dua dari empat ciri ini:

- **Kontras yang tidak masuk akal.** Contoh: kapal utuh tapi awaknya lenyap; terkenal justru karena dicuri.
- **Kaitan ke Indonesia.** Contoh: Tambora, Krakatau, Borobudur. Penonton Indonesia paling sering membagikan topik yang
  terasa "punya kita".
- **Angka yang mengejutkan.** Contoh: 4.800 km, 29 tahun, salju di bulan Juni.
- **Misteri dengan jawaban.** Penonton suka dibuat penasaran, lalu dipuaskan. Jangan biarkan mereka menggantung tanpa
  jawaban sama sekali.

Variasikan isi antrean dengan pola sekitar 40% sejarah Indonesia, 40% misteri dunia, dan 20% fakta unik atau asal-usul.

## 2. Tiga detik pertama: hook

- **Layar pertama sudah berisi teks besar.** Tidak boleh ada intro, logo, atau "Halo semuanya". Hook di layar
  (`hook` + `hook_accent`) panjangnya maksimal 6 kata.
- **Narasi adegan 1 maksimal 2 kalimat**, dan sudah memuat inti keanehannya.
- Pakai pola berikut, dan jangan memakai pola yang sama dua video berturut-turut:
  1. **Kontras:** "Kapalnya utuh. Awaknya lenyap."
  2. **Akibat dulu, sebab belakangan:** "Salju turun di bulan Juni. Penyebabnya… satu gunung di Indonesia."
  3. **Angka ekstrem:** "Suara ini terdengar sampai 4.800 kilometer jauhnya."
  4. **Pembalikan:** "Lukisan paling terkenal di dunia… dulu tidak seterkenal itu."
  5. **"Kamu":** "Kalau kamu di posisinya, kamu akan menyerah?"
- Tulis cover video dari frame hook, yaitu `videoCoverMilliseconds` 1200. Cover itu juga tampil di grid profil, jadi
  profil kita penuh dengan kalimat hook yang memancing klik.

## 3. Menjaga penonton sampai habis (retensi)

- **Satu adegan = satu informasi baru.** Paling lama 9 detik per adegan, dan setiap 3–5 detik gambarnya berganti.
- **Re-hook di tengah video.** Sekitar adegan 7–8, pasang kalimat yang membuka rasa penasaran baru, misalnya
  "Tapi dampaknya belum selesai.", "Dua tahun berlalu. Lalu pencurinya muncul sendiri.", atau "Dan pulau itu sendiri?".
  Di titik inilah penonton biasanya mulai menggeser layar.
- **Tahan jawaban.** Jawaban misteri baru muncul di 30% bagian akhir video.
- **Kata kunci berwarna.** Tandai 1–2 kata penting per adegan dengan `*bintang*`. Kata itu tampil emas di subtitle, sebab
  banyak orang menonton tanpa suara.
- **Durasi 61–80 detik** (140–170 kata). Lebih dari 60 detik diperlukan untuk TikTok Creator Rewards, tetapi makin pendek
  makin besar peluang ditonton sampai habis.

## 4. Akhir video yang menghasilkan komentar dan follow

- **Pertanyaan pilihan, bukan pertanyaan terbuka.** Contoh: "Setia atau keras kepala?", "Hukuman berat atau ringan?",
  "Percaya atau masih ragu?". Menjawab dengan satu kata itu gampang, jadi orang lebih mau berkomentar. Jawaban yang
  saling berlawanan juga memancing orang berdebat di kolom komentar.
- **Teaser berikutnya yang spesifik, lalu ajakan follow.** Contoh: "Berikutnya: prajurit yang terus berperang 29 tahun
  setelah perang usai. Follow, supaya tidak ketinggalan." Orang follow karena ingin tahu kelanjutannya, bukan karena
  diminta.
- **Komentar pertama** (`firstCommentText`) mengulang jadwal: 12.00 & 19.00 WIB.
- **Balas 10 komentar pertama** dalam satu jam pertama. Setiap balasan dihitung sebagai interaksi baru. Ini satu-satunya
  langkah yang harus dilakukan manual oleh pemilik akun.

## 5. Seri dan identitas

- **Dua format tetap:**
  - **12.00, "Fakta Sejarah":** topik yang lebih ringan dan mudah dibagikan, misalnya Indonesia atau asal-usul sesuatu.
  - **19.00, "Misteri Malam":** topik yang lebih gelap, dengan latar `night`, `fog` atau `storm`. Ini jam tayang utama.
- **Semua video punya rantai teaser**, sehingga penonton yang menonton satu video terdorong menonton video berikutnya.
- **Ciri khas yang konsisten:** watermark emas, musik ambient yang sama, suara narator yang sama, dan kalimat seri
  "🕯️ Jejak Kisah: kisah nyata yang jarang diceritakan." Penonton mengenali akun ini dalam 1 detik.
- **Topik besar boleh dibuat 2 bagian** (Part 1 dan Part 2), misalnya Roanoke atau Ekspedisi Franklin. Part 1 diakhiri
  cliffhanger, lalu Part 2 diposting di slot berikutnya. Format ini paling efektif menambah follower. Pakai paling banyak
  satu kali seminggu, karena kalau terlalu sering penonton merasa dipancing.

## 6. Yang TIDAK boleh, karena merusak akun

- **Clickbait palsu.** Hook harus benar dan dibuktikan di dalam video. Penonton yang merasa ditipu langsung menggeser
  layar, dan itu menurunkan jangkauan.
- **Fakta yang dikarang.** Selalu cantumkan `sources`. Akun sejarah yang ketahuan salah fakta akan ramai dikoreksi dan
  kehilangan kepercayaan. Program monetisasi juga bisa menolak konten yang menyesatkan.
- **Konten sadis tentang korban.** Tragedi diceritakan dengan hormat, tanpa detail luka.
- **Isi yang sama berulang-ulang.** Setiap video harus punya naskah, visual dan pertanyaan yang berbeda, supaya tidak
  dinilai "konten berulang" oleh YouTube dan TikTok.

## Checklist sebelum render

- [ ] Hook di layar ≤ 6 kata, dan narasi adegan 1 ≤ 2 kalimat
- [ ] Pola hook berbeda dari video sebelumnya
- [ ] Ada re-hook di adegan 7–8
- [ ] Setiap adegan ≤ 9 detik, dan ada 1–2 `*kata kunci*`
- [ ] 2–3 adegan pemahaman (FAKTANYA / MITOSNYA / TEORI TERKUAT / KONTEKSNYA / PELAJARANNYA)
- [ ] Penutup: pertanyaan pilihan, teaser spesifik, dan ajakan follow
- [ ] Caption: baris pertama adalah hook, ditambah 6–9 hashtag termasuk #JejakKisah #KisahNyata #MisteriSejarah
- [ ] `sources` terisi, dan setiap angka sudah dicek
