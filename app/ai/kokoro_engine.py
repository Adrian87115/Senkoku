from kokoro_tts import Kokoro, chunk_text, process_chunk_sequential
import numpy as np # type: ignore

class KokoroEngine:
    def __init__(self,
                 model_path = "models/kokoro_tts/kokoro-v1.0.onnx",
                 voices_path = "models/kokoro_tts/voices-v1.0.bin",
                 voice = "jf_alpha",
                 speed = 1.0,
                 lang = "ja",
                 debug = False):
        
        print("Loading Kokoro model...")
        self.kokoro = Kokoro(model_path, voices_path)
        print("Kokoro initialized.\n")

        self.voice = voice
        self.speed = speed
        self.lang = lang
        self.debug = debug

    def tts(self, text):
        chunks = chunk_text(text, initial_chunk_size = 2000)
        
        all_samples = []
        sample_rate = None
        
        for chunk in chunks:
            samples, sr = process_chunk_sequential(chunk,
                                                   self.kokoro,
                                                   self.voice,
                                                   self.speed,
                                                   self.lang,
                                                   retry_count = 0,
                                                   debug = self.debug)
            
            if samples is not None:
                if sample_rate is None:
                    sample_rate = sr
                all_samples.extend(samples)

        return np.array(all_samples, dtype = "float32"), sample_rate