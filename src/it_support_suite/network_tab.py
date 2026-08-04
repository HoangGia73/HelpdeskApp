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

from .network_scanner import NetworkScanner


class NetworkTabMixin:
    def build_ip_scanner_tab_ui(self):
        # Lưới Tab 2
        self.tab_ip_scanner.grid_columnconfigure(0, weight=4) # Khung cấu hình (Trái)
        self.tab_ip_scanner.grid_columnconfigure(1, weight=6) # Khung kết quả (Phải)
        self.tab_ip_scanner.grid_rowconfigure(0, weight=1)
        
        # --- CỘT TRÁI: CẤU HÌNH & THÔNG TIN MẠNG ---
        left_frame = customtkinter.CTkFrame(self.tab_ip_scanner)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(10, 5), pady=10)
        
        # Khung thông tin IP hiện tại của máy tính
        info_group = customtkinter.CTkFrame(left_frame)
        info_group.pack(fill="x", padx=15, pady=15)
        
        lbl_info_title = customtkinter.CTkLabel(
            info_group, 
            text="🖥️ THÔNG TIN MẠNG MÁY TÍNH", 
            font=customtkinter.CTkFont(size=14, weight="bold")
        )
        lbl_info_title.pack(anchor="w", padx=15, pady=(10, 10))
        
        # Hiển thị IP, Subnet Mask, Gateway hiện tại
        self.lbl_adapter = customtkinter.CTkLabel(info_group, text="Card mạng: Đang đọc...", anchor="w")
        self.lbl_adapter.pack(fill="x", padx=20, pady=2)

        self.lbl_local_ip = customtkinter.CTkLabel(info_group, text="IPv4 Address: Đang đọc...", anchor="w")
        self.lbl_local_ip.pack(fill="x", padx=20, pady=2)
        
        self.lbl_subnet = customtkinter.CTkLabel(info_group, text="Subnet Mask: Đang đọc...", anchor="w")
        self.lbl_subnet.pack(fill="x", padx=20, pady=2)
        
        self.lbl_gateway = customtkinter.CTkLabel(info_group, text="Default Gateway: Đang đọc...", anchor="w")
        self.lbl_gateway.pack(fill="x", padx=20, pady=2)
        
        btn_refresh = customtkinter.CTkButton(
            info_group, 
            text="🔄 Làm mới thông tin mạng", 
            height=25, 
            command=self.refresh_network_info
        )
        btn_refresh.pack(padx=20, pady=(10, 5), fill="x")

        self.btn_config_ip = customtkinter.CTkButton(
            info_group, 
            text="⚙️ Cấu hình IP mạng", 
            height=25, 
            fg_color="#3a3a3a",
            hover_color="#4a4a4a",
            command=self.open_ip_config_dialog
        )
        self.btn_config_ip.pack(padx=20, pady=(5, 15), fill="x")

        # Khung cấu hình Quét Mạng LAN
        scan_group = customtkinter.CTkFrame(left_frame)
        scan_group.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        lbl_scan_title = customtkinter.CTkLabel(
            scan_group, 
            text="📡 QUÉT MẠNG NỘI BỘ (LAN SCANNER)", 
            font=customtkinter.CTkFont(size=14, weight="bold")
        )
        lbl_scan_title.pack(anchor="w", padx=15, pady=(10, 10))
        
        # Nhập dải IP
        lbl_start_ip = customtkinter.CTkLabel(scan_group, text="IP Bắt đầu (Start IP):", anchor="w")
        lbl_start_ip.pack(fill="x", padx=20, pady=(5, 1))
        self.entry_start_ip = customtkinter.CTkEntry(scan_group, placeholder_text="192.168.1.1")
        self.entry_start_ip.pack(fill="x", padx=20, pady=(0, 5))
        
        lbl_end_ip = customtkinter.CTkLabel(scan_group, text="IP Kết thúc (End IP):", anchor="w")
        lbl_end_ip.pack(fill="x", padx=20, pady=(5, 1))
        self.entry_end_ip = customtkinter.CTkEntry(scan_group, placeholder_text="192.168.1.254")
        self.entry_end_ip.pack(fill="x", padx=20, pady=(0, 10))
        
        # Thanh tiến trình quét
        self.progress_scan = customtkinter.CTkProgressBar(scan_group, progress_color="#3b82f6")
        self.progress_scan.pack(fill="x", padx=20, pady=8)
        self.progress_scan.set(0)
        
        # Các nút quét và xuất CSV
        self.btn_scan = customtkinter.CTkButton(
            scan_group, 
            text="🔍 Bắt đầu quét mạng", 
            fg_color="#3b82f6", 
            hover_color="#2563eb",
            font=customtkinter.CTkFont(weight="bold"),
            command=self.start_network_scan
        )
        self.btn_scan.pack(fill="x", padx=20, pady=8)
        
        self.btn_export = customtkinter.CTkButton(
            scan_group, 
            text="📥 Xuất Báo cáo CSV/Excel", 
            fg_color="#10b981", 
            hover_color="#059669",
            font=customtkinter.CTkFont(weight="bold"),
            command=self.export_scan_results
        )
        self.btn_export.pack(fill="x", padx=20, pady=(0, 15))

        # --- CỘT PHẢI: BẢNG KẾT QUẢ THIẾT BỊ QUÉT ĐƯỢC ---
        right_frame = customtkinter.CTkFrame(self.tab_ip_scanner)
        right_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 10), pady=10)
        
        lbl_table_title = customtkinter.CTkLabel(
            right_frame, 
            text="📋 DANH SÁCH THIẾT BỊ HOẠT ĐỘNG TRONG MẠNG", 
            font=customtkinter.CTkFont(size=14, weight="bold")
        )
        lbl_table_title.pack(anchor="w", padx=15, pady=(10, 5))
        
        # Thiết kế bảng Treeview lồng vào customtkinter
        table_container = tk.Frame(right_frame, bg="#2a2d2e")
        table_container.pack(fill="both", expand=True, padx=15, pady=10)
        
        columns = ("ip", "mac", "status", "hostname")
        self.tree = ttk.Treeview(table_container, columns=columns, show="headings", selectmode="browse")
        
        self.tree.heading("ip", text="Địa chỉ IP")
        self.tree.heading("mac", text="Địa chỉ MAC")
        self.tree.heading("status", text="Trạng thái")
        self.tree.heading("hostname", text="Tên thiết bị (Hostname)")
        
        self.tree.column("ip", width=120, anchor="center")
        self.tree.column("mac", width=140, anchor="center")
        self.tree.column("status", width=90, anchor="center")
        self.tree.column("hostname", width=180, anchor="w")
        
        scrollbar = ttk.Scrollbar(table_container, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def refresh_network_info(self):
        """Cập nhật giao diện thông tin card mạng hiện tại của máy tính."""
        self.lbl_adapter.configure(text="Card mạng: Đang lấy dữ liệu...")
        self.lbl_local_ip.configure(text="IPv4 Address: Đang lấy dữ liệu...")
        self.lbl_subnet.configure(text="Subnet Mask: Đang lấy dữ liệu...")
        self.lbl_gateway.configure(text="Default Gateway: Đang lấy dữ liệu...")
        
        def run_refresh():
            ip, subnet, gateway, adapter = NetworkScanner.get_local_network_info()
            
            self.current_ip = ip
            self.current_subnet = subnet
            self.current_gateway = gateway
            self.current_adapter = adapter
            
            def update_ui():
                if ip:
                    self.lbl_adapter.configure(text=f"Card mạng: {adapter or 'Không rõ'}")
                    self.lbl_local_ip.configure(text=f"IPv4 Address: {ip}")
                    self.lbl_subnet.configure(text=f"Subnet Mask: {subnet}")
                    self.lbl_gateway.configure(text=f"Default Gateway: {gateway}")
                    
                    try:
                        interface = ipaddress.IPv4Interface(f"{ip}/{subnet}")
                        network = interface.network
                        hosts = list(network.hosts())
                        if hosts:
                            start_ip = str(hosts[0])
                            end_ip = str(hosts[-1])
                        else:
                            parts = ip.split('.')
                            start_ip = f"{parts[0]}.{parts[1]}.{parts[2]}.1"
                            end_ip = f"{parts[0]}.{parts[1]}.{parts[2]}.254"
                    except Exception:
                        parts = ip.split('.')
                        start_ip = f"{parts[0]}.{parts[1]}.{parts[2]}.1"
                        end_ip = f"{parts[0]}.{parts[1]}.{parts[2]}.254"
                        
                    self.entry_start_ip.delete(0, tk.END)
                    self.entry_start_ip.insert(0, start_ip)
                    self.entry_end_ip.delete(0, tk.END)
                    self.entry_end_ip.insert(0, end_ip)
                else:
                    self.lbl_adapter.configure(text="Card mạng: Không xác định")
                    self.lbl_local_ip.configure(text="IPv4 Address: Không xác định (Offline)")
                    self.lbl_subnet.configure(text="Subnet Mask: Không xác định")
                    self.lbl_gateway.configure(text="Default Gateway: Không xác định")
                    
                    self.entry_start_ip.delete(0, tk.END)
                    self.entry_start_ip.insert(0, "192.168.1.1")
                    self.entry_end_ip.delete(0, tk.END)
                    self.entry_end_ip.insert(0, "192.168.1.254")
                    
            self.after(0, update_ui)
            
        threading.Thread(target=run_refresh, daemon=True).start()

    def start_network_scan(self):
        """Kích hoạt tác vụ quét mạng đa luồng tránh treo GUI."""
        if self.scan_running:
            messagebox.showwarning("Cảnh báo", "Tiến trình quét mạng LAN đang được thực hiện!")
            return
            
        start_ip = self.entry_start_ip.get().strip()
        end_ip = self.entry_end_ip.get().strip()
        
        try:
            start_addr = ipaddress.IPv4Address(start_ip)
            end_addr = ipaddress.IPv4Address(end_ip)
        except ValueError:
            messagebox.showerror("Địa chỉ IP không hợp lệ", "Vui lòng nhập đúng định dạng IPv4 (ví dụ: 192.168.1.1)!")
            return

        if end_addr < start_addr:
            messagebox.showerror("Dải IP không hợp lệ", "IP kết thúc phải lớn hơn hoặc bằng IP bắt đầu!")
            return

        address_count = int(end_addr) - int(start_addr) + 1
        if address_count > 4096:
            messagebox.showerror("Dải IP quá lớn", "Mỗi lần chỉ quét tối đa 4096 địa chỉ IP.")
            return
            
        self.scan_running = True
        self.btn_scan.configure(state="disabled")
        self.btn_export.configure(state="disabled")
        self.progress_scan.set(0)
        
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        threading.Thread(
            target=self.run_network_scan, 
            args=(start_ip, end_ip), 
            daemon=True
        ).start()

    def run_network_scan(self, start_ip_str, end_ip_str):
        """Logic quét mạng chính (chạy ngầm)."""
        try:
            start_addr = ipaddress.IPv4Address(start_ip_str)
            end_addr = ipaddress.IPv4Address(end_ip_str)
            
            ips_to_scan = []
            curr = start_addr
            while curr <= end_addr:
                ips_to_scan.append(str(curr))
                curr += 1
                
            total_ips = len(ips_to_scan)
            if total_ips == 0:
                self.after(0, lambda: messagebox.showwarning("Dải IP rỗng", "Không có IP nào trong dải đã nhập!"))
                return
                
            scanned_count = 0
            
            def update_progress():
                nonlocal scanned_count
                scanned_count += 1
                self.after(0, lambda: self.progress_scan.set(scanned_count / total_ips))

            with ThreadPoolExecutor(max_workers=min(64, max(1, total_ips))) as executor:
                # Gửi công việc quét IP song song (ping, mac, hostname)
                future_to_ip = {executor.submit(NetworkScanner.scan_single_ip, ip): ip for ip in ips_to_scan}
                
                for future in concurrent.futures.as_completed(future_to_ip):
                    try:
                        result = future.result()
                    except Exception:
                        result = {
                            "ip": future_to_ip[future],
                            "mac": "N/A",
                            "status": "Offline",
                            "hostname": "N/A"
                        }
                    
                    ip = result["ip"]
                    mac = result["mac"]
                    status = result["status"]
                    hostname = result["hostname"]
                    tag = status.lower()
                    
                    self.after(0, lambda i=ip, m=mac, s=status, h=hostname, t=tag: self.tree.insert(
                        "", tk.END, values=(i, m, s, h), tags=(t,)
                    ))
                    
                    update_progress()
            
            # Sắp xếp lại bảng theo dải IP sau khi quét xong
            self.after(0, self.sort_treeview_by_ip)
            
        except Exception as e:
            self.after(0, lambda error=str(e): messagebox.showerror("Lỗi Quét Mạng", f"Lỗi xảy ra: {error}"))
        finally:
            self.scan_running = False
            self.after(0, lambda: self.btn_scan.configure(state="normal"))
            self.after(0, lambda: self.btn_export.configure(state="normal"))
            self.after(0, lambda: self.progress_scan.set(1.0))

    def sort_treeview_by_ip(self):
        """Sắp xếp các hàng dữ liệu của Treeview theo đúng thứ tự tăng dần của IP."""
        items = [(self.tree.set(k, "ip"), k) for k in self.tree.get_children("")]
        
        def ip_key(item_tuple):
            try:
                return ipaddress.IPv4Address(item_tuple[0])
            except ValueError:
                return ipaddress.IPv4Address("255.255.255.255")
                
        items.sort(key=ip_key)
        
        for index, (_, k) in enumerate(items):
            self.tree.move(k, "", index)

    def export_scan_results(self):
        """Xuất danh sách thiết bị quét được ra file CSV mã hóa UTF-8-BOM."""
        items = []
        for item in self.tree.get_children():
            items.append(self.tree.item(item, "values"))
            
        if not items:
            messagebox.showwarning("Cảnh báo", "Không có dữ liệu thiết bị nào trong bảng để xuất báo cáo!")
            return
            
        file_path = filedialog.asksaveasfilename(
            parent=self,
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")],
            title="Chọn thư mục để xuất báo cáo CSV"
        )
        if not file_path:
            return
            
        try:
            with open(file_path, mode='w', newline='', encoding='utf-8-sig') as r:
                writer = csv.writer(r)
                writer.writerow(["Địa chỉ IP", "Địa chỉ MAC", "Trạng thái", "Tên thiết bị (Hostname)"])
                writer.writerows(items)
                
            messagebox.showinfo(
                "Xuất dữ liệu thành công", 
                f"Báo cáo thiết bị đã được xuất thành công ra file:\n{file_path}"
            )
        except Exception as e:
            messagebox.showerror("Lỗi xuất file", f"Không thể lưu file báo cáo. Chi tiết lỗi: {str(e)}")

    def open_ip_config_dialog(self):
        """Mở cửa sổ cấu hình IP mạng."""
        curr_ip = getattr(self, "current_ip", "") or ""
        curr_subnet = getattr(self, "current_subnet", "") or ""
        curr_gateway = getattr(self, "current_gateway", "") or ""
        curr_adapter = getattr(self, "current_adapter", "") or "Ethernet"

        dialog = customtkinter.CTkToplevel(self)
        dialog.title("Cấu hình IP Mạng")
        dialog.geometry("460x420")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()

        # Tiêu đề
        lbl_title = customtkinter.CTkLabel(
            dialog,
            text="⚙️ THIẾT LẬP IP MÁY TÍNH CỤC BỘ",
            font=customtkinter.CTkFont(size=15, weight="bold")
        )
        lbl_title.pack(pady=(15, 10))

        # Khung chứa Form
        form_frame = customtkinter.CTkFrame(dialog)
        form_frame.pack(fill="both", expand=True, padx=20, pady=5)

        # Hàng 1: Tên Card Mạng (Dùng CTkComboBox hỗ trợ cả chọn từ danh sách và tự gõ)
        lbl_adapter = customtkinter.CTkLabel(form_frame, text="Tên Card mạng:", anchor="w", width=120)
        lbl_adapter.grid(row=0, column=0, padx=15, pady=8, sticky="w")
        
        all_adapters = NetworkScanner.get_all_adapters()
        combo_adapter = customtkinter.CTkComboBox(form_frame, values=all_adapters, width=240)
        combo_adapter.grid(row=0, column=1, padx=15, pady=8)
        
        if curr_adapter and curr_adapter in all_adapters:
            combo_adapter.set(curr_adapter)
        elif all_adapters:
            combo_adapter.set(all_adapters[0])

        # Hàng 2: Chế độ (DHCP / Static)
        lbl_mode = customtkinter.CTkLabel(form_frame, text="Chế độ:", anchor="w", width=120)
        lbl_mode.grid(row=1, column=0, padx=15, pady=8, sticky="w")
        
        def on_mode_change(choice):
            if choice == "Tự động (DHCP)":
                entry_ip.configure(state="disabled")
                entry_subnet.configure(state="disabled")
                entry_gateway.configure(state="disabled")
                entry_dns.configure(state="disabled")
            else:
                entry_ip.configure(state="normal")
                entry_subnet.configure(state="normal")
                entry_gateway.configure(state="normal")
                entry_dns.configure(state="normal")

        combo_mode = customtkinter.CTkOptionMenu(
            form_frame,
            values=["Tự động (DHCP)", "IP Tĩnh (Static IP)"],
            width=240,
            command=on_mode_change
        )
        combo_mode.grid(row=1, column=1, padx=15, pady=8)
        combo_mode.set("Tự động (DHCP)")

        # Hàng 3: Địa chỉ IP
        lbl_ip = customtkinter.CTkLabel(form_frame, text="Địa chỉ IP:", anchor="w", width=120)
        lbl_ip.grid(row=2, column=0, padx=15, pady=8, sticky="w")
        entry_ip = customtkinter.CTkEntry(form_frame, width=240)
        entry_ip.grid(row=2, column=1, padx=15, pady=8)
        entry_ip.insert(0, curr_ip or "192.168.1.50")

        # Hàng 4: Subnet Mask
        lbl_subnet = customtkinter.CTkLabel(form_frame, text="Subnet Mask:", anchor="w", width=120)
        lbl_subnet.grid(row=3, column=0, padx=15, pady=8, sticky="w")
        entry_subnet = customtkinter.CTkEntry(form_frame, width=240)
        entry_subnet.grid(row=3, column=1, padx=15, pady=8)
        entry_subnet.insert(0, curr_subnet or "255.255.255.0")

        # Hàng 5: Default Gateway
        lbl_gateway = customtkinter.CTkLabel(form_frame, text="Default Gateway:", anchor="w", width=120)
        lbl_gateway.grid(row=4, column=0, padx=15, pady=8, sticky="w")
        entry_gateway = customtkinter.CTkEntry(form_frame, width=240)
        entry_gateway.grid(row=4, column=1, padx=15, pady=8)
        entry_gateway.insert(0, curr_gateway or "192.168.1.1")

        # Hàng 6: DNS Server (Google DNS làm mặc định)
        lbl_dns = customtkinter.CTkLabel(form_frame, text="DNS Server:", anchor="w", width=120)
        lbl_dns.grid(row=5, column=0, padx=15, pady=8, sticky="w")
        entry_dns = customtkinter.CTkEntry(form_frame, width=240)
        entry_dns.grid(row=5, column=1, padx=15, pady=8)
        entry_dns.insert(0, "8.8.8.8")

        # Thiết lập trạng thái ban đầu của các ô nhập
        on_mode_change("Tự động (DHCP)")

        # Khung nút bấm điều hướng
        btn_frame = customtkinter.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=15)

        def apply_changes():
            mode = combo_mode.get()
            adapter = combo_adapter.get().strip()
            
            if not adapter:
                messagebox.showerror("Lỗi nhập liệu", "Tên card mạng không được để trống!", parent=dialog)
                return
                
            if mode == "IP Tĩnh (Static IP)":
                ip = entry_ip.get().strip()
                subnet = entry_subnet.get().strip()
                gateway = entry_gateway.get().strip()
                dns = entry_dns.get().strip()
                
                try:
                    ipaddress.IPv4Address(ip)
                    ipaddress.IPv4Address(subnet)
                    ipaddress.IPv4Address(gateway)
                    if dns:
                        ipaddress.IPv4Address(dns)
                except Exception:
                    messagebox.showerror("Lỗi cấu hình", "Vui lòng nhập đúng định dạng địa chỉ IPv4!", parent=dialog)
                    return
            else:
                ip, subnet, gateway, dns = None, None, None, None

            btn_apply.configure(state="disabled", text="Đang cấu hình...")
            btn_cancel.configure(state="disabled")

            def run_conrig():
                try:
                    if mode == "IP Tĩnh (Static IP)":
                        success, msg = NetworkScanner.set_static_ip(adapter, ip, subnet, gateway, dns)
                    else:
                        success, msg = NetworkScanner.set_dhcp(adapter)
                except Exception as e:
                    success, msg = False, str(e)

                def on_done():
                    if success:
                        messagebox.showinfo("Thành công", msg, parent=self)
                        dialog.destroy()
                        self.refresh_network_info()
                    else:
                        messagebox.showerror("Thất bại", msg, parent=dialog)
                        btn_apply.configure(state="normal", text="Áp dụng")
                        btn_cancel.configure(state="normal")

                self.after(0, on_done)

            threading.Thread(target=run_conrig, daemon=True).start()

        # Nút áp dụng
        btn_apply = customtkinter.CTkButton(
            btn_frame, 
            text="Áp dụng", 
            width=150, 
            command=apply_changes
        )
        btn_apply.pack(side="right", padx=10)

        # Nút hủy
        btn_cancel = customtkinter.CTkButton(
            btn_frame, 
            text="Hủy bỏ", 
            width=150, 
            fg_color="#3a3a3a", 
            hover_color="#4a4a4a",
            command=dialog.destroy
        )
        btn_cancel.pack(side="left", padx=10)
