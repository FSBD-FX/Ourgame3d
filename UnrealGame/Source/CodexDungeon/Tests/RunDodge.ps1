param(
 [ValidateSet('RED','GREEN','VERIFY')][string]$Phase='VERIFY',
 [string]$CompilerRoot='C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Tools\MSVC\14.38.33130',
 [string]$SdkRoot='C:\Program Files (x86)\Windows Kits\10',
 [string]$SdkVersion='10.0.19041.0'
)
$ErrorActionPreference='Stop'
$dodgeOutput=Join-Path $env:TEMP ('OurgameDodge\'+(Get-Date -Format 'yyyyMMdd-HHmmss-fff')+'-'+$Phase)
New-Item -ItemType Directory -Force -Path $dodgeOutput | Out-Null
$dodgeLog=Join-Path $dodgeOutput 'standalone.log'
$dodgePreviousInclude=$env:INCLUDE
$dodgePreviousLib=$env:LIB
try {
 $env:INCLUDE="$CompilerRoot\include;$SdkRoot\Include\$SdkVersion\ucrt;$SdkRoot\Include\$SdkVersion\shared;$SdkRoot\Include\$SdkVersion\um"
 $env:LIB="$CompilerRoot\lib\x64;$SdkRoot\Lib\$SdkVersion\ucrt\x64;$SdkRoot\Lib\$SdkVersion\um\x64"
 "PHASE=$Phase; standalone C++17 dodge kernel; analytic read-only caller sweep; no UE/runtime acceptance." | Tee-Object -FilePath $dodgeLog
 & "$CompilerRoot\bin\Hostx64\x64\cl.exe" /nologo /utf-8 /std:c++17 /EP /P /UDUNGEON_DODGE_STANDALONE (Join-Path $PSScriptRoot 'DungeonDodgeStandalone.cpp') "/Fi:$dodgeOutput\no-standalone-macro.i" 2>&1 | Tee-Object -FilePath $dodgeLog -Append
 if($LASTEXITCODE -ne 0){throw 'Standalone guard preprocessing failed.'}
 if(-not [string]::IsNullOrWhiteSpace((Get-Content -LiteralPath (Join-Path $dodgeOutput 'no-standalone-macro.i') -Raw))){throw 'Test translation unit must be empty without its opt-in macro.'}
 'NO_MACRO_TRANSLATION_UNIT_EMPTY=true' | Tee-Object -FilePath $dodgeLog -Append
 $dodgeHeader=(Join-Path (Split-Path -Parent $PSScriptRoot) 'DungeonDodge.h').Replace('\','/')
 ('#include "'+$dodgeHeader+'"'+[Environment]::NewLine+'static_assert(DungeonDodge::Speed == 462.5, "fixed speed");') | Set-Content -LiteralPath (Join-Path $dodgeOutput 'header-no-exceptions.cpp') -Encoding utf8
 & "$CompilerRoot\bin\Hostx64\x64\cl.exe" /nologo /c /utf-8 /std:c++17 /W4 /WX /EHs-c- /D_HAS_EXCEPTIONS=0 (Join-Path $dodgeOutput 'header-no-exceptions.cpp') "/Fo:$dodgeOutput\header-no-exceptions.obj" 2>&1 | Tee-Object -FilePath $dodgeLog -Append
 if($LASTEXITCODE -ne 0){throw 'Pure header compile without C++ exceptions failed.'}
 'NO_EXCEPTIONS_HEADER_COMPILE=true' | Tee-Object -FilePath $dodgeLog -Append
 & "$CompilerRoot\bin\Hostx64\x64\cl.exe" /nologo /EHsc /utf-8 /std:c++17 /W4 /WX /DDUNGEON_DODGE_STANDALONE (Join-Path $PSScriptRoot 'DungeonDodgeStandalone.cpp') "/Fe:$dodgeOutput\dodge.exe" "/Fo:$dodgeOutput\dodge.obj" 2>&1 | Tee-Object -FilePath $dodgeLog -Append
 $dodgeExit=$LASTEXITCODE
 "COMPILE_EXIT=$dodgeExit" | Tee-Object -FilePath $dodgeLog -Append
 if($dodgeExit -eq 0){& "$dodgeOutput\dodge.exe" 2>&1 | Tee-Object -FilePath $dodgeLog -Append; $dodgeExit=$LASTEXITCODE}
 "EXIT_CODE=$dodgeExit" | Tee-Object -FilePath $dodgeLog -Append
 "LOG_PATH=$dodgeLog"
} finally { $env:INCLUDE=$dodgePreviousInclude; $env:LIB=$dodgePreviousLib }
exit $dodgeExit
