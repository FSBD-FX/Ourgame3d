@echo off
call "C:\Program Files\Microsoft Visual Studio\2022\Community\Common7\Tools\VsDevCmd.bat" -arch=x64 -host_arch=x64 >nul
if errorlevel 1 exit /b %errorlevel%
cl /nologo /std:c++17 /EHsc /W4 /WX /I"F:/Ourgame/UnrealGame/Source/CodexDungeon" host/verify_real_event_order.cpp /Fe:evidence/real-event-order.exe /Fo:evidence/real-event-order.obj
if errorlevel 1 exit /b %errorlevel%
evidence\real-event-order.exe
exit /b %errorlevel%
