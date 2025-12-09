from transformers import M2M100ForConditionalGeneration, M2M100Tokenizer
import re
import pykakasi
import sounddevice as sd
import numpy as np

from ai.kokoro_engine import KokoroEngine

class LocalTranslatorEngine:
    def __init__(self):
        print("Loading offline Japanese <-> English M2M100 model...")
        self.tokenizer = M2M100Tokenizer.from_pretrained("facebook/m2m100_418M")
        self.translator = M2M100ForConditionalGeneration.from_pretrained("facebook/m2m100_418M")
        self.kks = pykakasi.kakasi()
        self.tts_engine = KokoroEngine()
        print("M2M100 model loaded.\n")

    def ja_to_en(self, text):
        self.tokenizer.src_lang = "ja"
        encoded = self.tokenizer(text, return_tensors = "pt")
        generated = self.translator.generate(**encoded, forced_bos_token_id = self.tokenizer.get_lang_id("en"))
        return self.tokenizer.decode(generated[0], skip_special_tokens = True)

    def en_to_ja(self, text):
        self.tokenizer.src_lang = "en"
        encoded = self.tokenizer(text, return_tensors = "pt")
        generated = self.translator.generate(**encoded, forced_bos_token_id = self.tokenizer.get_lang_id("ja"))
        return self.tokenizer.decode(generated[0], skip_special_tokens = True)
    
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
        if lang == 'ja':
            kokoro_lang = 'ja'
        elif lang in ('en', 'en-gb'):
            kokoro_lang = 'en-gb'
        else:
            raise ValueError(f"Unsupported language for TTS: {lang}")

        samples, samplerate = self.tts_engine.tts(text, kokoro_lang)

        if samples is None or len(samples) == 0:
            print("TTS error: no samples generated.")
            return

        samples = np.asarray(samples, dtype = 'float32')
        sd.play(samples, samplerate)
        sd.wait()