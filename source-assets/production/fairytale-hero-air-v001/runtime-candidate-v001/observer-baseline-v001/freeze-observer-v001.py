from pathlib import Path
import ast,hashlib,json,datetime,sys
BASE=Path(__file__).resolve().parent;name='HeroAir-baseline-observer-candidate-freeze-v001.json'
def pin(p):
    d=p.read_bytes();return {'path':p.relative_to(BASE).as_posix(),'bytes':len(d),'sha256':hashlib.sha256(d).hexdigest()}
if '--verify-only' in sys.argv:
    f=json.loads((BASE/name).read_text());assert all(pin(BASE/r['path'])==r for r in f['members']);print(json.dumps({'verified_members':len(f['members']),'freeze_sha256':hashlib.sha256((BASE/name).read_bytes()).hexdigest(),'written':False}));raise SystemExit
assert not (BASE/name).exists()
for p in BASE.glob('*.py'):ast.parse(p.read_text())
rows=[{'kind':'existing','candidate':'existing-source/DungeonHUD.cpp','actual':'UnrealGame/Source/CodexDungeon/DungeonHUD.cpp'}]
for p in sorted((BASE/'new-source').glob('*')):rows.append({'kind':'new','candidate':p.relative_to(BASE).as_posix(),'actual':'UnrealGame/Source/CodexDungeon/'+p.name})
(BASE/'observer-admission-index-v001.json').write_text(json.dumps({'schema':'HeroAir-baseline-observer-admission-index-v001','before_source_files':290,'after_source_files':292,'registered_tests':203,'files':rows},indent=2)+'\n',encoding='utf-8')
paths=sorted(p for p in BASE.rglob('*') if p.is_file() and p.name!=name and '__pycache__' not in p.parts);first=[pin(p) for p in paths];second=[pin(p) for p in paths];assert first==second
f={'schema':'HeroAir-baseline-observer-candidate-freeze-v001','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'candidate_only':True,'actual_source_written':False,'before_source_files':290,'after_root_admission_source_files':292,'registered_tests':203,'stage0_source_freeze_sha256':'37513295d00ee57f1726260c0da10a296e378962cb1d4cbe21bb6e3010d42c2a','audio_helper_freeze_sha256':'91e1a74f78dcf1b712d121930da8e08e3543254d4227d43c2b774df730089c3e','new_sources':2,'existing_narrow_patches':1,'two_sha_passes_equal':True,'independent_read_review':'Probe/audio/cleanup/no-replace reviewed, four findings corrected, exact reviewed h/cpp pins retained; Root HUD wiring review remains required','compiled':False,'native_passed':False,'baseline_native_gap_verified':False,'source_profile_pending':True,'auditioned':False,'final_accepted':False,'members':first}
(BASE/name).write_text(json.dumps(f,indent=2)+'\n',encoding='utf-8');d=(BASE/name).read_bytes();print(json.dumps({'path':str(BASE/name),'bytes':len(d),'sha256':hashlib.sha256(d).hexdigest(),'members':len(first),'two_sha_passes_equal':True}))
