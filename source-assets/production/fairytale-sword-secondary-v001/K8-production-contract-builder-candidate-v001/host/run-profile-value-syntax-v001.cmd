@echo off
call "C:\Program Files\Microsoft Visual Studio\2022\Community\Common7\Tools\VsDevCmd.bat" -arch=x64 -host_arch=x64 > "%~dp0vcvars-profile-v001.log"
if errorlevel 1 exit /b %errorlevel%
cl /nologo /std:c++17 /EHsc /W4 /WX /I"%~dp0..\baseline" /I"F:\Ourgame\UnrealGame\Source\CodexDungeon" "%~dp0profile-value-syntax-v001.cpp" /Fo"%~dp0profile-value-syntax-v001.obj" /Fe"%~dp0profile-value-syntax-v001.exe"
if errorlevel 1 exit /b %errorlevel%
"%~dp0profile-value-syntax-v001.exe"
