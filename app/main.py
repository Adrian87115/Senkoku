import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

from gui_components.MainWindow import MainWindow
from gui_components.ConfirmationPanel import ConfirmationPanel, ClickOutsideFilter
from manga_ocr_engine import MangaOCREngine
from gui_components.ScreenSelector import ScreenSelector
from app_settings import AppSettings
from utils import on_image_captured

def main():
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

# The app will not work properly in power saving mode
# After changing translator or shortcut, restart the app

# to do:
# - exe app
# - better furigana
# - make settings icon be next to in label

# if turned on after initially it was off it will crash
# Traceback (most recent call last):
#   File "C:\Users\adria\Desktop\Adrian\projects\Python\Senkoku\app\gui_components\MainWindow.py", line 226, in update_ui
#     self.confirmation_panel.update_text(original = input_text, reading = furigana_in, translation = result)
# AttributeError: 'NoneType' object has no attribute 'update_text'