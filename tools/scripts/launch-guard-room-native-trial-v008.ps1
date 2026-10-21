param([string]$EngineRoot='G:\UE_5.5',[string]$Snapshot='',[string]$RootCheckpoint='source-assets/production/fairytale-guard-v001/root-Hurt1286-checkpoint-v002/manual-input-v001.json',[switch]$LightArtTrial,[switch]$GuardFullArt,[switch]$ValidateOnly)
$ErrorActionPreference='Stop'
# Explicitly forward the default too: PSBoundParameters omits values supplied by param defaults.
$PSBoundParameters['RootCheckpoint']=$RootCheckpoint
$launcher='F:\Ourgame\source-assets\production\fairytale-guard-v001\current-Hurt1286-checkpoint-tooling-candidate-v001\tooling\launch-guard-room-native-trial-v007.ps1'
& $launcher @PSBoundParameters
if($LASTEXITCODE -ne 0){exit $LASTEXITCODE}
