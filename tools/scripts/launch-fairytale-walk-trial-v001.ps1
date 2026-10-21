param([string]$EngineRoot='G:\UE_5.5',[switch]$ValidateOnly)
$ErrorActionPreference='Stop'
$workspace='F:\Ourgame'
$manifestPath=Join-Path $workspace 'source-assets\production\backups\v127-walk-169G\compiled-source-manifest.json'
if((Get-FileHash -LiteralPath $manifestPath -Algorithm SHA256).Hash.ToLowerInvariant() -cne 'f8001a80b885a5a59466e66355cfd86ba482bfee679ddd1dcc691aa3c8ff0242'){throw 'The retained v127 manifest changed.'}
$manifest=Get-Content -LiteralPath $manifestPath -Raw|ConvertFrom-Json
if($manifest.strict_registered_tests -ne 169 -or $manifest.production_files -ne 1199){throw 'Current compiled suite/resource contract missing.'}
foreach($row in $manifest.files){
 $path=Join-Path $workspace $row.path
 if((Get-Item -LiteralPath $path).Length -ne $row.bytes -or (Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant() -cne $row.sha256){throw "Current compiled input differs: $($row.path)"}
}
$proofPath=Join-Path $workspace '过程图稿与视频\2026-10-18_棕皮军剑双向行走与三连斩实录_v001\原件\independent-walk-proof-verification-v001.json'
if((Get-FileHash -LiteralPath $proofPath -Algorithm SHA256).Hash.ToLowerInvariant() -cne '446e642f54c72a6a75206cb7f6072ebda4a42f2160708b21231942dab3a9b4b5'){throw 'Retained actual native proof receipt differs.'}
$proof=Get-Content -LiteralPath $proofPath -Raw|ConvertFrom-Json
if(-not $proof.passed -or -not $proof.same_actual_LGT_SWD -or $proof.masks_left_right[0] -ne 63 -or $proof.masks_left_right[1] -ne 63 -or $proof.actual_primary_phase_facing_pairs -ne 36 -or -not $proof.pixel_verification.every_source_viewport_pixel_crc_matches){throw 'Native moving/three-stage/instance/pixel proof missing.'}
if($ValidateOnly){[ordered]@{current_build_verified=$true;full_suite=169;production=1199;native_Walk_phases_both_sides=12;native_primary_phase_pairs=36;UE_started=$false}|ConvertTo-Json;return}
if(@(Get-Process -Name 'UnrealEditor*','UnrealBuildTool' -ErrorAction SilentlyContinue).Count){throw 'Close the current Unreal session before opening the interactive trial.'}
$log=Join-Path $workspace ('UnrealGame\Saved\Bootstrap\play-walk-v127-{0}.log' -f (Get-Date -Format 'yyyyMMdd-HHmmss-fff'))
$arguments=@(('"{0}"' -f (Join-Path $workspace 'UnrealGame\CodexDungeon.uproject')),'/Game/Maps/FirstRoom','-game','-windowed','-ResX=1280','-ResY=720','-NoSplash','-NoLiveCoding','-nop4',
 '-DungeonSceneExplorationPreview','-DungeonCandidateSprites','-DungeonFairytaleSwordBodyPreview','-DungeonFairytaleSwordBodyV002Preview','-DungeonFairytaleSwordArmorPrimary1Preview','-DungeonFairytaleSwordPrimary2Preview','-DungeonFairytaleSwordPrimary2BodyPreview','-DungeonFairytaleSwordPrimary2ArmorPreview','-DungeonFairytaleSwordPrimary3ArmorPreview',
 '-DungeonFairytaleLeatherReadyPreview','-DungeonFairytaleLeatherPrimary1Preview','-DungeonFairytaleLeatherPrimary2Preview','-DungeonFairytaleLeatherPrimary3Preview','-DungeonFairytaleSwordEquipmentBoundPreview','-DungeonFairytaleSwordWalkPreview',('-abslog="{0}"' -f $log))
$process=Start-Process -FilePath (Join-Path $EngineRoot 'Engine\Binaries\Win64\UnrealEditor.exe') -ArgumentList $arguments -WindowStyle Normal -PassThru
Write-Output "Walk trial PID $($process.Id). Enter starts, WASD moves, E picks up equipment, J attacks."
Write-Output 'Trial: matching Ready/Walk/three-stage sword with committed light armor. Other states, enemy art/audio and full content remain in production.'
Write-Output "Log: $log"
