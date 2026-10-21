param(
 [ValidateSet('RED','GREEN','VERIFY')][string]$Phase='VERIFY',
 [string]$CompilerRoot='C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Tools\MSVC\14.38.33130',
 [string]$SdkRoot='C:\Program Files (x86)\Windows Kits\10',
 [string]$SdkVersion='10.0.19041.0'
)
$ErrorActionPreference='Stop'
$equipmentInventoryOutput=Join-Path $env:TEMP ('OurgameEquipmentInventory\'+(Get-Date -Format 'yyyyMMdd-HHmmss-fff')+'-'+$Phase)
New-Item -ItemType Directory -Path $equipmentInventoryOutput | Out-Null
$equipmentInventoryLog=Join-Path $equipmentInventoryOutput 'standalone.log'
$equipmentInventoryPreviousInclude=$env:INCLUDE
$equipmentInventoryPreviousLib=$env:LIB
$equipmentInventoryExit=1
try {
 $env:INCLUDE="$CompilerRoot\include;$SdkRoot\Include\$SdkVersion\ucrt;$SdkRoot\Include\$SdkVersion\shared;$SdkRoot\Include\$SdkVersion\um"
 $env:LIB="$CompilerRoot\lib\x64;$SdkRoot\Lib\$SdkVersion\ucrt\x64;$SdkRoot\Lib\$SdkVersion\um\x64"
 "PHASE=$Phase; standalone C++17 equipment inventory memory only; no UE/runtime or D13 IO acceptance." | Tee-Object -FilePath $equipmentInventoryLog
 & "$CompilerRoot\bin\Hostx64\x64\cl.exe" /nologo /utf-8 /std:c++17 /EP /P /UDUNGEON_EQUIPMENT_INVENTORY_STANDALONE (Join-Path $PSScriptRoot 'DungeonEquipmentInventoryStandalone.cpp') "/Fi:$equipmentInventoryOutput\no-standalone-macro.i" 2>&1 | Tee-Object -FilePath $equipmentInventoryLog -Append
 if($LASTEXITCODE -ne 0){throw 'Standalone guard preprocessing failed.'}
 if(-not [string]::IsNullOrWhiteSpace((Get-Content -LiteralPath (Join-Path $equipmentInventoryOutput 'no-standalone-macro.i') -Raw))){throw 'Test translation unit must be empty without opt-in macro.'}
 'NO_MACRO_TRANSLATION_UNIT_EMPTY=true' | Tee-Object -FilePath $equipmentInventoryLog -Append
 & "$CompilerRoot\bin\Hostx64\x64\cl.exe" /nologo /EHsc /utf-8 /std:c++17 /W4 /WX /DDUNGEON_EQUIPMENT_INVENTORY_STANDALONE (Join-Path $PSScriptRoot 'DungeonEquipmentInventoryStandalone.cpp') "/Fe:$equipmentInventoryOutput\equipmentInventory.exe" "/Fo:$equipmentInventoryOutput\equipmentInventory.obj" 2>&1 | Tee-Object -FilePath $equipmentInventoryLog -Append
 $equipmentInventoryExit=$LASTEXITCODE
 "COMPILE_EXIT=$equipmentInventoryExit" | Tee-Object -FilePath $equipmentInventoryLog -Append
 if($equipmentInventoryExit -eq 0){& "$equipmentInventoryOutput\equipmentInventory.exe" 2>&1 | Tee-Object -FilePath $equipmentInventoryLog -Append;$equipmentInventoryExit=$LASTEXITCODE}
 "EXIT_CODE=$equipmentInventoryExit" | Tee-Object -FilePath $equipmentInventoryLog -Append
 "LOG_PATH=$equipmentInventoryLog"
} finally { $env:INCLUDE=$equipmentInventoryPreviousInclude;$env:LIB=$equipmentInventoryPreviousLib }
exit $equipmentInventoryExit

