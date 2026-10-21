from pathlib import Path
import hashlib,json,shutil
R=Path('F:/Ourgame');B=R/'source-assets/production/fairytale-armor-sword-primary2-runtime-v001'
D=B/'source-draft-v001';E=R/'docs/production/first-batch-v2/evidence/armor-primary2-source-admission-v001'
assert not E.exists();E.mkdir(parents=True)
def d(p):
 b=p.read_bytes();return dict(path=p.as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def new(p,v):
 assert not p.exists();p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
f=D/'draft-freeze-v001.json';v=json.loads(f.read_text())
assert d(f)['sha256']=='b1bee956dadbc1b39b1de8e6abc8ae123ed465c0adbc060438e8e7d4376bde73'
for x in v['files']:assert d(Path(x['path']))==x
for x in v['source_before']:assert d(Path(x['path']))==x
for name in ['DungeonHUD.cpp','DungeonFairytaleSwordPresentation.cpp','DungeonFairytaleSwordProbe.cpp']:
 p=R/'UnrealGame/Source/CodexDungeon'/name;shutil.copy2(p,E/'before'/name) if (E/'before').exists() else ((E/'before').mkdir(),shutil.copy2(p,E/'before'/name))
before=[d(R/'UnrealGame/Source/CodexDungeon'/n) for n in ['DungeonHUD.cpp','DungeonFairytaleSwordPresentation.cpp','DungeonFairytaleSwordProbe.cpp']]
inline=R/'UnrealGame/Source/CodexDungeon/DungeonFairytaleSwordPrimary2ArmorV001.inl';assert not inline.exists()
for p in (D/'candidate-source').iterdir():
 assert p.name in ['DungeonHUD.cpp','DungeonFairytaleSwordPresentation.cpp','DungeonFairytaleSwordPrimary2ArmorV001.inl']
 target=R/'UnrealGame/Source/CodexDungeon'/p.name;shutil.copy2(p,target);assert target.read_bytes()==p.read_bytes()
probe=R/'UnrealGame/Source/CodexDungeon/DungeonFairytaleSwordProbe.cpp';raw=probe.read_bytes();s=raw.decode('utf-8');nl='\r\n' if '\r\n' in s else '\n'
old='    const bool Second=FParse::Param(FCommandLine::Get(),TEXT("DungeonFairytaleSwordPrimary2Preview"));'
assert s.count(old)==2
s=s.replace(old,old[:-1]+nl+'        ||FParse::Param(FCommandLine::Get(),TEXT("DungeonFairytaleSwordPrimary2ArmorPreview"));',1)
s=s.replace(old,'    const bool Primary2ArmorTrial=FParse::Param(FCommandLine::Get(),TEXT("DungeonFairytaleSwordPrimary2ArmorPreview"));'+nl+old[:-1]+' || Primary2ArmorTrial;',1)
scope='    R->SetStringField(TEXT("scope"),Second'
assert s.count(scope)==1
s=s.replace(scope,'    R->SetStringField(TEXT("scope"),Primary2ArmorTrial'+nl+'        ?TEXT("Native171 body with opt-in42 Primary2 body/armor-layer textures (7x6), including integer-registered native172/173/174 armor, and currentV003 independent-sword markers under real paired J/kernelStage1. Existing Ready/Primary1 trial retained. No hit target, complete armor states/equipment identity, three-stage/fullmotion, thumb/footlock or audio acceptance")'+nl+'        :Second')
probe.write_bytes(s.encode('utf-8'));after=[d(R/'UnrealGame/Source/CodexDungeon'/n) for n in ['DungeonHUD.cpp','DungeonFairytaleSwordPresentation.cpp','DungeonFairytaleSwordProbe.cpp','DungeonFairytaleSwordPrimary2ArmorV001.inl']]
new(E/'root-admission-v001.json',dict(before=before,after=after,draft_freeze=d(f),scope='3 presentation files plus Probe newflag/scope only, old input times and kernel unchanged',compiled=False,formal_complete_units=0))
pp=R/'docs/production/first-batch-v2/progress.json';shutil.copy2(pp,E/'progress-before.json');status=json.loads(pp.read_text(encoding='utf-8-sig'))
status.update(ue_current_working_source_compiled=False,ue_current_working_source_verified=False,current_source_uncompiled_changes='P2Armor3presentation+Probe flag/scope admitted; no kernel or old time changes',current_task='EV048 actual42 P2armor textures saved old995unchanged/Production1037; Source4file trial admitted, actual compiler/full138/dual native armor fit next; formal0/15active')
status['fairytale_armor_primary2_current_v001'].update(state='42Texture native imported saved; Source trial admitted uncompiled',imported=True,production_packages_total=1037,registration_retention='E222')
pp.write_text(json.dumps(status,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(before=before,after=after,compiled=False),ensure_ascii=False))
