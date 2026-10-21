@echo off
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0tools\scripts\play-first-room.ps1" -FirstUnitPreview
if errorlevel 1 pause
