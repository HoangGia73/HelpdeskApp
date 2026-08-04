# -*- coding: utf-8 -*-
"""
Mô-đun backup_manager.py
------------------------
Quản lý toàn bộ tiến trình sao lưu và khôi phục dữ liệu (Driver, Userdata, Chrome, Outlook).
"""

import os
import shutil
import zipfile
import datetime
import json
import subprocess
import re
import ctypes
import base64
import tempfile

# Nhập các hàm lấy đường dẫn tiện ích
from .utils import get_user_data_paths, get_shell_folder

class BackupRestoreManager:
    CHROME_EXCLUDE_PARTS = {
        "cache", "code cache", "gpucache", "gpupersistentcache",
        "dawngraphitecache", "dawncache", "shadercache", "grshadercache",
        "cache_storage", "cachestorage", "service worker", "crashpad",
        "browsermetrics", "component_crx_cache", "system recovery"
    }

    @staticmethod
    def is_path_within(path, parent):
        try:
            return os.path.commonpath([os.path.realpath(path), os.path.realpath(parent)]) == os.path.realpath(parent)
        except ValueError:
            return False

    @staticmethod
    def is_process_running(image_name):
        result = subprocess.run(
            ["tasklist", "/FI", r"IMAGENAME eq {image_name}", "/NH"],
            capture_output=True, text=True, errors="replace",
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0)
        )
        return image_name.lower() in result.stdout.lower()

    @staticmethod
    def safe_extract_zip(zip_file, destination):
        """Extract a ZIP only when every member remains inside destination."""
        destination_real = os.path.realpath(destination)
        for member in zip_file.infolist():
            member_path = os.path.realpath(os.path.join(destination_real, member.filename))
            if os.path.commonpath([destination_real, member_path]) != destination_real:
                raise ValueError(r"Unsare ZIP member path: {member.filename}")
        zip_file.extractall(destination_real)

    @classmethod
    def estimate_backup_size(cls, paths_dict, selections):
        total = 0
        sources = []
        if selections.get("Userdata"):
            sources.extend(paths_dict.get(name) for name in ("Desktop", "Documents", "Downloads"))
        if selections.get("Chrome"):
            sources.append(paths_dict.get("Chrome"))
        for source in filter(None, sources):
            if not os.path.exists(source):
                continue
            for root, _, files in os.walk(source):
                for filename in files:
                    path = os.path.join(root, filename)
                    if selections.get("Chrome") and source == paths_dict.get("Chrome") and cls.should_exclude(path):
                        continue
                    try:
                        total += os.path.getsize(path)
                    except OSError:
                        pass
        if selections.get("Outlook"):
            for source in (paths_dict.get("Outlook_Docs"), paths_dict.get("Outlook_Local")):
                if source and os.path.exists(source):
                    for root, _, files in os.walk(source):
                        for filename in files:
                            if filename.lower().endswith((".pst", ".ost")):
                                try:
                                    total += os.path.getsize(os.path.join(root, filename))
                                except OSError:
                                    pass
        return total

    @classmethod
    def analyze_backup(cls, paths_dict, selections, excluded_paths=None):
        """Count files and bytes in one filesystem pass."""
        count = 0
        total_size = 0
        excluded_real = [os.path.realpath(path) for path in (excluded_paths or [])]

        def add_tree(source, predicate=None):
            nonlocal count, total_size
            if not source or not os.path.exists(source):
                return
            for root, dirs, files in os.walk(source):
                dirs[:] = [directory for directory in dirs if not any(
                    cls.is_path_within(os.path.join(root, directory), excluded)
                    for excluded in excluded_real
                )]
                for filename in files:
                    path = os.path.join(root, filename)
                    if predicate and not predicate(path):
                        continue
                    count += 1
                    try:
                        total_size += os.path.getsize(path)
                    except OSError:
                        pass

        if selections.get("Userdata"):
            for name in ("Desktop", "Documents", "Downloads"):
                add_tree(paths_dict.get(name))
        if selections.get("Chrome"):
            add_tree(paths_dict.get("Chrome"), lambda path: not cls.should_exclude(path))
        if selections.get("Outlook"):
            outlook_filter = lambda path: path.lower().endswith((".pst", ".ost"))
            add_tree(paths_dict.get("Outlook_Docs"), outlook_filter)
            add_tree(paths_dict.get("Outlook_Local"), outlook_filter)
        return count, total_size
    @staticmethod
    def _run_elevated_powershell(script):
        """Run PowerShell once with UAC and return JSON written by that process."""
        rd, output_path = tempfile.mkstemp(prefix="it_support_", suffix=".json")
        os.close(rd)
        try:
            os.remove(output_path)
            safe_output = output_path.replace("'", "''")
            wrapped = (
                "$ErrorActionPreference='Stop'; try { " + script +
                r" | ConvertTo-Json -Depth 8 -Compress | Set-Content -LiteralPath '{safe_output}' -Encoding UTF8; "
                "exit 0 } catch { "
                r"@{{error=$_.Exception.Message}} | ConvertTo-Json -Compress | Set-Content -LiteralPath '{safe_output}' -Encoding UTF8; "
                "exit 1 }"
            )
            encoded = base64.b64encode(wrapped.encode("utf-16-le")).decode("ascii")
            launcher = (
                "$p=Start-Process -FilePath 'powershell.exe' -Verb RunAs -Wait -PassThru "
                f"-ArgumentList @('-NoProfile','-EncodedCommand','{encoded}'); exit $p.ExitCode"
            )
            result = subprocess.run(
                ["powershell", "-NoProfile", "-Command", launcher],
                capture_output=True, text=True, errors="replace",
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0)
            )
            if not os.path.exists(output_path):
                detail = (result.stderr or result.stdout or "UAC was cancelled.").strip()
                raise RuntimeError(detail)
            with open(output_path, "r", encoding="utf-8-sig") as handle:
                payload = json.load(handle)
            if result.returncode != 0 or (isinstance(payload, dict) and payload.get("error")):
                raise RuntimeError(payload.get("error", "Privileged operation failed."))
            return payload
        finally:
            try:
                os.remove(output_path)
            except OSError:
                pass

    @staticmethod
    def scan_installed_drivers():
        """Return exportable third-party drivers currently installed on Windows."""
        if not ctypes.windll.shell32.IsUserAnAdmin():
            data = BackupRestoreManager._run_elevated_powershell(
                "Get-WindowsDriver -Online | Select-Object Driver,OriginalFileName,"
                "ProviderName,ClassName,Date,Version"
            )
            if isinstance(data, dict):
                data = [data]
            return BackupRestoreManager._normalize_driver_list(data)

        ps_script = (
            "Get-WindowsDriver -Online | "
            "Select-Object Driver,OriginalFileName,ProviderName,ClassName,"
            "Date,Version | ConvertTo-Json -Compress"
        )
        result = subprocess.run(
            ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_script],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0)
        )
        if result.returncode != 0:
            error = (result.stderr or result.stdout or "Driver scan failed.").strip()
            raise RuntimeError(error)
        raw = result.stdout.strip()
        if not raw:
            return []
        data = json.loads(raw)
        if isinstance(data, dict):
            data = [data]
        return BackupRestoreManager._normalize_driver_list(data)

    @staticmethod
    def _normalize_driver_list(data):
        drivers = []
        for item in data:
            published_name = (item.get("Driver") or "").strip()
            if published_name:
                drivers.append({
                    "published_name": published_name,
                    "original_name": os.path.basename(item.get("OriginalFileName") or ""),
                    "provider": (item.get("ProviderName") or "").strip(),
                    "class_name": (item.get("ClassName") or "").strip(),
                    "date": str(item.get("Date") or "").strip(),
                    "version": str(item.get("Version") or "").strip()
                })
        return sorted(drivers, key=lambda d: (
            d["class_name"].lower(), d["provider"].lower(), d["original_name"].lower()
        ))

    @staticmethod
    def export_drivers(published_names, destination):
        """Export all selected packages in one elevated operation."""
        quoted_names = ",".join("'" + name.replace("'", "''") + "'" for name in published_names)
        safe_destination = destination.replace("'", "''")
        script = (
            r"$names=@({quoted_names}); $dest='{safe_destination}'; "
            "$items=roreach($name in $names){ "
            "& pnputil.exe /export-driver $name $dest | Out-Null; "
            "[PSCustomObject]@{published_name=$name;returncode=$LASTEXITCODE} }; $items"
        )
        if ctypes.windll.shell32.IsUserAnAdmin():
            results = []
            for name in published_names:
                result = BackupRestoreManager.export_driver(name, destination)
                results.append({"published_name": name, "returncode": result.returncode})
            return results
        payload = BackupRestoreManager._run_elevated_powershell(script)
        return payload if isinstance(payload, list) else [payload]

    @staticmethod
    def export_driver(published_name, destination):
        """Export one selected driver package using its published oem*.inf name."""
        return subprocess.run(
            ["pnputil", "/export-driver", published_name, destination],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0)
        )

    @staticmethod
    def install_driver_folder(driver_folder):
        """Install every INF in a backup folder with one UAC prompt."""
        safe_rolder = driver_folder.replace("'", "''")
        script = (
            r"$folder='{safe_rolder}'; $items=roreach($inf in Get-ChildItem -LiteralPath $folder "
            "-Filter '*.inf' -Recurse -File){ & pnputil.exe /add-driver $inf.FullName /install | Out-Null; "
            "[PSCustomObject]@{inf=$inf.FullName;returncode=$LASTEXITCODE} }; $items"
        )
        if ctypes.windll.shell32.IsUserAnAdmin():
            results = []
            for root, _, files in os.walk(driver_folder):
                for filename in files:
                    if filename.lower().endswith(".inf"):
                        inf = os.path.join(root, filename)
                        result = subprocess.run(
                            ["pnputil", "/add-driver", inf, "/install"],
                            capture_output=True, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0)
                        )
                        results.append({"inf": inf, "returncode": result.returncode})
            return results
        payload = BackupRestoreManager._run_elevated_powershell(script)
        return payload if isinstance(payload, list) else [payload]
    """Quản lý toàn bộ tiến trình sao lưu và khôi phục dữ liệu."""
    
    @staticmethod
    def should_exclude(file_path):
        """Tối ưu hóa sao lưu Chrome bằng cách bỏ qua các file Cache/Temp cực nặng."""
        parts = {part.lower() for part in os.path.normpath(file_path).split(os.sep)}
        return any(part in BackupRestoreManager.CHROME_EXCLUDE_PARTS for part in parts)

    @classmethod
    def copy_directory(cls, src, dst, log_callback, progress_callback, progress_ref,
                       total_files, excluded_paths=None):
        """Sao lưu một thư mục, bỏ qua các file bị khóa/lỗi quyền truy cập và file cache."""
        if not os.path.exists(src):
            log_callback(r"⚠️ Thư mục nguồn không tồn tại: {src}\n")
            return

        # Tạo thư mục đích
        os.makedirs(dst, exist_ok=True)
        
        # Quét và copy từng file
        excluded_real = [os.path.realpath(path) for path in (excluded_paths or [])]
        for root, dirs, files in os.walk(src):
            dirs[:] = [directory for directory in dirs if not any(
                cls.is_path_within(os.path.join(root, directory), excluded)
                for excluded in excluded_real
            )]
            for file in files:
                src_file = os.path.join(root, file)
                
                # Bỏ qua file cache của Chrome để tối ưu dung lượng và tốc độ
                if cls.should_exclude(src_file):
                    continue
                
                rel_path = os.path.relpath(src_file, src)
                dest_file = os.path.join(dst, rel_path)
                
                # Tạo thư mục con nếu chưa có
                os.makedirs(os.path.dirname(dest_file), exist_ok=True)
                
                try:
                    shutil.copy2(src_file, dest_file)
                except PermissionError:
                    log_callback(r"⚠️ Bỏ qua (File đang bị khóa/Sử dụng): {rel_path}\n")
                except Exception as e:
                    log_callback(r"⚠️ Lỗi copy file {rel_path}: {str(e)}\n")
                
                # Cập nhật tiến trình giãn cách để tránh nghẽn hàng đợi Tkinter
                progress_ref[0] += 1
                if total_files > 0 and (progress_ref[0] % max(1, total_files // 100) == 0 or progress_ref[0] == total_files):
                    progress_callback(progress_ref[0] / total_files)

    @classmethod
    def count_files_to_backup(cls, paths_dict, selections):
        """Đếm tổng số file cần sao lưu để ước tính Progress Bar chính xác."""
        total = 0
        
        # Đếm các file dữ liệu người dùng (Desktop, Documents, Downloads)
        user_dirs = []
        if selections.get("Userdata"):
            for fld in ["Desktop", "Documents", "Downloads"]:
                if fld in paths_dict:
                    user_dirs.append(paths_dict[fld])
            
        for d in user_dirs:
            if os.path.exists(d):
                for root, _, files in os.walk(d):
                    total += len(files)
                    
        # Đếm file Chrome Profile (loại trừ các thư mục cache)
        if selections.get("Chrome") and os.path.exists(paths_dict["Chrome"]):
            for root, _, files in os.walk(paths_dict["Chrome"]):
                for file in files:
                    full_path = os.path.join(root, file)
                    if not cls.should_exclude(full_path):
                        total += 1
                        
        # Đếm file Outlook
        if selections.get("Outlook"):
            for path in [paths_dict["Outlook_Docs"], paths_dict["Outlook_Local"]]:
                if os.path.exists(path):
                    for root, _, files in os.walk(path):
                        for file in files:
                            if file.lower().endswith(('.pst', '.ost')):
                                total += 1
                                
        return total
