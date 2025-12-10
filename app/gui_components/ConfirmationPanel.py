from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt, QObject, QEvent
from PySide6.QtWidgets import QApplication

# confirmation panel is treated as popup, but without this class it will not close when pressed inside MainWindow
class ClickOutsideFilter(QObject):
    def __init__(self, panel):
        super().__init__()
        self.panel = panel

    def eventFilter(self, obj, event):
        if event.type() == QEvent.MouseButtonPress:
            if not self.panel.geometry().contains(event.globalPosition().toPoint()):
                self.panel.hide()
        return False

class ConfirmationPanel(QMainWindow):
    def __init__(self, settings, disable_reading = False, disable_translation = False):
        super().__init__()
        self.settings = settings 

        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_OpaquePaintEvent, True)
        self.setAttribute(Qt.WA_NoSystemBackground, True)

        screen_geometry = QApplication.primaryScreen().geometry()
        self.setGeometry(100, 100, 400, 200)

        self.setStyleSheet("background-color: rgba(50, 50, 50, 200); color: white; font-size: 14px;")

        container = QWidget()
        layout = QVBoxLayout(container)

        self.original_label = QLabel("Original: ")
        self.reading_label = QLabel("Reading: ")
        self.translation_label = QLabel("Translation: ")

        for label in [self.original_label, self.reading_label, self.translation_label]:
            label.setTextInteractionFlags(Qt.TextSelectableByMouse)

        layout.addWidget(self.original_label)

        if not disable_reading:
            layout.addWidget(self.reading_label)

        if not disable_translation:
            layout.addWidget(self.translation_label)

        container.setLayout(layout)
        self.setCentralWidget(container)

        self._drag_active = False
        self._drag_position = None

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_active = True
            self._drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if self._drag_active and event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self._drag_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        self._drag_active = False

    def update_text(self, original = "", reading = "", translation = ""):
        self.original_label.setText(f"Original: {original}")
        self.reading_label.setText(f"Reading: {reading}")
        self.translation_label.setText(f"Translation: {translation}")