param(
 [string]$CompilerRoot='C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Tools\MSVC\14.38.33130',
 [string]$SdkRoot='C:\Program Files (x86)\Windows Kits\10',
 [string]$SdkVersion='10.0.19041.0',
 [string]$LogPath=''
)
$ErrorActionPreference='Stop'
$contentTestOutput=Join-Path $env:TEMP 'OurgameDungeonContentCombat'
New-Item -ItemType Directory -Force -Path $contentTestOutput | Out-Null
$env:INCLUDE="$CompilerRoot\include;$SdkRoot\Include\$SdkVersion\ucrt;$SdkRoot\Include\$SdkVersion\shared;$SdkRoot\Include\$SdkVersion\um"
$env:LIB="$CompilerRoot\lib\x64;$SdkRoot\Lib\$SdkVersion\ucrt\x64;$SdkRoot\Lib\$SdkVersion\um\x64"
$contentLines=@('Standalone C++17 action kernel; no UE build or runtime.')
$contentLines+=& "$CompilerRoot\bin\Hostx64\x64\cl.exe" /nologo /EHsc /std:c++17 /W4 /WX (Join-Path $PSScriptRoot 'DungeonContentCombatStandalone.cpp') "/Fe:$contentTestOutput\content-combat.exe" "/Fo:$contentTestOutput\content-combat.obj" 2>&1
$contentExit=$LASTEXITCODE
if($contentExit -eq 0){$contentLines+=& "$contentTestOutput\content-combat.exe" 2>&1;$contentExit=$LASTEXITCODE}
$contentLines+="EXIT_CODE=$contentExit"
if($LogPath){$contentLogDirectory=Split-Path -Parent $LogPath;New-Item -ItemType Directory -Force -Path $contentLogDirectory | Out-Null;$contentLines | Set-Content -LiteralPath $LogPath -Encoding utf8}
$contentLines | ForEach-Object { Write-Output $_ }
exit $contentExit
