"""Root-only reviewed K8 source admission, preserving every original and failure."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json,re,subprocess
R=Path('F:/Ourgame');C=R/'source-assets/production/fairytale-sword-secondary-v001'
def need(b,s):
 if not b:raise ValueError(s)
def pin(p):
 p=Path(p);b=p.read_bytes();return dict(path=p.as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def check(row):
 p=Path(row['path']);p=p if p.is_absolute() else R/p;v=pin(p);need(v['bytes']==row['bytes'] and v['sha256']==row['sha256'],'pin differs '+str(p));return p
def write_new(p,b):
 p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('xb') as f:f.write(b)
def save_json(p,j):write_new(p,(json.dumps(j,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))
a=argparse.ArgumentParser();a.add_argument('--freeze',required=True,type=Path);a.add_argument('--freeze-sha',required=True);a.add_argument('--review',required=True,type=Path);a.add_argument('--review-sha',required=True);a.add_argument('--evidence',required=True,type=Path);n=a.parse_args()
need(n.freeze.resolve().is_relative_to(C) and pin(n.freeze)['sha256']==n.freeze_sha,'specific candidate freeze required')
need(n.review.resolve().is_relative_to(R/'.superpowers/sdd') and pin(n.review)['sha256']==n.review_sha,'specific independent approved review required')
review=n.review.read_text('utf-8-sig')
decisions=re.findall(r'^Decision:[ \t]*(.*?)[ \t]*$',review,re.MULTILINE)
need(decisions==['Approved'],'specific independent review must contain one explicit Decision: Approved line')
need(n.evidence.resolve().is_relative_to(R/'docs/production/first-batch-v2/evidence') and not n.evidence.exists() and n.evidence.parent.is_dir(),'fresh Root admission evidence required')
f=read(n.freeze)
for row in f['members']+f['dependency_pins']:check(row)
projection=n.freeze.parent/'source-projection-v001.json';need(projection.resolve() in {check(row).resolve() for row in f['members']},'frozen actual source projection required');j=read(projection)
need(j['schema']=='Root-K8-actual-import-backed-source-projection-v001' and j['source_count_before']==303 and j['proposed_source_count_after']==308 and j['actual_content_count']==1495,'actual K8 whole projection required')
need(j['all_existing_original_bytes_preserved'] is True and len(j['operations'])==18 and len(j['existing_files'])==7 and len(j['new_files'])==5,'18 inverse-exact inserts/7existing/5new required')
cm=read(check(j['predecessor_compiled_manifest']));existing={x['path']:x for x in j['existing_files']};new={x['path']:x for x in j['new_files']}
source_expected={x['path'] for x in cm['files'] if x['path'].startswith('UnrealGame/Source/')}
need(len(source_expected)==303 and {p.relative_to(R).as_posix() for p in (R/'UnrealGame/Source').rglob('*') if p.is_file()}==source_expected,'current Source303 membership differs')
for row in cm['files']:check(row)
v=read(check(j['actual_Content_verification']));need(v['verified'] is True and v['same_PID_exit0'] is True and v['added56_exact'] is True and v['actual_Production1495'] is True,'actual Content import verification required')
for row in v['saved_uasset_pins']:check(row)
production_expected={x['path'] for x in cm['files'] if x['path'].startswith('UnrealGame/Content/Production/')}|{check(x).relative_to(R).as_posix() for x in v['saved_uasset_pins']}
need(len(production_expected)==1495 and {p.relative_to(R).as_posix() for p in (R/'UnrealGame/Content/Production').rglob('*') if p.is_file()}==production_expected,'actual Production1495 closure differs')
payload={}
for path,x in existing.items():
 need(path in source_expected,'existing target outside current Source');before=check(x['before']).read_bytes();need((R/path).read_bytes()==before,'actual Source baseline differs '+path);payload[path]=check(x['after']).read_bytes()
for path,x in new.items():
 need(path.startswith('UnrealGame/Source/CodexDungeon/') and '..' not in Path(path).parts and not (R/path).exists(),'new Source target occupied or escaped');payload[path]=check(x['after']).read_bytes()
need(not set(existing)&set(new),'duplicate source targets')
ps=subprocess.run(['powershell','-NoProfile','-NonInteractive','-Command','@(Get-Process -Name UnrealEditor,UnrealEditor-Cmd,UnrealBuildTool -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id) | ConvertTo-Json -Compress'],capture_output=True,text=True,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0));need(ps.returncode==0 and ps.stdout.strip() in ('','[]'),'actual Source mutation requires no UE/UBT process')

# All immutable inputs and full current closure were verified before mutation.
n.evidence.mkdir();admitted=[];result=dict(schema='Root-K8-actual-source-admission-v001',utc=datetime.now(timezone.utc).isoformat(),candidate_freeze=pin(n.freeze),source_projection=pin(projection),independent_review=pin(n.review),predecessor_compiled_manifest=j['predecessor_compiled_manifest'],actual_Content_verification=j['actual_Content_verification'],source_before=303,source_after=None,production_files=1495,actual_Source_admitted=False,compiled=False,native_verified=False,FinalAccepted=False,files=admitted)
try:
 for path,x in existing.items():write_new(n.evidence/'before'/path,(R/path).read_bytes())
 save_json(n.evidence/'pre-admission-claim-v001.json',dict(candidate_freeze=pin(n.freeze),review=pin(n.review),old_Source_files=303,actual_Content_files=1495,originals_backed_up=7))
 for path,data in payload.items():
  target=R/path
  if path in new:write_new(target,data)
  else:
   need(target.read_bytes()==check(existing[path]['before']).read_bytes(),'source changed at mutation boundary '+path)
   with target.open('wb') as stream:stream.write(data)
  need(target.read_bytes()==data,'actual source write mismatch '+path);admitted.append(dict(path=path,actual=pin(target),new_file=path in new))
 for _ in range(2):
  actual={p.relative_to(R).as_posix() for p in (R/'UnrealGame/Source').rglob('*') if p.is_file()};need(actual==source_expected|set(new) and len(actual)==308,'actual Source308 membership differs')
  for path,data in payload.items():need((R/path).read_bytes()==data,'admitted source drift '+path)
  for row in cm['files']:
   if row['path'] not in existing:check(row)
  for row in v['saved_uasset_pins']:check(row)
 result.update(actual_Source_admitted=True,source_after=308,verification_passes=2,twoSHA_mismatches=0,old296_unrelated_Source_and_all203_test_sources_unchanged=True)
except Exception as error:
 result['failure']=repr(error);raise
finally:save_json(n.evidence/'actual-source-admission.json',result)
print(json.dumps(dict(receipt=pin(n.evidence/'actual-source-admission.json'),Source=308,Production=1495,compiled=False,native_verified=False),ensure_ascii=False))
