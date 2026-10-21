@echo off
cd /d "%~dp0"
pwsh -NoProfile -ExecutionPolicy Bypass -File "%~dp0tools\scripts\launch-hero-development-v148-portable-v001.ps1"
pause
