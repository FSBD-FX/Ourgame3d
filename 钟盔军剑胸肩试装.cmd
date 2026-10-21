@echo off
chcp 65001 >nul
pwsh.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0tools\scripts\launch-fairytale-sword-armor-ready-v001.ps1"
if errorlevel 1 pause
