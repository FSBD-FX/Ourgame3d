from pathlib import Path
import hashlib,json
R=Path('F:/Ourgame/source-assets/production/fairytale-sword-primary2-v001')
def desc(p):
    b=p.read_bytes();return {'path':p.as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
h=json.loads((R/'handoffs/primary2-native-input-v003.json').read_text(encoding='utf-8'))
row=h['rows'][0]
files=[R/'prepare-primary2-v003.py',R/'requests/primary2-numeric-input-v003.json',R/'handoffs/primary2-native-input-v003.json',
       Path(row['numeric_contract']['path']),Path(row['request']['path']),Path(row['prompt']['path'])]
files.extend(Path(x['file']['path']) for x in row['reference_images_in_order'])
f=R/'preparation-freeze-v003.json';assert not f.exists()
f.write_text(json.dumps({'files':[desc(p) for p in files],'status':'Root reviewed inputs E202/E203; all joints are design; no motion acceptance'},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
p=R/'extract-primary2-v002.py';q=R/'extract-primary2-v003.py';assert not q.exists()
s=p.read_text(encoding='utf-8').replace('Native169','Native170').replace('native169','native170').replace('native_request=169','native_request=170').replace('v002','v003').replace('v2\'','v3\'')
s=s.replace('44552ec706ace7a07a49a8b3169bfb6483aff22912837dea156667f269e26747','6963752d95b58592d7b736088904879e8811dd207d268272e4ab4e3cee9a6bdd')
s=s.replace('Root saw shorter forward extension in169 but bent elbow/side grip are still unaccepted; this reviewer has not viewed169 raw or new derived frames.',
 'Root saw a genuinely bent low elbow and rising wrist in170 raw, but phase1 glove appears open. Derived views must be reviewed before pose/grip acceptance.')
s=s.replace('Actual features and transverse-cut/anatomy judgment','Actual features and rising-cut/anatomy judgment')
q.write_text(s,encoding='utf-8')
print(json.dumps({'preparation_freeze':desc(f),'new_extractor':desc(q)},ensure_ascii=False))
