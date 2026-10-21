"""Create one-source exact proposal; writes only this new candidate."""
from pathlib import Path
import difflib,hashlib,json
HERE=Path(__file__).resolve().parent;NAME='DungeonHeroLandingPriorityProbeV001.cpp'
sha=lambda b:hashlib.sha256(b).hexdigest()
before=(HERE/'before'/NAME).read_bytes();assert sha(before)=='30b1db6503f8641bcac0165cfc134ae7e841b96f3f23b8d68b912a90696a2205'
text=before.decode('utf-8');nl='\r\n' if b'\r\n' in before else '\n';ops=[]
def fragment(name):return (HERE/'fragments'/name).read_text(encoding='utf-8').replace('\r\n','\n')
def change(old,new):
 global text
 a=old.replace('\n',nl);b=new.replace('\n',nl);assert text.count(a)==1,old
 text=text.replace(a,b,1);ops.append(dict(before=old,after=new))
change('#include "TextureResource.h"','#include "TextureResource.h"\n#if WITH_EDITOR\n#include "TextureCompiler.h"\n#endif')
change('JO DodgeDraw(const FDungeonFairytaleSwordDodgeDraw& D)',fragment('residency-status-helper.inc')+'JO DodgeDraw(const FDungeonFairytaleSwordDodgeDraw& D)')
change(' TArray<JV> HeroAudioCapturedRequests;',' TArray<JV> Bridge258LegacyResidencyBefore,Bridge258LegacyResidencyAfter;\n bool Bridge258LegacyFinishRequested=false;int32 Bridge258LegacyFinishTargetCount=0;\n TArray<JV> HeroAudioCapturedRequests;')
loop='   for(int32 Frame=0;Frame<2;++Frame)for(const TCHAR* Component:{TEXT("BodyRest"),TEXT("ShoulderFar"),TEXT("Chest"),TEXT("NearArmWithoutHand"),TEXT("ShoulderNear"),TEXT("HelmetForeground"),TEXT("NearHand")})'
change(loop,'   TArray<FString> Bridge258LegacyRequestedPaths;\n'+loop)
load='    Bridge258LegacyReadbackRefs.Emplace(LoadObject<UTexture2D>(nullptr,*Path));'
change(load,load+'\n    Bridge258LegacyRequestedPaths.Add(Path);')
flush='   FlushRenderingCommands(); // Before the original strict FindObject/RHI/pending checks, before audio/input.\n'
change(flush,fragment('before-finish.inc')+flush+fragment('after-flush.inc'))
final='  R->SetObjectField(TEXT("hero_locomotion_audio"),FinalHeroAudioRequests());'
addition='''  auto LegacyResidency=MakeShared<FJsonObject>();LegacyResidency->SetStringField(TEXT("schema"),TEXT("request258-old14-residency-diagnostics-v003"));
  LegacyResidency->SetBoolField(TEXT("requested"),Bridge258ObservationEnabled()&&Action==TEXT("J"));LegacyResidency->SetBoolField(TEXT("finish_compilation_requested"),Bridge258LegacyFinishRequested);LegacyResidency->SetNumberField(TEXT("finish_target_count"),Bridge258LegacyFinishTargetCount);
  LegacyResidency->SetArrayField(TEXT("before_finish"),Bridge258LegacyResidencyBefore);LegacyResidency->SetArrayField(TEXT("after_finish_and_render_flush"),Bridge258LegacyResidencyAfter);
  LegacyResidency->SetBoolField(TEXT("diagnostics_replace_strict_GPU_source_capture"),false);R->SetObjectField(TEXT("request258_primary1_legacy_residency"),LegacyResidency);
'''
change(final,addition+final)
after=text.encode('utf-8');(HERE/'projected'/NAME).write_bytes(after)
m=dict(schema='request258-old14-residency-exact-seams-v003',status='PROPOSAL_NOT_APPLIED',actual_source='F:/Ourgame/UnrealGame/Source/CodexDungeon/'+NAME,local_before='before/'+NAME,projected_source='projected/'+NAME,source_bytes=len(before),source_sha256=sha(before),result_bytes=len(after),result_sha256=sha(after),line_ending='CRLF' if nl=='\r\n' else 'LF',operations=ops,actual_source_files=303,actual_production_files=1439,actual_source_written=False,UE_run=False)
with (HERE/'exact-seams.json').open('x',encoding='utf-8') as f:json.dump(m,f,ensure_ascii=False,indent=2);f.write('\n')
with (HERE/'residency-fix-v003.patch').open('x',encoding='utf-8') as f:f.writelines(difflib.unified_diff(before.decode().splitlines(True),text.splitlines(True),fromfile='before/'+NAME,tofile='projected/'+NAME))
print(json.dumps({k:m[k] for k in ('source_bytes','source_sha256','result_bytes','result_sha256','actual_source_written','UE_run')}))
