param([Parameter(Mandatory=$true)][ValidatePattern('^v[0-9]{3}$')][string]$Version,[Parameter(Mandatory=$true)][string]$CompiledManifest,[Parameter(Mandatory=$true)][string]$SourceAdmission,[Parameter(Mandatory=$true)][string]$CheckerFreeze)
$ErrorActionPreference='Stop'
$readyRoot='F:/Ourgame'
$readyPython=Join-Path $readyRoot 'tools/runtime/asset-gen/Scripts/python.exe'
$readyChecker=Join-Path $PSScriptRoot 'verify-ready-entry-native-v001.py'
if(Get-Process -Name UnrealEditor,UnrealEditor-Cmd,UnrealBuildTool -ErrorAction SilentlyContinue){throw 'Exclusive native default Ready capture requires no UE/UBT process.'}
$readyPrep= & $readyPython -B -X utf8 (Join-Path $PSScriptRoot 'prepare-ready-entry-prereg-v001.py') --version $Version --checker-freeze $CheckerFreeze --compiled-manifest $CompiledManifest --source-admission $SourceAdmission
if($LASTEXITCODE -ne 0){throw 'Fresh Root prereg failed; preserve any created output.'}
$readyPrepared=$readyPrep|ConvertFrom-Json
$readyArchive=$readyPrepared.archive
$readyPreregPath=Join-Path $readyArchive 'preregistration-v001.json'
$readyPrereg=Get-Content -LiteralPath $readyPreregPath -Raw|ConvertFrom-Json
& $readyPython -B -X utf8 $readyChecker --preflight --compiled-manifest $CompiledManifest --source-admission $SourceAdmission --out (Join-Path $readyArchive 'independent-preflight-v001.json')
if($LASTEXITCODE -ne 0){throw 'Actual current preflight failed; UE was not started.'}
function Write-ReadyNewJson([string]$Path,[object]$Value){
 $readyStream=[IO.FileStream]::new($Path,[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::Read)
 try{$readyBytes=[Text.UTF8Encoding]::new($false).GetBytes(($Value|ConvertTo-Json -Depth 20));$readyStream.Write($readyBytes,0,$readyBytes.Length);$readyStream.Flush($true)}finally{$readyStream.Dispose()}
}
function Get-ReadyPin([string]$Path){$readyItem=Get-Item -LiteralPath $Path;return @{path=$readyItem.FullName;bytes=$readyItem.Length;sha256=(Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()}}
$readyArgs=@($readyPrereg.arguments)
$readyArgumentLine=($readyArgs|ForEach-Object {'"{0}"' -f $_}) -join ' '
$readyProcess=Start-Process -FilePath 'G:/UE_5.5/Engine/Binaries/Win64/UnrealEditor.exe' -ArgumentList $readyArgumentLine -WorkingDirectory 'F:/Ourgame/UnrealGame' -WindowStyle Hidden -PassThru
Write-ReadyNewJson (Join-Path $readyArchive 'launch-receipt-v001.json') @{schema='Root-primary1-bridge258-ready-entry-launch-v001';process_id=$readyProcess.Id;started_utc=(Get-Date).ToUniversalTime().ToString('O');arguments=$readyArgs;human_input=$false;Knight_cleanup=$false;forced_pose_HP_AI_position_time=$false;source_scope='original map/default EquipmentBound QA registered sources';FinalAccepted=$false}
Write-Output ('Ready entry native PID '+$readyProcess.Id+' archive '+$readyArchive)
$readyProcess.WaitForExit()
$readyReportPath=Join-Path $readyArchive '原件/runtime-report.json'
$readyPassed=$false
if(Test-Path -LiteralPath $readyReportPath){try{$readyRuntime=Get-Content -LiteralPath $readyReportPath -Raw|ConvertFrom-Json;$readyPassed=$readyRuntime.passed -eq $true -and $readyRuntime.flow_complete -eq $true}catch{$readyPassed=$false}}
Write-ReadyNewJson (Join-Path $readyArchive 'index.json') @{schema='Root-primary1-bridge258-ready-entry-native-session-v001';process_id=$readyProcess.Id;exit_code=$readyProcess.ExitCode;root_prereg_pin=(Get-ReadyPin $readyPreregPath);compiled_manifest_pin=$readyPrereg.compiled_manifest_pin;source_admission_pin=$readyPrereg.source_admission_pin;checker_freeze_pin=$readyPrereg.checker_freeze_pin;workflow_native_flow_passed=$readyPassed;finished_utc=(Get-Date).ToUniversalTime().ToString('O');internal_runtime_PID_available=$false;FinalAccepted=$false}
# Always preserve complete original report, extra combo and armor flow, including real native RED.
& $readyPython -B -X utf8 $readyChecker --archive $readyArchive --compiled-manifest $CompiledManifest --source-admission $SourceAdmission --out (Join-Path $readyArchive 'independent-verification-v001.json')
$readyCheckExit=$LASTEXITCODE
if($readyProcess.ExitCode -ne 0){exit $readyProcess.ExitCode}
if(-not $readyPassed -or $readyCheckExit -ne 0){Write-Output 'Original native default flow/capture failure preserved; no cleanup, pose forcing, retry or gate relaxation.';exit 3}
Write-Output ('Bounded Ready-to-258 native entry passed '+$readyArchive)
exit 0
