param(
 [string]$CompilerRoot='C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Tools\MSVC\14.38.33130',
 [string]$SdkRoot='C:\Program Files (x86)\Windows Kits\10',
 [string]$SdkVersion='10.0.19041.0',
 [string]$LogPath=''
)
$ErrorActionPreference='Stop'
$stoneTestOutput=Join-Path $env:TEMP 'OurgameStoneKnight'
New-Item -ItemType Directory -Force -Path $stoneTestOutput | Out-Null
$env:INCLUDE="$CompilerRoot\include;$SdkRoot\Include\$SdkVersion\ucrt;$SdkRoot\Include\$SdkVersion\shared;$SdkRoot\Include\$SdkVersion\um"
$env:LIB="$CompilerRoot\lib\x64;$SdkRoot\Lib\$SdkVersion\ucrt\x64;$SdkRoot\Lib\$SdkVersion\um\x64"
$stoneLines=@('Standalone stone-knight C++17 kernel; caller sweep fixtures only; no UE physics or runtime.')
$stoneLines+=& "$CompilerRoot\bin\Hostx64\x64\cl.exe" /nologo /EHsc /std:c++17 /W4 /WX /DDUNGEON_STONE_KNIGHT_STANDALONE (Join-Path $PSScriptRoot 'DungeonStoneKnightStandalone.cpp') "/Fe:$stoneTestOutput\stone-knight.exe" "/Fo:$stoneTestOutput\stone-knight.obj" 2>&1
$stoneExit=$LASTEXITCODE
if($stoneExit -eq 0){$stoneLines+=& "$stoneTestOutput\stone-knight.exe" 2>&1;$stoneExit=$LASTEXITCODE}
$stoneLines+="EXIT_CODE=$stoneExit"
if($LogPath){New-Item -ItemType Directory -Force -Path (Split-Path -Parent $LogPath) | Out-Null;$stoneLines | Set-Content -LiteralPath $LogPath -Encoding utf8}
$stoneLines | ForEach-Object { Write-Output $_ }
exit $stoneExit
