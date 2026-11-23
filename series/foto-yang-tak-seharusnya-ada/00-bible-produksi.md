# FOTO YANG TAK SEHARUSNYA ADA — Bible Produksi

Dokumen ini berisi semua yang **dipakai bersama oleh 10 episode**: timeline kanon, kunci karakter, kunci lokasi, style, negative prompt, suara, dan musik. File `ep01.md` sampai `ep10.md` memakai token di bawah ini, misalnya `[ADRIAN]`, `[RAKA]`, `[RUANG-TAMU]`, dan `[STYLE]`. Saat menempelkan prompt ke generator gambar, ganti token dengan teks bloknya, atau pasang gambar referensinya.

---

## 1. Timeline kanon

Disusun dari angka-angka di Master Story Bible.

| Tahun | Kejadian |
|---|---|
| 1996 | Daniel (±28 th) menemukan fenomena foto misterius di rumah Jl. Kenanga No. 17. Raka (±40 th) membantunya menjaga rahasia. Foto hitam-putih Daniel muda diambil di depan rumah ini, yaitu foto yang ditemukan Adrian di Episode 1. |
| 1998 | Adrian lahir. |
| 2004 | Daniel (±36 th) meninggal pada suatu malam di depan rumah ini, saat Adrian berumur 6 tahun. Raka (±48 th) ada di sana. (Episode 9) |
| 22 Nov 2026, malam | Episode 1–2. Adrian menemukan foto, datang ke rumah, bertemu Raka. |
| 23 Nov 2026, malam | Episode 3–9. Foto kedua bertanggal hari ini, Adrian masa depan muncul, dan mereka kembali ke malam 2004. |
| 24 Nov 2026, subuh | Episode 10. Adrian keluar rumah saat pagi datang. |
| 23 Nov 2056 | Tanggal pada "foto terakhir" (Episode 7), 30 tahun yang akan datang. Adrian masa depan berangkat dari tahun ini, saat berumur 58. |

**Catatan hook Episode 1:** "foto dirinya 30 tahun sebelum dia lahir" adalah kalimat hook dari sudut pandang Adrian. Foto itu sudah ±30 tahun dan diambil sebelum ia lahir. Penonton baru tahu di Episode 2 bahwa pria di foto adalah ayahnya, tanpa pernah menyebut tahun.

---

## 2. Kunci karakter

Tempel blok ini apa adanya di prompt. Untuk konsistensi, **selalu pasang gambar referensi**. REF Adrian dan REF Raka sudah ada di flow ElevenLabs "Foto 30 Tahun — Episode 2 Produksi".

**[ADRIAN]** (28 th, semua episode)
```
Adrian, a 28-year-old Indonesian man, short neat black hair slightly messy on top, warm tan sawo matang skin, average build, natural firm face with defined jaw, light stubble, expressive dark brown eyes, plain black crew-neck t-shirt under a dark-wash denim jacket, dark trousers, black shoes
```

**[RAKA]** (70 th, 2026)
```
Raka, a thin 70-year-old Indonesian man, thin wispy white hair combed back, deeply wrinkled tan face, sunken cheeks, serious knowing eyes, faded off-white long-sleeve button shirt, black trousers, simple old sandals, an old silver wristwatch with a cracked glass face and worn brown leather strap on his left wrist
```
Jam tangan perak berkaca retak adalah **petunjuk penting di Episode 6**. Tampilkan samar mulai Episode 3, tapi jangan pernah di-close-up sebelum Episode 6.

**[ADRIAN-58]** (Adrian dari masa depan, 30 tahun lagi)
```
the same man as Adrian but 58 years old: identical face structure and eyes, short black hair greying at the temples, deeper lines on forehead and around the eyes, light grey stubble, slightly gaunter cheeks, a thin pale scar across the back of his left hand, wearing a worn, faded black t-shirt under a faded dark denim jacket of the same style
```
Di **Episode 3–4** ia selalu tampil **dari belakang, siluet, atau setengah wajah dalam gelap**, sehingga terlihat "sama persis" dengan Adrian. Di **Episode 5** ia masuk ke cahaya bohlam dan usianya baru terlihat. Bekas luka di tangan kiri **disembunyikan sampai Episode 5**.

**[DANIEL-1996]** (ayah Adrian, ±28 th, hanya di foto hitam-putih)
```
Daniel, a 28-year-old Indonesian man who looks almost identical to Adrian, 1990s side-parted black hair, light collared short-sleeve shirt
```

**[DANIEL-2004]** (±36 th, rekaman Episode 6 dan malam kejadian Episode 9)
```
Daniel, a 36-year-old Indonesian man with Adrian's face but slightly older, side-parted black hair, clean-shaven, tired kind eyes, plain dark-grey collared shirt with sleeves rolled up, dark trousers
```

**[RAKA-2004]** (±48 th, Episode 9, hampir selalu siluet)
```
a 48-year-old thin Indonesian man, black hair with grey streaks, white shirt, the same silver wristwatch with a cracked glass face on his left wrist
```

