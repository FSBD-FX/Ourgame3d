from pathlib import Path
import hashlib,json,re,datetime,sys
ROOT=Path('F:/Ourgame');BASE=Path(__file__).resolve().parent;SRC=ROOT/'UnrealGame/Source'
CM=ROOT/'source-assets/production/backups/v141-GuardMove7-Observer200G-v003/compiled-source-manifest.json'
EXPECTED='71efa450e6aea3d5107554ac524166c824ee253211452001662dad3facb62553'
assert hashlib.sha256(CM.read_bytes()).hexdigest()==EXPECTED
authority=json.loads(CM.read_text(encoding='utf-8-sig'));pinned={x['path']:x for x in authority['files'] if x['path'].startswith('UnrealGame/Source/')}
checks=[]
def check(label,value):
    assert value,label
    checks.append({'check':label,'passed':True})
paths=sorted(p for p in SRC.rglob('*') if p.is_file())
check('actual Source file count remains283',len(paths)==len(pinned)==283)
passes=[]
for pass_id in (1,2):
    rows=[]
    for p in paths:
        rel=p.relative_to(ROOT).as_posix();raw=p.read_bytes();row={'path':rel,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}
        check(f'pass{pass_id} exact CM source pin {rel}',row==pinned[rel])
        rows.append(row)
    passes.append(rows)
check('two source SHA passes equal',passes[0]==passes[1])
if '--verify-only' not in sys.argv:(BASE/'before-Source283-pins-v001.json').write_text(json.dumps({'schema':'HeroAir-before-Source283-pins-v001','compiled_manifest':CM.relative_to(ROOT).as_posix(),'compiled_manifest_sha256':EXPECTED,'source_files':283,'two_sha_passes_equal':True,'files':passes[0]},indent=2)+'\n',encoding='utf-8')
new=sorted((BASE/'new-source').rglob('*'));new=[p for p in new if p.is_file()]
check('five authorized Stage0 sources only',len(new)==5)
test=BASE/'new-source/Tests/DungeonFairytaleSwordAirV001Tests.cpp';text=test.read_text(encoding='utf-8')
check('three registered new groups',text.count('IMPLEMENT_SIMPLE_AUTOMATION_TEST(')==3)
check('exactly one TARGET per new group',all(x.count('TARGET Stage0 RED:')==1 for x in text.split('IMPLEMENT_SIMPLE_AUTOMATION_TEST(')[1:]))
check('all three TARGET failures immediately return',all(re.search(r'if\(!TestTrue\(TEXT\("TARGET Stage0 RED:[^\n]+return false;',x) for x in text.split('IMPLEMENT_SIMPLE_AUTOMATION_TEST(')[1:]))
check('no misspelled WA state accessor','GetWeaponActionState' not in text and 'GetWeaponActionsState' in text)
check('actual Space/E/Enter and central fixture use',all(t in text for t in ['W.Pulse(EKeys::SpaceBar)','W.Pulse(EKeys::E)','Target.Pulse(EKeys::Enter)','RunCodecFixture_v001.h','W.Frame(.005f)']))
check('None6 and LGT9 are explicit',all(t in text for t in ['Light?9:6','for(bool Light:{false,true})','Residents.Num()==49']))
stub=(BASE/'new-source/DungeonFairytaleSwordAirV001.cpp').read_text(encoding='utf-8')
check('profile remains genuinely pending','static const FProfile Pending' in stub and 'SourceClosureVerified=true' not in stub)
check('Select/plan/resident Stage0 all fail closed',stub.count('return false;')==4)
for p in new:
    t=p.read_text(encoding='utf-8');bare=re.sub(r'//[^\n]*|/\*[\s\S]*?\*/|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'','',t);stack=[];pairs={')':'(',']':'[','}':'{'}
    for c in bare:
        if c in '([{':stack.append(c)
        elif c in ')]}':assert stack and stack.pop()==pairs[c],p
    check('balanced C++ delimiters '+p.name,not stack)
for row in json.loads((BASE/'existing-before-pins.json').read_text())['files']:
    p=BASE/row['candidate'];raw=p.read_bytes();check('exact candidate after pin '+p.name,len(raw)==row['after_bytes'] and hashlib.sha256(raw).hexdigest()==row['after_sha256'])
check('before actual old tests are unchanged',all(x==pinned[x['path']] for x in passes[1] if '/Tests/' in x['path']))
report={'schema':'HeroAir-Stage0-host-static-checks-v001','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'checks_count':len(checks),'checks':checks,'actual_source_written':False,'UE_run':False,'native_test_executed':False,'semantic_red_verified':False,'production_compiled':False,'candidate_source_count':5,'expected_actual_after_root_stage0':288,'expected_registered_tests_after_root_stage0':203}
if '--verify-only' not in sys.argv:(BASE/'host-static-checks-v001.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k!='checks'}))
