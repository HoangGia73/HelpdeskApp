# -*- coding: utf-8 -*-
"""
Mô-đun network_scanner.py
-------------------------
Quản lý các chức năng quét dải IP, lấy MAC từ bảng ARP và cấu hình IP máy tính cục bộ.
"""

import subprocess
import re
import ctypes
import socket
import ipaddress
import concurrent.futures

from .safety import validate_ipv4

_NO_WINDOW = getattr(subprocess, "CREATE_NO_WINDOW", 0)

def _run_hidden(command, **kwargs):
    """Run a console utility without flashing a CMD window on Windows."""
    kwargs.setdefault("creationflags", _NO_WINDOW)
    return subprocess.run(command, **kwargs)

class NetworkScanner:
    """Quản lý các chức năng quét dải IP, lấy MAC và cấu hình IP máy."""
    
    @staticmethod
    def get_local_network_info():
        """Chạy ipconfig để lấy thông tin IP, Subnet Mask và Gateway của máy."""
        try:
            # Chạy ipconfig với mã hóa bảng mã OEM của Windows
            res = _run_hidden(['ipconfig'], capture_output=True, timeout=10)
            encoding = 'utf-8'
            try:
                codepage = ctypes.windll.kernel32.GetOEMCP()
                encoding = f'cp{codepage}'
            except Exception:
                encoding = 'utf-8'
            
            output = res.stdout.decode(encoding, errors='ignore')
        except Exception:
            return None, None, None

        # Tách dòng để xử lý
        lines = output.split('\n')
        
        # Nhãn nhận dạng các trường (chuyển sang chữ thường để so khớp)
        ip_labels = ["ipv4 address", "địa chỉ ipv4", "ipv4"]
        subnet_labels = ["subnet mask", "mặt nạ mạng con", "subnet"]
        gw_labels = ["default gateway", "cổng kết nối mặc định", "gateway"]
        ipv4_pat = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")
        
        adapters = []
        temp_ip = None
        temp_subnet = None
        temp_gateway = None
        temp_name = None
        in_gateway_section = False
        
        for line in lines:
            line_lower = line.lower().strip()
            if not line_lower:
                continue
                
            # Phát hiện khi chuyển vùng sang card mạng mới
            # Loại trừ dòng 'DNS Suffix' hoặc 'Description' tránh reset nhầm trong khối của card mạng
            if ("adapter" in line_lower or "card" in line_lower or "bộ thích ứng" in line_lower) and not ("suffix" in line_lower or "description" in line_lower):
                if temp_ip and temp_subnet and temp_gateway and temp_gateway != "0.0.0.0":
                    adapters.append((temp_ip, temp_subnet, temp_gateway, temp_name))
                
                # Trích xuất tên card mạng
                name_val = line.replace(':', '').strip()
                for kw in ['ethernet adapter', 'wireless lan adapter', 'lan adapter', 'adapter', 'bộ thích ứng wireless lan', 'bộ thích ứng ethernet', 'bộ thích ứng']:
                    if name_val.lower().startswith(kw):
                        name_val = name_val[len(kw):].strip()
                        break
                temp_name = name_val
                temp_ip = temp_subnet = temp_gateway = None
                in_gateway_section = False
                continue
                
            # Parse IPv4 Address bằng cách tách dấu hai chấm ':'
            if any(lbl in line_lower for lbl in ip_labels) and ":" in line:
                parts = line.split(":", 1)
                val = parts[1].strip()
                ipv4_match = ipv4_pat.search(val)
                if ipv4_match:
                    temp_ip = ipv4_match.group(0)
                in_gateway_section = False
                continue
                
            # Parse Subnet Mask bằng cách tách dấu hai chấm ':'
            if any(lbl in line_lower for lbl in subnet_labels) and ":" in line:
                parts = line.split(":", 1)
                val = parts[1].strip()
                ipv4_match = ipv4_pat.search(val)
                if ipv4_match:
                    temp_subnet = ipv4_match.group(0)
                in_gateway_section = False
                continue
                
            # Parse Default Gateway (Dòng nhãn tiêu đề ban đầu)
            if any(lbl in line_lower for lbl in gw_labels) and ":" in line:
                parts = line.split(":", 1)
                val = parts[1].strip()
                in_gateway_section = True
                if val:
                    ipv4_match = ipv4_pat.search(val)
                    if ipv4_match:
                        temp_gateway = ipv4_match.group(0)
                continue
                
            # Nếu đang ở vùng Gateway và chưa tìm thấy IPv4 Gateway (xử lý dòng IPv4 in ở dòng sau dòng IPv6)
            if in_gateway_section and not temp_gateway:
                ipv4_match = ipv4_pat.search(line.strip())
                if ipv4_match:
                    temp_gateway = ipv4_match.group(0)

        # Lưu card mạng cuối cùng
        if temp_ip and temp_subnet and temp_gateway and temp_gateway != "0.0.0.0":
            adapters.append((temp_ip, temp_subnet, temp_gateway, temp_name))
            
        # Trả về adapter đầu tiên có kết nối internet
        if adapters:
            return adapters[0]
            
        return None, None, None, None

    @staticmethod
    def ping_ip(ip, timeout_ms=250):
        """Gửi gói tin ICMP Ping kiểm tra trạng thái thiết bị."""
        try:
            # -n 1: 1 gói tin, -w timeout_ms: thời gian chờ (ms)
            cmd = ["ping", "-n", "1", "-w", str(timeout_ms), str(ip)]
            res = _run_hidden(cmd, capture_output=True, timeout=max(2.0, timeout_ms / 1000.0 + 1.0))
            out = res.stdout.decode('ascii', errors='ignore')
            # Nếu phản hồi có TTL chứng tỏ thiết bị đang online
            if "TTL=" in out.upper():
                return True
        except Exception:
            pass
        return False

    @staticmethod
    def get_mac_address(ip):
        """Truy xuất MAC Address từ bảng ARP cache sau khi ping."""
        try:
            res = _run_hidden(["arp", "-a", str(ip)], capture_output=True, text=True, timeout=3)
            lines = res.stdout.split('\n')
            for line in lines:
                if ip in line:
                    parts = line.split()
                    for part in parts:
                        part_clean = part.replace('-', ':').lower()
                        # Kiểm tra xem có định dạng MAC hợp lệ không
                        if re.match(r'^([0-9a-f]{2}[:-]){5}([0-9a-f]{2})$', part_clean):
                            return part.upper().replace('-', ':')
        except Exception:
            pass
        return "N/A"
    @staticmethod
    def get_netbios_name(ip, timeout=0.2):
        """Truy xuất tên NetBIOS trực tiếp từ thiết bị qua UDP port 137."""
        packet = (
            b'\xad\xad'  # Transaction ID
            b'\x00\x00'  # Flags
            b'\x00\x01'  # Questions = 1
            b'\x00\x00'  # Answer RRs = 0
            b'\x00\x00'  # Authority RRs = 0
            b'\x00\x00'  # Additional RRs = 0
            b'\x20'      # Name length (32)
            b'CKAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
            b'\x00'      # Name terminator
            b'\x00\x21'  # Type = NBSTAT
            b'\x00\x01'  # Class = IN
        )
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(timeout)
        try:
            sock.sendto(packet, (ip, 137))
            data, _ = sock.recvfrom(1024)
            if len(data) >= 57:
                num_names = data[56]
                offset = 57
                for _ in range(num_names):
                    if offset + 18 > len(data):
                        break
                    name_bytes = data[offset : offset + 15]
                    name_type = data[offset + 15]
                    name = name_bytes.decode('utf-8', errors='ignore').strip()
                    if name_type in (0x00, 0x20) and name and not name.startswith('__MSBROWSE__'):
                        return name
                    offset += 18
        except Exception:
            pass
        finally:
            sock.close()
        return None

    @staticmethod
    def get_hostname(ip):
        """Phân giải Hostname từ địa chỉ IP cục bộ sử dụng phương thức lai (NetBIOS + DNS/mDNS/LLMNR)."""
        # 1. Thử truy vấn NetBIOS trước (cực nhanh, ~3ms cho Windows/Samba/NAS)
        nb_name = NetworkScanner.get_netbios_name(ip, timeout=0.2)
        if nb_name:
            return nb_name
            
        # 2. Dự phòng bằng cách chạy socket.gethostbyaddr trong luồng daemon với timeout 1.0 giây
        result = [None]
        
        def work():
            try:
                host, _, _ = socket.gethostbyaddr(ip)
                if host and not host.replace('.', '').isdigit():
                    result[0] = host
            except Exception:
                pass

        import threading
        t = threading.Thread(target=work, daemon=True)
        t.start()
        t.join(timeout=1.0)
        
        if result[0]:
            return result[0]
            
        return "Unknown"

    @staticmethod
    def scan_single_ip(ip, timeout_ms=150):
        """Kiểm tra trạng thái IP, nếu online thì lấy MAC và Hostname song song."""
        is_online = NetworkScanner.ping_ip(ip, timeout_ms)
        if is_online:
            mac = NetworkScanner.get_mac_address(ip)
            hostname = NetworkScanner.get_hostname(ip)
            return {
                "ip": ip,
                "mac": mac,
                "status": "Online",
                "hostname": hostname
            }
        else:
            return {
                "ip": ip,
                "mac": "N/A",
                "status": "Offline",
                "hostname": "N/A"
            }

    @staticmethod
    def set_static_ip(adapter_name, ip, subnet, gateway, dns=None):
        """Apply a validated static IPv4 configuration through UAC."""
        return NetworkScanner._set_network_elevated(
            adapter_name, ip, subnet, gateway, dns
        )

    @staticmethod
    def set_dhcp(adapter_name):
        """Switch an adapter to DHCP through UAC."""
        return NetworkScanner._set_network_elevated(adapter_name)

    @staticmethod
    def _set_network_elevated(adapter_name, ip=None, subnet=None, gateway=None, dns=None):
        """Apply IPv4 changes with one isolated UAC request."""
        try:
            from .backup_manager import BackupRestoreManager
            safe_adapter = adapter_name.replace("'", "''")
            if ip is None:
                script = (
                    f"$adapter='{safe_adapter}'; & netsh.exe interface ipv4 set address "
                    "name=$adapter source=dhcp | Out-Null; $code=$LASTEXITCODE; "
                    "if($code -eq 0){ & netsh.exe interface ipv4 set dns name=$adapter "
                    "source=dhcp | Out-Null; $code=$LASTEXITCODE }; "
                    "[PSCustomObject]@{returncode=$code}"
                )
                success_message = "Chuyen sang DHCP thanh cong."
            else:
                ip = validate_ipv4(ip)
                subnet = validate_ipv4(subnet, allow_unspecified=True)
                gateway = validate_ipv4(gateway)
                dns = validate_ipv4(dns) if dns else ""
                safe_dns = (dns or "").replace("'", "''")
                script = (
                    f"$adapter='{safe_adapter}'; & netsh.exe interface ipv4 set address "
                    f"name=$adapter static '{ip}' '{subnet}' '{gateway}' | Out-Null; "
                    "$code=$LASTEXITCODE; "
                    f"if($code -eq 0 -and '{safe_dns}'){{ & netsh.exe interface ipv4 set dns "
                    f"name=$adapter static '{safe_dns}' primary | Out-Null; $code=$LASTEXITCODE }}; "
                    "[PSCustomObject]@{returncode=$code}"
                )
                success_message = "Thiet lap IP tinh thanh cong."
            payload = BackupRestoreManager._run_elevated_powershell(script)
            if int(payload.get("returncode", 1)) != 0:
                return False, "Windows rejected the network configuration."
            return True, success_message
        except Exception as exc:
            return False, str(exc)

    @staticmethod
    def get_all_adapters():
        """Lấy danh sách tất cả các card mạng hiện có từ ipconfig."""
        try:
            res = _run_hidden(['ipconfig'], capture_output=True, timeout=10)
            encoding = 'utf-8'
            try:
                codepage = ctypes.windll.kernel32.GetOEMCP()
                encoding = f'cp{codepage}'
            except Exception:
                encoding = 'utf-8'
            output = res.stdout.decode(encoding, errors='ignore')
        except Exception:
            return ["Ethernet", "Wi-Fi"]
            
        lines = output.split('\n')
        adapters = []
        for line in lines:
            line_lower = line.lower().strip()
            if not line_lower:
                continue
                
            if ("adapter" in line_lower or "card" in line_lower or "bộ thích ứng" in line_lower) and not ("suffix" in line_lower or "description" in line_lower):
                name_val = line.replace(':', '').strip()
                for kw in ['ethernet adapter', 'wireless lan adapter', 'lan adapter', 'adapter', 'bộ thích ứng wireless lan', 'bộ thích ứng ethernet', 'bộ thích ứng']:
                    if name_val.lower().startswith(kw):
                        name_val = name_val[len(kw):].strip()
                        break
                if name_val and name_val not in adapters:
                    adapters.append(name_val)
                    
        if not adapters:
            return ["Ethernet", "Wi-Fi"]
        return adapters
