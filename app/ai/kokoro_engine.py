from kokoro_tts import Kokoro, chunk_text, process_chunk_sequential
import numpy as np

class KokoroEngine:
    def __init__(self,
                 model_path = "ai/models/kokoro_tts/kokoro-v1.0.onnx",
                 voices_path = "ai/models/kokoro_tts/voices-v1.0.bin",
                 speed = 1.0,
                 debug = False):
        
        print("Loading Kokoro model...")
        self.kokoro = Kokoro(model_path, voices_path)
        print("Kokoro initialized.\n")
        self.speed = speed
        self.debug = debug

    def tts(self, text, lang):
        chunks = chunk_text(text, initial_chunk_size = 2000)
        all_samples = []
        sample_rate = None
        
        if lang == "ja":
            for chunk in chunks:
                samples, sr = process_chunk_sequential(chunk,
                                                       self.kokoro,
                                                       "jf_alpha",
                                                       self.speed,
                                                       "ja",
                                                       retry_count = 0,
                                                       debug = self.debug)
        
        elif lang == "en-gb":
            for chunk in chunks:
                samples, sr = process_chunk_sequential(chunk,
                                                       self.kokoro,
                                                       "bf_alice",
                                                       self.speed,
                                                       "en-gb",
                                                       retry_count = 0,
                                                       debug = self.debug)
            
        if samples is not None:
            if sample_rate is None:
                sample_rate = sr
            all_samples.extend(samples)

        return np.array(all_samples, dtype = "float32"), sample_rate