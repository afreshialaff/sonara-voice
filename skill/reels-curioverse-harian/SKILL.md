---
name: "reels-curioverse-harian"
description: "Dipakai saat menyusun Reels Instagram Curioverse setiap hari: hook 3 detik, konteks terbaca tanpa caption, voice over dan subtitle dari Sonara VO, variasi format, dan gambar berkredit dari website."
---

# Reels Curioverse harian

Dipakai Layar (dan Lup sosial saat mengecek Reels) untuk setiap Reels. Standar bahasa tetap di `bahasa.md`, standar struktur dan visual di `social-copy.md`. Aturan di skill ini dan di `RULES.md` selalu menang atas saran dari plugin mana pun.

## 1. Tiga detik pertama
- Frame pertama sudah menampilkan subjek: gambar artikel atau ilustrasi, bukan latar kosong.
- Hook memuat topik dan satu pertanyaan atau klaim yang bisa dicek. Contoh: "Kenapa target 10.000 langkah?". Bukan "Ini yang nggak mereka kasih tau".
- Judul tidak diputar pelan dari kosong. Teks sudah utuh pada frame pertama.
- Setelah hook, adegan kedua menjawab pertanyaan hook, bukan mengulang judul.
- Kandidat hook boleh dibuat dengan `hook-writer` (Social Media Skills). Pilih yang memuat topik dan klaim yang bisa diperiksa. Tolak yang clickbait.

## 2. Struktur cerita
- Satu adegan membawa satu ide. Urutannya: masalah yang relatable, contoh konkret, penjelasan mekanisme, bukti dari artikel, lalu penutup.
- Konflik dibuat hidup lewat contoh sehari-hari, bukan lewat kata sifat. Contoh: "kalau kamu sering dibilang sudah cukup, tapi capek" lebih kuat daripada "hidup itu berat".
- Penutup berupa kutipan bernama atau satu pertanyaan terbuka. Tidak ada ajakan berjualan.
- Pakai `reels-script`, `short-form-video-script`, dan `storyboarding` (Social Media Skills) sebagai kerangka. Isi faktanya tetap dari artikel.
- Pelajari pola narasi dari referensi, tapi jangan menyalin kalimat, karakter, atau visualnya.

## 3. Voice over (Sonara VO)
Sonara VO adalah alat VO gratis milik tim di repo `afreshialaff/sonara-voice`. Kalau belum ada di mesin: `git clone https://github.com/afreshialaff/sonara-voice` lalu `pip install -r requirements.txt` di folder itu. ffmpeg disarankan supaya jeda dan volume rata. Panduan lengkap ada di `CLAUDE.md` repo tersebut.

- Setiap Reels wajib punya voice over. Naskah ditulis untuk telinga: kalimat pendek, maksimal sekitar 12 kata per baris, dibaca keras dulu.
- Setiap baris VO sama dengan teks di layar untuk adegan itu, jadi tetap terbaca kalau suara mati.
- Tulis naskah VO di `social/<tgl>/reel/naskah-vo.txt`. Satu paragraf sama dengan satu adegan, urut sesuai storyboard. Catatan shot ditulis di baris yang diawali `#`.
- Suara: pakai suara yang dipilih tim untuk Reels hari itu. Kalau tim belum memilih, pakai `ardi`. Daftar suara: `python sonara_vo.py list`. Naskah bahasa Indonesia hanya memakai suara Indonesia (`ardi`, `gadis`). Format dialog boleh dua suara dengan tag `[suara gadis]` dan `[suara ardi]` di dalam naskah.
- Render sekali:
  `python <folder-sonara>/sonara_vo.py say -v <suara> -i social/<tgl>/reel/naskah-vo.txt -o social/<tgl>/reel/vo.mp3 --words --json social/<tgl>/reel/vo.json`
  Hasilnya `vo.mp3`, `vo.srt` (subtitle per kata untuk caption animasi), dan `vo.json` (suara yang dipakai plus mulai, selesai, dan durasi tiap adegan).
