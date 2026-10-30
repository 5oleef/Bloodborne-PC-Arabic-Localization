@echo off
chcp 65001 >nul
title Bloodborne PC Arabic Localization Tool
echo ===================================================
echo     Bloodborne PC Arabic Localization (Egyptian)
echo ===================================================
echo Launching application...

set PYTHON_EXE=C:\Users\abdel\AppData\Local\Programs\Python\Python312\python.exe

if not exist "%PYTHON_EXE%" (
    where python >nul 2>nul
    if %ERRORLEVEL% equ 0 (
        set PYTHON_EXE=python
    ) else (
        echo [ERROR] Python not found on your system!
        pause
        exit /b 1
    )
)

start "" "%PYTHON_EXE%" "E:\Bloodborne\Bloodborne_Arabic_Tool\main.py"
exit /b 0
