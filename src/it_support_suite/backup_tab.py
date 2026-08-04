# -*- coding: utf-8 -*-
import os
import logging
import sys
import ctypes
import shutil
import zipfile
import datetime
import time
import re
import json
import socket
import threading
import csv
import ipaddress
import subprocess
import concurrent.futures
import tempfile
from concurrent.futures import ThreadPoolExecutor
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import customtkinter

from .utils import get_user_data_paths, get_shell_folder, get_downloads_folder
from .backup_manager import BackupRestoreManager
from .backup_crypto import decrypt_file, encrypt_file, is_encrypted_backup


LOGGER = logging.getLogger(__name__)


class BackupTabMixin:
    def build_backup_tab_ui(self):
        # Lưới Tab 1
        self.tab_backup.grid_columnconfigure(0, weight=1)
        self.tab_backup.grid_rowconfigure(0, minsize=80)  # Lựa chọn đường dẫn
        self.tab_backup.grid_rowconfigure(1, minsize=110) # Các Checkbox tùy chọn
        self.tab_backup.grid_rowconfigure(2, minsize=50)  # Các nút điều khiển
        self.tab_backup.grid_rowconfigure(3, weight=1)    # Khu vực log & tiến trình
        
        # --- Khung 1: Đường dẫn lưu trữ ---
        path_frame = customtkinter.CTkFrame(self.tab_backup)
        path_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=5)
        path_frame.grid_columnconfigure(0, weight=1)
        
        lbl_path = customtkinter.CTkLabel(
            path_frame, 
            text="Đường dẫn thư mục lưu trữ (Backup Destination) / File Zip khôi phục:", 
            font=customtkinter.CTkFont(weight="bold")
        )
        lbl_path.grid(row=0, column=0, columnspan=2, sticky="w", padx=15, pady=(8, 2))
        
        self.entry_backup_path = customtkinter.CTkEntry(path_frame, placeholder_text="Bấm 'Duyệt...' để chọn đường dẫn sao lưu hoặc khôi phục...")
        self.entry_backup_path.grid(row=1, column=0, sticky="ew", padx=(15, 10), pady=(0, 10))
        
        btn_browse = customtkinter.CTkButton(path_frame, text="Duyệt...", width=100, command=self.browse_backup_path)
        btn_browse.grid(row=1, column=1, sticky="e", padx=(0, 15), pady=(0, 10))
        
        # --- Khung 2: Các mục muốn sao lưu ---
        options_frame = customtkinter.CTkFrame(self.tab_backup)
        options_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        
        lbl_options = customtkinter.CTkLabel(
            options_frame, 
            text="Các thành phần hệ thống muốn Sao lưu:", 
            font=customtkinter.CTkFont(weight="bold")
        )
        lbl_options.pack(anchor="w", padx=15, pady=(8, 5))
        
        # Layout checkbox dạng ngang
        cb_subframe = customtkinter.CTkFrame(options_frame, fg_color="transparent")
        cb_subframe.pack(fill="x", padx=15, pady=(0, 10))
        
        self.cb_driver = customtkinter.CTkCheckBox(cb_subframe, text="Driver hệ thống")
        self.cb_driver.pack(side="left", padx=(0, 20))
        self.cb_driver.select()
        self.cb_driver.configure(command=self.update_driver_selection_controls)

        self.btn_select_drivers = customtkinter.CTkButton(
            cb_subframe, text="Qu\u00e9t & ch\u1ecdn driver...", width=145,
            command=self.open_driver_selection_dialog
        )
        self.btn_select_drivers.pack(side="left", padx=(0, 10))

        self.lbl_driver_count = customtkinter.CTkLabel(
            cb_subframe, text="Ch\u01b0a qu\u00e9t", text_color="#f59e0b"
        )
        self.lbl_driver_count.pack(side="left", padx=(0, 15))
        
        self.cb_userdata = customtkinter.CTkCheckBox(cb_subframe, text="Dữ liệu người dùng")
        self.cb_userdata.pack(side="left", padx=20)
        self.cb_userdata.select()
        
        self.cb_chrome = customtkinter.CTkCheckBox(cb_subframe, text="Google Chrome Profile")
        self.cb_chrome.pack(side="left", padx=20)
        
        self.cb_outlook = customtkinter.CTkCheckBox(cb_subframe, text="Dữ liệu Mail Outlook (.PST/.OST)")
        self.cb_outlook.pack(side="left", padx=20)
        
        self.cb_zip = customtkinter.CTkCheckBox(options_frame, text="Nén toàn bộ thành file .ZIP sau khi sao lưu xong (Tự động dọn dẹp thư mục gốc)", text_color="#3b82f6")
        self.cb_zip.pack(anchor="w", padx=15, pady=(0, 10))
        self.cb_zip.select()
        self.entry_backup_password = customtkinter.CTkEntry(
            options_frame,
            placeholder_text="Mật khẩu mã hóa (tối thiểu 12 ký tự; để trống nếu chỉ tạo ZIP)",
            show="*",
        )
        self.entry_backup_password.pack(fill="x", padx=15, pady=(0, 10))

        # Re-layout backup choices into a clean, responsive two-row grid.
        for widget in cb_subframe.winfo_children():
            widget.pack_forget()
        for column in range(4):
            cb_subframe.grid_columnconfigure(column, weight=1, uniform="backup_option")

        option_widgets = (
            self.cb_driver, self.cb_userdata, self.cb_chrome, self.cb_outlook
        )
        for column, widget in enumerate(option_widgets):
            widget.grid(row=0, column=column, sticky="w", padx=12, pady=(10, 8))

        self.btn_select_drivers.grid(
            row=1, column=0, sticky="ew", padx=12, pady=(2, 10)
        )
        self.btn_select_drivers.configure(
            height=34, corner_radius=8, fg_color="#2563eb", hover_color="#1d4ed8",
            font=customtkinter.CTkFont(size=12, weight="bold")
        )
        self.lbl_driver_count.grid(
            row=1, column=1, sticky="w", padx=12, pady=(2, 10)
        )
        self.lbl_driver_count.configure(
            font=customtkinter.CTkFont(size=12, weight="bold")
        )

        options_frame.configure(
            corner_radius=12,
            fg_color=("#ffffff", "#172033"),
            border_width=1,
            border_color=("#dbe3ef", "#2b3953")
        )
        cb_subframe.configure(fg_color=("#f8fafc", "#111827"), corner_radius=10)
        self.cb_zip.configure(
            font=customtkinter.CTkFont(size=12, weight="bold"),
            text_color=("#1d4ed8", "#60a5fa")
        )

        # --- Khung 3: Nút điều khiển ---
        control_frame = customtkinter.CTkFrame(self.tab_backup, fg_color="transparent")
        control_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=5)
        
        self.btn_backup = customtkinter.CTkButton(
            control_frame, 
            text="🚀 Bắt đầu Sao lưu (Backup)", 
            fg_color="#10b981", 
            hover_color="#059669",
            font=customtkinter.CTkFont(weight="bold"), 
            command=self.start_backup
        )
        self.btn_backup.pack(side="left", padx=(10, 20), fill="x", expand=True)
        self.btn_backup.configure(height=44, corner_radius=10)
        
        self.btn_restore = customtkinter.CTkButton(
            control_frame, 
            text="🔄 Bắt đầu Khôi phục (Restore)", 
            fg_color="#3b82f6", 
            hover_color="#2563eb",
            font=customtkinter.CTkFont(weight="bold"), 
            command=self.start_restore
        )
        self.btn_restore.pack(side="right", padx=(20, 10), fill="x", expand=True)
        self.btn_restore.configure(height=44, corner_radius=10)

        # --- Khung 4: Tiến trình & Hộp hiển thị log ---
        log_frame = customtkinter.CTkFrame(self.tab_backup)
        log_frame.grid(row=3, column=0, sticky="nsew", padx=10, pady=10)
        log_frame.grid_columnconfigure(0, weight=1)
        log_frame.grid_rowconfigure(0, minsize=25)
        log_frame.grid_rowconfigure(1, weight=1)
        
        # Thanh tiến trình
        self.progress_backup = customtkinter.CTkProgressBar(log_frame, progress_color="#10b981")
        self.progress_backup.grid(row=0, column=0, sticky="ew", padx=15, pady=8)
        self.progress_backup.set(0)
        
        # Ô hiển thị Log lớn kiểu Terminal đen
        self.txt_log = customtkinter.CTkTextbox(
            log_frame, 
            fg_color="#121212", 
            text_color="#00ff00", 
            font=customtkinter.CTkFont(family="Courier New", size=12)
        )
        self.txt_log.grid(row=1, column=0, sticky="nsew", padx=15, pady=(0, 15))
        self.txt_log.configure(state="disabled")

        path_frame.configure(
            corner_radius=12,
            fg_color=("#ffffff", "#172033"),
            border_width=1,
            border_color=("#dbe3ef", "#2b3953")
        )
        self.entry_backup_path.configure(height=38, corner_radius=8)
        log_frame.configure(
            corner_radius=12,
            fg_color=("#ffffff", "#172033"),
            border_width=1,
            border_color=("#dbe3ef", "#2b3953")
        )
        self.txt_log.configure(corner_radius=8, border_width=0)

    def log(self, message):
        """Ghi nhật ký hệ thống vào Textbox (Được gọi an toàn từ luồng phụ)."""
        def update():
            self.txt_log.configure(state="normal")
            self.txt_log.insert(tk.END, message)
            self.txt_log.see(tk.END)
            self.txt_log.configure(state="disabled")
        self.after(0, update)

    def set_backup_progress(self, val):
        """Cập nhật giá trị thanh tiến trình sao lưu (Gọi an toàn)."""
        self.after(0, lambda: self.progress_backup.set(val))

    def browse_backup_path(self):
        """Chọn thư mục đích để lưu bản sao lưu."""
        path = filedialog.askdirectory(title="Chọn thư mục đích để lưu bản sao lưu")
        if path:
            self.entry_backup_path.delete(0, tk.END)
            self.entry_backup_path.insert(0, path)

    def update_driver_selection_controls(self):
        state = "normal" if self.cb_driver.get() == 1 else "disabled"
        self.btn_select_drivers.configure(state=state)

    def open_driver_selection_dialog(self):
        """Scan installed drivers and let the user select individual packages."""
        dialog = customtkinter.CTkToplevel(self)
        dialog.title("Qu\u00e9t v\u00e0 ch\u1ecdn driver \u0111\u1ec3 sao l\u01b0u")
        dialog.geometry("900x560")
        dialog.minsize(760, 450)
        dialog.transient(self)
        dialog.grab_set()
        dialog.grid_columnconfigure(0, weight=1)
        dialog.grid_rowconfigure(2, weight=1)

        search_entry = customtkinter.CTkEntry(
            dialog, placeholder_text="T\u00ecm theo t\u00ean INF, h\u00e3ng, lo\u1ea1i ho\u1eb7c phi\u00ean b\u1ea3n..."
        )
        search_entry.grid(row=0, column=0, sticky="ew", padx=15, pady=(15, 5))
        status_label = customtkinter.CTkLabel(
            dialog, text="\u0110ang qu\u00e9t driver \u0111\u00e3 c\u00e0i \u0111\u1eb7t...", anchor="w"
        )
        status_label.grid(row=1, column=0, sticky="ew", padx=18, pady=5)

        table_frame = tk.Frame(dialog, bg="#2a2d2e")
        table_frame.grid(row=2, column=0, sticky="nsew", padx=15, pady=5)
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)
        columns = ("selected", "inf", "original", "provider", "class", "version")
        driver_tree = ttk.Treeview(
            table_frame, columns=columns, show="headings", selectmode="extended"
        )
        headings = {
            "selected": "Ch\u1ecdn", "inf": "Published INF", "original": "Driver INF",
            "provider": "Nh\u00e0 cung c\u1ea5p", "class": "Lo\u1ea1i", "version": "Phi\u00ean b\u1ea3n"
        }
        widths = {
            "selected": 48, "inf": 100, "original": 130,
            "provider": 180, "class": 120, "version": 130
        }
        for col in columns:
            driver_tree.heading(col, text=headings[col])
            driver_tree.column(col, width=widths[col], anchor=(
                "center" if col in ("selected", "inf", "class", "version") else "w"
            ))
        yscroll = ttk.Scrollbar(table_frame, orient="vertical", command=driver_tree.yview)
        xscroll = ttk.Scrollbar(table_frame, orient="horizontal", command=driver_tree.xview)
        driver_tree.configure(yscrollcommand=yscroll.set, xscrollcommand=xscroll.set)
        driver_tree.grid(row=0, column=0, sticky="nsew")
        yscroll.grid(row=0, column=1, sticky="ns")
        xscroll.grid(row=1, column=0, sticky="ew")
        selected_names = {d["published_name"] for d in self.selected_drivers}

        def refresh_table(*_):
            query = search_entry.get().strip().lower()
            driver_tree.delete(*driver_tree.get_children())
            for driver in self.installed_drivers:
                if query and query not in " ".join(str(v) for v in driver.values()).lower():
                    continue
                name = driver["published_name"]
                driver_tree.insert("", "end", iid=name, values=(
                    "X" if name in selected_names else "", name, driver["original_name"],
                    driver["provider"], driver["class_name"], driver["version"]
                ))
            status_label.configure(text=(
                f"Hi\u1ec3n th\u1ecb {len(driver_tree.get_children())}/{len(self.installed_drivers)} "
                f"driver - \u0111\u00e3 ch\u1ecdn {len(selected_names)}"
            ))

        def toggle_rows(event=None):
            rows = driver_tree.selection()
            if not rows and event:
                row = driver_tree.identify_row(event.y)
                rows = (row,) if row else ()
            for name in rows:
                if name in selected_names:
                    selected_names.remove(name)
                else:
                    selected_names.add(name)
            refresh_table()

        def select_visible():
            selected_names.update(driver_tree.get_children())
            refresh_table()

        def clear_selection():
            selected_names.clear()
            refresh_table()

        def save_selection():
            self.selected_drivers = [
                d for d in self.installed_drivers if d["published_name"] in selected_names
            ]
            self.lbl_driver_count.configure(
                text=f"\u0110\u00e3 ch\u1ecdn {len(self.selected_drivers)} driver",
                text_color="#10b981" if self.selected_drivers else "#ef4444"
            )
            dialog.destroy()

        buttons = customtkinter.CTkFrame(dialog, fg_color="transparent")
        buttons.grid(row=3, column=0, sticky="ew", padx=15, pady=(5, 15))
        customtkinter.CTkButton(
            buttons, text="Ch\u1ecdn t\u1ea5t c\u1ea3 \u0111ang hi\u1ec3n th\u1ecb", width=180,
            command=select_visible
        ).pack(side="left", padx=(0, 8))
        customtkinter.CTkButton(
            buttons, text="B\u1ecf ch\u1ecdn t\u1ea5t c\u1ea3", width=130,
            fg_color="#6b7280", command=clear_selection
        ).pack(side="left")
        customtkinter.CTkButton(
            buttons, text="X\u00e1c nh\u1eadn", width=120,
            fg_color="#10b981", command=save_selection
        ).pack(side="right")
        driver_tree.bind("<Double-1>", toggle_rows)
        driver_tree.bind("<space>", toggle_rows)
        search_entry.bind("<KeyRelease>", refresh_table)

        def scan_worker():
            try:
                self.installed_drivers = BackupRestoreManager.scan_installed_drivers()
                dialog.after(0, refresh_table)
            except Exception as exc:
                def show_error():
                    status_label.configure(text=f"L\u1ed7i qu\u00e9t driver: {exc}", text_color="#ef4444")
                    messagebox.showerror("Kh\u00f4ng th\u1ec3 qu\u00e9t driver", str(exc), parent=dialog)
                dialog.after(0, show_error)

        if self.installed_drivers:
            refresh_table()
        else:
            threading.Thread(target=scan_worker, daemon=True).start()

    def start_backup(self):
        """Kích hoạt tiến trình sao lưu chạy trên luồng riêng để tránh đơ GUI."""
        if self.backup_running:
            messagebox.showwarning("Cảnh báo", "Một tiến trình sao lưu/khôi phục khác đang chạy!")
            return
            
        dest_parent = self.entry_backup_path.get().strip()
        if not dest_parent or not os.path.exists(dest_parent):
            messagebox.showerror("Lỗi đường dẫn", "Vui lòng chọn thư mục lưu trữ hợp lệ trước khi sao lưu!")
            return
            
        selections = {
            "Driver": self.cb_driver.get() == 1,
            "Userdata": self.cb_userdata.get() == 1,
            "Chrome": self.cb_chrome.get() == 1,
            "Outlook": self.cb_outlook.get() == 1
        }

        if selections["Driver"] and not self.selected_drivers:
            messagebox.showwarning(
                "Ch\u01b0a ch\u1ecdn driver",
                "H\u00e3y b\u1ea5m 'Qu\u00e9t & ch\u1ecdn driver...' v\u00e0 ch\u1ecdn \u00edt nh\u1ea5t m\u1ed9t driver."
            )
            return

        locked_apps = []
        if selections["Chrome"] and BackupRestoreManager.is_process_running("chrome.exe"):
            locked_apps.append("Google Chrome")
        if selections["Outlook"] and BackupRestoreManager.is_process_running("outlook.exe"):
            locked_apps.append("Microsoft Outlook")
        if locked_apps:
            messagebox.showerror(
                "\u1ee8ng d\u1ee5ng c\u00f2n \u0111ang ch\u1ea1y",
                "Vui l\u00f2ng \u0111\u00f3ng ho\u00e0n to\u00e0n " + ", ".join(locked_apps) +
                " (k\u1ec3 c\u1ea3 ti\u1ebfn tr\u00ecnh ch\u1ea1y n\u1ec1n) r\u1ed3i th\u1eed l\u1ea1i."
            )
            return
        
        if not any(selections.values()):
            messagebox.showwarning("Cảnh báo", "Vui lòng tích chọn ít nhất một thành phần để sao lưu!")
            return
            
        zip_after = self.cb_zip.get() == 1
        encryption_password = self.entry_backup_password.get()
        if encryption_password and len(encryption_password) < 12:
            messagebox.showerror("Mật khẩu yếu", "Mật khẩu mã hóa phải có ít nhất 12 ký tự.")
            return
        if encryption_password:
            zip_after = True
        
        self.backup_running = True
        self.btn_backup.configure(state="disabled")
        self.btn_restore.configure(state="disabled")
        self.progress_backup.set(0)
        
        self.txt_log.configure(state="normal")
        self.txt_log.delete("1.0", tk.END)
        self.txt_log.configure(state="disabled")
        
        threading.Thread(
            target=self.run_backup, 
            args=(dest_parent, selections, zip_after, list(self.selected_drivers), encryption_password),
            daemon=True
        ).start()

    def run_backup(self, dest_parent, selections, zip_after, selected_drivers=None, encryption_password=""):
        """Tiến trình xử lý sao lưu chạy dưới nền."""
        try:
            import subprocess
            import ctypes
            
            username = os.environ.get('USERNAME', 'User')
            date_str = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            backup_folder_name = f"Backup_{username}_{date_str}"
            backup_path = os.path.normpath(os.path.join(dest_parent, backup_folder_name))
            
            if selections["Chrome"] or selections["Outlook"]:
                self.log("⚠️ LƯU Ý: Vui lòng đóng hoàn toàn Google Chrome và Outlook để tránh lỗi khóa dữ liệu.\n\n")
                
            self.log(f"📅 Bắt đầu sao lưu hệ thống vào: {backup_path}\n")
            
            paths_dict = get_user_data_paths()

            total_files, estimated_size = BackupRestoreManager.analyze_backup(
                paths_dict, selections, excluded_paths=[backup_path]
            )
            required_size = int(estimated_size * (2.1 if zip_after else 1.1))
            free_size = shutil.disk_usage(dest_parent).free
            if required_size > free_size:
                raise RuntimeError(
                    f"Khong du dung luong. Can khoang {required_size / (1024 ** 3):.2f} GB, "
                    f"chi con {free_size / (1024 ** 3):.2f} GB."
                )
            
            self.log("📊 Đang ước tính dữ liệu cần sao lưu...\n")
            self.log(f"Phat hien {total_files} file can sao luu.\n")
            
            selected_drivers = selected_drivers or []
            driver_weight = len(selected_drivers) if selections["Driver"] else 0
            zip_weight = int((total_files + driver_weight) * 0.1) if zip_after else 0
            
            total_steps = max(1, total_files + driver_weight + zip_weight)
            progress_ref = [0]
            
            os.makedirs(backup_path, exist_ok=True)
            
            metadata = {
                "backup_time": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "username": username,
                "items": {}
            }

            if selections["Driver"]:
                driver_dest = os.path.normpath(os.path.join(backup_path, "Drivers"))
                os.makedirs(driver_dest, exist_ok=True)
                self.log(f"Bat dau sao luu {len(selected_drivers)} driver da chon...\n")
                exported_drivers = []
                export_results = BackupRestoreManager.export_drivers(
                    [driver["published_name"] for driver in selected_drivers], driver_dest
                )
                result_codes = {
                    item.get("published_name"): int(item.get("returncode", 1))
                    for item in export_results
                }
                for index, driver in enumerate(selected_drivers, 1):
                    name = driver["published_name"]
                    label = driver["original_name"] or name
                    self.log(
                        f"[{index}/{len(selected_drivers)}] {label} ({driver['provider']})...\n"
                    )
                    if result_codes.get(name, 1) == 0:
                        exported_drivers.append(driver)
                        self.log(f"OK - Da sao luu: {name}\n")
                    else:
                        self.log(f"LOI - Khong the sao luu {name}.\n")
                    progress_ref[0] += 1
                    self.set_backup_progress(progress_ref[0] / total_steps)

                if exported_drivers:
                    self.log(
                        f"Da sao luu {len(exported_drivers)}/{len(selected_drivers)} driver.\n"
                    )
                    metadata["items"]["Drivers"] = "Drivers"
                    metadata["selected_drivers"] = exported_drivers
                else:
                    self.log("Khong co driver nao duoc sao luu thanh cong.\n")
            
            # --- SAO LƯU DRIVER HỆ THỐNG ---
            if selections["Userdata"]:
                for folder in ["Desktop", "Documents", "Downloads"]:
                    src_dir = paths_dict[folder]
                    dst_dir = os.path.join(backup_path, folder)
                    self.log(f"➜ Đang sao lưu thư mục: {folder}...\n")
                    BackupRestoreManager.copy_directory(
                        src_dir, dst_dir, self.log, self.set_backup_progress, progress_ref,
                        total_steps, excluded_paths=[backup_path]
                    )
                    self.log(f"✅ Đã sao lưu xong thư mục: {folder}\n")
                    metadata["items"][folder] = src_dir

            # --- SAO LƯU CHROME PROFILE ---
            if selections["Chrome"]:
                src_dir = paths_dict["Chrome"]
                dst_dir = os.path.join(backup_path, "Chrome")
                self.log("➜ Đang sao lưu cấu hình Google Chrome (Đã loại trừ bộ nhớ đệm cache)...\n")
                BackupRestoreManager.copy_directory(
                    src_dir, dst_dir, self.log, self.set_backup_progress, progress_ref,
                    total_steps, excluded_paths=[backup_path]
                )
                self.log("✅ Đã sao lưu xong Chrome Profile.\n")
                metadata["items"]["Chrome"] = src_dir

            # --- SAO LƯU DỮ LIỆU MAIL OUTLOOK ---
            if selections["Outlook"]:
                self.log("➜ Đang quét dữ liệu Outlook (.pst, .ost)...\n")
                dst_outlook = os.path.join(backup_path, "Outlook")
                os.makedirs(dst_outlook, exist_ok=True)
                
                outlook_files = []
                for key_path in ["Outlook_Docs", "Outlook_Local"]:
                    p = paths_dict[key_path]
                    if os.path.exists(p):
                        for root, _, files in os.walk(p):
                            for file in files:
                                if file.lower().endswith(('.pst', '.ost')):
                                    source_file = os.path.join(root, file)
                                    relative = os.path.join(key_path, os.path.relpath(source_file, p))
                                    outlook_files.append((source_file, relative))
                
                if outlook_files:
                    metadata["items"]["Outlook"] = {}
                    for file_path, relative in outlook_files:
                        filename = os.path.basename(file_path)
                        self.log(f"➜ Đang sao lưu Mail file: {filename}...\n")
                        try:
                            destination_file = os.path.join(dst_outlook, relative)
                            os.makedirs(os.path.dirname(destination_file), exist_ok=True)
                            shutil.copy2(file_path, destination_file)
                            self.log(f"✅ Sao lưu thành công file Outlook: {filename}\n")
                            metadata["items"]["Outlook"][relative] = file_path
                        except PermissionError:
                            self.log(f"⚠️ Bỏ qua (Đang bị khóa): {filename}. Hãy đóng Outlook và thử lại!\n")
                        except Exception as e:
                            self.log(f"⚠️ Lỗi copy file Outlook: {filename}. Chi tiết: {str(e)}\n")
                        
                        progress_ref[0] += 1
                        self.set_backup_progress(progress_ref[0] / total_steps)
                else:
                    self.log("ℹ️ Không phát hiện dữ liệu Mail Outlook (.pst, .ost) trên máy.\n")

            # Lưu file Metadata vào bản backup
            with open(os.path.join(backup_path, "backup_metadata.json"), "w", encoding="utf-8") as f:
                json.dump(metadata, f, ensure_ascii=False, indent=4)

            # --- NÉN THÀNH FILE ZIP ---
            if zip_after:
                zip_path = backup_path + ".zip"
                zip_temp_path = zip_path + ".partial"
                self.log("➜ Đang nén toàn bộ thư mục sao lưu thành file ZIP...\n")
                
                all_files_to_zip = []
                for root, _, files in os.walk(backup_path):
                    for f in files:
                        all_files_to_zip.append(os.path.join(root, f))
                
                z_total = len(all_files_to_zip)
                if z_total > 0:
                    with zipfile.ZipFile(zip_temp_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                        for idx, f_path in enumerate(all_files_to_zip):
                            rel = os.path.relpath(f_path, backup_path)
                            zipf.write(f_path, rel)
                            
                            # Cập nhật tiến trình giãn cách để tránh nghẽn hàng đợi Tkinter
                            if z_total > 0 and (idx % max(1, z_total // 50) == 0 or idx == z_total - 1):
                                z_progress = int(((idx + 1) / z_total) * zip_weight)
                                self.set_backup_progress((progress_ref[0] + z_progress) / total_steps)
                    
                    self.log("✅ Nén file ZIP hoàn tất.\n")
                    
                    with zipfile.ZipFile(zip_temp_path, 'r') as verify_zip:
                        bad_file = verify_zip.testzip()
                        if bad_file:
                            raise RuntimeError(f"ZIP verification failed at: {bad_file}")
                        if len(verify_zip.infolist()) != z_total:
                            raise RuntimeError("ZIP verification failed: file count mismatch")
                    os.replace(zip_temp_path, zip_path)
                    if encryption_password:
                        encrypted_path = backup_path + ".itsbackup"
                        self.log("Đang mã hóa và xác thực bản backup...\n")
                        encrypt_file(zip_path, encrypted_path, encryption_password)
                        os.remove(zip_path)
                        self.log(f"Đã tạo backup mã hóa: {encrypted_path}\n")

                    try:
                        shutil.rmtree(backup_path)
                        self.log("🗑️ Đã xóa thư mục tạm thời chưa nén.\n")
                    except Exception as e:
                        self.log(f"⚠️ Không thể dọn dẹp thư mục tạm: {str(e)}\n")
                else:
                    self.log("⚠️ Thư mục sao lưu trống, không thể nén ZIP.\n")

            self.set_backup_progress(1.0)
            self.log("\n🎉 TIẾN TRÌNH SAO LƯU HOÀN THÀNH MỸ MÃN! 🎉\n")
            
        except Exception as e:
            LOGGER.exception("Backup failed")
            self.log(f"\n❌ Đã xảy ra lỗi nghiêm trọng trong tiến trình sao lưu: {str(e)}\n")
        finally:
            self.backup_running = False
            self.after(0, lambda: self.btn_backup.configure(state="normal"))
            self.after(0, lambda: self.btn_restore.configure(state="normal"))

    def start_restore(self):
        """Kích hoạt tiến trình khôi phục chạy dưới nền."""
        if self.backup_running:
            messagebox.showwarning("Cảnh báo", "Một tiến trình sao lưu/khôi phục khác đang chạy!")
            return
            
        selected_path = filedialog.askopenfilename(
            title="Chọn file ZIP sao lưu để khôi phục",
            filetypes=[("Encrypted backups", "*.itsbackup"), ("Zip Files", "*.zip"), ("All Files", "*.*")]
        )
        if not selected_path:
            selected_path = filedialog.askdirectory(title="Hoặc chọn thư mục sao lưu chưa nén")
            if not selected_path:
                return

        restore_password = ""
        if os.path.isfile(selected_path) and is_encrypted_backup(selected_path):
            restore_password = simpledialog.askstring("Mật khẩu backup", "Nhập mật khẩu giải mã:", show="*", parent=self)
            if restore_password is None:
                return

        self.entry_backup_path.delete(0, tk.END)
        self.entry_backup_path.insert(0, selected_path)
        
        self.backup_running = True
        self.btn_backup.configure(state="disabled")
        self.btn_restore.configure(state="disabled")
        self.progress_backup.set(0)
        
        self.txt_log.configure(state="normal")
        self.txt_log.delete("1.0", tk.END)
        self.txt_log.configure(state="disabled")
        
        threading.Thread(
            target=self.run_restore,
            args=(selected_path, restore_password),
            daemon=True
        ).start()

    def run_restore(self, selected_path, restore_password=""):
        """Tiến trình khôi phục dữ liệu chạy dưới nền."""
        temp_dir = None
        decrypted_zip = None
        try:
            import subprocess
            import ctypes
            
            self.log(f"📅 Bắt đầu tiến trình khôi phục từ nguồn: {selected_path}\n")
            restore_source_dir = os.path.normpath(selected_path)
            if os.path.isfile(selected_path) and is_encrypted_backup(selected_path):
                decrypted_zip = os.path.join(tempfile.gettempdir(), f"its_restore_{os.getpid()}.zip")
                decrypt_file(selected_path, decrypted_zip, restore_password)
                selected_path = decrypted_zip
                restore_source_dir = selected_path
            
            if os.path.isfile(selected_path) and selected_path.lower().endswith('.zip'):
                temp_parent = os.path.dirname(selected_path)
                temp_dir = tempfile.mkdtemp(prefix="its_restore_", dir=temp_parent)
                
                self.log("📦 Đang giải nén file sao lưu ZIP vào thư mục tạm...\n")
                with zipfile.ZipFile(selected_path, 'r') as zipf:
                    BackupRestoreManager.safe_extract_zip(zipf, temp_dir)
                restore_source_dir = temp_dir
                self.log("✅ Giải nén hoàn tất.\n")
            
            metadata_file = os.path.join(restore_source_dir, "backup_metadata.json")
            metadata = None
            if os.path.exists(metadata_file):
                try:
                    with open(metadata_file, "r", encoding="utf-8") as f:
                        metadata = json.load(f)
                    self.log(f"ℹ️ Phát hiện bản sao lưu của User: {metadata.get('username')}, tạo ngày: {metadata.get('backup_time')}\n")
                except Exception:
                    pass
            
            current_paths = get_user_data_paths()
            
            subfolders = [f for f in os.listdir(restore_source_dir) if os.path.isdir(os.path.join(restore_source_dir, f))]
            
            total_tasks = len(subfolders)
            if total_tasks == 0:
                self.log("⚠️ Thư mục khôi phục trống hoặc không hợp lệ.\n")
                return
                
            task_done = 0
            
            for folder in subfolders:
                folder_path = os.path.join(restore_source_dir, folder)
                
                # --- KHÔI PHỤC DRIVER HỆ THỐNG ---
                if folder == "Drivers":
                    self.log("Requesting Administrator permission to restore drivers...\n")
                    results = BackupRestoreManager.install_driver_folder(folder_path)
                    succeeded = sum(1 for item in results if int(item.get("returncode", 1)) == 0)
                    self.log(f"Driver restore result: {succeeded}/{len(results)} installed.\n")
                    task_done += 1
                    self.set_backup_progress(task_done / total_tasks)
                    continue
                elif folder in ["Desktop", "Documents", "Downloads"]:
                    target_dst = current_paths.get(folder)
                        
                    if target_dst:
                        self.log(f"➜ Đang khôi phục thư mục {folder} về: {target_dst}...\n")
                        self.copy_tree_restore(folder_path, target_dst)
                        self.log(f"✅ Đã khôi phục thành công: {folder}\n")
                
                # --- KHÔI PHỤC CHROME PROFILE ---
                elif folder == "Chrome":
                    target_dst = current_paths.get("Chrome")
                        
                    if target_dst:
                        self.log(f"➜ Đang khôi phục Chrome Profile về: {target_dst}...\n")
                        self.copy_tree_restore(folder_path, target_dst)
                        self.log("✅ Đã khôi phục thành công cấu hình Google Chrome.\n")

                # --- KHÔI PHỤC OUTLOOK MAIL ---
                elif folder == "Outlook":
                    self.log("➜ Đang khôi phục dữ liệu Outlook...\n")
                    outlook_meta = metadata.get("items", {}).get("Outlook", {}) if metadata else {}
                    
                    for file in os.listdir(folder_path):
                        src_file = os.path.join(folder_path, file)
                        dst_file = None

                        if os.path.isdir(src_file):
                            target_base = current_paths.get(file)
                            if target_base:
                                self.copy_tree_restore(src_file, target_base)
                                self.log(f"OK - Restored Outlook group: {file}\n")
                            continue
                        
                        dst_file = os.path.join(current_paths["Outlook_Docs"], file)
                            
                        if dst_file:
                            os.makedirs(os.path.dirname(dst_file), exist_ok=True)
                            try:
                                self.log(f"➜ Đang sao chép file Mail {file} về: {dst_file}...\n")
                                shutil.copy2(src_file, dst_file)
                                self.log(f"✅ Đã khôi phục xong file: {file}\n")
                            except PermissionError:
                                self.log(f"⚠️ Bỏ qua (Bị khóa): {file}. Vui lòng tắt Outlook và thử lại.\n")
                            except Exception as e:
                                self.log(f"⚠️ Lỗi khôi phục file {file}: {str(e)}\n")
            
                task_done += 1
                self.set_backup_progress(task_done / total_tasks)
            
            self.set_backup_progress(1.0)
            self.log("\n🎉 TIẾN TRÌNH KHÔI PHỤC HOÀN THÀNH MỸ MÃN! 🎉\n")
            
        except Exception as e:
            LOGGER.exception("Restore failed")
            self.log(f"\n❌ Đã xảy ra lỗi trong tiến trình khôi phục: {str(e)}\n")
        finally:
            if decrypted_zip and os.path.exists(decrypted_zip):
                try:
                    os.remove(decrypted_zip)
                except OSError:
                    pass
            if temp_dir and os.path.exists(temp_dir):
                try:
                    shutil.rmtree(temp_dir)
                    self.log("🗑️ Đã dọn dẹp thư mục tạm giải nén.\n")
                except Exception:
                    pass
                    
            self.backup_running = False
            self.after(0, lambda: self.btn_backup.configure(state="normal"))
            self.after(0, lambda: self.btn_restore.configure(state="normal"))

    def copy_tree_restore(self, src, dst):
        """Sao chép thư mục khôi phục và xử lý ngoại lệ file bị khóa."""
        import shutil
        os.makedirs(dst, exist_ok=True)
        for root, _, files in os.walk(src):
            for file in files:
                src_file = os.path.join(root, file)
                rel = os.path.relpath(src_file, src)
                dst_file = os.path.join(dst, rel)
                
                os.makedirs(os.path.dirname(dst_file), exist_ok=True)
                try:
                    shutil.copy2(src_file, dst_file)
                except PermissionError:
                    self.log(f"⚠️ Bỏ qua (Đang bị khóa): {rel}\n")
                except Exception as e:
                    self.log(f"⚠️ Lỗi copy file {rel}: {str(e)}\n")
