# -*- coding: utf-8 -*-
"""Main application shell for IT Support Tool Suite."""
import tkinter as tk
from tkinter import ttk
import customtkinter
from .backup_tab import BackupTabMixin
from .network_tab import NetworkTabMixin
from .printer_tab import PrinterTabMixin
from .software_tab import SoftwareTabMixin
from .uninstaller_tab import UninstallerTabMixin


class ITSupportApp(BackupTabMixin, NetworkTabMixin, PrinterTabMixin,
                   SoftwareTabMixin, UninstallerTabMixin, customtkinter.CTk):
    def __init__(self):
        super().__init__()
        
        # Cài đặt kích thước và tiêu đề
        self.title("IT Support Tool Suite - Trợ Thủ Kỹ Thuật Viên")
        self.geometry("1100x800")
        self.minsize(980, 720)
        self.configure(fg_color=("#eef2f7", "#0b1120"))
        
        # Khởi tạo các trạng thái luồng chạy ngầm
        self.backup_running = False
        self.scan_running = False
        self.installed_drivers = []
        self.selected_drivers = []
        
        # Tạo lưới giao diện chính
        self.grid_rowconfigure(0, minsize=50) # Banner tiêu đề
        self.grid_rowconfigure(1, weight=1)    # Khung nội dung chính
        self.grid_columnconfigure(0, weight=1)
        
        self.build_banner()
        self.build_tabs()
        
        # Đọc thông tin mạng mặc định khi khởi động ứng dụng
        self.refresh_network_info()

    def build_banner(self):
        banner_frame = customtkinter.CTkFrame(
            self, corner_radius=0, height=64,
            fg_color=("#ffffff", "#111827"),
            border_width=0
        )
        banner_frame.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        
        # Tiêu đề ứng dụng
        title_label = customtkinter.CTkLabel(
            banner_frame, 
            text="🛠️ IT SUPPORT TOOL SUITE", 
            font=customtkinter.CTkFont(family="Segoe UI", size=22, weight="bold"),
            text_color=("#0f172a", "#f8fafc")
        )
        title_label.pack(side="left", padx=20, pady=10)
        
        # Trình chọn giao diện (Theme Switcher)
        theme_menu = customtkinter.CTkOptionMenu(
            banner_frame,
            values=["Tối (Dark)", "Sáng (Light)"],
            command=self.toggle_theme,
            width=130
        )
        theme_menu.pack(side="right", padx=20, pady=10)
        theme_menu.set("Tối (Dark)")
        
        theme_label = customtkinter.CTkLabel(banner_frame, text="Giao diện:", font=customtkinter.CTkFont(size=12))
        theme_label.pack(side="right", padx=5, pady=10)

    def build_tabs(self):
        self.tabview = customtkinter.CTkTabview(
            self,
            corner_radius=14,
            border_width=1,
            border_color=("#dbe3ef", "#253047"),
            fg_color=("#f8fafc", "#0f172a"),
            segmented_button_selected_color="#2563eb",
            segmented_button_selected_hover_color="#1d4ed8",
            segmented_button_unselected_color=("#e8eef7", "#1e293b"),
            segmented_button_unselected_hover_color=("#dbe7f7", "#334155")
        )
        self.tabview.grid(row=1, column=0, sticky="nsew", padx=15, pady=10)
        
        # Tạo 3 tab chạy song song
        self.tab_backup = self.tabview.add("SAO LƯU & KHÔI PHỤC")
        self.tab_ip_scanner = self.tabview.add("TRA CỨU & QUẢN LÝ IP/MAC")
        self.tab_printer = self.tabview.add("CÀI ĐẶT MÁY IN MẠNG")
        
        # Xây dựng chi tiết giao diện cho từng tab
        self.tab_software = self.tabview.add("C\u00c0I PH\u1ea6N M\u1ec0M")
        self.tab_uninstaller = self.tabview.add("G\u1ee0 C\u00c0I \u0110\u1eb6T")

        self.build_backup_tab_ui()
        self.build_ip_scanner_tab_ui()
        self.build_printer_tab_ui()
        self.build_software_tab_ui()
        self.build_uninstaller_tab_ui()
        
        # Áp dụng Custom Style cho bảng Treeview ngay sau khi vẽ UI
        self.apply_treeview_styles(dark_mode=True)

    def apply_treeview_styles(self, dark_mode=True):
        """Định cấu hình Style cho Treeview để đồng nhất với theme Dark/Light."""
        style = ttk.Style()
        style.theme_use("clam")
        
        bg_color = "#1e1e1e" if dark_mode else "#ffffff"
        fg_color = "#ffffff" if dark_mode else "#1e1e1e"
        head_bg = "#2d2d2d" if dark_mode else "#e0e0e0"
        head_fg = "#ffffff" if dark_mode else "#1e1e1e"
        select_bg = "#1f538d" if dark_mode else "#3b82f6"
        select_fg = "#ffffff"
        
        style.configure("Treeview",
                        background=bg_color,
                        foreground=fg_color,
                        rowheight=28,
                        fieldbackground=bg_color,
                        bordercolor=bg_color,
                        borderwidth=0)
                        
        style.map('Treeview', 
                  background=[('selected', select_bg)],
                  foreground=[('selected', select_fg)])
                  
        style.configure("Treeview.Heading",
                        background=head_bg,
                        foreground=head_fg,
                        font=("Segoe UI", 10, "bold"),
                        relief="flat")
                        
        style.map("Treeview.Heading",
                  background=[('active', select_bg)],
                  foreground=[('active', select_fg)])
                  
        if dark_mode:
            self.tree.tag_configure("online", foreground="#4ade80", background="#1a2e1a")
            self.tree.tag_configure("offline", foreground="#9ca3af")
        else:
            self.tree.tag_configure("online", foreground="#16a34a", background="#e8f5e9")
            self.tree.tag_configure("offline", foreground="#6b7280")

    def toggle_theme(self, choice):
        """Thay đổi chế độ giao diện Dark/Light của ứng dụng."""
        if choice == "Tối (Dark)":
            customtkinter.set_appearance_mode("dark")
            self.apply_treeview_styles(dark_mode=True)
        else:
            customtkinter.set_appearance_mode("light")
            self.apply_treeview_styles(dark_mode=False)
