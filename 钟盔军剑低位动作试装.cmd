@echo off
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0tools\scripts\launch-fairytale-sword-body-v002.ps1"
pause
