from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,difflib
HERE=Path(__file__).resolve().parent;ROOT=Path('F:/Ourgame');SOURCE=ROOT/'UnrealGame/Source/CodexDungeon';NAME='DungeonHeroLandingPriorityProbeV001.cpp'
CM=ROOT/'source-assets/production/backups/v145-HeroLocomotionAudio303-1425-203GREEN-v001/compiled-source-manifest.json';CMSHA='97d4d0290ce17ff2bb0c4a97b3c03d8921bb398c8d0eddef1505809eae77ebd5'
sha=lambda b:hashlib.sha256(b).hexdigest()
def write(p,value):
 with (HERE/p).open('x',encoding='utf-8',newline='\n') as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n')
assert sha(CM.read_bytes())==CMSHA
original=(SOURCE/NAME).read_bytes();nl='\r\n' if b'\r\n' in original else '\n';text=original.decode('utf-8');ops=[]
def insert(anchor,addition):
 global text
 a=anchor.replace('\n',nl);b=addition.replace('\n',nl)
 assert text.count(a)==1,anchor
 text=text.replace(a,b+a,1);ops.append({'before':anchor,'after':addition+anchor,'mode':'INSERT_ONLY'})
helper=(HERE/'fragments/portable-cursor.inc').read_text(encoding='utf-8')+'\n'+(HERE/'fragments/json-helpers.inc').read_text(encoding='utf-8')+'\n'
insert('namespace\n{\nusing JO=TSharedPtr<FJsonObject>;using JV=TSharedPtr<FJsonValue>;',helper)
state=(HERE/'fragments/state-and-observe-helper.inc').read_text(encoding='utf-8')
insert(' void Next(int32 P){Phase=P;',state)
insert('  O->SetObjectField(TEXT("action"),X);Observations.Add(MakeShared<FJsonValueObject>(O));','  O->SetObjectField(TEXT("hero_locomotion_audio"),ObserveHeroAudioRequests(*G,*P,Observations.Num(),Start+Offset));\n')
insert('  R->SetArrayField(TEXT("normal_inputs"),Inputs);','  R->SetObjectField(TEXT("hero_locomotion_audio"),FinalHeroAudioRequests());\n')
(HERE/'projected').mkdir();(HERE/'before').mkdir()
with (HERE/'before'/NAME).open('xb') as f:f.write(original)
result=text.encode('utf-8')
with (HERE/'projected'/NAME).open('xb') as f:f.write(result)
patch=''.join(difflib.unified_diff(original.decode('utf-8').replace('\r\n','\n').splitlines(True),text.replace('\r\n','\n').splitlines(True),fromfile='a/UnrealGame/Source/CodexDungeon/'+NAME,tofile='b/UnrealGame/Source/CodexDungeon/'+NAME))
with (HERE/'native-observation.patch').open('x',encoding='utf-8',newline='\n') as f:f.write(patch)
pins=[]
for name in [NAME,'DungeonHeroLandingPriorityProbeV001.h','DungeonHeroLocomotionAudioV001.h','DungeonHeroLocomotionAudioNativeV001.h','DungeonHeroLocomotionAudioNativeV001.cpp','DungeonCompletedGroundMotion.h']:
 b=(SOURCE/name).read_bytes();snapshot=HERE/'before'/name
 if not snapshot.exists():
  with snapshot.open('xb') as f:f.write(b)
 assert snapshot.read_bytes()==b
 pins.append({'historical_actual_path':str(SOURCE/name),'snapshot_relative_path':'before/'+name,'bytes':len(b),'sha256':sha(b)})
write('before-source-pins.json',{'base_compiled_source_manifest':str(CM),'base_compiled_source_manifest_sha256':CMSHA,'pins':pins})
write('exact-seams.json',{'status':'CANDIDATE_NOT_APPLIED','actual_source':str(SOURCE/NAME),'source_bytes':len(original),'source_sha256':sha(original),'line_ending':'CRLF' if nl=='\r\n' else 'LF','operations':ops,'projected_source':str(HERE/'projected'/NAME),'result_bytes':len(result),'result_sha256':sha(result),'actual_source_count_observed':sum(p.is_file() for p in SOURCE.parent.rglob('*')),'actual_production_file_count_observed':sum(p.is_file() for p in (ROOT/'UnrealGame/Content/Production').rglob('*')),'new_actual_source_files_proposed':0,'existing_source_files_modified_proposed':1})
print(json.dumps({'insertions':len(ops),'source_before_sha256':sha(original),'projected_sha256':sha(result),'actual_files_written':False}))
