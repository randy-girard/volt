# -*- mode: python -*-

block_cipher = None


a = Analysis(['main.py'],
             pathex=['.'],
             binaries=[],
             datas=[('./config.json', ".")],
             hiddenimports=[
               'PySide6.sip'
             ],
             hookspath=[],
             runtime_hooks=[],
             excludes=[
               "./ginaconfig.xml"
             ],
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
         name='Volt.app',
         icon='icon.png',
         console=False,
         bundle_identifier=None)
