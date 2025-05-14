import os
import random
from moviepy.editor import TextClip, ImageClip, AudioFileClip, CompositeVideoClip, ColorClip
from PIL import Image
import numpy as np
from tqdm import tqdm
import traceback

from lyric_effects import LyricEffects

class VideoGenerator:
    """
    Class untuk generate video lirik dari file audio + gambar background
    """
    
    def __init__(self, 
                 audio_path=None,
                 background_image_path=None,
                 output_path="output",
                 font="Arial",
                 font_size=70,
                 font_color="white",
                 text_effect="fade_in",
                 output_size=(1920, 1080),
                 quality="1080p",
                 text_position="center",  # Posisi teks: top, center, bottom
                 color_effect="none"):    # Efek warna: none, gradient, pulse, spectrum
        """
        Initialize the video generator
        """
        self.audio_path = audio_path
        self.background_image_path = background_image_path
        self.output_path = output_path
        self.font = font
        self.font_size = font_size
        self.font_color = font_color
        self.text_effect = text_effect
        self.text_position = text_position
        self.color_effect = color_effect
        
        # Set output size berdasarkan quality
        self.quality_presets = {
            "720p": (1280, 720),
            "1080p": (1920, 1080),
            "4K": (3840, 2160)
        }
        
        if isinstance(output_size, str) and output_size in self.quality_presets:
            self.output_size = self.quality_presets[output_size]
        else:
            self.output_size = output_size
            
        # Set quality
        self.quality = quality
        
        # Create output directory if not exists
        if not os.path.exists(output_path):
            os.makedirs(output_path)
            
    def random_background_image(self, image_dir):
        """
        Pilih background image random dari direktori
        """
        valid_extensions = ('.jpg', '.jpeg', '.png', '.bmp')
        image_files = [f for f in os.listdir(image_dir) 
                      if f.lower().endswith(valid_extensions)]
                      
        if not image_files:
            raise ValueError(f"No image files found in {image_dir}")
            
        random_image = random.choice(image_files)
        return os.path.join(image_dir, random_image)
        
    def resize_background(self, image_path, target_size):
        """
        Resize background image sesuai ukuran target
        """
        image = Image.open(image_path)
        
        # Get original aspect ratio
        width, height = image.size
        aspect_ratio = width / height
        
        target_width, target_height = target_size
        target_aspect_ratio = target_width / target_height
        
        # Resize strategy
        if aspect_ratio > target_aspect_ratio:
            # Image lebih wide, crop pinggirnya
            new_width = int(height * target_aspect_ratio)
            left = (width - new_width) // 2
            image = image.crop((left, 0, left + new_width, height))
        else:
            # Image lebih tall, crop atas bawahnya
            new_height = int(width / target_aspect_ratio)
            top = (height - new_height) // 2
            image = image.crop((0, top, width, top + new_height))
            
        # Resize ke target size
        image = image.resize(target_size, Image.LANCZOS)
        
        # Convert ke array untuk MoviePy
        return np.array(image)
        
    def make_portrait_video(self, lyrics, audio_clip, bg_image_path):
        """
        Buat vertical video untuk portrait mode (9:16)
        """
        # Set portrait size (e.g., 1080x1920 for 9:16)
        portrait_size = (1080, 1920)
        
        # Resize background untuk portrait
        bg_array = self.resize_background(bg_image_path, portrait_size)
        bg_clip = ImageClip(bg_array).set_duration(audio_clip.duration)
        
        # Bikin semua text clips
        text_clips = []
        
        # Parameter warna gradient jika digunakan
        gradient_colors = None
        if self.color_effect == "gradient":
            # Gunakan warna font sebagai warna awal
            start_color = self.font_color
            # Buat warna akhir yang kontras
            # Konversi hex ke RGB dan balik nilainya untuk mendapatkan warna yang kontras
            hex_color = self.font_color.lstrip('#')
            rgb = tuple(255 - int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            end_color = '#{:02x}{:02x}{:02x}'.format(rgb[0], rgb[1], rgb[2])
            gradient_colors = [start_color, end_color]
        
        for i, lyric in enumerate(lyrics):
            start_time = lyric['start']
            end_time = lyric['end']
            duration = end_time - start_time
            
            # Tentukan efek yang akan digunakan
            effect_name = self.text_effect
            
            # Jika ada color effect, prioritaskan
            if self.color_effect != "none":
                if self.color_effect == "gradient":
                    effect_name = "color_gradient"
                elif self.color_effect == "pulse":
                    effect_name = "color_pulse"
                elif self.color_effect == "spectrum":
                    effect_name = "color_spectrum"
                elif self.color_effect == "rainbow":
                    effect_name = "rainbow"
            
            # Parameter tambahan untuk efek
            kwargs = {}
            if effect_name == "color_gradient" and gradient_colors:
                kwargs["gradient_colors"] = gradient_colors
            
            # Apply text effect
            text_clip = LyricEffects.apply_effect(
                text=lyric['text'],
                effect_name=effect_name,
                font=self.font,
                fontsize=self.font_size,
                color=self.font_color,
                duration=duration,
                position=self.text_position,
                screen_size=portrait_size,
                **kwargs
            )
            
            # Set timing
            text_clip = text_clip.set_start(start_time)
            text_clips.append(text_clip)
            
        # Gabungkan semua clips
        final_clip = CompositeVideoClip([bg_clip] + text_clips, size=portrait_size)
        
        # Set audio
        final_clip = final_clip.set_audio(audio_clip)
        
        return final_clip
        
    def make_landscape_video(self, lyrics, audio_clip, bg_image_path):
        """
        Buat landscape video untuk 16:9 ratio
        """
        # Set landscape size berdasarkan quality
        landscape_size = self.quality_presets.get(self.quality, (1920, 1080))
        
        # Resize background
        bg_array = self.resize_background(bg_image_path, landscape_size)
        bg_clip = ImageClip(bg_array).set_duration(audio_clip.duration)
        
        # Bikin semua text clips
        text_clips = []
        
        # Parameter warna gradient jika digunakan
        gradient_colors = None
        if self.color_effect == "gradient":
            # Gunakan warna font sebagai warna awal
            start_color = self.font_color
            # Buat warna akhir yang kontras
            # Konversi hex ke RGB dan balik nilainya untuk mendapatkan warna yang kontras
            hex_color = self.font_color.lstrip('#')
            rgb = tuple(255 - int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            end_color = '#{:02x}{:02x}{:02x}'.format(rgb[0], rgb[1], rgb[2])
            gradient_colors = [start_color, end_color]
        
        for i, lyric in enumerate(lyrics):
            start_time = lyric['start']
            end_time = lyric['end']
            duration = end_time - start_time
            
            # Tentukan efek yang akan digunakan
            effect_name = self.text_effect
            
            # Jika ada color effect, prioritaskan
            if self.color_effect != "none":
                if self.color_effect == "gradient":
                    effect_name = "color_gradient"
                elif self.color_effect == "pulse":
                    effect_name = "color_pulse"
                elif self.color_effect == "spectrum":
                    effect_name = "color_spectrum"
                elif self.color_effect == "rainbow":
                    effect_name = "rainbow"
            
            # Parameter tambahan untuk efek
            kwargs = {}
            if effect_name == "color_gradient" and gradient_colors:
                kwargs["gradient_colors"] = gradient_colors
            
            # Apply text effect
            text_clip = LyricEffects.apply_effect(
                text=lyric['text'],
                effect_name=effect_name,
                font=self.font,
                fontsize=self.font_size,
                color=self.font_color,
                duration=duration,
                position=self.text_position,
                screen_size=landscape_size,
                **kwargs
            )
            
            # Set timing
            text_clip = text_clip.set_start(start_time)
            text_clips.append(text_clip)
            
        # Gabungkan semua clips
        final_clip = CompositeVideoClip([bg_clip] + text_clips, size=landscape_size)
        
        # Set audio
        final_clip = final_clip.set_audio(audio_clip)
        
        return final_clip
        
    def generate_video(self, lyrics, output_ratio="landscape"):
        """
        Generate video lirik dengan audio + background + lirik
        
        Parameters:
            lyrics (list): List of lyric dictionaries dengan timestamps
            output_ratio (str): 'landscape' atau 'portrait'
            
        Returns:
            str: Path ke video output
        """
        try:
            # Load audio file
            audio_clip = AudioFileClip(self.audio_path)
            
            # Load background image
            if os.path.isdir(self.background_image_path):
                bg_image_path = self.random_background_image(self.background_image_path)
            else:
                bg_image_path = self.background_image_path
                
            print(f"Using background image: {os.path.basename(bg_image_path)}")
            
            # Generate video berdasarkan ratio
            if output_ratio.lower() == "portrait":
                print("Generating portrait video (9:16)...")
                final_clip = self.make_portrait_video(lyrics, audio_clip, bg_image_path)
            else:
                print("Generating landscape video (16:9)...")
                final_clip = self.make_landscape_video(lyrics, audio_clip, bg_image_path)
                
            # Output filename
            audio_basename = os.path.splitext(os.path.basename(self.audio_path))[0]
            output_file = os.path.join(self.output_path, f"{audio_basename}_lyric_video.mp4")
            
            # Set codec dan bitrate berdasarkan quality
            codec = "libx264"
            if self.quality == "4K":
                bitrate = "20000k"
            elif self.quality == "1080p":
                bitrate = "8000k"
            else:  # 720p
                bitrate = "4000k"
                
            # Write output video file
            print(f"Rendering video to: {output_file}")
            final_clip.write_videofile(
                output_file,
                codec=codec,
                bitrate=bitrate,
                audio_codec="aac",
                audio_bitrate="320k",
                fps=30,
                threads=4,
                preset="medium"
            )
            
            print(f"✓ Video generated successfully: {output_file}")
            return output_file
            
        except Exception as e:
            print(f"✗ Error generating video: {str(e)}")
            traceback.print_exc()
            return None
            
    def batch_generate(self, lyrics_dict, output_ratio="landscape"):
        """
        Generate multiple videos dari dictionary lyrics
        
        Parameters:
            lyrics_dict (dict): Dictionary {filename: lyrics}
            output_ratio (str): 'landscape' atau 'portrait'
            
        Returns:
            list: List of output video paths
        """
        output_videos = []
        
        # Mendapatkan direktori audio
        audio_dir = ""
        if self.audio_path:
            audio_dir = os.path.dirname(self.audio_path)
        
        # Print debugging info
        print(f"Audio directory: {audio_dir}")
        print(f"Audio folder from settings: {getattr(self, 'audio_folder', 'Not set')}")
        print(f"Processing {len(lyrics_dict)} transcriptions")
        
        for filename, lyrics in tqdm(lyrics_dict.items(), desc="Generating videos"):
            try:
                # Cari file audio yang sesuai dengan nama file dari hasil transkripsi
                found = False
                audio_path = None
                
                # List ekstensi audio yang mungkin
                extensions = ['.mp3', '.wav', '.flac', '.ogg', '.m4a']
                
                # Debug info for current file
                print(f"\nTrying to match audio file for: {filename}")
                
                # CARA 1: Coba cari di direktori yang sama dengan audio_path yang diatur sebelumnya
                if audio_dir:
                    for ext in extensions:
                        potential_path = os.path.join(audio_dir, f"{filename}{ext}")
                        print(f"Checking: {potential_path}")
                        if os.path.exists(potential_path):
                            audio_path = potential_path
                            found = True
                            print(f"FOUND at audio_dir: {audio_path}")
                            break
                
                # CARA 2: Jika tidak ditemukan, coba cari di direktori audio yang dipilih (self.audio_folder)
                if not found and hasattr(self, 'audio_folder') and self.audio_folder:
                    for ext in extensions:
                        potential_path = os.path.join(self.audio_folder, f"{filename}{ext}")
                        print(f"Checking: {potential_path}")
                        if os.path.exists(potential_path):
                            audio_path = potential_path
                            found = True
                            print(f"FOUND at audio_folder: {audio_path}")
                            break
                            
                    # CARA 2.1: Cari dengan nama file lengkap (bukan hanya base filename)
                    if not found:
                        # List semua file di direktori audio
                        audio_files = [f for f in os.listdir(self.audio_folder) if os.path.splitext(f)[1].lower() in [e.lower() for e in extensions]]
                        for audio_file in audio_files:
                            base_name = os.path.splitext(audio_file)[0]
                            if base_name == filename or filename in base_name:
                                audio_path = os.path.join(self.audio_folder, audio_file)
                                found = True
                                print(f"FOUND by similar name: {audio_path}")
                                break
                
                # CARA 3: Jika tidak ditemukan, coba cari di direktori saat ini
                if not found:
                    for ext in extensions:
                        potential_path = f"{filename}{ext}"
                        print(f"Checking: {potential_path}")
                        if os.path.exists(potential_path):
                            audio_path = potential_path
                            found = True
                            print(f"FOUND at current dir: {audio_path}")
                            break
                
                if not found:
                    print(f"✗ Cannot find audio file for {filename}")
                    continue
                
                # Set audio path untuk generator ini
                self.audio_path = audio_path
                
                # Generate video
                print(f"Generating video for {filename} using audio: {audio_path}")
                output_video = self.generate_video(lyrics, output_ratio)
                if output_video:
                    output_videos.append(output_video)
                    
            except Exception as e:
                print(f"✗ Error processing {filename}: {str(e)}")
                traceback.print_exc()
                
        return output_videos 