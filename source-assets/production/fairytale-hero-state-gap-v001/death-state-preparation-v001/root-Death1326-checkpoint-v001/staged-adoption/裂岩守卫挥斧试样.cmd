@echo off
cd /d "F:\Ourgame"
pwsh -NoProfile -ExecutionPolicy Bypass -File "F:\Ourgame\tools\scripts\launch-guard-room-native-trial-v009.ps1" -LightArtTrial -GuardFullArt
pause
