# -*- coding: utf-8 -*-
"""Install and inspect common applications through Windows Package Manager."""

import locale
import shutil
import subprocess


class SoftwareManager:
    PACKAGES = (
        {"name": "UniKey", "id": "UniKey.UniKey", "description": "B\u1ed9 g\u00f5 ti\u1ebfng Vi\u1ec7t"},
        {"name": "UltraViewer", "id": "DucFabulous.UltraViewer", "description": "H\u1ed7 tr\u1ee3 m\u00e1y t\u00ednh t\u1eeb xa"},
        {"name": "WinRAR", "id": "RARLab.WinRAR", "description": "N\u00e9n v\u00e0 gi\u1ea3i n\u00e9n t\u1eadp tin"},
        {"name": "7-Zip", "id": "7zip.7zip", "description": "N\u00e9n v\u00e0 gi\u1ea3i n\u00e9n m\u00e3 ngu\u1ed3n m\u1edf"},
        {"name": "Zalo", "id": "VNGCorp.Zalo", "description": "Nh\u1eafn tin v\u00e0 g\u1ecdi \u0111i\u1ec7n"},
        {"name": "Foxit PDF Reader", "id": "Foxit.FoxitReader", "description": "\u0110\u1ecdc t\u00e0i li\u1ec7u PDF"},
        {"name": "Google Chrome", "id": "Google.Chrome", "description": "Tr\u00ecnh duy\u1ec7t web"},
        {"name": "Microsoft PowerToys", "id": "Microsoft.PowerToys", "description": "B\u1ed9 ti\u1ec7n \u00edch n\u00e2ng cao cho Windows"},
        {"name": "VLC media player", "id": "VideoLAN.VLC", "description": "Ph\u00e1t video v\u00e0 \u00e2m thanh nhi\u1ec1u \u0111\u1ecbnh d\u1ea1ng"},
        {"name": "Everything", "id": "voidtools.Everything", "description": "T\u00ecm ki\u1ebfm t\u1eadp tin c\u1ef1c nhanh"},
        {"name": "Notepad++", "id": "Notepad++.Notepad++", "description": "So\u1ea1n th\u1ea3o v\u0103n b\u1ea3n v\u00e0 m\u00e3 ngu\u1ed3n"},
        {"name": "LibreOffice", "id": "TheDocumentFoundation.LibreOffice", "description": "B\u1ed9 \u1ee9ng d\u1ee5ng v\u0103n ph\u00f2ng mi\u1ec5n ph\u00ed"},
        {"name": "CrystalDiskInfo", "id": "CrystalDewWorld.CrystalDiskInfo", "description": "Ki\u1ec3m tra s\u1ee9c kh\u1ecfe HDD v\u00e0 SSD"},
        {"name": "CPU-Z", "id": "CPUID.CPU-Z", "description": "Xem th\u00f4ng tin CPU, RAM v\u00e0 mainboard"},
        {"name": "HWiNFO", "id": "REALiX.HWiNFO", "description": "Ch\u1ea9n \u0111o\u00e1n v\u00e0 gi\u00e1m s\u00e1t ph\u1ea7n c\u1ee9ng"},
    )

    @staticmethod
    def _run(arguments, timeout=None):
        return subprocess.run(
            ["winget", *arguments], capture_output=True, text=True,
            encoding=locale.getpreferredencoding(False) or "utf-8", errors="replace",
            timeout=timeout, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0)
        )

    @classmethod
    def winget_available(cls):
        if not shutil.which("winget"):
            return False
        try:
            return cls._run(["--version"], timeout=10).returncode == 0
        except (OSError, subprocess.SubprocessError):
            return False

    @classmethod
    def is_installed(cls, package_id):
        result = cls._run([
            "list", "--id", package_id, "--exact",
            "--accept-source-agreements", "--disable-interactivity"
        ], timeout=45)
        return result.returncode == 0 and package_id.lower() in result.stdout.lower()

    @classmethod
    def install(cls, package_id, output_callback=None):
        command = [
            "winget", "install", "--id", package_id, "--exact", "--source", "winget",
            "--silent", "--disable-interactivity", "--accept-package-agreements",
            "--accept-source-agreements"
        ]
        process = subprocess.Popen(
            command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
            encoding=locale.getpreferredencoding(False) or "utf-8", errors="replace",
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0)
        )
        if process.stdout:
            for line in process.stdout:
                line = line.strip()
                if line and output_callback:
                    output_callback(line)
        return process.wait()
