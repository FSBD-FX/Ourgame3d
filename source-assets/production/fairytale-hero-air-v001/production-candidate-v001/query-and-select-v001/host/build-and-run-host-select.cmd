@echo off
set "AIR_HOST_VC=C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Tools\MSVC\14.38.33130"
set "AIR_HOST_SDK=C:\Program Files (x86)\Windows Kits\10"
set "INCLUDE=%AIR_HOST_VC%\include;%AIR_HOST_SDK%\Include\10.0.19041.0\ucrt;%AIR_HOST_SDK%\Include\10.0.19041.0\shared;%AIR_HOST_SDK%\Include\10.0.19041.0\um"
set "LIB=%AIR_HOST_VC%\lib\x64;%AIR_HOST_SDK%\Lib\10.0.19041.0\ucrt\x64;%AIR_HOST_SDK%\Lib\10.0.19041.0\um\x64"
set "PATH=%AIR_HOST_VC%\bin\Hostx64\x64;%PATH%"
if not exist "%~dp0build" mkdir "%~dp0build"
cl /nologo /EHsc /std:c++17 /W4 /I"%~dp0shim" /Fo"%~dp0build\host_select.obj" /Fe"%~dp0build\host_select.exe" /Fd"%~dp0build\host_select.pdb" "%~dp0host-select-cases-v001.cpp"
if errorlevel 1 exit /b 3
"%~dp0build\host_select.exe"
