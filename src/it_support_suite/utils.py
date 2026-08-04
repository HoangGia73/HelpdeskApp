# -*- coding: utf-8 -*-
"""
Mô-đun utils.py
---------------
Chứa các hàm tiện ích hệ thống: kiểm tra quyền Administrator, 
truy cập Registry lấy đường dẫn thư mục người dùng (Desktop, Documents, Downloads).
"""

import os
import sys
import ctypes
import winreg

def is_admin():
    """Kiểm tra xem ứng dụng hiện tại có đang chạy dưới quyền Administrator hay không."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False

def get_shell_folder(folder_name):
    """
    Truy vấn registry để lấy đường dẫn thực tế của các thư mục hệ thống người dùng.
    Hỗ trợ xử lý trường hợp chuyển hướng thư mục sang OneDrive.
    """
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders"
        )
        val, _ = winreg.QueryValueEx(key, folder_name)
        winreg.CloseKey(key)
        # Giải mã các biến môi trường như %USERPROFILE% thành đường dẫn thực
        return os.path.expandvars(val)
    except Exception:
        # Phương án dự phòng nếu registry lỗi
        fallback_map = {
            "Desktop": os.path.expanduser("~/Desktop"),
            "Personal": os.path.expanduser("~/Documents"),
            "{374DE290-123F-4565-9164-39C4925E467B}": os.path.expanduser("~/Downloads"),
            "{7D1C3A1A-BE33-4F30-AEB5-EE9BBEA786B7}": os.path.expanduser("~/Downloads"),
        }
        return fallback_map.get(folder_name, None)

def get_downloads_folder():
    """Lấy chính xác đường dẫn thư mục Downloads của người dùng."""
    guid_new = "{7D1C3A1A-BE33-4F30-AEB5-EE9BBEA786B7}"
    guid_old = "{374DE290-123F-4565-9164-39C4925E467B}"
    
    path = get_shell_folder(guid_new)
    if path and os.path.exists(path):
        return path
    
    path = get_shell_folder(guid_old)
    if path and os.path.exists(path):
        return path
        
    return os.path.join(os.path.expanduser('~'), 'Downloads')

def get_user_data_paths():
    """Trả về danh sách đường dẫn cần sao lưu cho người dùng hiện tại."""
    desktop = get_shell_folder("Desktop")
    documents = get_shell_folder("Personal")
    downloads = get_downloads_folder()
    
    chrome = os.path.join(os.environ.get('LOCALAPPDATA', ''), r'Google\Chrome\User Data')
    outlook_docs = os.path.join(documents, 'Outlook Files')
    outlook_local = os.path.join(os.environ.get('LOCALAPPDATA', ''), r'Microsoft\Outlook')
    
    return {
        "Desktop": desktop,
        "Documents": documents,
        "Downloads": downloads,
        "Chrome": chrome,
        "Outlook_Docs": outlook_docs,
        "Outlook_Local": outlook_local
    }
