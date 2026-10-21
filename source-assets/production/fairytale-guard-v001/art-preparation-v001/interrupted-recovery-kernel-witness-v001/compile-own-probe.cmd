@echo off
call "C:/Program Files/Microsoft Visual Studio/2022/Community/Common7/Tools/VsDevCmd.bat" -no_logo -arch=x64 -host_arch=x64
if errorlevel 1 exit /b 1
cl /nologo /std:c++17 /EHsc /W4 /Od /Fe:"F:\Ourgame\source-assets\production\fairytale-guard-v001\art-preparation-v001\interrupted-recovery-kernel-witness-v001\probe.exe" /Fo:"F:\Ourgame\source-assets\production\fairytale-guard-v001\art-preparation-v001\interrupted-recovery-kernel-witness-v001\obj\" "F:\Ourgame\source-assets\production\fairytale-guard-v001\art-preparation-v001\interrupted-recovery-kernel-witness-v001\DungeonStoneGuard.cpp" "F:\Ourgame\source-assets\production\fairytale-guard-v001\art-preparation-v001\interrupted-recovery-kernel-witness-v001\probe.cpp"
