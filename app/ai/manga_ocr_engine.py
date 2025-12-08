from manga_ocr import MangaOcr # type: ignore

class MangaOCREngine():
    def __init__(self):
        print("Loading Manga OCR model...")
        self.manga_ocr = MangaOcr()
        print("Manga OCR initialized.\n")
        
    def read_from_image(self, img):
        text = self.manga_ocr(img)
        return text