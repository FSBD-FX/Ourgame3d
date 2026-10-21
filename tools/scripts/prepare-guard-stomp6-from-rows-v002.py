"""Prepare six exact imports; explicit late recovery author root is not foot-lock."""
from pathlib import Path
from datetime import datetime, timezone
import argparse,hashlib,json
from PIL import Image
R=Path('F:/Ourgame');B=R/'source-assets/production/fairytale-guard-v001'
p=argparse.ArgumentParser();p.add_argument('--approved',required=True);a=p.parse_args()
def read(q):return json.loads(q.read_text(encoding='utf-8-sig'))
def sha(q):return hashlib.sha256(q.read_bytes()).hexdigest()
def pin(q):return dict(path=q.as_posix(),bytes=q.stat().st_size,sha256=sha(q))
def check(x):
    q=Path(x['path']);q=q if q.is_absolute() else R/q
    assert q.stat().st_size==x['bytes'] and sha(q)==x['sha256'],q
    return q
def write(q,v):
    with q.open('x',encoding='utf-8',newline='\n') as f:f.write(v if isinstance(v,str) else json.dumps(v,ensure_ascii=False,indent=2)+'\n')
approved=Path(a.approved);approved=approved if approved.is_absolute() else R/approved
d=read(approved);assert d['schema']=='Root-GuardStomp6-preimport-source-rows-v001' and d['RootApproved'] is True and d['FinalAccepted'] is False
rows=d['rows'];assert [x['clip'] for x in rows]==['StompActive','StompRecovery']
assert [len(x['frames']) for x in rows]==[2,4]
old_snapshot=R/'source-assets/production/backups/v138-HeroDeath190G/compiled-source-manifest.json'
old=[x for x in read(old_snapshot)['files'] if x['path'].startswith('UnrealGame/Content/Production/')]
assert len(old)==1326
for repeat in range(2):
    for x in old:check(x)
actual={q.relative_to(R).as_posix() for q in (R/'UnrealGame/Content/Production').rglob('*') if q.is_file()}
assert actual=={x['path'] for x in old}
namespace='/Game/Production/FirstBatch/GuardWhole_stomp_v004'
assets=[];lines=['#pragma once','namespace DungeonFairytaleGuardStompV004','{',
 'inline const TArray<DungeonFairytaleGuardFullV003::FRow>& ProfileStompV004()', '{',
 ' using namespace DungeonFairytaleGuardFullV003;', ' static const TArray<FRow> Rows=[]', ' {',
 '  TArray<FRow> A;']
