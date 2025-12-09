import sys
from PySide6.QtWidgets import QApplication # type: ignore
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon

from gui_components.MainWindow import MainWindow
from gui_components.ConfirmationPanel import ConfirmationPanel, ClickOutsideFilter
from ai.kokoro_engine import KokoroEngine
from ai.manga_ocr_engine import MangaOCREngine
from gui_components.ScreenSelector import ScreenSelector
from app_settings import AppSettings
from utils import on_image_captured


def main():
    print("Local mode offers moderate experience, Users are encouraged to use online mode when possible.")
    ocr_engine = MangaOCREngine()
   
    settings = AppSettings()
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

# The app will not work properly in power saver mode