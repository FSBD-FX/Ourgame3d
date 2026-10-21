param(
 [ValidateSet('RED','GREEN','VERIFY')][string]$Phase='VERIFY',
 [string]$CompilerRoot='C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Tools\MSVC\14.38.33130',
 [string]$SdkRoot='C:\Program Files (x86)\Windows Kits\10',
 [string]$SdkVersion='10.0.19041.0'
)
$ErrorActionPreference='Stop'
$explorationOutput=Join-Path $env:TEMP ('OurgameExploration\'+(Get-Date -Format 'yyyyMMdd-HHmmss-fff')+'-'+$Phase)
New-Item -ItemType Directory -Path $explorationOutput | Out-Null
$explorationLog=Join-Path $explorationOutput 'standalone.log'
$explorationPreviousInclude=$env:INCLUDE
$explorationPreviousLib=$env:LIB
$explorationExit=1
try {
 $env:INCLUDE="$CompilerRoot\include;$SdkRoot\Include\$SdkVersion\ucrt;$SdkRoot\Include\$SdkVersion\shared;$SdkRoot\Include\$SdkVersion\um"
 $env:LIB="$CompilerRoot\lib\x64;$SdkRoot\Lib\$SdkVersion\ucrt\x64;$SdkRoot\Lib\$SdkVersion\um\x64"
 "PHASE=$Phase; standalone C++17 visual exploration only; no UE/runtime or D13 IO acceptance." | Tee-Object -FilePath $explorationLog
 & "$CompilerRoot\bin\Hostx64\x64\cl.exe" /nologo /utf-8 /std:c++17 /EP /P /UDUNGEON_EXPLORATION_STANDALONE (Join-Path $PSScriptRoot 'DungeonExplorationStandalone.cpp') "/Fi:$explorationOutput\no-standalone-macro.i" 2>&1 | Tee-Object -FilePath $explorationLog -Append
 if($LASTEXITCODE -ne 0){throw 'Standalone guard preprocessing failed.'}
 if(-not [string]::IsNullOrWhiteSpace((Get-Content -LiteralPath (Join-Path $explorationOutput 'no-standalone-macro.i') -Raw))){throw 'Test translation unit must be empty without opt-in macro.'}
 'NO_MACRO_TRANSLATION_UNIT_EMPTY=true' | Tee-Object -FilePath $explorationLog -Append
 & "$CompilerRoot\bin\Hostx64\x64\cl.exe" /nologo /EHsc /utf-8 /std:c++17 /W4 /WX /DDUNGEON_EXPLORATION_STANDALONE (Join-Path $PSScriptRoot 'DungeonExplorationStandalone.cpp') "/Fe:$explorationOutput\exploration.exe" "/Fo:$explorationOutput\exploration.obj" 2>&1 | Tee-Object -FilePath $explorationLog -Append
 $explorationExit=$LASTEXITCODE
 "COMPILE_EXIT=$explorationExit" | Tee-Object -FilePath $explorationLog -Append
 if($explorationExit -eq 0){& "$explorationOutput\exploration.exe" 2>&1 | Tee-Object -FilePath $explorationLog -Append;$explorationExit=$LASTEXITCODE}
 "EXIT_CODE=$explorationExit" | Tee-Object -FilePath $explorationLog -Append
 "LOG_PATH=$explorationLog"
} finally { $env:INCLUDE=$explorationPreviousInclude;$env:LIB=$explorationPreviousLib }
exit $explorationExit
