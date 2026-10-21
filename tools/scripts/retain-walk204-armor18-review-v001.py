from pathlib import Path
import hashlib, json, shutil
from PIL import Image

root = Path('F:/Ourgame')
art = root/'source-assets/production/fairytale-lgt-readability-v003'
out = root/'过程图稿与视频/2026-10-17_Walk闭握六帧与三甲提取实像复核_v001'
assert not out.exists()
original = out/'原件'
presentation = out/'展示副本'
original.mkdir(parents=True)
presentation.mkdir()
records = []
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def copy(p, rel):
    q=original/rel
    q.parent.mkdir(parents=True,exist_ok=True)
    assert not q.exists()
    shutil.copy2(p,q)
    assert p.stat().st_size==q.stat().st_size and sha(p)==sha(q)
    records.append({'source':str(p),'original':str(q),'bytes':q.stat().st_size,'sha256':sha(q)})
    return q

hand=art/'walk-hand204-extraction-v001'
freeze=json.loads((hand/'extraction-freeze-v001.json').read_text(encoding='utf-8-sig'))
for item in freeze['files']:
    p=hand/item['path']
    assert p.stat().st_size==item['bytes'] and sha(p)==item['sha256'],p
    copy(p,Path('hand204')/item['path'])
copy(hand/'extraction-freeze-v001.json',Path('hand204/extraction-freeze-v001.json'))
for p in (original/'hand204/measurement-guides').glob('*.png'):
    shutil.copy2(p,presentation/p.name)

indexpath=art/'walk-far201-min256-v002/walk-eighteen-source-index-v002.json'
index=json.loads(indexpath.read_text(encoding='utf-8-sig'))
copy(indexpath,Path('armor18/walk-eighteen-source-index-v002.json'))
contacts=[]
for component in index['components']:
    contact=Image.new('RGBA',(384,256),(0,0,0,0))
    for frame in component['frames']:
        p=Path(frame['source']['path'])
        assert sha(p)==frame['source']['sha256'],p
        copied=copy(p,Path('armor18')/component['component']/p.name)
        im=Image.open(copied).convert('RGBA')
        assert im.size==(512,512)
        crop=im.crop((192,192,320,320))
        bbox=im.getchannel('A').getbbox()
        assert 192<=bbox[0] and 192<=bbox[1] and bbox[2]<=320 and bbox[3]<=320
        i=frame['frame']
        contact.paste(crop,((i%3)*128,(i//3)*128))
    name=f"{component['component']}-six-UNSCALED-sourceRect192-320-v001.png"
    q=original/'armor18'/name
    contact.save(q)
    shutil.copy2(q,presentation/name)
    contacts.append({'name':name,'source_crop':[192,192,320,320],'rescaled':False,'order':[0,1,2,3,4,5],'sha256':sha(q)})
data={'schema':'walk204-armor18-pre-view-retention-v001','status':'EXTRACTED_CANDIDATE_NOT_FITTED_NOT_IMPORTED_NOT_RUNTIME_ACCEPTED','sources':records,'armor_contact_maps':contacts,'hand_grid_note':'608 canvases show original 512 source pixels with labels; close contact is 128x128 exact crop per frame, no resizing.','frame5_hand_risk':'cuff orientation may mismatch back arm; not accepted as wrist fit','E_retention_required_before_view':True}
(out/'index.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
(out/'README.md').write_text('本批为闭握204六帧与三甲十八帧标准提取后的实际像素复核。原件、坐标图与原比例裁剪展示副本同时保留。当前为候选，尚未接受腕部拼合、武器握持、护甲适配或游戏实景。所有裁剪只作诊断展示，未修改原生产像素。\n',encoding='utf-8')
print(json.dumps({'out':str(out),'copied_sources':len(records),'contacts':contacts},ensure_ascii=False))
