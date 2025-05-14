# 🎶 Auto Lyric Video Generator

Bikin video lirik otomatis dari file audio + gambar background.  
Lirik langsung ditranskrip otomatis pake OpenAI Whisper.  
Style lirik? Bebas bro! Font, warna, efek, dan layout semua lo yang atur.

---

## 🚀 Fitur

- ✅ Input pilih folder berisi file audio (.mp3, .wav, etc)
- ✅ Input pilih folder berisi image background (otomatis random pick atau disesuaikan)
- ✅ Transkrip otomatis lirik dengan OpenAI Whisper (offline, GRATIS!)
- ✅ Pilih font lirik (TTF/OTF)
- ✅ Pilih warna lirik
- ✅ Pilih efek lirik (ketik satu-satu, fade-in, dll)
- ✅ Output video dengan opsi:
  - 📐 Landscape 16:9
  - 📱 Portrait 9:16 (buat TikTok/IG Reels)
- ✅ Set kualitas output (720p, 1080p, 4K)
- ✅ Simpan video ke folder output
- ✅ Dukungan multi-bahasa (Indonesia, Inggris, dll)

---

## 📦 Instalasi

1. **Clone repo:**
   ```bash
   git clone https://github.com/amatechx/auto-lyric-video-generator.git
   cd auto-lyric-video-generator
   ```

2. **Install dependensi:**

   ```bash
   pip install -r requirements.txt
   ```

3. **(Opsional) Install Whisper via Git:**

   ```bash
   pip install git+https://github.com/openai/whisper.git
   ```

4. **Pastikan `ffmpeg` terinstall di sistem kamu.**

   * Windows: install dari [https://ffmpeg.org/download.html](https://ffmpeg.org/download.html)
   * Mac: `brew install ffmpeg`
   * Linux: `sudo apt install ffmpeg`

---

## 🧪 Cara Pakai

1. Jalankan app GUI-nya:

   ```bash
   python app.py
   ```

2. Pilih:

   * 📂 Folder Audio
   * 🖼️ Folder Image Background
   * 🔤 Font Lirik (bisa pilih .ttf/.otf)
   * 🎨 Warna Font
   * ✨ Efek Font (ketik, fade, bounce, dll)
   * 📐 Rasio video: `Landscape` / `Portrait`
   * 🎥 Kualitas: `720p`, `1080p`, `4K`

3. Klik **Generate**
   -> Boom! 🎬 Video lirik siap di-export otomatis ke folder output.

---

## 🎨 Contoh Output

![Example](./screenshots/sample_output.gif)

---

## ⚙️ Stack Tech:

* `Python 3.8+`
* `OpenAI Whisper`
* `ffmpeg-python`
* `moviepy`
* `tkinter` (untuk GUI)
* `Pillow` (untuk gambar)
* `customtkinter` (biar UI-nya gak norak)

---

## 📢 Catatan

* Gunakan folder dengan nama file audio yang rapi (judul tanpa karakter aneh).
* Audio dengan noise tinggi bisa hasilkan lirik yang kurang akurat.
* File output berupa `.mp4` dengan lirik tertanam.

---

## ☕ Kontribusi

Pull request? Silakan bro.
Punya fitur lucu-lucu kayak efek api di teks? Kirim PR lo. Gua approve kalo keren 😎

---

## 🧠 License

MIT License - bebas oprek, asal jangan dijual pake nama lo sendiri doang 😅

---

## 👋 Credits

Developed with 🤘 by [AMA]
Powered by OpenAI Whisper & FFmpeg Magic ✨ 