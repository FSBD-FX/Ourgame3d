"""Candidate-only structural/pin checks. Never compiles UE or modifies actual Source."""
from pathlib import Path
import argparse,ast,hashlib,json,sys
C=Path(__file__).resolve().parent;ROOT=Path('F:/Ourgame')
def need(ok,why):
 if not ok:raise ValueError(why)
def pin(p):
 b=p.read_bytes();return dict(path=p.as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def apply(data,o):
 anchor=o['anchor'].encode();text=o['text'].encode();need(data.count(anchor)==1,'unique insertion anchor missing: '+o['target']);return data.replace(anchor,text+anchor if o['kind']=='insert_before' else anchor+text,1)
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--against-current',action='store_true');ns=ap.parse_args();seams=json.loads((C/'exact-seams-v001.json').read_text());results=[]
 try:
  for target in sorted({o['target'] for o in seams['operations']}):
   before=(C/'before'/Path(target).name).read_bytes();projected=before
   if ns.against_current:need((ROOT/target).read_bytes()==before,'current target changed, rebase required: '+target)
   for o in seams['operations']:
    if o['target']==target:projected=apply(projected,o)
   reverse=projected
   for o in reversed(seams['operations']):
    if o['target']==target:
     anchor=o['anchor'].encode();text=o['text'].encode();combo=text+anchor if o['kind']=='insert_before' else anchor+text;need(reverse.count(combo)==1,'reverse anchor ambiguous');reverse=reverse.replace(combo,anchor,1)
   need(reverse==before,'exact insert roundtrip changed old bytes');results.append(dict(target=target,insert_only_roundtrip=True))
  cpp=(C/'projected/UnrealGame/Source/CodexDungeon/DungeonSwdForwardStepProbeV001.cpp').read_text()
  for word in ['SetActorLocation','ApplyCombatHit','SetActorTickEnabled','bAIEnabled =','JumpHeight=','Health=','FApp::SetFixedTimeStep','GetHeroLocomotionPlayRequests'] :need(word not in cpp,'unexpected forcing or ring seam: '+word)
  for word in ['GetActionAudioState().Records','GetActionAudioPlayReceipts()','GetFairytaleSwordSecondaryDraw()','ForwardStep.Present','RuntimeUpdates','CommitResolvedWeaponRuntime']:
   if word=='CommitResolvedWeaponRuntime':need(word not in cpp,'observer must not commit runtime')
   else:need(word in cpp,'actual readback seam missing: '+word)
  for p in C.rglob('*.py'):ast.parse(p.read_text(encoding='utf-8'))
  need(seams['new_source_files_count']==2 and len(seams['new_files'])==2,'minimal +2 source admission required')
  freeze=C/'candidate-freeze-v001.json'
  if freeze.exists():
   f=json.loads(freeze.read_text());
   for row in f['members']+f['dependencies']:
    p=Path(row['path']);p=p if p.is_absolute() else C/p;got=pin(p);need(got['bytes']==row['bytes'] and got['sha256']==row['sha256'],'freeze pin mismatch: '+str(p))
  out=dict(passed=True,against_current=ns.against_current,exact_insert_operations=len(seams['operations']),new_Source_files=2,roundtrips=results,force_write_scan_passed=True,Python_AST=True,freeze_pins_verified=freeze.exists(),UE_compiled=False,native_ran=False,ready=False)
 except (ValueError,KeyError,OSError,SyntaxError) as e:out=dict(passed=False,reason=str(e));print(json.dumps(out,indent=2));sys.exit(3)
 print(json.dumps(out,indent=2))
