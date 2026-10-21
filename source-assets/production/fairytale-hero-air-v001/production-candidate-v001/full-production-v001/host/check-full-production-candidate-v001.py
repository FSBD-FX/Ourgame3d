from pathlib import Path
import json,hashlib,difflib,ast
ROOT=Path('F:/Ourgame');BASE=Path(__file__).resolve().parents[1];checks=[]
def text(p):return p.read_text(encoding='utf-8')
def check(label,ok):
 checks.append({'check':label,'passed':bool(ok)})
 assert ok,label
before=json.loads((BASE/'before-Source292-pins-v001.json').read_bytes());second={r['path']:r['sha256'] for r in json.loads((BASE/'host/independent-Source292-GetFileHash-v001.json').read_text(encoding='utf-8-sig'))}
check('all292 independent SHA inventory exactly matches',len(second)==292 and len(before['files'])==292)
for r in before['files']:
 b=(ROOT/r['path']).read_bytes();check('actual before '+r['path'],len(b)==r['bytes'] and hashlib.sha256(b).hexdigest()==r['sha256']==second[r['path']])
index=json.loads((BASE/'full-production-admission-index-v001.json').read_bytes());check('exact5 existing plus2new admission',len(index['files'])==7 and sum(r['kind']=='existing' for r in index['files'])==5 and sum(r['kind']=='new' for r in index['files'])==2)
check('all actual test sources excluded from admission',not any('/Tests/' in r['actual'] for r in index['files']))
check('five bounded existing names',set(Path(r['actual']).name for r in index['files'] if r['kind']=='existing')=={'DungeonFighter.cpp','DungeonFairytaleSwordAirV001.cpp','DungeonHUD.h','DungeonHUD.cpp','DungeonFairytaleSwordPresentation.cpp'})
for r in index['files']:
 b=(BASE/r['candidate']).read_bytes();check('candidate final pin '+r['candidate'],len(b)==r['after_bytes'] and hashlib.sha256(b).hexdigest()==r['after_sha256'])
 if r['kind']=='existing':
  old=(BASE/'before-source'/Path(r['actual']).name).read_bytes();check('exact existing before '+r['candidate'],len(old)==r['before_bytes'] and hashlib.sha256(old).hexdigest()==r['before_sha256'])
  patch=''.join(difflib.unified_diff(old.decode().splitlines(keepends=True),b.decode().splitlines(keepends=True),fromfile='actual/'+Path(r['actual']).name,tofile='candidate/'+Path(r['actual']).name))
  check('patch byte correspondence '+r['candidate'],(BASE/(r['candidate']+'.patch')).read_bytes()==patch.encode())
 else:check('new actual path absent '+r['actual'],not (ROOT/r['actual']).exists())
