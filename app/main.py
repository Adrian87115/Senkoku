import sys
from PySide6.QtWidgets import QApplication # type: ignore
import sounddevice as sd # type: ignore
import keyboard

from gui_components.MainWindow import MainWindow
from gui_components.ConfirmationPanel import ConfirmationPanel, ClickOutsideFilter
from ai.kokoro_engine import KokoroEngine
from ai.manga_ocr_engine import MangaOCREngine
from gui_components.ScreenSelector import ScreenSelector, on_image_captured
from app_settings import AppSettings

def main():
    print("Local mode offers moderate experience, Users are encouraged to use online mode when possible.")
    # tts_engine = KokoroEngine(voice = "jf_alpha", lang = "ja")
    # ocr_engine = MangaOCREngine()
    # translator_engine = GoogleTranslatorEngine()
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

    selector = ScreenSelector(hotkey = settings.screen_selector_sc, callback = on_image_captured, app =  app)

    # print("Ready. Press Ctrl+Q to capture screen region.")

    # keyboard.wait()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()