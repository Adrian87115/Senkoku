from manga_ocr import MangaOcr # type: ignore
from pathlib import Path

class MangaOCREngine():
    def __init__(self):
        print("Loading Manga OCR model...")
        self.manga_ocr = MangaOcr()
        print("Manga OCR initialized.\n")
        
    def read_from_image(self, image_path):
        image_path = Path(image_path)

        if not image_path.exists():
            raise FileNotFoundError(f"Image not found.")
        
        text = self.manga_ocr(image_path)
        return text