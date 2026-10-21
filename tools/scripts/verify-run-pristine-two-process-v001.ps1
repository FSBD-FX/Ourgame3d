param(
    [string]$EngineRoot='G:\UE_5.5',
    [string]$SessionRoot='',
    [ValidateRange(1,999)][int]$Version=1,
    [switch]$Run
)
$ErrorActionPreference='Stop'
$workspace=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\..'))
$python=Join-Path $workspace 'tools\runtime\asset-gen\Scripts\python.exe'
$checker=Join-Path $PSScriptRoot 'verify-run-pristine-two-process-v001.py'
$editor=Join-Path $EngineRoot 'Engine\Binaries\Win64\UnrealEditor.exe'
$module=Join-Path $workspace 'UnrealGame\Binaries\Win64\UnrealEditor-CodexDungeon.dll'
$sourceRoot=Join-Path $workspace 'UnrealGame\Source\CodexDungeon'
$project=Join-Path $workspace 'UnrealGame\CodexDungeon.uproject'
foreach($required in @($python,$checker,$editor,$module,$project)){
    if(-not (Test-Path -LiteralPath $required -PathType Leaf)){throw "Missing required tooling/build: $required"}
}
& $python -B -X utf8 -c 'import ast,sys;from pathlib import Path;ast.parse(Path(sys.argv[1]).read_text(encoding="utf-8"));print("Independent verifier syntax parsed; no UE launched")' $checker
if($LASTEXITCODE -ne 0){throw 'Verifier syntax failed'}
if(-not $Run){
    [ordered]@{mode='tooling_only';UE_started=$false;requires_explicit_Run=$true;candidate_source='docs/production/first-batch-v2/evidence/run-pristine-bootstrap-v001/two-process-tooling-v001/candidate-source';scope='Actual native two-process Run-only proof pending Root source admission/build/execution; no full D13/visual/device-audio claim'} | ConvertTo-Json
    return
}
function Get-TaskSha([string]$TaskPath){(Get-FileHash -LiteralPath $TaskPath -Algorithm SHA256).Hash.ToLowerInvariant()}
function Get-TaskFact([string]$TaskPath){[ordered]@{path=[IO.Path]::GetFullPath($TaskPath);bytes=(Get-Item -LiteralPath $TaskPath).Length;sha256=(Get-TaskSha $TaskPath)}}
function Get-TaskSources{
    $rows=[ordered]@{}
    foreach($item in Get-ChildItem -LiteralPath $sourceRoot -Recurse -File | Sort-Object FullName){
        $rows[$item.FullName.Substring($workspace.Length+1)]=(Get-TaskSha $item.FullName)
    }
    return $rows
}
if(@(Get-Process -Name 'UnrealEditor*','UnrealBuildTool' -ErrorAction SilentlyContinue).Count){throw 'Root must run two-process proof sequentially with no existing UE/UBT.'}
foreach($required in @('DungeonRunContinueProbe.h','DungeonRunContinueProbe.cpp')){
    if(-not (Test-Path -LiteralPath (Join-Path $sourceRoot $required))){throw 'Candidate Probe has not been admitted to actual Source and compiled by Root.'}
}
if([string]::IsNullOrWhiteSpace($SessionRoot)){
    $topic=(Get-Date -Format 'yyyyMMdd-HHmmss')+'-native-two-process-v'+$Version.ToString('000')
    $SessionRoot=Join-Path $workspace ('UnrealGame\Saved\RunPristineProofs\'+$topic)
}
$SessionRoot=[IO.Path]::GetFullPath($SessionRoot)
if(Test-Path -LiteralPath $SessionRoot){throw 'Choose an unused evidence session; never reuse a prior profile or failed run.'}
$proofMutex=[Threading.Mutex]::new($false,'Local\CodexDungeon-RunPristineTwoProcess-v1')
$ownsMutex=$false
$leaseStream=$null
$sessionPath=Join-Path $SessionRoot 'two-process-session.json'
$session=$null
try{
    $ownsMutex=$proofMutex.WaitOne(0)
    if(-not $ownsMutex){throw 'Another two-process coordinator owns the exclusive launcher mutex.'}
    if(@(Get-Process -Name 'UnrealEditor*','UnrealBuildTool' -ErrorAction SilentlyContinue).Count){throw 'UE/UBT started during coordinator admission.'}
    [IO.Directory]::CreateDirectory($SessionRoot)|Out-Null
    $leaseStream=[IO.File]::Open((Join-Path $SessionRoot 'coordinator.lock'),[IO.FileMode]::CreateNew,[IO.FileAccess]::ReadWrite,[IO.FileShare]::None)
    $profilesDirectory=Join-Path $SessionRoot 'BoundRunOnly-v1'
    [IO.Directory]::CreateDirectory($profilesDirectory)|Out-Null
    $proofProfileId=[guid]::NewGuid().ToString('D').ToLowerInvariant()
    $beforeSources=Get-TaskSources
    $beforeModule=Get-TaskSha $module
    $session=[ordered]@{schema='run-pristine-two-native-processes-v1';status='started';profile_id=$proofProfileId;
        profiles_directory=$profilesDirectory;module_sha256_before=$beforeModule;module_sha256_after='';source_sha256_before=$beforeSources;
        source_sha256_after=[ordered]@{};sources_unchanged=$false;processes=@();tool_sha256=[ordered]@{launcher=(Get-TaskSha $PSCommandPath);verifier=(Get-TaskSha $checker)};
        full_D13_profile=$false;visual_running_proof_reviewed=$false;audio_device_auditioned=$false;formal_complete_units=0}
    function Write-TaskSession{
        [IO.File]::WriteAllText($sessionPath,($session | ConvertTo-Json -Depth 12),[Text.UTF8Encoding]::new($false))
    }
    Write-TaskSession
    foreach($role in @('source','restore')){
        if(@(Get-Process -Name 'UnrealEditor*','UnrealBuildTool' -ErrorAction SilentlyContinue).Count){throw 'A native process is still running; no overlapping restore process is allowed.'}
        if((Get-TaskSha $module) -ne $beforeModule){throw 'DLL changed before role launch.'}
        $currentSources=Get-TaskSources
        if(($currentSources | ConvertTo-Json -Compress) -cne ($beforeSources | ConvertTo-Json -Compress)){throw 'Source changed before role launch.'}
        $roleDirectory=Join-Path $SessionRoot $role
        [IO.Directory]::CreateDirectory($roleDirectory)|Out-Null
        $nativeLog=Join-Path $SessionRoot ($role+'-native.log')
        $map=if($role -eq 'source'){'/Game/Maps/FirstRoom'}else{'/Game/Maps/FirstRoom?DungeonContinuePristine'}
        $proofFlag=if($role -eq 'source'){'-DungeonRunSaveProof'}else{'-DungeonRunRestoreProof'}
        $runArguments=@(('"{0}"' -f $project),$map,'-game','-windowed','-ResX=1280','-ResY=720','-NoSplash','-NoLiveCoding','-nop4','-unattended',
            $proofFlag,('-DungeonRunProofDir="{0}"' -f $roleDirectory),('-DungeonRunProofProfiles="{0}"' -f $profilesDirectory),
            ('-DungeonRunProofProfile='+$proofProfileId),('-DungeonRunProofBuildId='+$beforeModule),'-ExecCmds="t.MaxFPS 30"',('-abslog="{0}"' -f $nativeLog))
        if($role -eq 'source'){$runArguments+='-DungeonSceneExplorationPreview'}
        $started=[DateTime]::UtcNow.ToString('o')
        $ueProcess=Start-Process -FilePath $editor -ArgumentList $runArguments -WindowStyle Hidden -PassThru
        $entry=[ordered]@{role=$role;pid=$ueProcess.Id;started_utc=$started;exited_utc='';exit_code=$null;exited_before_next_launch=$false;
            module_sha256=$beforeModule;map_url=$map;arguments=$runArguments;native_log=$null}
        $session.processes+=,$entry;Write-TaskSession
        Write-Output "Two-process $role PID $($ueProcess.Id); evidence $roleDirectory"
        $deadline=[DateTime]::UtcNow.AddSeconds(120)
        while(-not $ueProcess.WaitForExit(30000)){
            if([DateTime]::UtcNow -ge $deadline){Stop-Process -Id $ueProcess.Id -Force;throw "Owned $role proof timed out; native log and partial originals retained."}
            Write-Output "Two-process $role remains active in PID $($ueProcess.Id); no second process launched."
        }
        $ueProcess.Refresh();$entry.exited_utc=[DateTime]::UtcNow.ToString('o');$entry.exit_code=$ueProcess.ExitCode;$entry.exited_before_next_launch=$true
        if(Test-Path -LiteralPath $nativeLog){$entry.native_log=Get-TaskFact $nativeLog}
        Write-TaskSession
        if($ueProcess.ExitCode -ne 0){throw "Owned $role proof failed with exit $($ueProcess.ExitCode); preserve this session and use a new version for retry."}
        if(-not (Test-Path -LiteralPath (Join-Path $roleDirectory ($role+'-report.json')))){throw "Actual $role report missing despite native exit."}
    }
    $session.source_sha256_after=Get-TaskSources;$session.module_sha256_after=Get-TaskSha $module
    $session.sources_unchanged=($session.module_sha256_after -ceq $beforeModule) -and (($session.source_sha256_after | ConvertTo-Json -Compress) -ceq ($beforeSources | ConvertTo-Json -Compress))
    $session.status='native_processes_exited_pending_independent_verification';Write-TaskSession
    if(-not $session.sources_unchanged){throw 'Actual Source/DLL changed across the two processes.'}
    $verifierLog=Join-Path $SessionRoot 'independent-verifier-output.txt'
    & $python -B -X utf8 $checker --session $SessionRoot --write-receipt *> $verifierLog
    $verifierExit=$LASTEXITCODE
    Get-Content -LiteralPath $verifierLog | Write-Output
    if($verifierExit -ne 0){throw 'Independent full-byte/head/clock/owner/reload/audio verification failed; verifier output retained.'}
    $session.status='two_real_processes_run_only_passed_visual_device_audio_full_D13_pending';Write-TaskSession
    Write-Output $SessionRoot
}
catch{
    if($null -ne $session){$session.status='failed_preserved';$session.failure=$_.Exception.Message;Write-TaskSession}
    throw
}
finally{
    if($null -ne $leaseStream){$leaseStream.Dispose()}
    if($ownsMutex){$proofMutex.ReleaseMutex()}
    $proofMutex.Dispose()
}
