# -*- coding: utf-8 -*-
"""Installed application browser and uninstaller tab."""
import os
import queue
import threading
import threading
import tkinter as tk
from tkinter import messagebox, ttk
import customtkinter
from .uninstaller_manager import UninstallerManager

class UninstallerTabMixin:
    def build_uninstaller_tab_ui(self):
        tab = self.tab_uninstaller
        tab.grid_columnconfigure(0, weight=1); tab.grid_rowconfigure(2, weight=1)
        
        head = customtkinter.CTkFrame(
            tab, corner_radius=12, fg_color=("#ffffff", "#0f172a"),
            border_width=1, border_color=("#e2e8f0", "#1e293b")
        )
        head.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))
        
        customtkinter.CTkLabel(
            head, text="🗑️ QUẢN LÝ & GỠ CÀI ĐẶT PHẦN MỀM",
            font=customtkinter.CTkFont(family="Segoe UI", size=15, weight="bold"),
            text_color=("#0f172a", "#f8fafc")
        ).pack(anchor="w", padx=18, pady=(12, 2))
        
        customtkinter.CTkLabel(
            head, text="Xem danh sách phần mềm hệ thống, khởi chạy trình gỡ cài đặt chính thức và kiểm tra tàn dư Registry/File.",
            font=customtkinter.CTkFont(family="Segoe UI", size=11),
            text_color=("#64748b", "#94a3b8")
        ).pack(anchor="w", padx=18, pady=(0, 12))
        
        bar = customtkinter.CTkFrame(tab, fg_color="transparent")
        bar.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        bar.grid_columnconfigure(0, weight=1)
        
        self.uninstall_search = customtkinter.CTkEntry(
            bar, placeholder_text="🔍 Tìm theo tên, phiên bản hoặc nhà phát hành...",
            height=36, corner_radius=8,
            font=customtkinter.CTkFont(family="Segoe UI", size=12)
        )
        self.uninstall_search.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        self.uninstall_search.bind("<KeyRelease>", self.filter_uninstall_apps)
        
        self.btn_uninstall_refresh = customtkinter.CTkButton(
            bar, text="🔄 Làm mới", width=110, height=36, corner_radius=8,
            fg_color="#2563eb", hover_color="#1d4ed8",
            font=customtkinter.CTkFont(family="Segoe UI", size=12, weight="bold"),
            command=self.start_load_uninstall_apps
        )
        self.btn_uninstall_refresh.grid(row=0, column=1, padx=4)
        
        self.btn_uninstall_run = customtkinter.CTkButton(
            bar, text="🗑️ Gỡ cài đặt", width=125, height=36, corner_radius=8,
            fg_color="#dc2626", hover_color="#b91c1c",
            font=customtkinter.CTkFont(family="Segoe UI", size=12, weight="bold"),
            command=self.uninstall_selected_app
        )
        self.btn_uninstall_run.grid(row=0, column=2, padx=(4, 0))
        
        body = customtkinter.CTkFrame(tab, fg_color="transparent")
        body.grid(row=2, column=0, sticky="nsew", padx=10, pady=(5, 10))
        body.grid_columnconfigure(0, weight=3)
        body.grid_columnconfigure(1, weight=2)
        body.grid_rowconfigure(0, weight=1)
        
        listing = customtkinter.CTkFrame(
            body, corner_radius=12,
            fg_color=("#ffffff", "#0f172a"),
            border_width=1, border_color=("#e2e8f0", "#1e293b")
        )
        listing.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        listing.grid_columnconfigure(0, weight=1)
        listing.grid_rowconfigure(0, weight=1)
        
        self.uninstall_tree = ttk.Treeview(listing, columns=("name", "version", "publisher", "scope"), show="headings", selectmode="browse")
        for key, title, width in (("name", "Tên ứng dụng", 230), ("version", "Phiên bản", 90), ("publisher", "Nhà phát hành", 150), ("scope", "Phạm vi", 110)):
            self.uninstall_tree.heading(key, text=title)
            self.uninstall_tree.column(key, width=width, minwidth=70)
        
        scroll = ttk.Scrollbar(listing, orient="vertical", command=self.uninstall_tree.yview)
        self.uninstall_tree.configure(yscrollcommand=scroll.set)
        self.uninstall_tree.grid(row=0, column=0, sticky="nsew", padx=(8, 0), pady=8)
        scroll.grid(row=0, column=1, sticky="ns", padx=(0, 8), pady=8)
        
        self.uninstall_tree.bind("<<TreeviewSelect>>", self.show_uninstall_details)
        self.uninstall_tree.bind("<Double-1>", lambda _e: self.uninstall_selected_app())
        
        panel = customtkinter.CTkFrame(
            body, corner_radius=12,
            fg_color=("#ffffff", "#0f172a"),
            border_width=1, border_color=("#e2e8f0", "#1e293b")
        )
        panel.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        panel.grid_columnconfigure(0, weight=1)
        panel.grid_rowconfigure(2, weight=1)
        
        self.uninstall_count = customtkinter.CTkLabel(
            panel, text="Đang tải...",
            font=customtkinter.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color=("#0f172a", "#f8fafc")
        )
        self.uninstall_count.grid(row=0, column=0, sticky="w", padx=15, pady=(12, 6))
        
        self.uninstall_details = customtkinter.CTkLabel(
            panel, text="Chọn một ứng dụng để xem thông tin chi tiết.",
            anchor="nw", justify="left", wraplength=310,
            font=customtkinter.CTkFont(family="Segoe UI", size=11),
            text_color=("#64748b", "#94a3b8")
        )
        self.uninstall_details.grid(row=1, column=0, sticky="ew", padx=15, pady=5)
        
        self.uninstall_leftovers = customtkinter.CTkTextbox(
            panel, fg_color="#090d16", text_color="#38bdf8",
            font=customtkinter.CTkFont(family="Consolas", size=11)
        )
        self.uninstall_leftovers.grid(row=2, column=0, sticky="nsew", padx=15, pady=10)
        self._set_leftover_text("Kết quả quét tàn dư sẽ hiển thị tại đây.")
        
        actions = customtkinter.CTkFrame(panel, fg_color="transparent")
        actions.grid(row=3, column=0, sticky="ew", padx=10, pady=(0, 12))
        
        customtkinter.CTkButton(
            actions, text="📁 Mở thư mục", height=34, corner_radius=8,
            fg_color=("#475569", "#334155"), hover_color=("#334155", "#475569"),
            font=customtkinter.CTkFont(family="Segoe UI", size=11, weight="bold"),
            command=self.open_uninstall_location
        ).pack(side="left", fill="x", expand=True, padx=5)
        
        customtkinter.CTkButton(
            actions, text="🧹 Quét tàn dư", height=34, corner_radius=8,
            fg_color="#f59e0b", hover_color="#d97706",
            font=customtkinter.CTkFont(family="Segoe UI", size=11, weight="bold"),
            command=self.scan_uninstall_leftovers
        ).pack(side="left", fill="x", expand=True, padx=5)
        
        self.uninstall_apps, self.uninstall_visible = [], {}
        self.after(150, self.start_load_uninstall_apps)

    def _set_leftover_text(self, text):
        self.uninstall_leftovers.configure(state="normal"); self.uninstall_leftovers.delete("1.0", tk.END); self.uninstall_leftovers.insert("1.0", text); self.uninstall_leftovers.configure(state="disabled")
    def start_load_uninstall_apps(self):
        """Load Registry data without calling Tkinter from a worker thread."""
        self.btn_uninstall_refresh.configure(state="disabled")
        self.uninstall_count.configure(text="Đang đọc danh sách ứng dụng...")
        result_queue = queue.Queue(maxsize=1)
        self._uninstall_load_queue = result_queue

        def worker():
            try:
                result_queue.put((True, UninstallerManager.list_installed()))
            except Exception as exc:
                result_queue.put((False, str(exc)))

        threading.Thread(target=worker, daemon=True).start()
        self.after(50, lambda: self._poll_uninstall_apps(result_queue))

    def _poll_uninstall_apps(self, result_queue):
        if result_queue is not getattr(self, "_uninstall_load_queue", None):
            return
        try:
            success, result = result_queue.get_nowait()
        except queue.Empty:
            self.after(50, lambda: self._poll_uninstall_apps(result_queue))
            return

        self.btn_uninstall_refresh.configure(state="normal")
        if success:
            self._finish_load_uninstall_apps(result)
        else:
            self.uninstall_count.configure(text="Không thể đọc danh sách ứng dụng")
            messagebox.showerror("Lỗi đọc ứng dụng", result)

    def _finish_load_uninstall_apps(self, apps):
        self.uninstall_apps = apps; self.btn_uninstall_refresh.configure(state="normal"); self.filter_uninstall_apps()
    def filter_uninstall_apps(self, _event=None):
        query = self.uninstall_search.get().strip().casefold(); self.uninstall_tree.delete(*self.uninstall_tree.get_children()); self.uninstall_visible = {}
        self.uninstall_details.configure(text="Chọn một ứng dụng để xem thông tin.")
        self._set_leftover_text("Chọn ứng dụng rồi bấm “Quét tàn dư”.")
        matches = [a for a in self.uninstall_apps if not query or query in " ".join((a["name"], a["version"], a["publisher"])).casefold()]
        for i, app in enumerate(matches):
            iid = f"app-{i}"; self.uninstall_tree.insert("", "end", iid=iid, values=(app["name"], app["version"], app["publisher"], app["scope"])); self.uninstall_visible[iid] = app
        self.uninstall_count.configure(text=f"{len(matches)} ứng dụng" + (f" / tổng {len(self.uninstall_apps)}" if query else ""))
    def _selected_uninstall_app(self):
        selected = self.uninstall_tree.selection(); return self.uninstall_visible.get(selected[0]) if selected else None
    def show_uninstall_details(self, _event=None):
        app = self._selected_uninstall_app()
        if not app: return
        date = app["date"]; date = f"{date[6:8]}/{date[4:6]}/{date[:4]}" if len(date) == 8 and date.isdigit() else date
        self.uninstall_details.configure(text=f"{app['name']}\n\nPhiên bản: {app['version'] or 'Không rõ'}\nNhà phát hành: {app['publisher'] or 'Không rõ'}\nNgày cài: {date or 'Không rõ'}\nPhạm vi: {app['scope']}\nThư mục: {app['location'] or 'Không khai báo'}")
        self._set_leftover_text(f"Chưa quét tàn dư cho: {app['name']}\n\nBấm “Quét tàn dư” để kiểm tra.")
    def uninstall_selected_app(self):
        app = self._selected_uninstall_app()
        if not app: messagebox.showwarning("Chưa chọn", "Vui lòng chọn một ứng dụng cần gỡ."); return
        if not messagebox.askyesno("Xác nhận gỡ cài đặt", f"Bạn có chắc muốn gỡ “{app['name']}”?\n\nSau khi trình gỡ kết thúc, ứng dụng sẽ tự quét file tàn dư, AppData và cache liên quan."): return
        self.btn_uninstall_run.configure(state="disabled", text="Đang gỡ...")
        self._set_leftover_text(f"Đang chờ gỡ {app['name']} hoàn tất...")
        threading.Thread(target=self._uninstall_wait_and_scan, args=(app,), daemon=True).start()

    def _uninstall_wait_and_scan(self, app):
        try:
            UninstallerManager.uninstall_and_wait(app)
            items = UninstallerManager.find_leftovers(app)
            self.after(0, lambda: self._finish_uninstall_scan(app, items))
        except Exception as exc:
            self.after(0, lambda e=str(exc): messagebox.showerror("Không thể gỡ cài đặt", e))
            self.after(0, self._reset_uninstall_button)

    def _reset_uninstall_button(self):
        self.btn_uninstall_run.configure(state="normal", text="Gỡ cài đặt")

    def _finish_uninstall_scan(self, app, items):
        self._reset_uninstall_button()
        self.start_load_uninstall_apps()
        if not items:
            self._set_leftover_text(f"Kết quả cho: {app['name']}\n\nKhông tìm thấy file tàn dư.")
            messagebox.showinfo("Đã gỡ sạch", f"Đã gỡ {app['name']}. Không tìm thấy file tàn dư, AppData hoặc cache liên quan.")
            return
        self._show_leftover_dialog(app, items)

    def _show_leftover_dialog(self, app, items):
        dialog = customtkinter.CTkToplevel(self)
        dialog.title(f"Tàn dư của {app['name']}"); dialog.geometry("780x460"); dialog.minsize(650, 380)
        dialog.transient(self); dialog.grab_set(); dialog.grid_columnconfigure(0, weight=1); dialog.grid_rowconfigure(1, weight=1)
        customtkinter.CTkLabel(dialog, text=f"TÌM THẤY {len(items)} MỤC TÀN DƯ", font=customtkinter.CTkFont(size=16, weight="bold"), text_color="#f59e0b").grid(row=0, column=0, sticky="w", padx=18, pady=(18, 4))
        customtkinter.CTkLabel(dialog, text="Các mục đã được chọn sẵn. Giữ Ctrl để chọn/bỏ chọn nhiều mục trước khi xóa.", text_color=("#64748b", "#94a3b8")).grid(row=0, column=0, sticky="sw", padx=18, pady=(0, 18))
        frame = customtkinter.CTkFrame(dialog); frame.grid(row=1, column=0, sticky="nsew", padx=18, pady=5); frame.grid_columnconfigure(0, weight=1); frame.grid_rowconfigure(0, weight=1)
        listbox = tk.Listbox(frame, selectmode=tk.EXTENDED, bg="#0b1020", fg="#e5e7eb", selectbackground="#2563eb", borderwidth=0, font=("Consolas", 10))
        scroll = ttk.Scrollbar(frame, orient="vertical", command=listbox.yview); listbox.configure(yscrollcommand=scroll.set)
        listbox.grid(row=0, column=0, sticky="nsew", padx=(8, 0), pady=8); scroll.grid(row=0, column=1, sticky="ns", padx=(0, 8), pady=8)
        for item in items: listbox.insert(tk.END, f"[{item['kind']}] {item['path']}")
        listbox.selection_set(0, tk.END)
        buttons = customtkinter.CTkFrame(dialog, fg_color="transparent"); buttons.grid(row=2, column=0, sticky="ew", padx=13, pady=(8, 18))
        customtkinter.CTkButton(buttons, text="Bỏ qua", fg_color="#64748b", command=dialog.destroy).pack(side="right", padx=5)
        customtkinter.CTkButton(buttons, text="Xóa mục đã chọn", fg_color="#dc2626", hover_color="#b91c1c", command=lambda: self._delete_selected_leftovers(dialog, listbox, app, items)).pack(side="right", padx=5)
        self._set_leftover_text(f"Kết quả cho: {app['name']}\n\n" + "\n".join(f"[{x['kind']}] {x['path']}" for x in items))

    def _delete_selected_leftovers(self, dialog, listbox, app, items):
        indexes = list(listbox.curselection())
        if not indexes: messagebox.showwarning("Chưa chọn", "Hãy chọn ít nhất một mục cần xóa.", parent=dialog); return
        selected = [items[i] for i in indexes]
        if not messagebox.askyesno("Xác nhận xóa", f"Xóa vĩnh viễn {len(selected)} mục tàn dư của {app['name']}?", parent=dialog): return
        deleted, failed = UninstallerManager.delete_leftovers(selected)
        dialog.destroy()
        if failed:
            detail = "\n".join(f"• {item['path']}: {error}" for item, error in failed[:8])
            messagebox.showwarning("Xóa chưa hoàn tất", f"Đã xóa {len(deleted)}/{len(selected)} mục.\n\n{detail}")
        else: messagebox.showinfo("Đã dọn dẹp", f"Đã xóa {len(deleted)} mục tàn dư của {app['name']}.")
        remaining = UninstallerManager.find_leftovers(app)
        self._set_leftover_text(f"Kết quả kiểm tra lại cho: {app['name']}\n\n" + ("\n".join(f"[{x['kind']}] {x['path']}" for x in remaining) if remaining else "Không còn tàn dư được phát hiện."))
    def open_uninstall_location(self):
        app = self._selected_uninstall_app()
        if not app or not app["location"] or not os.path.isdir(app["location"]): messagebox.showwarning("Không tìm thấy", "Ứng dụng không khai báo thư mục cài đặt."); return
        os.startfile(app["location"])
    def scan_uninstall_leftovers(self):
        app = self._selected_uninstall_app()
        if not app: messagebox.showwarning("Chưa chọn", "Vui lòng chọn một ứng dụng."); return
        items = UninstallerManager.find_leftovers(app)
        result = "\n".join(f"[{item['kind']}] {item['path']}" for item in items) if items else "Không tìm thấy tàn dư theo các vị trí an toàn đã kiểm tra."
        self._set_leftover_text(f"Kết quả cho: {app['name']}\n\n{result}")
