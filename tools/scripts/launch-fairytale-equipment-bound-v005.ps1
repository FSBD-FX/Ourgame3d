param(
 [Parameter(Mandatory=$true)][string]$Snapshot,
 [Parameter(Mandatory=$true)][string]$ProofContract,
 [string]$ProjectRoot='F:\Ourgame',
 [string]$EngineRoot='G:\UE_5.5'
)
$ErrorActionPreference='Stop'
$workspace=[IO.Path]::GetFullPath($ProjectRoot)
$python=Join-Path $workspace 'tools\runtime\asset-gen\Scripts\python.exe'
$verifier=Join-Path $PSScriptRoot 'verify-equipment-bound-current-build-v005.py'
$verified=& $python -B -X utf8 $verifier --project $workspace --snapshot $Snapshot --proof-contract $ProofContract
if($LASTEXITCODE -ne 0){throw 'Current strict checkpoint/native proof preflight failed.'}
$proof=$verified | ConvertFrom-Json
if(-not $proof.preflight_passed){throw 'Verifier did not return a strict pass.'}
$allowed=@('-DungeonCandidateSprites','-DungeonSceneExplorationPreview','-DungeonFairytaleSwordEquipmentBoundPreview','-DungeonFairytaleLeatherReadyPreview','-DungeonFairytaleLeatherPrimary1Preview')
foreach($flag in $proof.launch_flags){if($flag -cnotin $allowed){throw 'Verifier returned an unexpected launch flag.'}}
$log=Join-Path $workspace ('UnrealGame\Saved\Bootstrap\play-equipment-bound-{0}.log' -f (Get-Date -Format 'yyyyMMdd-HHmmss-fff'))
$arguments=@(('"{0}"' -f (Join-Path $workspace 'UnrealGame\CodexDungeon.uproject')),'/Game/Maps/FirstRoom','-game','-windowed','-ResX=1280','-ResY=720','-NoSplash','-NoLiveCoding','-nop4')
$arguments += @($proof.launch_flags)
$arguments += ('-abslog="{0}"' -f $log)
# This script is explicitly interactive. No QA actor/auto input/proof-only flag.
$process=Start-Process -FilePath (Join-Path $EngineRoot 'Engine\Binaries\Win64\UnrealEditor.exe') -ArgumentList $arguments -WindowStyle Normal -PassThru
Write-Output "Equipment-bound preview started: PID $($process.Id)"
Write-Output 'Enter starts. WASD/arrows move. J/left mouse attacks; fresh press near the end queues the next stage. E interacts; Enter confirms slot selection.'
Write-Output 'Actual SWD/light armor only; unsupported states and full audio/motion acceptance remain incomplete. Body max72px; interface hidden.'
Write-Output "Log: $log"
