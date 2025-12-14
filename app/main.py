import sys
from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import Qt
import os

from gui_components.MainWindow import MainWindow
from gui_components.ConfirmationPanel import ConfirmationPanel, ClickOutsideFilter
from manga_ocr_engine import MangaOCREngine
from gui_components.ScreenSelector import ScreenSelector
from app_settings import AppSettings
from utils import on_image_captured

def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    key_path = os.path.abspath(os.path.join(current_dir, "..", "senkoku_api_key.json"))
    settings = AppSettings()
    if settings.official_online and not os.path.exists(key_path):
        settings.disable_official_online()
        app = QApplication(sys.argv)
        QMessageBox.critical(None, 
                             "Missing Requirements",
                             "Google Cloud API key was not found.\n"
                             "Official Online mode has been disabled.\n"
                             "Please restart the application.\n"
                             "To use Google Translate please add senkoku_api_key.json file.")
        sys.exit(1)

    ocr_engine = MangaOCREngine()
    app = QApplication(sys.argv)

    panel = ConfirmationPanel(settings)
    panel.setWindowFlags(Qt.Popup)
    window = MainWindow(settings, panel)
    window.show()

    filter = ClickOutsideFilter(panel)
    app.installEventFilter(filter)

    screen_selector = ScreenSelector(settings, callback = lambda img: on_image_captured(img, window, ocr_engine), app = app)
    sys.exit(app.exec())

if __name__ == "__main__":
    main()

# users must provide api file on their own

# pyinstaller Senkoku.spec to run