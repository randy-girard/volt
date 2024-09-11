# -*- mode: python -*-

block_cipher = None

data = [('data', 'data')]
data += [('plugins', 'plugins')]

from PyInstaller.utils.hooks import copy_metadata
data += copy_metadata('colorhash')

a = Analysis(['main.py'],
             pathex=['.'],
             binaries=[],
             datas=data,
             hookspath=[],
             runtime_hooks=[],
             #excludes=[
            # "PySide6.QtQml",
            #   "PySide6.QtOpenGL",
            #   "PySide6.QtQuick",
            #   "PySide6.QtQuickWidgets",
            #   "PySide6.QtNetwork",
            #   "PySide6.QtWebChannel",
            #   "PySide6.QtPositioning",
            #   "PySide6.QtDBus",
            #   "PySide6.QtPrintSupport",
            #   "PySide6.QtWebEngineCore",
            #   "PySide6.QtWebEngineWidgets"
             #],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher
)
from glob import glob

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='Volt',
          icon='icon.png',
          strip=False,
          upx=True,
          console=False,
          runtime_tmpdir=None)

app = BUNDLE(exe,
         a.scripts,
         a.binaries,
         a.zipfiles,
         a.datas,
         strip=False,
         upx=True,
         name='Volt.app',
         icon='icon.png',
         console=False,
         bundle_identifier=None)
