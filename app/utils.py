from PySide6.QtGui import QGuiApplication
import re
import pykakasi
from sudachipy import dictionary, tokenizer as sudachi_tokenizer
import os
import winshell
from win32com.client import Dispatch

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

# Initialize
tokenizer_obj = dictionary.Dictionary().create()
mode = sudachi_tokenizer.Tokenizer.SplitMode.C
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
             "「": "\"",
             "」": "\"",
             "『": "\"",
             "』": "\"",
             ".": ".",
             ",": ",",
             "!": "!",
             "?": "?"}

def apply_macrons(s):
    for src, tgt in MACRONS.items():
        s = s.replace(src, tgt)
    return s

def is_punctuation(surface):
    return surface in PUNCT_MAP

def capitalize_sentence_starts(text):
    text = re.sub(r"^[a-z]", lambda m: m.group().upper(), text)
    text = re.sub(r"([.!?]\s+)([a-z])", lambda m: m.group(1) + m.group(2).upper(), text)
    text = re.sub(r"([\(\[\{]\s*)([a-z])", lambda m: m.group(1) + m.group(2).upper(), text)
    text = re.sub(r"([\"“”『』]\s*)([a-z])", lambda m: m.group(1) + m.group(2).upper(), text)
    return text

SOKUON_PLACEHOLDER = "¤"  # rarely used ASCII character

# sokuon is treated as tsu, so it has to be preserved
def mark_sokuon(text):
    new_text = ""
    for char in text:
        if char in ("っ", "ッ"):
            new_text += SOKUON_PLACEHOLDER
        else:
            new_text += char
    return new_text

# since sokuon is treated as tsu we must manually make it work as it is meant to
def apply_sokuon_doubling(romaji):
    result = ""
    i = 0
    while i < len(romaji):
        if romaji[i] == SOKUON_PLACEHOLDER and i + 1 < len(romaji):

            next_char = romaji[i + 2]
            if result.endswith(" "):
                result = result[:-1]
            result += next_char

            i += 1
        else:
            result += romaji[i]
        i += 1

    return result

def get_romaji(text):
    text = mark_sokuon(text)
    romaji_parts = []

    for token in tokenizer_obj.tokenize(text, mode):
        surface = token.surface()

        if surface in PUNCT_MAP:
            if romaji_parts:
                romaji_parts[-1] = romaji_parts[-1].rstrip()
            romaji_parts.append(PUNCT_MAP[surface])
            continue

        pron = token.reading_form() or surface

        if all((ord(c) < 128 or c == SOKUON_PLACEHOLDER) for c in surface):
            romaji_parts.append(surface)
            continue

        conv = kks.convert(pron)
        romaji = "".join(entry["hepburn"] for entry in conv)

        if romaji:
            romaji_parts.append(romaji)

    romaji = " ".join(romaji_parts)
    romaji = re.sub(r"\s+([.,!?])", r"\1", romaji)
    romaji = re.sub(r"\s+", " ", romaji).strip()
    romaji = apply_macrons(romaji)
    romaji = capitalize_sentence_starts(romaji)
    romaji = apply_sokuon_doubling(romaji)
    return romaji

def create_desktop_shortcut(path_to_exe, icon_path):
    desktop = winshell.desktop()
    shortcut_path = os.path.join(desktop, "Senkoku.lnk")
    icon_location = f"{icon_path},0"

    if not os.path.isfile(path_to_exe):
        print(f"Executable file not found: {path_to_exe}")
        return
    
    if not os.path.isfile(icon_path):
        print(f"Executable file not found: {icon_path}")
        return

    shell = Dispatch('WScript.Shell')
    shortcut = shell.CreateShortcut(shortcut_path)
    shortcut.Targetpath = path_to_exe
    shortcut.WorkingDirectory = os.path.dirname(path_to_exe)
    shortcut.IconLocation = icon_location 
    shortcut.save()
    print("Desktop shortcut created!")