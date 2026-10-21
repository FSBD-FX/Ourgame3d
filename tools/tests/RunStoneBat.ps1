param(
 [ValidateSet('RED','GREEN','VERIFY')][string]$Phase='VERIFY',
 [string]$CompilerRoot='C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Tools\MSVC\14.38.33130',
 [string]$SdkRoot='C:\Program Files (x86)\Windows Kits\10',
 [string]$SdkVersion='10.0.19041.0'
)
$ErrorActionPreference='Stop'
$batProject=Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$batSource=Join-Path $batProject 'UnrealGame\Source\CodexDungeon\Tests\DungeonStoneBatStandalone.cpp'
$batHeader=(Join-Path $batProject 'UnrealGame\Source\CodexDungeon\DungeonStoneBat.h').Replace('\','/')
$batOutput=Join-Path $env:TEMP ('OurgameStoneBat\'+(Get-Date -Format 'yyyyMMdd-HHmmss-fff')+'-'+$Phase)
New-Item -ItemType Directory -Path $batOutput | Out-Null
$batLog=Join-Path $batOutput 'standalone.log'
$batPreviousInclude=$env:INCLUDE;$batPreviousLib=$env:LIB
try {
 $env:INCLUDE="$CompilerRoot\include;$SdkRoot\Include\$SdkVersion\ucrt;$SdkRoot\Include\$SdkVersion\shared;$SdkRoot\Include\$SdkVersion\um"
 $env:LIB="$CompilerRoot\lib\x64;$SdkRoot\Lib\$SdkVersion\ucrt\x64;$SdkRoot\Lib\$SdkVersion\um\x64"
 "PHASE=$Phase; C++17 StoneBat pure kernel only; no UE/Actor/art/D13 IO acceptance." | Tee-Object -FilePath $batLog
 & "$CompilerRoot\bin\Hostx64\x64\cl.exe" /nologo /utf-8 /std:c++17 /EP /P /UDUNGEON_STONE_BAT_STANDALONE $batSource "/Fi:$batOutput\no-macro.i" 2>&1 | Tee-Object -FilePath $batLog -Append
 if($LASTEXITCODE -ne 0){throw 'Standalone guard preprocessing failed'}
 if(-not [string]::IsNullOrWhiteSpace((Get-Content -LiteralPath (Join-Path $batOutput 'no-macro.i') -Raw))){throw 'Standalone TU is not empty without its opt-in macro'}
 'NO_MACRO_TRANSLATION_UNIT_EMPTY=true' | Tee-Object -FilePath $batLog -Append
 ('#include "'+$batHeader+'"'+[Environment]::NewLine+'static_assert(DungeonStoneBat::FBatKernel::Definition().HP == 55, "source HP");') | Set-Content -LiteralPath (Join-Path $batOutput 'header.cpp') -Encoding utf8
 & "$CompilerRoot\bin\Hostx64\x64\cl.exe" /nologo /c /utf-8 /std:c++17 /W4 /WX /EHs-c- /D_HAS_EXCEPTIONS=0 (Join-Path $batOutput 'header.cpp') "/Fo:$batOutput\header.obj" 2>&1 | Tee-Object -FilePath $batLog -Append
 if($LASTEXITCODE -ne 0){throw 'Header without exceptions did not compile'}
 'NO_EXCEPTIONS_HEADER_COMPILE=true' | Tee-Object -FilePath $batLog -Append
 & "$CompilerRoot\bin\Hostx64\x64\cl.exe" /nologo /EHsc /utf-8 /std:c++17 /W4 /WX /DDUNGEON_STONE_BAT_STANDALONE $batSource "/Fe:$batOutput\stone-bat.exe" "/Fo:$batOutput\stone-bat.obj" 2>&1 | Tee-Object -FilePath $batLog -Append
 $batExit=$LASTEXITCODE;"COMPILE_EXIT=$batExit" | Tee-Object -FilePath $batLog -Append
 if($batExit -eq 0){& "$batOutput\stone-bat.exe" 2>&1 | Tee-Object -FilePath $batLog -Append;$batExit=$LASTEXITCODE}
 "EXIT_CODE=$batExit" | Tee-Object -FilePath $batLog -Append
 "LOG_PATH=$batLog"
} finally {$env:INCLUDE=$batPreviousInclude;$env:LIB=$batPreviousLib}
exit $batExit
