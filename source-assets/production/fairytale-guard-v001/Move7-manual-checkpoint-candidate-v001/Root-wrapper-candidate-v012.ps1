param([string]$EngineRoot='G:\UE_5.5',[string]$Snapshot='',[string]$RootCheckpoint='F:/Ourgame/source-assets/production/fairytale-guard-v001/root-Move7-checkpoint-v001/manual-input-v001.json',[switch]$LightArtTrial,[switch]$GuardFullArt,[switch]$ValidateOnly)
$ErrorActionPreference='Stop'
$PSBoundParameters['RootCheckpoint']=$RootCheckpoint
$launcher='F:/Ourgame/source-assets/production/fairytale-guard-v001/Move7-manual-checkpoint-candidate-v001/launch-guard-room-native-trial-v012.ps1'
& $launcher @PSBoundParameters
if($LASTEXITCODE -ne 0){exit $LASTEXITCODE}
