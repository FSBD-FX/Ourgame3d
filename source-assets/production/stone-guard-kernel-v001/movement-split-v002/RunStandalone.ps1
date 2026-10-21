param([string]$Version='movement-RED-v001',[string]$SourceVersion='before-v001',[string]$Suite='DungeonStoneGuardMovementStandalone.cpp',[string]$TestRoot='')
$ErrorActionPreference='Stop'
$guardFamily=$PSScriptRoot
$guardOutput=Join-Path (Join-Path $PSScriptRoot 'runs') $Version
if(Test-Path -LiteralPath $guardOutput){throw 'Refusing to overwrite prior standalone run'}
New-Item -ItemType Directory -Path $guardOutput | Out-Null
$guardCompilerRoot='C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Tools\MSVC\14.38.33130'
$guardSdkRoot='C:\Program Files (x86)\Windows Kits\10'
$guardSdkVersion='10.0.19041.0'
$env:INCLUDE="$guardCompilerRoot\include;$guardSdkRoot\Include\$guardSdkVersion\ucrt;$guardSdkRoot\Include\$guardSdkVersion\shared;$guardSdkRoot\Include\$guardSdkVersion\um"
$env:LIB="$guardCompilerRoot\lib\x64;$guardSdkRoot\Lib\$guardSdkVersion\ucrt\x64;$guardSdkRoot\Lib\$guardSdkVersion\um\x64"
$guardSource=Join-Path $guardFamily $SourceVersion
if(-not $TestRoot){$TestRoot=Join-Path $guardFamily 'tests'}
$guardTest=Join-Path $TestRoot $Suite
Push-Location -LiteralPath $guardOutput
try {
 $guardBuild=@(& "$guardCompilerRoot\bin\Hostx64\x64\cl.exe" /nologo /EHsc /std:c++17 /W4 /WX /utf-8 "/I$guardSource" "/I$TestRoot" (Join-Path $guardSource 'DungeonStoneGuard.cpp') $guardTest '/Fe:stone-guard.exe' 2>&1)
 $guardBuildExit=$LASTEXITCODE
 $guardBuild+="BUILD_EXIT_CODE=$guardBuildExit"
 $guardBuild | Set-Content -LiteralPath 'build.log' -Encoding utf8
 $guardBuild | ForEach-Object {Write-Output $_}
 if($guardBuildExit -ne 0){exit $guardBuildExit}
 $guardRun=@(& '.\stone-guard.exe' 2>&1)
 $guardRunExit=$LASTEXITCODE
 $guardRun+="RUN_EXIT_CODE=$guardRunExit"
 $guardRun | Set-Content -LiteralPath 'run.log' -Encoding utf8
 $guardRun | ForEach-Object {Write-Output $_}
 exit $guardRunExit
} finally {Pop-Location}
