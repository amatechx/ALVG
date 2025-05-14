import os
import whisper
import tempfile
from tqdm import tqdm
import datetime
from pydub import AudioSegment

class AudioProcessor:
    """
    Class untuk memproses file audio dan mengekstrak lirik
    """
    
    def __init__(self, model_size="base"):
        """
        Initialize the audio processor
        
        Parameters:
            model_size (str): Ukuran model Whisper ('tiny', 'base', 'small', 'medium', 'large')
        """
        self.model = None
        self.model_size = model_size
        
    def load_model(self):
        """
        Load model Whisper jika belum diload
        """
        if self.model is None:
            print(f"Loading Whisper model '{self.model_size}'...")
            self.model = whisper.load_model(self.model_size)
            print("Model loaded!")
            
    def transcribe_audio(self, audio_path, language=None):
        """
        Transcribe audio file dan return lirik + timestamps
        
        Parameters:
            audio_path (str): Path ke file audio
            language (str): Kode bahasa (opsional, ex: 'id', 'en', 'ja')
            
        Returns:
            list: List of dictionaries dengan format {'text': 'lyric line', 'start': start_time, 'end': end_time}
        """
        self.load_model()
        
        print(f"Transcribing: {os.path.basename(audio_path)}")
        
        # Set language-specific options
        options = {}
        if language:
            options["language"] = language
        
        # Transcribe audio file
        result = self.model.transcribe(audio_path, **options)
        
        # Extract segments with timestamps
        segments = result["segments"]
        lyrics = []
        
        for segment in segments:
            lyrics.append({
                'text': segment['text'].strip(),
                'start': segment['start'],
                'end': segment['end']
            })
            
        return lyrics
        
    def format_lyrics(self, lyrics, formatting="srt"):
        """
        Format lirik ke format yang diinginkan
        
        Parameters:
            lyrics (list): List of lyric dictionaries
            formatting (str): Format output ('srt', 'txt', 'json')
            
        Returns:
            str or dict: Formatted lyrics
        """
        if formatting == "srt":
            srt_content = ""
            for i, lyric in enumerate(lyrics):
                start_time = str(datetime.timedelta(seconds=lyric['start'])).replace(".", ",")[:11]
                end_time = str(datetime.timedelta(seconds=lyric['end'])).replace(".", ",")[:11]
                srt_content += f"{i+1}\n{start_time} --> {end_time}\n{lyric['text']}\n\n"
            return srt_content
            
        elif formatting == "txt":
            return "\n".join([lyric['text'] for lyric in lyrics])
            
        elif formatting == "json":
            return lyrics
            
        else:
            raise ValueError(f"Unsupported format: {formatting}")
            
    def process_audio_directory(self, directory_path, language=None):
        """
        Process semua file audio dalam direktori dan return hasil transkrip
        
        Parameters:
            directory_path (str): Path ke direktori audio
            language (str): Kode bahasa (opsional)
            
        Returns:
            dict: Dictionary dengan format {filename: lyrics}
        """
        results = {}
        
        # List semua file audio
        audio_files = [f for f in os.listdir(directory_path) 
                      if f.lower().endswith(('.mp3', '.wav', '.flac', '.ogg', '.m4a'))]
        
        if not audio_files:
            print(f"No audio files found in {directory_path}")
            return results
            
        print(f"Found {len(audio_files)} audio files")
        print(f"Audio files: {', '.join(audio_files[:5])} {'and more...' if len(audio_files) > 5 else ''}")
        
        # Proses tiap file
        for audio_file in tqdm(audio_files, desc="Processing audio files"):
            audio_path = os.path.join(directory_path, audio_file)
            
            try:
                lyrics = self.transcribe_audio(audio_path, language)
                
                # Simpan hasil transkrip dengan nama file tanpa ekstensi
                # Tetapi pastikan nama file mudah dicocokkan nanti
                filename = os.path.splitext(audio_file)[0]
                print(f"Adding to results with key: {filename}")
                results[filename] = lyrics
                
                # Save transcript to file
                with open(f"{os.path.splitext(audio_path)[0]}.srt", "w", encoding="utf-8") as f:
                    f.write(self.format_lyrics(lyrics, formatting="srt"))
                    
                print(f"✓ Transcribed: {filename}")
                
            except Exception as e:
                print(f"✗ Error processing {audio_file}: {str(e)}")
                import traceback
                traceback.print_exc()
                
        print(f"Total results processed: {len(results)} files")
        print(f"Result keys: {list(results.keys())}")
        return results
        
    @staticmethod
    def get_audio_duration(audio_path):
        """
        Get durasi audio file
        
        Parameters:
            audio_path (str): Path ke file audio
            
        Returns:
            float: Durasi audio dalam detik
        """
        try:
            audio = AudioSegment.from_file(audio_path)
            return len(audio) / 1000.0  # Convert milliseconds to seconds
        except Exception as e:
            print(f"Error getting duration: {str(e)}")
            return None 