from pathlib import Path
import json,hashlib,shutil,os,datetime
R=Path('F:/Ourgame');D=R/'docs/production/first-batch-v2';B=R/'source-assets/production/fairytale-lgt-readability-v003/primary1-native-source-v002';F=B/'source-freeze-v002.json';O=D/'evidence/leather-primary1-v001/root-source-admission-v002'
def pin(p):
 b=p.read_bytes();return dict(path=p.as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
assert not O.exists();v=read(F)
for r in v['inputs']+v['files']:assert pin(Path(r['path']))==r
guard=D/'evidence/stone-guard-restore-v001/root-production-admission-v001/admission.json'
assert guard.is_file()
before={p:pin(p) for p in (R/'UnrealGame/Source').rglob('*') if p.is_file()};O.mkdir(parents=True)
names=['DungeonFairytaleSwordPresentation.cpp','DungeonFairytaleEquipmentBoundProbe.h','DungeonFairytaleEquipmentBoundProbe.cpp'];admitted=[]
for name in names:
 p=R/'UnrealGame/Source/CodexDungeon'/name;c=B/name;q=O/'before'/p.relative_to(R);q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q);assert p.read_bytes()==q.read_bytes();shutil.copy2(c,p);os.utime(p,None);assert p.read_bytes()==c.read_bytes();admitted.append(pin(p))
assert {p for p,d in before.items() if pin(p)!=d}=={R/'UnrealGame/Source/CodexDungeon'/n for n in names}
write(O/'admission.json',dict(freeze=pin(F),admitted=admitted,all_other_Source_unchanged=True,default_preview_flags_unchanged=True,conditional_new_art_dependencies_pending=True,actual_art_import=None,actual_native_trial=None,compiled=False,full_unit_complete=False))
p=D/'progress.json';x=read(p);x.update(ue_current_working_source_compiled=False,ue_current_working_source_verified=False,current_source_uncompiled_changes='Guard Restore production + optional leatherPrimary1 renderer/probe admitted. Texture18 fit/import remains pending; actual compile/target3/full157 and native proofs pending.',actual_registered_test_count_current=157,updated_utc=datetime.datetime.now(datetime.timezone.utc).isoformat());x['leather_primary1_v001']=dict(source_admission=pin(O/'admission.json'),art_import=None,actual_native_trial=None,full_animation_accepted=False,formal_complete_units=0);write(p,x)
print(json.dumps(dict(source_three_admitted=True,all_other_Source_unchanged=True,new_art_dependencies_pending=True,default_preview_unchanged=True),ensure_ascii=False))
