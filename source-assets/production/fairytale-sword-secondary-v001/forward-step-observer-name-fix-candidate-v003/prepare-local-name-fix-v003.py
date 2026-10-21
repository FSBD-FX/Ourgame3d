"""Exactly two local identifier renames, preserving all other original bytes."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,re
H=Path(__file__).resolve().parent;B=H.parent;OLD=B/'forward-step-native-observer-candidate-v002';ROOT=H.parents[3]
REL='projected/UnrealGame/Source/CodexDungeon/'
def pin(p):
 p=Path(p).resolve();v=p.read_bytes();return {'path':p.as_posix(),'bytes':len(v),'sha256':hashlib.sha256(v).hexdigest()}
def write(rel,obj):
 p=H/rel;p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x',encoding='utf8') as f:f.write(obj if isinstance(obj,str) else json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
 return p
def rawwrite(rel,v):
 p=H/rel;p.parent.mkdir(parents=True,exist_ok=True)
 if p.exists():
  assert p.read_bytes()==v;return p
 with p.open('xb') as f:f.write(v)
 return p
oldfreeze=OLD/'candidate-freeze-v002-current81.json';assert pin(oldfreeze)['sha256']=='13ab5c9e13643ddaccc71377a66dfe022185e8a666f26fadbb895400ba81305c'
f=json.loads(oldfreeze.read_text(encoding='utf8'))
for row in f['members']:assert pin(row['path'])==row
cp=OLD/(REL+'DungeonSwdForwardStepProbeV002.cpp');hp=OLD/(REL+'DungeonSwdForwardStepProbeV002.h');sp=OLD/'exact-seams-v002.json'
v=cp.read_bytes();assert pin(cp)['sha256']=='1610e9a3c1dec1836538c59161e8d9ac618ae24a9aaef25f6730ed105769fe8b'
edits=[
 ('capture-local-declaration',b'const double ReadStop=FPlatformTime::Seconds();',b'const double GPUReadStop=FPlatformTime::Seconds();'),
 ('capture-json-read-stop-value',b'O->SetNumberField(TEXT("read_stop_monotonic_s"),ReadStop);',b'O->SetNumberField(TEXT("read_stop_monotonic_s"),GPUReadStop);'),
 ('placement-local-key-declaration',b'const FString Key=W.RunGuid.ToString',b'const FString PlacementKey=W.RunGuid.ToString'),
 ('placement-key-lookup',b'PlacementKeys.IndexOfByKey(Key);',b'PlacementKeys.IndexOfByKey(PlacementKey);'),
 ('placement-key-insert',b'PlacementKeys.Add(Key);',b'PlacementKeys.Add(PlacementKey);')]
a=v;ops=[]
for label,before,after in edits:
 assert a.count(before)==1 and a.count(after)==0,(label,'non-exact occurrence');pos=a.index(before);line=a[:pos].count(b'\n')+1;a=a.replace(before,after,1);ops.append({'id':label,'line':line,'old_utf8':before.decode(),'new_utf8':after.decode(),'old_occurrences':1,'new_occurrences':1,'byte_offset_when_applied':pos})
inv=a
for _,before,after in reversed(edits):assert inv.count(after)==1;inv=inv.replace(after,before,1)
assert inv==v and len(a)-len(v)==33
np=rawwrite(REL+'DungeonSwdForwardStepProbeV002.cpp',a);nh=rawwrite(REL+'DungeonSwdForwardStepProbeV002.h',hp.read_bytes());ns=rawwrite('exact-seams-v002.json',sp.read_bytes())
assert pin(nh)['sha256']==pin(hp)['sha256'] and pin(ns)['sha256']==pin(sp)['sha256']
# Keep original proof member ReadStop and actual Key() method untouched.
assert b'Warm=0,Start=0,Stop=0,ReadStop=0' in a and b'void Key(FKey K,bool Down)' in a
assert b'ReadStop=FPlatformTime::Seconds();ReadComplete=' in a and b'Start>ReadStop' in a
assert b'TEXT("startup_readback_stop_monotonic_s"),ReadStop' in a
# Manual source-scope declaration inventory for same-name collisions in this proof.
# This is not a compiler/AST guarantee; actual UHT/Editor /we4458 remains Root.
proof=a[a.index(b'struct FDungeonSwdForwardStepProofV002 {'):a.index(b'void FDungeonSwdForwardStepProofDeleterV002::')].decode()
member_names=['Directory','Case','Failure','PreregFile','Prereg','Route','G','C','H','Inputs','Observations','Offsets','StartupTextures','PlacementRecords','PlacementKeys','PlacementValues','ExploratoryPilot','Audio','Loaded','Keys','PulseKey','ReleaseAt','NeutralUntil','Warm','Start','Stop','ReadStop','PhaseWall','AcceptedSampleTime','LockedSampleTime','Phase','Waypoint','Frames','ReadyBefore','ReadyAfter','Mask','Facing','StillFrames','PreviousPosition','Sword','SwordVersion','SwordObservedVersion','Light','LightSource','LightVersion','Owner','Room','Epoch','Restart','ActionId','Run','Accepted','LockedSnapshot','PrewarmRequested','PrewarmDone','AudioRequested','Capturing','Stopping','Stopped','ReadComplete','Claimed','FlowComplete','EIssued','KIssued','LockedCaptured','Need','Next','Key','CanPulse','Pulse','Move','Release','Scope','Gear','PlacementPoll','PlacementClassification','RuntimeInventory','Readback','StopNow','Observe','Finalize','Tick']
# Inspect local declarations after the first method starts. Types here are the actual
# simple local forms used by this source, not a general C++ shadow diagnostic tool.
body=proof[proof.index('bool Need('):];locals_found=re.findall(r'\b(?:const\s+)?(?:auto|double|float|int32|uint64|uint32|FString|FVector2D|FKey|JO|JV|FDungeonWeaponForwardStepPlacementV001)(?:\s*\*|\s*&)?\s+([A-Za-z_]\w*)\s*(?=[=;,(])',body)
method_headers={'PlacementClassification','PlacementPoll','RuntimeInventory'}
collisions=sorted((set(locals_found)&set(member_names))-method_headers);assert not collisions,collisions
write('exact-name-fix-ops-v003.json',{'schema':'observer-v002-local-name-only-fix-v003','source_original':pin(cp),'source_projected':pin(np),'ops':ops,'inverse_original_all_bytes_exact':True,'unchanged_header_original':pin(hp),'unchanged_header_projected':pin(nh),'unchanged_exact_seams_original':pin(sp),'unchanged_exact_seams_projected':pin(ns),'class_file_flag_version':'V002','new_Unreal_source_files_if_admitted':2})
write('mechanical-read-and-inverse-receipt-v003.json',{'schema':'observer-local-name-fix-read-inverse-v003','utc':datetime.now(timezone.utc).isoformat(),'old_observer_current81_freeze':pin(oldfreeze),'read_original_cpp':pin(cp),'read_original_header':pin(hp),'read_original_seams':pin(sp),'projected_cpp':pin(np),'projected_header':pin(nh),'projected_seams':pin(ns),'five_token_sites_changed':5,'local_identifiers_renamed':{'Capture lambda ReadStop':'GPUReadStop','PlacementPoll local Key':'PlacementKey'},'old_new_size_delta_bytes':33,'reverse_edits_all_original_bytes_exact':True,'header_all_bytes_unchanged':True,'seams_all_bytes_unchanged':True,'member_ReadStop_and_Key_method_unchanged':True,'same_name_local_declaration_inventory':{'method':'bounded regex declaration scan plus direct inspection of proof methods/lambda; not a C++ compiler claim','member_names_checked':member_names,'local_names_observed':sorted(set(locals_found)),'additional_observed_collisions':collisions},'actual_source_current_file_count_readonly':len([p for p in (ROOT/'UnrealGame/Source').rglob('*') if p.is_file()]),'actual_Source_Content_tools_E_status_ledger_modified':False,'UE_compiled':False,'native_executed':False})
write('HANDOFF-v003.md','''# V002 observer local name correction v003

NEW derivative only. Original v002/current81 freeze13ab5c9e..., Root compound v001 and actual Source/Content/tools/E/status/ledger untouched. Class, generated header, filenames and opt-in flag remain V002. Native observer Source growth remains2 files.

Use this directory's exact-seams-v002.json (byte-identical to v002) and projected/UnrealGame/Source/CodexDungeon/DungeonSwdForwardStepProbeV002.{cpp,h} for Root compound v002. The h is byte-identical. Only CPP5 token sites change: Capture lambda local ReadStop→GPUReadStop and its JSON value reference; PlacementPoll local Key→PlacementKey and its lookup/insert references. Proof member ReadStop, readback completion/audio timing, Key() input method, all serialized field keys and all other original bytes remain exact. Reversing only these substitutions recovers every original CPP byte, including CRLF, with a33-byte forward size increase.

The issue is source-confirmed same-name hiding under the project's known /we4458 setting. A bounded declaration inventory and direct inspection found no additional same-name proof local/member collision; this is not an exhaustive compiler guarantee. No UE/UHT/Editor compile or native pass claim. Root freshreview/build remains required.

Do not copy driver/checker/templates from this directory: none was duplicated. Continue the original immutable forward-step-native-observer-candidate-v002 Python entry points, actual81 prereg template and pilot/strict acceptance rules. This candidate only replaces the2 observer file inputs in Root's composition; JSON schema, fields, source-event witness logic and capture mechanisms are unchanged.

FinalAccepted=false, runtime_ready=false, actual_source_modified=false.
''')
deps=[pin(oldfreeze),pin(cp),pin(hp),pin(sp)];members=[pin(p) for p in sorted(H.rglob('*')) if p.is_file() and p.name!='candidate-freeze-v003.json']
for _ in range(2):
 for row in members+deps:assert pin(row['path'])==row
fp=write('candidate-freeze-v003.json',{'schema':'observer-local-name-only-fix-candidate-freeze-v003','members':members,'dependency_pins':deps,'verification_passes':2,'twoSHA_mismatches':0,'new_files':['UnrealGame/Source/CodexDungeon/DungeonSwdForwardStepProbeV002.cpp','UnrealGame/Source/CodexDungeon/DungeonSwdForwardStepProbeV002.h'],'new_Unreal_source_files_if_admitted':2,'opt_in_insert_operations':3,'source_original_observer_freeze':pin(oldfreeze),'exact_inverse_all_original_cpp_bytes':True,'header_and_seams_all_bytes_unchanged':True,'only_two_local_identifiers_five_sites_changed':True,'class_file_flag_version':'V002','actual_source_modified':False,'UE_compiled':False,'native_executed':False,'runtime_ready':False,'RootApproved':False,'FinalAccepted':False})
print(json.dumps({'freeze':pin(fp),'members':len(members),'deps':len(deps),'cpp':pin(np),'header':pin(nh),'seams':pin(ns),'sites':[(o['id'],o['line']) for o in ops],'inverse_exact':True,'additional_observed_shadow_collisions':collisions,'actual_source_untouched':True},ensure_ascii=False))
