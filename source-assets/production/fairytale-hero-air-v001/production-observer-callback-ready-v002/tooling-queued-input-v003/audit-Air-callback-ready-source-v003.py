"""Readonly exact delta audit: callback-ready source + queued checker.
Only an optional NEW JSON report is written. Never modifies the checked files.
"""
from pathlib import Path
import argparse
import ast
import difflib
import hashlib
import json
import sys
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent))
import air_production_contract_v001 as C
HERE=Path(__file__).resolve().parent
OLD=C.AIR/'production-observer-candidate-v001/tooling-freeze-relative-v002'
OLD_SOURCE_FREEZE=C.AIR/'production-observer-candidate-v001/HeroAir-production-observer-source-freeze-v001.json'
SOURCE_FREEZE=HERE.parent/'HeroAir-production-observer-callback-ready-source-freeze-v002.json'
SOURCE_FREEZE_SHA='be6e3a1cb2e6344b51bef45a872b3bfb05056f73b37cbf923ebb33474422a36f'
CPP_SHA='75dd41c0b615363e82a4b18d3dcfa018bc966ea371cf4510126ed0c0fe701da3'
OLD_FLOW_BLOCK="""            before = obs[i - 1] if i else None
            C.need(before is not None and before['wall_offset_s'] < trigger['wall_offset_s'] <= offset
                   and before['sim'] <= trigger['sim'] <= o['sim']
                   and trigger['before_H'] == trigger['before_V'] == 0
                   and trigger['after_H'] == 0 and trigger['after_V'] == 630, 'Actual ordinary Space input must precede its first native airborne callback')
"""

def cut(text,start,end):
 C.need(text.count(start)==text.count(end)==1,'Unique source delta anchor required')
 a=text.index(start);b=text.index(end,a);return text[:a]+text[b:]

def restore_cpp_to_baseline(new,old):
 new=cut(new,' // This token is created only by an actual completed screenshot callback.',' TArray<JV> Inputs,Steps,Observations,Offsets,DiagnosticHits,StartupTextures;')
 new=cut(new,'  if(Game.IsValid())\n  {\n   const auto& InputView=Game->GetEquipmentView();','  if(P){O->SetNumberField(TEXT("before_H"),P->JumpHeight);')
 new=cut(new,'  // HUD.Tick prerequisites do not wait for DrawHUD.','  if(Pose>=0)')
 strengthened='LightReadyCallbackObserved&&LightReadyCallbackConsumed&&JumpInputs==3'
 C.need(new.count(strengthened)==1,'Only the final Need may add callback token completion')
 new=new.replace(strengthened,'JumpInputs==3',1)
 new=cut(new,'  R->SetBoolField(TEXT("LGT_completed_Ready_callback_observed"),LightReadyCallbackObserved);','  R->SetArrayField(TEXT("normal_inputs"),Inputs);')
 a=new.index('   case 5:');b=new.index('   case 6:',a)
 oa=old.index('   case 5:');ob=old.index('   case 6:',oa)
 return new[:a]+old[oa:ob]+new[b:]

def function_text(source,name):
 tree=ast.parse(source);node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name==name)
 return ast.get_source_segment(source,node)

def checker_delta(old,new):
 C.need((HERE/'air_production_contract_v001.py').read_bytes()==(OLD/'air_production_contract_v001.py').read_bytes(),'Frozen contract altered')
 oldtree,newtree=ast.parse(old),ast.parse(new)
 oldf={n.name:n for n in oldtree.body if isinstance(n,ast.FunctionDef)};newf={n.name:n for n in newtree.body if isinstance(n,ast.FunctionDef)}
 additions={'exact_base_partition_first_air','verify_queued_spaces','verify_completed_light_ready'}
 C.need(set(newf)==set(oldf)|additions,'Unexpected added/removed checker function')
 unchanged=[]
 for name in set(oldf)-{'verify_flow','main'}:
  C.need(ast.dump(oldf[name],include_attributes=False)==ast.dump(newf[name],include_attributes=False),'Unrelated checker function changed: '+name);unchanged.append(name)
 # Exact expected body edits, rather than treating all changes in verify_flow/main as allowed.
 expected=function_text(old,'verify_flow')
 expected=expected.replace("           and last_space['after_H'] == 0 and last_space['after_V'] == 630\n",'')
 C.need(OLD_FLOW_BLOCK in expected,'Frozen old queue bug block changed')
 expected=expected.replace(OLD_FLOW_BLOCK,"            C.need(queued['witnesses'][air_transitions-1]['first_air_observation'] == i, 'Queued first-air witness not this actual callback')\n")
 expected=expected.replace('    masks = [0, 0, 0]; air_transitions','    queued = verify_queued_spaces(r, require_enqueue_binding=True)\n    completed_ready = verify_completed_light_ready(r)\n    masks = [0, 0, 0]; air_transitions')
 expected=expected.replace('                Ready_join_frames=ready, actual_adjacent_rejump=joins[0], NoArmor_is_formal20_pair=False)',
  '                Ready_join_frames=ready, actual_adjacent_rejump=joins[0], queued_input_causality=queued,\n                completed_LGT_Ready_handoff=completed_ready, NoArmor_is_formal20_pair=False)')
 C.need(expected==function_text(new,'verify_flow'),'verify_flow has edits beyond explicit queued/Ready delta')
 expected=function_text(old,'main')
 expected=expected.replace("    modes.add_argument('--source-only'","    modes.add_argument('--queued-component', action='store_true')\n    parser.add_argument('--report')\n    modes.add_argument('--source-only'",1)
 expected=expected.replace('    if a.source_only:\n',"    if a.queued_component:\n        C.need(a.report, 'Actual report JSON required for component audit')\n        report = C.read(a.report)\n        result = verify_queued_spaces(report, require_enqueue_binding=False)\n        result.update(schema='hero-Air6-queued-input-component-v003', component_passed=True,\n                      original_report_passed=report['passed'], UE_started=False, visual_reviewed=False)\n    elif a.source_only:\n",1)
 C.need(expected==function_text(new,'main'),'CLI has edits beyond explicit readonly component mode')
 oa=[n for n in oldtree.body if not isinstance(n,ast.FunctionDef)];na=[n for n in newtree.body if not isinstance(n,ast.FunctionDef)]
 C.need([ast.dump(n,include_attributes=False) for n in oa]==[ast.dump(n,include_attributes=False) for n in na],'Unrelated top-level checker code changed')
 return dict(contract_byte_identical=True,unchanged_function_AST=sorted(unchanged),verify_flow_exact_explicit_delta=True,main_exact_explicit_delta=True,top_level_AST_equal=True)

