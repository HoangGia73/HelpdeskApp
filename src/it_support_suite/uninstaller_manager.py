# -*- coding: utf-8 -*-
"""Enumerate, uninstall and clean remnants of Windows desktop applications."""
import ctypes
from ctypes import wintypes
import os
import re
import shutil
import subprocess
import time
import winreg

from .safety import validate_removal_target

class _ShellExecuteInfo(ctypes.Structure):
    _fields_ = [
        ("cbSize", wintypes.DWORD), ("fMask", wintypes.ULONG),
        ("hwnd", wintypes.HWND), ("lpVerb", wintypes.LPCWSTR),
        ("lpFile", wintypes.LPCWSTR), ("lpParameters", wintypes.LPCWSTR),
        ("lpDirectory", wintypes.LPCWSTR), ("nShow", ctypes.c_int),
        ("hInstApp", wintypes.HINSTANCE), ("lpIDList", ctypes.c_void_p),
        ("lpClass", wintypes.LPCWSTR), ("hkeyClass", wintypes.HKEY),
        ("dwHotKey", wintypes.DWORD), ("hMonitor", wintypes.HANDLE),
        ("hProcess", wintypes.HANDLE),
    ]

class UninstallerManager:
    PATH = r"Software\Microsoft\Windows\CurrentVersion\Uninstall"
    ROOTS = ((winreg.HKEY_CURRENT_USER, 0, "Người dùng"),
             (winreg.HKEY_LOCAL_MACHINE, winreg.KEY_WOW64_64KEY, "Toàn máy 64-bit"),
             (winreg.HKEY_LOCAL_MACHINE, winreg.KEY_WOW64_32KEY, "Toàn máy 32-bit"))

    @staticmethod
    def _get(key, name, default=""):
        try: return winreg.QueryValueEx(key, name)[0]
        except OSError: return default

    @classmethod
    def list_installed(cls):
        apps, seen = [], set()
        for root, view, scope in cls.ROOTS:
            try: parent = winreg.OpenKey(root, cls.PATH, 0, winreg.KEY_READ | view)
            except OSError: continue
            with parent:
                i = 0
                while True:
                    try: subname = winreg.EnumKey(parent, i); i += 1
                    except OSError: break
                    try:
                        with winreg.OpenKey(parent, subname) as key:
                            name = str(cls._get(key, "DisplayName")).strip()
                            command = str(cls._get(key, "UninstallString")).strip()
                            if not name or not command or cls._get(key, "SystemComponent", 0) == 1: continue
                            app = {"name": name, "version": str(cls._get(key, "DisplayVersion")).strip(),
                                   "publisher": str(cls._get(key, "Publisher")).strip(),
                                   "date": str(cls._get(key, "InstallDate")).strip(),
                                   "location": os.path.expandvars(str(cls._get(key, "InstallLocation")).strip().strip('"')),
                                   "command": os.path.expandvars(command), "scope": scope,
                                   "root": root, "view": view, "key": cls.PATH + "\\" + subname}
                            ident = (name.casefold(), app["version"].casefold(), command.casefold())
                            if ident not in seen: seen.add(ident); apps.append(app)
                    except (OSError, TypeError): pass
        return sorted(apps, key=lambda x: x["name"].casefold())

    @staticmethod
    def _split(command):
        command = command.strip()
        if command and command[0] not in ('"', "'"):
            if os.path.isfile(command): return [command]
            for match in re.finditer(r"\.(?:exe|com|bat|cmd)(?=\s|$)", command, re.I):
                executable = command[:match.end()].strip()
                if os.path.isfile(executable):
                    rest = command[match.end():].strip()
                    return [executable] + (UninstallerManager._split(rest) if rest else [])
        argc = ctypes.c_int()
        fn = ctypes.windll.shell32.CommandLineToArgvW
        fn.argtypes = (wintypes.LPCWSTR, ctypes.POINTER(ctypes.c_int)); fn.restype = ctypes.POINTER(wintypes.LPWSTR)
        argv = fn(command, ctypes.byref(argc))
        if not argv: raise OSError("Không đọc được lệnh gỡ cài đặt.")
        try: return [argv[i] for i in range(argc.value)]
        finally: ctypes.windll.kernel32.LocalFree(argv)

    @classmethod
    def uninstall_and_wait(cls, app):
        args = cls._split(app["command"])
        if os.path.basename(args[0]).casefold() in ("msiexec", "msiexec.exe"):
            args[1:] = [re.sub(r"^/i(?=\{)", "/X", x, flags=re.I) for x in args[1:]]
        info = _ShellExecuteInfo()
        info.cbSize = ctypes.sizeof(info); info.fMask = 0x00000040
        info.lpVerb = "runas"; info.lpFile = args[0]
        info.lpParameters = subprocess.list2cmdline(args[1:]) or None; info.nShow = 1
        execute = ctypes.windll.shell32.ShellExecuteExW
        execute.argtypes = [ctypes.POINTER(_ShellExecuteInfo)]; execute.restype = wintypes.BOOL
        if not execute(ctypes.byref(info)):
            code = ctypes.windll.kernel32.GetLastError()
            raise OSError(code, "Không thể chạy trình gỡ cài đặt hoặc yêu cầu UAC đã bị hủy.")
        if info.hProcess:
            ctypes.windll.kernel32.WaitForSingleObject(info.hProcess, 0xFFFFFFFF)
            ctypes.windll.kernel32.CloseHandle(info.hProcess)

    @staticmethod
    def _norm(value):
        value = re.sub(r"\b(?:x86|x64|32-bit|64-bit|version|v)?\s*\d+(?:[._-]\d+)*\b", " ", value, flags=re.I)
        return re.sub(r"[^a-z0-9]+", "", value.casefold())

    @classmethod
    def find_leftovers(cls, app):
        """Find strongly name-related remnants, including app cache directories."""
        found, seen = [], set()
        def add(kind, path, **extra):
            identity = (kind, os.path.normcase(path))
            if identity not in seen:
                seen.add(identity); found.append({"kind": kind, "path": path, **extra})
        location = app.get("location", "")
        if location and os.path.exists(location): add("Thư mục cài đặt", location)
        aliases = {cls._norm(app["name"]), cls._norm(os.path.basename(location)) if location else ""}
        aliases.discard(""); aliases = {x for x in aliases if len(x) >= 4}
        publisher = cls._norm(app.get("publisher", ""))
        roots = [x for x in (os.environ.get("APPDATA"), os.environ.get("LOCALAPPDATA"), os.environ.get("PROGRAMDATA")) if x]
        local = os.environ.get("LOCALAPPDATA")
        if local: roots += [os.path.join(local, "Temp"), os.path.join(local, "Packages")]
        for root in roots:
            if not os.path.isdir(root): continue
            try: children = list(os.scandir(root))
            except OSError: continue
            for entry in children:
                name_norm = cls._norm(entry.name)
                direct_match = any(a == name_norm or (len(a) >= 6 and a in name_norm) or (len(name_norm) >= 6 and name_norm in a) for a in aliases)
                if direct_match and entry.is_dir(follow_symlinks=False): add("Dữ liệu/Cache", entry.path)
                elif publisher and len(publisher) >= 5 and name_norm == publisher and entry.is_dir(follow_symlinks=False):
                    try:
                        for sub in os.scandir(entry.path):
                            sub_norm = cls._norm(sub.name)
                            if sub.is_dir(follow_symlinks=False) and any(a == sub_norm or (len(a) >= 6 and a in sub_norm) for a in aliases): add("Dữ liệu/Cache", sub.path)
                    except OSError: pass
        try:
            with winreg.OpenKey(app["root"], app["key"], 0, winreg.KEY_READ | app["view"]):
                add("Registry", app["key"], root=app["root"], view=app["view"])
        except OSError: pass
        return found

    @staticmethod
    def _delete_registry_tree(root, path, view):
        try:
            with winreg.OpenKey(root, path, 0, winreg.KEY_READ | winreg.KEY_WRITE | view) as key:
                while True:
                    try: child = winreg.EnumKey(key, 0)
                    except OSError: break
                    UninstallerManager._delete_registry_tree(root, path + "\\" + child, view)
            winreg.DeleteKeyEx(root, path, view, 0)
        except FileNotFoundError: pass

    @classmethod
    def delete_leftovers(cls, items):
        deleted, failed = [], []
        for item in items:
            try:
                if item["kind"] == "Registry": cls._delete_registry_tree(item["root"], item["path"], item["view"])
                else:
                    roots = [os.environ.get(name) for name in (
                        "ProgramFiles", "ProgramFiles(x86)", "PROGRAMDATA",
                        "APPDATA", "LOCALAPPDATA", "TEMP",
                    ) if os.environ.get(name)]
                    target = validate_removal_target(item["path"], roots)
                    if target.is_dir():
                        shutil.rmtree(target)
                    elif target.exists():
                        target.unlink()
                deleted.append(item)
            except Exception as exc: failed.append((item, str(exc)))
        return deleted, failed