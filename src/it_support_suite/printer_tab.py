# -*- coding: utf-8 -*-
import os
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
from concurrent.futures import ThreadPoolExecutor
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import customtkinter

from .printer_manager import PrinterManager
from .network_scanner import NetworkScanner


class PrinterTabMixin:
    def build_printer_tab_ui(self):
        # Lưới Tab 3: Cài đặt máy in
        self.tab_printer.grid_columnconfigure(0, weight=4) # Khung Cấu hình (Trái)
        self.tab_printer.grid_columnconfigure(1, weight=6) # Khung Tiến trình & Log (Phải)
        self.tab_printer.grid_rowconfigure(0, weight=1)
        
        # --- CỘT TRÁI: THIẾT LẬP MÁY IN MẠNG ---
        left_frame = customtkinter.CTkFrame(self.tab_printer)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(10, 5), pady=10)
        
        # Khung 1: Địa chỉ IP & Quét
        scan_group = customtkinter.CTkFrame(left_frame)
        scan_group.pack(fill="x", padx=15, pady=15)
        
        lbl_scan_title = customtkinter.CTkLabel(
            scan_group, 
            text="🔍 DÒ TÌM MÁY IN TRONG MẠNG", 
            font=customtkinter.CTkFont(size=14, weight="bold")
        )
        lbl_scan_title.pack(anchor="w", padx=15, pady=(10, 10))
        
        self.btn_scan_printer = customtkinter.CTkButton(
            scan_group, 
            text="🔍 Bắt đầu quét máy in mạng", 
            height=30,
            command=self.start_printer_scan
        )
        self.btn_scan_printer.pack(padx=20, pady=5, fill="x")
        
        self.combo_discovered_printers = customtkinter.CTkOptionMenu(
            scan_group,
            values=["(Bấm Quét để tìm máy in)"],
            command=self.on_select_discovered_printer
        )
        self.combo_discovered_printers.pack(padx=20, pady=(5, 15), fill="x")
        
        # Khung 2: Nhập thông tin thủ công
        manual_group = customtkinter.CTkFrame(left_frame)
        manual_group.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        lbl_manual_title = customtkinter.CTkLabel(
            manual_group, 
            text="⚙️ THÔNG TIN MÁY IN CÀI ĐẶT", 
            font=customtkinter.CTkFont(size=14, weight="bold")
        )
        lbl_manual_title.pack(anchor="w", padx=15, pady=(10, 10))
        
        lbl_printer_ip = customtkinter.CTkLabel(manual_group, text="Địa chỉ IP Máy in:", anchor="w")
        lbl_printer_ip.pack(fill="x", padx=20, pady=2)
        self.entry_printer_ip = customtkinter.CTkEntry(manual_group, placeholder_text="Ví dụ: 192.168.1.100")
        self.entry_printer_ip.pack(fill="x", padx=20, pady=5)
        
        lbl_printer_name = customtkinter.CTkLabel(manual_group, text="Tên hiển thị Máy in:", anchor="w")
        lbl_printer_name.pack(fill="x", padx=20, pady=2)
        self.entry_printer_name = customtkinter.CTkEntry(manual_group, placeholder_text="Ví dụ: HP_LaserJet_Ke_Toan")
        self.entry_printer_name.pack(fill="x", padx=20, pady=5)
        
        lbl_driver_mode = customtkinter.CTkLabel(manual_group, text="Chế độ Driver máy in:", anchor="w")
        lbl_driver_mode.pack(fill="x", padx=20, pady=2)
        
        self.var_driver_mode = tk.StringVar(value="auto")
        
        def on_driver_mode_change():
            mode = self.var_driver_mode.get()
            if mode == "auto":
                self.btn_browse_inr.configure(state="disabled")
                self.combo_inf_models.configure(state="disabled")
            else:
                self.btn_browse_inr.configure(state="normal")
                self.combo_inf_models.configure(state="normal")
                
        rb_subframe = customtkinter.CTkFrame(manual_group, fg_color="transparent")
        rb_subframe.pack(fill="x", padx=20, pady=5)
        
        rb_auto = customtkinter.CTkRadioButton(
            rb_subframe, 
            text="Tự động (Windows IPP)", 
            variable=self.var_driver_mode, 
            value="auto", 
            command=on_driver_mode_change
        )
        rb_auto.pack(side="left", padx=(0, 20))
        
        rb_manual = customtkinter.CTkRadioButton(
            rb_subframe, 
            text="Thủ công (chọn file .inf)", 
            variable=self.var_driver_mode, 
            value="manual", 
            command=on_driver_mode_change
        )
        rb_manual.pack(side="left", padx=20)
        
        # Các ô nhập Driver thủ công (.inf)
        self.btn_browse_inr = customtkinter.CTkButton(
            manual_group, 
            text="📂 Chọn file Driver (.inf)...", 
            height=25, 
            state="disabled",
            fg_color="#3a3a3a",
            hover_color="#4a4a4a",
            command=self.browse_inf_rile
        )
        self.btn_browse_inr.pack(fill="x", padx=20, pady=5)
        
        self.combo_inf_models = customtkinter.CTkOptionMenu(
            manual_group,
            values=["(Chọn file .inf để load danh sách model)"],
            state="disabled"
        )
        self.combo_inf_models.pack(fill="x", padx=20, pady=5)
        
        # --- CỘT PHẢI: LOG TIẾN TRÌNH & CÀI ĐẶT ---
        right_frame = customtkinter.CTkFrame(self.tab_printer)
        right_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 10), pady=10)
        
        lbl_log_title = customtkinter.CTkLabel(
            right_frame, 
            text="📋 TRẠNG THÁI CÀI ĐẶT MÁY IN", 
            font=customtkinter.CTkFont(size=14, weight="bold")
        )
        lbl_log_title.pack(anchor="w", padx=15, pady=(10, 5))
        
        # Hộp log máy in
        self.txt_printer_log = customtkinter.CTkTextbox(
            right_frame, 
            fg_color="#121212", 
            text_color="#00ff00", 
            font=customtkinter.CTkFont(family="Courier New", size=12)
        )
        self.txt_printer_log.pack(fill="both", expand=True, padx=15, pady=10)
        self.txt_printer_log.configure(state="disabled")
        
        # Thanh tiến trình
        self.progress_printer = customtkinter.CTkProgressBar(right_frame, progress_color="#3b82f6")
        self.progress_printer.pack(fill="x", padx=15, pady=5)
        self.progress_printer.set(0)
        
        # Nút bấm cài đặt máy in
        self.btn_install_printer = customtkinter.CTkButton(
            right_frame, 
            text="📥 KHỞI CHẠY CÀI ĐẶT MÁY IN", 
            fg_color="#3b82f6", 
            hover_color="#2563eb",
            font=customtkinter.CTkFont(size=14, weight="bold"),
            height=35,
            command=self.start_printer_install
        )
        self.btn_install_printer.pack(fill="x", padx=15, pady=(5, 15))

    def log_printer(self, message):
        """Ghi log vào ô hiển thị trạng thái cài đặt máy in."""
        self.after(0, lambda: self._log_printer_threadsafe(message))

    def _log_printer_threadsafe(self, message):
        self.txt_printer_log.configure(state="normal")
        self.txt_printer_log.insert(tk.END, message)
        self.txt_printer_log.see(tk.END)
        self.txt_printer_log.configure(state="disabled")

    def on_select_discovered_printer(self, choice):
        """Tự động điền IP khi chọn máy in quét được."""
        if choice and choice != "(Bấm Quét để tìm máy in)" and choice != "Không tìm thấy máy in nào":
            # Tách IP và Hostname
            parts = choice.split()
            ip = parts[0]
            
            # Trích xuất hostname nằm trong ngoặc đơn nếu có
            hostname = None
            if len(parts) > 1:
                match = re.search(r'\((.*?)\)', choice)
                if match:
                    hostname = match.group(1)
            
            self.entry_printer_ip.delete(0, tk.END)
            self.entry_printer_ip.insert(0, ip)
            
            self.entry_printer_name.delete(0, tk.END)
            if hostname and hostname != "Unknown":
                self.entry_printer_name.insert(0, f"Printer_{hostname}")
            else:
                clean_ip = ip.replace('.', '_')
                self.entry_printer_name.insert(0, f"Printer_{clean_ip}")

    def browse_inf_rile(self):
        """Mở hộp thoại chọn file .inf và parse danh sách Model máy in."""
        file_path = filedialog.askopenfilename(
            parent=self,
            filetypes=[("Driver Files", "*.inf"), ("All Files", "*.*")],
            title="Chọn file Driver máy in (.inf)"
        )
        if not file_path:
            return
            
        self.selected_inf_path = file_path
        self.log_printer(f"📂 Đã chọn file Driver: {file_path}\n➜ Đang phân tích (parse) danh sách model...\n")
        
        models = PrinterManager.parse_inf_driver_names(file_path)
        if models:
            self.log_printer(f"✅ Tìm thấy {len(models)} model máy in trong file .inf.\n")
            self.combo_inf_models.configure(values=models)
            self.combo_inf_models.set(models[0])
        else:
            self.log_printer("⚠️ Cảnh báo: Không phân tích được model nào từ file .inf. Bạn có thể tự gõ tên Driver nếu biết.\n")
            self.combo_inf_models.configure(values=["(Không phân tích được model nào)"])
            self.combo_inf_models.set("(Không phân tích được model nào)")

    def start_printer_scan(self):
        """Khởi chạy quét tìm máy in trong mạng (TCP Port 9100)."""
        start_ip = self.entry_start_ip.get().strip()
        end_ip = self.entry_end_ip.get().strip()
        
        try:
            start_addr = ipaddress.IPv4Address(start_ip)
            end_addr = ipaddress.IPv4Address(end_ip)
        except Exception:
            messagebox.showwarning("Cảnh báo", "Vui lòng cấu hình/nhập dải IP quét hợp lệ ở Tab Quét mạng trước!")
            return
            
        ips_to_scan = []
        curr = start_addr
        while curr <= end_addr:
            ips_to_scan.append(str(curr))
            curr += 1
            
        if len(ips_to_scan) > 256:
            if not messagebox.askyesno("Xác nhận", f"Dải IP cần quét lớn ({len(ips_to_scan)} IP). Tiến trình quét tìm máy in có thể lâu. Bạn có muốn tiếp tục?"):
                return

        self.btn_scan_printer.configure(state="disabled", text="🔍 Đang quét máy in...")
        self.txt_printer_log.configure(state="normal")
        self.txt_printer_log.delete("1.0", tk.END)
        self.txt_printer_log.configure(state="disabled")
        
        self.log_printer(f"📅 Bắt đầu quét tìm máy in trên dải IP: {start_ip} -> {end_ip}...\n")
        self.progress_printer.set(0.2)
        
        def run_scan():
            printers = PrinterManager.scan_printers(ips_to_scan)
            
            # Phân giải tên máy in (Model name qua PJL hoặc Hostname) song song
            printers_with_names = []
            if printers:
                def get_printer_display_name(p):
                    # 1. Thử lấy tên model qua PJL thô cổng 9100
                    model = PrinterManager.get_printer_model(p)
                    if model:
                        return model
                    # 2. Dự phòng bằng Hostname
                    h = NetworkScanner.get_hostname(p)
                    if h and h != "Unknown":
                        return h
                    return None

                with concurrent.futures.ThreadPoolExecutor(max_workers=min(32, max(1, len(printers)))) as executor:
                    names = list(executor.map(get_printer_display_name, printers))
                
                for p, n in zip(printers, names):
                    if n:
                        printers_with_names.append(f"{p} ({n})")
                    else:
                        printers_with_names.append(p)
            
            def on_done():
                self.progress_printer.set(1.0)
                self.btn_scan_printer.configure(state="normal", text="🔍 Bắt đầu quét máy in mạng")
                if printers:
                    self.log_printer(f"🎉 Quét hoàn tất. Tìm thấy {len(printers)} máy in trực tuyến:\n")
                    for p_with_name in printers_with_names:
                        self.log_printer(f"   + IP: {p_with_name} (Cổng 9100 đang Mở)\n")
                    self.combo_discovered_printers.configure(values=printers_with_names)
                    self.combo_discovered_printers.set(printers_with_names[0])
                    self.on_select_discovered_printer(printers_with_names[0])
                else:
                    self.log_printer("❌ Quét hoàn tất. Không tìm thấy thiết bị nào mở cổng máy in 9100.\n")
                    self.combo_discovered_printers.configure(values=["Không tìm thấy máy in nào"])
                    self.combo_discovered_printers.set("Không tìm thấy máy in nào")
                    
            self.after(0, on_done)
            
        threading.Thread(target=run_scan, daemon=True).start()

    def start_printer_install(self):
        """Khởi chạy luồng cài đặt máy in."""
        ip = self.entry_printer_ip.get().strip()
        printer_name = self.entry_printer_name.get().strip()
        driver_mode = self.var_driver_mode.get()
        
        if not ip:
            messagebox.showerror("Lỗi dữ liệu", "Vui lòng nhập địa chỉ IP của máy in mạng!")
            return
        if not printer_name:
            messagebox.showerror("Lỗi dữ liệu", "Vui lòng đặt tên hiển thị cho máy in!")
            return
            
        try:
            ipaddress.IPv4Address(ip)
        except Exception:
            messagebox.showerror("Lỗi dữ liệu", "Địa chỉ IP máy in nhập vào không đúng định dạng IPv4!")
            return
            
        driver_model = None
        inf_path = None
        
        if driver_mode == "manual":
            inf_path = getattr(self, "selected_inf_path", None)
            driver_model = self.combo_inf_models.get()
            if not inf_path or not os.path.exists(inf_path):
                messagebox.showerror("Lỗi Driver", "Vui lòng chọn file driver .inf hợp lệ!")
                return
            if not driver_model or driver_model.startswith("("):
                messagebox.showerror("Lỗi Driver", "Vui lòng chọn Model máy in từ danh sách Driver!")
                return

        self.btn_install_printer.configure(state="disabled", text="Đang cài đặt máy in...")
        self.progress_printer.set(0.1)
        self.txt_printer_log.configure(state="normal")
        self.txt_printer_log.delete("1.0", tk.END)
        self.txt_printer_log.configure(state="disabled")
        
        self.log_printer("🏁 BẮT ĐẦU QUÁ TRÌNH CÀI ĐẶT MÁY IN MẠNG\n")
        self.log_printer("========================================\n")
        
        def run_install():
            self.after(0, lambda: self.progress_printer.set(0.3))
            
            success, msg = PrinterManager.install_printer(
                ip=ip,
                printer_name=printer_name,
                driver_mode=driver_mode,
                driver_model=driver_model,
                inf_path=inf_path,
                log_callback=self.log_printer
            )
            
            def on_done():
                self.btn_install_printer.configure(state="normal", text="📥 KHỞI CHẠY CÀI ĐẶT MÁY IN")
                if success:
                    self.progress_printer.set(1.0)
                    messagebox.showinfo("Thành công", msg, parent=self)
                else:
                    self.progress_printer.set(0)
                    messagebox.showerror("Thất bại", msg, parent=self)
                    
            self.after(0, on_done)
            
        threading.Thread(target=run_install, daemon=True).start()
