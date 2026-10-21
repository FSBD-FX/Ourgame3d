from pathlib import Path
import ast,difflib,hashlib,json,datetime,subprocess,sys
ROOT=Path('F:/Ourgame');BASE=Path(__file__).resolve().parent;SRC=ROOT/'UnrealGame/Source/CodexDungeon'
CM=ROOT/'source-assets/production/backups/v142-HeroAir6-Stage0-200G3R-v001/compiled-source-manifest.json';EXPECTED='64d4eee9cca114ecd5161bf693d3091b55241370808ad2110c417984b8f5e877'
assert hashlib.sha256(CM.read_bytes()).hexdigest()==EXPECTED
cm=json.loads(CM.read_text(encoding='utf-8-sig'));assert cm['source_files']==290 and cm['passed']==200 and cm['failed']==3 and cm['all_old200_passed'] and cm['only_three_expected_target_errors']
authority={r['path']:r for r in cm['files']};tree=ast.parse((BASE/'prepare-query-select-v001.py').read_text())
embedded={n.targets[0].id:ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and isinstance(n.targets[0],ast.Name) and n.targets[0].id in ('QUERY','SELECT')}
def function(text,signature):
    a=text.index(signature);b=text.index('{',a);depth=0
    for end in range(b,len(text)):
        if text[end]=='{':depth+=1
        elif text[end]=='}':
            depth-=1
            if depth==0:return text[a:end+1]
    raise AssertionError(signature)
rows=[]
for name,key,sig in [('DungeonFighter.cpp','QUERY','bool ADungeonFighter::QueryHeroNonAttackAir('),('DungeonFairytaleSwordAirV001.cpp','SELECT','bool Select(')]:
    original=(SRC/name).read_bytes();rel='UnrealGame/Source/CodexDungeon/'+name;record=authority[rel]
    assert len(original)==record['bytes'] and hashlib.sha256(original).hexdigest()==record['sha256']
    candidate=BASE/'existing-source'/name;result=candidate.read_bytes();assert function(result.decode('utf-8-sig').replace('\r\n','\n'),sig)==embedded[key]
    (BASE/(name+'.patch')).write_text(''.join(difflib.unified_diff(original.decode('utf-8-sig').splitlines(True),result.decode('utf-8-sig').splitlines(True),fromfile='a/'+rel,tofile='b/'+rel)),encoding='utf-8',newline='')
    rows.append({'actual':rel,'before_bytes':len(original),'before_sha256':hashlib.sha256(original).hexdigest(),'candidate':candidate.relative_to(BASE).as_posix(),'after_bytes':len(result),'after_sha256':hashlib.sha256(result).hexdigest()})
data={'schema':'HeroAir-production-query-select-preparation-pins-v001','actual_semantic_red_compiled_manifest':CM.relative_to(ROOT).as_posix(),'actual_semantic_red_compiled_manifest_sha256':EXPECTED,'Root_verified_old200_green_three_semantic_target_red':True,'source_profile_pending':True,'atomic_plan_and_presenter_pending':True,'actual_source_written':False,'native_query_compiled_in_UE':False,'files':rows}
(BASE/'before-after-pins-v001.json').write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
completed=subprocess.run(['cmd.exe','/d','/c',str(BASE/'host/build-and-run-host-select.cmd')],capture_output=True,text=True);assert completed.returncode==0,completed.stdout+completed.stderr
result=json.loads(next(x for x in completed.stdout.splitlines() if x.startswith('{')));assert result['actual_select_cpp_cases']==39 and result['failed']==0
(BASE/'host-select-verification-v001.json').write_text(json.dumps({'schema':'HeroAir-actual-Select-standalone-host-checks-v001','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'compiler':'installed MSVC14.38.33130 x64 with Windows SDK10.0.19041.0; direct INCLUDE/LIB because vcvars batch absent','actual_cpp':rows[1]['after_sha256'],'test_source_sha256':hashlib.sha256((BASE/'host/host-select-cases-v001.cpp').read_bytes()).hexdigest(),'shim_header_sha256':hashlib.sha256((BASE/'host/shim/DungeonFairytaleSwordAirV001.h').read_bytes()).hexdigest(),'result':result,'UE_run':False,'native_owner_query_executed':False,'resource_or_art_verified':False},indent=2)+'\n',encoding='utf-8')
print(json.dumps({'final_candidate_copies_patch_generator_pins_agree':True,'source_files':len(rows),'actual_select_cpp_cases':39,'failed':0,'actual_source_written':False,'production_complete':False}))
