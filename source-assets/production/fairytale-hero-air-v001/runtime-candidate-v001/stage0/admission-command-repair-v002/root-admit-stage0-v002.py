from pathlib import Path
import argparse,hashlib,json

ROOT=Path('F:/Ourgame');BASE=Path(__file__).resolve().parent.parent
parser=argparse.ArgumentParser();parser.add_argument('--freeze-sha',required=True);mode=parser.add_mutually_exclusive_group();mode.add_argument('--admit',action='store_true');mode.add_argument('--validate-only',action='store_true');args=parser.parse_args()
freeze=BASE/'HeroAir-Stage0-candidate-freeze-v001.json';raw=freeze.read_bytes();assert hashlib.sha256(raw).hexdigest()==args.freeze_sha
f=json.loads(raw);assert f['schema']=='HeroAir-Stage0-candidate-freeze-v001'
for row in f['members']:
    p=BASE/row['path'];data=p.read_bytes();assert len(data)==row['bytes'] and hashlib.sha256(data).hexdigest()==row['sha256'],str(p)
before=json.loads((BASE/'before-Source283-pins-v001.json').read_text());assert before['compiled_manifest_sha256']=='71efa450e6aea3d5107554ac524166c824ee253211452001662dad3facb62553'
actual=list((ROOT/'UnrealGame/Source').rglob('*'));actual=[p for p in actual if p.is_file()];assert len(actual)==283
for row in before['files']:
    p=ROOT/row['path'];data=p.read_bytes();assert len(data)==row['bytes'] and hashlib.sha256(data).hexdigest()==row['sha256'],str(p)
index=json.loads((BASE/'stage0-admission-index-v001.json').read_text());writes=[]
for row in index['files']:
    src=BASE/row['candidate'];dst=ROOT/row['actual'];assert dst.resolve().is_relative_to((ROOT/'UnrealGame/Source/CodexDungeon').resolve())
    assert dst.exists()==(row['kind']=='existing');writes.append((src,dst))
if args.admit:
    for src,dst in writes:dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(src.read_bytes());assert dst.read_bytes()==src.read_bytes()
print(json.dumps({'schema':'HeroAir-Stage0-Root-admission-command-v001','admitted':args.admit,'read_only':not args.admit,'files':len(writes),'before_source_files':283,'after_source_files':288 if args.admit else 283,'expected_registered_tests':203,'Root_review_required':True,'UE_run':False,'compiled':False,'semantic_red_verified':False}))
