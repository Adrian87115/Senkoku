import sys
from PySide6.QtWidgets import QApplication # type: ignore
import sounddevice as sd # type: ignore
import keyboard

from gui_components.MainWindow import MainWindow
from gui_components.ConfirmationPanel import ConfirmationPanel, ClickOutsideFilter
from ai.kokoro_engine import KokoroEngine
from ai.manga_ocr_engine import MangaOCREngine
from gui_components.ScreenSelector import ScreenSelector
from app_settings import AppSettings
from utils import on_image_captured

def main():
    print("Local mode offers moderate experience, Users are encouraged to use online mode when possible.")
    # tts_engine = KokoroEngine(voice = "jf_alpha", lang = "ja")
    ocr_engine = MangaOCREngine()
    settings = AppSettings()
    app = QApplication(sys.argv)
    window = MainWindow(settings)
    window.show()
    # panel = ConfirmationPanel()

    # panel.show()

    # filter = ClickOutsideFilter(panel)
    # app.installEventFilter(filter)

    # panel.update_text(original = "こんにちは",
    #                     reading = "kon'nichiwa",
    #                     translation = "Hello")

    screen_selector = ScreenSelector(callback = lambda img: on_image_captured(img, window, ocr_engine), app = app)
    sys.exit(app.exec())

if __name__ == "__main__":
    main()