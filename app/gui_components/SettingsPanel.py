from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QCheckBox, QLineEdit, QApplication, QPushButton
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QKeyEvent # Needed for type hinting keyPressEvent

class SettingsPanel(QWidget):
    def __init__(self, settings):
        super().__init__(None, Qt.Window | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
        self.settings = settings
        self.setWindowTitle("Settings")
        self.setFixedSize(QSize(300, 160))

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        # --- Toggles ---
        # Store references to checkboxes
        self.checkbox_official_online = QCheckBox()
        self.checkbox_official_online.setChecked(settings.official_online)
        self.checkbox_official_online.stateChanged.connect(lambda s: self._update("official_online", bool(s)))
        layout.addLayout(self._toggle("Official Online", self.checkbox_official_online))

        self.checkbox_confirmation_panel = QCheckBox()
        self.checkbox_confirmation_panel.setChecked(settings.confirmation_panel_enabled)
        self.checkbox_confirmation_panel.stateChanged.connect(lambda s: self._update("confirmation_panel_enabled", bool(s)))
        layout.addLayout(self._toggle("Confirmation Panel", self.checkbox_confirmation_panel))

        # --- Hotkey Input ---
        shortcut_layout = QHBoxLayout()
        shortcut_layout.addWidget(QLabel("Screen selector hotkey:"))
        self.lineedit_screen_selector = QLineEdit(settings.screen_selector_sc)
        self.lineedit_screen_selector.textChanged.connect(lambda text: self._update("screen_selector_sc", text))
        shortcut_layout.addWidget(self.lineedit_screen_selector)
        layout.addLayout(shortcut_layout)
        layout.addStretch()

        # --- Button Row ---
        self.btn_cancel = QPushButton("Cancel")
        self.btn_cancel.clicked.connect(self.close)

        self.btn_accept = QPushButton("Save")
        self.btn_accept.clicked.connect(self.save_and_close)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_row.addWidget(self.btn_cancel)
        btn_row.addWidget(self.btn_accept)
        layout.addLayout(btn_row)

    def _toggle(self, label: str, checkbox: QCheckBox):
        layout = QHBoxLayout()
        layout.addWidget(QLabel(label))
        layout.addStretch()
        layout.addWidget(checkbox)
        return layout

    def _update(self, key, value):
        if key == "screen_selector_sc":
            valid_keys = {k.name for k in Qt.Key.__members__.values()}
            if value not in valid_keys:
                return
        
        setattr(self.settings, key, value)

    def save_and_close(self):
        self.settings.save()
        self.close()

    def refresh_from_settings(self):
        """Update all widgets to match the current saved settings"""
        self.checkbox_official_online.setChecked(self.settings.official_online)
        self.checkbox_confirmation_panel.setChecked(self.settings.confirmation_panel_enabled)
        self.lineedit_screen_selector.setText(self.settings.screen_selector_sc)

    # Escape key closes the panel like cancel
    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.close()
        super().keyPressEvent(event)
