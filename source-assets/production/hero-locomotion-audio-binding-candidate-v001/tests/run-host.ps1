param([ValidateSet('RED','GREEN')][string]$Phase='GREEN')
$ErrorActionPreference='Stop'
$candidate=Split-Path -Parent $PSScriptRoot
$compilerRoot='C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Tools\MSVC\14.38.33130'
$sdkRoot='C:\Program Files (x86)\Windows Kits\10';$sdkVersion='10.0.19041.0'
$out=Join-Path $candidate ('reports/host-'+$Phase+'-'+(Get-Date -Format 'yyyyMMdd-HHmmss-fff'))
New-Item -ItemType Directory -Path $out | Out-Null
$priorInclude=$env:INCLUDE;$priorLib=$env:LIB
try {
 $env:INCLUDE="$compilerRoot\include;$sdkRoot\Include\$sdkVersion\ucrt;$sdkRoot\Include\$sdkVersion\shared;$sdkRoot\Include\$sdkVersion\um"
 $env:LIB="$compilerRoot\lib\x64;$sdkRoot\Lib\$sdkVersion\ucrt\x64;$sdkRoot\Lib\$sdkVersion\um\x64"
 ('#include "DungeonHeroLocomotionAudioV001.h"'+[Environment]::NewLine+'void HeaderCheck(){DungeonHeroLocomotionAudioV001::FState State;(void)State;}') | Set-Content -LiteralPath (Join-Path $out 'header-check.cpp') -Encoding utf8
 & "$compilerRoot\bin\Hostx64\x64\cl.exe" /nologo /c /std:c++17 /utf-8 /W4 /WX /EHs-c- /D_HAS_EXCEPTIONS=0 ('/I'+ (Join-Path $candidate 'Source')) (Join-Path $out 'header-check.cpp') ('/Fo:'+ (Join-Path $out 'header-check.obj')) 2>&1 | Tee-Object -FilePath (Join-Path $out 'no-exceptions-compile.log')
 if($LASTEXITCODE -ne 0){throw 'Pure header no-exceptions compilation failed'}
 & "$compilerRoot\bin\Hostx64\x64\cl.exe" /nologo /EHsc /std:c++17 /utf-8 /W4 /WX '/IF:/Ourgame/UnrealGame/Source/CodexDungeon' ('/I'+ (Join-Path $candidate 'Source')) (Join-Path $PSScriptRoot 'locomotion-audio.cpp') ('/Fe:'+ (Join-Path $out 'tests.exe')) ('/Fo:'+ (Join-Path $out 'tests.obj')) 2>&1 | Tee-Object -FilePath (Join-Path $out 'compile.log')
 if($LASTEXITCODE -ne 0){throw 'Host compilation failed'}
 & (Join-Path $out 'tests.exe') 2>&1 | Tee-Object -FilePath (Join-Path $out 'results.log')
 $result=$LASTEXITCODE
 "PHASE=$Phase EXIT=$result HOST_ONLY=true UE_RUN=false OUTPUT=$out" | Tee-Object -FilePath (Join-Path $out 'receipt.txt')
} finally {$env:INCLUDE=$priorInclude;$env:LIB=$priorLib}
exit $result
