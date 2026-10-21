param([switch]$ValidateOnly)
$ErrorActionPreference='Stop'
$previewRoot='F:/Ourgame'
$previewCM=Join-Path $previewRoot 'source-assets/production/backups/v146-Primary1Bridge258-Residency-303-1439-203GREEN-v002/compiled-source-manifest.json'
if((Get-FileHash -LiteralPath $previewCM -Algorithm SHA256).Hash.ToLowerInvariant() -ne 'e08bf832e82c6af093650b7ebde3fa4fc25b59aa47bfe465bb239f7308292564'){throw 'Development checkpoint changed.'}
$previewManifest=Get-Content -LiteralPath $previewCM -Raw|ConvertFrom-Json
if($previewManifest.source_files -ne 303 -or $previewManifest.production_files -ne 1439 -or $previewManifest.passed -ne 203 -or $previewManifest.failed -ne 0){throw 'Development compiled checkpoint does not match.'}
foreach($previewMember in $previewManifest.files){
 $previewPath=Join-Path $previewRoot $previewMember.path
 $previewItem=Get-Item -LiteralPath $previewPath
 if($previewItem.Length -ne $previewMember.bytes -or (Get-FileHash -LiteralPath $previewPath -Algorithm SHA256).Hash.ToLowerInvariant() -ne $previewMember.sha256){throw ('Development files changed; use the independent stable preview or update this checkpoint: '+$previewMember.path)}
}
foreach($previewSet in @(@{prefix='UnrealGame/Source/';count=303},@{prefix='UnrealGame/Content/Production/';count=1439})){
 $previewExpected=[System.Collections.Generic.HashSet[string]]::new([StringComparer]::Ordinal)
 foreach($previewMember in $previewManifest.files){if($previewMember.path.StartsWith($previewSet.prefix,[StringComparison]::Ordinal)){[void]$previewExpected.Add($previewMember.path)}}
 $previewActual=[System.Collections.Generic.HashSet[string]]::new([StringComparer]::Ordinal)
 foreach($previewFile in Get-ChildItem -LiteralPath (Join-Path $previewRoot $previewSet.prefix) -Recurse -File -Force){[void]$previewActual.Add($previewFile.FullName.Substring($previewRoot.Length+1).Replace('\','/'))}
 if($previewActual.Count -ne $previewSet.count -or -not $previewActual.SetEquals($previewExpected)){throw 'Development directory membership changed.'}
}
$previewArgs=@((Join-Path $previewRoot 'UnrealGame/CodexDungeon.uproject'),'/Game/Maps/FirstRoom?DungeonFirstBatchGuardRoom','-game','-d3d11','-windowed','-ResX=1280','-ResY=720','-NoSplash','-NoLiveCoding','-nop4','-DungeonCandidateSprites','-DungeonFairytaleSwordBodyPreview','-DungeonFairytaleSwordBodyV002Preview','-DungeonFairytaleSwordArmorPrimary1Preview','-DungeonFairytaleSwordPrimary2Preview','-DungeonFairytaleSwordPrimary2BodyPreview','-DungeonFairytaleSwordPrimary2ArmorPreview','-DungeonFairytaleSwordPrimary3ArmorPreview','-DungeonFairytaleLeatherReadyPreview','-DungeonFairytaleLeatherPrimary1Preview','-DungeonFairytaleLeatherPrimary2Preview','-DungeonFairytaleLeatherPrimary3Preview','-DungeonFairytaleSwordEquipmentBoundPreview','-DungeonFairytaleSwordWalkPreview','-DungeonFairytaleSwordHurtPreview','-DungeonFairytaleSwordDeathPreview','-DungeonFairytaleSwordDodgePreview','-DungeonFairytaleSwordAirPreview','-DungeonGuardRoomManualLightSource','-DungeonFairytaleGuardFullPreview','-DungeonFairytaleGuardStompPreview','-DungeonFairytaleGuardMoveRigPreview','-DungeonFairytalePrimary1Bridge258Preview')
if($ValidateOnly){[ordered]@{schema='Root-development-manual-v146-v001';source_files=303;production_files=1439;registered_tests=203;current_compiled_inputs_verified=$true;new_primary1_bridge258=$true;native_land_right_callbacks=186;native_land_left_callbacks=174;native_Ready_combo_callbacks=141;automatic_input=$false;diagnostic_damage=$false;QA_manual_light_source=$true;isolated_staged_package=$false;full_manual_combat_reviewed=$false;full_realtime_playback_reviewed=$false;audio_listened=$false;FinalAccepted=$false;UE_started=$false;arguments=$previewArgs}|ConvertTo-Json -Depth 5;return}
if(Get-Process -Name UnrealEditor,UnrealEditor-Cmd,UnrealBuildTool -ErrorAction SilentlyContinue){throw 'Close UE before starting this development preview.'}
$previewLog=Join-Path $previewRoot ('UnrealGame/Saved/Bootstrap/development-v146-'+(Get-Date -Format 'yyyyMMdd-HHmmss-fffffff')+'.log')
$previewArgs+=('-abslog='+$previewLog)
$previewArgumentLine=($previewArgs|ForEach-Object {'"{0}"' -f $_}) -join ' '
$previewProcess=Start-Process -FilePath 'G:/UE_5.5/Engine/Binaries/Win64/UnrealEditor.exe' -WorkingDirectory (Join-Path $previewRoot 'UnrealGame') -ArgumentList $previewArgumentLine -WindowStyle Normal -PassThru
Write-Output ('Development preview PID '+$previewProcess.Id+'. Enter starts; WASD moves; E equips nearby light armor after .50s; J combo; K skill; Space jump; Shift dodge; R fresh Run.')
Write-Output 'LIMITED WIP: new J0/J1 artwork; K/air attack/pickup presentation and other equipment remain incomplete. QA light source, normal three-enemy room, manual input. No automatic input or diagnostic damage. Stable preview is a separate older snapshot.'
