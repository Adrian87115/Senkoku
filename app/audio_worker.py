from PySide6.QtCore import QThread, Signal

class TTSThread(QThread):
    finished = Signal()

    def __init__(self, engine, text, lang):
        super().__init__()
        self.engine = engine
        self.text = text
        self.lang = lang
        self._running = True

    def run(self):
        try:
            self.engine.speak(self.text, lang=self.lang)
        finally:
            self.finished.emit()

    def stop(self):
        self._running = False
        try:
            if hasattr(self.engine, "stop"):
                self.engine.stop()
        except:
            pass
