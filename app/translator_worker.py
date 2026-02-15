from PySide6.QtCore import QObject, Signal

from logger import log_exceptions

class TranslatorWorker(QObject):
    finished = Signal(str)

    def __init__(self, text, source, target, engine):
        super().__init__()
        self.text = text
        self.src = source
        self.tgt = target
        self.engine = engine

    @log_exceptions
    def run(self):
        if not self.text:
            self.finished.emit("")
            return

        try:
            res = self._perform_translation()
            self.finished.emit(res)

        except Exception as e:
            print(f"Translation failed (likely idle timeout): {e}")
            print("Attempting to reconnect...")

            try:
                if hasattr(self.engine, 'reconnect'):
                    self.engine.reconnect()
                    res = self._perform_translation()
                    self.finished.emit(res)
                else:
                    self.finished.emit(f"Error: {e}")

            except Exception as final_error:
                self.finished.emit(f"Translation Error: {final_error}")

    def _perform_translation(self):
        if self.src == "ja" and self.tgt == "en":
            return self.engine.ja_to_en(self.text)
        elif self.src == "en" and self.tgt == "ja":
            return self.engine.en_to_ja(self.text)
        return ""