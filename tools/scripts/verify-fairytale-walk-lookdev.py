"""Actual walk-lookdev observations + unchanged native lossless capture audit."""
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json
import math

ROOT=Path(__file__).resolve().parents[2]
BASE=Path(__file__).with_name("verify-fairytale-lookdev.py")
BASE_SHA="f94684fa62e1080d330b096ea5ba2f1f0ef5a1be1075c027f187ad25b9d176b1"


def require(condition, why):
    if not condition: raise ValueError(why)


def load_module(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def validate_walk(report,manifest):
    require(report["schema"]=="fairytale-lookdev-capture-v1" and report["profile"]=="fairytale_walk_observation_silent_v001" and report["passed"], "Wrong/failed actual walk profile")
    require(report["silent_video"] and not report["audio_capture_started"] and not report["native_async_flush_after_audio_stop"], "Silent capture cannot claim audio recording")
    require(not report["new_style_accepted"] and not report["motion_reviewed"] and not report["auditioned"] and report["formal_complete_units"]==0, "Capture cannot grant review/completion")
    timing=report["capture_timing"];offsets=timing["frame_wall_offsets_s"];rows=report["observations"]
    require(len(rows)==len(offsets)>=100 and not timing["use_fixed_time_step"], "Missing real-time30fps observations")
    duration=timing["capture_stop_monotonic_s"]-timing["capture_start_monotonic_s"]
    require(4.1<=duration<=4.8 and abs(duration-timing["requested_video_wall_duration_s"])<1e-6, "Wrong actual capture duration")
    require(0<offsets[0]<=.15 and all(b>a for a,b in zip(offsets,offsets[1:])) and offsets[-1]<=duration and duration-offsets[-1]<.18, "Invalid/missing capture frame intervals")
    warm=report["prewarm_screenshot"]
    require(warm["requested"] and warm["completed_file_received"] and not warm["used_as_recording_frame"], "Missing separate actual prewarm")
    require(0<warm["request_monotonic_s"]<=warm["complete_monotonic_s"]<=timing["capture_start_monotonic_s"], "Prewarm ordering")
    baseline=report["baseline_game"]
    require(baseline["available"] and baseline["mode"] and baseline["waiting"] and not baseline["player_tick_enabled"], "Independent frozen observation mode missing")
    require(all(not e["tick_enabled"] and not e["ai_enabled"] for e in baseline["enemies"]), "Enemy gameplay changed in observation mode")
    masks={(a,s):0 for a in ('hero','stone') for s in (-1,1)}
    loops=dict.fromkeys(masks,0);previous={};serial=-1;epoch=None
    for row,offset in zip(rows,offsets):
        require(abs(row["wall_offset_s"]-offset)<1e-8 and row["hud_available"] and row["active"] and row["configuration_confirmed"] and row["hero_walk_active"], "Wrong/stale HUD observation")
        require(row["game"]==baseline, "Gameplay advanced or normal stress keys mutated frozen state")
        require(not row["interface_visible"] and row["text_draw_calls"]==row["legacy_stack_count"]==row["action_audio_requests"]==0 and not row["legacy_weapon_used"], "Old UI/identity/audio request leaked")
        require(row["viewport"]==[1280,720] and abs(row["ui_scale"]-1)<1e-7, "Wrong native viewport")
        current=int(row["draw_serial"]);require(current>serial, "Repeated HUD draw record");serial=current
        wall=timing["capture_start_monotonic_s"]+offset
        require(0<=wall-row["draw_wall"]<.15, "Draw not current to actual screenshot")
        elapsed=row["animation_elapsed_s"];require(math.isfinite(elapsed) and elapsed>=0, "Bad animation clock")
        current_epoch=row["draw_wall"]-elapsed
        if epoch is None:epoch=current_epoch
        require(abs(current_epoch-epoch)<1e-6 and epoch<=timing["capture_start_monotonic_s"], "Animation epoch changed")
        input_side=-1 if row["input_A"] and not row["input_D"] else 1 if row["input_D"] and not row["input_A"] else None
        for actor in ('hero','stone'):
            hero=actor=='hero';draw=row[actor];count=6 if hero else 4;step=.083 if hero else .167
            sample=math.floor(elapsed/step);frame=draw["frame"];side=draw["facing"]
            require(frame==sample%count and int(draw["sample"])==sample, "83ms walk/167ms stone manifest clock mismatch")
            require(draw["clip"]==('walk' if hero else 'idle'), "Wrong source clip")
            require(side in (-1,1) and draw["native_facing"]==(1 if hero else -1), "Native facing mismatch")
            if input_side is not None:require(side==(input_side if hero else -input_side), "Normal A/D did not control display facing")
            if hero:
                expected=manifest['assets'][frame]['object_path'];pivot=[256,464];canvas=manifest['preview_canvas_size']
            else:
                name=f'T_Fairytale_StoneIdle_{frame:03d}_v001';expected=f'/Game/Production/ArtTrials/EV047/v001/StoneIdle/{name}.{name}'
                pivot=[[260,464],[257,464],[264,464],[265,464]][frame];canvas=93.6*512/386.5
            require(draw["texture_ready"] and draw["path"]==expected, "Missing source texture/old fallback")
            require(draw["root"]==pivot and abs(draw["canvas_size"]-canvas)<1e-7, "Display pivot/shared scale changed")
            flip=side!=draw['native_facing'];require(draw['flipped']==flip, "Wrong mirror direction")
            x,y=draw['ground_screen'];require(abs(x-(435.2 if hero else 819.2))<1e-3 and abs(y-540)<1e-3, "Observation anchor drift")
            camera=row['camera_ground_center'];ground=draw['ground']
            require(abs(x-(640+(ground[0]-camera[0])*.65))<1e-3 and abs(y-(490-ground[1]*.38))<1e-3, "Actual ground projection changed")
            root_x=512-pivot[0] if flip else pivot[0]
            top=[x-canvas*root_x/512,y-canvas*pivot[1]/512]
            require(all(abs(a-b)<1e-3 for a,b in zip(top,draw['top_screen'])), "Actual source quad placement/mirroring mismatch")
            key=(actor,side);masks[key]|=1<<frame;last=previous.get(actor)
            if last and last[0]==side and last[1]==count-1 and frame==0 and sample==last[2]+1:loops[key]+=1
            previous[actor]=(side,frame,sample)
    require(all(masks[('hero',s)]==63 and masks[('stone',s)]==15 for s in (-1,1)), "Every source frame in both facings not observed")
    require(all(loops[('hero',s)]>=2 and loops[('stone',s)]>=1 for s in (-1,1)), "Two real5→0 walk wraps per facing and stone context loop missing")
    for key in ('A','D','W','S','J','K','E','Q','T','R','Enter','SpaceBar','LeftShift'):
        require(any(r['key']==key and r['down'] for r in report['normal_input_requests']) and any(r['key']==key and not r['down'] for r in report['normal_input_requests']), "Actual normal input stress missing: "+key)
    heights=[(r['source_bbox'][3]-r['source_bbox'][1])*manifest['preview_canvas_size']/512 for r in manifest['assets']]
    return {'observations':len(rows),'duration_s':duration,'frame_masks':{f'{a}_{s}':v for (a,s),v in masks.items()},'actual_wraps':{f'{a}_{s}':v for (a,s),v in loops.items()},'source_visible_heights_at_fixed_canvas':heights,'actual_gameplay_movement':False,'scope':'Source animation observation with normal A/D display facing; gameplay kernels frozen.'}


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--archive',default='');parser.add_argument('--manifest',required=True);parser.add_argument('--preflight-only',action='store_true');args=parser.parse_args()
    require(hashlib.sha256(BASE.read_bytes()).hexdigest()==BASE_SHA, "Native audit implementation changed")
    native=load_module('walk_lossless_native_audit',BASE)
    checks=load_module('walk_frozen_sources',Path(__file__).with_name('ue_fairytale_walk_lookdev_checks.py'))
    require(Path(args.manifest).resolve()==checks.MANIFEST.resolve(), "Wrong source manifest")
    manifest=checks.preflight(require_unused=False)
    if args.preflight_only:
        print(json.dumps({'source_preflight':True,'source_PNGs':6,'native_imported_packages_unchanged':6,'old_packages_unchanged':863}))
        return
    require(bool(args.archive), "Runtime inspection requires an actual capture archive")
    archive=Path(args.archive).resolve();report_path=archive/'原件/runtime-report.json'
    report=json.loads(report_path.read_text(encoding='utf-8-sig'))
    old=ROOT/'source-assets/production/fairytale-lookdev-v001/manifests/import-lookdev-v001.json'
    native.validate_manifest(old)
    result={'schema':'fairytale-walk-lookdev-runtime-audit-v1','passed':True,**validate_walk(report,manifest),**native.validate_native(archive,report),
        'manifest_sha256':checks.MANIFEST_SHA,'report_sha256':hashlib.sha256(report_path.read_bytes()).hexdigest(),'motion_reviewed':False,'runtime_gameplay_identity_installed':False,'formal_complete_units':0}
    print(json.dumps(result,ensure_ascii=False))


if __name__=='__main__':main()
