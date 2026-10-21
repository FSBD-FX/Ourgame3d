from pathlib import Path
import hashlib,json,difflib
HERE=Path(__file__).resolve().parent;NAME='DungeonHeroLandingPriorityProbeV001.cpp';sha=lambda b:hashlib.sha256(b).hexdigest();SRC=Path('F:/Ourgame/UnrealGame/Source/CodexDungeon')/NAME
e73=(HERE/'before'/NAME).read_bytes();v1=(HERE/'before/v001-projected-DungeonHeroLandingPriorityProbeV001.cpp').read_bytes();assert sha(e73)=='e73bb9df5e3b95d1dcf16152e945f0efeb90ffc4c522a89b3c6a2d06cc71a422';assert sha(v1)=='a4782db14de4f94979681d8f909f26dd46e33ebd94ea86db2beed558ea1a41d7';assert SRC.read_bytes()==e73
nl='\r\n' if b'\r\n' in e73 else '\n';text=v1.decode('utf-8');delta=[]
def insert(anchor,added,fragment):
 global text
 a=anchor.replace('\n',nl);b=added.replace('\n',nl);assert text.count(a)==1;text=text.replace(a,b+a,1);delta.append({'before':anchor,'after':added+anchor,'fragment':fragment,'mode':'INSERT_ONLY'})
insert('#include "Engine/Texture2D.h"','#include "UObject/StrongObjectPtr.h"\n','inline readonly dependency include')
legacy=(HERE/'fragments/legacy-preload.inc').read_text(encoding='utf-8');insert('  IFileManager::Get().MakeDirectory(*(Directory/TEXT("texture-readback")),false);',legacy,'fragments/legacy-preload.inc')
result=text.encode('utf-8');(HERE/'projected'/NAME).write_bytes(result);(HERE/'tests/legacy-preload-under-test.inc').write_text(legacy,encoding='utf-8')
base=json.loads((HERE/'before/v001-exact-seams.json').read_text(encoding='utf-8'));ops=base['operations']+delta
manifest={'status':'V002_CANDIDATE_NOT_APPLIED','historical_actual_source':str(SRC),'before_snapshot':'before/'+NAME,'source_bytes':len(e73),'source_sha256':sha(e73),'projected_source':'projected/'+NAME,'result_bytes':len(result),'result_sha256':sha(result),'line_ending':'CRLF' if nl=='\r\n' else 'LF','operations':ops,'new_actual_source_files':0,'existing_actual_source_files_modified_proposed':1,'dependency_v001_observer_freeze_sha256':'0fcc6eb38e6675c48a6fa66811b371c3443e2570ce19ef6d7ddefaaf5b81c35e'}
(HERE/'exact-seams.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(HERE/'v001-to-v002-exact-delta.json').write_text(json.dumps({'before_snapshot':'before/v001-projected-'+NAME,'before_sha256':sha(v1),'after_projected':'projected/'+NAME,'after_sha256':sha(result),'line_ending':manifest['line_ending'],'operations':delta,'scope':'Only old14 explicit preload/strongref/renderflush and dependency header'},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
for filename,before in [('native-observation.patch',e73),('v001-to-v002.patch',v1)]:
 patch=''.join(difflib.unified_diff(before.decode('utf-8').replace('\r\n','\n').splitlines(True),text.replace('\r\n','\n').splitlines(True),fromfile='a/UnrealGame/Source/CodexDungeon/'+NAME,tofile='b/UnrealGame/Source/CodexDungeon/'+NAME));(HERE/filename).write_text(patch,encoding='utf-8')
print(json.dumps({'full_e73_insertions':len(ops),'delta_v001_insertions':len(delta),'final_bytes':len(result),'final_sha256':sha(result),'actual_source_written':False}))
