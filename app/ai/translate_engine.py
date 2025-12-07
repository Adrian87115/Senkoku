from transformers import MarianMTModel, MarianTokenizer

class MarianEngine:
    def __init__(self):
        print("Loading Japanese <-> English translation models from local...")

        self.tokenizer_ja_en = MarianTokenizer.from_pretrained("models/translator/opus-mt-jap-en")
        self.model_ja_en = MarianMTModel.from_pretrained("models/translator/opus-mt-jap-en")

        self.tokenizer_en_ja = MarianTokenizer.from_pretrained("models/translator/opus-mt-en-jap")
        self.model_en_ja = MarianMTModel.from_pretrained("models/translator/opus-mt-en-jap")

        print("Translator models loaded from local.\n")

    def ja_to_en(self, text):
        inputs = self.tokenizer_ja_en(text, return_tensors="pt")
        translated = self.model_ja_en.generate(**inputs, max_length=128, num_beams=5)
        return self.tokenizer_ja_en.decode(translated[0], skip_special_tokens=True)

    def en_to_ja(self, text):
        inputs = self.tokenizer_en_ja(text, return_tensors="pt")
        translated = self.model_en_ja.generate(**inputs, max_length=128, num_beams=5)
        return self.tokenizer_en_ja.decode(translated[0], skip_special_tokens=True)