for row in rows:
    n=len(row['frames']);assert row['source_pose_approved'] is True and row['trial_allowed'] is True and row['final_accepted'] is False
    assert row['target_standing_body_height_px']==100.8 and row['canvas_source_px']==[512,512]
    assert row['standing_body_nearsole_y']-row['standing_body_crown_y']+1==row['standing_body_extent_px']>0
    assert 0<=row['standing_basis_frame']<n
    check(row['registration_evidence']);check(row['source_index']);check(row['Root_source_fit_approval'])
    eindex=check(row['E_retention_index']);e=read(eindex)
    assert e['verification_passes']==2 and e['source_and_target_hash_mismatches']==0
    lines+=['  {FRow R;',f'   R.Clip=EClip::{row["clip"]};R.NativeSourceId={row["native_source_id"]};R.SourcePoseApproved=true;',
            f'   R.TrialAllowed=true;R.FinalAccepted=false;R.TrialApprovalRecord=TEXT("{row["trial_approval_record"]}");',
            f'   R.StandingBasisFrame={row["standing_basis_frame"]};R.StandingCrownY={row["standing_body_crown_y"]};R.StandingSoleY={row["standing_body_nearsole_y"]};R.StandingExtent={float(row["standing_body_extent_px"])};',
            f'   R.RegistrationEvidenceSHA256=TEXT("{row["registration_evidence"]["sha256"]}");',
            f'   R.SourceIndexSHA256=TEXT("{row["source_index"]["sha256"]}");']
    for i,frame in enumerate(row['frames']):
        assert frame['frame']==i and frame['clip']==row['clip'] and frame['native_source_id']==row['native_source_id']
        src=check(frame['source'])
        with Image.open(src) as im:
            assert im.mode=='RGBA' and im.size==(512,512) and im.getchannel('A').getbbox()
            assert hashlib.sha256(im.tobytes()).hexdigest()==frame['RGBA_sha256']
        x,y=frame['floor_pivot_source_px'];assert 0<=x<=512 and 0<=y<=512
        assert frame['pivot_authority'] in ['ArtistNearSupportDeltaPropagation','ArtistStandingRootPropagation']
        name=f'T_Guard{row["native_source_id"]}_{row["clip"]}_{i:02d}';package=namespace+'/'+name;obj=package+'.'+name
        assert frame['object_path']==obj
        saved=R/'UnrealGame/Content'/Path(package.removeprefix('/Game/')+'.uasset');assert not saved.exists()
        matches=[z for z in e['files'] if z['sha256']==frame['source']['sha256'] and z['bytes']==frame['source']['bytes']]
        assert matches
        retained=eindex.parent/matches[0]['retained_relative'];retainedpin=pin(retained);assert retainedpin['sha256']==frame['source']['sha256']
        assets.append(dict(component=row['clip'],frame=i,name=name,source=frame['source'],source_RGBA_sha256=frame['RGBA_sha256'],
                           destination_path=namespace,package_path=package,object_path=obj,saved_path=saved.as_posix(),retained_E=retainedpin))
        lines.append(f'   R.Frames.Add({{TEXT("{obj}"),TEXT("{frame["source"]["sha256"]}"),TEXT("{frame["RGBA_sha256"]}"),FVector2D({float(x)},{float(y)}),EPivotAuthority::{frame["pivot_authority"]}}});')
    lines+=['   A.Add(MoveTemp(R));}']
lines+=['  TArray<FRow> Result=ProfileFull();',
        '  for(auto& Override:A){FRow* Target=Result.FindByPredicate([&](const FRow& Q){return Q.Clip==Override.Clip;});check(Target);*Target=MoveTemp(Override);}',
        '  return Result;',' }();',' return Rows;','}','}','']
out=B/'root-Stomp6-import-v001';assert not out.exists();out.mkdir(parents=True)
source_manifest=out/'Stomp6-selected-source-manifest-v001.json'
write(source_manifest,dict(schema='GuardStomp6-selected-source-manifest-v001',Root_source_approval=pin(approved),namespace=namespace,rows=rows,assets=assets,FinalAccepted=False))
trial=out/'Root-Stomp6-limited-import-trial-v001.json'
write(trial,dict(schema='Root-GuardStomp6-limited-native-import-v001',utc=datetime.now(timezone.utc).isoformat(),
                 RootApproved=True,is_template=False,limited_import_approved=True,source_manifest=pin(source_manifest),
                 source_fit_approval=pin(approved),scope='Two StompActive and four StompRecovery exact source frames; original kernel and old44 retained',
                 runtime_verified=False,footlock_certified=False,FinalAccepted=False))
manifest=out/'import-manifest.json'
write(manifest,dict(schema='Root-GuardStomp6-import-v001',expected_old_count=1326,expected_new_count=6,expected_final_count=1332,
                    namespace=namespace,replace_existing=False,root_trial_registration=pin(trial),source_manifest=pin(source_manifest),
                    old_compiled_snapshot=pin(old_snapshot),old_production_files=old,assets=assets,FinalAccepted=False))
candidate=out/'DungeonFairytaleGuardStompDataV004.inl';write(candidate,'\n'.join(lines))
print(json.dumps(dict(manifest=pin(manifest),data_candidate=pin(candidate),source6_verified=True,old1326_twice_unchanged=True,import_started=False)))
