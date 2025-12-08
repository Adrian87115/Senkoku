import keyboard
import mss
from PIL import Image
import numpy as np
from PySide6.QtWidgets import QApplication, QWidget
from PySide6.QtGui import QPainter, QColor, QPen, QGuiApplication, QImage
from PySide6.QtCore import Qt, QRect, Signal, QObject

class HotkeyBridge(QObject):
    trigger = Signal()

class ScreenSelector(QWidget):
    def __init__(self, hotkey = "ctrl+q", callback = None, app: QApplication = None):
        super().__init__()
        self.hotkey = hotkey
        self.callback = callback
        self.app = app or QApplication.instance()

        if self.app is None:
            raise RuntimeError("ScreenSelector requires an existing QApplication")

        self.start = None
        self.end = None

        # bridge between keyboard thread and main thread
        self.bridge = HotkeyBridge()
        self.bridge.trigger.connect(self.start_selection)

        # register global hotkey
        keyboard.add_hotkey(self.hotkey, self._hotkey_pressed)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.cancel_selection()

    def _hotkey_pressed(self):
        self.bridge.trigger.emit()
    
    def start_selection(self):
        self._prepare_overlay()
        self.show()
        self.raise_()
        self.activateWindow()

    def _prepare_overlay(self):
        self.setWindowTitle("Select Area")
        self.setWindowOpacity(0.3)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool) # prevents focus problems
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.showFullScreen()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(0, 0, 0, 100))

        if self.start and self.end:
            painter.setPen(QPen(QColor("red"), 2))
            painter.drawRect(QRect(self.start, self.end))

    def mousePressEvent(self, event):
        if event.button() == Qt.RightButton:
            self.cancel_selection()
            return

        self.start = event.pos()
        self.end = self.start
        self.update()

    def mouseMoveEvent(self, event):
        self.end = event.pos()
        self.update()

    def mouseReleaseEvent(self, event):
        self.end = event.pos()
        self.update()
        global_start = self.mapToGlobal(self.start)
        global_end = self.mapToGlobal(self.end)
        global_rect = QRect(global_start, global_end).normalized()
        screen = self.screen()
        scale = screen.devicePixelRatio()

        x = int(global_rect.left() * scale)
        y = int(global_rect.top() * scale)
        w = int(global_rect.width() * scale)
        h = int(global_rect.height() * scale)
        w = max(1, w)
        h = max(1, h)

        rect = {"left": x, "top": y, "width": w, "height": h}
        
        # hide overlay before capturing the image
        self.hide() 
        img = self.capture_rect(rect)
        self.close() 
        self.copy_to_clipboard(img)

        if self.callback:
            self.callback(img)

        self.start = None
        self.end = None

    def capture_rect(self, rect):
        with mss.mss() as sct:
            grab = sct.grab(rect)

        return Image.frombytes("RGB", grab.size, grab.rgb)

    def copy_to_clipboard(self, pil_img):
        arr = np.array(pil_img)
        h, w, ch = arr.shape
        bytes_per_line = ch * w
        qimg = QImage(arr.data, w, h, bytes_per_line, QImage.Format_RGB888)
        clipboard = QGuiApplication.clipboard()
        clipboard.setImage(qimg)

    def cancel_selection(self):
        self.start = None
        self.end = None
        self.hide()
        self.close()