"""Root prepares NEW source projection after actual K56 import; never admits Source."""
from pathlib import Path
from datetime import datetime, timezone
import argparse, hashlib, json

R=Path('F:/Ourgame'); C=R/'source-assets/production/fairytale-sword-secondary-v001'
CM=R/'source-assets/production/backups/v147-SWDStepAudio303-1439-203GREEN-v001/compiled-source-manifest.json'
def need(b,s):
    if not b: raise ValueError(s)
def read(p): return json.loads(Path(p).read_text('utf-8-sig'))
def pin(p):
    p=Path(p); b=p.read_bytes(); return dict(path=p.as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def checked(row,base=R):
    p=Path(row['path']); p=p if p.is_absolute() else base/p
    v=pin(p);need(v['bytes']==row['bytes'] and v['sha256']==row['sha256'],'pin differs: '+str(p));return p
def frozen(p,sha):
    need(pin(p)['sha256']==sha,'frozen candidate differs');j=read(p)
    for row in j['members']+j.get('dependency_pins',[]):checked(row,p.parent)
    return j
def write(p,b):
    p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('xb') as f:f.write(b)
def jsonbytes(j):return (json.dumps(j,ensure_ascii=False,indent=2)+'\n').encode('utf-8')

a=argparse.ArgumentParser();a.add_argument('--content-verification',required=True,type=Path);a.add_argument('--content-verification-sha',required=True);a.add_argument('--observer-directory',required=True,type=Path);a.add_argument('--observer-freeze',required=True,type=Path);a.add_argument('--observer-freeze-sha',required=True);a.add_argument('--output',required=True,type=Path);args=a.parse_args()
need(not args.output.exists() and args.output.resolve().is_relative_to(C),'NEW owned candidate output required')
need(pin(CM)['sha256']=='ae00569bad81eae953b989b964ed2592e6f1e8e0dff43b81163358c43bb3007a','actual predecessor CM differs')
cm=read(CM)
for row in cm['files']:checked(row)
need({p.relative_to(R).as_posix() for p in (R/'UnrealGame/Source').rglob('*') if p.is_file()}=={row['path'] for row in cm['files'] if row['path'].startswith('UnrealGame/Source/')},'actual complete Source303 membership differs')
builder=C/'K8-production-contract-builder-candidate-v001'
bf=builder/'candidate-freeze-v001.json';frozen(bf,'0fa0060f9572fb7ecd8ff927137a8f4955910e102d609539bfeab7aa03d938ab')
witness=C/'forward-step-placement-witness-candidate-v001'
wf=witness/'candidate-freeze-v001.json';frozen(wf,'4e1b918fc1908a0ccd4d0905ee223cb6c4ee2e39d050cd1a41db09f8bd4fb074')
observer_freeze=frozen(args.observer_freeze,args.observer_freeze_sha)
need(args.observer_directory.resolve()==args.observer_freeze.parent.resolve(),'observer directory must equal frozen candidate directory')
observer_members={checked(row,args.observer_freeze.parent).resolve() for row in observer_freeze['members']}
need(pin(args.content_verification)['sha256']==args.content_verification_sha,'actual Content verification differs')
v=read(args.content_verification)
need(v['schema']=='Root-K56-readonly-actual-import-verification-v001' and all(v[k] is True for k in ('verified','old1439_unchanged','Source303_unchanged','added56_exact','actual_Production1495','same_PID_exit0')),'actual successful56 Content import required')
need(v['twoSHA_mismatches']==0 and v['verification_passes']==2,'actual two-pass import verification required')
receipt=read(checked(v['actual_import']));checked(v['actual_launch']);checked(v['actual_exit']);checked(v['actual_log'])
need(receipt['success'] is True and receipt['actual_count']==receipt['saved_count']==len(receipt['assets'])==56,'actual saved56 native receipt missing')
package=builder/'output/source-contract-package-v001';manifest=read(package/'texture-import-manifest-v001.json')
need(v['manifest']==pin(package/'texture-import-manifest-v001.json') and v['source_contract']==manifest['source_contract'],'import source-contract lineage differs')
for row in v['saved_uasset_pins']:checked(row)
expected_prod={R/row['path'] for row in cm['files'] if row['path'].startswith('UnrealGame/Content/Production/')}
expected_prod|={Path(row['saved']['path']) for row in receipt['assets']}
actual_prod={p for p in (R/'UnrealGame/Content/Production').rglob('*') if p.is_file()}
need(actual_prod==expected_prod and len(actual_prod)==1495,'actual Content1495 closure differs')

projected={};before={};applied=[]
def insert(path,anchor,addition,where,label):
    relative=str(path).replace('\\','/');target=R/relative
    if relative not in projected:before[relative]=target.read_bytes();projected[relative]=before[relative]
    old=projected[relative];a=anchor.encode('utf-8')
    if old.count(a)==0:
        # Witness JSON uses LF-normalized inserts. Only materialize its new
        # text where a unique CRLF anchor exists; never normalize old Source.
        alternate=anchor.replace('\r\n','\n').replace('\n','\r\n')
        need(alternate!=anchor and old.count(alternate.encode('utf-8'))==1,'no exact or unique materialized anchor '+label)
        anchor=alternate;addition=addition.replace('\r\n','\n').replace('\n','\r\n');a=anchor.encode('utf-8')
    b=addition.encode('utf-8')
    replacement=b+a if where=='before' else a+b
    need(a and b and old.count(a)==1 and replacement not in old,'non-unique or already applied anchored seam '+label)
    new=old.replace(a,replacement,1)
    need(new.replace(replacement,a,1)==old,'anchored inverse bytes differ '+label)
    projected[relative]=new;applied.append(dict(path=relative,anchor=anchor,addition=addition,where=where,label=label))

runtime=C/'runtime-plan-candidate-v001'
runtime_seams=runtime/'exact-seams-v001.json'
need(pin(runtime_seams)['sha256']=='624bd23b73e3037583506ed349e5b1d35df4bc3c983cbff8853bbd03bf280ec0','reviewed exact runtime seam JSON differs')
for op in read(runtime_seams)['operations']:
    need(op['kind'] in ('insert_before','insert_after'),'unsupported runtime seam')
    insert(op['path'],op['anchor'],op['addition'],op['kind'][7:],op['label'])
for op in read(witness/'exact-seams-v001.json')['ops']:
    insert('UnrealGame/Source/CodexDungeon/'+op['file'],op['anchor'],op['insert'],op['where'],op['id'])
for name,row in read(witness/'exact-seams-v001.json')['projected_files'].items():
    need(projected['UnrealGame/Source/CodexDungeon/'+name]==checked(row).read_bytes(),'materialized witness EOL/bytes differ from reviewed projection '+name)
observer_seam_path=args.observer_directory/'exact-seams-v002.json'
need(observer_seam_path.resolve() in observer_members,'observer seam must be a frozen member')
observer_seams=read(observer_seam_path)
for op in observer_seams['operations']:
    need(op['kind'] in ('insert_before','insert_after'),'unsupported observer seam')
    insert(op['target'],op['anchor'],op['text'],op['kind'][7:],'observer:'+op['target'])

new_sources={}
for name in ('DungeonFairytaleSwordSecondaryPlanV001.h','DungeonFairytaleSwordSecondaryDrawStateV001.h'):
    new_sources['UnrealGame/Source/CodexDungeon/'+name]=(builder/'baseline'/name).read_bytes()
cpp=package/'projected/UnrealGame/Source/CodexDungeon/DungeonFairytaleSwordSecondaryPresentationV001.cpp'
body=cpp.read_bytes();need(body.count(b'P.RuntimeReady=false;')==1 and b'P.RuntimeReady=true;' not in body,'complete metadata profile must initially be disabled')
new_sources['UnrealGame/Source/CodexDungeon/'+cpp.name]=body.replace(b'P.RuntimeReady=false;',b'P.RuntimeReady=true;')
observer_new=observer_seams['new_files']
need(set(observer_new)=={'UnrealGame/Source/CodexDungeon/DungeonSwdForwardStepProbeV002.h','UnrealGame/Source/CodexDungeon/DungeonSwdForwardStepProbeV002.cpp'},'exact two new V002 observer Source files required')
for relative in observer_new:
    p=args.observer_directory/'projected'/relative
    need(p.resolve() in observer_members,'observer new Source must be a frozen member')
    new_sources[relative]=p.read_bytes()
need(len(new_sources)==5 and all(not (R/p).exists() for p in new_sources),'five genuinely NEW Source files required')
for p,data in before.items():need((R/p).read_bytes()==data,'actual Source changed during projection')
for p,data in projected.items():
    inverse=data
    for op in reversed([x for x in applied if x['path']==p]):
        a=op['anchor'].encode('utf-8');b=op['addition'].encode('utf-8');replacement=b+a if op['where']=='before' else a+b
        need(inverse.count(replacement)==1,'non-unique anchored inverse '+op['label'])
        inverse=inverse.replace(replacement,a,1)
    need(inverse==before[p],'full inverse changed actual original Source '+p)

# All validations before creating this NEW candidate. Actual Source remains untouched.
args.output.mkdir()
for p,data in before.items():write(args.output/'before'/p,data)
for p,data in {**projected,**new_sources}.items():write(args.output/'projected'/p,data)
report=dict(schema='Root-K8-actual-import-backed-source-projection-v001',utc=datetime.now(timezone.utc).isoformat(),predecessor_compiled_manifest=pin(CM),actual_Content_verification=pin(args.content_verification),builder_freeze=pin(bf),witness_freeze=pin(wf),observer_freeze=pin(args.observer_freeze),source_contract=manifest['source_contract'],whole_profile_metadata_before=pin(cpp),RuntimeReady_enabled_only_after_actual56_import=True,existing_files=[dict(path=p,before=pin(args.output/'before'/p),after=pin(args.output/'projected'/p)) for p in projected],new_files=[dict(path=p,after=pin(args.output/'projected'/p)) for p in new_sources],operations=applied,all_existing_original_bytes_preserved=True,source_count_before=303,proposed_source_count_after=308,actual_content_count=1495,actual_Source_admitted=False,UE_compiled=False,native_verified=False,FinalAccepted=False)
report['runtime_exact_seams']=pin(runtime_seams)
report['observer_consumed_members']=[pin(observer_seam_path)]+[pin(args.observer_directory/'projected'/p) for p in observer_new]
write(args.output/'source-projection-v001.json',jsonbytes(report))
print(json.dumps(dict(projection=pin(args.output/'source-projection-v001.json'),existing=len(projected),new=len(new_sources),source_admitted=False),ensure_ascii=False))
