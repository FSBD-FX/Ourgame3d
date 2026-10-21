param(
 [string]$EngineRoot='G:\UE_5.5',
 [Parameter(Mandatory=$true)][ValidatePattern('^[A-Za-z0-9_-]+$')][string]$Version,
 [Parameter(Mandatory=$true)][string]$Snapshot,
 [switch]$ValidateOnly
)
$ErrorActionPreference='Stop';$workspace='F:\Ourgame'
$snapshotDirectory=if([IO.Path]::IsPathRooted($Snapshot)){[IO.Path]::GetFullPath($Snapshot)}else{[IO.Path]::GetFullPath((Join-Path $workspace $Snapshot))}
$manifestPath=Join-Path $snapshotDirectory 'compiled-source-manifest.json'
$manifest=Get-Content -LiteralPath $manifestPath -Raw -Encoding UTF8|ConvertFrom-Json
foreach($row in $manifest.files){$p=Join-Path $workspace $row.path;if((Get-Item -LiteralPath $p).Length -ne $row.bytes -or (Get-FileHash -LiteralPath $p -Algorithm SHA256).Hash.ToLowerInvariant() -cne $row.sha256){throw "Compiled input mismatch: $p"}}
$paths=@($manifest.files|ForEach-Object {$_.path.Replace('\','/')})
foreach($required in @('UnrealGame/Source/CodexDungeon/DungeonGuardRoomFlowProbe.cpp','UnrealGame/Source/CodexDungeon/DungeonGuardRoomFlowProbe.h','UnrealGame/Source/CodexDungeon/DungeonHUD.cpp')){if($required -cnotin $paths){throw "Actual compiled manifest omits admitted proof source: $required"}}
if(-not @($paths|Where-Object {$_ -match '/Binaries/Win64/UnrealEditor-CodexDungeon\.dll$'}).Count){throw 'Actual compiled DLL pin missing.'}
if($manifest.strict_registered_tests -le 0 -or $manifest.production_files -le 0){throw 'Actual full registry/resource record missing.'}
foreach($record in @($manifest.full_suite,$manifest.current_build)){$p=Join-Path $workspace $record.path;if((Get-Item -LiteralPath $p).Length -ne $record.bytes -or (Get-FileHash -LiteralPath $p -Algorithm SHA256).Hash.ToLowerInvariant() -cne $record.sha256){throw 'Actual full-suite/build receipt differs.'}}
$suite=Get-Content -LiteralPath (Join-Path $workspace $manifest.full_suite.path) -Raw -Encoding UTF8|ConvertFrom-Json
$build=Get-Content -LiteralPath (Join-Path $workspace $manifest.current_build.path) -Raw -Encoding UTF8|ConvertFrom-Json
if($suite.succeeded -ne $manifest.strict_registered_tests -or $suite.failed -ne 0 -or $suite.succeededWithWarnings -ne 0 -or $suite.notRun -ne 0 -or $suite.inProcess -ne 0 -or $build.ExitCode -ne 0){throw 'Real compiled build/full registry is not strict GREEN.'}
foreach($folder in @('UnrealGame/Source','UnrealGame/Content/Production')){
 $expected=@($paths|Where-Object {$_.StartsWith($folder+'/')}|Sort-Object)
 $actual=@(Get-ChildItem -LiteralPath (Join-Path $workspace $folder) -Recurse -File|ForEach-Object {$_.FullName.Substring($workspace.Length+1).Replace('\','/')}|Sort-Object)
 if(Compare-Object -ReferenceObject $expected -DifferenceObject $actual -CaseSensitive){throw "Actual file set differs from compiled manifest: $folder"}
 if($folder -eq 'UnrealGame/Content/Production' -and $actual.Count -ne $manifest.production_files){throw 'Actual Production count differs from manifest.'}
}
if($ValidateOnly){[ordered]@{compiled_inputs_verified=$true;registry=$manifest.strict_registered_tests;production=$manifest.production_files;UE_started=$false}|ConvertTo-Json;return}
if(@(Get-Process -Name 'UnrealEditor*','UnrealBuildTool' -ErrorAction SilentlyContinue).Count){throw 'Sequential native proof requires no live UE/UBT.'}
$archive=Join-Path $workspace ('过程图稿与视频\'+(Get-Date -Format 'yyyy-MM-dd')+'_石廊三敌原生流程诊断_'+$Version)
if(Test-Path -LiteralPath $archive){throw 'Preserve prior proof; use a new version.'}
$original=Join-Path $archive '原件';[IO.Directory]::CreateDirectory($original)|Out-Null;[IO.Directory]::CreateDirectory((Join-Path $archive '展示副本'))|Out-Null
$indexPath=Join-Path $archive 'index.json';$index=[ordered]@{schema='guard-room-native-flow-session-v001';status='capture_started';snapshot=$Snapshot;manifest_sha256=(Get-FileHash -LiteralPath $manifestPath -Algorithm SHA256).Hash.ToLowerInvariant();process_id=$null;exit_code=$null;native_reported_passed=$null;independent_passed=$false;normal_J_full_clear=$false;diagnostic_public_damage_expected=$true;audio_recorded=$false;E_before_view=$true}
$index|ConvertTo-Json -Depth 8|Set-Content -LiteralPath $indexPath -Encoding utf8
$art=@('-DungeonCandidateSprites','-DungeonFairytaleSwordBodyPreview','-DungeonFairytaleSwordBodyV002Preview','-DungeonFairytaleSwordArmorPrimary1Preview','-DungeonFairytaleSwordPrimary2Preview','-DungeonFairytaleSwordPrimary2BodyPreview','-DungeonFairytaleSwordPrimary2ArmorPreview','-DungeonFairytaleSwordPrimary3ArmorPreview','-DungeonFairytaleLeatherReadyPreview','-DungeonFairytaleLeatherPrimary1Preview','-DungeonFairytaleLeatherPrimary2Preview','-DungeonFairytaleLeatherPrimary3Preview','-DungeonFairytaleSwordEquipmentBoundPreview','-DungeonFairytaleSwordWalkPreview')
$arguments=@(('"{0}"' -f (Join-Path $workspace 'UnrealGame\CodexDungeon.uproject')),'/Game/Maps/FirstRoom?DungeonFirstBatchGuardRoom','-game','-windowed','-ResX=1280','-ResY=720','-NoSplash','-NoLiveCoding','-nop4','-unattended','-DungeonGuardRoomFlowProof','-DungeonContentProof','-DungeonFastLosslessCapture','-DungeonAsyncLosslessCapture',('-DungeonContentProofDir="{0}"' -f $original),'-ExecCmds="t.MaxFPS 30,r.ScreenshotDelegate 1"',('-abslog="{0}"' -f (Join-Path $archive 'runtime.log')))+$art
try{
 $process=Start-Process -FilePath (Join-Path $EngineRoot 'Engine\Binaries\Win64\UnrealEditor.exe') -ArgumentList $arguments -WindowStyle Hidden -PassThru;$index.process_id=$process.Id
 Write-Output "Normal room native diagnostic PID $($process.Id), archive $archive"
 if(-not $process.WaitForExit(180000)){Stop-Process -Id $process.Id -Force;throw 'Native diagnostic timeout; failed originals preserved.'}
 $process.Refresh();$index.exit_code=$process.ExitCode;$reportPath=Join-Path $original 'runtime-report.json'
 if(-not(Test-Path -LiteralPath $reportPath)){throw 'Actual native report missing.'}
 $report=Get-Content -LiteralPath $reportPath -Raw -Encoding UTF8|ConvertFrom-Json;$index.native_reported_passed=$report.passed
 if($process.ExitCode -ne 0 -or -not $report.passed){$index.status='actual_native_RED_preserved';throw ('Actual native flow RED: '+$report.failure)}
 & (Join-Path $workspace 'tools/runtime/asset-gen/Scripts/python.exe') -B -X utf8 (Join-Path $PSScriptRoot 'verify-guard-room-native-flow-v001.py') --archive $archive --write-receipt
 if($LASTEXITCODE -ne 0){throw 'Independent native CRC/warning/coin/RootV2 audit failed.'};$index.independent_passed=$true
 foreach($row in $manifest.files){$p=Join-Path $workspace $row.path;if((Get-Item -LiteralPath $p).Length -ne $row.bytes -or (Get-FileHash -LiteralPath $p -Algorithm SHA256).Hash.ToLowerInvariant() -cne $row.sha256){throw "Proof changed compiled input: $p"}}
 $index.status='native_flow_diagnostic_passed_visual_review_pending'
}catch{
 if($index.status -ne 'actual_native_RED_preserved'){$index.status='failed_preserved'};$index['failure']=$_.Exception.Message;$index|ConvertTo-Json -Depth 8|Set-Content -LiteralPath $indexPath -Encoding utf8;throw
}
$index|ConvertTo-Json -Depth 8|Set-Content -LiteralPath $indexPath -Encoding utf8;Write-Output $archive
