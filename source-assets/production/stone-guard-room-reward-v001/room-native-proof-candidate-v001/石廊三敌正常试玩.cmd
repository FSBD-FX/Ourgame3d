@echo off
if "%~1"=="" (
  echo Usage: drag or pass the exact compiled snapshot directory as the first argument.
  echo Root must seal the admitted Source and DLL before this native trial.
  pause
  exit /b 2
)
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0tools\scripts\launch-guard-room-native-trial-v001.ps1" -Snapshot "%~1" -LightArtTrial
pause
