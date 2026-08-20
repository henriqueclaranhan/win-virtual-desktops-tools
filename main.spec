# -*- mode: python ; coding: utf-8 -*-

import os
import sys

sys.path.insert(0, os.path.abspath('.'))

from _version import __version__

versioned_name = f'win-virtual-desktops-tools-standalone-{__version__.replace(".", "-")}'

block_cipher = None

excluded_modules = [
    'numpy',
    'scipy',
    'pandas',
    'matplotlib',
    'psutil',
    'charset_normalizer',
    'PIL.ImageFilter',
    'PIL.SpiderImagePlugin',
    'PIL.ImageTk',
    'PIL.ImageQt',
    'PIL.ImageWin',
    'PIL.ImageShow',
    'unittest',
    'pydoc',
    'pydoc_data',
    'doctest',
    'sqlite3',
    'email',
    'xml',
    'xmlrpc',
    'distutils',
    'setuptools',
    'pkg_resources',
    'pdb',
    'curses',
    'asyncio',
    'tkinter.test',
    'lib2to3',
    'test',
]


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[('./dll/VirtualDesktopAccessor.dll', '.')],
    datas=[('assets', './assets')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excluded_modules,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# Filter out unnecessary Tcl/Tk bloat (tzdata, msgs, demos, exotic encodings)
def filter_datas(datas):
    filtered = []
    for item in datas:
        dest_path = item[0].lower()
        if 'tcl' in dest_path or 'tk' in dest_path:
            if 'tzdata' in dest_path:
                continue
            if 'msgs' in dest_path:
                continue
            if 'demos' in dest_path:
                continue
            if 'encoding' in dest_path:
                if not any(enc in dest_path for enc in ['utf-8', 'cp1252', 'ascii', 'iso8859-1']):
                    continue
        filtered.append(item)
    return filtered

a.datas = filter_datas(a.datas)

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

