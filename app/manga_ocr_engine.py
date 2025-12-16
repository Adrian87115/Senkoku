from manga_ocr import MangaOcr
import re
from PIL import Image

from logger import log_exceptions

class MangaOCREngine():
    def __init__(self):
        print("Loading Manga OCR model...")
        self.manga_ocr = MangaOcr()

        # model must run on cpu, or it may crash on some devices when they are not plugged in or are in power saving mode
        self.manga_ocr.model.to("cpu")
        print("Manga OCR initialized.\n")
    
    @log_exceptions
    def read_from_image(self, img):
        if not self._is_valid_image(img):
            return ""
        
        text = self.manga_ocr(img)
        text = self.clean_text(text)

        if not self.is_valid_text(text):
            return ""
        
        return text
    
    # prevent crashing
    def _is_valid_image(self, img):
        # prevents channel ambiguity
        if img.size[0] <= 3 or img.size[1] <= 3:
            return False
        
        # RGB and non empty
        if isinstance(img, Image.Image):
            return img.mode == "RGB" and img.width > 0 and img.height > 0
        
        return False

    def clean_text(self, text):
        text = text.strip()
        return text

    # prevent sending weird texts
    def is_valid_text(self, text):
        text = text.strip()
        
        if not text:
            return False
        
        jp_chars = re.findall(r"[\u3040-\u30FF\u4E00-\u9FFF]", text)

        if len(jp_chars) == 0:
            return False

        if re.fullmatch(r"[^a-zA-Z0-9\u3040-\u30FF\u4E00-\u9FFF]+", text):
            return False

        return True