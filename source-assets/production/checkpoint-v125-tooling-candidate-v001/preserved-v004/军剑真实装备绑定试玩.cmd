@echo off
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0tools\scripts\launch-fairytale-equipment-bound-v004.ps1"
if errorlevel 1 pause
