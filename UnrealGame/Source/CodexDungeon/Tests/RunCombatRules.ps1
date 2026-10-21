param(
    [string]$CompilerRoot = 'C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Tools\MSVC\14.38.33130',
    [string]$SdkRoot = 'C:\Program Files (x86)\Windows Kits\10',
    [string]$SdkVersion = '10.0.19041.0'
)
$ErrorActionPreference = 'Stop'
$testOutput = Join-Path $env:TEMP 'OurgameDungeonRules'
New-Item -ItemType Directory -Force -Path $testOutput | Out-Null
$env:INCLUDE = "$CompilerRoot\include;$SdkRoot\Include\$SdkVersion\ucrt;$SdkRoot\Include\$SdkVersion\shared;$SdkRoot\Include\$SdkVersion\um"
$env:LIB = "$CompilerRoot\lib\x64;$SdkRoot\Lib\$SdkVersion\ucrt\x64;$SdkRoot\Lib\$SdkVersion\um\x64"
& "$CompilerRoot\bin\Hostx64\x64\cl.exe" /nologo /EHsc /std:c++17 /W4 /DDUNGEON_COMBAT_RULES_STANDALONE (Join-Path $PSScriptRoot 'DungeonCombatRulesStandalone.cpp') "/Fe:$testOutput\combat-rules.exe" "/Fo:$testOutput\combat-rules.obj"
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
& "$testOutput\combat-rules.exe"
exit $LASTEXITCODE
