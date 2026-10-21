@echo off
call "C:\Program Files\Microsoft Visual Studio\2022\Community\Common7\Tools\VsDevCmd.bat" -arch=x64 -host_arch=x64 >nul
if errorlevel 1 exit /b %errorlevel%
cl /nologo /std:c++17 /EHsc /W4 /WX /I"F:/Ourgame/UnrealGame/Source/CodexDungeon" /I"projected/UnrealGame/Source/CodexDungeon" tests/secondary_plan_tests.cpp /Fe:verification/secondary-plan-tests-red.exe /Fo:verification/secondary-plan-tests-red.obj
if errorlevel 1 exit /b %errorlevel%
verification\secondary-plan-tests-red.exe
exit /b %errorlevel%

