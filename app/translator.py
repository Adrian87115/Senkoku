from googletrans import Translator
import pykakasi
from gtts import gTTS
import sounddevice as sd
import soundfile as sf
import io
import re

class GoogleTranslatorEngine:
    def __init__(self):
        print("Initializing Google Translator Engine...")
        self.translator = Translator()
        self.kks = pykakasi.kakasi()
        print("Google Translator Engine ready.\n")

    def ja_to_en(self, text):
        result = self.translator.translate(text, src = 'ja', dest = 'en')
        return result.text

    def en_to_ja(self, text):
        result = self.translator.translate(text, src = 'en', dest = 'ja')
        return result.text

    def get_furigana(self, text, romanize = True):
        output = []
        japanese_regex = re.compile(r'[\u4E00-\u9FFF\u3040-\u309F\u30A0-\u30FF]+')
        pos = 0
        for match in japanese_regex.finditer(text):
            start, end = match.span()
            if start > pos:
                non_jap = text[pos:start]
                output.append(f" {non_jap} " if not non_jap.isspace() else non_jap)
            japanese_chunk = text[start:end]
            converted = self.kks.convert(japanese_chunk)
            reading = " ".join([w['hepburn'] if romanize else w['reading'] for w in converted])
            output.append(reading)
            pos = end
        if pos < len(text):
            non_jap = text[pos:]
            output.append(f" {non_jap} " if not non_jap.isspace() else non_jap)
        return re.sub(r'\s+', ' ', "".join(output)).strip()

    def speak(self, text, lang = 'ja'):
        mp3_fp = io.BytesIO()
        tts = gTTS(text, lang = lang)
        tts.write_to_fp(mp3_fp)
        mp3_fp.seek(0)
        data, samplerate = sf.read(mp3_fp, dtype = 'float32')
        sd.play(data, samplerate)
        sd.wait()