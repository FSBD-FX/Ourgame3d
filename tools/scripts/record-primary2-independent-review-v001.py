from pathlib import Path
import json,hashlib
R=Path('F:/Ourgame');D=R/'docs/production/first-batch-v2'
f=D/'evidence/armor-primary2-native-review-v001/review-freeze-v001.json'
assert hashlib.sha256(f.read_bytes()).hexdigest()=='efebb06ad5269d9bbdb3e2d5cce0fe622872fa5b6e32a6328811025cc02a5d56'
p=D/'progress.json';s=json.loads(p.read_text(encoding='utf-8-sig'))
s['fairytale_armor_primary2_current_v001']['independent_native_static_review']={'report':'docs/production/first-batch-v2/evidence/armor-primary2-native-review-v001/native-review-v001.md','freeze_sha256':'efebb06ad5269d9bbdb3e2d5cce0fe622872fa5b6e32a6328811025cc02a5d56','actual_view_count':20,'selected_file_pairs_checked':36,'differences':0,'chest_near_continuity_improved':True,'far_silhouette_every_phase_accepted':False,'grip_or_fullmotion_accepted':False}
s['next_work']=['Primary3 actual660ms sixphases110/110/60/60/160/160; genuine source and armor/independent sword registration; realthree-stage sequence','Grip/thumb/AAhead-blade and farcap silhouette/footlock/fullmotion; finish other states','Finish original5weapons/4armors/5enemies/Boss+15deps/20pairings/VFX/SFX/acquire/equip/drop/full persistence; formal0/15active']
p.write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'independent_review_recorded':True,'goal_status':'active','formal_complete_units':0}))
