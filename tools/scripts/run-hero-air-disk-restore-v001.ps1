param([Parameter(Mandatory=$true)][string]$PreregPath,[Parameter(Mandatory=$true)][string]$CheckerDirectory)
$ErrorActionPreference='Stop'
$airDiskRoot='F:/Ourgame'
$airDiskPython=Join-Path $airDiskRoot 'tools/runtime/asset-gen/Scripts/python.exe'
$airDiskChecker=Join-Path ([IO.Path]::GetFullPath($CheckerDirectory)) 'verify-air-disk-restore-native-v001.py'
if(Get-Process -Name UnrealEditor,UnrealEditor-Cmd,UnrealBuildTool -ErrorAction SilentlyContinue){throw 'Two-process capture requires no existing UE/UBT process.'}
function Get-AirDiskPin([string]$Path){$airDiskItem=Get-Item -LiteralPath $Path;return @{path=$airDiskItem.FullName.Replace('\','/');bytes=$airDiskItem.Length;sha256=(Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()}}
function Write-AirDiskNewJson([string]$Path,[object]$Value){
 $airDiskStream=[IO.FileStream]::new($Path,[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::Read)
 try{$airDiskBytes=[Text.UTF8Encoding]::new($false).GetBytes(($Value|ConvertTo-Json -Depth 24));$airDiskStream.Write($airDiskBytes,0,$airDiskBytes.Length);$airDiskStream.Flush($true)}finally{$airDiskStream.Dispose()}
}
function Assert-AirDiskPin([object]$Pin){$airDiskGot=Get-AirDiskPin $Pin.path;if($airDiskGot.bytes -ne $Pin.bytes -or $airDiskGot.sha256 -cne $Pin.sha256){throw ('Actual pin changed: '+$Pin.path)}}
$airDiskPrereg=Get-Content -LiteralPath $PreregPath -Raw | ConvertFrom-Json
if($airDiskPrereg.schema -cne 'hero-air-disk-restore-root-prereg-v001' -or $airDiskPrereg.RootApproved -ne $true -or $airDiskPrereg.is_template -ne $false -or $airDiskPrereg.pre_registered_before_capture -ne $true){throw 'Actual reviewed Root prereg required.'}
foreach($airDiskField in @('compiled_manifest_pin','game_dll_pin','engine_executable_pin','uproject_pin','checker_freeze_pin','protocol_pin')){Assert-AirDiskPin $airDiskPrereg.$airDiskField}
$airDiskFreeze=Get-Content -LiteralPath $airDiskPrereg.checker_freeze_pin.path -Raw | ConvertFrom-Json
foreach($airDiskMember in $airDiskFreeze.members){Assert-AirDiskPin $airDiskMember}
$airDiskCheckerPin=Get-AirDiskPin $airDiskChecker
if(-not ($airDiskFreeze.members | Where-Object {$_.sha256 -ceq $airDiskCheckerPin.sha256 -and [IO.Path]::GetFullPath($_.path) -eq [IO.Path]::GetFullPath($airDiskChecker)})){throw 'Checker is not an exact frozen member.'}
$airDiskSessionDirectory=[IO.Path]::GetFullPath($airDiskPrereg.session_directory)
$airDiskProfilePath=Join-Path $airDiskPrereg.profiles_directory $airDiskPrereg.profile_id
if(Test-Path -LiteralPath $airDiskProfilePath){throw 'Fresh profile must be absent before source launch; preserve any existing failure.'}
& $airDiskPython -B -X utf8 $airDiskChecker --preflight --prereg $PreregPath --out (Join-Path $airDiskSessionDirectory 'independent-preflight-v001.json')
if($LASTEXITCODE -ne 0){throw 'Frozen current-lineage preflight failed; no UE launched.'}
$airDiskBeforeCM=Get-AirDiskPin $airDiskPrereg.compiled_manifest_pin.path
$airDiskBeforeDLL=Get-AirDiskPin $airDiskPrereg.game_dll_pin.path
$airDiskRoleRows=@{}
$airDiskSourcePID=0
$airDiskSourceRun=''
$airDiskSourceOwner=''
$airDiskSourceCodecSHA=''
foreach($airDiskRole in @('source','target')){
 $airDiskArchive=[IO.Path]::GetFullPath($airDiskPrereg.($airDiskRole+'_archive'))
 $airDiskOriginal=Join-Path $airDiskArchive '原件'
 if(-not (Test-Path -LiteralPath $airDiskOriginal -PathType Container)){throw 'Preregistered original directory is missing.'}
 $airDiskClaim=Join-Path $airDiskOriginal 'observer-process-claim-v001.json'
 if(Test-Path -LiteralPath $airDiskClaim){throw 'Exclusive role directory already has a process claim.'}
 Assert-AirDiskPin $airDiskPrereg.compiled_manifest_pin;Assert-AirDiskPin $airDiskPrereg.game_dll_pin
 $airDiskAbsent=$null
 $airDiskSourceExited=$null
 if($airDiskRole -eq 'source'){$airDiskAbsent=-not (Test-Path -LiteralPath $airDiskProfilePath);if(-not $airDiskAbsent){throw 'Profile appeared before source launch.'}}
 else{$airDiskSourceExited=$null -eq (Get-Process -Id $airDiskSourcePID -ErrorAction SilentlyContinue);if(-not $airDiskSourceExited){throw 'Source PID remains live; target will not start.'}}
 $airDiskMap=$airDiskPrereg.($airDiskRole+'_map')
 $airDiskArgs=@($airDiskPrereg.uproject_pin.path,$airDiskMap,'-game','-d3d11','-windowed','-ResX=1280','-ResY=720','-NoSplash','-NoLiveCoding','-nop4')
 $airDiskArgs+=@($airDiskPrereg.visual_flags|ForEach-Object {'-'+$_})
 $airDiskArgs+=@(('-DungeonHeroAirDiskRole='+$airDiskRole),('-DungeonContentProofDir='+$airDiskOriginal),('-DungeonHeroAirDiskProfilesDir='+$airDiskPrereg.profiles_directory),('-DungeonHeroAirDiskProfileGuid='+$airDiskPrereg.profile_id),('-DungeonHeroAirDiskCompiledManifestSHA='+$airDiskPrereg.compiled_manifest_pin.sha256),('-DungeonHeroAirDiskGameDLLSHA='+$airDiskPrereg.game_dll_pin.sha256),('-DungeonHeroAirDiskBuildId=v144-'+$airDiskPrereg.compiled_manifest_pin.sha256+'-'+$airDiskPrereg.game_dll_pin.sha256),('-abslog='+(Join-Path $airDiskArchive 'native-engine.log')))
 if($airDiskRole -eq 'source' -and $airDiskPrereg.diagnostic_clear_knight){$airDiskArgs+='-DungeonHeroAirDiskClearKnightDiagnostic'}
 if($airDiskRole -eq 'target'){$airDiskArgs+=@(('-DungeonHeroAirDiskExpectedRun='+$airDiskSourceRun),('-DungeonHeroAirDiskExpectedOwner='+$airDiskSourceOwner),('-DungeonHeroAirDiskExpectedCodecSHA='+$airDiskSourceCodecSHA),('-DungeonHeroAirDiskSourcePID='+[string]$airDiskSourcePID))}
 $airDiskArgumentLine=($airDiskArgs|ForEach-Object {'"{0}"' -f $_}) -join ' '
 $airDiskProcess=Start-Process -FilePath $airDiskPrereg.engine_executable_pin.path -ArgumentList $airDiskArgumentLine -WorkingDirectory (Join-Path $airDiskRoot 'UnrealGame') -WindowStyle Hidden -PassThru
 $airDiskStartedUTC=$airDiskProcess.StartTime.ToUniversalTime().ToString('O')
 $airDiskLaunch=Join-Path $airDiskArchive 'launch-receipt-v001.json'
 Write-AirDiskNewJson $airDiskLaunch @{schema='hero-air-disk-restore-process-launch-v001';is_template=$false;actual_recorded=$true;role=$airDiskRole;process_id=$airDiskProcess.Id;started_utc=$airDiskStartedUTC;executable_pin=$airDiskPrereg.engine_executable_pin;uproject_pin=$airDiskPrereg.uproject_pin;game_dll_pin=$airDiskPrereg.game_dll_pin;root_prereg_pin=(Get-AirDiskPin $PreregPath);arguments=$airDiskArgs;source_profile_absent_before_launch=$airDiskAbsent;source_process_observed_exited_before_target=$airDiskSourceExited;source_process_id=$(if($airDiskRole -eq 'target'){$airDiskSourcePID}else{$null})}
 Write-Output ('Air disk '+$airDiskRole+' PID '+$airDiskProcess.Id)
 $airDiskProcess.WaitForExit()
 $airDiskExit=Join-Path $airDiskArchive 'exit-receipt-v001.json'
 Write-AirDiskNewJson $airDiskExit @{schema='hero-air-disk-restore-process-exit-v001';is_template=$false;actual_recorded=$true;role=$airDiskRole;process_id=$airDiskProcess.Id;started_utc=$airDiskStartedUTC;exited_utc=$airDiskProcess.ExitTime.ToUniversalTime().ToString('O');exit_code=$airDiskProcess.ExitCode;os_exit_confirmed=$true;process_still_running=$false;launch_receipt_pin=(Get-AirDiskPin $airDiskLaunch)}
 $airDiskRuntimePath=Join-Path $airDiskOriginal 'runtime-report.json'
 $airDiskRuntime=$null;$airDiskPassed=$false
 if(Test-Path -LiteralPath $airDiskRuntimePath){$airDiskRuntime=Get-Content -LiteralPath $airDiskRuntimePath -Raw|ConvertFrom-Json;$airDiskPassed=$airDiskRuntime.passed -eq $true -and $airDiskRuntime.flow_complete -eq $true}
 $airDiskIndex=Join-Path $airDiskArchive 'index.json'
 Write-AirDiskNewJson $airDiskIndex @{schema='hero-air-disk-restore-native-session-index-v001';is_template=$false;actual_recorded=$true;role=$airDiskRole;process_id=$airDiskProcess.Id;exit_code=$airDiskProcess.ExitCode;root_prereg_pin=(Get-AirDiskPin $PreregPath);compiled_manifest_pin=$airDiskPrereg.compiled_manifest_pin;source_candidate_freeze_pin=$airDiskPrereg.source_candidate_freeze_pin;source_admission_pin=$airDiskPrereg.source_admission_pin;source_repair_admission_pins=@($airDiskPrereg.source_repair_admission_pins);checker_freeze_pin=$airDiskPrereg.checker_freeze_pin;game_dll_pin=$airDiskPrereg.game_dll_pin;runtime_report_pin=$(if(Test-Path -LiteralPath $airDiskRuntimePath){Get-AirDiskPin $airDiskRuntimePath}else{$null});launch_receipt_pin=(Get-AirDiskPin $airDiskLaunch);exit_receipt_pin=(Get-AirDiskPin $airDiskExit);native_runtime_passed=$airDiskPassed;archive=$airDiskArchive.Replace('\','/');FinalAccepted=$false}
 $airDiskRoleRows[$airDiskRole]=@{archive=$airDiskArchive.Replace('\','/');launch_receipt_pin=(Get-AirDiskPin $airDiskLaunch);exit_receipt_pin=(Get-AirDiskPin $airDiskExit);session_index_pin=(Get-AirDiskPin $airDiskIndex)}
 if($airDiskProcess.ExitCode -ne 0 -or -not $airDiskPassed){Write-Output 'Actual role failed; preserve all outputs, no subsequent process.';exit 3}
 if($airDiskRole -eq 'source'){
  $airDiskSourcePID=$airDiskProcess.Id;$airDiskSourceRun=[string]$airDiskRuntime.run;$airDiskSourceOwner=[string]$airDiskRuntime.owner
  if($airDiskSourceRun -cnotmatch '^[0-9a-fA-F]{32}$' -or $airDiskSourceOwner -cnotmatch '^[1-9][0-9]*$'){throw 'Actual source stable identity missing.'}
  $airDiskSourceCodecSHA=(Get-AirDiskPin (Join-Path $airDiskOriginal 'source-codec.json')).sha256
 }
}
$airDiskAfterCM=Get-AirDiskPin $airDiskPrereg.compiled_manifest_pin.path
$airDiskAfterDLL=Get-AirDiskPin $airDiskPrereg.game_dll_pin.path
if($airDiskBeforeCM.sha256 -cne $airDiskAfterCM.sha256 -or $airDiskBeforeDLL.sha256 -cne $airDiskAfterDLL.sha256){throw 'Current CM/DLL changed during pair; preserve both actual sessions.'}
$airDiskPair=Join-Path $airDiskSessionDirectory 'two-process-session-v001.json'
Write-AirDiskNewJson $airDiskPair @{schema='hero-air-disk-restore-two-process-session-v001';is_template=$false;actual_recorded=$true;root_prereg_pin=(Get-AirDiskPin $PreregPath);before_compiled_manifest_pin=$airDiskBeforeCM;after_compiled_manifest_pin=$airDiskAfterCM;before_game_dll_pin=$airDiskBeforeDLL;after_game_dll_pin=$airDiskAfterDLL;source=$airDiskRoleRows.source;target=$airDiskRoleRows.target;RootApproved=$true;FinalAccepted=$false}
& $airDiskPython -B -X utf8 $airDiskChecker --prereg $PreregPath --source $airDiskPrereg.source_archive --target $airDiskPrereg.target_archive --session $airDiskPair --out (Join-Path $airDiskSessionDirectory 'independent-two-process-verification-v001.json')
exit $LASTEXITCODE
