"""Actual near-bracer/shin observation over the fixed chest/shoulder baseline."""
from pathlib import Path
import argparse,hashlib,importlib.util,json,math

BASE=Path(__file__).with_name('verify-fairytale-lookdev.py')
BASE_SHA='f94684fa62e1080d330b096ea5ba2f1f0ef5a1be1075c027f187ad25b9d176b1'

def require(condition,why):
    if not condition:raise ValueError(why)

def load(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def validate(report,manifest,shoulders,limbs):
    require(report['schema']=='fairytale-lookdev-capture-v1' and report['profile']=='fairytale_near_limb_observation_silent_v001' and report['passed'],'Wrong actual near-limb profile')
    require(report['silent_video'] and not report['audio_capture_started'] and not report['native_async_flush_after_audio_stop'],'Unexpected audio claim')
    require(not report['new_style_accepted'] and not report['motion_reviewed'] and not report['auditioned'] and report['formal_complete_units']==0,'Capture cannot grant acceptance')
    t=report['capture_timing'];rows=report['observations'];offsets=t['frame_wall_offsets_s'];duration=t['capture_stop_monotonic_s']-t['capture_start_monotonic_s']
    require(len(rows)==len(offsets)>=600 and not t['use_fixed_time_step'] and 24.0<=duration<=26.0 and abs(duration-t['requested_video_wall_duration_s'])<1e-6,'Wrong real-time duration/count')
    require(0<offsets[0]<.15 and all(b>a for a,b in zip(offsets,offsets[1:])) and 0<=duration-offsets[-1]<.18,'Missing/invalid real-time frame interval')
    warm=report['prewarm_screenshot'];require(warm['requested'] and warm['completed_file_received'] and not warm['used_as_recording_frame'] and 0<warm['request_monotonic_s']<=warm['complete_monotonic_s']<=t['capture_start_monotonic_s'],'Wrong prewarm ordering')
    game=report['baseline_game'];require(game['available'] and game['mode'] and game['waiting'] and not game['player_tick_enabled'] and all(not e['tick_enabled'] and not e['ai_enabled'] for e in game['enemies']),'Missing frozen observation mode')
    combinations={(dark,side,mode):0 for dark in (False,True) for side in (-1,1) for mode in ('off','both','bracer','shin')}
    wraps={k:0 for k in combinations};previous=None;serial=-1;epoch=None
    for row,offset in zip(rows,offsets):
        require(abs(row['wall_offset_s']-offset)<1e-8 and row['hud_available'] and row['active'] and row['configuration_confirmed'] and row['hero_chest_active'] and row['hero_shoulder_active'] and row['hero_near_limb_active'] and not row['hero_walk_active'],'Wrong/stale HUD observation')
        require(row['game']==game,'Observation controls advanced frozen gameplay')
        require(not row['interface_visible'] and row['text_draw_calls']==row['legacy_stack_count']==row['action_audio_requests']==0 and not row['legacy_weapon_used'],'UI/legacy/audio leaked')
        require(row['viewport']==[1280,720] and abs(row['ui_scale']-1)<1e-7,'Wrong native viewport')
        current=int(row['draw_serial']);require(current>serial,'Repeated draw serial');serial=current
        require(0<=t['capture_start_monotonic_s']+offset-row['draw_wall']<.15,'HUD not current to screenshot')
        elapsed=row['animation_elapsed_s'];require(math.isfinite(elapsed) and elapsed>=0,'Bad animation clock')
        e=row['draw_wall']-elapsed
        if epoch is None:epoch=e
        require(abs(e-epoch)<1e-6,'Animation epoch changed')
        require(row['hero_dark_position']==row['input_W'] and row['chest_visible_choice'] and row['input_C'],'Actual baseline W/C choice changed')
        require(not row['input_N'] and not row['input_F'] and not row['near_shoulder_only'] and not row['far_shoulder_only'],'Fixed shoulder baseline was isolated')
        require(row['limb_visible_choice']==row['input_L'] and row['near_bracer_only']==(row['input_L'] and row['input_B']) and row['near_shin_only']==(row['input_L'] and row['input_G']),'Actual L/B/G choice differs from HUD')
        require(not (row['input_B'] and row['input_G']),'Ambiguous simultaneous isolated-limb choice')
        input_side=-1 if row['input_A'] and not row['input_D'] else 1 if row['input_D'] and not row['input_A'] else None
        for actor in ('hero','stone'):
            hero=actor=='hero';a=row[actor];sample=math.floor(elapsed/.167);frame=sample%4;side=a['facing']
            require(a['frame']==frame and int(a['sample'])==sample and a['clip']=='idle','Original4x167ms timing changed')
            require(side in (-1,1) and a['native_facing']==(1 if hero else -1),'Wrong facing')
            if input_side is not None:require(side==(input_side if hero else -input_side),'A/D did not control facing')
            n=f'T_Fairytale_{"Hero" if hero else "Stone"}Idle_{frame:03d}_v001'
            expected=f'/Game/Production/ArtTrials/EV047/v001/{"HeroCommonIdle" if hero else "StoneIdle"}/{n}.{n}'
            pivot=[256,464] if hero else [[260,464],[257,464],[264,464],[265,464]][frame]
            canvas=manifest['preview_canvas_size'] if hero else 93.6*512/386.5
            require(a['texture_ready'] and a['path']==expected and a['root']==pivot and abs(a['canvas_size']-canvas)<1e-7,'Source/pivot/shared scale changed')
            flip=side!=a['native_facing'];require(a['flipped']==flip,'Wrong mirror')
            dark=hero and row['hero_dark_position'];x,y=a['ground_screen'];anchor=[190,590] if dark else [435.2,540] if hero else [819.2,540]
            require(abs(x-anchor[0])<1e-3 and abs(y-anchor[1])<1e-3,'Presentation anchor drift')
            camera=row['camera_ground_center'];ground=a['ground']
            require(abs(x-(640+(ground[0]-camera[0])*.65))<1e-3 and abs(y-(490-ground[1]*.38))<1e-3,'Actual projection changed')
            top=[x-canvas*(512-pivot[0] if flip else pivot[0])/512,y-canvas*pivot[1]/512]
            require(all(abs(u-v)<1e-3 for u,v in zip(top,a['top_screen'])),'Actual source quad changed')
            if hero:
                require(a['chest_texture_ready'] and a['chest_path']==manifest['assets'][frame]['object_path'] and a['chest_drawn'],'Actual isolated chest source missing or wrong choice')
                require(row['near_shoulder_only']==row['input_N'] and row['far_shoulder_only']==row['input_F'] and not (row['input_N'] and row['input_F']),'Wrong isolated controls')
                for shoulder in ('near','far'):
                    asset=next(v for v in shoulders['assets'] if v['side'].lower()==shoulder and v['frame']==frame)
                    expected_drawn=row['input_C'] and not (row['input_N'] and shoulder=='far') and not (row['input_F'] and shoulder=='near')
                    require(a[shoulder+'_shoulder_ready'] and a[shoulder+'_shoulder_path']==asset['object_path'] and a[shoulder+'_shoulder_drawn']==expected_drawn,'Missing/wrong actual separate shoulder source')
                for part,component in (('bracer','NearBracer'),('shin','NearShin')):
                    asset=next(v for v in limbs['assets'] if v['component']==component and v['frame']==frame)
                    expected_drawn=row['input_L'] and not (row['input_B'] and part=='shin') and not (row['input_G'] and part=='bracer')
                    require(a['near_'+part+'_ready'] and a['near_'+part+'_path']==asset['object_path'] and a['near_'+part+'_frame']==frame and a['near_'+part+'_drawn']==expected_drawn,'Missing/wrong actual separate near '+part+' source/phase/choice')
                mode='off' if not row['input_L'] else 'bracer' if row['input_B'] else 'shin' if row['input_G'] else 'both'
                k=(row['hero_dark_position'],side,mode);require(k in combinations,'Unexpected near-limb combination');combinations[k]|=1<<frame
                if previous and previous[0]==k and previous[1]==3 and frame==0 and sample==previous[2]+1:wraps[k]+=1
                previous=(k,frame,sample)
            else:
                require(not a['chest_texture_ready'] and not a['chest_drawn'] and not a['chest_path'],'Chest incorrectly applied to monster')
                require(all(not a[k] for k in ('near_shoulder_ready','far_shoulder_ready','near_shoulder_drawn','far_shoulder_drawn','near_shoulder_path','far_shoulder_path')),'Shoulders incorrectly applied to monster')
                require(all(not a['near_'+part+'_'+field] for part in ('bracer','shin') for field in ('ready','drawn','path')) and a['near_bracer_frame']==a['near_shin_frame']==-1,'Near limbs incorrectly applied to monster')
    require(all(v==15 for v in combinations.values()) and all(v>=1 for v in wraps.values()),'Every4-frame cycle and at least one wrap in sixteen combinations not observed')
    for key in ('A','D','W','C','S','J','K','E','Q','T','R','Enter','SpaceBar','LeftShift','L','B','G'):
        require(any(v['key']==key and v['down'] for v in report['normal_input_requests']) and any(v['key']==key and not v['down'] for v in report['normal_input_requests']),'Missing actual normal input press/release: '+key)
    return {'observations':len(rows),'duration_s':duration,'sixteen_combination_masks':{str(k):v for k,v in combinations.items()},'actual_wraps':{str(k):v for k,v in wraps.items()},'actual_gameplay_equipping':False}

def main():
    p=argparse.ArgumentParser();p.add_argument('--archive',default='');p.add_argument('--manifest',required=True);p.add_argument('--preflight-only',action='store_true');args=p.parse_args()
    require(hashlib.sha256(BASE.read_bytes()).hexdigest()==BASE_SHA,'Native pixel auditor changed')
    native=load('shoulder_lossless_native_audit',BASE)
    chest=load('shoulder_actual_chest_sources',Path(__file__).with_name('ue_fairytale_chest_lookdev_checks.py'))
    shoulder_checks=load('limb_baseline_shoulders',Path(__file__).with_name('ue_fairytale_shoulder_lookdev_checks.py'))
    checks=load('limb_frozen_sources',Path(__file__).with_name('ue_fairytale_limb_lookdev_v002_checks.py'))
    require(Path(args.manifest).resolve()==checks.MANIFEST.resolve(),'Wrong manifest')
    manifest=chest.preflight(require_unused=False);shoulders=shoulder_checks.preflight(require_unused=False);limbs=checks.preflight(require_unused=False)
    native.validate_manifest(checks.ROOT/'source-assets/production/fairytale-lookdev-v001/manifests/import-lookdev-v001.json')
    if args.preflight_only:print(json.dumps({'source_preflight':True,'source_PNGs':8,'old_packages_unchanged':889}));return
    require(bool(args.archive),'Actual archive required');archive=Path(args.archive).resolve();report_path=archive/'原件/runtime-report.json';report=json.loads(report_path.read_text(encoding='utf-8-sig'))
    print(json.dumps({'schema':'fairytale-near-limb-lookdev-runtime-audit-v2','passed':True,**validate(report,manifest,shoulders,limbs),**native.validate_native(archive,report),'manifest_sha256':checks.MANIFEST_SHA,'report_sha256':hashlib.sha256(report_path.read_bytes()).hexdigest(),'motion_reviewed':False,'limb_visibility_reviewed':False,'runtime_gameplay_identity_installed':False,'formal_complete_units':0},ensure_ascii=False))
if __name__=='__main__':main()
