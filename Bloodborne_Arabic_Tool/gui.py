# -*- coding: utf-8 -*-
"""
واجهة المستخدم الرسومية (GUI) لأداة تعريب Bloodborne PC Native
"""
import os
import sys
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path

# ضبط مسار الاستيراد
CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

from engine.patcher import BloodbornePatcher


class BloodborneArabicApp:
    def __init__(self, root):
        self.root = root
        self.root.title("مُعرّب بلودبورن للكمبيوتر | Bloodborne PC Native - التعريب المصري")
        self.root.geometry("780x680")
        self.root.minsize(720, 620)
        self.root.configure(bg="#121318")

        # الألوان والثيم القوطي للعبة
        self.colors = {
            "bg": "#121318",
            "card_bg": "#1B1D24",
            "card_border": "#2C2E3B",
            "text": "#E8E8ED",
            "subtext": "#9699A6",
            "gold": "#C9A050",
            "crimson": "#8E1F1F",
            "crimson_hover": "#A82424",
            "crimson_active": "#731818",
            "success": "#2E7D32",
            "error": "#C62828",
            "btn_sec": "#272A35",
            "btn_sec_hover": "#343847",
            "log_bg": "#0D0E12",
        }

        self.patcher = BloodbornePatcher()
        self.mode_var = tk.StringVar(value="egyptian")
        self.path_var = tk.StringVar()

        self._setup_styles()
        self._build_ui()
        self._init_data()

    def _setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        # Radio button style
        style.configure("Dark.TRadiobutton",
                        background=self.colors["card_bg"],
                        foreground=self.colors["text"],
                        font=("Segoe UI", 10, "bold"),
                        focuscolor=self.colors["gold"])
        style.map("Dark.TRadiobutton",
                  background=[("active", self.colors["card_bg"])],
                  foreground=[("active", self.colors["gold"])])

    def _build_ui(self):
        # 1. Header Frame
        header_frame = tk.Frame(self.root, bg="#181A22", pady=15, padx=20, highlightthickness=1, highlightbackground=self.colors["card_border"])
        header_frame.pack(fill="x", padx=15, pady=(15, 10))

        title_lbl = tk.Label(header_frame, text="⚔️ مُعرّب Bloodborne PC Native (النسخة المصرية) 🩸",
                             font=("Segoe UI", 16, "bold"), fg=self.colors["gold"], bg="#181A22")
        title_lbl.pack(anchor="center")

        subtitle_lbl = tk.Label(header_frame, text="أداة التثبيت التلقائي للتعريب الكامل مع دعم اللهجة العامية المصرية الأصلية للبورت الرسمي",
                                font=("Segoe UI", 9), fg=self.colors["subtext"], bg="#181A22")
        subtitle_lbl.pack(anchor="center", pady=(4, 0))

        # 2. Main Container
        main_container = tk.Frame(self.root, bg=self.colors["bg"])
        main_container.pack(fill="both", expand=True, padx=15, pady=5)

        # 2.1 Game Path Selection Card
        path_card = tk.LabelFrame(main_container, text=" 📂 تحديد مسار اللعبة ",
                                  font=("Segoe UI", 10, "bold"), fg=self.colors["gold"],
                                  bg=self.colors["card_bg"], bd=1, relief="solid")
        path_card.pack(fill="x", pady=6, padx=5, ipady=5)

        path_inner = tk.Frame(path_card, bg=self.colors["card_bg"])
        path_inner.pack(fill="x", padx=12, pady=8)

        self.path_entry = tk.Entry(path_inner, textvariable=self.path_var, font=("Segoe UI", 10),
                                   bg="#0F1015", fg="#FFFFFF", insertbackground="#FFFFFF",
                                   bd=1, relief="solid", highlightthickness=1, highlightbackground=self.colors["card_border"])
        self.path_entry.pack(side="left", fill="x", expand=True, padx=(0, 8), ipady=4)
        self.path_entry.bind("<KeyRelease>", self._on_path_changed)

        browse_btn = tk.Button(path_inner, text="استعراض... (Browse)", font=("Segoe UI", 9, "bold"),
                               bg=self.colors["btn_sec"], fg=self.colors["text"],
                               activebackground=self.colors["btn_sec_hover"], activeforeground="#FFFFFF",
                               bd=0, padx=14, pady=5, cursor="hand2", command=self._browse_path)
        browse_btn.pack(side="right")

        self.path_status_lbl = tk.Label(path_card, text="", font=("Segoe UI", 9),
                                        bg=self.colors["card_bg"], fg=self.colors["subtext"])
        self.path_status_lbl.pack(anchor="w", padx=12, pady=(0, 4))

        # 2.2 Status & Dialect Selection
        options_row = tk.Frame(main_container, bg=self.colors["bg"])
        options_row.pack(fill="x", pady=6, padx=5)

        # Dialect Choice Card
        dialect_card = tk.LabelFrame(options_row, text=" 🗣️ خيارات اللهجة والتعريب ",
                                     font=("Segoe UI", 10, "bold"), fg=self.colors["gold"],
                                     bg=self.colors["card_bg"], bd=1, relief="solid")
        dialect_card.pack(side="left", fill="both", expand=True, padx=(0, 6), ipady=4)

        rb_egyptian = ttk.Radiobutton(dialect_card, text="🇪🇬 تعريب بالمصري (العامية المصرية)",
                                      variable=self.mode_var, value="egyptian",
                                      style="Dark.TRadiobutton")
        rb_egyptian.pack(anchor="w", padx=14, pady=4)

        egyptian_desc = tk.Label(dialect_card, text="شاشات الموت والانتصار والقوائم الرئيسية باللهجة المصرية (متّ خلاص، دبحت الفريسة يا وحش)",
                                 font=("Segoe UI", 8), fg=self.colors["subtext"], bg=self.colors["card_bg"])
        egyptian_desc.pack(anchor="w", padx=32, pady=(0, 4))

        rb_standard = ttk.Radiobutton(dialect_card, text="📜 تعريب فصحى كامل (رسمي)",
                                      variable=self.mode_var, value="standard",
                                      style="Dark.TRadiobutton")
        rb_standard.pack(anchor="w", padx=14, pady=4)

        # Status Badge Card
        status_card = tk.LabelFrame(options_row, text=" 📊 حالة التثبيت الحالية ",
                                    font=("Segoe UI", 10, "bold"), fg=self.colors["gold"],
                                    bg=self.colors["card_bg"], bd=1, relief="solid")
        status_card.pack(side="right", fill="both", expand=True, padx=(6, 0), ipady=4)

        self.status_game_lbl = tk.Label(status_card, text="اللعبة: جاري الفحص...",
                                        font=("Segoe UI", 9, "bold"), fg=self.colors["text"], bg=self.colors["card_bg"])
        self.status_game_lbl.pack(anchor="w", padx=14, pady=(6, 2))

        self.status_arabic_lbl = tk.Label(status_card, text="التعريب: جاري الفحص...",
                                          font=("Segoe UI", 9), fg=self.colors["subtext"], bg=self.colors["card_bg"])
        self.status_arabic_lbl.pack(anchor="w", padx=14, pady=2)

        # 2.3 Action Buttons
        btn_bar = tk.Frame(main_container, bg=self.colors["bg"])
        btn_bar.pack(fill="x", pady=10, padx=5)

        self.install_btn = tk.Button(btn_bar, text="🩸 تثبيت التعريب الآن",
                                     font=("Segoe UI", 11, "bold"),
                                     bg=self.colors["crimson"], fg="#FFFFFF",
                                     activebackground=self.colors["crimson_hover"], activeforeground="#FFFFFF",
                                     bd=0, padx=20, pady=9, cursor="hand2", command=self._on_install_click)
        self.install_btn.pack(side="left", fill="x", expand=True, padx=(0, 5))

        self.uninstall_btn = tk.Button(btn_bar, text="🔄 استرجاع النسخة الإنجليزية",
                                       font=("Segoe UI", 10),
                                       bg=self.colors["btn_sec"], fg=self.colors["text"],
                                       activebackground=self.colors["btn_sec_hover"], activeforeground="#FFFFFF",
                                       bd=0, padx=15, pady=9, cursor="hand2", command=self._on_uninstall_click)
        self.uninstall_btn.pack(side="left", fill="x", expand=True, padx=5)

        self.launch_btn = tk.Button(btn_bar, text="⚔️ تشغيل اللعبة",
                                    font=("Segoe UI", 11, "bold"),
                                    bg="#1D4E24", fg="#FFFFFF",
                                    activebackground="#26632E", activeforeground="#FFFFFF",
                                    bd=0, padx=20, pady=9, cursor="hand2", command=self._on_launch_click)
        self.launch_btn.pack(side="right", fill="x", expand=True, padx=(5, 0))

        # 2.4 Progress & Live Log
        log_card = tk.LabelFrame(main_container, text=" 📝 سجل العمليات والخطوات ",
                                 font=("Segoe UI", 9, "bold"), fg=self.colors["gold"],
                                 bg=self.colors["card_bg"], bd=1, relief="solid")
        log_card.pack(fill="both", expand=True, pady=(5, 0), padx=5)

        self.log_text = tk.Text(log_card, bg=self.colors["log_bg"], fg="#D2D4DC",
                                font=("Consolas", 9), bd=0, padx=10, pady=8, state="disabled")
        scrollbar = tk.Scrollbar(log_card, command=self.log_text.yview, bg="#1A1C22")
        self.log_text.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.log_text.pack(side="left", fill="both", expand=True)

        # 3. Footer
        footer_lbl = tk.Label(self.root, text="ملحوظة: تأكد من ضبط لغة اللعبة داخل الإعدادات على English لكي تظهر النصوص العربية بشكل صحيح",
                              font=("Segoe UI", 8), fg="#7A7C88", bg=self.colors["bg"])
        footer_lbl.pack(side="bottom", pady=8)

    def _init_data(self):
        detected = self.patcher.auto_detect()
        if detected:
            self.path_var.set(detected)
            self._log(f"تم اكتشاف مسار اللعبة تلقائياً: {detected}")
        else:
            self._log("يرجى اختيار مجلد لعبة Bloodborne PC...")
        self._refresh_status()

    def _on_path_changed(self, event=None):
        path = self.path_var.get().strip()
        if path:
            self.patcher.set_game_path(path)
        self._refresh_status()

    def _browse_path(self):
        folder = filedialog.askdirectory(title="اختر مجلد لعبة Bloodborne PC Native")
        if folder:
            self.path_var.set(folder)
            self.patcher.set_game_path(folder)
            self._refresh_status()

    def _refresh_status(self):
        status = self.patcher.get_status()
        if status["game_found"]:
            self.path_status_lbl.config(text="✓ تم التحقق: مجلد اللعبة و Bloodborne.exe متوفران بنجاح", fg="#4CAF50")
            self.status_game_lbl.config(text="اللعبة: جاهزة ✓", fg="#4CAF50")
            self.launch_btn.config(state="normal")
            self.install_btn.config(state="normal")
        else:
            self.path_status_lbl.config(text="✗ لم يتم العثور على Bloodborne.exe في هذا المجلد", fg="#EF5350")
            self.status_game_lbl.config(text="اللعبة: غير موجودة ✗", fg="#EF5350")
            self.launch_btn.config(state="disabled")
            self.install_btn.config(state="disabled")

        if status["installed"]:
            mode_text = "بالمصري 🇪🇬" if status["mode"] == "egyptian" else "فصحى 📜"
            self.status_arabic_lbl.config(text=f"التعريب: مثبت ({mode_text}) ✓", fg="#4CAF50")
            self.uninstall_btn.config(state="normal")
        else:
            self.status_arabic_lbl.config(text="التعريب: غير مثبت ✗", fg=self.colors["subtext"])
            self.uninstall_btn.config(state="disabled")

    def _log(self, text):
        self.log_text.config(state="normal")
        self.log_text.insert("end", f"{text}\n")
        self.log_text.see("end")
        self.log_text.config(state="disabled")

    def _on_install_click(self):
        mode = self.mode_var.get()
        mode_label = "بالمصري (اللهجة العامية المصرية)" if mode == "egyptian" else "فصحى كاملة"
        
        self.install_btn.config(state="disabled")
        self.uninstall_btn.config(state="disabled")
        self.launch_btn.config(state="disabled")
        
        self._log(f"\n==========================================")
        self._log(f"بدء تثبيت التعريب: {mode_label}...")

        def run_thread():
            try:
                self.patcher.install(mode=mode, log_callback=self._log)
                self.root.after(0, lambda: messagebox.showinfo("نجاح التثبيت", f"تم تثبيت تعريب Bloodborne {mode_label} بنجاح!\nيمكنك تشغيل اللعبة الآن والتمتع بالتجربة."))
            except Exception as e:
                self._log(f"خطأ أثناء التثبيت: {e}")
                self.root.after(0, lambda: messagebox.showerror("خطأ", f"حدث خطأ أثناء تثبيت التعريب:\n{e}"))
            finally:
                self.root.after(0, self._refresh_status)

        threading.Thread(target=run_thread, daemon=True).start()

    def _on_uninstall_click(self):
        if not messagebox.askyesno("تأكيد الاسترجاع", "هل أنت متأكد من رغبتك في حذف التعريب والعودة للنسخة الإنجليزية الأصلية؟"):
            return

        self.install_btn.config(state="disabled")
        self.uninstall_btn.config(state="disabled")

        self._log(f"\n==========================================")
        self._log("بدء استرجاع النسخة الأصلية...")

        def run_thread():
            try:
                self.patcher.uninstall(log_callback=self._log)
                self.root.after(0, lambda: messagebox.showinfo("نجاح الاسترجاع", "تم استرجاع النسخة الإنجليزية الأصلية بنجاح."))
            except Exception as e:
                self._log(f"خطأ أثناء الاسترجاع: {e}")
                self.root.after(0, lambda: messagebox.showerror("خطأ", f"حدث خطأ أثناء الاسترجاع:\n{e}"))
            finally:
                self.root.after(0, self._refresh_status)

        threading.Thread(target=run_thread, daemon=True).start()

    def _on_launch_click(self):
        try:
            exe_path = self.patcher.launch_game()
            self._log(f"تم تشغيل اللعبة بنجاح: {exe_path}")
        except Exception as e:
            messagebox.showerror("خطأ في التشغيل", f"فشل تشغيل اللعبة:\n{e}")


def launch_gui():
    root = tk.Tk()
    app = BloodborneArabicApp(root)
    root.mainloop()

if __name__ == "__main__":
    launch_gui()
