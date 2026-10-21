from pathlib import Path
import ast,datetime,hashlib,json,re,sys
ROOT=Path('F:/Ourgame');BASE=Path(__file__).resolve().parent;STAGE=BASE.parent/'stage0';AUDIO=BASE.parent.parent/'audio-capture-helper-candidate-v001'
checks=[]
def pin(p):
    d=p.read_bytes();return {'bytes':len(d),'sha256':hashlib.sha256(d).hexdigest()}
def check(label,ok):
    assert ok,label
    checks.append({'check':label,'passed':True})
stage=STAGE/'HeroAir-Stage0-candidate-freeze-v001.json';audio=AUDIO/'native-main-submix-capture-helper-freeze-v001.json'
check('frozen Stage0 dependency exact',pin(stage)['sha256']=='37513295d00ee57f1726260c0da10a296e378962cb1d4cbe21bb6e3010d42c2a')
check('frozen audio helper dependency exact',pin(audio)['sha256']=='91e1a74f78dcf1b712d121930da8e08e3543254d4227d43c2b774df730089c3e')
expected={r['path']:r for r in json.loads((STAGE/'before-Source283-pins-v001.json').read_text())['files']}
for r in json.loads((STAGE/'stage0-admission-index-v001.json').read_text())['files']:expected[r['actual']]={'path':r['actual'],**pin(STAGE/r['candidate'])}
for r in json.loads(audio.read_text())['files']:
    if r['path'].startswith('new-source/'):
        name=Path(r['path']).name;rel='UnrealGame/Source/CodexDungeon/'+name;expected[rel]={'path':rel,**pin(AUDIO/r['path'])}
actual=sorted(p for p in (ROOT/'UnrealGame/Source').rglob('*') if p.is_file());check('Root-admitted Stage0 plus helper current Source290',len(actual)==len(expected)==290)
passes=[]
for pass_id in (1,2):
    rows=[]
    for p in actual:
        rel=p.relative_to(ROOT).as_posix();r={'path':rel,**pin(p)};check(f'pass{pass_id} exact admitted source {rel}',r==expected[rel]);rows.append(r)
    passes.append(rows)
check('two current Source290 SHA passes equal',passes[0]==passes[1])
if '--verify-only' not in sys.argv:(BASE/'before-Source290-pins-v001.json').write_text(json.dumps({'schema':'HeroAir-baseline-before-Source290-pins-v001','source_files':290,'two_sha_passes_equal':True,'scope':'Actual source values after Root Stage0/helper admission; not a compiled-state claim','baseline_compiled_manifest_sha256':'71efa450e6aea3d5107554ac524166c824ee253211452001662dad3facb62553','stage0_source_freeze_sha256':pin(stage)['sha256'],'audio_helper_freeze_sha256':pin(audio)['sha256'],'files':passes[0]},indent=2)+'\n',encoding='utf-8')
h=(BASE/'new-source/DungeonHeroAirProbeV001.h').read_text();cpp=(BASE/'new-source/DungeonHeroAirProbeV001.cpp').read_text()
check('two new source files only',len(list((BASE/'new-source').glob('*')))==2)
check('audio owner strongly held','UPROPERTY(Transient) TObjectPtr<UDungeonNativeMainSubmixCaptureV001> MainMixCapture' in h)
check('Recording gate before movie enable',cpp.index('Status().Phase==EDungeonNativeMixCapturePhaseV001::Recording')<cpp.index('Start=Status.StartMonotonic;Capturing=true;GIsDumpingMovie=-1'))
check('Arming not mistaken for recording','Status.StartRequested&&Status.StartMonotonic>0.' in cpp)
check('Stop owns exact helper timestamp','Stop=Actor.MainMixCapture->Status().StopMonotonic' in cpp)
check('final callback stops capture before asynchronous terminal report','Next(9);BeginStop(Actor)' in cpp and 'if(Stopping){if(!Actor.MainMixCapture||Actor.MainMixCapture->IsTerminal())Finalize(Actor);return;}' in cpp)
check('stopped callbacks cannot append offsets','if(Stopped||Stopping)return;' in cpp)
check('JSON actual atomic Windows no-replace','CREATE_NEW' in cpp and 'WriteNewUTF8(Path,Text)' in cpp and 'FILEWRITE_NoReplaceExisting' not in cpp and 'FlushFileBuffers' in cpp)
check('no invalid TSharedRef ToSharedRef','R.ToSharedRef()' not in cpp and 'FJsonSerializer::Serialize(R,Writer)' in cpp)
check('startup deadline before incomplete player binding return',cpp.index('Now-WarmStarted>12.')<cpp.index('if(!P||!V.Bound||!V.RunGuid.IsValid())return'))
check('EndPlay failure cleanup and report','Proof->BeginStop(*this);Proof->Finalize(*this)' in cpp)
check('no native game state assignment',not re.search(r'(?:P|Player)->(?:JumpHeight|JumpVelocity|Health|bAIEnabled|LandingVisualAge|AnimationTime|Facing)\s*=(?!=)',cpp))
check('no direct jump/position/clock/AI stepping',all(x not in cpp for x in ['->StartJump(', '->SetActorLocation(', '->ResetFighter(', '->SimulateMotion(', '->StepTo(', '->bAIEnabled=']))
check('exact Knight public diagnostic only',cpp.count('->ApplyCombatHit(')==1 and 'Knight->ApplyCombatHit(' in cpp and 'DungeonHeroAirClearKnightDiagnostic' in cpp)
check('normal Space counted exactly twice by flow',cpp.count('++JumpInputs')==2 and 'JumpInputs==2&&AirTransitions==2&&LandingTransitions==2' in cpp)
check('baseline scope never claims new Air acceptance','SetBoolField(TEXT("new_air_passed"),false)' in cpp and 'SetBoolField(TEXT("final_accepted"),false)' in cpp)
check('bareReady0 uses actual submitted body-only stack','B.DrawStack.Num()==1&&B.DrawStack[0]==B.TexturePath' in cpp and 'A.Slots.IsEmpty()&&!A.Drawn' in cpp)
review=json.loads((BASE/'independent-static-review-v001.json').read_text())
for r in review['reviewed_files']:check('exact independent reviewed file '+r['path'],pin(BASE/r['path'])=={'bytes':r['bytes'],'sha256':r['sha256']})
for p in (BASE/'new-source').glob('*'):
    t=p.read_text();t=re.sub(r'//[^\n]*|/\*[\s\S]*?\*/|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'','',t);stack=[];pairs={')':'(',']':'[','}':'{'}
    for c in t:
        if c in '([{':stack.append(c)
        elif c in ')]}':assert stack and stack.pop()==pairs[c],p
    check('balanced C++ delimiters '+p.name,not stack)
for p in BASE.glob('*.py'):ast.parse(p.read_text());check('Python AST '+p.name,True)
for r in json.loads((BASE/'existing-before-pins.json').read_text())['files']:
    check('HUD source still exact baseline before pin',pin(ROOT/r['path'])=={'bytes':r['bytes'],'sha256':r['sha256']})
    check('HUD candidate exact after pin',pin(BASE/r['candidate'])=={'bytes':r['after_bytes'],'sha256':r['after_sha256']})
report={'schema':'HeroAir-baseline-host-static-checks-v001','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'checks_count':len(checks),'checks':checks,'actual_source_written':False,'UE_run':False,'compiled':False,'native_passed':False,'auditioned':False,'before_source_files':290,'expected_after_root_admission_source_files':292,'expected_registered_tests':203}
if '--verify-only' not in sys.argv:(BASE/'host-static-checks-v001.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k!='checks'}))
