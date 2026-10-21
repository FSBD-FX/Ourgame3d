param([ValidateSet('left','right')][string]$Side='left')
$ErrorActionPreference='Stop'
$taskRoot='F:/Ourgame'
$media=Join-Path $taskRoot ('过程图稿与视频/2026-10-19_钟盔跳跃旧渲染缺口实录_{0}_v001' -f $Side)
& (Join-Path $taskRoot 'tools/runtime/asset-gen/Scripts/python.exe') -B -X utf8 (Join-Path $taskRoot 'tools/scripts/prepare-hero-Air6-baseline-prereg-v001.py') --side $Side
if($LASTEXITCODE -ne 0){throw 'Native baseline preflight failed'}
$native=Join-Path $media '原件'
$face=if($Side -eq 'left'){'-1'}else{'1'}
$tokens=@('F:/Ourgame/UnrealGame/CodexDungeon.uproject','/Game/Maps/FirstRoom?DungeonFirstBatchGuardRoom','-game','-windowed','-ResX=1280','-ResY=720','-NoSplash','-NoLiveCoding','-nop4','-DungeonCandidateSprites','-DungeonFairytaleSwordEquipmentBoundPreview','-DungeonFairytaleSwordWalkPreview','-DungeonFairytaleSwordHurtPreview','-DungeonFairytaleSwordDeathPreview','-DungeonFairytaleSwordDodgePreview','-DungeonFairytaleGuardFullPreview','-DungeonFairytaleGuardStompPreview','-DungeonFairytaleGuardMoveRigPreview','-DungeonContentProof','-DungeonHeroAirProofV001','-DungeonHeroAirBaselineV001',('-DungeonHeroAirFacing='+$face),'-DungeonHeroAirClearKnightDiagnostic','-DungeonFastLosslessCapture','-DungeonAsyncLosslessCapture',('-DungeonContentProofDir='+$native),('-abslog='+(Join-Path $media 'native-engine.log')))
$arguments=($tokens | ForEach-Object {'"{0}"' -f $_}) -join ' '
$process=Start-Process -FilePath 'G:/UE_5.5/Engine/Binaries/Win64/UnrealEditor.exe' -ArgumentList $arguments -WindowStyle Hidden -PassThru
[pscustomobject]@{Pid=$process.Id;Side=$Side;Arguments=$tokens;FixedTimeStep=$false;HumanInput=$false;DiagnosticOnly=$true;StartedUtc=(Get-Date).ToUniversalTime().ToString('O')} | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath (Join-Path $media 'launch-receipt-v001.json') -Encoding utf8
Write-Output ('Hero Air baseline PID {0}, side {1}' -f $process.Id,$Side)
$process.WaitForExit()
[pscustomobject]@{Pid=$process.Id;ExitCode=$process.ExitCode;FinishedUtc=(Get-Date).ToUniversalTime().ToString('O')} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $media 'exit-receipt-v001.json') -Encoding utf8
Write-Output ('Hero Air baseline exit {0}: {1}' -f $process.ExitCode,$media)
exit $process.ExitCode
