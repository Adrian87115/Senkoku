from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel, QTextEdit, QPushButton, QSizePolicy, QHBoxLayout
from PySide6.QtGui import QColor, QPalette, QFont, QIcon
from PySide6.QtCore import QThread, QTimer, Qt
from translator import FreeGoogleTranslatorEngine, OfficialGoogleTranslatorEngine
from translator_worker import TranslatorWorker
from audio_worker import TTSThread
from gui_components.SettingsPanel import SettingsPanel

class MainWindow(QMainWindow):
    def __init__(self, settings, confirmation_panel):
        super().__init__()
        self.settings = settings
        self.from_screen_selector = False

        if self.settings.official_online:
            self.translation_engine = OfficialGoogleTranslatorEngine()
        else:
            self.translation_engine = FreeGoogleTranslatorEngine()

        if self.settings.confirmation_panel_enabled:
                self.confirmation_panel = confirmation_panel
        else:
            self.confirmation_panel = None

        self.central = QWidget()
        self.setCentralWidget(self.central)
        self.layout = QVBoxLayout(self.central)

        self.setWindowTitle("Senkoku")
        self.setWindowIcon(QIcon("../icon.png"))
        self.setGeometry(600, 100, 500, 450)
        self.setup_theme()
        self.setup_layout()
        self.setup_widgets()

        self.settings_panel = SettingsPanel(self.settings)

        self.source_lang = "ja"
        self.target_lang = "en"
        self.current_thread = None

        self.tts_busy = False

        self.debounce_timer = QTimer()
        self.debounce_timer.setSingleShot(True)
        self.debounce_timer.setInterval(300)
        self.debounce_timer.timeout.connect(self.start_translation_thread)
        self.input_text.textChanged.connect(self.debounce_timer.start)

    # app theme
    def setup_theme(self):
        p = self.palette()
        p.setColor(QPalette.Window, QColor("#222222"))
        p.setColor(QPalette.WindowText, QColor("#FFFFFF"))
        p.setColor(QPalette.Button, QColor("#444444"))
        p.setColor(QPalette.ButtonText, QColor("#ffffff"))
        p.setColor(QPalette.Base, QColor("#2F2F2F"))
        p.setColor(QPalette.Text, QColor("#ffffff"))
        self.setPalette(p)

    # app layout
    def setup_layout(self):
        # font of labels
        label_font = QFont()
        label_font.setFamily("Arial")
        label_font.setPointSize(16)
        label_font.setBold(True)

        # font of buttons
        button_font = QFont()
        button_font.setFamily("Arial")
        button_font.setPointSize(10)

        title_row = QHBoxLayout()

        # in
        self.label_in = QLabel("Japanese:")
        self.label_in.setFont(label_font)

        title_row.addWidget(self.label_in, alignment = Qt.AlignVCenter)
        title_row.addStretch()
        self.btn_settings = QPushButton("⚙")
        self.btn_settings.setFixedSize(32, 32)
        self.btn_settings.setToolTip("Settings")
        self.btn_settings.clicked.connect(self.open_settings_panel)
        self.btn_settings.setStyleSheet("""QPushButton {background-color: #444;
                                                        border: 1px solid #666;
                                                        border-radius: 6px;
                                                        font-size: 16px;
                                                        color: white;}
                                           QPushButton:hover {background-color: #555;}""")

        title_row.addWidget(self.btn_settings)

        self.layout.addLayout(title_row)

        self.input_text = QTextEdit()
        self.input_text.setMinimumHeight(120)
        self.input_text.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.input_text.setPlaceholderText("Enter Japanese text...")

        # out
        self.label_out = QLabel("English:")
        self.label_out.setFont(label_font)
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setMinimumHeight(120)
        self.output_text.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # romaji
        self.romaji_text_in = QTextEdit()
        self.romaji_text_in.setReadOnly(True)
        self.romaji_text_in.setMinimumHeight(50)
        self.romaji_text_in.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.romaji_text_out = QTextEdit()
        self.romaji_text_out.setReadOnly(True)
        self.romaji_text_out.setMinimumHeight(50)
        self.romaji_text_out.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # swap languages button
        self.btn_reverse = QPushButton("Swap Languages (JA => EN)")
        self.btn_reverse.clicked.connect(self.swap_languages)
        self.btn_reverse.setFont(button_font)

        # play input button
        self.btn_play_in = QPushButton("Play")
        self.btn_play_in.clicked.connect(self.play_input)
        self.btn_play_in.setFont(button_font)

        # play output button
        self.btn_play_out = QPushButton("Play")
        self.btn_play_out.clicked.connect(self.play_output)
        self.btn_play_out.setFont(button_font)
        
        # layout
        self.layout.addWidget(self.label_in)
        self.layout.addWidget(self.input_text, stretch = 3)
        self.layout.addWidget(self.romaji_text_in, stretch = 1.25)
        self.layout.addWidget(self.btn_play_in)
        self.layout.addWidget(self.btn_reverse)
        self.layout.addWidget(self.label_out)
        self.layout.addWidget(self.output_text, stretch = 3)
        self.layout.addWidget(self.romaji_text_out, stretch = 1.25)
        self.layout.addWidget(self.btn_play_out)

    # app widgets
    def setup_widgets(self):
        # style of text spaces
        style_box = """QTextEdit {background-color: #2F2F2F;
                                  color: white;
                                  border: 1px solid #555;
                                  font-size: 16pt;}
                       QTextEdit[placeholderText]:empty {color: #888888;
                                                         font-size: 16pt;}"""
        self.input_text.setStyleSheet(style_box)
        self.output_text.setStyleSheet(style_box)
        self.romaji_text_in.setStyleSheet(style_box)
        self.romaji_text_out.setStyleSheet(style_box)
        self.label_in.setStyleSheet("color: white; font-weight: bold;")
        self.label_out.setStyleSheet("color: white; font-weight: bold;")

    # play input voice
    def play_input(self):
        self.play_tts(text = self.input_text.toPlainText().strip(), lang = self.source_lang, attr_name = "tts_thread_in")

    # play output voice
    def play_output(self):
        self.play_tts(text = self.output_text.toPlainText().strip(), lang = self.target_lang, attr_name = "tts_thread_out")

    def play_tts(self, text, lang, attr_name):
        if not text:
            return

        # prevent any simultaneous playback
        if self.tts_busy:
            return

        self.tts_busy = True
        thread = getattr(self, attr_name, None)

        if thread is not None and thread.isRunning():
            self.tts_busy = False
            return

        new_thread = TTSThread(self.translation_engine, text, lang)
        setattr(self, attr_name, new_thread)

        def cleanup():
            setattr(self, attr_name, None)
            self.tts_busy = False

        new_thread.finished.connect(cleanup)
        new_thread.start()

    # update output text and romaji panels
    def update_ui(self, result):
        if not result.strip():
            self.output_text.clear()

            if self.settings.confirmation_panel_enabled:
                self.confirmation_panel.hide()

            self.romaji_text_in.clear()
            self.romaji_text_out.clear()
            return

        self.output_text.setPlainText(result)
        input_text = self.input_text.toPlainText().strip()
        romaji_in = ""

        if self.source_lang == "ja":
            romaji_in = self.translation_engine.get_romaji(input_text)
            self.romaji_text_in.setPlainText(romaji_in)
        else:
            self.romaji_text_in.clear()

        if self.target_lang == "ja":
            romaji_out = self.translation_engine.get_romaji(result)
            self.romaji_text_out.setPlainText(romaji_out)
        else:
            self.romaji_text_out.clear()

        if self.from_screen_selector:
            if self.settings.confirmation_panel_enabled:
                self.confirmation_panel.update_text(original = input_text, reading = romaji_in, translation = result)
                self.confirmation_panel.show()
            self.from_screen_selector = False
        else:
            if self.settings.confirmation_panel_enabled:
                self.confirmation_panel.hide()

    # language swap
    def swap_languages(self):
        if self.source_lang == "ja":
            self.source_lang, self.target_lang = "en", "ja"
            self.label_in.setText("English:")
            self.label_out.setText("Japanese:")
            self.btn_reverse.setText("Swap Languages (EN => JA)")
            self.input_text.setPlaceholderText("Enter English text...")
        else:
            self.source_lang, self.target_lang = "ja", "en"
            self.label_in.setText("Japanese:")
            self.label_out.setText("English:")
            self.btn_reverse.setText("Swap Languages (JA => EN)")
            self.input_text.setPlaceholderText("Enter Japanese text...")
        
        new_input = self.output_text.toPlainText()
        self.input_text.blockSignals(True)
        self.input_text.setPlainText(new_input)
        self.input_text.blockSignals(False)

        # Clear the old output
        self.output_text.clear()

        # Trigger translation manually after swap
        self.start_translation_thread()

    # asynchronous translation
    def start_translation_thread(self):
        text = self.input_text.toPlainText().strip()
        if not text:
            self.output_text.clear()
            self.romaji_text_in.clear()
            self.romaji_text_out.clear()
            self.romaji_text_out.clear()
            if self.settings.confirmation_panel_enabled:
                self.confirmation_panel.hide()
            return

        # stop and clean up any running previous thread, only when there is one
        if self.current_thread is not None and self.current_thread.isRunning():
            self.current_thread.quit()
            self.current_thread.wait() # wait for the thread to stop

        # create worker and thread
        self.worker = TranslatorWorker(text, self.source_lang, self.target_lang, self.translation_engine)
        thread = QThread()
        
        # store the new thread reference
        self.current_thread = thread 
        
        self.worker.moveToThread(thread)
        
        # connect signal
        thread.started.connect(self.worker.run)
        
        # clean up worker and thread when done
        self.worker.finished.connect(self.update_ui)
        self.worker.finished.connect(thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        
        # clean
        thread.finished.connect(thread.deleteLater)
        thread.finished.connect(self.cleanup_thread)

        thread.start()

    # stop threads when closing app
    def closeEvent(self, event):
        if self.current_thread and self.current_thread.isRunning():
            self.current_thread.quit()
            self.current_thread.wait()

        if hasattr(self, "settings_panel") and self.settings_panel is not None:
            self.settings_panel.close()

        super().closeEvent(event)

    # called when the thread finishes and safely clears the reference
    # prevents clearing the reference if another thread finishes unexpectedly
    def cleanup_thread(self):
        sender_thread = self.sender()
        if sender_thread is self.current_thread:
            self.current_thread = None

    def open_settings_panel(self):
        self.settings_panel.refresh_from_settings()
        self.settings_panel.show()
        self.settings_panel.raise_()
        self.settings_panel.activateWindow()