param([string]$EngineRoot='G:\UE_5.5',[string]$Snapshot='',[string]$RootCheckpoint='F:/Ourgame/source-assets/production/fairytale-guard-v001/root-Stomp1332-checkpoint-v001/manual-input-v001.json',[switch]$LightArtTrial,[switch]$GuardFullArt,[switch]$ValidateOnly)
$ErrorActionPreference='Stop'
$PSBoundParameters['RootCheckpoint']=$RootCheckpoint
$launcher='F:/Ourgame/source-assets/production/fairytale-guard-v001/Stomp50-manual-checkpoint-candidate-v001/launch-guard-room-native-trial-v010.ps1'
& $launcher @PSBoundParameters
if($LASTEXITCODE -ne 0){exit $LASTEXITCODE}
