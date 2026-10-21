param([string]$EngineRoot='G:\UE_5.5',[string]$Snapshot='',[string]$RootCheckpoint='F:/Ourgame/source-assets/production/fairytale-hero-state-gap-v001/death-state-preparation-v001/root-Death1326-checkpoint-v001/manual-input-v001.json',[switch]$LightArtTrial,[switch]$GuardFullArt,[switch]$ValidateOnly)
$ErrorActionPreference='Stop'
$PSBoundParameters['RootCheckpoint']=$RootCheckpoint
$launcher='F:/Ourgame/source-assets/production/fairytale-hero-state-gap-v001/death-state-preparation-v001/Death40-manual-checkpoint-tooling-candidate-v001/launch-guard-room-native-trial-v009.ps1'
& $launcher @PSBoundParameters
if($LASTEXITCODE -ne 0){exit $LASTEXITCODE}
