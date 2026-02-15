from googletrans import Translator
import pykakasi
from gtts import gTTS
import sounddevice as sd
import soundfile as sf
import io
import os
from google.cloud import translate_v2 as translate
from google.oauth2 import service_account
import html
import numpy as np

from utils import get_romaji
from logger import log_exceptions

class BaseTranslatorEngine:
    def __init__(self):
        self.kks = pykakasi.kakasi()
    
    def get_romaji(self, text):
        return get_romaji(text)

    def speak(self, text, lang = 'ja'):
        mp3_fp = io.BytesIO()
        tts = gTTS(text, lang = lang)
        tts.write_to_fp(mp3_fp)
        mp3_fp.seek(0)
        data, samplerate = sf.read(mp3_fp, dtype = 'float32')

        # prevents audio glitches on headphones
        silence_duration = 0.2
        num_silent_samples = int(silence_duration * samplerate)
        silence = np.zeros((num_silent_samples, data.shape[1])) if data.ndim > 1 else np.zeros(num_silent_samples)
        data_with_silence = np.concatenate((data, silence))

        sd.play(data_with_silence, samplerate)
        sd.wait()

class FreeGoogleTranslatorEngine(BaseTranslatorEngine):
    def __init__(self):
        print("Initializing Translator Engine...")
        super().__init__()
        self.translator = Translator()
        print("Translator Engine ready.\n")

    def ja_to_en(self, text):
        return self.translator.translate(text, src = 'ja', dest = 'en').text

    def en_to_ja(self, text):
        return self.translator.translate(text, src = 'en', dest = 'ja').text

# official version, requires api key
class OfficialGoogleTranslatorEngine(BaseTranslatorEngine):
    def __init__(self):
        print("Initializing Official Google Cloud Translator Engine...")
        super().__init__()
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.key_path = os.path.abspath(os.path.join(current_dir, "..", "senkoku_api_key.json"))
        self.reconnect()
        print("Official Google Translator Engine ready.\n")

    # after iddleness for some time the api will disconnect, this funciton is meant to reestablish the connection
    @log_exceptions
    def reconnect(self):
        try:
            credentials = service_account.Credentials.from_service_account_file(self.key_path)
            self.translate_client = translate.Client(credentials = credentials)
            print("Google Cloud Connection Refreshed.")
        except Exception as e:
            print(f"Failed to connect to Google Cloud: {e}")
            raise e

    @log_exceptions
    def ja_to_en(self, text):
        raw_translation = self.translate_client.translate(text, source_language = 'ja', target_language = 'en')['translatedText']
        return html.unescape(raw_translation)

    @log_exceptions
    def en_to_ja(self, text):
        raw_translation = self.translate_client.translate(text, source_language = 'en', target_language = 'ja')['translatedText']
        return html.unescape(raw_translation)