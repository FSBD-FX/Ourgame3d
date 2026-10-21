from pathlib import Path
import hashlib,json,datetime,sys

BASE=Path(__file__).resolve().parent;name='HeroAir-Stage0-candidate-freeze-v001.json'
def pin(p):
    data=p.read_bytes();return {'path':p.relative_to(BASE).as_posix(),'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}
if '--verify-only' in sys.argv:
    f=json.loads((BASE/name).read_text());assert all(pin(BASE/r['path'])==r for r in f['members']);print(json.dumps({'verified_members':len(f['members']),'freeze_sha256':hashlib.sha256((BASE/name).read_bytes()).hexdigest(),'written':False}));raise SystemExit
assert not (BASE/name).exists()
rows=[]
for p in sorted((BASE/'existing-source').rglob('*')):
    if p.is_file():rows.append({'kind':'existing','candidate':p.relative_to(BASE).as_posix(),'actual':'UnrealGame/Source/CodexDungeon/'+p.name})
for p in sorted((BASE/'new-source').rglob('*')):
    if p.is_file():rows.append({'kind':'new','candidate':p.relative_to(BASE).as_posix(),'actual':'UnrealGame/Source/CodexDungeon/'+p.relative_to(BASE/'new-source').as_posix()})
assert len(rows)==8
(BASE/'stage0-admission-index-v001.json').write_text(json.dumps({'schema':'HeroAir-Stage0-admission-index-v001','before_source_files':283,'expected_after_source_files':288,'old_registered_tests':200,'expected_registered_tests':203,'files':rows},indent=2)+'\n',encoding='utf-8')
paths=sorted(p for p in BASE.rglob('*') if p.is_file() and p.name!=name and '__pycache__' not in p.parts)
first=[pin(p) for p in paths];second=[pin(p) for p in paths];assert first==second
f={'schema':'HeroAir-Stage0-candidate-freeze-v001','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'NEW candidate only; Root separately reviews/adopts/compiles/runs','before_compiled_manifest':'source-assets/production/backups/v141-GuardMove7-Observer200G-v003/compiled-source-manifest.json','before_compiled_manifest_sha256':'71efa450e6aea3d5107554ac524166c824ee253211452001662dad3facb62553','before_source_files':283,'before_production_files':1371,'before_old_registered_tests':200,'new_source_files':5,'existing_narrow_patch_files':3,'expected_after_source_files':288,'expected_registered_tests':203,'two_sha_passes_equal':True,'independent_Root_review':'pending external Root review; no approval fabricated','source_profile_pending':True,'native_tests_executed':False,'semantic_red_verified':False,'production_compiled':False,'actual_source_written':False,'members':first}
(BASE/name).write_text(json.dumps(f,indent=2)+'\n',encoding='utf-8');data=(BASE/name).read_bytes();print(json.dumps({'path':str(BASE/name),'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),'members':len(first),'two_sha_passes_equal':True}))
