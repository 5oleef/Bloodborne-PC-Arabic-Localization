# -*- coding: utf-8 -*-
"""
نقطة الدخول الرئيسية لتطبيق تعريب Bloodborne PC Native
"""
import sys
from pathlib import Path

# إضافة المجلد الحالي إلى مسار الاستيراد
CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

from gui import launch_gui

if __name__ == "__main__":
    launch_gui()
