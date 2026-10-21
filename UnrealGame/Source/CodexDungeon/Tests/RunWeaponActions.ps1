param(
 [ValidateSet('BASELINE','RED','GREEN','VERIFY')][string]$Phase='VERIFY',
 [string]$CompilerRoot='C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Tools\MSVC\14.38.33130',
 [string]$SdkRoot='C:\Program Files (x86)\Windows Kits\10',
 [string]$SdkVersion='10.0.19041.0'
)
$ErrorActionPreference='Stop'
$weaponOutput=Join-Path $env:TEMP ('OurgameWeaponActions\'+(Get-Date -Format 'yyyyMMdd-HHmmss-fff')+'-'+$Phase)
New-Item -ItemType Directory -Force -Path $weaponOutput | Out-Null
$weaponLog=Join-Path $weaponOutput 'standalone.log'
$weaponPreviousInclude=$env:INCLUDE;$weaponPreviousLib=$env:LIB
try {
 $env:INCLUDE="$CompilerRoot\include;$SdkRoot\Include\$SdkVersion\ucrt;$SdkRoot\Include\$SdkVersion\shared;$SdkRoot\Include\$SdkVersion\um"
 $env:LIB="$CompilerRoot\lib\x64;$SdkRoot\Lib\$SdkVersion\ucrt\x64;$SdkRoot\Lib\$SdkVersion\um\x64"
 "PHASE=$Phase; standalone C++17 weapon kernel only; no UE/runtime acceptance." | Tee-Object -FilePath $weaponLog
 & "$CompilerRoot\bin\Hostx64\x64\cl.exe" /nologo /utf-8 /std:c++17 /EP /P /UDUNGEON_WEAPON_ACTIONS_STANDALONE (Join-Path $PSScriptRoot 'DungeonWeaponActionsStandalone.cpp') "/Fi:$weaponOutput\no-standalone-macro.i" 2>&1 | Tee-Object -FilePath $weaponLog -Append
 if($LASTEXITCODE -ne 0){throw 'Standalone guard preprocessing failed.'}
 if(-not [string]::IsNullOrWhiteSpace((Get-Content -LiteralPath (Join-Path $weaponOutput 'no-standalone-macro.i') -Raw))){throw 'Test translation unit is not empty without its opt-in macro.'}
 'NO_MACRO_TRANSLATION_UNIT_EMPTY=true' | Tee-Object -FilePath $weaponLog -Append
 & "$CompilerRoot\bin\Hostx64\x64\cl.exe" /nologo /EHsc /utf-8 /std:c++17 /W4 /WX /DDUNGEON_WEAPON_ACTIONS_STANDALONE (Join-Path $PSScriptRoot 'DungeonWeaponActionsStandalone.cpp') "/Fe:$weaponOutput\weapon-actions.exe" "/Fo:$weaponOutput\weapon-actions.obj" 2>&1 | Tee-Object -FilePath $weaponLog -Append
 $weaponExit=$LASTEXITCODE
 "COMPILE_EXIT=$weaponExit" | Tee-Object -FilePath $weaponLog -Append
 if($weaponExit -eq 0){& "$weaponOutput\weapon-actions.exe" 2>&1 | Tee-Object -FilePath $weaponLog -Append;$weaponExit=$LASTEXITCODE}
 "EXIT_CODE=$weaponExit" | Tee-Object -FilePath $weaponLog -Append
 "LOG_PATH=$weaponLog"
} finally {$env:INCLUDE=$weaponPreviousInclude;$env:LIB=$weaponPreviousLib}
exit $weaponExit
