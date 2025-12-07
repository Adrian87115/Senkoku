import keyboard
import mss
from PIL import Image
import numpy as np

from PySide6.QtWidgets import QApplication, QWidget
from PySide6.QtGui import QPainter, QColor, QPen, QGuiApplication, QImage
from PySide6.QtCore import Qt, QRect, Signal, QObject


class HotkeyBridge(QObject):
    trigger = Signal()   # signal to be emitted from keyboard thread


class ScreenSelector(QWidget):
    def __init__(self, hotkey="ctrl+q", callback=None, app: QApplication = None):
        super().__init__()

        self.hotkey = hotkey
        self.callback = callback
        self.app = app or QApplication.instance()
        if self.app is None:
            raise RuntimeError("ScreenSelector requires an existing QApplication")

        self.start = None
        self.end = None

        # bridge between keyboard thread → Qt main thread
        self.bridge = HotkeyBridge()
        self.bridge.trigger.connect(self.start_selection)

        # Register global hotkey
        keyboard.add_hotkey(self.hotkey, self._hotkey_pressed)
        print(f"[ScreenSelector] Hotkey '{self.hotkey}' registered. Press it to capture screen.")

    # ---------------------------
    # Hotkey called from thread → forward to Qt
    # ---------------------------
    def _hotkey_pressed(self):
        # Emit Qt signal safely (thread-safe)
        self.bridge.trigger.emit()

    # ---------------------------
    # Overlay UI
    # ---------------------------
    def start_selection(self):
        print("[ScreenSelector] Starting selection overlay...")

        self._prepare_overlay()
        self.show()
        self.raise_()
        self.activateWindow()

    def _prepare_overlay(self):
        self.setWindowTitle("Select Area")
        self.setWindowOpacity(0.3)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint |
                            Qt.Tool)      # prevents focus problems
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.showFullScreen()

    # ---------------------------
    # Mouse Events
    # ---------------------------
    def paintEvent(self, event):
        painter = QPainter(self)
        
        # Draw dimmed overlay background
        painter.fillRect(self.rect(), QColor(0, 0, 0, 100))   # <── Add this

        # Draw selection rectangle
        if self.start and self.end:
            painter.setPen(QPen(QColor("red"), 2))
            painter.drawRect(QRect(self.start, self.end))

    def mousePressEvent(self, event):
        self.start = event.pos()
        self.end = self.start
        self.update()

    def mouseMoveEvent(self, event):
        self.end = event.pos()
        self.update()

    # offcentered
    def mouseReleaseEvent(self, event):
        self.end = event.pos()
        self.update()

        # Get QRect in global widget coordinates
        global_start = self.mapToGlobal(self.start)
        global_end = self.mapToGlobal(self.end)
        
        # Create a normalized QRect from the two points
        global_rect = QRect(global_start, global_end).normalized()

        # Get current screen's device pixel ratio
        screen = self.screen()  # QScreen
        scale = screen.devicePixelRatio()

        # Convert normalized QRect to physical pixels (int required for mss)
        x = int(global_rect.left() * scale)
        y = int(global_rect.top() * scale)
        w = int(global_rect.width() * scale)
        h = int(global_rect.height() * scale)
        
        # Ensure minimum size (optional, but good practice)
        w = max(1, w)
        h = max(1, h)

        rect = {"left": x, "top": y, "width": w, "height": h}
        
        # --- FIX 1: Temporarily hide the overlay before capture ---
        self.hide() 
        # ---------------------------------------------------------

        img = self.capture_rect(rect)
        self.close() 

        # ... rest of the method ...

        # ... rest of the method ...

        # Copy to clipboard
        self.copy_to_clipboard(img)

        if self.callback:
            self.callback(img)

        self.start = None
        self.end = None




    # ---------------------------
    # Capture
    # ---------------------------
    def capture_rect(self, rect):
        with mss.mss() as sct:
            grab = sct.grab(rect)

        return Image.frombytes("RGB", grab.size, grab.rgb)

    
    def copy_to_clipboard(self, pil_img):
        """Convert PIL image to QImage and store in system clipboard."""
        arr = np.array(pil_img)

        # Convert RGB → Qt format
        h, w, ch = arr.shape
        bytes_per_line = ch * w
        qimg = QImage(arr.data, w, h, bytes_per_line, QImage.Format_RGB888)

        clipboard = QGuiApplication.clipboard()
        clipboard.setImage(qimg)

        print("[ScreenSelector] Image copied to clipboard.")



# Test callback
def on_image_captured(img):
    print("Image captured!")
    img.show()
