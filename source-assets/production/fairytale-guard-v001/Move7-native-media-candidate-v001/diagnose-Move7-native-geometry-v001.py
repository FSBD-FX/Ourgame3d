from pathlib import Path
import json, math, runpy, sys, hashlib
R=Path('F:/Ourgame')
C=R/'source-assets/production/fairytale-guard-v001/Move7-native-observer-candidate-v001'
D=C/'tool-contract-fix-v002/tooling'
sys.path.insert(0,str(D))
v=runpy.run_path(str(D/'verify-Move7-native-v001.py'))
A=R/'过程图稿与视频/2026-10-18_裂岩守卫Move7真实追随128与自然入战试样_left_v001'
r=json.loads((A/'原件/runtime-report.json').read_text(encoding='utf-8-sig'))
x=json.loads((C/'read-only-input-pins-v001.json').read_text(encoding='utf-8-sig'))['inputs']
p=json.loads(Path(x['prepared_profile']['path']).read_text(encoding='utf-8-sig'))
s=runpy.run_path(x['host_solver']['path'])['ReferenceSolver'](Path(x['prepared_profile']['path']),x['prepared_profile']['sha256'])
fields=[('source_pivot','source_pivot_px',0),('component_scale','component_to_rest_scale',0),('source_rotation_radians','source_rotation_radians',1e-9),('art_anchor_from_ground','art_anchor_from_source_ground',1e-8),('screen_anchor','screen_anchor',1e-8)]
residuals={key:0. for key,_,_ in fields}
failures=[];count=0
for i,o in enumerate(r['observations']):
 if not o.get('move_query_ok'):continue
 count+=1;q=o['move_query'];f32=v['f32']
 g=[f32(640+(o['guard_ground'][0]-o['camera_ground'][0])*f32(.65)),f32(490-o['guard_ground'][1]*f32(.38))]
 w=s.solve(dict(owner_entity_id=int(r['guard_entity']),accepted_path_owner_entity_id=int(r['guard_entity']),accepted_distance_world=q['accepted_distance'],actual_facing=q['facing'],screen_ground_px=g,ui_scale=1,source_snapshot_sha256=v['SNAPSHOT_SHA'],profile_sha256=v['PROFILE_SHA'],atomic_texture_ready_paths=[z['texture_object_path']for z in p['source7']]))
 for a,b in zip(o['rig_draw']['planned_parts'],w['parts']):
  for key,bk,tol in fields:
   aa,bb=a[key],b[bk]
   vector=isinstance(aa,list)
   residual=max(abs(m-n)for m,n in zip(aa,bb))if vector else abs(aa-bb)
   residuals[key]=max(residuals[key],residual)
   ok=v['point'](aa,bb,tol)if vector else aa==bb if key=='component_scale'else v['near'](aa,bb,tol)
   if not ok:
    failures.append(dict(observation=i,component=a['component'],field=key,actual=aa,expected=bb,actual_types=[type(t).__name__ for t in aa]if vector else type(aa).__name__,expected_types=[type(t).__name__ for t in bb]if isinstance(bb,list)else type(bb).__name__,residual=residual,tolerance=tol,gate=ok))
report=dict(schema='Move7-native-geometry-JSON-only-diagnosis-v001',native_report_path=(A/'原件/runtime-report.json').as_posix(),native_report_sha256=hashlib.sha256((A/'原件/runtime-report.json').read_bytes()).hexdigest(),actual_move_observations=count,actual_seven_components_per_observation=7,maximum_residual_by_field=residuals,failed_comparisons=len(failures),first_failure=failures[0]if failures else None,failures=failures,PNG_read=False,View=False,thresholds_changed=False,Source_changed=False,FinalAccepted=False)
out=Path(__file__).with_name('native-geometry-JSON-diagnosis-v001.json')
with out.open('x',encoding='utf-8')as f:json.dump(report,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps({k:z for k,z in report.items()if k!='failures'},ensure_ascii=False))
