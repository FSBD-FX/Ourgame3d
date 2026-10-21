from pathlib import Path
import hashlib,importlib.util,json
R=Path('F:/Ourgame');T=R/'tools/scripts'
receipts=list((R/'UnrealGame/Saved/Bootstrap').glob('sword-armor-ready-v001-import-*.json'));assert len(receipts)==1
p=receipts[0];b=p.read_bytes();d=json.loads(b.decode('utf-8-sig'))
assert d['success'] and d['actual_count']==d['saved_count']==24 and d['old_packages_unchanged']==917
assert d['registry_exact_set_passed'] and d['disk_exact_set_passed']
pointer={'path':p.as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
out=R/'source-assets/production/fairytale-sword-armor-ready-runtime-v001/manifests/actual-import-receipt-ref.json';assert not out.exists()
out.write_text(json.dumps(pointer,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
spec=importlib.util.spec_from_file_location('ready24checks',T/'ue_sword_armor_ready_v001_checks.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
m.preflight(require_unused=False)
assert sum(1 for p in (R/'UnrealGame/Content/Production').rglob('*') if p.is_file())==941
print(json.dumps({'actual_Texture2Ds':24,'saved':24,'old917_unchanged':True,'production_packages':941,'receipt':pointer},ensure_ascii=False))
