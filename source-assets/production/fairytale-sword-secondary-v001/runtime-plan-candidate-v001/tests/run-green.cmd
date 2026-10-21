@echo off
call "C:\Program Files\Microsoft Visual Studio\2022\Community\Common7\Tools\VsDevCmd.bat" -arch=x64 -host_arch=x64 >nul
if errorlevel 1 exit /b %errorlevel%
cl /nologo /std:c++17 /EHsc /W4 /WX /I"projected/UnrealGame/Source/CodexDungeon" /I"F:/Ourgame/UnrealGame/Source/CodexDungeon" tests/secondary_plan_tests.cpp /Fe:verification/secondary-plan-tests-green.exe /Fo:verification/secondary-plan-tests-green.obj
if errorlevel 1 exit /b %errorlevel%
verification\secondary-plan-tests-green.exe
exit /b %errorlevel%



