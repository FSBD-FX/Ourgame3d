param([string]$EngineRoot = 'G:\UE_5.5', [switch]$FirstUnitPreview, [switch]$ManualWeaponPreview, [switch]$SceneExplorationPreview, [switch]$FairytaleLookdevPreview, [switch]$FairytaleWalkLookdevPreview, [switch]$FairytaleChestLookdevPreview, [switch]$FairytaleShoulderLookdevPreview, [switch]$FairytaleLimbLookdevPreview, [switch]$FairytaleSwordBodyPreview)
$ErrorActionPreference = 'Stop'
if(([int][bool]$FirstUnitPreview+[int][bool]$ManualWeaponPreview+[int][bool]$SceneExplorationPreview+[int][bool]$FairytaleLookdevPreview+[int][bool]$FairytaleWalkLookdevPreview+[int][bool]$FairytaleChestLookdevPreview+[int][bool]$FairytaleShoulderLookdevPreview+[int][bool]$FairytaleLimbLookdevPreview+[int][bool]$FairytaleSwordBodyPreview) -gt 1){throw 'Choose one development preview mode.'}
$workspace = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\..'))
$project = Join-Path $workspace 'UnrealGame\CodexDungeon.uproject'
$map = Join-Path $workspace 'UnrealGame\Content\Maps\FirstRoom.umap'
if (-not (Test-Path -LiteralPath $map)) { throw 'FirstRoom map is missing. Run the preparation script after building.' }
$editor = Join-Path $EngineRoot 'Engine\Binaries\Win64\UnrealEditor.exe'
$log = Join-Path $workspace ('UnrealGame\Saved\Bootstrap\play-{0}.log' -f (Get-Date -Format 'yyyyMMdd-HHmmss'))
$arguments = @(('"{0}"' -f $project), '/Game/Maps/FirstRoom', '-game', '-windowed', '-ResX=1280', '-ResY=720', '-NoSplash', '-NoLiveCoding', '-nop4', ('-abslog="{0}"' -f $log))
if($FirstUnitPreview){$arguments+=@('-DungeonCandidateSprites','-DungeonStoneKnightPreview')}
if($ManualWeaponPreview){$arguments+=@('-DungeonCandidateSprites','-DungeonWeaponBodyPreview','-DungeonXBWPrimaryBodyPreview','-DungeonXBWReloadBodyPreview','-DungeonManualWeaponPreview')}
if($SceneExplorationPreview){$arguments+=@('-DungeonCandidateSprites','-DungeonStoneKnightPreview','-DungeonSceneExplorationPreview')}
if($FairytaleLookdevPreview){$arguments+='-DungeonFairytaleLookdevPreview'}
if($FairytaleWalkLookdevPreview){$arguments+=@('-DungeonFairytaleLookdevPreview','-DungeonFairytaleWalkLookdev')}
if($FairytaleChestLookdevPreview){$arguments+=@('-DungeonFairytaleLookdevPreview','-DungeonFairytaleChestLookdev')}
if($FairytaleShoulderLookdevPreview){$arguments+=@('-DungeonFairytaleLookdevPreview','-DungeonFairytaleChestLookdev','-DungeonFairytaleShoulderLookdev')}
if($FairytaleLimbLookdevPreview){$arguments+=@('-DungeonFairytaleLookdevPreview','-DungeonFairytaleChestLookdev','-DungeonFairytaleShoulderLookdev','-DungeonFairytaleLimbLookdev')}
if($FairytaleSwordBodyPreview){
    & (Join-Path $workspace 'tools/runtime/asset-gen/Scripts/python.exe') -B -X utf8 (Join-Path $PSScriptRoot 'verify-fairytale-sword-body.py') --preflight-only
    if($LASTEXITCODE -ne 0){throw 'Import/pinned body trial preflight failed.'}
    $arguments+=@('-DungeonCandidateSprites','-DungeonSceneExplorationPreview','-DungeonFairytaleSwordBodyPreview')
}
$process = Start-Process -FilePath $editor -ArgumentList $arguments -WindowStyle Normal -PassThru
Write-Output "First playable room started: PID $($process.Id)"
if($FairytaleLookdevPreview){Write-Output 'A/D changes observation direction. Independent idle art trial: combat and movement are disabled. Close the window to exit.'}
if($FairytaleLimbLookdevPreview){Write-Output 'A/D turns; fixed chest and both shoulders. Hold L for both near limbs; L+B bracer only, L+G shin only; W dark background. Fixed72px four-frame idle; frozen gameplay/audio. Close window to exit.'}
elseif($FairytaleShoulderLookdevPreview){Write-Output 'A/D turns; chest stays visible. Hold C for both shoulders; C+N near only, C+F far only. W selects dark background. Original72px four-frame idle; frozen observation, gameplay/audio disabled.'}
elseif($FairytaleChestLookdevPreview){Write-Output 'A/D turns; hold C to show isolated chest; hold W to compare the dark-edge anchor. Fixed72px hero, original four-frame idle; gameplay and audio disabled. Close the window to exit.'}
elseif($FairytaleWalkLookdevPreview){Write-Output 'A/D changes observation direction. Six-frame source walk at fixed72px maximum height; fixed observation position, gameplay and audio disabled. Close the window to exit.'}
else{Write-Output 'WASD/arrows move, Space jump, J/left mouse attack, E interact, Q weapon, R restart.'}
Write-Output "Log: $log"
if($FirstUnitPreview){Write-Output 'Candidate animation development encounter: sword and one real stone knight. No formal armor acquisition, save or full-unit acceptance.'}
if($ManualWeaponPreview){Write-Output 'Manual development preview: Enter starts; E acquires the nearby QA crossbow in .35s, Q switches, J uses native ground primary, T toggles real four-keypose reload and current Actor hand socket, R creates a fresh preview run. Armor/allstate/full weapon unfinished. Memory-only, no disk continuation.'}
if($SceneExplorationPreview){Write-Output 'Exploration development preview: Enter starts; WASD explores the west alcove, E investigates the board. Clear the knight, then E at the east exit and fresh Enter to continue; Escape cancels. Same Run, memory-only; no formal hidden-room income or disk continuation.'}

if($FairytaleSwordBodyPreview){Write-Output 'Enter starts the real development room. Single J, then wait over 1.1s before J again for this first-stage body trial; A/D faces. Only Ready/grounded first primary use new sword art. Other states show explicit newReady0/noSword placeholders; no new armor art/fullcombo acceptance.'}
