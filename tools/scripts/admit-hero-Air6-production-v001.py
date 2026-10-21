"""Root admission of the reviewed seven-source Air candidate after actual48 import."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json,shutil,subprocess,sys
R=Path('F:/Ourgame')
C=R/'source-assets/production/fairytale-hero-air-v001/production-candidate-v001/full-production-v001'
O=R/'docs/production/first-batch-v2/evidence/HeroAir6-v142-v001/Root-production-admission-v001'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def pin(p):
 b=p.read_bytes();return dict(path=p.as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def need(v,why):
 if not v:raise ValueError(why)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--import-receipt',required=True);ap.add_argument('--import-verification',required=True);a=ap.parse_args()
 receipt=Path(a.import_receipt).resolve();verification=Path(a.import_verification).resolve();n=read(receipt);v=read(verification)
 need(n['success'] is True and n['actual_new_saved']==48 and n['actual_total']==1419,'Actual native48 import success required')
 need(v['success'] is True and v['native_receipt']==pin(receipt) and v['hash_mismatches']==0 and v['verification_passes']==2,'Independent actual saved-byte verification required')
 need(n['old1371_unchanged'] is True and v['manifest']==n['manifest'],'Exact import/verification pair required')
 barriers=n['texture_compilation_barriers'];need(len(barriers)==97 and all(x['command']=='Editor.AsyncTextureCompilationFinishAll' and x['command_requested'] is True and x['after_dimensions']==[512,512] for x in barriers),'Actual old1+new96 strict512 compilation readbacks required')
 need(sum(p.is_file() for p in (R/'UnrealGame/Content/Production').rglob('*'))==1419,'Actual Production count drift')
 freeze=C/'HeroAir-full-production-candidate-freeze-v001.json';need(pin(freeze)['sha256']=='7197705254448e380d643edbef4b31fe3adf4f95a7b3c9d389ad574adea532e6','Reviewed candidate freeze changed')
 ix=read(C/'full-production-admission-index-v001.json')
 need(not O.exists(),'Fresh Root receipt directory required');O.mkdir(parents=True)
 for row in ix['files']:
  if row['kind']=='existing':
   p=R/row['actual'];dst=O/'before'/p.name;dst.parent.mkdir(exist_ok=True);shutil.copy2(p,dst);need(pin(dst)['sha256']==row['before_sha256'],'Preserved before copy differs')
 result=subprocess.run([sys.executable,'-B','-X','utf8',str(C/'root-admit-full-production-v001.py'),'--admit'],cwd=R,capture_output=True,text=True,encoding='utf-8')
 with (O/'actual-admit-output.txt').open('x',encoding='utf-8') as f:f.write(result.stdout+result.stderr)
 need(result.returncode==0,'Source admission failed; preserve all partial results')
 need(sum(p.is_file() for p in (R/'UnrealGame/Source').rglob('*'))==294,'Actual Source count differs')
 after=[]
 for repeat in range(2):
  for row in ix['files']:
   p=R/row['actual'];x=pin(p);need((x['bytes'],x['sha256'])==(row['after_bytes'],row['after_sha256']),'Admitted source differs '+row['actual'])
   if repeat==0:after.append(x)
 report=dict(schema='Root-HeroAir6-production-source-admission-v001',utc=datetime.now(timezone.utc).isoformat(),candidate_freeze=pin(freeze),native_import_receipt=pin(receipt),independent_saved_byte_verification=pin(verification),actual_source_files=294,actual_production_files=1419,admission_files=after,verification_passes=2,source_byte_mismatches=0,review_scope='Actual source prep/Profile/Query/Select/Plan/Presenter and HUD opt-in seam; no completed runtime or art acceptance',ue_compiled=False,native_new_air_reviewed=False,FinalAccepted=False)
 out=O/'actual-source-admission.json'
 with out.open('x',encoding='utf-8') as f:json.dump(report,f,ensure_ascii=False,indent=2)
 print(json.dumps(pin(out)))
if __name__=='__main__':main()
