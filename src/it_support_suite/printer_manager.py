# -*- coding: utf-8 -*-
"""
Mô-đun printer_manager.py
-------------------------
Quản lý việc quét máy in mạng và thực thi cài đặt máy in trên Windows.
"""

import subprocess
import socket
import concurrent.futures
import re
import os

class PrinterManager:
    """Quản lý quét máy in mạng và cài đặt driver, port, hàng đợi máy in."""
    
    @staticmethod
    def check_printer_port(ip, timeout_s=0.5):
        """Kiểm tra xem thiết bị có mở cổng máy in RAW (9100) không."""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(timeout_s)
                res = s.connect_ex((ip, 9100))
                if res == 0:
                    return True
        except Exception:
            pass
        return False

    @staticmethod
    def scan_printers(ips_to_scan):
        """Quét dải IP để tìm thiết bị mở cổng máy in 9100."""
        discovered_printers = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=min(64, max(1, len(ips_to_scan)))) as executor:
            future_to_ip = {executor.submit(PrinterManager.check_printer_port, ip): ip for ip in ips_to_scan}
            for future in concurrent.futures.as_completed(future_to_ip):
                ip = future_to_ip[future]
                try:
                    is_printer = future.result()
                    if is_printer:
                        discovered_printers.append(ip)
                except Exception:
                    pass
        return sorted(discovered_printers)

    @staticmethod
    def get_printer_model(ip, timeout_s=1.0):
        """Lấy tên model máy in sử dụng lệnh PJL qua cổng 9100."""
        pjl_command = b'\x1b%-12345X@PJL INFO ID\r\n\x1b%-12345X'
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(timeout_s)
                sock.connect((ip, 9100))
                sock.sendall(pjl_command)
                data = sock.recv(1024)
                response = data.decode('utf-8', errors='ignore')
                for line in response.splitlines():
                    line = line.strip()
                    if line.startswith('"') and line.endswith('"'):
                        return line.strip('"')
                    if line and not line.startswith('@') and not line.startswith('\x1b') and 'INFO' not in line:
                        return line.strip('"')
        except Exception:
            pass
        return None


    @staticmethod
    def parse_inf_driver_names(inf_path):
        """Phân tích file .inf để trích xuất danh sách tên Model máy in."""
        names = []
        try:
            content = ""
            for enc in ['utf-8', 'utf-16', 'mbcs']:
                try:
                    with open(inf_path, 'r', encoding=enc) as r:
                        content = r.read()
                    break
                except Exception:
                    continue
            if not content:
                return []
            
            lines = content.split('\n')
            in_models_section = False
            skip_sections = ['version', 'strings', 'sourcedisksnames', 'sourcedisksfiles', 'destinationdirs', 'manuracturer']
            
            for line in lines:
                line_strip = line.strip()
                if not line_strip or line_strip.startswith(';'):
                     continue
                
                if line_strip.startswith('[') and line_strip.endswith(']'):
                     section_name = line_strip[1:-1].lower()
                     if not any(skip in section_name for skip in skip_sections):
                         in_models_section = True
                     else:
                         in_models_section = False
                     continue
                     
                if in_models_section:
                     if '=' in line_strip:
                         part = line_strip.split('=', 1)[0].strip()
                         if part.startswith('"') and part.endswith('"'):
                             part = part[1:-1]
                         if part and part not in names:
                             names.append(part)
        except Exception:
            pass
        return names

    @staticmethod
    def install_printer(ip, printer_name, driver_mode, driver_model=None,
                        inf_path=None, log_callback=None):
        """Install a printer through one isolated elevated operation."""
        return PrinterManager._install_printer_elevated(
            ip, printer_name, driver_mode, driver_model, inf_path, log_callback
        )

    @staticmethod
    def _install_printer_elevated(ip, printer_name, driver_mode,
                                  driver_model=None, inf_path=None, log_callback=None):
        """Install a printer in one encoded, elevated PowerShell operation."""
        def quote(value):
            return (value or "").replace("'", "''")

        try:
            from .backup_manager import BackupRestoreManager
            port_name = f"IP_{ip}"
            driver_name = driver_model if driver_mode == "manual" else "Microsoft IPP Class Driver"
            if driver_mode == "manual" and (not inf_path or not driver_model):
                return False, "Missing INF file or printer driver model."
            if log_callback:
                log_callback("Requesting Administrator permission to install the printer...\n")
            manual_script = ""
            if driver_mode == "manual":
                manual_script = (
                    f"$model='{quote(driver_model)}'; $inf='{quote(inf_path)}'; "
                    "& rundll32.exe 'printui.dll,PrintUIEntry' '/ia' '/m' $model '/r' $inf; "
                    "if($LASTEXITCODE -ne 0){ throw 'Printer driver registration failed.' }; "
                )
            script = (
                f"$port='{quote(port_name)}'; $ip='{quote(ip)}'; "
                f"$printer='{quote(printer_name)}'; $driver='{quote(driver_name)}'; "
                "if(-not (Get-PrinterPort -Name $port -ErrorAction SilentlyContinue)){ "
                "Add-PrinterPort -Name $port -PrinterHostAddress $ip }; "
                + manual_script +
                "if(Get-Printer -Name $printer -ErrorAction SilentlyContinue){ "
                "throw 'A printer with this name already exists.' }; "
                "Add-Printer -Name $printer -PortName $port -DriverName $driver; "
                "[PSCustomObject]@{success=$true}"
            )
            payload = BackupRestoreManager._run_elevated_powershell(script)
            if payload.get("success"):
                if log_callback:
                    log_callback("Printer installed successfully.\n")
                return True, "Cai dat may in thanh cong."
            return False, "Printer installation failed."
        except Exception as exc:
            return False, str(exc)
