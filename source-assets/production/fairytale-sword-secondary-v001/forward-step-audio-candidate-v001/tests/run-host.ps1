param([ValidateSet('RED','GREEN')][string]$Phase='GREEN')
$ErrorActionPreference='Stop';$candidate=Split-Path -Parent $PSScriptRoot
$compilerRoot='C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Tools\MSVC\14.38.33130';$sdkRoot='C:\Program Files (x86)\Windows Kits\10';$sdkVersion='10.0.19041.0'
$out=Join-Path $candidate ('reports/host-'+$Phase+'-'+(Get-Date -Format 'yyyyMMdd-HHmmss-fff'));New-Item -ItemType Directory -Path $out | Out-Null
$priorInclude=$env:INCLUDE;$priorLib=$env:LIB
try{
 $env:INCLUDE="$compilerRoot\include;$sdkRoot\Include\$sdkVersion\ucrt;$sdkRoot\Include\$sdkVersion\shared;$sdkRoot\Include\$sdkVersion\um";$env:LIB="$compilerRoot\lib\x64;$sdkRoot\Lib\$sdkVersion\ucrt\x64;$sdkRoot\Lib\$sdkVersion\um\x64"
 & "$compilerRoot\bin\Hostx64\x64\cl.exe" /nologo /EHsc /std:c++17 /utf-8 /W4 /WX ('/I'+(Join-Path $candidate 'projected')) ('/I'+$PSScriptRoot) ('/I'+(Join-Path $candidate 'before')) (Join-Path $PSScriptRoot 'forward-step-host.cpp') ('/Fe:'+(Join-Path $out 'tests.exe')) ('/Fo:'+(Join-Path $out 'tests.obj')) 2>&1 | Tee-Object -FilePath (Join-Path $out 'compile.log');if($LASTEXITCODE -ne 0){throw 'Host compilation failed'}
 & (Join-Path $out 'tests.exe') 2>&1 | Tee-Object -FilePath (Join-Path $out 'results.log');$result=$LASTEXITCODE;"PHASE=$Phase EXIT=$result HOST_SHIM_ONLY=true UE_RUN=false OUTPUT=$out" | Tee-Object -FilePath (Join-Path $out 'receipt.txt')
}finally{$env:INCLUDE=$priorInclude;$env:LIB=$priorLib};exit $result
