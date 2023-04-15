# -*- mode: python -*-

block_cipher = None


a = Analysis(['differentiel.py'],
             pathex=['C:\\Users\\raphael abele\\Documents\\Mathieu LISART'],
             binaries=[],
             datas=[('C:/Users/raphael abele/Documents/Qt/Realign_IHM/realign.ui', '.')],
             hiddenimports=['PySide.QtXml'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='differentiel',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='differentiel')
