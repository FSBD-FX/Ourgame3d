param([Parameter(Mandatory=$true)][string]$Version,[string]$SourceVariant='stage0-source',[string]$Suite='DungeonStoneGuardRestoreStandalone.cpp')
$ErrorActionPreference='Stop'
$guardRestoreOutput=Join-Path (Join-Path $PSScriptRoot 'runs') $Version
if(Test-Path -LiteralPath $guardRestoreOutput){throw 'Refusing to overwrite prior restore evidence'}
New-Item -ItemType Directory -Path $guardRestoreOutput | Out-Null
$guardRestoreCompiler='C:/Program Files/Microsoft Visual Studio/2022/Community/VC/Tools/MSVC/14.38.33130'
$guardRestoreSdk='C:/Program Files (x86)/Windows Kits/10'
$guardRestoreSdkVersion='10.0.19041.0'
$env:INCLUDE="$guardRestoreCompiler/include;$guardRestoreSdk/Include/$guardRestoreSdkVersion/ucrt;$guardRestoreSdk/Include/$guardRestoreSdkVersion/shared;$guardRestoreSdk/Include/$guardRestoreSdkVersion/um"
$env:LIB="$guardRestoreCompiler/lib/x64;$guardRestoreSdk/Lib/$guardRestoreSdkVersion/ucrt/x64;$guardRestoreSdk/Lib/$guardRestoreSdkVersion/um/x64"
$guardRestoreSource=Join-Path $PSScriptRoot $SourceVariant
$guardRestoreTests=Join-Path $PSScriptRoot 'tests'
$guardRestoreSuite=if([System.IO.Path]::IsPathRooted($Suite)){$Suite}else{Join-Path $guardRestoreTests $Suite}
Push-Location -LiteralPath $guardRestoreOutput
try{
 $guardRestoreBuild=@(& "$guardRestoreCompiler/bin/Hostx64/x64/cl.exe" /nologo /EHsc /std:c++17 /W4 /WX /utf-8 "/I$guardRestoreSource" "/I$guardRestoreTests" (Join-Path $guardRestoreSource 'DungeonStoneGuard.cpp') $guardRestoreSuite '/Fe:stone-guard-restore.exe' 2>&1)
 $guardRestoreBuildExit=$LASTEXITCODE;$guardRestoreBuild+="BUILD_EXIT_CODE=$guardRestoreBuildExit"
 $guardRestoreBuild | Set-Content -LiteralPath 'build.log' -Encoding utf8
 $guardRestoreBuild | ForEach-Object {Write-Output $_}
 if($guardRestoreBuildExit -ne 0){exit $guardRestoreBuildExit}
 $guardRestoreRun=@(& '.\stone-guard-restore.exe' 2>&1);$guardRestoreRunExit=$LASTEXITCODE
 $guardRestoreRun+="RUN_EXIT_CODE=$guardRestoreRunExit";$guardRestoreRun | Set-Content -LiteralPath 'run.log' -Encoding utf8
 $guardRestoreRun | ForEach-Object {Write-Output $_};exit $guardRestoreRunExit
}finally{Pop-Location}
