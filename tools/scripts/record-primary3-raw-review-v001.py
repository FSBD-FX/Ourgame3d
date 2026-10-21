from pathlib import Path
import hashlib,json
b=Path('F:/Ourgame/source-assets/production/fairytale-sword-primary3-v001')
p=b/'root-native175-raw-review-v001.json';assert not p.exists()
raw=b/'run-primary3-v001/raw/sword_primary_3.png';data=raw.read_bytes()
assert hashlib.sha256(data).hexdigest()=='2fc43b327ee464673954bd39f139fbee334d1ccb1bf17f976a072ad31e88e6f7'
p.write_text(json.dumps({'native_request':175,'raw':{'path':raw.as_posix(),'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()},'retention':'2026-10-16-OurgameUE-primary3-native175-v227','raw_explicitly_viewed_after_retention':True,'observed':'Six separated bell-helmet charcoal-cloth bodies. Phase1 near hand rises to image-left outside helmet; phases2/3 near wrist travels forward then lower; phase4 low brake; phase5 low guard. Distinct from actual171 rising cut. No weapon/armor baked into body; near glove appears closed at raw scale.','remaining':'Phase0 inward load is subtle; phase1 hand very near helmet side; phase2 near/far hand contours overlap. Need each original512 derivative and hand/foot crops, actual palm measurement and independent weapon clearance; no native motion or armor acceptance.','standard_extraction_allowed':True,'actual_grip_px':None,'actual_blade_axis':None,'semantic_masks_accepted':False,'motion_accepted':False,'complete_unit':False,'formal_complete_units':0},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(p.as_posix())
