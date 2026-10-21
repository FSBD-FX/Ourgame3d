from pathlib import Path
import ast,datetime,hashlib,json,sys
BASE=Path(__file__).resolve().parent;name='HeroAir-query-select-preparation-freeze-v001.json'
def pin(p):
    d=p.read_bytes();return {'path':p.relative_to(BASE).as_posix(),'bytes':len(d),'sha256':hashlib.sha256(d).hexdigest()}
if '--verify-only' in sys.argv:
    f=json.loads((BASE/name).read_text());assert all(pin(BASE/r['path'])==r for r in f['members']);print(json.dumps({'verified_members':len(f['members']),'freeze_sha256':hashlib.sha256((BASE/name).read_bytes()).hexdigest(),'written':False}));raise SystemExit
assert not (BASE/name).exists()
for p in BASE.glob('*.py'):ast.parse(p.read_text())
review=json.loads((BASE/'independent-query-select-review-v001.json').read_text())
for r in review['reviewed_files']:assert pin(BASE/r['path'])==r
paths=sorted(p for p in BASE.rglob('*') if p.is_file() and p.name!=name and '__pycache__' not in p.parts);first=[pin(p) for p in paths];second=[pin(p) for p in paths];assert first==second
f={'schema':'HeroAir-query-select-preparation-freeze-v001','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'candidate_only':True,'source49_pending':True,'atomic_plan_presenter_pending':True,'actual_source_written':False,'native_query_compiled_in_UE':False,'actual_select_cpp_host_cases':39,'host_cpp_failures':0,'actual_stage0_200G3R_compiled_manifest_sha256':'64d4eee9cca114ecd5161bf693d3091b55241370808ad2110c417984b8f5e877','independent_read_review_complete':True,'two_sha_passes_equal':True,'final_accepted':False,'members':first}
(BASE/name).write_text(json.dumps(f,indent=2)+'\n',encoding='utf-8');d=(BASE/name).read_bytes();print(json.dumps({'path':str(BASE/name),'bytes':len(d),'sha256':hashlib.sha256(d).hexdigest(),'members':len(first),'two_sha_passes_equal':True}))
