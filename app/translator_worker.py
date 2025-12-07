from PySide6.QtCore import QObject, Signal

class TranslatorWorker(QObject):
    finished = Signal(str)

    def __init__(self, text, source, target, engine, online):
        super().__init__()
        self.text = text
        self.src = source
        self.tgt = target
        self.engine = engine
        self.online = online

    def run(self):
        if not self.text:
            self.finished.emit("")
            return

        try:
            if self.online:
                if self.src == "ja":
                    res = self.engine.ja_to_en(self.text)
                else:
                    res = self.engine.en_to_ja(self.text)
            else:
                res = "[OFFLINE] Mode enabled."
        except Exception as e:
            res = f"Error: {e}"
        
        self.finished.emit(res)