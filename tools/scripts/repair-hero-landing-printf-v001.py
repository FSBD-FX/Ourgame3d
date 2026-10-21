from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,shutil
R=Path('F:/Ourgame');P=R/'UnrealGame/Source/CodexDungeon/DungeonHeroLandingPriorityProbeV001.cpp';O=R/'docs/production/first-batch-v2/evidence/HeroLandingPriority-v143-v001/Root-Printf-literal-repair-v001'
def pin(p):
 p=Path(p).resolve();b=p.read_bytes();return dict(path=p.as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
before=pin(P);assert before['sha256']=='2a7094068fe3cf8d22e57baaa15ddbd361157ec14c1b8311f6aad3cba55f4393'
old=P.read_bytes();new=old
edits=[('Primary','T_Fairytale_LeatherPrimary1%s_%03d_v001','T_Fairytale_LeatherReady%s_%03d_v001','Parts[I],D.Frame'),('Armor','T_Fairytale_LeatherReady%s_%03d_v001','T_Fairytale_SwordReady%s_%03d_v001','Component,Frame'),('Armor','T_Fairytale_LeatherPrimary1%s_%03d_v001','T_Fairytale_SwordPrimary1%s_%03d_v001','Component,Frame')]
for condition,yes,no,args in edits:
 a=f'FString::Printf({condition}?TEXT("{yes}"):TEXT("{no}"),{args})'.encode()
 b=f'{condition}?FString::Printf(TEXT("{yes}"),{args}):FString::Printf(TEXT("{no}"),{args})'.encode()
 assert new.count(a)==1;new=new.replace(a,b,1)
assert not O.exists();O.mkdir(parents=True)
shutil.copy2(P,O/'before-DungeonHeroLandingPriorityProbeV001.cpp')
build=R/'UnrealGame/Saved/Bootstrap/last-build.json';failed=json.loads(build.read_text(encoding='utf-8-sig'));assert failed['ExitCode']!=0
log=Path(failed['Log']);assert 'Formatting string must be a literal TCHAR array' in log.read_text(encoding='utf-8-sig',errors='replace')
shutil.copy2(build,O/'failed-last-build.json');shutil.copy2(log,O/log.name)
P.write_bytes(new)
for n in range(2):assert P.read_bytes()==new
result=dict(schema='Root-hero-landing-Printf-literal-source-repair-v001',utc=datetime.now(timezone.utc).isoformat(),RootApproved=True,is_template=False,actual_applied=True,reason='Actual UE5.5 C2338 Printf template requires literal TCHAR array; move only three ternary choices outside literal Printf calls.',before=before,after=pin(P),failed_build=pin(O/'failed-last-build.json'),failed_log=pin(O/log.name),exact_three_literal_call_repairs=True,protocol_texture_paths_and_action_behavior_changed=False,actual_source_files=298,actual_production_files=1419,UE_compiled=False,FinalAccepted=False)
with (O/'actual-source-repair-admission.json').open('x',encoding='utf-8') as f:json.dump(result,f,ensure_ascii=False,indent=2)
print(json.dumps(result,ensure_ascii=False))
