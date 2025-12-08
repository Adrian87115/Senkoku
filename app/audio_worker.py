from PySide6.QtCore import QThread, QObject, Signal

class TTSThread(QThread):
    def __init__(self, engine, text, lang):
        super().__init__()
        self.engine = engine
        self.text = text
        self.lang = lang

    def run(self):
        self.engine.speak(self.text, lang = self.lang)