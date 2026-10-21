"""Prepare pinned ten-body import only after real extracted v002/v003 sources exist."""
from pathlib import Path
import hashlib, importlib.util, json

R=Path(__file__).resolve().parents[2]
B=R/'source-assets/production/fairytale-sword-v001'
OUT=R/'source-assets/production/fairytale-sword-runtime-v002'
OLD=R/'source-assets/production/fairytale-sword-runtime-v001/manifests/import-sword-body-v001.json'
NS='/Game/Production/ArtTrials/EV048/v005/HeroSwordBody'
DEC=R/'tools/scripts/ue-import-armor-primary2-four-v001.py'
assert not OUT.exists(), 'No overwrite of prior prepared import'

def desc(p):
    b=p.read_bytes(); return {'path':p.as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}

def new(p,v):
    assert not p.exists(),p
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(v if isinstance(v,str) else json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

spec=importlib.util.spec_from_file_location('native_rgba_decoder',DEC)
dec=importlib.util.module_from_spec(spec);spec.loader.exec_module(dec)
d=json.loads(OLD.read_text(encoding='utf-8'));d['schema']='frozen-fairytale-sword-body-ten-v2';d['namespace']=NS
paths={'Ready':B/'run-ready-v002','Primary1':B/'run-primary1-v003'}
d['references']={key:desc(B/folder/'extracted-freeze-v001.json') for key,folder in [('ready_extract','ready-extraction-v002'),('primary1_extract','primary1-extraction-v003')]}
for clip,number,component in [('Ready',158,'SwordReady'),('Primary1',159,'SwordPrimary1')]:
    receipt_path=B/f'generation-control-v001/generation-receipt{number}-v001.json'
    receipt=json.loads(receipt_path.read_text(encoding='utf-8'))
    state='sword_ready_idle' if clip=='Ready' else 'sword_primary_1'
    raw=paths[clip]/f'raw/{state}.png'
    assert receipt['request_number']==number and receipt['component']==component
    assert receipt['canonical_raw']==desc(raw) and receipt['source_pixels_modified'] is False
    d['references'][clip.lower()+'_native_receipt']=desc(receipt_path)
assets=[]
for clip,n in [('Ready',4),('Primary1',6)]:
    req=json.loads((paths[clip]/'sprite-request.json').read_text(encoding='utf-8'))
    state='sword_ready_idle' if clip=='Ready' else 'sword_primary_1'
    assert req['states'][state]['frames']==n and req['states'][state]['durations_ms']==d['durations_ms'][clip]
    for i in range(n):
        p=paths[clip]/f'curated/frame-{i}.png';s=desc(p);pixels=dec.inspect_rgba_png(p.read_bytes())
        assert pixels['nonempty'] and pixels['corners_transparent'] and pixels['alpha_extrema']==[0,255]
        name=f'T_Fairytale_Sword{clip}_{i:03d}_v002'
        assets.append({'clip':clip,'frame':i,'source':s['path'],'source_bytes':s['bytes'],'source_sha256':s['sha256'],'source_bbox':pixels['bbox_px'],'name':name,'package_path':NS+'/'+name,'object_path':NS+'/'+name+'.'+name})
assert len({a['source_sha256'] for a in assets})==10
d['assets']=assets;d['source_requests']={'Ready':158,'Primary1':159}
d['scope']='Low guard and revised Primary1 sourcebody trial; no macro armor, fullmotion/thumb/complete actions acceptance'
rows=[]
for p in sorted((R/'UnrealGame/Content/Production').rglob('*')):
    if p.is_file():
        row=desc(p);row['path']=p.relative_to(R).as_posix();rows.append(row)
assert len(rows)==907, 'Confirm current old package count explicitly before new imports'
manifest=OUT/'manifests/import-sword-body-v002.json'
new(manifest,d);new(OUT/'manifests/old-production907-before-import.json',{'files':rows})
replacements={
    'ue_fairytale_sword_body_v001_checks.py':'ue_fairytale_sword_body_v002_checks.py',
    'ue-import-fairytale-sword-body-v001.py':'ue-import-fairytale-sword-body-v002.py',
    'import-fairytale-sword-body-v001.ps1':'import-fairytale-sword-body-v002.ps1',
    'fairytale-sword-runtime-v001':'fairytale-sword-runtime-v002',
    'import-sword-body-v001.json':'import-sword-body-v002.json',
    'old-production897-before-import.json':'old-production907-before-import.json',
    'fairytale-sword-body-v001-import-':'fairytale-sword-body-v002-import-',
    '/EV048/v004/HeroSwordBody':'/EV048/v005/HeroSwordBody',
    'frozen-fairytale-sword-body-ten-v1':'frozen-fairytale-sword-body-ten-v2',
    'fairytale-sword-body-ten-native-import-v1':'fairytale-sword-body-ten-native-import-v2',
    '155Ready and157Primary1':'158Ready and159Primary1',
    'native155Ready and157Primary1':'native158Ready and159Primary1',
    '897':'907',
    '267ff08aa63dcaf35a3bdbd3c134c92b6f35bab1858293f8272ab82273e8f891':desc(manifest)['sha256'],
    '{row["frame"]:03d}_v001':'{row["frame"]:03d}_v002',
}
tools=[]
for oldname in ['ue_fairytale_sword_body_v001_checks.py','ue-import-fairytale-sword-body-v001.py','import-fairytale-sword-body-v001.ps1']:
    s=(R/'tools/scripts'/oldname).read_text(encoding='utf-8-sig')
    for a,b in replacements.items():s=s.replace(a,b)
    target=R/'tools/scripts'/replacements[oldname]
    if target.suffix=='.py':compile(s,str(target),'exec')
    new(target,s);new(OUT/'import-tool-version-used'/target.name,s);tools.append(target)
assert 'ue-import-armor-primary2-four-v001.py' in tools[0].read_text(encoding='utf-8')
files=[manifest,OUT/'manifests/old-production907-before-import.json',Path(__file__),*tools,*list((OUT/'import-tool-version-used').iterdir())]
new(OUT/'preimport-freeze-v001.json',{'files':[desc(p) for p in files],'source_requests':[158,159],'scope':d['scope'],'UE_import_called':False,'formal_complete_units':0})
print(json.dumps({'manifest':desc(manifest),'assets':len(assets),'old_packages':len(rows),'preimport_freeze':desc(OUT/'preimport-freeze-v001.json')},ensure_ascii=False))