def audit():
 c=C.import_contract();sfpin=c.pin(SOURCE_FREEZE)
 C.need(sfpin['sha256']==SOURCE_FREEZE_SHA,'New source freeze pin differs')
 oldf=C.frozen(c.pin(OLD_SOURCE_FREEZE),c);newf=C.frozen(sfpin,c)
 oldpins={Path(x['path']).name:x for x in oldf['source_files']};newpins={Path(x['path']).name:x for x in newf['source_files']}
 C.need(set(oldpins)==set(newpins) and len(newpins)==3,'Only three original probe source files required')
 cpp='DungeonHeroAirProductionProbeV001.cpp'
 C.need(newpins[cpp]['sha256']==CPP_SHA,'Unreviewed new source CPP pin')
 for name in set(newpins)-{cpp}:C.need((newpins[name]['bytes'],newpins[name]['sha256'])==(oldpins[name]['bytes'],oldpins[name]['sha256']),'Header/HUD overlay changed')
 old=Path(oldpins[cpp]['path']).read_text(encoding='utf-8');new=Path(newpins[cpp]['path']).read_text(encoding='utf-8')
 C.need(restore_cpp_to_baseline(new,old)==old,'Source has changes outside explicit callback token/Key logging/case5/final Need/report fields')
 critical=['JumpInputs==3&&AirTransitions==3&&LandingTransitions==3&&NoArmorMask==63&&LightFirstMask==63&&LightSecondMask==63&&RejumpIssuedInsideLanding&&NoArmorFrames>=6&&LightFrames>=12',
 'Now-Start<12.&&Now-PhaseAt<5.','Before>=.06f&&Before<.12f','Controller->InputKey(FInputKeyParams(K,Down?IE_Pressed:IE_Released,Down?1.:0.));Keys.Add(K,Down);']
 C.need(all(x in old and x in new for x in critical),'Original masks/timeout/landing/InputKey guard changed')
 delta=checker_delta((OLD/'verify-Air-production-native-v001.py').read_text(),(HERE/'verify-Air-production-native-v001.py').read_text())
 physics=[c.pin(C.ROOT/'UnrealGame/Source/CodexDungeon'/name) for name in ('DungeonFighter.cpp','DungeonGameMode.cpp')]
 return dict(schema='hero-Air6-callback-ready-exact-source-delta-v003',passed=True,
  old_source_freeze=c.pin(OLD_SOURCE_FREEZE),new_source_freeze=sfpin,old_source_cpp=oldpins[cpp],new_source_cpp=newpins[cpp],
  old_checker_freeze=c.pin(OLD/'Air-production-proof-checker-freeze-v002.json'),new_checker=c.pin(HERE/'verify-Air-production-native-v001.py'),
  exact_restore_to_old_source=True,original_guards_preserved=True,header_and_HUD_byte_identical=True,
  source_delta_unified='\n'.join(difflib.unified_diff(old.splitlines(),new.splitlines(),fromfile='e7b9 frozen source',tofile='be6e callback-ready source',n=2)),
  checker_delta=delta,physics_diagnostic_source_pins=physics,physics_actual_substeps='OPEN_not_recorded',physics_diagnostic_required_for_native_PASS=False,
  UE_started=False,compiled=False,View=False,FinalAccepted=False)

if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output');a=p.parse_args();r=audit()
 if a.output:C.import_contract().write_new(a.output,r)
 print(json.dumps(r,ensure_ascii=False,allow_nan=False))
