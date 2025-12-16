# -*- mode: python ; coding: utf-8 -*-

import os
from PyInstaller.utils.hooks import collect_submodules, collect_data_files

block_cipher = None

datas = (collect_data_files("pykakasi") + collect_data_files("unidic_lite") + collect_data_files("manga_ocr") + [('../icon.ico', '.')])

a = Analysis(['main.py'],
             pathex=['./app'],
             binaries=[],
             datas=datas,
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             cipher=block_cipher)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='Senkoku',
          debug=True,
          bootloader_ignore_signals=False,
          strip=False,
          upx=False,
          console=True,
          icon='../icon.ico')

coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='Senkoku')