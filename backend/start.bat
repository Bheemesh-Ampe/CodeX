@echo off
title CivicFix Backend Server
cd /d "%~dp0"
echo ==================================================
echo   Starting CivicFix Backend Server
echo ==================================================
python run.py
if errorlevel 1 (
    echo.
    echo Backend exited with error. Attempting to install requirements...
    pip install -r requirements.txt
    python run.py
)
pause
