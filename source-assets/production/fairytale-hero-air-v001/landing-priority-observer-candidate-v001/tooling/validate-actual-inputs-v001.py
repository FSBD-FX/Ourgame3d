"""Read actual immutable inputs and historical adapter witnesses; never run UE."""
from pathlib import Path
import argparse
import copy
import importlib.util
import json
import time

P=Path(__file__).with_name('verify-landing-priority-native-v001.py')
S=importlib.util.spec_from_file_location('landing_actual_inputs',P)
V=importlib.util.module_from_spec(S);S.loader.exec_module(V)

def validate():
    start=time.perf_counter();lineage=V.read(P.parent/'Root-actual-input-pins-v001.json')
    loaded,F,C=V.dependencies();cm=V.read(V.resolve_pin(lineage['compiled_manifest_pin']))
    V.need(cm['registered_tests']==cm['passed']==203 and cm['failed']==cm['notRun']==0 and cm['production_files']==1419,'Actual strict203 required')
    C.strict203(V.read(V.resolve_pin(cm['full_suite'])))
    before=V.read(P.parent.parent/'before-source-pins-v001.json')
    admission=V.read(V.resolve_pin(lineage['source_admission_pin']));repair=V.read(V.resolve_pin(lineage['source_repair_admission_pin']))
    freeze=V.read(V.resolve_pin(lineage['source_candidate_freeze_pin']))
    for row in freeze['members']:V.resolve_pin(row)
    overlay=V.verify_source_overlay(before,admission,repair,freeze,cm)
    original=next(x for x in freeze['members'] if x['path'].replace('\\','/').endswith('/new-source/DungeonHeroLandingPriorityProbeV001.cpp'))
    V.need(V.printf_repair_bytes(V.resolve_pin(original).read_bytes())==V.resolve_pin(repair['after']).read_bytes(),'Actual three-call repair differs')
    for key in ('failed_build','failed_log'):V.resolve_pin(repair[key])
    for _ in range(2):
        for row in cm['files']:V.resolve_pin(row)
    names={x['path'] for x in cm['files']};V.need(len(names)==len(cm['files'])==1721,'Exact current CM1721 required')
    for prefix,count in (('UnrealGame/Source/',298),('UnrealGame/Content/Production/',1419)):
        actual={x.relative_to(V.ROOT).as_posix() for x in (V.ROOT/prefix).rglob('*') if x.is_file()}
        V.need(actual=={x for x in names if x.startswith(prefix)} and len(actual)==count,'Actual membership changed')
    source_counts={}
    for action in ('J','Shift'):source_counts[action]=len(V.sources_for(action,loaded,C)[0])
    _,am,ap,*_=C.source_only();resident_paths={a['object_path'] for a in am['assets']}|{V.SWORD}
    ready_markers=V.read(loaded['ready-marker-proposal-v002.json']);witnesses=[];rejections=0
    for side in ('left','right'):
        path=V.ROOT/'过程图稿与视频'/('2026-10-19_钟盔装备跳跃三连实录_'+side+'_v003')/'原件/runtime-report.json'
        r=V.read(path)
        for frame in range(5):
            o=next(o for o in r['observations'] if o['new_air_draw']['drawn'] and o['new_air_draw']['slot_count']==9 and o['physical_visual_key']==frame)
            paths={a['component']:a['object_path'] for a in am['assets'] if a['frame']==frame};paths['IndependentSword']=V.SWORD
            V.quad_geometry(o,ap['Frames'][frame],paths,True,resident_paths)
            for field in ('mirror','resident'):
                bad=copy.deepcopy(o)
                if field=='mirror':bad['new_air_draw']['slots'][0]['uv_size'][0]*=-1
                else:bad['new_air_draw']['resident_textures'][0]['texture']='unknown-resident'
                try:V.quad_geometry(bad,ap['Frames'][frame],paths,True,resident_paths)
                except ValueError:rejections+=1
                else:raise ValueError('Historical geometry mutation was accepted: '+field)
        ready=[o for o in r['observations'] if o['old_draw']['clip']=='sword_ready_idle' and o['old_draw']['armor_drawn']]
        V.need(ready,'Historical brown Ready unavailable')
        for o in ready:V.legacy_identity(o,'sword_ready_idle');V.legacy_quads(o,ready_markers)
        witnesses.append(dict(side=side,report_pin=V.pin(path),actual_Air_geometry_witnesses=5,actual_brown_Ready_geometry_witnesses=len(ready)))
    return dict(schema='hero-landing-priority-actual-inputs-and-historical-adapters-v001',passed=True,checker_pin=V.pin(P),validation_script_pin=V.pin(__file__),compiled_manifest_pin=lineage['compiled_manifest_pin'],source_admission_pin=lineage['source_admission_pin'],source_repair_admission_pin=lineage['source_repair_admission_pin'],source_overlay=overlay,compiled_members_checked=1721,actual_file_SHA_passes=2,exact_source_content_membership=True,source_texture_families=source_counts,historical_witnesses=witnesses,historical_geometry_negative_rejections=rejections,elapsed_s=time.perf_counter()-start,RootApproved=False,UE_started=False,new_landing_native_verified=False,visual_reviewed=False,audio_listened=False,FinalAccepted=False)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--out');args=parser.parse_args();result=validate()
    if args.out:
        with Path(args.out).open('x',encoding='utf-8') as f:json.dump(result,f,indent=2,ensure_ascii=False);f.write('\n')
    print(json.dumps(result,ensure_ascii=False))
