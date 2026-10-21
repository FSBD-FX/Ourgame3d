from pathlib import Path
import argparse,hashlib,json,sys
BASE=Path(__file__).resolve().parent
ROOT=Path('F:/Ourgame')
def digest(p):
 b=p.read_bytes();return len(b),hashlib.sha256(b).hexdigest()
def pinned(p,r):
 assert p.is_file(),f'missing {p}'
 n,h=digest(p);assert n==r['bytes'] and h==r['sha256'],f'pin mismatch {p}'
def main():
 ap=argparse.ArgumentParser();g=ap.add_mutually_exclusive_group();g.add_argument('--validate-only',action='store_true');g.add_argument('--admit',action='store_true');args=ap.parse_args()
 freeze=json.loads((BASE/'HeroAir-full-production-candidate-freeze-v001.json').read_bytes())
 for r in freeze['members']:pinned(BASE/r['path'],r)
 source=json.loads((BASE/'source-preparation-binding-v001.json').read_bytes())
 for key in ['native_ready_freeze','data_inl','Root_source_import_approval']:
  r=source[key];pinned(Path(r['path']),r)
 retained=json.loads(Path(source['native_ready_freeze']['path']).read_bytes())
 for r in retained['members']:pinned(Path(r['path']),r)
 approval=json.loads(Path(source['Root_source_import_approval']['path']).read_bytes())
 assert approval['RootApproved'] is True and approval['limited_import_approved'] is True and approval['FinalAccepted'] is False
 pinned(Path(approval['source_closure']['path']),approval['source_closure'])
 before=json.loads((BASE/'before-Source292-pins-v001.json').read_bytes());pinned(Path(before['compiled_source_manifest']['path']),before['compiled_source_manifest'])
 actual=sorted(p.relative_to(ROOT).as_posix() for p in (ROOT/'UnrealGame/Source').rglob('*') if p.is_file());expected=sorted(r['path'] for r in before['files']);assert actual==expected,'actual Source count/path drift'
 for r in before['files']:pinned(ROOT/r['path'],r)
 index=json.loads((BASE/'full-production-admission-index-v001.json').read_bytes());assert len(index['files'])==7 and sum(r['kind']=='new' for r in index['files'])==2
 for r in index['files']:
  candidate=BASE/r['candidate'];pinned(candidate,{'bytes':r['after_bytes'],'sha256':r['after_sha256']});target=ROOT/r['actual']
  if r['kind']=='new':assert not target.exists(),f'new path occupied {target}'
  else:pinned(target,{'bytes':r['before_bytes'],'sha256':r['before_sha256']})
 if args.admit:
  for r in index['files']:(ROOT/r['actual']).write_bytes((BASE/r['candidate']).read_bytes())
  after=sum(p.is_file() for p in (ROOT/'UnrealGame/Source').rglob('*'));assert after==294
  print(json.dumps({'mode':'Root-explicit-admit','written':7,'source_files':after,'ue_compiled':False,'native_verified':False,'FinalAccepted':False}))
 else:print(json.dumps({'mode':'ValidateOnly','readonly':True,'source_before':292,'source_after_expected':294,'admission_files':7,'ue_compiled':False,'native_verified':False,'FinalAccepted':False}))
if __name__=='__main__':
 try:main()
 except Exception as e:print(str(e),file=sys.stderr);sys.exit(3)