- Durasi tiap adegan mengikuti `scenes[].duration` di `vo.json`. Kalau VO kepanjangan, potong naskahnya, jangan mempercepat suara dengan `--rate`.
- Tanda baca mengatur napas: koma untuk jeda kecil, `…` untuk jeda sesaat, `[jeda]` atau `[jeda 1.2]` untuk jeda yang pasti, `[pelan]` sebelum kalimat kunci, `[normal]` untuk kembali.
- `vo.json` sudah berisi `"ai_voice": true`. Salin keterangan ini ke `post.json` supaya Corong bisa menambahkan keterangan di caption.
- Sonara VO gratis. Jangan memakai ElevenLabs atau layanan VO berbayar lain kecuali tim memintanya.
- Kalau Sonara gagal (misalnya `Speech service failed` setelah dicoba ulang sekali), tulis "VO BELUM ADA" dan jangan memakai suara lain. Reels tanpa VO tidak lolos ke Lup sosial.

## 4. Konteks harus terbaca tanpa caption
- Penonton yang tidak membaca caption harus tahu: apa topiknya, siapa yang bicara (nama dan jabatan di layar), dan kapan atau di mana kejadiannya.
- Setiap angka punya label satuan dan tahun di dalam frame, bukan hanya di caption.
- Kutipan selalu disertai nama dan jabatan orangnya.

## 5. Teks di layar
- Maksimal 8 kata sekaligus. Di atas itu, pecah jadi dua frame.
- Angka besar minimal sekitar 60 px di lebar 1080. Isi minimal sekitar 36 px. Label grafik minimal sekitar 30 px.
- Judul tidak diulang di adegan lain.
- Ruang kosong dijaga. Tidak ada teks yang menimpa gambar atau diagram.

## 6. Variasi format antar Reels
Jangan pakai format yang sama dua hari berturut-turut. Pilih salah satu dan catat di log:
- **Tanya-jawab:** pertanyaan di frame 1, jawaban dengan satu bukti per adegan.
- **Bukti satu angka:** satu angka besar, lalu konteksnya, lalu sumbernya.
- **Timeline:** tahun-tahun dalam urutan, dengan satu peristiwa per frame.
- **Perbandingan:** dua hal berdampingan, misalnya kelompok umur atau dua klaim.
- **Cerita bersambung:** satu tokoh atau situasi yang berubah dari adegan ke adegan, berakhir dengan pertanyaan terbuka.

## 7. Gambar
- Sumber yang boleh: `image` dan `img` artikel di `content/stories/<id>.json` (sudah berlisensi terbuka dan berkredit), atau ilustrasi SVG di `assets/illustrations/`.
- Kredit ditampilkan di dalam frame, kecil tapi terbaca, di sudut bawah.
- Gambar dipilih karena relevan dengan adegan. Dilarang memakai foto peristiwa lain seolah-olah peristiwa yang dibahas.
- Footage dan foto dari luar tetap dilarang.

## 8. Sebelum render
- Ambil snapshot tiap adegan dan lihat contact sheet. Pastikan frame pertama sudah berisi subjek dan teks hook.
- Hitung waktu baca: minimal 0,4 detik per kata yang tampil.
- Dengarkan VO dari awal sampai akhir. Tidak ada kata terpotong atau salah ucap. Kalau ada yang salah ucap (singkatan, nama asing, angka), tulis ulang ejaannya di naskah lalu render ulang.
- Cocokkan `vo.srt` dengan teks di layar. Teks subtitle dan teks layar harus sama.
- Cocokkan setiap angka dan nama dengan artikel. Angka yang tidak ada di artikel tidak boleh masuk.

## 9. Data performa dan setelah terbit
- Data performa diambil dari `pipeline/rapat/ig-insights/` (reach, saves, shares, likes, comments). Kalau data repo belum ada, skill `instagram` atau `social-media-insights` dari Windsor.ai bisa dipakai sebagai pembanding. Sebutkan sumbernya di log.
- Catat format, suara yang dipakai, dan hipotesisnya di `pipeline/rapat/viral-log.md`.

## Batas
- Tidak ada klaim tentang algoritma. Format dipilih berdasarkan data akun dan pola yang bisa diuji.
- Hook yang clickbait ditolak, sesuai `bahasa.md` bagian 5.
- Saran dari plugin tidak boleh mengubah fakta, angka, atau sumber artikel.
- Suara AI wajib diberi keterangan. Tidak boleh meniru suara orang nyata tanpa izin tertulis.