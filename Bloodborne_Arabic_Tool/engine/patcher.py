# -*- coding: utf-8 -*-
"""
محرك تثبيت وإدارة تعريب Bloodborne PC Native
"""
import os
import sys
import json
import shutil
import zipfile
import subprocess
from pathlib import Path
from datetime import datetime

# إضافة مسار السكربتات الخاصة باللعبة للوصول لأدوات FromSoftware
CURRENT_DIR = Path(__file__).resolve().parent
TOOL_DIR = CURRENT_DIR.parent
ASSETS_DIR = TOOL_DIR / "assets"
BASE_PATCH_ZIP = ASSETS_DIR / "base_patch.zip"

from .egyptian_dict import get_shaped_overrides

def find_fromsoft_tools(game_dir):
    """البحث عن مكتبات fromsoft و menu_assets في اللعبة أو نسخها محلياً"""
    potential_paths = [
        game_dir / "bbport-windows" / "scripts",
        game_dir / "scripts",
        Path(r"E:\Bloodborne\bbport-windows\scripts"),
    ]
    for p in potential_paths:
        if p.is_dir() and (p / "fromsoft.py").is_file():
            if str(p) not in sys.path:
                sys.path.insert(0, str(p))
            return True
    return False


class BloodbornePatcher:
    def __init__(self, target_path=None):
        self.game_root = None
        self.bbport_dir = None
        self.game_dvdroot = None
        if target_path:
            self.set_game_path(target_path)
        else:
            self.auto_detect()

    def set_game_path(self, path_str):
        """التحقق من صحة مسار اللعبة وضبط المسارات الداخلية"""
        if not path_str:
            return False
        p = Path(path_str).resolve()
        
        # الاحتمال الأول: المستخدم اختار مجلد E:\Bloodborne الرئيسي
        if (p / "bbport-windows" / "Bloodborne.exe").is_file():
            self.game_root = p
            self.bbport_dir = p / "bbport-windows"
            self.game_dvdroot = p / "game" / "dvdroot_ps4"
            find_fromsoft_tools(self.game_root)
            return True
            
        # الاحتمال الثاني: المستخدم اختار مجلد bbport-windows مباشرة
        if (p / "Bloodborne.exe").is_file():
            self.bbport_dir = p
            self.game_root = p.parent
            self.game_dvdroot = p.parent / "game" / "dvdroot_ps4"
            find_fromsoft_tools(self.game_root)
            return True
            
        # الاحتمال الثالث: فحص وجود Bloodborne.exe في أي مجلد فرعي مباشر
        for sub in p.iterdir() if p.is_dir() else []:
            if sub.is_dir() and (sub / "Bloodborne.exe").is_file():
                self.game_root = p
                self.bbport_dir = sub
                self.game_dvdroot = p / "game" / "dvdroot_ps4"
                find_fromsoft_tools(self.game_root)
                return True
                
        return False

    def auto_detect(self):
        """محاولة اكتشاف مسار اللعبة تلقائياً على النظام"""
        candidates = [
            Path(r"E:\Bloodborne"),
            Path(r"D:\Bloodborne"),
            Path(r"C:\Bloodborne"),
            Path(r"E:\Games\Bloodborne"),
            Path(r"D:\Games\Bloodborne"),
            Path(r"C:\Games\Bloodborne"),
            Path.cwd(),
            Path.cwd().parent,
        ]
        for candidate in candidates:
            if self.set_game_path(candidate):
                return str(self.game_root or self.bbport_dir)
        return ""

    def get_status(self):
        """معرفة حالة اللعبة والتعريب الحالي"""
        if not self.bbport_dir or not (self.bbport_dir / "Bloodborne.exe").is_file():
            return {
                "game_found": False,
                "installed": False,
                "mode": "none",
                "message": "لم يتم العثور على ملفات اللعبة في المسار المحدد"
            }
            
        arabic_mod_dir = self.bbport_dir / "mods" / "Arabic"
        arabic_dvdroot = arabic_mod_dir / "dvdroot_ps4"
        
        # فحص ملفات التعريب
        font_file = arabic_dvdroot / "menu" / "engus" / "font.gfx"
        msg_file = arabic_dvdroot / "msg" / "engus" / "menu.msgbnd.dcx"
        
        if not (font_file.is_file() and msg_file.is_file()):
            return {
                "game_found": True,
                "installed": False,
                "mode": "none",
                "message": "اللعبة جاهزة ولكن التعريب غير مثبت"
            }
            
        # فحص mods.json
        mods_json_path = self.bbport_dir / "mods.json"
        is_active = True
        if mods_json_path.is_file():
            try:
                mods_cfg = json.loads(mods_json_path.read_text(encoding="utf-8"))
                if "Arabic" in mods_cfg.get("disabled", []):
                    is_active = False
            except Exception:
                pass
                
        marker_file = arabic_mod_dir / ".arabic_mode.json"
        mode = "standard"
        if marker_file.is_file():
            try:
                m_data = json.loads(marker_file.read_text(encoding="utf-8"))
                mode = m_data.get("mode", "standard")
            except Exception:
                pass
                
        return {
            "game_found": True,
            "installed": is_active,
            "mode": mode if is_active else "disabled",
            "message": f"التعريب مثبت ونشط ({'بالمصري' if mode == 'egyptian' else 'فصحى'})" if is_active else "التعريب معطّل في mods.json"
        }

    def install(self, mode="egyptian", log_callback=None):
        """
        تثبيت التعريب على اللعبة
        mode: 'egyptian' (مصري عامية) أو 'standard' (فصحى رسمية)
        """
        def log(msg):
            if log_callback:
                log_callback(msg)
            else:
                print(msg)

        if not self.bbport_dir:
            raise ValueError("مسار اللعبة غير محدد أو غير صالح")

        if not BASE_PATCH_ZIP.is_file():
            raise FileNotFoundError(f"ملف حزمة التعريب الأساسية غير موجود: {BASE_PATCH_ZIP}")

        log("1. جاري استخراج ملفات التعريب والخطوط العربية...")
        with zipfile.ZipFile(BASE_PATCH_ZIP, "r") as z:
            z.extractall(self.bbport_dir)

        arabic_mod_dir = self.bbport_dir / "mods" / "Arabic"
        arabic_dvdroot = arabic_mod_dir / "dvdroot_ps4"

        if not arabic_dvdroot.is_dir():
            raise RuntimeError("فشل فك ضغط مجلد dvdroot_ps4 الخاص بالتعريب")

        log("2. تم تثبيت الخطوط العربية وملفات الرسوميات (font.gfx و title.gfx)")

        if mode == "egyptian":
            log("3. جاري تطبيق صياغة اللهجة العامية المصرية والتشكيل (Reshaping & BiDi)...")
            find_fromsoft_tools(self.game_root)
            from fromsoft import Bnd4, dcx_decompress, dcx_compress
            from menu_assets import fmg_read, fmg_write

            menu_overrides, item_overrides = get_shaped_overrides(mode="egyptian")

            # تعديل اللغتين engus و enggb لضمان العمل تحت أي إعداد لغة باللعبة
            for lang in ["engus", "enggb"]:
                lang_msg_dir = arabic_dvdroot / "msg" / lang
                if not lang_msg_dir.is_dir():
                    continue

                # تعديل menu.msgbnd.dcx
                menu_path = lang_msg_dir / "menu.msgbnd.dcx"
                if menu_path.is_file():
                    log(f"   - تخصيص نصوص القوائم بالمصري ({lang})...")
                    raw_data = menu_path.read_bytes()
                    bnd = Bnd4(dcx_decompress(raw_data))

                    for (target_fid, target_mid), arabic_text in menu_overrides.items():
                        if target_fid in bnd.ids:
                            idx = bnd.ids.index(target_fid)
                            fmg = fmg_read(bnd.files[idx])
                            fmg[target_mid] = arabic_text.encode("utf-16-le")
                            bnd.files[idx] = fmg_write(fmg)

                    repacked = bnd.to_bytes()
                    compressed = dcx_compress(repacked, template=raw_data)
                    menu_path.write_bytes(compressed)

                # تعديل item.msgbnd.dcx
                item_path = lang_msg_dir / "item.msgbnd.dcx"
                if item_path.is_file():
                    log(f"   - تخصيص أسماء الأدوات والأسلحة بالمصري ({lang})...")
                    raw_data = item_path.read_bytes()
                    bnd = Bnd4(dcx_decompress(raw_data))

                    for (target_fid, target_mid), arabic_text in item_overrides.items():
                        if target_fid in bnd.ids:
                            idx = bnd.ids.index(target_fid)
                            fmg = fmg_read(bnd.files[idx])
                            fmg[target_mid] = arabic_text.encode("utf-16-le")
                            bnd.files[idx] = fmg_write(fmg)

                    repacked = bnd.to_bytes()
                    compressed = dcx_compress(repacked, template=raw_data)
                    item_path.write_bytes(compressed)

        log("4. جاري تسجيل المود في إعدادات اللعبة (mods.json)...")
        mods_json_path = self.bbport_dir / "mods.json"
        mods_data = {"order": ["Arabic"], "disabled": []}
        if mods_json_path.is_file():
            try:
                mods_data = json.loads(mods_json_path.read_text(encoding="utf-8"))
            except Exception:
                mods_data = {"order": ["Arabic"], "disabled": []}

        order = mods_data.get("order", [])
        if "Arabic" in order:
            order.remove("Arabic")
        order.insert(0, "Arabic")
        mods_data["order"] = order

        disabled = mods_data.get("disabled", [])
        if "Arabic" in disabled:
            disabled.remove("Arabic")
        mods_data["disabled"] = disabled

        mods_json_path.write_text(json.dumps(mods_data, indent=2, ensure_ascii=False), encoding="utf-8")

        # حفظ ملف حالة المود
        marker = arabic_mod_dir / ".arabic_mode.json"
        marker.write_text(json.dumps({
            "mode": mode,
            "installed_at": datetime.now().isoformat(),
            "version": "1.0"
        }, indent=2), encoding="utf-8")

        log("✓ تم تثبيت التعريب بنجاح! جاهز للانطلاق في يارنام.")
        return True

    def uninstall(self, log_callback=None):
        """إلغاء تثبيت التعريب واسترجاع الوضع الأصلي"""
        def log(msg):
            if log_callback:
                log_callback(msg)
            else:
                print(msg)

        if not self.bbport_dir:
            raise ValueError("مسار اللعبة غير محدد")

        log("1. جاري تعطيل مود التعريب من mods.json...")
        mods_json_path = self.bbport_dir / "mods.json"
        if mods_json_path.is_file():
            try:
                mods_data = json.loads(mods_json_path.read_text(encoding="utf-8"))
                order = mods_data.get("order", [])
                if "Arabic" in order:
                    order.remove("Arabic")
                mods_data["order"] = order
                mods_json_path.write_text(json.dumps(mods_data, indent=2), encoding="utf-8")
            except Exception as e:
                log(f"تنبيه: خطأ في تعديل mods.json ({e})")

        arabic_mod_dir = self.bbport_dir / "mods" / "Arabic"
        if arabic_mod_dir.is_dir():
            log("2. جاري حذف ملفات مود التعريب...")
            try:
                shutil.rmtree(arabic_mod_dir)
                log("✓ تم حذف مجلد التعريب بنجاح.")
            except Exception as e:
                log(f"تنبيه: لم يتم حذف مجلد المود كاملاً ({e})")

        log("✓ تم استرجاع النسخة الإنجليزية الأصلية بنجاح.")
        return True

    def launch_game(self):
        """تشغيل اللعبة مباشرة"""
        if not self.bbport_dir:
            raise ValueError("مسار اللعبة غير محدد")

        exe_candidates = [
            self.bbport_dir / "Play Bloodborne.exe",
            self.bbport_dir / "Bloodborne.exe",
            self.game_root / "bbport-windows" / "Play Bloodborne.exe" if self.game_root else None,
            self.game_root / "bbport-windows" / "Bloodborne.exe" if self.game_root else None,
        ]

        for exe in exe_candidates:
            if exe and exe.is_file():
                subprocess.Popen([str(exe)], cwd=str(exe.parent))
                return str(exe)

        raise FileNotFoundError("لم يتم العثور على ملف تشغيل Bloodborne.exe")
