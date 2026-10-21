"""Prepare only a startup texture-selection candidate. Never edits actual Source."""
from pathlib import Path
import ast,datetime,difflib,hashlib,json
ROOT=Path('F:/Ourgame');OUT=Path(__file__).resolve().parent;SRC=ROOT/'UnrealGame/Source/CodexDungeon'
NAMES=['DungeonHUD.cpp','DungeonFairytaleSwordPresentation.cpp','DungeonFairytaleSwordPrimary2ArmorV001.inl','DungeonFairytaleSwordPrimary3V001.inl','DungeonFairytaleEquipmentBoundProbe.h','DungeonFairytaleEquipmentBoundProbe.cpp']
archive=ROOT/'过程图稿与视频/2026-10-17_NONRELEASE软皮连招美术诊断_diag_v001'
reportpath=archive/'原件/runtime-report.json';rootmanifest=ROOT/'source-assets/production/leather-combo-diagnostic-root-input-v001/diagnostic-compiled-inputs-v001.json'
def desc(p):
 b=p.read_bytes();return {'path':p.as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def write(n,v):
 p=OUT/n;p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x',encoding='utf-8',newline='\n') as f:f.write(v if isinstance(v,str) else json.dumps(v,ensure_ascii=False,indent=2)+'\n')
 return p
def copyn(n,b):
 p=OUT/n;p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('xb') as f:f.write(b)
 return p
report=json.loads(reportpath.read_text(encoding='utf-8-sig'));obs=report['observations']
assert report['passed'] is False and len(obs)==168
assert len(report['mismatches'])==4 and {x['first_observation'] for x in report['mismatches']}=={59}
bad=[i for i,o in enumerate(obs) if not o['texture_ready']]
assert bad==[59,61,63,65,69,73,76,79,81,83,88]
manifest=json.loads(rootmanifest.read_text(encoding='utf-8-sig'));pins={r['path']:r for r in manifest['files']}
source=[]
for name in NAMES:
 p=SRC/name;d=desc(p);pin=pins[p.relative_to(ROOT).as_posix()]
 assert d['bytes']==pin['bytes'] and d['sha256']==pin['sha256'],name
 source.append(d);copyn('current-source-originals/'+name,p.read_bytes())
hud=(SRC/'DungeonHUD.cpp').read_bytes();newhud=hud
for stage,ns in [(2,'DungeonFairytaleSwordPrimary2ArmorV001'),(3,'DungeonFairytaleSwordPrimary3V001')]:
 old=f'if(auto Texture={ns}::GetTexture(Component,I,Frames))ReadyArmorTextures.Add(Texture);'.encode()
 new=(f'if(auto Texture={ns}::GetTexture(Component,I,Frames,\r\n'
      f'                        bUseFairytaleSwordEquipmentBoundPreview&&FParse::Param(FCommandLine::Get(),TEXT("DungeonFairytaleLeatherPrimary{stage}Preview"))))ReadyArmorTextures.Add(Texture);').encode()
 assert newhud.count(old)==1,stage
 newhud=newhud.replace(old,new)
# This is a source audit, not a C++ runtime test. Only two startup call sites differ.
expected_diff=list(difflib.unified_diff(hud.decode().splitlines(True),newhud.decode().splitlines(True),fromfile='a/UnrealGame/Source/CodexDungeon/DungeonHUD.cpp',tofile='b/UnrealGame/Source/CodexDungeon/DungeonHUD.cpp'))
assert sum(x.startswith('-') and not x.startswith('---') for x in expected_diff)==2
assert sum(x.startswith('+') and not x.startswith('+++') for x in expected_diff)==4
for n in NAMES:copyn(n,newhud if n=='DungeonHUD.cpp' else (SRC/n).read_bytes())
patch=write('leather-combo-startup-preload-v002.patch',''.join(expected_diff))
rows=[]
for i in bad:
 o=obs[i];stage=o['stage'];frame=o['frame'];key=(o['clip'],frame)
 first=next(j for j,x in enumerate(obs) if (x['clip'],x['frame'])==key)
 nextgood=next((j for j in range(i+1,len(obs)) if (obs[j]['clip'],obs[j]['frame'])==key and obs[j]['texture_ready']),None)
 expected=[]
 for component in ['ShoulderFar','Chest','ShoulderNear']:
  name=f'T_Fairytale_LeatherPrimary{stage+1}{component}_{frame:03d}_v001'
  expected.append(f'/Game/Production/ArtTrials/EV048/v{stage+13:03d}/HeroLeatherPrimary{stage+1}/{name}.{name}')
 rows.append({'observation':i,'wall_offset_s':o['wall_offset_s'],'actual_clip':o['clip'],'actual_frame':frame,'actual_stage':stage,'actual_action_id':o['action_id'],'actual_facing':o['facing'],'actual_body_texture':o['texture'],'actual_texture_ready':o['texture_ready'],'actual_armor_ready':o['armor_ready'],'actual_armor_drawn':o['armor_drawn'],'actual_draw_stack':o['draw_stack'],'actual_weapon_path':o['weapon'],'actual_draw_id':o['draw_id'],'first_observation_of_clip_frame':first,'is_first_use':i==first,'next_observation_same_clip_frame_ready':nextgood,'next_ready_wall_offset_s':obs[nextgood]['wall_offset_s'] if nextgood is not None else None,'next_ready_body_matches':obs[nextgood]['texture']==o['texture'] if nextgood is not None else None,'expected_new_armor_paths_derived_from_unchanged_renderer_NOT_observed_failed_paths':expected,'individual_failed_texture_or_GetResource_vs_pending_reason':'UNKNOWN: native report stores aggregate armor_ready only.'})
firsts=[]
seen=set()
for i,o in enumerate(obs):
 key=(o['clip'],o['frame'])
 if key not in seen:
  seen.add(key);firsts.append({'observation':i,'clip':o['clip'],'frame':o['frame'],'ready':o['texture_ready'],'armor_ready':o['armor_ready'],'facing':o['facing'],'action_id':o['action_id']})
assert all(x['is_first_use'] for x in rows)
assert not any(not o['texture_ready'] for o in obs if o['facing']==1)
start=hud.decode();finish=start.index('FTextureCompilingManager::Get().FinishCompilation(ReadyArmorTextures)');flush=start.index('    FlushRenderingCommands();')
investigation=write('startup-first-use-investigation-v002.json',{'schema':'actual-native-leather-startup-first-use-investigation-v002','created_local':datetime.datetime.now().astimezone().isoformat(),'actual_report':desc(reportpath),'actual_capture_index':desc(archive/'index.json'),'actual_runtime_log':desc(archive/'runtime.log'),'actual_root_diagnostic_inputs':desc(rootmanifest),'native_passed':False,'flow_complete':report['flow_complete'],'observations':len(obs),'deduplicated_mismatches':report['mismatches'],'actual_bad_observation_count':len(bad),'bad_observations':rows,'all_clip_frame_first_observations':firsts,'later_right_facing_bad_observations':0,'facts':['Ready/P1 GetTexture helpers select leather by the art flags internally, including during startup.','P2/P3 startup calls omit UseLeather and therefore select old armor via the default false argument.','The actual renderer passes committed BoundLightArmor AND explicit leather flag, selecting the new v014/v015 components.','All 11 failed observations are first use of the corresponding P2/P3 clip-frame; the next observed same phase is ready and later right-facing sequence has no failure.','P2 frame0 first observed use is already ready. First-use asynchronous resource initialization does not fail deterministically for every phase.','Each failed observation has armor_ready=false, an empty actual draw_stack and empty weapon path, because the unchanged whole-draw resource gate returns before emitting either armor/body or sword.','The native four mismatch reasons are deduplicated per step, not four distinct failed observations.'],'inference':'The startup source-selection defect leaves 36 new selected P2/P3 armor textures out of FinishCompilation/startup render flush; drawing then first-loads them. The first-use-only aggregate armor failures are consistent with asynchronous texture/render initialization.','uncertainty':['No individual per-layer resource state was recorded, so this evidence cannot name which of the three layers had a null resource, was pending, or was still compiling.','A minimal preload correction is a hypothesis to verify in a new cold native capture, not proof that every resource timing issue is solved.'],'working_reference':'The existing Ready/P1 startup helpers select their new leather textures before the existing FinishCompilation and FlushRenderingCommands, unlike P2/P3 omitted argument.','correction_scope':'Only the two HUD BeginPlay P2/P3 calls receive selected bound-mode plus their art flag. Existing FinishCompilation, startup FlushRenderingCommands, rendering readiness gate, draw order, normal input, actual clock/frame/IDs, observation capture and verification remain byte-identical.','risk_and_cost':'Same number of selected startup armor textures; replace old armor selection with new selection under explicit Bound plus per-stage flag. Preloading a possible asset does not authorize drawing it; committed equipment resolver remains unchanged. Default/no-flag calls remain old selection.','required_native_test':'Root must recompile and run a new process/cold native combo capture; all 168-style observations, all 36 phase-facing samples, six true attack IDs, Ready counts, CRC/FIFO/flush, and mismatch==0 checks stay intact. Do not postprocess the old RED as passing.'})
outputs=[]
for d in source:
 n=Path(d['path']).name;o=desc(OUT/n);outputs.append({'target':d['path'],'candidate':o,'original':d,'changed':n=='DungeonHUD.cpp'})
contract=write('preload-candidate-contract-v002.json',{'schema':'leather-combo-startup-preload-unapplied-source-v002','scope':'UNAPPLIED candidate; new cold native verification required; not release/full unit acceptance.','source_count':6,'modified_source_files':['DungeonHUD.cpp'],'unchanged_original_art_source_count':5,'inputs':source,'source_outputs':outputs,'source_selection_mismatches_fixed_in_candidate':2,'old_5Source_candidate_or_renderer_changes':False,'new_6Source_binding_required':True,'native_source_freeze':desc(ROOT/'source-assets/production/fairytale-lgt-readability-v003/leather-combo-source-v001/source-freeze-v001.json'),'formal_NATIVE_NAMES_5_unchanged':True,'additional_source_pins':[{'path':(SRC/'DungeonHUD.cpp').as_posix(),'bytes':(OUT/'DungeonHUD.cpp').stat().st_size,'sha256':desc(OUT/'DungeonHUD.cpp')['sha256']}],'old_Diagnostic_inputs_reusable_after_admission':False,'probe_or_validator_assertions_modified':False,'error_observations_removed':False,'fake_time_frame_ids_or_masks':False,'actual_compile_performed':False,'actual_native_retest_performed':False,'runtime_fix_verified':False,'formal_complete_units':0,'investigation':desc(investigation),'patch':desc(patch)})
write('HANDOFF.md','Only DungeonHUD.cpp changes: the two existing P2/P3 startup calls now select the same optional leather namespace as the renderer, before the unchanged texture compilation completion and startup render flush. The original five art Source files remain byte-exact; explicit complete candidate binding has six files.\n\nActual diag_v001 remains RED: 11 first-use observations fail aggregate armor readiness; the four reasons are deduplicated. Individual failing component and null-vs-pending state were not recorded. Recompile and cold native retest are required. Do not hide observations, delay/fake action timing or weaken checks. Root owns admission, new Source/DLL contract, native test and E retention/view. No UE, Source, tools, ledger, status or media writes/view were performed here.\n')
verification=write('candidate-source-verification-v002.json',{'source_checks':'Static byte/patch/selection audit only; not C++ compilation or runtime test.','actual_native_RED_fixture':desc(reportpath),'retained_bad_observation_indices':bad,'before_source_selection_defect_call_count':2,'after_candidate_explicit_selection_call_count':2,'only_modified_source':'DungeonHUD.cpp','removed_source_lines':2,'added_source_lines':4,'unchanged_original_art_sources':5,'original_source_pins_before_after_mismatch':0,'actual_compiled':False,'actual_native_retest':False})
for d in source:assert desc(Path(d['path']))==d,'Live source changed during prepare'
files=[desc(p) for p in sorted(OUT.rglob('*')) if p.is_file()]
freeze=write('source-freeze-v002.json',{'schema':'leather-combo-startup-preload-unapplied-source-candidate-freeze-v002','inputs':source,'source_outputs':outputs,'files':files,'contract':desc(contract),'patch':desc(patch),'status':'READY_FOR_ROOT_REVIEW_NOT_ADMITTED_NOT_COMPILED','actual_native_retest_performed':False,'formal_complete_units':0})
for d in files:assert desc(Path(d['path']))==d
print(json.dumps({'freeze':desc(freeze),'candidateHUD':desc(OUT/'DungeonHUD.cpp'),'files':len(files),'bad_observations':bad,'source_mismatches':0,'changed_sources':1,'unchanged_art_sources':5},indent=2))
