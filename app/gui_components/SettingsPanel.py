from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QCheckBox, QLineEdit, QPushButton, QMessageBox
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QKeyEvent

class SettingsPanel(QWidget):
    VALID_QT_IDENTIFIERS = set()
    for name in dir(Qt.Key):
        if name.startswith('Key_'):
            VALID_QT_IDENTIFIERS.add(name.lstrip('Key_').upper())

    for name in ["CTRL", "SHIFT", "ALT", "META"]:
        VALID_QT_IDENTIFIERS.add(name)

    for name in dir(Qt.KeyboardModifier):
        if name.endswith('Modifier'):
            VALID_QT_IDENTIFIERS.add(name.removesuffix('Modifier').upper())

    def __init__(self, settings):
        super().__init__(None, Qt.Window | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
        self.settings = settings
        self.temp_settings = settings._data.copy()
        self.setWindowTitle("Settings")
        self.setFixedSize(QSize(300, 160))

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        self.checkbox_official_online = QCheckBox()
        self.checkbox_official_online.setChecked(self.temp_settings["official_online"])
        self.checkbox_official_online.stateChanged.connect(lambda s: self._update("official_online", bool(s)))
        layout.addLayout(self._toggle("Official Online", self.checkbox_official_online))

        self.checkbox_confirmation_panel = QCheckBox()
        self.checkbox_confirmation_panel.setChecked(self.temp_settings["confirmation_panel_enabled"])
        self.checkbox_confirmation_panel.stateChanged.connect(lambda s: self._update("confirmation_panel_enabled", bool(s)))
        layout.addLayout(self._toggle("Confirmation Panel", self.checkbox_confirmation_panel))

        shortcut_layout = QHBoxLayout()
        shortcut_layout.addWidget(QLabel("Screen selector hotkey:"))
        self.lineedit_screen_selector = QLineEdit(self.temp_settings["screen_selector_sc"])
        self.lineedit_screen_selector.textChanged.connect(lambda text: self._update("screen_selector_sc", text))
        shortcut_layout.addWidget(self.lineedit_screen_selector)
        layout.addLayout(shortcut_layout)
        layout.addStretch()

        self.btn_cancel = QPushButton("Cancel")
        self.btn_cancel.clicked.connect(self.close)

        self.btn_accept = QPushButton("Save")
        self.btn_accept.clicked.connect(self.save_and_close)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_row.addWidget(self.btn_cancel)
        btn_row.addWidget(self.btn_accept)
        layout.addLayout(btn_row)

    def _toggle(self, label, checkbox):
        layout = QHBoxLayout()
        layout.addWidget(QLabel(label))
        layout.addStretch()
        layout.addWidget(checkbox)
        return layout

    def _validate_shortcut(self, shortcut_text):
        if not shortcut_text:
            return True
            
        parts = shortcut_text.upper().split('+')
        
        for part in parts:
            part = part.strip()
            if not part in self.VALID_QT_IDENTIFIERS:
                return False
        
        return True

    def _update(self, key, value):
        if key == "screen_selector_sc":
            if not self._validate_shortcut(value):
                return 

        self.temp_settings[key] = value

    def save_and_close(self):
        for key, value in self.temp_settings.items():
            setattr(self.settings, key, value)

        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Restart Required")
        msg_box.setText("Settings saved. Please restart the application for changes to take effect. Application may not work properly.")
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec()
        self.close()

    def refresh_from_settings(self):
        self.temp_settings = self.settings._data.copy()
        self.checkbox_official_online.setChecked(self.temp_settings["official_online"])
        self.checkbox_confirmation_panel.setChecked(self.temp_settings["confirmation_panel_enabled"])
        self.lineedit_screen_selector.setText(self.temp_settings["screen_selector_sc"])

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Escape:
            self.close()
        super().keyPressEvent(event)