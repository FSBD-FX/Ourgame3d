"""One actual Data admission after approved six-source native import verification."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json,shutil,subprocess
R=Path('F:/Ourgame');B=R/'source-assets/production/fairytale-guard-v001'
p=argparse.ArgumentParser();p.add_argument('--native-import',required=True);p.add_argument('--independent-import',required=True);a=p.parse_args()
def resolve(q):q=Path(q);return q if q.is_absolute() else R/q
def read(q):return json.loads(q.read_text(encoding='utf-8-sig'))
def sha(q):return hashlib.sha256(q.read_bytes()).hexdigest()
def pin(q):return dict(path=q.relative_to(R).as_posix(),bytes=q.stat().st_size,sha256=sha(q))
def check(x):
    q=resolve(x['path']);assert q.stat().st_size==x['bytes'] and sha(q)==x['sha256'],q
    return q
native=resolve(a.native_import);independent=resolve(a.independent_import);rec=read(native);proof=read(independent)
manifest=B/'root-Stomp6-import-v001/import-manifest.json';m=read(manifest)
assert rec['success'] is True and rec['schema']=='guard-Stomp6-actual-import-v001' and rec['actual_total']==1332
assert proof['success'] is True and proof['verification_passes']==2 and proof['hash_mismatches']==0
assert proof['receipt']['sha256']==sha(native) and rec['manifest']['sha256']==proof['manifest']['sha256']==sha(manifest)
assert proof['old1326_unchanged_twice'] is True and proof['new6_saved_twice'] is True
for x in m['old_production_files']:check(x)
for x in rec['assets']:check(x['saved'])
assert len([q for q in (R/'UnrealGame/Content/Production').rglob('*') if q.is_file()])==1332
target=R/'UnrealGame/Source/CodexDungeon/DungeonFairytaleGuardStompDataV004.inl'
stage=read(R/'docs/production/first-batch-v2/evidence/guard-Stomp-v139-v001/stage0-admission-v001/admission-receipt-v001.json')
previous=next(x for x in stage['admitted'] if x['path']==target.relative_to(R).as_posix());check(previous)
candidate=B/'root-Stomp6-import-v001/DungeonFairytaleGuardStompDataV004.inl';assert candidate.is_file()
assert 'TArray<FRow> Result=ProfileFull();' in candidate.read_text(encoding='utf-8')
before=[pin(q) for q in sorted((R/'UnrealGame/Source').rglob('*')) if q.is_file()];assert len(before)==262
out=R/'docs/production/first-batch-v2/evidence/guard-Stomp-v139-v001/approved-data-admission-v001';assert not out.exists();out.mkdir(parents=True)
receipt=dict(schema='Root-GuardStomp-approved-Data-admission-v001',is_template=False,RootApproved=True,success=False,
             utc=datetime.now(timezone.utc).isoformat(),previous_Data_pin=previous,Source_count=262,FinalAccepted=False,
             exact_import_manifest=pin(manifest),native_import_receipt=pin(native),independent_import_receipt=pin(independent),
             selected_source_manifest=pin(B/'root-Stomp6-import-v001/Stomp6-selected-source-manifest-v001.json'),candidate=pin(candidate))
try:
    shutil.copy2(target,out/'previous-Data-stub-v001.inl');shutil.copy2(candidate,target);assert sha(target)==sha(candidate)
    for x in before:
        if x['path']!=previous['path']:check(x)
    assert len([q for q in (R/'UnrealGame/Source').rglob('*') if q.is_file()])==262
    receipt.update(success=True,admitted=[pin(target)],other261_Source_unchanged=True,
                   source_compiled_after_admission=False,native_stomp_verified=False)
except Exception as e:receipt['failure']=str(e);raise
finally:
    with (out/'admission-receipt-v001.json').open('x',encoding='utf-8') as f:json.dump(receipt,f,ensure_ascii=False,indent=2)
print(json.dumps(dict(success=True,Source262=True,Production1332=True,receipt=pin(out/'admission-receipt-v001.json'))))