check('Fighter immutable frozen Query exact',(BASE/'existing-source/DungeonFighter.cpp').read_bytes()==(BASE.parent/'query-and-select-v001/existing-source/DungeonFighter.cpp').read_bytes())
hud=text(BASE/'existing-source/DungeonHUD.cpp');hh=text(BASE/'existing-source/DungeonHUD.h');sword=text(BASE/'existing-source/DungeonFairytaleSwordPresentation.cpp');presenter=text(BASE/'new-source/DungeonFairytaleSwordAirPresentationV001.cpp');plan=text(BASE/'existing-source/DungeonFairytaleSwordAirV001.cpp')
check('strong UPROPERTY Air texture cache','UPROPERTY() TMap<FString,TObjectPtr<UTexture2D>> FairytaleSwordAirTextures;' in hh)
check('startup original render flush after Air load',hud.index('LoadFairytaleSwordAirTrial();')<hud.index('FlushRenderingCommands();'))
check('BeginPlay finish actual texture compilation','FTextureCompilingManager::Get().FinishCompilation(Pending);' in presenter)
check('draw callback Trace reset before Super/noCanvas',hud.index('FairytaleSwordAirDraw=FDungeonFairytaleSwordAirDrawV001();',hud.index('void ADungeonHUD::DrawHUD()'))<hud.index('Super::DrawHUD();'))
check('restore Trace reset without extra epoch/timer','ActorQuads.Reset();FairytaleGuardMoveRigDraws.Reset();\n    FairytaleSwordAirDraw=FDungeonFairytaleSwordAirDrawV001();'.replace('\\n','\n') in hud)
check('Air after Death/Hurt/Dodge dispatch',sword.index('DrawFairytaleSwordAirBody(F)')>sword.index('DrawFairytaleSwordDodgeBody(F))return true;')>sword.index('DrawFairytaleSwordHurtBody(F)')>sword.index('DrawFairytaleSwordDeathBody(F)'))
check('all49 preflight before only actual DrawTexture site',presenter.count('DrawTexture(')==1 and presenter.index('ValidateResidentSet(Profile(),Trace.ResidentTextures')<presenter.index('if(!Trace.AtomicPreflightReady)')<presenter.index('DrawTexture('))
check('actual Slots appended only after native submission',presenter.index('Trace.Slots.Add(')>presenter.index('DrawTexture('))
check('draw path cache only',presenter.index('LoadObject<')<presenter.index('bool ADungeonHUD::DrawFairytaleSwordAirBody') and presenter[presenter.index('bool ADungeonHUD::DrawFairytaleSwordAirBody'):].count('LoadObject<')==0)
check('preflight before actual Canvas check then DrawTexture',presenter.index('if(!Trace.AtomicPreflightReady)')<presenter.index('if(!Canvas)')<presenter.index('DrawTexture('))
check('same quad floats in trace and submission',all(s in presenter for s in ['Quad.Top={float(Top.X),float(Top.Y)}','Quad.Size={float(Width),float(Width)}','double(float(Plan.WeaponAngle))','Quad.RotationPivot=Sword?Plan.SwordPivotUV','float(Quad.RotationDegrees),Quad.RotationPivot']))
check('source preloading all48 plus sword49',all(s in presenter for s in ['for(const auto& Frame:Profile().Frames)for(const auto& Layer:Frame.Layers)Load(Layer.TexturePath);','Load(Profile().SwordTexturePath);','for(const auto& Frame:Profile().Frames)for(const auto& Layer:Frame.Layers)AddResident(Layer.TexturePath);','AddResident(Profile().SwordTexturePath);']))
check('None actual6 Lightactual9','P.NonemptyDrawCount!=(Light?9:6)' in plan and 'if(!Slot.Enabled)continue;' in presenter)
check('no obsolete Armor None enum','Armor::None' not in plan)
check('native float corner collapse required','Right!=X&&Bottom!=Y' in plan)
check('no canvas clamp for source Root',not any(s in plan for s in ['Root.X<0','Root.Y<0','Root.Y>512','Clamp(Frame.Root','Clamp(F.Root']))
check('no invented jump action event/serial/timer',not any(s in presenter+plan for s in ['StartJump(','EmitEvent(','NotifyTakeoff(','NotifyLand(','JumpSerial','TakeoffId','SourceEventID']))
check('actual projection double Ground->float Screen','Screen(float(GroundPoint.X),float(GroundPoint.Y))' in presenter)
check('all actual native priorities before Air branch',all(s in presenter for s in ['Fighter->AttackTime>0.f','GetMeleeCombatState().Action.Active','GetWeaponSkillAction().Active','GetDodgeState().Phase!=DungeonDodge::EPhase::Idle','GetArmorChangeRemaining()>0.f','GetEquipmentActionDeadline()>0.','AnimationName==TEXT("hurt")']))
check('Root record import scope honest',json.loads((BASE/'source-preparation-binding-v001.json').read_bytes())['Root_source_import_approval']['TrialAllowed'] is False)
check('true data seam exact native-ready',hashlib.sha256((BASE/'new-source/DungeonFairytaleSwordAirDataV001.inl').read_bytes()).hexdigest()=='a0b179e2132674e0bad302809802ff2a68b5e9d486909762fdb322213a896191')
host=[json.loads(l) for l in (BASE/'host/actual-cpp-host-results-v001.jsonl').read_text(encoding='utf-8-sig').splitlines()];check('actual CPP39+158 value cases real execution',len(host)==2 and host[0]['actual_select_cpp_cases']==39 and host[1]['actual_full_cpp_value_cases']==158 and all(r['failed']==0 for r in host))
ast.parse(text(BASE/'root-admit-full-production-v001.py'));check('Root helper syntax',True)
report={'schema':'HeroAir-full-production-host-static-and-cpp-checks-v001','checks':checks,'checks_passed':len(checks),'failed':0,'actual_cpp_host_cases':197,'actual_cpp_host_failed':0,'ue_compiled':False,'actual_source_changed':False,'actual_import_verified_by_this_candidate':False,'native_draw_verified':False,'FinalAccepted':False,'scope':'Actual source pins, candidate boundaries, real CPP/value seams and wiring static checks only; not actual Unreal actors/resources/GPU/pixels/audio/art acceptance.'}
(BASE/'host/full-production-host-checks-v001.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print('host static checks',len(checks),'plus actualCPP197 value cases: PASS')
