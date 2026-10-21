"""Small shared file/report gates for this one Root Hurt1286 checkpoint; no UE launch."""
from pathlib import Path
import hashlib,json
R=Path('F:/Ourgame').resolve();C=Path(__file__).resolve().parent.parent
EXT=R/'source-assets/production/fairytale-guard-v001/guard-known44-profile-extension-candidate-v004'
HURT_FLAG='DungeonFairytaleSwordHurtPreview'
HURT_TESTS=tuple('CodexDungeon.Content.FairytaleSwordHurtV001.'+n for n in [
 'ActualPoiseBreakFourPhasesAndExclusions','RealBindingSource32MirrorAndAtomicRejection','RealCodecPauseContinueKeepsAgeAndEquipment'])
HURT_SOURCES=tuple('UnrealGame/Source/CodexDungeon/'+n for n in [
 'DungeonFighter.h','DungeonFighter.cpp','DungeonHUD.h','DungeonHUD.cpp','DungeonFairytaleSwordPresentation.cpp','DungeonFairytaleSwordDrawState.h',
 'DungeonFairytaleSwordHurtPlan.cpp','DungeonFairytaleSwordHurtPlan.h','DungeonFairytaleSwordHurtProfile.cpp','DungeonFairytaleSwordHurtProfile.h','DungeonHurtPresentation.h',
 'DungeonFairytaleSwordHurtDrawState.h','DungeonFairytaleSwordHurtTextures.inl','DungeonFairytaleSwordHurtPresentation.cpp','Tests/DungeonFairytaleSwordHurtV001Tests.cpp'])
def need(v,why):
 if not v:raise ValueError(why)
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def resolve(v):
 p=Path(v);p=(p if p.is_absolute() else R/p).resolve();need(p.is_relative_to(R),'Path must stay in project');return p
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def pin(p,absolute=False):
 p=Path(p).resolve();need(p.is_relative_to(R) and p.is_file(),'Missing project file: '+str(p));return dict(path=p.as_posix() if absolute else p.relative_to(R).as_posix(),bytes=p.stat().st_size,sha256=sha(p))
def check(x):
 need(type(x) is dict and set(x)=={'path','bytes','sha256'},'Exact real pin required');p=resolve(x['path']);q=pin(p);need(type(x['bytes']) is int and q['bytes']==x['bytes'] and q['sha256']==x['sha256'],'Pin changed: '+str(p));return p
def rows_of_freeze(p):
 p=Path(p).resolve();result={p}
 for row in read(p)['files']:
  raw=Path(row['path']);q=raw if raw.is_absolute() else p.parent/raw
  if not q.is_file() and not raw.is_absolute():q=R/raw
  q=q.resolve();need(q.is_relative_to(R),'Frozen dependency escapes project');need(q.is_file() and q.stat().st_size==row['bytes'] and sha(q)==row['sha256'],'Frozen candidate changed: '+str(q));result.add(q)
 return result
def own_freeze():
 f=C/'checkpoint-tooling-freeze-v001.json';rows_of_freeze(f);return f
def strict_suite(s):
 need(type(s['succeeded']) is int and s['succeeded']==187 and all(type(s[k]) is int and s[k]==0 for k in ['failed','succeededWithWarnings','notRun','inProcess']),'Full actual187 strict GREEN required')
 ts=s['tests'];names=[x['fullTestPath'] for x in ts];need(len(ts)==len(set(names))==187,'Actual187 registry must be unique')
 for x in ts:
  need(x['state']=='Success' and type(x['errors']) is int and x['errors']==0 and type(x['warnings']) is int and x['warnings']==0,'Every native test must be strict GREEN')
  need(not any(e.get('event',{}).get('type') in ['Error','Warning'] for e in x.get('entries',[])),'Hidden native Error/Warning entry')
 for n in HURT_TESTS:need(names.count(n)==1,'Exact actual Hurt target missing: '+n)
 return names
def write(p,v):
 p=Path(p);need(not p.exists(),'Never overwrite old output: '+str(p));p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x',encoding='utf-8') as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n')
