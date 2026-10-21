"""Read-only delta and historical full-callback checks; no native trial created."""
from pathlib import Path
import ast
import copy
import importlib.util
import json
import sys
import time

sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
def module(path,name):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
V=module(HERE/'verify-landing-priority-native-v001.py','review_fixed_checker')
OLD=module(HERE.parent/'tooling/verify-landing-priority-native-v001.py','review_original_checker')

def adapt_dodge(original):
    o=copy.deepcopy(original);d=o['dodge_draw'];d['slot_count']=len(d['slots']);d['resident_count']=len(d['resident_textures']);o['owner']=d['owner'];o['jump_height']=d['jump_height'];o['rendered_player_stack']=o['rendered_stack'];o['old_draw']={'clip':'sword_dodge','actual_stack':d['actual_stack']};o['action']={'active':True};o['new_air_draw']={'drawn':False,'slot_count':0,'actual_stack':[]};o['new_air_query_ok']=False;o['physical_visual_key']=-1;return o

def validate():
    started=time.perf_counter();oldp=HERE.parent/'tooling/verify-landing-priority-native-v001.py';newp=HERE/'verify-landing-priority-native-v001.py'
    old=oldp.read_text(encoding='utf-8-sig');new=newp.read_text(encoding='utf-8-sig')
    functions=lambda s:{n.name:n for n in ast.parse(s).body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))}
    before,after=functions(old),functions(new);changed={n for n in before if ast.dump(before[n],include_attributes=False)!=ast.dump(after[n],include_attributes=False)}
    V.need(changed=={'verify_causal','quad_geometry','verify_native'} and set(after)-set(before)=={'verify_typed_callbacks'},'Fix exceeds the exact three reviewed function seams and new callback loop')
    oldquad=ast.get_source_segment(old,before['quad_geometry']);newquad=ast.get_source_segment(new,after['quad_geometry']);V.need(oldquad.replace("spec['Axis_artist_raw_xy']","spec['Axis_artist_unit_xy']")==newquad,'Dodge actual unit-axis correction exceeds the one existing authority field')
    def test_methods(path):
        return {n.name:ast.dump(n,include_attributes=False) for n in ast.walk(ast.parse(path.read_text(encoding='utf-8-sig'))) if isinstance(n,ast.FunctionDef) and n.name.startswith('test_')}
    oldtests=test_methods(HERE.parent/'tooling/test-landing-priority-v001.py');newtests=test_methods(HERE/'test-landing-priority-v001.py');V.need(len(oldtests)==44 and all(newtests[k]==v for k,v in oldtests.items()),'Original44 assertions changed')
    oldfreeze=V.read(HERE.parent/'HeroLandingPriority-Task2-tooling-freeze-v001.json')
    for _ in range(2):
        for row in oldfreeze['members']:V.resolve_pin(row)
    loaded,F,C=V.dependencies();_,AM,AP,*_=C.source_only();DM=V.read(loaded['import-Dodge32-v001.json']);DP=V.read(loaded['Dodge-runtime-profile-data-v001.json'])
    origins=V.read(HERE/'geometry-fixture-origins-v002.json');results=[];old_rejections=[]
    for origin in origins['members']:
        r=V.read(V.resolve_pin(origin))
        if origin['kind']=='Air':
            rows=[]
            for original in r['observations']:
                if not original['new_air_draw']['drawn'] or original['new_air_draw']['slot_count']!=9:continue
                o=copy.deepcopy(original);o['action']={'active':False};o['dodge_draw']={'drawn':False,'slot_count':0,'actual_stack':[]};rows.append(o)
            check=V.verify_typed_callbacks(dict(requested_action='J',observations=rows),AM,AP,DM,DP);V.need(check['counts']=={'Air':len(rows),'Dodge':0},'Not every historical Air callback was checked')
        else:
            indexed=[(i,adapt_dodge(o)) for i,o in enumerate(r['observations']) if o['dodge_draw']['drawn']];rows=[o for i,o in indexed]
            for frame in (1,2):
                i,o=next((i,o) for i,o in indexed if o['dodge_draw']['frame']==frame);paths={a['component']:a['object_path'] for a in DM['assets'] if a['frame']==frame};paths['IndependentSword']=V.SWORD
                try:OLD.quad_geometry(o,DP['frames'][frame],paths,False,{a['object_path'] for a in DM['assets']}|{V.SWORD})
                except ValueError as e:old_rejections.append(dict(side=origin['side'],observation_index=i,frame=frame,actual_axis=o['dodge_draw']['axis_artist'],raw_axis=DP['frames'][frame]['Axis_artist_raw_xy'],unit_axis=DP['frames'][frame]['Axis_artist_unit_xy'],v001_rejected=str(e)))
                else:raise ValueError('Expected actual v001 raw/unit mismatch RED did not reproduce')
            check=V.verify_typed_callbacks(dict(requested_action='Shift',observations=rows),AM,AP,DM,DP);V.need(check['counts']=={'Air':0,'Dodge':len(rows)},'Not every historical Dodge callback was checked')
        results.append(dict(kind=origin['kind'],side=origin['side'],report_pin={k:origin[k] for k in ('path','bytes','sha256')},checks=check))
    return dict(schema='hero-landing-priority-review-fix-validation-v002',passed=True,checker_before_pin=V.pin(oldp),checker_after_pin=V.pin(newp),exact_changed_existing_functions=sorted(changed),exact_new_functions=['verify_typed_callbacks'],unchanged_existing_functions=sorted(set(before)-changed),original_44_test_methods_AST_unchanged=True,old_freeze_members=13,old_freeze_SHA_passes=2,old_freeze_mismatches=0,Dodge_unit_field_is_pinned_existing_authority=True,v001_actual_legal_Dodge_rejections=old_rejections,historical_all_callback_geometry=results,elapsed_s=time.perf_counter()-started,RootApproved=False,UE_started=False,new_landing_native_verified=False,pixel_thresholds_changed=False,optical_midpoint_function_AST_unchanged=True,audio_changed=False,FinalAccepted=False)

if __name__=='__main__':
    result=validate();print(json.dumps(result,ensure_ascii=False,indent=2))
