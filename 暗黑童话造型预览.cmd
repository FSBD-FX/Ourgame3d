@echo off
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0tools\scripts\play-first-room.ps1" -FairytaleLookdevPreview
pause
