from pathlib import Path
import hashlib,json
R=Path('F:/Ourgame/source-assets/production/fairytale-sword-primary2-v001')
def desc(p):
    b=p.read_bytes();return {'path':p.as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
hp=R/'handoffs/primary2-native-input-root-reviewed-v005.json';h=json.loads(hp.read_text(encoding='utf-8'));row=h['rows'][0]
files=[R/'prepare-primary2-v004.py',R/'requests/primary2-numeric-input-v004.json',hp,Path(h['root_input_review']['path']),Path(row['request']['path']),Path(row['prompt']['path'])]
files.extend(Path(x['file']['path']) for x in row['reference_images_in_order'])
f=R/'preparation-freeze-v004.json';assert not f.exists()
f.write_text(json.dumps({'files':[desc(p) for p in files],'status':'Targeted171 input reviewed E206/207; no finalmotion acceptance'},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
p=R/'extract-primary2-v003.py';q=R/'extract-primary2-v004.py';assert not q.exists()
s=p.read_text(encoding='utf-8').replace('Native170','Native171').replace('native170','native171').replace('native_request=170','native_request=171').replace('v003','v004')
s=s.replace('primary2-native-input-v004.json','primary2-native-input-root-reviewed-v005.json')
s=s.replace('6963752d95b58592d7b736088904879e8811dd207d268272e4ab4e3cee9a6bdd','527f93f7838c9a95f69c1ac16ecb7095c3aeda3e5a9190088aed6bdc89b1af85')
s=s.replace('Root saw a genuinely bent low elbow and rising wrist in170 raw, but phase1 glove appears open. Derived views must be reviewed before pose/grip acceptance.',
 'Root saw closed phase1 grasp in171 targeted raw edit. All new derived frames and native grip/continuity still require review; other pixels are not presumed identical.')
q.write_text(s,encoding='utf-8')
p=Path('F:/Ourgame/tools/scripts/retain-primary2-v003-derived-v001.py');q=Path('F:/Ourgame/tools/scripts/retain-primary2-v004-derived-v001.py');assert not q.exists()
s=p.read_text(encoding='utf-8').replace('v003','v004').replace('native170','native171').replace('原生170','原生171').replace('军剑短肘上挑','军剑闭合握姿')
s=s.replace('phase1 grasp concern','targeted phase1 grasp correction pending review')
q.write_text(s,encoding='utf-8')
print(json.dumps({'preparation_freeze':desc(f),'extractor':desc(R/'extract-primary2-v004.py'),'retainer':desc(q)},ensure_ascii=False))
