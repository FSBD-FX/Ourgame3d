@echo off
cd /d F:\Ourgame
pwsh -NoProfile -File "%~dp0tools\scripts\launch-fairytale-walk-trial-v001.ps1"
if errorlevel 1 pause
