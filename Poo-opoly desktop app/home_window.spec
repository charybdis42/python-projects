# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['home_window.py'],
    pathex=[],
    binaries=[],
    datas=[('app.ico', '.'), ('black.png', '.'), ('coles_cata.json', '.'), ('loading.png', '.'), ('no_image.png', '.'), ('update_coles_cata.mp4', '.'), ('update_woolies_cata.mp4', '.'), ('user_data.json', '.'), ('woolies_cata.json', '.')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='home_window',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
