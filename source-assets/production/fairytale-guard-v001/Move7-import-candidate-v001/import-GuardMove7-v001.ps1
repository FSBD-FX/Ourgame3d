param(
 [string]$EngineRoot='G:\UE_5.5',
 [Parameter(Mandatory=$true)][string]$Manifest,
 [string]$RootApproval,
 [switch]$ValidateOnly,
 [switch]$ExecuteImport
)
$ErrorActionPreference='Stop'
$workspace='F:\Ourgame'
$python=Join-Path $workspace 'tools\runtime\asset-gen\Scripts\python.exe'
$script=Join-Path $PSScriptRoot 'ue-import-GuardMove7-v001.py'
$Manifest=if([IO.Path]::IsPathRooted($Manifest)){[IO.Path]::GetFullPath($Manifest)}else{[IO.Path]::GetFullPath((Join-Path $workspace $Manifest))}
$hostArguments=@('-B','-X','utf8',$script,'--manifest',$Manifest,'--validate-only')
if($RootApproval){
 $RootApproval=if([IO.Path]::IsPathRooted($RootApproval)){[IO.Path]::GetFullPath($RootApproval)}else{[IO.Path]::GetFullPath((Join-Path $workspace $RootApproval))}
 $hostArguments+=@('--root-approval',$RootApproval)
}
& $python @hostArguments
if($LASTEXITCODE -ne 0){throw 'Move7 exact sources/old1364/approval preflight failed; no UE launch.'}
if($ValidateOnly -or -not $ExecuteImport){Write-Output 'Move7 source-only validation passed; no UE started.';return}
if(-not $RootApproval){throw 'Root approved receipt and explicit -ExecuteImport required.'}
if(Get-Process -Name 'UnrealEditor','UnrealEditor-Cmd','UnrealBuildTool' -ErrorAction SilentlyContinue){throw 'Sequential native import requires UE/UBT closed.'}
$bootstrap=Join-Path $workspace 'UnrealGame\Saved\Bootstrap'
$before=@(Get-ChildItem -LiteralPath $bootstrap -Filter 'GuardMove7-v001-import-*.json' -File|ForEach-Object FullName)
$log=Join-Path $bootstrap ('GuardMove7-import-{0}.log' -f (Get-Date -Format 'yyyyMMdd-HHmmss-fffffff'))
$arguments=@(('"{0}"' -f (Join-Path $workspace 'UnrealGame\CodexDungeon.uproject')),'-unattended','-nosplash','-nop4','-NoLiveCoding',('-ExecutePythonScript="{0}"' -f $script),('-abslog="{0}"' -f $log))
$previousManifest=$env:DUNGEON_MOVE7_IMPORT_MANIFEST
$previousApproval=$env:DUNGEON_MOVE7_IMPORT_APPROVAL
$previousExecute=$env:DUNGEON_MOVE7_EXECUTE_IMPORT
try{
 $env:DUNGEON_MOVE7_IMPORT_MANIFEST=$Manifest;$env:DUNGEON_MOVE7_IMPORT_APPROVAL=$RootApproval;$env:DUNGEON_MOVE7_EXECUTE_IMPORT='1'
 $process=Start-Process -FilePath (Join-Path $EngineRoot 'Engine\Binaries\Win64\UnrealEditor.exe') -ArgumentList $arguments -WorkingDirectory $workspace -WindowStyle Hidden -PassThru
 Write-Output ('Move7 native import PID {0}; log {1}' -f $process.Id,$log)
 $process.WaitForExit();$process.Refresh()
}finally{$env:DUNGEON_MOVE7_IMPORT_MANIFEST=$previousManifest;$env:DUNGEON_MOVE7_IMPORT_APPROVAL=$previousApproval;$env:DUNGEON_MOVE7_EXECUTE_IMPORT=$previousExecute}
$fresh=@(Get-ChildItem -LiteralPath $bootstrap -Filter 'GuardMove7-v001-import-*.json' -File|Where-Object {$_.FullName -notin $before})
if($process.ExitCode -ne 0 -or $fresh.Count -ne 1){throw 'Actual Move7 import failed/unique fresh receipt absent; preserve partial outputs.'}
& $python -B -X utf8 $script --manifest $Manifest --verify-receipt $fresh[0].FullName
if($LASTEXITCODE -ne 0){throw 'Independent actual seven saved packages/old1364 twoSHA verification failed.'}
Write-Output ('Native saved7, Production1371; independent byte verification: '+$fresh[0].FullName)
