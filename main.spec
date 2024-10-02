# -*- mode: python ; coding: utf-8 -*-

import os
import sys

sys.path.insert(0, os.path.abspath('.'))

from _version import __version__

versioned_name = f'win-virtual-desktops-tools-standalone-{__version__.replace(".", "-")}'


block_cipher = None


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[('./dll/VirtualDesktopAccessor.dll', '.')],
    datas=[('assets', './assets')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name=versioned_name,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['./assets/icon.ico'],
)
