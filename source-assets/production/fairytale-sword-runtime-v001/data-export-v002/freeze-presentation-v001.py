"""Static interface/source checks only; root owns the real UBT/UE validation."""
from pathlib import Path
import datetime, difflib, hashlib, json, re
R=Path('F:/Ourgame/UnrealGame/Source/CodexDungeon');O=Path(__file__).resolve().parent
paths=[R/'DungeonFairytaleSwordDrawState.h',R/'DungeonFairytaleSwordPresentation.cpp']
def desc(p):
 b=p.read_bytes();return {'path':p.as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def write(p,v):
 assert not p.exists(),p;p.write_text(v if isinstance(v,str) else json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
header,cpp=[p.read_text(encoding='utf-8') for p in paths]
hud=(R/'DungeonHUD.h').read_text(encoding='utf-8')
marker=R/'DungeonFairytaleSwordBodyV001.inl'
assert desc(marker)['sha256']=='022d0cff100f3323f6b40c64d929ad6077ae351a5a47a1c5a7a1cd2fc6ad35dd'
checks={
 'HUD_declares_both_helpers':all(x in hud for x in ['GetFairytaleSwordTexture(const FString& Clip,int32 Index)','DrawFairytaleSwordBody(ADungeonFighter* Fighter)']),
 'HUD_declares_new_state':all(x in hud for x in ['FDungeonFairytaleSwordDraw FairytaleSwordDraw','DungeonFairytaleSwordDrawState.h']),
 'new_namespace_only':'DungeonFairytaleSwordBodyV001' in cpp and 'DungeonCandidateAssembly' not in cpp and 'V007' not in cpp,
 'primary_uses_kernel_frame':"Record.Frame=Primary1?F->GetPrimaryPoseFrame()" in cpp,
 'primary_requires_real_stage0_ground_start':all(x in cpp for x in ['Action.Active','Action.Stage==0','!Action.StartedAirborne','Action.Weapon==DungeonContentCombat::EWeapon::SWD001']),
 'idle_uses167ms':"FMath::FloorToInt(double(F->AnimationTime)/.167)%4" in cpp,
 'unsupported_body_remains_new_and_sword_hidden':all(x in cpp for x in ['Record.Clip=Primary1?TEXT("sword_primary_1"):TEXT("sword_ready_idle")','if(!Record.Supported)return true;','?FMath::FloorToInt(double(F->AnimationTime)/.167)%4:0']),
 'no_actor_or_kernel_assignments':re.search(r'F->\w+\s*=(?!=)',cpp) is None,
 'no_input_or_damage_calls':not any(x in cpp for x in ['BeginAttack(', 'SimulateActions(', 'MoveOnGround(', 'ApplyCombatHit(', 'PressPrimary(', 'StepTo(', 'RestoreOwnerSnapshot(', 'SpawnActor']),
 'screenshot_request_is_read_only':all(x in cpp for x in ['FScreenshotRequest::IsScreenshotRequested()','FScreenshotRequest::GetFilename()']) and 'RequestScreenshot(' not in cpp,
 'weapon_scale_grip_and_axis_design_explicit':all(x in cpp for x in ['constexpr double WeaponScale=.40','ComponentGrip(99.,256.)','FMath::Atan2(Marker->Axis.Y,Marker->Axis.X)']),
 'source_hand_replay_uses_new_polygon':all(x in cpp for x in ['Marker->FistPolygon','Tri.V0_UV=Polygon[0]/512.','Canvas->DrawItem(Item)']),
 'only_literal_printf_formats':all('TEXT(' in x and '?' not in x for x in cpp.splitlines() if 'FString::Printf(' in x),
 'no_old_armor_layer_draw':'GetArmorLayerFrame(' not in cpp and 'GetXBW' not in cpp,
 'actual_body_draw_increments_id':'DrawTexture(Body,' in cpp and '++Record.DrawId;' in cpp,
 'new_import_namespace':'/Game/Production/ArtTrials/EV048/v004/HeroSwordBody/' in cpp,
}
assert all(checks.values()),checks
patch=''.join(''.join(difflib.unified_diff([],p.read_text(encoding='utf-8').splitlines(keepends=True),fromfile='/dev/null',tofile=p.as_posix())) for p in paths)
pp=O/'new-presentation-only-v001.patch';write(pp,patch)
report={'schema':'fairytale-sword-presentation-static-preflight-v1','created_local':datetime.datetime.now().astimezone().isoformat(),
 'owned_source':[desc(p) for p in paths],'unchanged_numeric_include':desc(marker),'checks':checks,
 'checks_passed':len(checks),'checks_failed':0,'actual_ubt_executed':False,'actual_ue_executed':False,
 'actor_kernel_or_ids_mutated':False,'existing_source_modified_by_this_task':False,
 'field_semantics':{'Active':'Opt-in presentation attempted, not combat action Active.','Supported':'Only live SWD ground-start Primary1 or stable grounded idle.','DrawId':'Monotonic count of actual new body DrawTexture submissions.','ActionId_and_times':'Live active melee Action only; zero when no active action.','Stage':'Actual active melee stage, else-1.','InstanceId':'Active action weapon instance or current melee instance when idle.','WeaponAngle':'Actual screen rotation: candidate native atan2 axis, sign reflected for Facing<0.','DrawStack':'Actual texture paths in order; final repeated body path is original fist pixel replay.','TextureReady':'New body texture resource and matching marker ready, independent of weapon texture readiness.'},
 'remaining_runtime_checks':['Actual source import/load and ordinary J phases','Left/right one-mirror transform','Fist/weapon layering and frame3 far-finger overlap','Helmet/eye clearance with first positive-axis blade sign','Ready-to-action seam and source foot drift','Unsupported state visibly remains unaccepted Ready0 with no sword'],
 'formal_complete_units':0,'status':'Static only; root must compile and review actual game.'}
rp=O/'static-preflight-v001.json';write(rp,report)
readme=O/'handoff-v001.md';write(readme,'''# New opt-in sword presentation handoff

Only the two newSource files and this new evidence directory were written. Root owns existing HUD/GameMode/Fighter edits, import, UBT and actual ordinary-input recording. Frozen numeric inl remains unchanged.

Ready4 samples AnimationTime/.167; real grounded-start SWD stage0 samples GetPrimaryPoseFrame. Unsupported states deliberately show newReady0 with Supported=false and no sword. Missing new resources suppress old-body fallthrough and report TextureReady=false. No old armor, mask, marker, angle or XBW socket is used.

Body → independent sword → new source visible-fist polygon. Fixed max72px canvas, pivot256464; screen projection plus negativeU reflect once. Existing weapon-only component grip99/256 and scale.40 are reused. Root's initial blade-positive-axis choice is explicit; thumb, source axis, approximate fist boundaries, foot drift and helmet clearance remain trial limitations.

Static checks are not a build, screenshot, playback or accepted action. Exact source bytes/SHA and a new-file-only patch accompany this handoff.
''')
files=paths+sorted(p for p in O.iterdir() if p.is_file())
fp=O/'source-freeze-v001.json';write(fp,{'schema':'fairytale-sword-presentation-source-freeze-v1','file_count':len(files),'total_bytes':sum(p.stat().st_size for p in files),'files':[desc(p) for p in files],'numeric_include_unchanged':desc(marker),'compiled':False,'ue_run':False})
print(json.dumps({'source':[desc(p) for p in paths],'patch':desc(pp),'report':desc(rp),'freeze':desc(fp),'checks':len(checks)},ensure_ascii=False))
