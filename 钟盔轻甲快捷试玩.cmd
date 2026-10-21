@echo off
cd /d "%~dp0"
pwsh -NoProfile -ExecutionPolicy Bypass -File "%~dp0tools\scripts\launch-hero-stable-preview-v002.ps1"
pause
