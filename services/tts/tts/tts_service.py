import io
import wave
from pathlib import Path

from piper import PiperVoice

VOICE_NAME = "en_US-lessac-medium"
VOICE_DIR = "voices"

VOICE_PATH = Path(VOICE_DIR, f"{VOICE_NAME}.onnx")

class PiperTTS:
    def __init__(self):
        self.voice = PiperVoice.load(VOICE_PATH)
    
    def to_speech(self, text: str):
        buf = io.BytesIO()

        with wave.open(buf, "wb") as wav_writer:
            wav_writer.setnchannels(1)
            wav_writer.setsampwidth(2)
            wav_writer.setframerate(22050)

            self.voice.synthesize_wav(text, wav_writer)
        return buf.getvalue()

tts_model = PiperTTS()