$ErrorActionPreference='Stop'
$locAudioRoot='F:/Ourgame'
$locAudioStage=Join-Path $locAudioRoot 'docs/production/first-batch-v2/evidence/HeroLocomotionAudio-v145-v001/Root-staged-UE-import-v001'
if(Get-Process -Name UnrealEditor,UnrealEditor-Cmd,UnrealBuildTool -ErrorAction SilentlyContinue){throw 'Exclusive UE import requires no other UE or UBT process.'}
function Get-LocAudioPin([string]$Path){$locAudioItem=Get-Item -LiteralPath $Path;return @{path=$locAudioItem.FullName.Replace('\','/');bytes=$locAudioItem.Length;sha256=(Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()}}
function Write-LocAudioNewJson([string]$Path,[object]$Value){$locAudioStream=[IO.FileStream]::new($Path,[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::Read);try{$locAudioBytes=[Text.UTF8Encoding]::new($false).GetBytes(($Value|ConvertTo-Json -Depth 20));$locAudioStream.Write($locAudioBytes,0,$locAudioBytes.Length);$locAudioStream.Flush($true)}finally{$locAudioStream.Dispose()}}
$locAudioBuildPath=Join-Path $locAudioRoot 'UnrealGame/Saved/Bootstrap/last-build.json'
$locAudioBuild=Get-Content -LiteralPath $locAudioBuildPath -Raw|ConvertFrom-Json
if($locAudioBuild.ExitCode -ne 0){throw 'Current actual successful build required.'}
if(Select-String -LiteralPath $locAudioBuild.Log -Pattern 'Expected DungeonHeroLocomotionAudioNativeV001.h to be first header included.' -Quiet){throw 'First-header diagnostic must be repaired and rebuilt before import.'}
$locAudioStageReceipt=Get-Content -LiteralPath (Join-Path $locAudioStage 'staging-receipt.json') -Raw|ConvertFrom-Json
foreach($locAudioRow in $locAudioStageReceipt.copies){$locAudioPin=Get-LocAudioPin $locAudioRow.copy;if($locAudioPin.bytes -ne $locAudioRow.bytes -or $locAudioPin.sha256 -cne $locAudioRow.sha256){throw 'Exact importer staging changed.'}}
$locAudioScript=Join-Path $locAudioStage 'import/ue-import-hero-locomotion-v001.py'
$locAudioLog=Join-Path $locAudioStage 'native-UE-import-v001.log'
$locAudioLaunch=Join-Path $locAudioStage 'launch-receipt-v001.json'
$locAudioExit=Join-Path $locAudioStage 'exit-receipt-v001.json'
if((Test-Path -LiteralPath $locAudioLog) -or (Test-Path -LiteralPath $locAudioLaunch) -or (Test-Path -LiteralPath $locAudioExit)){throw 'Preserve previous import attempt; no overwrite or automatic retry.'}
$locAudioExe='G:/UE_5.5/Engine/Binaries/Win64/UnrealEditor-Cmd.exe'
$locAudioArgs=@((Join-Path $locAudioRoot 'UnrealGame/CodexDungeon.uproject'),'-unattended','-nosplash','-nop4','-NoLiveCoding','-run=pythonscript',('-script='+$locAudioScript),('-abslog='+$locAudioLog))
$locAudioArgLine=($locAudioArgs|ForEach-Object {'"{0}"' -f $_}) -join ' '
$locAudioDLL=Join-Path $locAudioRoot 'UnrealGame/Binaries/Win64/UnrealEditor-CodexDungeon.dll'
$locAudioDLLBefore=Get-LocAudioPin $locAudioDLL
$locAudioProcess=Start-Process -FilePath $locAudioExe -ArgumentList $locAudioArgLine -WindowStyle Hidden -WorkingDirectory (Join-Path $locAudioRoot 'UnrealGame') -PassThru
Write-LocAudioNewJson $locAudioLaunch @{schema='Root-hero-locomotion-UE-import-launch-v001';process_id=$locAudioProcess.Id;started_utc=$locAudioProcess.StartTime.ToUniversalTime().ToString('O');arguments=$locAudioArgs;engine=(Get-LocAudioPin $locAudioExe);game_dll=$locAudioDLLBefore;successful_build=(Get-LocAudioPin $locAudioBuildPath);importer=(Get-LocAudioPin $locAudioScript);source_admission=(Get-LocAudioPin (Join-Path $locAudioRoot 'docs/production/first-batch-v2/evidence/HeroLocomotionAudio-v145-v001/Root-source-admission-v001/actual-source-admission.json'));source_repair=(Get-LocAudioPin (Join-Path $locAudioRoot 'docs/production/first-batch-v2/evidence/HeroLocomotionAudio-v145-v001/Root-own-first-header-repair-v001/actual-source-repair-admission.json'));actual_recorded=$true;FinalAccepted=$false}
Write-Output ('Six-cue native UE import PID '+$locAudioProcess.Id)
$locAudioProcess.WaitForExit()
$locAudioDLLAfter=Get-LocAudioPin $locAudioDLL
Write-LocAudioNewJson $locAudioExit @{schema='Root-hero-locomotion-UE-import-exit-v001';process_id=$locAudioProcess.Id;exit_code=$locAudioProcess.ExitCode;exited_utc=$locAudioProcess.ExitTime.ToUniversalTime().ToString('O');os_exit_confirmed=$true;game_dll_after=$locAudioDLLAfter;launch=(Get-LocAudioPin $locAudioLaunch);actual_recorded=$true;FinalAccepted=$false}
if($locAudioProcess.ExitCode -ne 0){throw 'Actual UE import failed; preserve logs, receipts and any partial packages.'}
if($locAudioDLLBefore.sha256 -cne $locAudioDLLAfter.sha256){throw 'Actual DLL changed during import.'}
$locAudioReports=@(Get-ChildItem -LiteralPath (Join-Path $locAudioStage 'reports') -File -Filter 'ue-import-*.json')
if($locAudioReports.Count -ne 1){throw 'One actual import receipt required.'}
$locAudioReceipt=Get-Content -LiteralPath $locAudioReports[0].FullName -Raw|ConvertFrom-Json
if($locAudioReceipt.success -ne $true -or $locAudioReceipt.actual_imported -ne 6 -or $locAudioReceipt.actual_saved -ne 6){throw 'Actual six imports and saves not complete; preserve partial outcome.'}
Write-Output ('Actual six SoundWave imports/saves passed: '+$locAudioReports[0].FullName)
