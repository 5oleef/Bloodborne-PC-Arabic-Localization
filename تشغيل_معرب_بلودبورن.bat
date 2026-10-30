@echo off
chcp 65001 >nul
title مُعرّب Bloodborne PC Native (النسخة المصرية)
echo ===================================================
echo     مُعرّب بلودبورن للكمبيوتر (النسخة المصرية) 🩸
echo ===================================================
echo جاري تشغيل الأداة...

set PYTHON_EXE=C:\Users\abdel\AppData\Local\Programs\Python\Python312\python.exe

if not exist "%PYTHON_EXE%" (
    where python >nul 2>nul
    if %ERRORLEVEL% equ 0 (
        set PYTHON_EXE=python
    ) else (
        echo [خطأ] لم يتم العثور على بايثون المثبت على جهازك!
        pause
        exit /b 1
    )
)

start "" "%PYTHON_EXE%" "E:\Bloodborne\Bloodborne_Arabic_Tool\main.py"
exit /b 0
