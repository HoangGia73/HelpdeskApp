# -*- coding: utf-8 -*-
"""Software installation tab for provisioning a new Windows computer."""

import threading
import tkinter as tk
from tkinter import messagebox
import customtkinter

from .software_manager import SoftwareManager


class SoftwareTabMixin:
    def build_software_tab_ui(self):
        self.tab_software.grid_columnconfigure(0, weight=1)
        self.tab_software.grid_rowconfigure(1, weight=1)
        self.tab_software.grid_rowconfigure(1, weight=1)
        header = customtkinter.CTkFrame(
            self.tab_software, corner_radius=12, fg_color=("#ffffff", "#0f172a"),
            border_width=1, border_color=("#e2e8f0", "#1e293b")
        )
        header.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))
        customtkinter.CTkLabel(
            header, text="📦 CÀI ĐẶT PHẦN MỀM TỰ ĐỘNG",
            font=customtkinter.CTkFont(family="Segoe UI", size=15, weight="bold"),
            text_color=("#0f172a", "#f8fafc")
        ).pack(anchor="w", padx=18, pady=(12, 2))
        customtkinter.CTkLabel(
            header, text="Chọn phần mềm cần thiết cho máy tính. Quản lý và tải tự động qua Windows Package Manager (winget).",
            font=customtkinter.CTkFont(family="Segoe UI", size=11),
            text_color=("#64748b", "#94a3b8")
        ).pack(anchor="w", padx=18, pady=(0, 12))

        content = customtkinter.CTkFrame(self.tab_software, fg_color="transparent")
        content.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        content.grid_columnconfigure(0, weight=3)
        content.grid_columnconfigure(1, weight=2)
        content.grid_rowconfigure(0, weight=1)
        listing = customtkinter.CTkScrollableFrame(
            content, label_text="📋 Danh sách phần mềm sẵn có", corner_radius=12,
            fg_color=("#ffffff", "#0f172a"),
            border_width=1, border_color=("#e2e8f0", "#1e293b")
        )
        listing.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        listing.grid_columnconfigure(0, weight=1)
        self.software_rows = {}
        for index, package in enumerate(SoftwareManager.PACKAGES):
            card = customtkinter.CTkFrame(
                listing, corner_radius=10,
                fg_color=("#f8fafc", "#1e293b"),
                border_width=1, border_color=("#e2e8f0", "#334155")
            )
            card.grid(row=index, column=0, sticky="ew", padx=5, pady=4)
            card.grid_columnconfigure(1, weight=1)
            checkbox = customtkinter.CTkCheckBox(
                card, text=package["name"], font=customtkinter.CTkFont(family="Segoe UI", size=12, weight="bold")
            )
            checkbox.grid(row=0, column=0, rowspan=2, sticky="w", padx=12, pady=10)
            customtkinter.CTkLabel(
                card, text=package["description"], anchor="w",
                font=customtkinter.CTkFont(family="Segoe UI", size=11),
                text_color=("#64748b", "#94a3b8")
            ).grid(row=0, column=1, sticky="sw", padx=8, pady=(7, 0))
            customtkinter.CTkLabel(
                card, text=package["id"], anchor="w",
                font=customtkinter.CTkFont(family="Consolas", size=10),
                text_color=("#94a3b8", "#64748b")
            ).grid(row=1, column=1, sticky="nw", padx=8, pady=(0, 7))
            status = customtkinter.CTkLabel(
                card, text="Chưa kiểm tra", width=110,
                font=customtkinter.CTkFont(family="Segoe UI", size=11, weight="bold"),
                text_color="#f59e0b"
            )
            status.grid(row=0, column=2, rowspan=2, sticky="e", padx=12)
            self.software_rows[package["id"]] = {"package": package, "checkbox": checkbox, "status": status}

        panel = customtkinter.CTkFrame(
            content, corner_radius=12,
            fg_color=("#ffffff", "#0f172a"),
            border_width=1, border_color=("#e2e8f0", "#1e293b")
        )
        panel.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        panel.grid_columnconfigure(0, weight=1)
        panel.grid_rowconfigure(4, weight=1)
        customtkinter.CTkLabel(
            panel, text="⚡ THAO TÁC & TIẾN TRÌNH",
            font=customtkinter.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color=("#0f172a", "#f8fafc")
        ).grid(row=0, column=0, sticky="w", padx=15, pady=(12, 8))

        choose = customtkinter.CTkFrame(panel, fg_color="transparent")
        choose.grid(row=1, column=0, sticky="ew", padx=10)
        customtkinter.CTkButton(
            choose, text="✓ Chọn tất cả",
            font=customtkinter.CTkFont(family="Segoe UI", size=11, weight="bold"),
            height=32, corner_radius=8,
            fg_color=("#2563eb", "#2563eb"), hover_color="#1d4ed8",
            command=lambda: self.set_all_software_selected(True)
        ).pack(side="left", padx=5, fill="x", expand=True)
        customtkinter.CTkButton(
            choose, text="✗ Bỏ chọn",
            font=customtkinter.CTkFont(family="Segoe UI", size=11, weight="bold"),
            height=32, corner_radius=8,
            fg_color=("#64748b", "#475569"), hover_color="#334155",
            command=lambda: self.set_all_software_selected(False)
        ).pack(side="left", padx=5, fill="x", expand=True)
        self.btn_check_software = customtkinter.CTkButton(
            panel, text="🔍 Kiểm tra phần mềm đã cài", height=36, corner_radius=8,
            fg_color="#0284c7", hover_color="#0369a1",
            font=customtkinter.CTkFont(family="Segoe UI", size=11, weight="bold"),
            command=self.start_check_software
        )
        self.btn_check_software.grid(row=2, column=0, sticky="ew", padx=15, pady=(10, 5))
        self.btn_install_software = customtkinter.CTkButton(
            panel, text="🚀 Bắt đầu Cài phần mềm đã chọn", height=42, corner_radius=10,
            fg_color="#10b981", hover_color="#059669",
            font=customtkinter.CTkFont(family="Segoe UI", size=12, weight="bold"),
            command=self.start_install_software
        )
        self.btn_install_software.grid(row=3, column=0, sticky="ew", padx=15, pady=5)
        self.software_log = customtkinter.CTkTextbox(
            panel, fg_color="#090d16", text_color="#38bdf8",
            font=customtkinter.CTkFont(family="Consolas", size=11)
        )
        self.software_log.grid(row=4, column=0, sticky="nsew", padx=15, pady=(10, 15))
        self.software_log.configure(state="disabled")
        self.software_busy = False

    def software_log_message(self, message):
        def update():
            self.software_log.configure(state="normal")
            self.software_log.insert(tk.END, message + "\n")
            self.software_log.see(tk.END)
            self.software_log.configure(state="disabled")
        self.after(0, update)

    def set_all_software_selected(self, selected):
        for row in self.software_rows.values():
            row["checkbox"].select() if selected else row["checkbox"].deselect()

    def set_software_controls(self, enabled):
        state = "normal" if enabled else "disabled"
        self.btn_check_software.configure(state=state)
        self.btn_install_software.configure(state=state)

    def start_check_software(self):
        if self.software_busy:
            return
        self.software_busy = True
        self.set_software_controls(False)
        threading.Thread(target=self.run_check_software, daemon=True).start()

    def run_check_software(self):
        try:
            if not SoftwareManager.winget_available():
                raise RuntimeError("Kh\u00f4ng t\u00ecm th\u1ea5y winget. H\u00e3y c\u00e0i App Installer t\u1eeb Microsoft Store.")
            self.software_log_message("Dang kiem tra phan mem...")
            for package_id, row in self.software_rows.items():
                installed = SoftwareManager.is_installed(package_id)
                text, color = ("\u0110\u00e3 c\u00e0i", "#10b981") if installed else ("Ch\u01b0a c\u00e0i", "#f59e0b")
                self.after(0, lambda r=row, t=text, c=color: r["status"].configure(text=t, text_color=c))
            self.software_log_message("Kiem tra hoan tat.")
        except Exception as exc:
            self.software_log_message(f"LOI: {exc}")
            self.after(0, lambda e=str(exc): messagebox.showerror("L\u1ed7i winget", e))
        finally:
            self.software_busy = False
            self.after(0, lambda: self.set_software_controls(True))

    def start_install_software(self):
        selected = [row["package"] for row in self.software_rows.values() if row["checkbox"].get() == 1]
        if self.software_busy:
            return
        if not selected:
            messagebox.showwarning("Ch\u01b0a ch\u1ecdn", "Vui l\u00f2ng ch\u1ecdn \u00edt nh\u1ea5t m\u1ed9t ph\u1ea7n m\u1ec1m.")
            return
        self.software_busy = True
        self.set_software_controls(False)
        threading.Thread(target=self.run_install_software, args=(selected,), daemon=True).start()

    def run_install_software(self, selected):
        try:
            if not SoftwareManager.winget_available():
                raise RuntimeError("Kh\u00f4ng t\u00ecm th\u1ea5y winget. H\u00e3y c\u00e0i App Installer t\u1eeb Microsoft Store.")
            success = 0
            for index, package in enumerate(selected, 1):
                row, package_id = self.software_rows[package["id"]], package["id"]
                if SoftwareManager.is_installed(package_id):
                    self.software_log_message(f"[{index}/{len(selected)}] {package['name']}: da cai, bo qua.")
                    self.after(0, lambda r=row: r["status"].configure(text="\u0110\u00e3 c\u00e0i", text_color="#10b981"))
                    success += 1
                    continue
                self.software_log_message(f"[{index}/{len(selected)}] Dang cai {package['name']}...")
                self.after(0, lambda r=row: r["status"].configure(text="\u0110ang c\u00e0i...", text_color="#38bdf8"))
                code = SoftwareManager.install(package_id, lambda line, name=package["name"]: self.software_log_message(f"  {name}: {line}"))
                installed = code == 0 or SoftwareManager.is_installed(package_id)
                text, color = ("\u0110\u00e3 c\u00e0i", "#10b981") if installed else ("Th\u1ea5t b\u1ea1i", "#ef4444")
                success += int(installed)
                self.software_log_message(("OK: " if installed else "LOI: ") + package["name"])
                self.after(0, lambda r=row, t=text, c=color: r["status"].configure(text=t, text_color=c))
            self.after(0, lambda: messagebox.showinfo("Ho\u00e0n t\u1ea5t", r"Th\u00e0nh c\u00f4ng {success}/{len(selected)} ph\u1ea7n m\u1ec1m."))
        except Exception as exc:
            self.software_log_message(f"LOI: {exc}")
            self.after(0, lambda e=str(exc): messagebox.showerror("L\u1ed7i c\u00e0i \u0111\u1eb7t", e))
        finally:
            self.software_busy = False
            self.after(0, lambda: self.set_software_controls(True))
