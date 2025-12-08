from PySide6.QtGui import QGuiApplication

# processing captured image
def on_image_captured(img, window, ocr_engine):
    text = ocr_engine.read_from_image(img)

    if window.source_lang != "ja":
        window.swap_languages()

    clipboard = QGuiApplication.clipboard()
    clipboard.setText(text)
    window.input_text.blockSignals(True) # avoid triggering debounce
    window.input_text.setPlainText(text)
    window.input_text.blockSignals(False)
    window.start_translation_thread()