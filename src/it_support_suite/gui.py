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
from . import __version__


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
        self.grid_rowconfigure(2, minsize=36)  # Footer
        self.grid_columnconfigure(0, weight=1)
        
        self.build_banner()
        self.build_tabs()
        self.build_footer()
        
        # Đọc thông tin mạng mặc định khi khởi động ứng dụng
        self.refresh_network_info()


    def build_footer(self):
        """Render a modern professional status bar with product credits & system status."""
        footer = customtkinter.CTkFrame(
            self,
            height=36,
            corner_radius=0,
            fg_color=("#e2e8f0", "#080d1a"),
            border_width=1,
            border_color=("#cbd5e1", "#1e293b"),
        )
        footer.grid(row=2, column=0, sticky="ew")
        footer.grid_propagate(False)

        # Config 3 cột bằng nhau: Trai (Info/Version) - Giua (Author Pill) - Phai (Status)
        footer.grid_columnconfigure(0, weight=1)
        footer.grid_columnconfigure(1, weight=1)
        footer.grid_columnconfigure(2, weight=1)

        # --- Góc trái: Tên ứng dụng + Badge Version ---
        left_frame = customtkinter.CTkFrame(footer, fg_color="transparent")
        left_frame.grid(row=0, column=0, sticky="w", padx=15, pady=4)

        customtkinter.CTkLabel(
            left_frame,
            text="🛠️ IT Support Suite",
            font=customtkinter.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color=("#475569", "#94a3b8"),
        ).pack(side="left")

        version_badge = customtkinter.CTkFrame(
            left_frame,
            corner_radius=6,
            fg_color=("#dbeafe", "#1e293b"),
            border_width=1,
            border_color=("#bfdbfe", "#3b82f6"),
        )
        version_badge.pack(side="left", padx=8)

        customtkinter.CTkLabel(
            version_badge,
            text=f"v{__version__}",
            font=customtkinter.CTkFont(family="Segoe UI", size=10, weight="bold"),
            text_color=("#1d4ed8", "#38bdf8"),
        ).pack(padx=6, pady=1)

        # --- Góc giữa: Designed & Developed by Royal (Thẻ Pill cách điệu) ---
        center_pill = customtkinter.CTkFrame(
            footer,
            corner_radius=12,
            fg_color=("#f1f5f9", "#0f172a"),
            border_width=1,
            border_color=("#cbd5e1", "#1e293b"),
        )
        center_pill.grid(row=0, column=1, pady=4)

        center_content = customtkinter.CTkFrame(center_pill, fg_color="transparent")
        center_content.pack(padx=12, pady=2)

        customtkinter.CTkLabel(
            center_content,
            text="✨ Designed & Developed by ",
            font=customtkinter.CTkFont(family="Segoe UI", size=11),
            text_color=("#64748b", "#94a3b8"),
        ).pack(side="left")

        customtkinter.CTkLabel(
            center_content,
            text="Royal",
            font=customtkinter.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color=("#2563eb", "#38bdf8"),
        ).pack(side="left")

        # --- Góc phải: Trạng thái hệ thống ---
        right_frame = customtkinter.CTkFrame(footer, fg_color="transparent")
        right_frame.grid(row=0, column=2, sticky="e", padx=15, pady=4)

        customtkinter.CTkLabel(
            right_frame,
            text="🟢 Hệ thống sẵn sàng",
            font=customtkinter.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color=("#16a34a", "#4ade80"),
        ).pack(side="right")

    def build_banner(self):
        banner_frame = customtkinter.CTkFrame(
            self, corner_radius=0, height=64,
            fg_color=("#ffffff", "#0f172a"),
            border_width=1,
            border_color=("#e2e8f0", "#1e293b")
        )
        banner_frame.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        banner_frame.grid_columnconfigure(0, weight=1)
        
        # Tiêu đề ứng dụng & Subtitle bên trái
        title_box = customtkinter.CTkFrame(banner_frame, fg_color="transparent")
        title_box.pack(side="left", padx=20, pady=10)

        badge_icon = customtkinter.CTkFrame(
            title_box, corner_radius=10,
            fg_color=("#dbeafe", "#1e293b"),
            border_width=1, border_color=("#93c5fd", "#3b82f6"),
            width=42, height=42
        )
        badge_icon.pack(side="left", padx=(0, 12))
        badge_icon.pack_propagate(False)
        
        customtkinter.CTkLabel(
            badge_icon, text="🛠", font=customtkinter.CTkFont(size=20)
        ).pack(expand=True)

        titles_subframe = customtkinter.CTkFrame(title_box, fg_color="transparent")
        titles_subframe.pack(side="left")

        title_label = customtkinter.CTkLabel(
            titles_subframe, 
            text="IT SUPPORT TOOL SUITE", 
            font=customtkinter.CTkFont(family="Segoe UI", size=18, weight="bold"),
            text_color=("#0f172a", "#f8fafc")
        )
        title_label.pack(anchor="w")

        subtitle_label = customtkinter.CTkLabel(
            titles_subframe,
            text="Trợ thủ kỹ thuật viên - Tối ưu công việc IT Helpdesk",
            font=customtkinter.CTkFont(family="Segoe UI", size=11),
            text_color=("#64748b", "#94a3b8")
        )
        subtitle_label.pack(anchor="w")
        
        # Trình chọn giao diện (Theme Switcher)
        theme_box = customtkinter.CTkFrame(banner_frame, fg_color="transparent")
        theme_box.pack(side="right", padx=20, pady=12)

        theme_label = customtkinter.CTkLabel(
            theme_box, text="Giao diện:",
            font=customtkinter.CTkFont(family="Segoe UI", size=12, weight="bold"),
            text_color=("#475569", "#cbd5e1")
        )
        theme_label.pack(side="left", padx=(0, 8), pady=2)

        theme_menu = customtkinter.CTkOptionMenu(
            theme_box,
            values=["Tối (Dark)", "Sáng (Light)"],
            command=self.toggle_theme,
            width=125,
            height=32,
            corner_radius=8,
            button_color="#2563eb",
            button_hover_color="#1d4ed8"
        )
        theme_menu.pack(side="left")
        theme_menu.set("Tối (Dark)")

    def build_tabs(self):
        self.tabview = customtkinter.CTkTabview(
            self,
            corner_radius=14,
            border_width=1,
            border_color=("#cbd5e1", "#1e293b"),
            fg_color=("#f8fafc", "#0b101d"),
            text_color=("#0f172a", "#f8fafc"),
            segmented_button_selected_color="#2563eb",
            segmented_button_selected_hover_color="#1d4ed8",
            segmented_button_unselected_color=("#cbd5e1", "#1e293b"),
            segmented_button_unselected_hover_color=("#94a3b8", "#334155")
        )
        self.tabview.grid(row=1, column=0, sticky="nsew", padx=15, pady=10)
        
        # Tạo các tab với biểu tượng sạch (Loại bỏ U+FE0F variation selector gây lỗi ô vuông trên Windows)
        self.tab_backup = self.tabview.add("💾 Sao Lưu & Khôi Phục")
        self.tab_ip_scanner = self.tabview.add("🌐 Tra Cứu & Quản Lý IP")
        self.tab_printer = self.tabview.add("🖨 Máy In Mạng")
        self.tab_software = self.tabview.add("📦 Cài Phần Mềm")
        self.tab_uninstaller = self.tabview.add("🗑 Gỡ Cài Đặt")

        # Định cấu hình font chữ và text_color chuẩn độ tương phản cao cho thanh Tab
        if hasattr(self.tabview, "_segmented_button"):
            self.tabview._segmented_button.configure(
                font=customtkinter.CTkFont(family="Segoe UI", size=12, weight="bold"),
                text_color=("#0f172a", "#f8fafc")
            )

        self.build_backup_tab_ui()
        self.build_ip_scanner_tab_ui()
        self.build_printer_tab_ui()
        self.build_software_tab_ui()
        self.build_uninstaller_tab_ui()
        
        # Áp dụng Custom Style cho bảng Treeview ngay sau khi vẽ UI
        self.apply_treeview_styles(dark_mode=True)

    def apply_treeview_styles(self, dark_mode=True):
        """Định cấu hình Style hiện đại cho Treeview để đồng nhất với theme Dark/Light."""
        style = ttk.Style()
        style.theme_use("clam")
        
        bg_color = "#0f172a" if dark_mode else "#ffffff"
        fg_color = "#f8fafc" if dark_mode else "#0f172a"
        head_bg = "#1e293b" if dark_mode else "#e2e8f0"
        head_fg = "#f8fafc" if dark_mode else "#0f172a"
        select_bg = "#2563eb" if dark_mode else "#3b82f6"
        select_fg = "#ffffff"
        
        style.configure("Treeview",
                        background=bg_color,
                        foreground=fg_color,
                        rowheight=32,
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
            self.tree.tag_configure("online", foreground="#4ade80", background="#142918")
            self.tree.tag_configure("offline", foreground="#9ca3af", background="#182030")
        else:
            self.tree.tag_configure("online", foreground="#16a34a", background="#e8f5e9")
            self.tree.tag_configure("offline", foreground="#6b7280", background="#f1f5f9")

    def toggle_theme(self, choice):
        """Thay đổi chế độ giao diện Dark/Light của ứng dụng."""
        if choice == "Tối (Dark)":
            customtkinter.set_appearance_mode("dark")
            self.apply_treeview_styles(dark_mode=True)
        else:
            customtkinter.set_appearance_mode("light")
            self.apply_treeview_styles(dark_mode=False)
