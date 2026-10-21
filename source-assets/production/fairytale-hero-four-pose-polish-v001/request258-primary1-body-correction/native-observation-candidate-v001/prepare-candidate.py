from pathlib import Path
import hashlib,json,difflib
HERE=Path(__file__).resolve().parent;sha=lambda b:hashlib.sha256(b).hexdigest();NAME='DungeonHeroLandingPriorityProbeV001.cpp';SRC=Path('F:/Ourgame/UnrealGame/Source/CodexDungeon')/NAME
original=(HERE/'before'/NAME).read_bytes();assert sha(original)=='e73bb9df5e3b95d1dcf16152e945f0efeb90ffc4c522a89b3c6a2d06cc71a422';assert SRC.read_bytes()==original
nl='\r\n' if b'\r\n' in original else '\n';text=original.decode('utf-8');ops=[]
def insert(anchor,fragment):
 global text
 before=anchor.replace('\n',nl);added=(HERE/'fragments'/fragment).read_text(encoding='utf-8').replace('\n',nl);assert text.count(before)==1,(anchor,text.count(before));text=text.replace(before,added+before,1);ops.append({'before':anchor,'after':added.replace(nl,'\n')+anchor,'fragment':'fragments/'+fragment,'mode':'INSERT_ONLY'})
insert('bool Brown(const FDungeonFairytaleSwordDraw& D,bool Primary)','helper.inc')
insert(' const TCHAR* Parts[]={TEXT("ShoulderFar"),TEXT("Chest"),TEXT("ShoulderNear")};const int32 Slots[]={1,2,4};','brown-branch.inc')
insert('  FlushRenderingCommands();StartupReadbackStop=FPlatformTime::Seconds();StartupReadbackComplete=Need(Unique.Num()==ExpectedReadbacks','readback.inc')
insert('  R->SetObjectField(TEXT("hero_locomotion_audio"),FinalHeroAudioRequests());','report-metadata.inc')
result=text.encode('utf-8');(HERE/'projected'/NAME).write_bytes(result)
patch=''.join(difflib.unified_diff(original.decode('utf-8').replace('\r\n','\n').splitlines(True),text.replace('\r\n','\n').splitlines(True),fromfile='a/UnrealGame/Source/CodexDungeon/'+NAME,tofile='b/UnrealGame/Source/CodexDungeon/'+NAME));(HERE/'native-observation.patch').write_text(patch,encoding='utf-8')
manifest={'status':'CANDIDATE_NOT_APPLIED','historical_actual_source':str(SRC),'before_snapshot':'before/'+NAME,'source_bytes':len(original),'source_sha256':sha(original),'projected_source':'projected/'+NAME,'result_bytes':len(result),'result_sha256':sha(result),'line_ending':'CRLF' if nl=='\r\n' else 'LF','operations':ops,'new_actual_source_files':0,'existing_actual_source_files_modified_proposed':1,'new_texture_imports_performed':0}
(HERE/'exact-seams.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
after=text.replace('\r\n','\n');brown=after[after.index('bool Brown('):after.index('JO DodgeDraw(')];(HERE/'tests/brown-under-test.inc').write_text(brown,encoding='utf-8');(HERE/'tests/readback-under-test.inc').write_text((HERE/'fragments/readback.inc').read_text(encoding='utf-8'),encoding='utf-8')
print(json.dumps({'insertions':len(ops),'projected_bytes':len(result),'projected_sha256':sha(result),'actual_source_written':False,'old_audio_telemetry_preserved':True}))
