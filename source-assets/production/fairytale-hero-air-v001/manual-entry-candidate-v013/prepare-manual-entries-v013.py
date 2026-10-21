"""Prepare existing eight manual-entry derivatives. Never adopt or launch UE."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,difflib,re

ROOT=Path('F:/Ourgame');HERE=Path(__file__).resolve().parent
OLD_CORE=ROOT/'source-assets/production/fairytale-guard-v001/Move7-manual-checkpoint-candidate-v001/launch-guard-room-native-trial-v012.ps1'
OLD_WRAPPER=ROOT/'tools/scripts/launch-guard-room-native-trial-v012.ps1'
CM=ROOT/'source-assets/production/backups/v142-HeroAir6-Observer296-CallbackReady-203GREEN-v002/compiled-source-manifest.json'
CM_SHA='52f906018a042d006db3470ec2fa7b4603a6b54e2489ab33d2bdff0bf309cd62'
CHECKER_DIR=HERE.parent/'production-observer-callback-ready-v002/tooling-queued-input-v003'
CHECKER_FREEZE=CHECKER_DIR/'Air-production-proof-checker-freeze-v003.json'
CHECKER_SHA='a6bb3f8bd3127aa49b788f72ec1e7d9c9a9bddf8d790eb3c80c1de45e8166a46'
FUTURE_CHECKPOINT=HERE.parent/'root-manual-v013/manual-input-v013.json'
NAMES=['裂岩守卫挥斧试样.cmd','石廊三敌原生试玩.cmd','裂岩守卫三动作试样.cmd','钟盔轻甲倒地试玩.cmd','钟盔轻甲受击试玩.cmd','裂岩守卫跺击试玩.cmd','钟盔轻甲闪避试玩.cmd','裂岩守卫行走试玩.cmd']


def pin(p):
    p=Path(p).resolve();b=p.read_bytes();return dict(path=p.as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())


def write(p,data):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    if not isinstance(data,(str,bytes)):data=json.dumps(data,ensure_ascii=False,indent=2,allow_nan=False)+'\n'
    b=data.encode('utf-8') if isinstance(data,str) else data
    with p.open('xb') as f:f.write(b)


def main():
    if pin(CM)['sha256']!=CM_SHA or pin(CHECKER_FREEZE)['sha256']!=CHECKER_SHA:raise ValueError('Current frozen input differs')
    cm=json.loads(CM.read_text(encoding='utf-8-sig'))
    if (cm['source_files'],cm['production_files'],cm['registered_tests'],cm['passed'],cm['failed'],cm['notRun'])!=(296,1419,203,203,0,0):raise ValueError('Current strict CM differs')
    old=OLD_CORE.read_text(encoding='utf-8-sig')
    cut=old.index("if(@(Get-Process -Name")
    native_body=old[cut:]
    needle="'-DungeonFairytaleSwordDodgePreview',"
    if native_body.count(needle)!=1:raise ValueError('Existing manual flag seam absent')
    native_body=native_body.replace(needle,"'-DungeonFairytaleSwordDodgePreview','-DungeonFairytaleSwordAirPreview',",1)
    native_body=native_body.replace('guard-room-Move7-trial-','guard-room-Air6-v013-trial-',1)
    native_body+="Write-Output 'Hero Air6 is a bounded SWD/NoArmor and SWD/LGT preview. Landing/Ready joins remain WIP; no formal unit acceptance.'\n"
    gate=r'''param([string]$EngineRoot='G:\UE_5.5',[string]$Snapshot='',[string]$RootCheckpoint='',[switch]$LightArtTrial,[switch]$GuardFullArt,[switch]$ValidateOnly)
$ErrorActionPreference='Stop';$workspace='F:\Ourgame'
if(-not $RootCheckpoint){throw 'Root must select a v013 manual admission after actual Air keyframe review for LIMITED_WIP.'}
function Resolve-PinPath($Pin){
 if(-not $Pin){throw 'Required Root actual pin is missing.'}
 if([IO.Path]::IsPathRooted($Pin.path)){[IO.Path]::GetFullPath($Pin.path)}else{[IO.Path]::GetFullPath((Join-Path $workspace $Pin.path))}
}
function Assert-PinnedFile($Pin){
 $path=Resolve-PinPath $Pin;$item=Get-Item -LiteralPath $path
 if($item.Length -ne $Pin.bytes -or (Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant() -ne $Pin.sha256){throw "Root actual pin changed: $path"}
}
function Read-PinnedJson($Pin){
 Assert-PinnedFile $Pin
 Get-Content -LiteralPath (Resolve-PinPath $Pin) -Raw|ConvertFrom-Json
}
function Same-Pin($A,$B){
 $A -and $B -and $A.bytes -eq $B.bytes -and $A.sha256 -eq $B.sha256 -and (Resolve-PinPath $A) -eq (Resolve-PinPath $B)
}
$checkpointPath=if([IO.Path]::IsPathRooted($RootCheckpoint)){[IO.Path]::GetFullPath($RootCheckpoint)}else{[IO.Path]::GetFullPath((Join-Path $workspace $RootCheckpoint))}
$checkpoint=Get-Content -LiteralPath $checkpointPath -Raw|ConvertFrom-Json
if($checkpoint.schema -ne 'HeroAir6-Root-manual-entry-v013' -or $checkpoint.RootApproved -ne $true -or $checkpoint.is_template -ne $false -or $checkpoint.approval_scope -ne 'LIMITED_WIP' -or $checkpoint.Root_visible_keyframes_reviewed -ne $true -or $checkpoint.manual_trial_allowed -ne $true -or $checkpoint.full_realtime_playback_reviewed -ne $false -or $checkpoint.audio_listened -ne $false -or $checkpoint.known_pose_join_refinement_open -ne $true -or $checkpoint.FinalAccepted -ne $false){throw 'Candidate lacks actual LIMITED_WIP Root manual-trial approval; UE has not been started.'}
if($checkpoint.compiled_manifest_pin.sha256 -ne '__CM_SHA__'){throw 'Manual v013 must bind its actual current CM296/1419/203.'}
$compiled=Read-PinnedJson $checkpoint.compiled_manifest_pin
if($compiled.source_files -ne 296 -or $compiled.production_files -ne 1419 -or $compiled.registered_tests -ne 203 -or $compiled.passed -ne 203 -or $compiled.failed -ne 0 -or $compiled.notRun -ne 0){throw 'Current compiled registry/counts differ.'}
if($Snapshot){$selected=[IO.Path]::GetFullPath($Snapshot);$bound=[IO.Path]::GetFullPath($checkpoint.compiled_manifest_pin.path);if($selected -ne $bound -and $selected -ne [IO.Path]::GetDirectoryName($bound)){throw 'Snapshot override differs from Root approved current CM.'}}
$prereg=Read-PinnedJson $checkpoint.native_prereg_pin
if($prereg.compiled_manifest_pin.sha256 -ne '__CM_SHA__' -or $prereg.checker_freeze_pin.sha256 -ne '__CHECKER_SHA__'){throw 'Root native prerequisite binds different compiled/checker inputs.'}
$pair=Read-PinnedJson $checkpoint.native_pair_result_pin
if($pair.schema -ne 'hero-Air6-production-independent-pair-v001' -or $pair.passed -ne $true -or $pair.actual_two_fresh_PIDs -ne $true -or $pair.both6pose_None6_LGT9_rejump_Ready_verified -ne $true -or $checkpoint.full_preflight_evidence -ne 'frozen_v003_paircheck_each_native_branch'){throw 'Actual fresh left/right Air validation and retained complete preflight evidence are required.'}
foreach($branch in @($pair.left,$pair.right)){
 if($branch.schema -ne 'hero-Air6-production-independent-native-v001' -or $branch.passed -ne $true -or -not (Same-Pin $branch.compiled_manifest_pin $checkpoint.compiled_manifest_pin) -or -not (Same-Pin $branch.checker_freeze_pin $prereg.checker_freeze_pin) -or -not (Same-Pin $branch.source_probe_freeze_pin $prereg.source_probe_freeze_pin)){throw 'Native pair branch binds different compiled/source/checker inputs.'}
}
if(-not ((Same-Pin $pair.left.root_prereg_pin $checkpoint.native_prereg_pin) -or (Same-Pin $pair.right.root_prereg_pin $checkpoint.native_prereg_pin))){throw 'Selected actual prereg is absent from the approved native pair.'}
$checkerFreeze=Read-PinnedJson $prereg.checker_freeze_pin
foreach($member in $checkerFreeze.members){Assert-PinnedFile $member}
$null=Read-PinnedJson $checkpoint.Root_visual_review_receipt_pin
$candidateFreeze=Read-PinnedJson $checkpoint.manual_candidate_freeze_pin
if(-not @($candidateFreeze.members|Where-Object {[IO.Path]::GetFullPath($_.path) -eq [IO.Path]::GetFullPath($PSCommandPath)}).Count){throw 'Current manual launcher is absent from Root approved candidate freeze.'}
foreach($member in $candidateFreeze.members){
 $file=Get-Item -LiteralPath $member.path
 if($file.Length -ne $member.bytes -or (Get-FileHash -LiteralPath $member.path -Algorithm SHA256).Hash.ToLowerInvariant() -ne $member.sha256){throw "Manual candidate changed: $($member.path)"}
}
# Full v003 paircheck calls verify_native -> complete C.preflight for each branch.
# Root pins that actual result at admission; each launch verifies all current CM bytes/membership.
$names=[System.Collections.Generic.HashSet[string]]::new([StringComparer]::Ordinal)
foreach($member in $compiled.files){
 if(-not $names.Add([string]$member.path)){throw 'Duplicate current compiled membership.'}
 Assert-PinnedFile $member
}
if(-not $names.Contains('UnrealGame/Binaries/Win64/UnrealEditor-CodexDungeon.dll')){throw 'Current compiled game DLL pin is missing.'}
foreach($directory in @(@{prefix='UnrealGame/Source/';count=296},@{prefix='UnrealGame/Content/Production/';count=1419})){
 $expected=[System.Collections.Generic.HashSet[string]]::new([StringComparer]::Ordinal)
 foreach($name in $names){if($name.StartsWith($directory.prefix,[StringComparison]::Ordinal)){[void]$expected.Add($name)}}
 $actual=[System.Collections.Generic.HashSet[string]]::new([StringComparer]::Ordinal)
 foreach($file in Get-ChildItem -LiteralPath (Join-Path $workspace $directory.prefix) -Recurse -File -Force){[void]$actual.Add($file.FullName.Substring($workspace.Length+1).Replace('\','/'))}
 if($actual.Count -ne $directory.count -or -not $actual.SetEquals($expected)){throw "Current compiled directory membership differs: $($directory.prefix)"}
}
if($ValidateOnly){[ordered]@{compiled_inputs_verified=$true;actual_CM_members_checked=$names.Count;full_preflight_evidence='frozen_v003_paircheck_each_native_branch';historical_E_closure_reexpanded=$false;strict_registry=203;source_files=296;production_files=1419;manual_light_source=[bool]$LightArtTrial;guard_full_art=[bool]$GuardFullArt;death_art=$true;dodge_art=$true;dodge_preload=33;stomp_overlay=[bool]($GuardFullArt -or $LightArtTrial);oldGuardProfileUnique=44;StompOverlayUnique=50;Move7_enabled=[bool]($GuardFullArt -or $LightArtTrial);Move7_parts=7;Move7_required_resources=7;Move7_flag='DungeonFairytaleGuardMoveRigPreview';Air6_enabled=$true;Air6_flag='DungeonFairytaleSwordAirPreview';Air6_source_textures=49;Air6_None_slots=6;Air6_LGT_slots=9;automatic_inputs=$false;diagnostic_damage=$false;debug_range_enabled=$false;traditional_HUD_shown=$false;approval_scope='LIMITED_WIP';content_status='WIP limited manual preview; joins under refinement';full_realtime_playback_reviewed=$false;audio_listened=$false;known_pose_join_refinement_open=$true;UE_started=$false;FinalAccepted=$false}|ConvertTo-Json;return}
'''
    gate=gate.replace('__CM_SHA__',CM_SHA).replace('__CHECKER_SHA__',CHECKER_SHA).replace('__CHECKER_ENTRY__',(CHECKER_DIR/'verify-Air-production-native-v001.py').as_posix())
    core=HERE/'launch-guard-room-native-trial-v013.ps1';write(core,gate+native_body)
    wrapper=OLD_WRAPPER.read_text(encoding='utf-8-sig')
    wrapper=wrapper.replace('F:/Ourgame/source-assets/production/fairytale-guard-v001/root-Move7-checkpoint-v001/manual-input-v001.json',FUTURE_CHECKPOINT.as_posix())
    wrapper=wrapper.replace('F:/Ourgame/source-assets/production/fairytale-guard-v001/Move7-manual-checkpoint-candidate-v001/launch-guard-room-native-trial-v012.ps1',core.as_posix())
    wrapper_path=HERE/'Root-wrapper-candidate-v013.ps1';write(wrapper_path,wrapper)
    before=[];admissions=[]
    for name in NAMES:
        src=ROOT/name;data=src.read_bytes()
        if data.count(b'launch-guard-room-native-trial-v012.ps1')!=1:raise ValueError('Actual v012 entry differs: '+name)
        before.append(pin(src));write(HERE/'before-entries'/name,data)
        after=data.replace(b'launch-guard-room-native-trial-v012.ps1',b'launch-guard-room-native-trial-v013.ps1',1)
        dst=HERE/'entries'/name;write(dst,after)
        admissions.append(dict(actual_target=src.as_posix(),before=pin(src),candidate_after=pin(dst)))
    write(HERE/'before-source/Root-wrapper-v012.ps1',OLD_WRAPPER.read_bytes())
    write(HERE/'before-source/launcher-core-v012.ps1',OLD_CORE.read_bytes())
    write(HERE/'manual-native-arguments-only-v012-to-v013.diff',''.join(difflib.unified_diff(old[cut:].splitlines(True),native_body.splitlines(True),fromfile='v012-native-body',tofile='v013-native-body')))
    old_flags=re.findall(r"'-Dungeon[^']+'",old[cut:])
    new_flags=re.findall(r"'-Dungeon[^']+'",native_body)
    if sorted(new_flags)!=sorted(old_flags+["'-DungeonFairytaleSwordAirPreview'"]):raise ValueError('Non-Air gameplay flag changed')
    forbidden=['-DungeonContentProof','-DungeonHeroAirProductionProofV001','-DungeonHeroAirProofV001','-DungeonHeroAirProductionClearKnightDiagnostic','InputKey(','ApplyCombatHit(','-ExecCmds','-FixedTimeStep','-nullrhi','-DungeonShowInterface','-DungeonCombatRangeDebug']
    if any(x in gate+native_body for x in forbidden):raise ValueError('Automatic/diagnostic/nonmanual path present')
    template=dict(schema='HeroAir6-Root-manual-entry-v013',RootApproved=False,is_template=True,manual_trial_allowed=False,approval_scope='LIMITED_WIP',Root_visible_keyframes_reviewed=False,
        full_realtime_playback_reviewed=False,audio_listened=False,known_pose_join_refinement_open=True,
        full_preflight_evidence='frozen_v003_paircheck_each_native_branch',compiled_manifest_pin=pin(CM),native_prereg_pin=None,native_pair_result_pin=None,Root_visual_review_receipt_pin=None,manual_candidate_freeze_pin=None,
        expected_source_files=296,expected_production_files=1419,strict_registry=203,
        content_status='WIP SWD/NoArmor and SWD/LGT Air6 preview; landing/Ready joins need refinement; formal units not accepted',
        actual_entry_adoption_performed=False,automatic_inputs=False,diagnostic_damage=False,FinalAccepted=False)
    write(HERE/'Root-manual-input-TEMPLATE-v013.json',template)
    write(HERE/'Root-manual-entry-admit-index-v013.json',dict(schema='HeroAir6-manual-entry-candidate-admit-index-v013',utc=datetime.now(timezone.utc).isoformat(),
        RootApproved=False,is_template=True,actual_applied=False,current_CM=pin(CM),current_frozen_checker=pin(CHECKER_FREEZE),
        actual_old_wrapper=pin(OLD_WRAPPER),old_core=pin(OLD_CORE),old_v012_files_preserved=True,
        actual_wrapper_target=(ROOT/'tools/scripts/launch-guard-room-native-trial-v013.ps1').as_posix(),candidate_wrapper=pin(wrapper_path),candidate_runtime_core=pin(core),
        future_Root_manual_checkpoint=FUTURE_CHECKPOINT.as_posix(),eight_entry_admissions=admissions,entry_count=8,
        old_manual_contract='Historical Source283/Production1371/full200 contract is preserved and not claimed valid for current296. Root admission reuses the actual frozen Air queued v003 paircheck complete preflights; launches check all current CM bytes and exact Source/Production membership; Root separately approves LIMITED_WIP manual trial after actual keyframe review; full realtime playback and listening remain unreviewed.',
        candidate_native_flags=old_flags+["'-DungeonFairytaleSwordAirPreview'"],one_added_gameplay_flag_only=True,
        Root_must_preserve_old_actual_entries_before_adoption=True,Root_actual_keyframe_review_and_non_template_LIMITED_WIP_approval_required=True,approval_scope='LIMITED_WIP',full_realtime_playback_reviewed=False,audio_listened=False,known_pose_join_refinement_open=True,
        no_actual_cmd_tools_README_Source_Content_E_writes=True,UE_started=False,automatic_inputs=False,diagnostic_damage=False,FinalAccepted=False))
    print(json.dumps(dict(entries=8,core=pin(core),wrapper=pin(wrapper_path),current_CM=pin(CM),candidate_only=True,UE_started=False,actual_entry_adoption=False)))


if __name__=='__main__':main()
