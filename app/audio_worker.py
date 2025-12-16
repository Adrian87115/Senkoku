from PySide6.QtCore import QThread

from logger import log_exceptions

class TTSThread(QThread):
    def __init__(self, engine, text, lang):
        super().__init__()
        self.engine = engine
        self.text = text
        self.lang = lang
        self._running = True

    @log_exceptions
    def run(self):
        if self._running:
            self.engine.speak(self.text, lang = self.lang)

    @log_exceptions
    def stop(self):
        self._running = False
        try:
            if hasattr(self.engine, "stop"):
                self.engine.stop()
        except Exception:
            pass