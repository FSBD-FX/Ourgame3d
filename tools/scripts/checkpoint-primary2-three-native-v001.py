from pathlib import Path
import json,hashlib,shutil
R=Path('F:/Ourgame');B=R/'source-assets/production/fairytale-armor-sword-primary2-v001';D=R/'docs/production/first-batch-v2'
def desc(p):
 b=p.read_bytes();return dict(path=p.as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
report=B/'root-native172-174-raw-review-v001.json';assert not report.exists()
rows=[]
for n in [172,173,174]:
 receipt=B/f'generation-control-v001/generation-receipt{n}-v001.json';v=json.loads(receipt.read_text())
 assert desc(Path(v['canonical_raw']['path']))==v['canonical_raw']
 rows.append(dict(native_request=n,receipt=desc(receipt),raw=v['canonical_raw'],raw_size=v['raw_size'],explicit_root_view_after_retention=True,components_visible=6,
  no_body_or_weapon_visible=True,material_family_preserved_in_raw_candidate=True,actual_feature_A_measured=False))
report.write_text(json.dumps(dict(rows=rows,retention=['E218','E219','E220'],
 observations=['Chest has central round boss and compact shell; small perspective differences remain candidate.',
 'Near cap opening clearly varies across folding arm phases, with actual central washer/hole.',
 'Far cap top strap continues to lateral rivet; not central face boss. Physical feature and same-family fit await extracted detail.'],
 decision='Allow standard deterministic shared-row extraction only; no component feature/fit/equipment acceptance',
 source_body_changed=False,runtime_imported=False,formal_complete_units=0),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
p=D/'progress.json';backup=D/'evidence/armor-primary2-native-tooling-v001/progress-before-actual-native174-v001.json';assert not backup.exists();shutil.copy2(p,backup)
s=json.loads(p.read_text(encoding='utf-8-sig'));g=json.loads((R/'source-assets/production/first-unit-animation-v003/generation-ledger.json').read_text(encoding='utf-8-sig'))
assert g['requested_count']==174 and g['current_window']['requested_count']==6
s['generation_accounting_current']=dict(requested_count=174,window_number=8,window_requested_count=6,window_limit=24,remaining_in_window=18,lifetime_requested_count=198,external_api_calls=0,fee_unknown=True)
s['next_native_request']=175;s['next_retention_batch']='E221'
s['fairytale_armor_primary2_current_v001'].update(state='three actual native172/173/174 raw six-view rows retained and Root-reviewed; standard extraction pending',raw_retention=['E218','E219','E220'],raw_review=report.as_posix(),native_requests=[172,173,174],feature_A_measured=False,imported=False)
s['current_retention_batches']=list(dict.fromkeys(s.get('current_retention_batches',[])+['E217','E218','E219','E220']))
s['current_task']='EV048 v114 actual short-elbow risingcut source171 full138 and real buffered bothfacings; actual172/173/174 Chest/Near/Far native6view rows retained/reviewed, standard extraction then real-feature registration and armor fit pending; formal0/15active'
p.write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
note='\n2026-10-16 17:34 EV048续行：实际生成172胸/173近肩/174远肩三组六透视，2172×724原图E218/219/220均展示前两SHA0。Root原图审允许标准提取，实际特征/穿甲实景未验收。ledger174/window0086/24/rem18/lifetime198/external0/费用未知，正式0/15active。\n'
for n in ['README.md','AGENTS.md','项目需求台账.md']:
 with (R/n).open('a',encoding='utf-8') as f:f.write(note)
print(json.dumps(dict(report=desc(report),native=174,remaining=18,formal_complete_units=0),ensure_ascii=False))
