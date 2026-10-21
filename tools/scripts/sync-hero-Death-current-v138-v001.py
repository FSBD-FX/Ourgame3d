"""Remove superseded generic preparation fields without rewriting historical records."""
from pathlib import Path
import json,shutil
R=Path('F:/Ourgame');p=R/'docs/production/first-batch-v2/progress.json'
out=R/'docs/production/first-batch-v2/evidence/hero-Death40-v001/current-status-alias-sync-v138-v001';assert not out.exists();out.mkdir(parents=True);shutil.copy2(p,out/'progress-before.json')
j=json.loads(p.read_text(encoding='utf-8-sig'));s=j['current_hero_Dodge_Death_equipment_sources']
s.update(Production_imported=dict(Death40=True,Dodge32=False),Death_current_sourcefit_accepted=True,
 Death_sourcefit_acceptance_scope='Limited SWD001/LGT001 Death5 source and actual native display review only. FullUnit/FinalAccepted remain false.',
 Death_known_defect='Own-hand/helmet/sleeve partition and terminal renderer resolved for current Death5. Artist floor/contact/socket, source joins/footlock and other equipment states remain unverified or incomplete.',
 Death_runtime_current_gap='Death5 is actually rendered and both native sides reviewed. Full equipped Dodge/air and remaining combinations still incomplete; no inventory/world-drop change.',
 next='Prioritize Guard Move/Stomp real art to remove observed geometric pop, then Dodge32 joint correction/native return and remaining units. No additional image call after241 in this phase.')
j['next_snapshot']='Create a new snapshot after the next actual Source change and required validation; current actual checkpoint is v138-HeroDeath190G.'
j['current_turn_progress_classification']='progress: actual SWD/LGT Death5 native state completed; full units and combinations remain unaccepted'
j['latest_native_review_player']='Two native diagnostic silent MP4s actually played to end in browser tab4; separate E514 playback proof; no audio acceptance.'
j['current_review']='v138 Death5 native+visual finite state pass, Guard Stomp placeholder visible and prioritized; full0/15, combos0/20.'
p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(out/'receipt.json').write_text(json.dumps(dict(current='v138',generic_source_preparation_aliases_corrected=True,actual_source_modified=False,tests_repeated=False,goal='active',formal_complete_units=0),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(current='v138',Death_imported_native_reviewed=True,Dodge_unimported=True,Source_unchanged=True,formal0=True)))
