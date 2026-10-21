"""Build only local projected files; Root composes these exact seams with its other candidate."""
from pathlib import Path
import hashlib,json,difflib
HERE=Path(__file__).resolve().parent
assert not (HERE/'candidate-freeze-v001.json').exists(),'Frozen candidate cannot be regenerated'
sha=lambda b:hashlib.sha256(b).hexdigest()
read=lambda name:(HERE/'fragments'/name).read_text().replace('\r\n','\n')
dto=read('eligibility-and-dto.inc')
producer=read('post-commit-producer.inc')
specs={
 'DungeonActionAudioFeedback.h':[
  ('// Transient presentation facts only.',dto+'// Transient presentation facts only.'),
  ('    uint64 OperationId = 0, Revision = 0;','    uint64 OperationId = 0, Revision = 0;\n    FDungeonActionAudioForwardStepV001 ForwardStep;')],
 'DungeonWorldProjectiles.cpp':[
  ('            const auto Delta=SweepWeaponStep(Fighter,E.ForwardStep,E.AtTime);','            const auto AudioBefore=Fighter->GetGroundPosition();\n            const auto Delta=SweepWeaponStep(Fighter,E.ForwardStep,E.AtTime);'),
  ('            Fighter->SetActorLocation(FVector(End.X,End.Y,0));Fighter->SyncWeaponMuzzleTransform();\n','            Fighter->SetActorLocation(FVector(End.X,End.Y,0));Fighter->SyncWeaponMuzzleTransform();\n'+producer)],
 'DungeonHUD.cpp':[
  ('    if (auto Sound=LoadObject<USoundBase>(nullptr,TEXT("/Game/ThirdParty/Kenney/ImpactSounds/ImpactLight/SW_ImpactLight.SW_ImpactLight")))',
   '    if(auto Sound=LoadObject<USoundBase>(nullptr,TEXT("/Game/Production/HeroLocomotion/v001/Audio/SW_AUD_HERO_STEP_LIGHT_01_v001.SW_AUD_HERO_STEP_LIGHT_01_v001")))\n    {PreloadedSounds.Add(Sound);ActionAudioSounds.Add(TEXT("HERO_STEP_LIGHT_01"),Sound);}\n    if (auto Sound=LoadObject<USoundBase>(nullptr,TEXT("/Game/ThirdParty/Kenney/ImpactSounds/ImpactLight/SW_ImpactLight.SW_ImpactLight")))'),
  ('        const float Volume=Melee?.25f:Record.Cue==TEXT("XBW_RELOAD_INSERT_01")?.55f:.32f;',
   '        const bool HeroForwardStep=Record.Cue==TEXT("HERO_STEP_LIGHT_01");\n        const float Volume=(Melee||HeroForwardStep)?.25f:Record.Cue==TEXT("XBW_RELOAD_INSERT_01")?.55f:.32f;')]
}
files=[];patch=[]
for name,ops in specs.items():
 b=(HERE/'before'/name).read_bytes();nl='\r\n' if b'\r\n' in b else '\n';text=b.decode()
 operations=[]
 for old,new in ops:
  a=old.replace('\n',nl);z=new.replace('\n',nl);assert text.count(a)==1,(name,old,text.count(a));text=text.replace(a,z,1)
  operations.append(dict(before=old,after=new))
 after=text.encode();out=HERE/'projected'/name;out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(after)
 files.append(dict(name=name,before='before/'+name,projected='projected/'+name,before_bytes=len(b),before_sha256=sha(b),after_bytes=len(after),after_sha256=sha(after),line_ending='CRLF' if nl=='\r\n' else 'LF',operations=operations))
 patch.extend(difflib.unified_diff(b.decode().splitlines(True),text.splitlines(True),fromfile='before/'+name,tofile='projected/'+name))
(HERE/'exact-seams.json').write_text(json.dumps(dict(schema='hero-swd-forward-step-audio-exact-seams-v001',status='UNAPPLIED_CANDIDATE',files=files,actual_project_writes=0,UE_runs=0),indent=2)+'\n',encoding='utf-8')
(HERE/'forward-step-audio-v001.patch').write_bytes(''.join(patch).encode())
print(json.dumps(dict(files=[{k:r[k] for k in ('name','before_bytes','before_sha256','after_bytes','after_sha256')} for r in files],actual_project_writes=0,UE_runs=0)))
