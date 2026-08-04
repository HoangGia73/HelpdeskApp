# -*- mode: python ; coding: utf-8 -*-
from pathlib import Path
from PyInstaller.utils.hooks import collect_all

project_root = Path(SPECPATH).parent
version = (project_root / "VERSION").read_text(encoding="utf-8").strip()
app_name = f"ITSupportToolSuite-v{version}"
datas, binaries, hiddenimports = collect_all("customtkinter")
datas.append((str(project_root / "VERSION"), "."))

a = Analysis(
    [str(project_root / "packaging" / "entrypoint.py")],
    pathex=[str(project_root / "src")], binaries=binaries, datas=datas,
    hiddenimports=hiddenimports, hookspath=[], hooksconfig={}, runtime_hooks=[],
    excludes=[], noarchive=False, optimize=1,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz, a.scripts, a.binaries, a.datas, [], name=app_name, debug=False,
    bootloader_ignore_signals=False, strip=False, upx=True, upx_exclude=[],
    runtime_tmpdir=None, console=False, disable_windowed_traceback=False,
    argv_emulation=False, target_arch=None, codesign_identity=None,
    entitlements_file=None,
)
