from pathlib import Path
import argparse,hashlib,json
ROOT=Path('F:/Ourgame');BASE=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--freeze-sha',required=True);g=p.add_mutually_exclusive_group();g.add_argument('--admit',action='store_true');g.add_argument('--validate-only',action='store_true');a=p.parse_args()
frozen=BASE/'HeroAir-baseline-observer-candidate-freeze-v001.json';raw=frozen.read_bytes();assert hashlib.sha256(raw).hexdigest()==a.freeze_sha;f=json.loads(raw)
for r in f['members']:
    b=(BASE/r['path']).read_bytes();assert len(b)==r['bytes'] and hashlib.sha256(b).hexdigest()==r['sha256'],r['path']
before=json.loads((BASE/'before-Source290-pins-v001.json').read_text());files=[x for x in (ROOT/'UnrealGame/Source').rglob('*') if x.is_file()];assert len(files)==290
for r in before['files']:
    b=(ROOT/r['path']).read_bytes();assert len(b)==r['bytes'] and hashlib.sha256(b).hexdigest()==r['sha256'],r['path']
index=json.loads((BASE/'observer-admission-index-v001.json').read_text());writes=[]
for r in index['files']:
    src=BASE/r['candidate'];dst=ROOT/r['actual'];assert dst.resolve().is_relative_to((ROOT/'UnrealGame/Source/CodexDungeon').resolve());assert dst.exists()==(r['kind']=='existing');writes.append((src,dst))
if a.admit:
    for src,dst in writes:dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(src.read_bytes());assert dst.read_bytes()==src.read_bytes()
print(json.dumps({'schema':'HeroAir-baseline-Root-admission-command-v001','admitted':a.admit,'read_only':not a.admit,'files':len(writes),'before_source_files':290,'after_source_files':292 if a.admit else 290,'registered_tests':203,'Root_actual_semantic_RED_and_HUD_review_required':True,'UE_run':False,'compiled':False,'native_passed':False}))
