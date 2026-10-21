param([string]$Version='original-EHoff-compile-boundary-v001',[string]$SourceVersion='original-v001',[ValidateSet('On','Off')][string]$Exceptions='Off',[switch]$UnrealSTLPolicy)
$ErrorActionPreference='Stop'
$allocationRoot=$PSScriptRoot
$allocationOutput=Join-Path (Join-Path $allocationRoot 'runs') $Version
if(Test-Path -LiteralPath $allocationOutput){throw 'Refusing to overwrite prior run'}
New-Item -ItemType Directory -Path $allocationOutput | Out-Null
$allocationCompilerRoot='C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Tools\MSVC\14.38.33130'
$allocationSdkRoot='C:\Program Files (x86)\Windows Kits\10'
$allocationSdkVersion='10.0.19041.0'
$env:INCLUDE="$allocationCompilerRoot\include;$allocationSdkRoot\Include\$allocationSdkVersion\ucrt;$allocationSdkRoot\Include\$allocationSdkVersion\shared;$allocationSdkRoot\Include\$allocationSdkVersion\um"
$env:LIB="$allocationCompilerRoot\lib\x64;$allocationSdkRoot\Lib\$allocationSdkVersion\ucrt\x64;$allocationSdkRoot\Lib\$allocationSdkVersion\um\x64"
$allocationSource=Join-Path $allocationRoot $SourceVersion
$allocationTests=Join-Path (Split-Path -Parent $allocationRoot) 'tests/RoomCoinAllocationStandalone.cpp'
$allocationEH=if($Exceptions -eq 'On'){'/EHsc'}else{'/EHs-c-'}
$allocationPolicyFlags=if($UnrealSTLPolicy){@('/D_HAS_EXCEPTIONS=0','/DPLATFORM_EXCEPTIONS_DISABLED=1')}else{@()}
Push-Location -LiteralPath $allocationOutput
try {
 "EXCEPTIONS=$Exceptions FLAG=$allocationEH UNREAL_STL_POLICY=$UnrealSTLPolicy DEFINES=$allocationPolicyFlags" | Set-Content -LiteralPath 'invocation.log' -Encoding utf8
 $allocationBuild=@(& "$allocationCompilerRoot\bin\Hostx64\x64\cl.exe" /nologo $allocationEH @allocationPolicyFlags /std:c++17 /W4 /WX /utf-8 "/I$allocationSource" (Join-Path $allocationSource 'DungeonRoomCoinAllocation.cpp') $allocationTests '/Fe:room-coins.exe' 2>&1)
 $allocationBuildExit=$LASTEXITCODE
 $allocationBuild+="BUILD_EXIT_CODE=$allocationBuildExit"
 $allocationBuild | Set-Content -LiteralPath 'build.log' -Encoding utf8
 $allocationBuild | ForEach-Object {Write-Output $_}
 if($allocationBuildExit -ne 0){exit $allocationBuildExit}
 $allocationRun=@(& '.\room-coins.exe' 2>&1)
 $allocationRunExit=$LASTEXITCODE
 $allocationRun+="RUN_EXIT_CODE=$allocationRunExit"
 $allocationRun | Set-Content -LiteralPath 'run.log' -Encoding utf8
 $allocationRun | ForEach-Object {Write-Output $_}
 exit $allocationRunExit
} finally {Pop-Location}
