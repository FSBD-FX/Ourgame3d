@echo off
cd /d "%~dp0"
pwsh -NoProfile -ExecutionPolicy Bypass -File "%~dp0tools\scripts\launch-hero-stable-preview-v001.ps1"
pause
