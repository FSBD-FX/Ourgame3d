@echo off
call "C:\Program Files\Microsoft Visual Studio\2022\Community\Common7\Tools\VsDevCmd.bat" -arch=x64 -host_arch=x64 >nul
if errorlevel 1 exit /b %errorlevel%
cl /nologo /std:c++17 /EHsc /W4 /WX /I"F:/Ourgame/source-assets/production/fairytale-sword-secondary-v001/runtime-plan-candidate-v001/verification/mutations/wrong-recovery-boundary" /I"F:/Ourgame/source-assets/production/fairytale-sword-secondary-v001/runtime-plan-candidate-v001/projected/UnrealGame/Source/CodexDungeon" /I"F:/Ourgame/UnrealGame/Source/CodexDungeon" tests/secondary_plan_tests.cpp /Fe:"F:/Ourgame/source-assets/production/fairytale-sword-secondary-v001/runtime-plan-candidate-v001/verification/mutations/wrong-recovery-boundary/test.exe" /Fo:"F:/Ourgame/source-assets/production/fairytale-sword-secondary-v001/runtime-plan-candidate-v001/verification/mutations/wrong-recovery-boundary/test.obj"
if errorlevel 1 exit /b %errorlevel%
"F:/Ourgame/source-assets/production/fairytale-sword-secondary-v001/runtime-plan-candidate-v001/verification/mutations/wrong-recovery-boundary/test.exe"
exit /b %errorlevel%
