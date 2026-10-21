from pathlib import Path
import hashlib,json,difflib

HERE=Path(__file__).resolve().parent
PROJECT=HERE.parents[3]
assert PROJECT.name=='Ourgame'
def pin(path):
    data=path.read_bytes()
    return {'path':path.relative_to(PROJECT).as_posix(),'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}
def write(name,value):
    p=HERE/name
    assert not p.exists(),f'frozen output exists: {p}'
    p.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

stage=json.loads((HERE/'stage0-freeze-v001.json').read_text())
for item in stage['files']:
    p=PROJECT/item['path'];assert pin(p)==item
baseline=json.loads((HERE/'baseline-pins-v001.json').read_text())
actual=[]
for item in baseline['actual_source_files']:
    p=PROJECT/item['path'];observed=pin(p)
    actual.append({'expected':item,'actual':observed,'unchanged':observed==item})
assert all(item['unchanged'] for item in actual),'Root Source changed; do not overwrite a new baseline'

paths=['Body','BodyRest','NearArmWithoutHand','HelmetForeground','NearHand','ShoulderFar','Chest','ShoulderNear']
template={
 'schema':'fairytale-ground-walk-required-art-input-v001',
 'status':'PENDING_ROOT_MEASUREMENTS_AND_IMPORT_RECEIPTS',
 'runtime_profile_configured':False,
 'animation_label':'walk_distance_v001',
 'immutable_compiled_profile_only':True,
 'cycle_distance_world_units':None,'cycle_seconds':None,
 'source_canvas':[512,512], 'draw_canvas':'72*512/416', 'independent_sword_scale':.5,
 'phase_durations_seconds':[None]*6,
 'assembly_freeze':None,'source_import_receipts':[],
 'phases':[{'index':i,'whole_body_reference':None,'component_object_paths':{name:None for name in paths if name!='Body'},
    'source_file_and_rgba_sha256':None,'root_source_px':None,'grip_source_px':None,'axis_source_vector':None,
    'support_foot_identity':None,'contact_source_px':None,'contact_interval':None,'measurements_supplied':False} for i in range(6)],
 'no_fabricated_values':True,'foot_lock_implemented':False,
 'required_proof':'Measured contact interval/cycle fraction and projection, closed NearHand six phases, exact four-part body closure plus matched LGT three parts, object/receipt hashes, both-facing native draw and transitions.'}
write('required-art-input-v001.json',template)

def patch(label,from_stage):
    chunks=[]
    for p in sorted((HERE/'production-source').iterdir()):
        old=(HERE/'stage0-source'/p.name) if from_stage and (HERE/'stage0-source'/p.name).is_file() else HERE/'baseline-source'/p.name
        old_text=old.read_text(encoding='utf-8-sig').splitlines(keepends=True) if old.is_file() else []
        new_text=p.read_text(encoding='utf-8').splitlines(keepends=True)
        target='UnrealGame/Source/CodexDungeon/'+p.name
        chunks.extend(difflib.unified_diff(old_text,new_text,fromfile='a/'+target if old.is_file() else '/dev/null',tofile='b/'+target))
    target=HERE/label;assert not target.exists()
    target.write_text(''.join(chunks),encoding='utf-8',newline='\n')
patch('production-from-stage0-v001.patch',True)
patch('production-from-baseline-v001.patch',False)
result={
 'schema':'fairytale-ground-walk-candidate-verification-v001',
 'standalone':{'compiler':'MSVC 19.38.33130 /std:c++17 /EHsc /MT','compile_exit_code':0,'run_exit_code':0,
    'stdout':'phase checks 34 PASS; numeric fixture only; no UE/native/art claim',
    'meaningful_checks':'policy domain, output rejection atomicity, zero/huge distances, split distances, six intervals, complete-cycle and tiny stride finite boundary',
    'source':pin(HERE/'standalone-phase-v001.cpp'),'header':pin(HERE/'production-source/DungeonGroundWalkPhase.h'),
    'executable':pin(HERE/'standalone-phase-v001.exe')},
 'actual_source_before_after':actual,
 'stage0_freeze_unchanged':True,'frozen_tests_unchanged':True,
 'new_animation_label':'walk_distance_v001','legacy_walk_time_reinterpreted':False,
 'runtime_art_profile_configured':False,'native_tests_compiled_or_run':False,'UE_UBT_run':False,
 'actual_Source_tools_or_media_mutated':False,'foot_lock_implemented_or_passed':False}
write('verification-v001.json',result)
selected=sorted((HERE/'production-source').iterdir())+[
 HERE/'production-from-stage0-v001.patch',HERE/'production-from-baseline-v001.patch',HERE/'required-art-input-v001.json',
 HERE/'contract-v001.md',HERE/'verification-v001.json',HERE/'standalone-phase-v001.cpp',HERE/'standalone-phase-v001.exe',
 HERE/'build-production-v001.py',HERE/'freeze-production-v001.py',HERE/'new-tests/DungeonFairytaleGroundWalkTests.cpp']
freeze={
 'schema':'fairytale-ground-walk-production-candidate-freeze-v001',
 'baseline':pin(HERE/'baseline-pins-v001.json'),'stage0_freeze':pin(HERE/'stage0-freeze-v001.json'),
 'files':[pin(p) for p in selected],
 'tests_identical_to_stage0':True,'new_test_groups':stage['new_test_groups'],
 'api':'bool ADungeonFighter::QueryCompletedGroundMotion(FDungeonCompletedGroundMotion&) const',
 'new_saved_owner_fields':[],'animation_label':'walk_distance_v001','old_walk_clock_semantics':'historical wall-time unchanged',
 'actual_native_passes':0,'formal_complete_units':0,
 'runtime_profile_configured':False,'requires_Root_art_and_measurement_table_before_Walk_enable':True,
 'current_full161_is_historical_baseline_only':True,
 'apply_order':'Root real Stage0 clean RED; review production candidate; unchanged tests real GREEN/full current registry; separately freeze measured art profile and native visual acceptance',
 'limitations':['No actual UE/UBT/native execution here','Numeric phase tests do not approve runtime stride/markers/art',
    'No continuous foot lock/root compensation','Saved phase uses existing float precision','New configured-label/profile native acceptance cases remain pending'],
 'write_scope':'only this candidate directory; no ActualSource/tools/media/ledger/README edits'}
write('production-freeze-v001.json',freeze)
print(json.dumps(pin(HERE/'production-freeze-v001.json'),ensure_ascii=False))
