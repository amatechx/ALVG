import numpy as np
from moviepy.editor import TextClip, CompositeVideoClip, ColorClip, ImageClip
import random
import os
from PIL import Image, ImageDraw, ImageFont
import tempfile
import colorsys

class LyricEffects:
    """
    Class untuk menerapkan berbagai efek animasi pada teks lirik
    """
    
    @staticmethod
    def create_text_clip(text, font, fontsize, color, duration=None):
        """
        Buat text clip tanpa bergantung pada ImageMagick
        Metode alternatif menggunakan PIL untuk membuat gambar teks
        """
        try:
            # Coba cara biasa dulu
            return TextClip(text, font=font, fontsize=fontsize, color=color, method='label')
        except Exception as e:
            print(f"Error creating text clip with default method: {str(e)}")
            print("Trying alternative method with PIL...")
            
            # Buat gambar dengan PIL
            font_path = font
            if font in ["Arial", "Times New Roman", "Calibri", "Verdana", "Helvetica"]:
                # Untuk font default sistem, gunakan PIL default
                font_path = None
            
            # Buat gambar kosong dengan ukuran besar
            width, height = 1000, 200
            img = Image.new('RGBA', (width, height), color=(0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            
            # Siapkan font
            try:
                if font_path and os.path.exists(font_path):
                    pil_font = ImageFont.truetype(font_path, fontsize)
                else:
                    # Gunakan font default jika tidak ditemukan
                    pil_font = ImageFont.truetype("arial.ttf", fontsize)
            except Exception:
                # Fallback ke default PIL font
                pil_font = ImageFont.load_default()
                
            # Gambar teks
            draw.text((10, 10), text, fill=color, font=pil_font)
            
            # Crop ke ukuran teks
            bbox = img.getbbox()
            if bbox:
                img = img.crop(bbox)
            
            # Simpan ke file temporary
            temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
            img.save(temp_file.name)
            
            # Buat clip dari file
            clip = ImageClip(temp_file.name)
            if duration:
                clip = clip.set_duration(duration)
                
            # Jadwalkan penghapusan file sementara
            def cleanup():
                try:
                    os.unlink(temp_file.name)
                except:
                    pass
            clip.cleanup = cleanup
            
            return clip
    
    @staticmethod
    def apply_text_position(clip, position, screen_size):
        """
        Fungsi untuk mengatur posisi teks pada screen
        
        Parameters:
            clip (TextClip): Clip teks yang akan diatur posisinya
            position (str): Posisi teks ('top', 'center', 'bottom')
            screen_size (tuple): Ukuran layar (width, height)
            
        Returns:
            TextClip: Clip dengan posisi yang sudah diatur
        """
        width, height = screen_size
        
        if position == "top":
            pos = ('center', height * 0.2)  # 20% dari atas
        elif position == "center":
            pos = ('center', 'center')  # Tengah layar
        elif position == "bottom":
            pos = ('center', height * 0.8)  # 80% dari atas (20% dari bawah)
        else:
            # Default ke tengah
            pos = ('center', 'center')
            
        return clip.set_position(pos)
    
    @staticmethod
    def color_gradient_effect(text, font, fontsize, colors, duration):
        """
        Efek gradient warna (transisi antar warna)
        
        Parameters:
            text (str): Teks yang akan ditampilkan
            font (str): Font yang digunakan
            fontsize (int): Ukuran font
            colors (list): List warna untuk gradient [color1, color2]
            duration (float): Durasi clip dalam detik
            
        Returns:
            VideoClip: Clip dengan efek gradient
        """
        clips = []
        start_color = colors[0]
        end_color = colors[1]
        
        # Buat 10 frame untuk transisi warna halus
        steps = 10
        
        # Konversi warna hex ke RGB untuk interpolasi
        def hex_to_rgb(hex_color):
            hex_color = hex_color.lstrip('#')
            return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        
        def rgb_to_hex(rgb):
            return '#{:02x}{:02x}{:02x}'.format(int(rgb[0]), int(rgb[1]), int(rgb[2]))
        
        start_rgb = hex_to_rgb(start_color)
        end_rgb = hex_to_rgb(end_color)
        
        # Buat beberapa clip dengan warna berbeda untuk transisi
        for i in range(steps):
            # Interpolasi warna
            t = i / (steps - 1)
            r = start_rgb[0] + (end_rgb[0] - start_rgb[0]) * t
            g = start_rgb[1] + (end_rgb[1] - start_rgb[1]) * t
            b = start_rgb[2] + (end_rgb[2] - start_rgb[2]) * t
            
            color = rgb_to_hex((r, g, b))
            start_time = duration * (i / steps)
            clip_duration = duration / steps
            
            txt_clip = LyricEffects.create_text_clip(text, font, fontsize, color)
            txt_clip = txt_clip.set_start(start_time).set_duration(clip_duration)
            clips.append(txt_clip)
            
        return CompositeVideoClip(clips).set_duration(duration)
    
    @staticmethod
    def color_pulse_effect(text, font, fontsize, color, duration):
        """
        Efek pulse warna (berubah kecerahan/opacity)
        
        Parameters:
            text (str): Teks yang akan ditampilkan
            font (str): Font yang digunakan
            fontsize (int): Ukuran font
            color (str): Warna dasar
            duration (float): Durasi clip dalam detik
            
        Returns:
            VideoClip: Clip dengan efek pulse
        """
        base_clip = LyricEffects.create_text_clip(text, font, fontsize, color).set_duration(duration)
        
        # Fungsi untuk mengubah opacity berdasarkan waktu
        def pulse_opacity(t):
            # Menggunakan fungsi sin untuk efek pulse
            return 0.6 + 0.4 * np.sin(t * 2 * np.pi)
        
        return base_clip.set_opacity(pulse_opacity)
    
    @staticmethod
    def color_spectrum_effect(text, font, fontsize, duration):
        """
        Efek perubahan warna melalui seluruh spektrum
        
        Parameters:
            text (str): Teks yang akan ditampilkan
            font (str): Font yang digunakan
            fontsize (int): Ukuran font
            duration (float): Durasi clip dalam detik
            
        Returns:
            VideoClip: Clip dengan efek perubahan spektrum warna
        """
        clips = []
        steps = 20  # Jumlah langkah untuk animasi
        
        for i in range(steps):
            # Menggunakan HSV untuk transisi warna halus melalui spektrum
            hue = i / steps
            sat = 1.0
            val = 1.0
            
            # Konversi HSV ke RGB
            r, g, b = colorsys.hsv_to_rgb(hue, sat, val)
            color = '#{:02x}{:02x}{:02x}'.format(int(r*255), int(g*255), int(b*255))
            
            start_time = duration * (i / steps)
            clip_duration = duration / steps
            
            txt_clip = LyricEffects.create_text_clip(text, font, fontsize, color)
            txt_clip = txt_clip.set_start(start_time).set_duration(clip_duration)
            clips.append(txt_clip)
            
        return CompositeVideoClip(clips).set_duration(duration)
    
    @staticmethod
    def typing_effect(text, font, fontsize, color, duration, bg_color=None):
        """
        Efek ketik satu per satu (typing effect)
        """
        clips = []
        total_chars = len(text)
        
        # Kalo tekstnya kosong, return clip kosong
        if total_chars == 0:
            return LyricEffects.create_text_clip(" ", font, fontsize, color).set_duration(duration)
            
        char_duration = duration / total_chars
        
        for i in range(1, total_chars + 1):
            current_text = text[:i]
            t_start = (i - 1) * char_duration
            
            txt_clip = LyricEffects.create_text_clip(current_text, font, fontsize, color)
            txt_clip = txt_clip.set_start(t_start).set_duration(char_duration)
            
            if bg_color:
                # Bikin background clip kalo ada
                txt_w, txt_h = txt_clip.size
                bg_clip = ColorClip(size=(txt_w, txt_h), color=bg_color)
                bg_clip = bg_clip.set_opacity(0.5).set_duration(char_duration).set_start(t_start)
                clips.append(bg_clip)
                
            clips.append(txt_clip)
            
        return CompositeVideoClip(clips).set_duration(duration)
        
    @staticmethod
    def fade_effect(text, font, fontsize, color, duration, fade_type="in"):
        """
        Efek fade in / fade out
        """
        fade_duration = min(duration / 3, 1.5)  # Max 1.5 detik atau 1/3 durasi
        
        txt_clip = LyricEffects.create_text_clip(text, font, fontsize, color).set_duration(duration)
        
        if fade_type == "in":
            return txt_clip.fadein(fade_duration)
        elif fade_type == "out":
            return txt_clip.fadeout(fade_duration)
        elif fade_type == "both":
            return txt_clip.fadein(fade_duration).fadeout(fade_duration)
        else:
            return txt_clip
            
    @staticmethod
    def slide_effect(text, font, fontsize, color, duration, direction="left"):
        """
        Efek slide dari berbagai arah
        """
        txt_clip = LyricEffects.create_text_clip(text, font, fontsize, color).set_duration(duration)
        screen_w, screen_h = 1920, 1080  # Default size, bisa diatur sesuai output
        
        # Posisi awal dan akhir tergantung arah
        if direction == "left":
            start_pos = lambda t: (screen_w * (1 - t/1.5), 'center') if t < 1.5 else ('center', 'center')
        elif direction == "right":
            start_pos = lambda t: (-screen_w * (1 - t/1.5), 'center') if t < 1.5 else ('center', 'center')
        elif direction == "top":
            start_pos = lambda t: ('center', -screen_h * (1 - t/1.5)) if t < 1.5 else ('center', 'center')
        elif direction == "bottom":
            start_pos = lambda t: ('center', screen_h * (1 - t/1.5)) if t < 1.5 else ('center', 'center')
        else:
            start_pos = ('center', 'center')
            
        return txt_clip.set_position(start_pos)
        
    @staticmethod
    def zoom_effect(text, font, fontsize, color, duration, zoom_type="in"):
        """
        Efek zoom in / zoom out
        """
        txt_clip = LyricEffects.create_text_clip(text, font, fontsize, color).set_duration(duration)
        
        if zoom_type == "in":
            scale_factor = lambda t: min(1, t)  # Dari 0 ke 1 dalam 1 detik
        elif zoom_type == "out":
            scale_factor = lambda t: max(0.1, 1 - t/duration)  # Dari 1 ke 0 selama durasi
        else:
            return txt_clip
            
        return txt_clip.resize(lambda t: scale_factor(t))
        
    @staticmethod
    def bounce_effect(text, font, fontsize, color, duration):
        """
        Efek bounce (mantul-mantul)
        """
        txt_clip = LyricEffects.create_text_clip(text, font, fontsize, color).set_duration(duration)
        
        # Fungsi bounce: y position berubah berdasarkan sin function
        def bounce_pos(t):
            # Frekuensi bounce
            freq = 3
            # Amplitudo bounce (seberapa tinggi mantulnya)
            amp = 10
            # Sin function untuk efek mantul
            bounce_offset = amp * np.sin(freq * t * 2 * np.pi)
            return ('center', 'center' + bounce_offset)
            
        return txt_clip.set_position(bounce_pos)
        
    @staticmethod
    def glow_effect(text, font, fontsize, color, duration):
        """
        Efek glow / neon flicker
        """
        base_clip = LyricEffects.create_text_clip(text, font, fontsize, color).set_duration(duration)
        
        # Bikin beberapa lapis teks dengan opacity berbeda dan ukuran sedikit lebih besar
        clips = [base_clip]
        glow_color = "white"  # atau sesuaikan dengan warna teksnya
        
        for i in range(3):
            glow = LyricEffects.create_text_clip(text, font, fontsize + i*2, glow_color)
            glow = glow.set_opacity(0.3 - i*0.1).set_duration(duration)
            
            # Efek flicker (kedip) dengan opacity berubah
            if i == 0:
                flicker = lambda t: 0.3 + 0.1 * np.sin(t * 8)
                glow = glow.set_opacity(flicker)
                
            clips.append(glow)
            
        return CompositeVideoClip(clips).set_duration(duration)
        
    @staticmethod
    def shake_effect(text, font, fontsize, color, duration):
        """
        Efek shake / vibration (getar)
        """
        txt_clip = LyricEffects.create_text_clip(text, font, fontsize, color).set_duration(duration)
        
        # Intensitas getaran (makin gede, makin keras getarnya)
        intensity = 3
        
        # Fungsi untuk posisi random tiap frame buat efek getar
        def shake_pos(t):
            # Random offset untuk x dan y
            dx = random.uniform(-intensity, intensity)
            dy = random.uniform(-intensity, intensity)
            return ('center' + dx, 'center' + dy)
            
        return txt_clip.set_position(shake_pos)
        
    @staticmethod
    def wave_effect(text, font, fontsize, color, duration):
        """
        Efek wave / wobble (bergelombang)
        """
        # Ini lebih kompleks, kita perlu bikin frame-by-frame
        # Contoh sederhana dengan pendekatan posisi
        txt_clip = LyricEffects.create_text_clip(text, font, fontsize, color).set_duration(duration)
        
        # Fungsi wave berdasarkan waktu
        def wave_pos(t):
            wave_x = 5 * np.sin(t * 2 * np.pi)
            wave_y = 5 * np.cos(t * 3 * np.pi)
            return ('center' + wave_x, 'center' + wave_y)
            
        return txt_clip.set_position(wave_pos)
        
    @staticmethod
    def rainbow_effect(text, font, fontsize, duration):
        """
        Efek warna berubah-ubah / rainbow
        """
        # Untuk rainbow kita perlu membuat beberapa clip untuk setiap perubahan warna
        clips = []
        colors = ['red', 'orange', 'yellow', 'green', 'blue', 'purple']
        segment_duration = duration / len(colors)
        
        for i, color in enumerate(colors):
            start_time = i * segment_duration
            txt_clip = LyricEffects.create_text_clip(text, font, fontsize, color)
            txt_clip = txt_clip.set_start(start_time).set_duration(segment_duration)
            clips.append(txt_clip)
            
        return CompositeVideoClip(clips).set_duration(duration)

    @staticmethod
    def apply_effect(text, effect_name, font="Arial", fontsize=70, color="white", duration=3.0, position="center", screen_size=(1920, 1080), **kwargs):
        """
        Fungsi helper untuk menerapkan efek berdasarkan nama
        
        Parameters:
            text (str): Teks yang akan ditampilkan
            effect_name (str): Nama efek yang akan diterapkan
            font (str): Font yang digunakan
            fontsize (int): Ukuran font
            color (str): Warna font
            duration (float): Durasi clip dalam detik
            position (str): Posisi teks ('top', 'center', 'bottom')
            screen_size (tuple): Ukuran layar (width, height)
            **kwargs: Parameter tambahan untuk efek
            
        Returns:
            VideoClip: Clip dengan efek yang sudah diterapkan
        """
        # Efek teks standard
        if effect_name == "typing":
            clip = LyricEffects.typing_effect(text, font, fontsize, color, duration, **kwargs)
        elif effect_name == "fade_in":
            clip = LyricEffects.fade_effect(text, font, fontsize, color, duration, fade_type="in")
        elif effect_name == "fade_out":
            clip = LyricEffects.fade_effect(text, font, fontsize, color, duration, fade_type="out") 
        elif effect_name == "fade_both":
            clip = LyricEffects.fade_effect(text, font, fontsize, color, duration, fade_type="both")
        elif effect_name == "slide_left":
            clip = LyricEffects.slide_effect(text, font, fontsize, color, duration, direction="left")
        elif effect_name == "slide_right":
            clip = LyricEffects.slide_effect(text, font, fontsize, color, duration, direction="right")
        elif effect_name == "slide_top":
            clip = LyricEffects.slide_effect(text, font, fontsize, color, duration, direction="top")
        elif effect_name == "slide_bottom":
            clip = LyricEffects.slide_effect(text, font, fontsize, color, duration, direction="bottom")
        elif effect_name == "zoom_in":
            clip = LyricEffects.zoom_effect(text, font, fontsize, color, duration, zoom_type="in")
        elif effect_name == "zoom_out":
            clip = LyricEffects.zoom_effect(text, font, fontsize, color, duration, zoom_type="out")
        elif effect_name == "bounce":
            clip = LyricEffects.bounce_effect(text, font, fontsize, color, duration)
        elif effect_name == "glow":
            clip = LyricEffects.glow_effect(text, font, fontsize, color, duration)
        elif effect_name == "shake":
            clip = LyricEffects.shake_effect(text, font, fontsize, color, duration)
        elif effect_name == "wave":
            clip = LyricEffects.wave_effect(text, font, fontsize, color, duration)
        
        # Efek warna
        elif effect_name == "rainbow":
            clip = LyricEffects.rainbow_effect(text, font, fontsize, duration)
        elif effect_name == "color_gradient":
            gradient_colors = kwargs.get('gradient_colors', ['#FF0000', '#0000FF'])  # Default: red to blue
            clip = LyricEffects.color_gradient_effect(text, font, fontsize, gradient_colors, duration)
        elif effect_name == "color_pulse":
            clip = LyricEffects.color_pulse_effect(text, font, fontsize, color, duration)
        elif effect_name == "color_spectrum":
            clip = LyricEffects.color_spectrum_effect(text, font, fontsize, duration)
        
        # Default: no effect, just static text
        else:
            clip = LyricEffects.create_text_clip(text, font, fontsize, color).set_duration(duration)
        
        # Terapkan posisi akhir sesuai dengan parameter
        # Jika efeknya tidak mengganti posisi original
        if effect_name not in ["slide_left", "slide_right", "slide_top", "slide_bottom", "bounce", "wave", "shake"]:
            clip = LyricEffects.apply_text_position(clip, position, screen_size)
            
        return clip 