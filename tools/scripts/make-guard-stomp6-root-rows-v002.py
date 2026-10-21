"""Root rows v002: retain explicit per-frame authored registration authority."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json
R=Path('F:/Ourgame');B=R/'source-assets/production/fairytale-guard-v001'
p=argparse.ArgumentParser();p.add_argument('--recovery-registration',required=True);p.add_argument('--recovery-approval',required=True);p.add_argument('--recovery-retention',required=True);a=p.parse_args()
def read(q):return json.loads(q.read_text(encoding='utf-8-sig'))
def sha(q):return hashlib.sha256(q.read_bytes()).hexdigest()
def pin(q):return dict(path=q.as_posix(),bytes=q.stat().st_size,sha256=sha(q))
def resolve(q):q=Path(q);return q if q.is_absolute() else R/q
active=B/'stomp-source-fit-audit-v001/active245-extraction-review-v001/post-E529-minimal-visible-registration-proposal-v001.json'
active_approval=B/'root-Stomp-source-approval-v001/Active245-Root-limited-source-fit-v001.json'
active_E=Path('E:/OurGame/Knight/过程图稿与视频/2026-10-18-OurgameUE-GuardStomp245-extraction-v529/source-size-SHA256.json')
rows=[]
for clip,regpath,apath,epath in [('StompActive',active,active_approval,active_E),
                               ('StompRecovery',resolve(a.recovery_registration),resolve(a.recovery_approval),resolve(a.recovery_retention))]:
    reg=read(regpath);approval=read(apath);e=read(epath)
    assert approval['RootApproved'] is True and approval['is_template'] is False and approval['FinalAccepted'] is False
    assert approval['clip']==clip and approval['limited_import_candidate_approved'] is True
    assert approval['registration_proposal_sha256']==sha(regpath)
    assert e['verification_passes']==2 and e['source_and_target_hash_mismatches']==0
    index=reg['source_index'];ip=resolve(index['path']);assert pin(ip)==index and sha(ip)==approval['source_index_sha256']
    basis=reg['bodybasis_frame'];crown=reg['bodybasis_crown_y'];floor=reg['bodybasis_NEAR_floor_y'];extent=reg['standing_equivalent_extent_px']
    assert floor-crown==extent and reg['body_display_height_target']==100.8
    assert (basis,crown,floor-1,extent)==tuple(approval[k] for k in ['standing_basis_frame','standing_body_crown_y','standing_body_nearsole_y','standing_body_extent_px'])
    native=approval['native_source_id'];frames=[]
    for i,f in enumerate(reg['rows']):
        assert f['frame']==i and pin(resolve(f['source']['path']))==f['source']
        x,y=reg['perframe_roots'][i];assert [x,y]==f['authorRoot_proposal']
        name=f'T_Guard{native}_{clip}_{i:02d}';package='/Game/Production/FirstBatch/GuardWhole_stomp_v004/'+name
        frames.append(dict(clip=clip,frame=i,native_source_id=native,object_path=package+'.'+name,
                           source=f['source'],RGBA_sha256=f['RGBA_sha256'],floor_pivot_source_px=[x,y],
                           pivot_authority=f.get('pivot_authority','ArtistNearSupportDeltaPropagation')))
    assert len(frames)==(2 if clip=='StompActive' else 4)
    rows.append(dict(clip=clip,native_source_id=native,logical_frames=len(frames),source_pose_approved=True,
                     trial_allowed=True,final_accepted=False,trial_approval_record=f'Root.GuardStomp50.v139.20261018.ScopedTrial.{clip}',
                     standing_basis_frame=basis,standing_body_crown_y=crown,standing_body_nearsole_y=floor-1,
                     standing_body_extent_px=extent,target_standing_body_height_px=100.8,canvas_source_px=[512,512],
                     registration_evidence=pin(regpath),source_index=index,Root_source_fit_approval=pin(apath),
                     E_retention_index=pin(epath),frames=frames))
out=B/'root-Stomp-source-approval-v001/Root-Stomp6-preimport-source-rows-v001.json';assert not out.exists()
with out.open('x',encoding='utf-8') as f:json.dump(dict(schema='Root-GuardStomp6-preimport-source-rows-v001',is_template=False,
    RootApproved=True,utc=datetime.now(timezone.utc).isoformat(),rows=rows,source_pixels_modified=False,
    native_stomp_verified=False,footlock_certified=False,FinalAccepted=False),f,ensure_ascii=False,indent=2)
print(json.dumps(dict(source_rows=pin(out),new6_source_facts=True,native_import_started=False)))
