param([string]$EngineRoot='G:\UE_5.5',[string]$Snapshot='',[string]$RootCheckpoint='F:/Ourgame/source-assets/production/fairytale-hero-air-v001/root-manual-v013/manual-input-v013.json',[switch]$LightArtTrial,[switch]$GuardFullArt,[switch]$ValidateOnly)
$ErrorActionPreference='Stop'
$PSBoundParameters['RootCheckpoint']=$RootCheckpoint
$launcher='F:/Ourgame/source-assets/production/fairytale-hero-air-v001/manual-entry-candidate-v013/launch-guard-room-native-trial-v013.ps1'
& $launcher @PSBoundParameters
if($LASTEXITCODE -ne 0){exit $LASTEXITCODE}
