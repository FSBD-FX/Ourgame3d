param([string]$LogPath='')
$ErrorActionPreference='Stop'
$feedbackCompiler='C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Tools\MSVC\14.38.33130'
$feedbackSdk='C:\Program Files (x86)\Windows Kits\10'
$feedbackOutput=Join-Path $env:TEMP 'OurgameStoneFeedback'
New-Item -ItemType Directory -Force -Path $feedbackOutput | Out-Null
$env:INCLUDE="$feedbackCompiler\include;$feedbackSdk\Include\10.0.19041.0\ucrt;$feedbackSdk\Include\10.0.19041.0\shared;$feedbackSdk\Include\10.0.19041.0\um"
$env:LIB="$feedbackCompiler\lib\x64;$feedbackSdk\Lib\10.0.19041.0\ucrt\x64;$feedbackSdk\Lib\10.0.19041.0\um\x64"
$feedbackLines=@('Transient stone feedback journal; no audio listening, GPU or gameplay acceptance.')
$feedbackLines+=& "$feedbackCompiler\bin\Hostx64\x64\cl.exe" /nologo /EHsc /std:c++17 /W4 /WX /DDUNGEON_STONE_FEEDBACK_STANDALONE (Join-Path $PSScriptRoot 'DungeonStoneFeedbackStandalone.cpp') "/Fe:$feedbackOutput\feedback.exe" "/Fo:$feedbackOutput\feedback.obj" 2>&1
$feedbackExit=$LASTEXITCODE
if($feedbackExit -eq 0){$feedbackLines+=& "$feedbackOutput\feedback.exe" 2>&1;$feedbackExit=$LASTEXITCODE}
$feedbackLines+="EXIT_CODE=$feedbackExit"
if($LogPath){New-Item -ItemType Directory -Force -Path (Split-Path -Parent $LogPath) | Out-Null;$feedbackLines | Set-Content -LiteralPath $LogPath -Encoding utf8}
$feedbackLines | ForEach-Object { Write-Output $_ }
exit $feedbackExit
