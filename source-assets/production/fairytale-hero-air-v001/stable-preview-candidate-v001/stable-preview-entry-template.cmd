@echo off
cd /d "%~dp0"
pwsh -NoProfile -ExecutionPolicy Bypass -File "%~dp0_proof\tools\launch-stable-preview-v001.ps1" -LightArtTrial -GuardFullArt
pause
