param([string]$EngineRoot='G:\UE_5.5',[Parameter(Mandatory=$true)][string]$Snapshot,[switch]$LightArtTrial,[switch]$ValidateOnly)
$ErrorActionPreference='Stop';$workspace='F:\Ourgame'
& (Join-Path $PSScriptRoot 'capture-guard-room-native-flow-v001.ps1') -Snapshot $Snapshot -Version trial-preflight -ValidateOnly|Out-Null
$snapshotDirectory=if([IO.Path]::IsPathRooted($Snapshot)){[IO.Path]::GetFullPath($Snapshot)}else{[IO.Path]::GetFullPath((Join-Path $workspace $Snapshot))}
$manifest=Get-Content -LiteralPath (Join-Path $snapshotDirectory 'compiled-source-manifest.json') -Raw -Encoding UTF8|ConvertFrom-Json
foreach($row in $manifest.files){$p=Join-Path $workspace $row.path;if((Get-Item -LiteralPath $p).Length -ne $row.bytes -or (Get-FileHash -LiteralPath $p -Algorithm SHA256).Hash.ToLowerInvariant() -cne $row.sha256){throw "Actual compiled input mismatch: $p"}}
if($LightArtTrial -and -not @($manifest.files|Where-Object {$_.path.Replace('\','/') -ceq 'UnrealGame/Source/CodexDungeon/DungeonGuardRoomFlowProbe.cpp'}).Count){throw 'Manual display-source probe not in actual compiled manifest.'}
if($ValidateOnly){[ordered]@{compiled_inputs_verified=$true;manual_light_source=[bool]$LightArtTrial;automatic_inputs=$false;UE_started=$false}|ConvertTo-Json;return}
if(@(Get-Process -Name 'UnrealEditor*','UnrealBuildTool' -ErrorAction SilentlyContinue).Count){throw 'Close UE/UBT before starting the visible native trial.'}
$log=Join-Path $workspace ('UnrealGame\Saved\Bootstrap\guard-room-trial-'+(Get-Date -Format 'yyyyMMdd-HHmmss-fffffff')+'.log')
$arguments=@(('"{0}"' -f (Join-Path $workspace 'UnrealGame\CodexDungeon.uproject')),'/Game/Maps/FirstRoom?DungeonFirstBatchGuardRoom','-game','-windowed','-ResX=1280','-ResY=720','-NoSplash','-NoLiveCoding','-nop4','-DungeonCandidateSprites','-DungeonFairytaleSwordBodyPreview','-DungeonFairytaleSwordBodyV002Preview','-DungeonFairytaleSwordArmorPrimary1Preview','-DungeonFairytaleSwordPrimary2Preview','-DungeonFairytaleSwordPrimary2BodyPreview','-DungeonFairytaleSwordPrimary2ArmorPreview','-DungeonFairytaleSwordPrimary3ArmorPreview','-DungeonFairytaleLeatherReadyPreview','-DungeonFairytaleLeatherPrimary1Preview','-DungeonFairytaleLeatherPrimary2Preview','-DungeonFairytaleLeatherPrimary3Preview','-DungeonFairytaleSwordEquipmentBoundPreview','-DungeonFairytaleSwordWalkPreview',('-abslog="{0}"' -f $log))
if($LightArtTrial){$arguments+='-DungeonGuardRoomManualLightSource'}
$process=Start-Process -FilePath (Join-Path $EngineRoot 'Engine\Binaries\Win64\UnrealEditor.exe') -ArgumentList $arguments -WindowStyle Normal -PassThru
Write-Output "Native room PID $($process.Id). Enter starts, WASD moves, J attacks, Shift dodges, Space jumps, E interacts after all3 enemies, R starts a fresh Run."
if($LightArtTrial){Write-Output 'One explicit display-only LGT source is near entry; after Enter, press E and wait for the actual .50s commit. It is not room loot. No automatic input or diagnostic damage runs.'}
Write-Output "Log $log"
