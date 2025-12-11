from PySide6.QtGui import QGuiApplication
import re
import fugashi
import pykakasi

# processing captured image
def on_image_captured(img, window, ocr_engine):
    text = ocr_engine.read_from_image(img)

    if window.source_lang != "ja":
        window.swap_languages()

    window.from_screen_selector = True
    clipboard = QGuiApplication.clipboard()
    clipboard.setText(text)
    window.input_text.blockSignals(True) # avoid triggering debounce
    window.input_text.setPlainText(text)
    window.input_text.blockSignals(False)
    window.start_translation_thread()

tagger = fugashi.Tagger()
kks = pykakasi.kakasi()

MACRONS = {"ou": "ō",
           "oo": "ō",
           "uu": "ū",
           "aa": "ā",
           "ee": "ē",
           "ii": "ī"}

PUNCT_MAP = {"。": ".",
             "、": ",",
             "！": "!",
             "？": "?",
             ".": ".",
             ",": ",",
             "!": "!",
             "?": "?"}

def apply_macrons(s):
    for src, tgt in MACRONS.items():
        s = s.replace(src, tgt)

    return s

# prevent None
def token_pronunciation(features, token_surface):
    if not features or token_surface is None:
        return ""
    
    if len(features) > 8 and features[8] not in ("", "*", None):
        return features[8]
    
    if len(features) > 7 and features[7] not in ("", "*", None):
        return features[7]

    return token_surface or ""

def is_punctuation(surface):
    return surface in PUNCT_MAP

def capitalize_sentence_starts(text):
    text = re.sub(r"^[a-z]", lambda m: m.group().upper(), text)
    text = re.sub(r"([.!?]\s+)([a-z])", lambda m: m.group(1) + m.group(2).upper(), text)
    text = re.sub(r"([\(\[\{]\s*)([a-z])", lambda m: m.group(1) + m.group(2).upper(), text)
    return text

def get_romaji(text):
    romaji_parts = []

    for token in tagger(text):
        features = token.feature
        pron = token_pronunciation(features, token.surface)
        if not pron:
            continue

        conv = kks.convert(pron or "")
        romaji = "".join(entry["hepburn"] for entry in conv)

        if not romaji:
            continue

        if is_punctuation(token.surface):
            mapped = PUNCT_MAP[token.surface]
            if romaji_parts:
                romaji_parts[-1] = romaji_parts[-1].rstrip()
                romaji_parts.append(mapped)
            else:
                romaji_parts.append(mapped)
        else:
            romaji_parts.append(romaji)

    romaji = " ".join(romaji_parts)
    romaji = re.sub(r"\s+([.,!?])", r"\1", romaji)
    romaji = re.sub(r"\s+", " ", romaji).strip()
    romaji = apply_macrons(romaji)
    romaji = capitalize_sentence_starts(romaji)

    return romaji