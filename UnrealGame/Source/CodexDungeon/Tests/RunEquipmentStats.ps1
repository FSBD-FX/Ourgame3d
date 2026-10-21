param(
 [ValidateSet('RED','GREEN','VERIFY')][string]$Phase='VERIFY',
 [string]$CompilerRoot='C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Tools\MSVC\14.38.33130',
 [string]$SdkRoot='C:\Program Files (x86)\Windows Kits\10',
 [string]$SdkVersion='10.0.19041.0'
)
$ErrorActionPreference='Stop'
$equipmentOutput=Join-Path $env:TEMP ('OurgameEquipmentStats\'+(Get-Date -Format 'yyyyMMdd-HHmmss-fff')+'-'+$Phase)
New-Item -ItemType Directory -Path $equipmentOutput | Out-Null
$equipmentLog=Join-Path $equipmentOutput 'standalone.log'
$equipmentOldInclude=$env:INCLUDE;$equipmentOldLib=$env:LIB
$equipmentExit=1
try {
 $env:INCLUDE="$CompilerRoot\include;$SdkRoot\Include\$SdkVersion\ucrt;$SdkRoot\Include\$SdkVersion\shared;$SdkRoot\Include\$SdkVersion\um"
 $env:LIB="$CompilerRoot\lib\x64;$SdkRoot\Lib\$SdkVersion\ucrt\x64;$SdkRoot\Lib\$SdkVersion\um\x64"
 "PHASE=$Phase; standalone C++17 equipment stats only; no UE build/runtime acceptance." | Tee-Object -FilePath $equipmentLog
 & "$CompilerRoot\bin\Hostx64\x64\cl.exe" /nologo /utf-8 /std:c++17 /EP /P /UDUNGEON_EQUIPMENT_STATS_STANDALONE (Join-Path $PSScriptRoot 'DungeonEquipmentStatsStandalone.cpp') "/Fi:$equipmentOutput\no-standalone-macro.i" 2>&1 | Tee-Object -FilePath $equipmentLog -Append
 if($LASTEXITCODE -ne 0){throw 'Standalone guard preprocessing failed.'}
 if(-not [string]::IsNullOrWhiteSpace((Get-Content -LiteralPath (Join-Path $equipmentOutput 'no-standalone-macro.i') -Raw))){throw 'Test translation unit is not empty without its opt-in macro.'}
 'NO_MACRO_TRANSLATION_UNIT_EMPTY=true' | Tee-Object -FilePath $equipmentLog -Append
 & "$CompilerRoot\bin\Hostx64\x64\cl.exe" /nologo /EHsc /utf-8 /std:c++17 /W4 /WX /DDUNGEON_EQUIPMENT_STATS_STANDALONE (Join-Path $PSScriptRoot 'DungeonEquipmentStatsStandalone.cpp') "/Fe:$equipmentOutput\equipment-stats.exe" "/Fo:$equipmentOutput\equipment-stats.obj" 2>&1 | Tee-Object -FilePath $equipmentLog -Append
 $equipmentExit=$LASTEXITCODE
 "COMPILE_EXIT=$equipmentExit" | Tee-Object -FilePath $equipmentLog -Append
 if($equipmentExit -eq 0){
  & "$equipmentOutput\equipment-stats.exe" 2>&1 | Tee-Object -FilePath $equipmentLog -Append
  $equipmentExit=$LASTEXITCODE
 }
 "EXIT_CODE=$equipmentExit" | Tee-Object -FilePath $equipmentLog -Append
 "LOG_PATH=$equipmentLog"
} finally { $env:INCLUDE=$equipmentOldInclude;$env:LIB=$equipmentOldLib }
exit $equipmentExit
