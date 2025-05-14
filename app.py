import os
import sys
import threading
import tkinter as tk
from tkinter import filedialog, colorchooser, ttk
import customtkinter as ctk
from PIL import Image, ImageTk
import random
import time
from tqdm import tqdm

# Import module kita
from audio_processor import AudioProcessor
from video_generator import VideoGenerator
from lyric_effects import LyricEffects

# Set UI theme
ctk.set_appearance_mode("dark")  # Mode: system (default), light, dark
ctk.set_default_color_theme("blue")  # Themes: blue (default), dark-blue, green

class LyricVideoApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Setup window
        self.title("Auto Lyric Video Generator 🎵")
        self.geometry("1100x680")
        self.minsize(900, 600)
        
        # Variables
        self.audio_folder = tk.StringVar()
        self.image_folder = tk.StringVar()
        self.output_folder = tk.StringVar(value="output")
        self.selected_font = tk.StringVar(value="Arial")
        self.font_size = tk.IntVar(value=70)
        self.font_color = tk.StringVar(value="#FFFFFF")
        self.video_ratio = tk.StringVar(value="landscape")
        self.video_quality = tk.StringVar(value="1080p")
        self.text_effect = tk.StringVar(value="fade_in")
        self.language = tk.StringVar(value="auto")
        self.whisper_model = tk.StringVar(value="base")
        self.text_position = tk.StringVar(value="center")
        self.color_effect = tk.StringVar(value="none")
        
        # Daftar font umum
        self.fonts = [
            "Arial",
            "Times New Roman",
            "Calibri",
            "Verdana",
            "Helvetica",
            "Tahoma",
            "Comic Sans MS",
            "Georgia",
            "Impact",
            "Courier New",
            "Segoe UI"
        ]
        
        # Efek-efek teks yang tersedia
        self.text_effects = [
            "none",
            "typing",
            "fade_in",
            "fade_both",
            "slide_left",
            "slide_right", 
            "slide_top",
            "slide_bottom",
            "zoom_in",
            "zoom_out",
            "bounce",
            "glow",
            "shake",
            "wave",
            "rainbow"
        ]
        
        # Posisi teks yang tersedia
        self.text_positions = [
            "top",
            "center",
            "bottom"
        ]
        
        # Efek warna yang tersedia
        self.color_effects = [
            "none",
            "gradient",
            "pulse", 
            "spectrum",
            "rainbow"
        ]
        
        # Bahasa yang didukung
        self.languages = [
            "auto",
            "id",  # Indonesian
            "en",  # English
            "ja",  # Japanese
            "ko",  # Korean
            "zh",  # Chinese
            "es",  # Spanish
            "fr",  # French
            "de",  # German
            "it",  # Italian
            "ru",  # Russian
        ]
        
        # Whisper model sizes
        self.whisper_models = [
            "tiny",
            "base",
            "small",
            "medium",
            "large"
        ]
        
        # Create UI
        self.create_ui()
        
        # Untuk simpan path font yang dipilih
        self.font_path = None
        
        # Inisialisasi processor dan generator
        self.audio_processor = AudioProcessor(model_size=self.whisper_model.get())
        self.video_generator = VideoGenerator(
            output_path=self.output_folder.get(),
            font=self.selected_font.get(),
            font_size=self.font_size.get(),
            font_color=self.font_color.get(),
            text_effect=self.text_effect.get(),
            quality=self.video_quality.get(),
            text_position=self.text_position.get(),
            color_effect=self.color_effect.get()
        )
        
    def create_ui(self):
        """Create the main UI elements"""
        # Main Frame (container)
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left Panel - Input Controls
        self.left_panel = ctk.CTkFrame(self.main_frame, width=400)
        self.left_panel.pack(side=tk.LEFT, fill=tk.BOTH, padx=10, pady=10, expand=False)
        
        # Right Panel - Preview & Log
        self.right_panel = ctk.CTkFrame(self.main_frame)
        self.right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, padx=10, pady=10, expand=True)
        
        # Create the UI components
        self.create_input_controls()
        self.create_preview_area()
        self.create_log_area()
        self.create_buttons()
        
    def create_input_controls(self):
        """Create input controls in the left panel"""
        # Title
        title = ctk.CTkLabel(self.left_panel, text="🎬 Video Settings", font=ctk.CTkFont(size=20, weight="bold"))
        title.pack(pady=10, padx=10, anchor="w")
        
        # Folder Selection Frames
        folder_frame = ctk.CTkFrame(self.left_panel)
        folder_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Audio Folder
        audio_label = ctk.CTkLabel(folder_frame, text="📂 Audio Folder:")
        audio_label.pack(anchor="w", padx=5, pady=2)
        
        audio_frame = ctk.CTkFrame(folder_frame)
        audio_frame.pack(fill=tk.X, padx=5, pady=2)
        
        audio_entry = ctk.CTkEntry(audio_frame, textvariable=self.audio_folder)
        audio_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        audio_btn = ctk.CTkButton(audio_frame, text="Browse", command=self.browse_audio_folder, width=80)
        audio_btn.pack(side=tk.RIGHT, padx=5)
        
        # Image Folder
        image_label = ctk.CTkLabel(folder_frame, text="🖼️ Background Image Folder:")
        image_label.pack(anchor="w", padx=5, pady=(10, 2))
        
        image_frame = ctk.CTkFrame(folder_frame)
        image_frame.pack(fill=tk.X, padx=5, pady=2)
        
        image_entry = ctk.CTkEntry(image_frame, textvariable=self.image_folder)
        image_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        image_btn = ctk.CTkButton(image_frame, text="Browse", command=self.browse_image_folder, width=80)
        image_btn.pack(side=tk.RIGHT, padx=5)
        
        # Output Folder
        output_label = ctk.CTkLabel(folder_frame, text="📤 Output Folder:")
        output_label.pack(anchor="w", padx=5, pady=(10, 2))
        
        output_frame = ctk.CTkFrame(folder_frame)
        output_frame.pack(fill=tk.X, padx=5, pady=2)
        
        output_entry = ctk.CTkEntry(output_frame, textvariable=self.output_folder)
        output_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        output_btn = ctk.CTkButton(output_frame, text="Browse", command=self.browse_output_folder, width=80)
        output_btn.pack(side=tk.RIGHT, padx=5)
        
        # Separator
        separator = ttk.Separator(self.left_panel, orient="horizontal")
        separator.pack(fill=tk.X, padx=10, pady=10)
        
        # Font Settings
        font_title = ctk.CTkLabel(self.left_panel, text="🔤 Font Settings", font=ctk.CTkFont(size=16, weight="bold"))
        font_title.pack(pady=5, padx=10, anchor="w")
        
        font_frame = ctk.CTkFrame(self.left_panel)
        font_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Font Selection - Diganti dari button menjadi dropdown
        font_label = ctk.CTkLabel(font_frame, text="Font:")
        font_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        
        font_dropdown = ctk.CTkOptionMenu(font_frame, values=self.fonts, variable=self.selected_font, command=self.update_preview)
        font_dropdown.grid(row=0, column=1, padx=5, pady=5, sticky="ew", columnspan=2)
        
        # Tambahkan tombol untuk custom font jika masih diperlukan
        custom_font_btn = ctk.CTkButton(font_frame, text="Custom Font", command=self.select_font, width=100)
        custom_font_btn.grid(row=0, column=3, padx=5, pady=5)
        
        # Font Size
        size_label = ctk.CTkLabel(font_frame, text="Size:")
        size_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        
        size_slider = ctk.CTkSlider(font_frame, from_=20, to=100, variable=self.font_size, command=self.update_preview)
        size_slider.grid(row=1, column=1, padx=5, pady=5, sticky="ew", columnspan=2)
        
        size_value = ctk.CTkLabel(font_frame, textvariable=self.font_size)
        size_value.grid(row=1, column=3, padx=5, pady=5)
        
        # Font Color
        color_label = ctk.CTkLabel(font_frame, text="Color:")
        color_label.grid(row=2, column=0, padx=5, pady=5, sticky="w")
        
        color_btn = ctk.CTkButton(font_frame, text="", width=30, height=30, command=self.select_color)
        color_btn.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        self.color_button = color_btn  # Save reference for updating
        
        # Initial color button
        self.update_color_button()
        
        # Text Effect
        effect_label = ctk.CTkLabel(font_frame, text="Effect:")
        effect_label.grid(row=3, column=0, padx=5, pady=5, sticky="w")
        
        effect_dropdown = ctk.CTkOptionMenu(font_frame, values=self.text_effects, variable=self.text_effect)
        effect_dropdown.grid(row=3, column=1, padx=5, pady=5, sticky="ew", columnspan=3)
        
        # Text Position (new)
        position_label = ctk.CTkLabel(font_frame, text="Position:")
        position_label.grid(row=4, column=0, padx=5, pady=5, sticky="w")
        
        position_dropdown = ctk.CTkOptionMenu(font_frame, values=self.text_positions, variable=self.text_position, command=self.update_preview)
        position_dropdown.grid(row=4, column=1, padx=5, pady=5, sticky="ew", columnspan=3)
        
        # Color Effect (new)
        color_effect_label = ctk.CTkLabel(font_frame, text="Color Effect:")
        color_effect_label.grid(row=5, column=0, padx=5, pady=5, sticky="w")
        
        color_effect_dropdown = ctk.CTkOptionMenu(font_frame, values=self.color_effects, variable=self.color_effect)
        color_effect_dropdown.grid(row=5, column=1, padx=5, pady=5, sticky="ew", columnspan=3)
        
        # Configure grid
        font_frame.columnconfigure(1, weight=1)
        
        # Separator
        separator2 = ttk.Separator(self.left_panel, orient="horizontal")
        separator2.pack(fill=tk.X, padx=10, pady=10)
        
        # Video Settings
        video_title = ctk.CTkLabel(self.left_panel, text="🎥 Video Options", font=ctk.CTkFont(size=16, weight="bold"))
        video_title.pack(pady=5, padx=10, anchor="w")
        
        video_frame = ctk.CTkFrame(self.left_panel)
        video_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Video Ratio
        ratio_label = ctk.CTkLabel(video_frame, text="Ratio:")
        ratio_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        
        ratio_landscape = ctk.CTkRadioButton(video_frame, text="Landscape (16:9)", variable=self.video_ratio, 
                                           value="landscape", command=self.update_preview)
        ratio_landscape.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        
        ratio_portrait = ctk.CTkRadioButton(video_frame, text="Portrait (9:16)", variable=self.video_ratio, 
                                          value="portrait", command=self.update_preview)
        ratio_portrait.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        
        # Video Quality
        quality_label = ctk.CTkLabel(video_frame, text="Quality:")
        quality_label.grid(row=2, column=0, padx=5, pady=5, sticky="w")
        
        quality_dropdown = ctk.CTkOptionMenu(video_frame, values=["720p", "1080p", "4K"], variable=self.video_quality)
        quality_dropdown.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        
        # Language
        lang_label = ctk.CTkLabel(video_frame, text="Language:")
        lang_label.grid(row=3, column=0, padx=5, pady=5, sticky="w")
        
        lang_dropdown = ctk.CTkOptionMenu(video_frame, values=self.languages, variable=self.language)
        lang_dropdown.grid(row=3, column=1, padx=5, pady=5, sticky="ew")
        
        # Whisper Model
        model_label = ctk.CTkLabel(video_frame, text="Whisper Model:")
        model_label.grid(row=4, column=0, padx=5, pady=5, sticky="w")
        
        model_dropdown = ctk.CTkOptionMenu(video_frame, values=self.whisper_models, variable=self.whisper_model)
        model_dropdown.grid(row=4, column=1, padx=5, pady=5, sticky="ew")
        
        # Configure grid
        video_frame.columnconfigure(1, weight=1)
        
    def create_preview_area(self):
        """Create preview area in the right panel"""
        preview_frame = ctk.CTkFrame(self.right_panel)
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        preview_label = ctk.CTkLabel(preview_frame, text="📺 Preview", font=ctk.CTkFont(size=16, weight="bold"))
        preview_label.pack(pady=5, anchor="w")
        
        # Preview canvas
        preview_canvas = tk.Canvas(preview_frame, bg="#1A1A1A", highlightthickness=0)
        preview_canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Preview text
        preview_canvas.create_text(
            250, 150, 
            text="Preview will appear here", 
            fill="white", 
            font=("Arial", 14)
        )
        
        self.preview_canvas = preview_canvas
        
    def create_log_area(self):
        """Create log area in the right panel"""
        log_frame = ctk.CTkFrame(self.right_panel)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        log_label = ctk.CTkLabel(log_frame, text="📝 Log", font=ctk.CTkFont(size=16, weight="bold"))
        log_label.pack(pady=5, anchor="w")
        
        # Log text
        log_text = ctk.CTkTextbox(log_frame, height=200)
        log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Set initial text
        log_text.insert("1.0", "Welcome to Auto Lyric Video Generator! 🎵\n")
        log_text.insert("end", "Select audio and background folders to start.\n")
        log_text.configure(state="disabled")
        
        self.log_text = log_text
        
    def create_buttons(self):
        """Create action buttons"""
        button_frame = ctk.CTkFrame(self.main_frame)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Generate button
        generate_btn = ctk.CTkButton(
            button_frame, 
            text="🚀 GENERATE VIDEO", 
            command=self.start_generation,
            height=40,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color="#28a745"
        )
        generate_btn.pack(side=tk.RIGHT, padx=10)
        
        # Open output folder button
        open_output_btn = ctk.CTkButton(
            button_frame, 
            text="📂 Open Output Folder", 
            command=self.open_output_folder,
            height=40
        )
        open_output_btn.pack(side=tk.RIGHT, padx=10)
        
    def log(self, message):
        """Add message to log"""
        self.log_text.configure(state="normal")
        self.log_text.insert("end", f"[{time.strftime('%H:%M:%S')}] {message}\n")
        self.log_text.see("end")
        self.log_text.configure(state="disabled")
        self.update()
        
    def browse_audio_folder(self):
        """Browse for audio folder"""
        folder = filedialog.askdirectory(title="Select Audio Folder")
        if folder:
            self.audio_folder.set(folder)
            self.log(f"Audio folder set: {folder}")
            
    def browse_image_folder(self):
        """Browse for image folder"""
        folder = filedialog.askdirectory(title="Select Background Image Folder")
        if folder:
            self.image_folder.set(folder)
            self.log(f"Image folder set: {folder}")
            self.show_random_background()
            
    def browse_output_folder(self):
        """Browse for output folder"""
        folder = filedialog.askdirectory(title="Select Output Folder")
        if folder:
            self.output_folder.set(folder)
            self.log(f"Output folder set: {folder}")
            
    def open_output_folder(self):
        """Open output folder in file explorer"""
        output_folder = self.output_folder.get()
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
            
        # Platform-specific folder opening
        if sys.platform == 'win32':
            os.startfile(output_folder)
        elif sys.platform == 'darwin':  # macOS
            os.system(f'open "{output_folder}"')
        else:  # Linux
            os.system(f'xdg-open "{output_folder}"')
            
    def select_font(self):
        """Open font selector"""
        file_path = filedialog.askopenfilename(
            title="Select Font File",
            filetypes=[("Font Files", "*.ttf *.otf"), ("All Files", "*.*")]
        )
        if file_path:
            self.font_path = file_path
            font_name = os.path.basename(file_path)
            self.selected_font.set(font_name)
            self.log(f"Font selected: {font_name}")
            
    def select_color(self):
        """Open color picker"""
        color = colorchooser.askcolor(self.font_color.get())
        if color[1]:
            self.font_color.set(color[1])
            self.update_color_button()
            self.log(f"Font color set: {color[1]}")
            self.update_preview()  # Update preview setelah warna berubah
            
    def update_color_button(self):
        """Update the color button appearance"""
        color = self.font_color.get()
        self.color_button.configure(fg_color=color)
        
        # Set text color based on brightness
        r, g, b = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)
        brightness = (r * 299 + g * 587 + b * 114) / 1000
        
        if brightness > 128:
            text_color = "black"
        else:
            text_color = "white"
            
        self.color_button.configure(text_color=text_color)
        
    def update_preview(self, *args):
        """Update preview berdasarkan setting terbaru"""
        # Jika tidak ada background folder yang dipilih, tidak perlu update
        if not self.image_folder.get() or not os.path.exists(self.image_folder.get()):
            return
            
        self.show_random_background()
        
    def show_random_background(self):
        """Show a random background from the selected folder"""
        image_folder = self.image_folder.get()
        if not image_folder or not os.path.exists(image_folder):
            return
            
        # Get list of images
        valid_extensions = ('.jpg', '.jpeg', '.png', '.bmp')
        images = [f for f in os.listdir(image_folder) 
                if f.lower().endswith(valid_extensions)]
                
        if not images:
            self.log("No images found in the selected folder")
            return
            
        # Choose a random image
        random_image = random.choice(images)
        image_path = os.path.join(image_folder, random_image)
        
        try:
            # Load original image
            original_img = Image.open(image_path)
            original_width, original_height = original_img.size
            
            # Tentukan dimensi canvas berdasarkan ratio
            canvas_width = self.preview_canvas.winfo_width()
            canvas_height = self.preview_canvas.winfo_height()
            
            if canvas_width <= 1 or canvas_height <= 1:
                # Canvas belum terukur, gunakan default
                canvas_width, canvas_height = 500, 300
            
            # Padding untuk memberi ruang di sekitar preview
            padding = 20
            display_area_width = canvas_width - (padding * 2)
            display_area_height = canvas_height - (padding * 2)
            
            # Tentukan rasio target berdasarkan pilihan mode
            if self.video_ratio.get() == "portrait":
                # Portrait (9:16)
                target_ratio = 9 / 16
            else:
                # Landscape (16:9)
                target_ratio = 16 / 9
            
            # Hitung dimensi preview berdasarkan rasio
            if target_ratio < 1:  # Portrait mode
                # Batasi tinggi ke display area height
                display_height = display_area_height
                display_width = int(display_height * target_ratio)
                
                # Pastikan lebar juga tidak melebihi area
                if display_width > display_area_width:
                    display_width = display_area_width
                    display_height = int(display_width / target_ratio)
            else:  # Landscape mode
                # Batasi lebar ke display area width
                display_width = display_area_width
                display_height = int(display_width / target_ratio)
                
                # Pastikan tinggi juga tidak melebihi area
                if display_height > display_area_height:
                    display_height = display_area_height
                    display_width = int(display_height * target_ratio)
            
            # Crop dan resize gambar asli untuk mempertahankan rasio aspek
            # Tentukan rasio gambar asli
            original_ratio = original_width / original_height
            
            # Tentukan area crop pada gambar asli
            if original_ratio > target_ratio:  # Gambar lebih lebar dari target
                # Crop dari sisi kiri dan kanan
                new_original_width = int(original_height * target_ratio)
                left = (original_width - new_original_width) // 2
                img = original_img.crop((left, 0, left + new_original_width, original_height))
            else:  # Gambar lebih tinggi dari target
                # Crop dari atas dan bawah
                new_original_height = int(original_width / target_ratio)
                top = (original_height - new_original_height) // 2
                img = original_img.crop((0, top, original_width, top + new_original_height))
            
            # Resize gambar ke dimensi display
            img = img.resize((display_width, display_height), Image.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            
            # Clear canvas dan tampilkan image
            self.preview_canvas.delete("all")
            
            # Posisikan gambar di tengah canvas
            x_pos = canvas_width // 2
            y_pos = canvas_height // 2
            
            self.preview_canvas.create_image(x_pos, y_pos, image=photo)
            
            # Tambahkan semi-transparan background untuk teks agar lebih terbaca
            text_bg_width = display_width
            text_bg_height = int(display_height * 0.2)  # 20% dari tinggi display
            
            # Posisikan berdasarkan text_position yang dipilih
            text_position = self.text_position.get()
            
            if text_position == "top":
                text_y = y_pos - (display_height // 2) + text_bg_height + 10  # 10px dari atas
            elif text_position == "bottom":
                text_y = y_pos + (display_height // 2) - text_bg_height - 10  # 10px dari bawah
            else:  # center
                text_y = y_pos  # Tengah
            
            # Buat background semi-transparan untuk teks
            self.preview_canvas.create_rectangle(
                x_pos - text_bg_width//2,
                text_y - text_bg_height//2,
                x_pos + text_bg_width//2,
                text_y + text_bg_height//2,
                fill="black", 
                outline="",
                stipple="gray50"  # Efek semi-transparan
            )
            
            # Tambahkan contoh teks untuk menunjukkan font & warna
            font_name = self.selected_font.get()
            font_size = self.font_size.get()
            font_color = self.font_color.get()
            
            # Hitung ukuran font yang proporsional dengan area preview
            adjusted_font_size = int(min(display_width, display_height) / 12)
            
            # Tampilkan juga efek warna yang dipilih
            color_effect_text = ""
            if self.color_effect.get() != "none":
                color_effect_text = f" - {self.color_effect.get()} effect"
                
            # Tambahkan teks contoh
            self.preview_canvas.create_text(
                x_pos,
                text_y,
                text=f"Example Lyric Text{color_effect_text}",
                fill=font_color,
                font=(font_name, adjusted_font_size),
                width=text_bg_width - 20  # Batasi lebar teks agar tidak keluar dari area
            )
            
            # Simpan referensi untuk mencegah garbage collection
            self.preview_canvas.image = photo
            
            # Tambahkan border outline untuk menunjukkan dimensi aktual video
            border_color = "#FF5733"  # Orange outline
            outline_width = 2
            
            x1 = x_pos - display_width//2
            y1 = y_pos - display_height//2
            x2 = x_pos + display_width//2
            y2 = y_pos + display_height//2
            
            self.preview_canvas.create_rectangle(x1, y1, x2, y2, outline=border_color, width=outline_width)
            
            # Tampilkan juga indikator posisi teks
            position_indicator_color = "#00FFFF"  # Cyan
            text_position_text = f"Text position: {text_position}"
            self.preview_canvas.create_text(
                x_pos, y1 + 20,
                text=text_position_text,
                fill=position_indicator_color,
                font=("Arial", 10, "bold")
            )
            
            # Tambahkan label yang menunjukkan rasio
            ratio_text = "9:16 Portrait" if self.video_ratio.get() == "portrait" else "16:9 Landscape"
            self.preview_canvas.create_text(
                x_pos, y1 - 10,
                text=ratio_text,
                fill=border_color,
                font=("Arial", 10, "bold")
            )
            
            self.log(f"Showing background: {random_image} ({ratio_text})")
            
        except Exception as e:
            self.log(f"Error loading image: {str(e)}")
            import traceback
            traceback.print_exc()
            
    def start_generation(self):
        """Start the video generation process"""
        # Validasi input
        if not self.audio_folder.get():
            self.log("⚠️ Please select an audio folder")
            return
            
        if not self.image_folder.get():
            self.log("⚠️ Please select a background image folder")
            return
            
        # Create output folder if not exists
        output_folder = self.output_folder.get()
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
            
        # Start generation in separate thread
        self.log("🎬 Starting video generation process...")
        
        # Setup button state
        generate_button = self.main_frame.winfo_children()[-1].winfo_children()[0]
        generate_button.configure(state="disabled", text="⏳ Processing...")
        
        # Run in thread
        threading.Thread(target=self.generate_videos, daemon=True).start()
        
    def generate_videos(self):
        """Generate lyric videos (run in separate thread)"""
        try:
            # Update audio processor settings
            self.audio_processor = AudioProcessor(model_size=self.whisper_model.get())
            
            # Process audio files
            self.log(f"📝 Transcribing audio files with Whisper model: {self.whisper_model.get()}")
            self.log("💡 This may take a while depending on the audio files...")
            
            lyrics_dict = self.audio_processor.process_audio_directory(
                self.audio_folder.get(),
                language=None if self.language.get() == "auto" else self.language.get()
            )
            
            if not lyrics_dict:
                self.log("❌ No transcription results. Check audio files.")
                return
                
            # Log info tentang hasil transkripsi untuk debugging
            self.log(f"✅ Transcription completed. Found {len(lyrics_dict)} audio file(s) with lyrics.")
            for filename in lyrics_dict.keys():
                self.log(f"  → Transcribed: {filename}")
                
            # Update video generator settings
            self.video_generator = VideoGenerator(
                output_path=self.output_folder.get(),
                background_image_path=self.image_folder.get(),
                font=self.font_path if self.font_path else self.selected_font.get(),
                font_size=self.font_size.get(),
                font_color=self.font_color.get(),
                text_effect=self.text_effect.get(),
                quality=self.video_quality.get(),
                text_position=self.text_position.get(),
                color_effect=self.color_effect.get()
            )
            
            # Tambahkan informasi audio_folder ke video_generator
            self.video_generator.audio_folder = self.audio_folder.get()
            
            # Generate videos
            self.log(f"🎬 Generating {self.video_ratio.get()} videos with {self.text_effect.get()} effect...")
            
            # Log posisi dan efek warna
            self.log(f"📍 Text position: {self.text_position.get()}")
            color_effect_msg = "none" if self.color_effect.get() == "none" else f"{self.color_effect.get()} effect"
            self.log(f"🎨 Color effect: {color_effect_msg}")
            
            # Check file-file audio yang ada di folder audio untuk debugging
            audio_files = []
            for ext in ['.mp3', '.wav', '.flac', '.ogg', '.m4a']:
                audio_files.extend([f for f in os.listdir(self.audio_folder.get()) if f.lower().endswith(ext)])
            self.log(f"📂 Audio files available in folder: {len(audio_files)}")
            for audio_file in audio_files[:5]:  # Tampilkan 5 file pertama saja
                self.log(f"  → {audio_file}")
            if len(audio_files) > 5:
                self.log(f"  → ... and {len(audio_files)-5} more files")
            
            output_videos = self.video_generator.batch_generate(
                lyrics_dict, 
                output_ratio=self.video_ratio.get()
            )
            
            # Show completion
            if output_videos:
                self.log(f"✅ Generated {len(output_videos)} videos!")
                self.log(f"📂 Videos saved to: {self.output_folder.get()}")
            else:
                self.log("❌ No videos were generated. Check logs for errors.")
                
        except Exception as e:
            self.log(f"❌ Error: {str(e)}")
            import traceback
            error_traceback = traceback.format_exc()
            self.log(f"Traceback: {error_traceback}")
        finally:
            # Reset button state
            self.after(0, self.reset_ui)
            
    def reset_ui(self):
        """Reset UI state after processing"""
        generate_button = self.main_frame.winfo_children()[-1].winfo_children()[0]
        generate_button.configure(state="normal", text="🚀 GENERATE VIDEO")
        
if __name__ == "__main__":
    app = LyricVideoApp()
    app.mainloop() 