**[ADRIAN-KECIL]** (6 th, Episode 7, 9, dan 10)
```
a 6-year-old Indonesian boy with short black hair and warm tan skin, wearing a small navy-blue t-shirt and shorts
```

---

## 3. Kunci lokasi

**[RUMAH-LUAR]**
```
a white two-story Dutch-colonial house with peeling paint, a dark front porch with old wooden double doors, tall shuttered windows, a low iron fence and gate, a frangipani tree in the yard, on a quiet residential street (Jl. Kenanga No. 17)
```

**[RUANG-TAMU]**
```
the dusty living room of the old colonial house: peeling cream walls covered with faded black-and-white family portraits in wooden frames, an old rattan chair and dusty teak furniture, patterned old floor tiles, a dark wooden writing desk with drawers against the wall, an old paper wall calendar, a narrow dark-wood staircase on the right side rising to the second floor, lit by a single bare tungsten bulb hanging from the ceiling
```

**[LORONG-ATAS]**
```
the long upstairs hallway of the old colonial house: old wooden floorboards, peeling walls, closed wooden doors on both sides, a tall window at the far end letting in cold blue moonlight
```

**[KAMAR-ATAS]**
```
a small old upstairs bedroom: an old iron bed with a white sheet, a small wooden desk under a shuttered window, a tall wooden wardrobe, cold blue moonlight through the shutters
```

**[JALAN-2004]** (Episode 9)
```
the same street in front of the same colonial house 22 years earlier: the house freshly painted white, a sodium streetlamp casting orange light, wet asphalt after rain, an old black 1990s sedan parked at the curb
```

**Aturan cahaya:**
- **Lantai bawah:** satu bohlam kuning hangat.
- **Lantai atas dan luar rumah:** cahaya bulan biru dingin.
- **Tahun 2004:** lampu jalan oranye dan aspal basah.
- **Episode 10 bagian akhir:** cahaya subuh biru-keemasan.

---

## 4. Style dan negative prompt

**[STYLE]** (tambahkan di akhir setiap prompt gambar)
```
photorealistic cinematic film still, modern Indonesian mystery thriller, shot on ARRI Alexa, 35mm anamorphic lens, shallow depth of field, low-key dark cinematic lighting, warm tungsten vs cool blue moonlight, muted teal-and-amber grade, subtle film grain, high detail, natural skin texture and natural facial expression, vertical 9:16, no captions, no watermark
```

**NEGATIVE PROMPT (O) — dasar untuk semua episode**
```
cartoon, anime, illustration, painting, 3d render, CGI, video game, plastic skin, airbrushed face, doll face, deformed face, asymmetric eyes, extra fingers, deformed hands, extra limbs, different hairstyle, long hair, blond hair, beard, glasses, hat, different jacket colour, leather jacket, hoodie, white t-shirt on Adrian, colourful clothes, modern glass house, bright daylight, oversaturated colours, neon, fantasy glow, magic particles, portal, sci-fi effects, horror gore, blood, monster face, jump-scare face, watermark, logo, misspelled text, random text
```
Setiap episode punya tambahan negative prompt sendiri di bagian **O** file episodenya.

---

## 5. Suara (ElevenLabs, model eleven_v4)

| Peran | Suara | Catatan |
|---|---|---|
| Narator | EDOT – Indonesian Documentary Narrator (`igbPDrDECUgQHdjybk9E`) | Sama dengan Episode 1–2. |
| Adrian | Saos Cocol – Warm Cinematic Storyteller (`R86jddkroI9bJwXFfjsr`) | Sama dengan Episode 2. |
| Raka | A Serak – Deep, hoarse (`LxiqOV1uxBCgYTeitAHf`) | Sama dengan Episode 1–2. |
| Adrian masa depan | Suara Adrian yang sama dengan tag `[older, tired, low, raspy]` | Agar penonton merasa itu orang yang sama. |
| Daniel | Belum dipilih (pria Indonesia 30-an, hangat, lembut) | Pertama bicara di Episode 6. |

Tag emosi seperti `[whispering]` hanya untuk generator suara. Voice over final di setiap file episode ditulis tanpa tag.

---

## 6. Musik dan aturan editing

- **Musik dasar:** drone cello rendah, piano jarang, dan pulsa sub-bass, dengan tekstur jam berdetak di dalam rumah. Mulai Episode 8 masuk motif piano yang lebih hangat (tema Daniel), lalu tema itu memuncak di Episode 10.
- **Subtitle:** Inter ExtraBold putih dengan kata kunci kuning, maksimal sekitar 6 kata per baris. Label kecil "FOTO YANG TAK SEHARUSNYA ADA • EP X" di atas layar.
- **Akhir setiap episode:** potong ke hitam disertai bunyi "BOOM" rendah, 1–2 baris teks besar, lalu "EPISODE X BESOK."
- **Durasi:** setiap scene 4–7 detik, total 40–50 detik.
