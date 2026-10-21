"""Read actual retained Ready pixels; save unscaled diagnostic crops, never edit assets."""
from pathlib import Path
import datetime, hashlib, json
from PIL import Image

root = Path(__file__).resolve().parent
out = root / 'ready-measurement-v001'
assert not out.exists()
out.mkdir()
def desc(path):
    b = path.read_bytes()
    return {'path': path.as_posix(), 'bytes': len(b), 'sha256': hashlib.sha256(b).hexdigest()}
def foot(im, roi):
    x0, y0, x1, y1 = roi
    a = im.getchannel('A')
    ys = [y for y in range(y0, y1) if any(a.getpixel((x,y)) >= 128 for x in range(x0,x1))]
    last = max(ys)
    span = [x for x in range(x0,x1) if a.getpixel((x,last)) >= 128]
    return {'roi_px':roi, 'alpha_threshold':128, 'last_contact_pixel_y':last,
            'span_inclusive_px':[min(span),max(span)], 'center_x':(min(span)+max(span))/2,
            'boundary_below_pixel_y':last+1,
            'meaning':'Visible opaque boot sole edge in explicit boot ROI; no ground/shadow pixels.'}
rows=[]
for i in range(4):
    p = root / 'run-ready-v001' / 'curated' / f'frame-{i}.png'
    im=Image.open(p).convert('RGBA')
    rois={'near_hand':[188,248,285,315], 'feet':[142,411,368,465]}
    crops=[]
    for key, roi in rois.items():
        q=out/f'frame-{i}-{key}-diagnostic.png'
        im.crop(roi).save(q)
        crops.append({'role':key,'roi_px':roi,'file':desc(q),'resampled':False,'art_asset':False})
    near=foot(im,[142,430,230,464]);far=foot(im,[260,430,368,464])
    rows.append({'frame':i,'source':desc(p),'diagnostic_crops':crops,'near_boot':near,'far_boot':far,
                 'dual_visible_contact_center_x':(near['center_x']+far['center_x'])/2,
                 'display_root_candidate_px':[256,464],
                 'root_status':'Design pivot retained separately; this is not automatically the averaged sole center.',
                 'grip_actual_px':None,'grip_axis_actual_xy':None,'hand_replay_polygon_px':None,
                 'hand_status':'Await E-retained diagnostic view; no old marker or planned grip copied.'})
receipt={'schema':'fairytale-sword-ready-readonly-pixel-diagnostics-v1',
         'created_local':datetime.datetime.now().astimezone().isoformat(),'frames':rows,
         'source_assets_modified':False,'new_diagnostics_viewed':False,'native_called':False,'ue_called':False}
p=out/'pixel-evidence-v001.json';p.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
files=sorted(out.glob('*'))+[Path(__file__).resolve()]
freeze={'schema':'fairytale-sword-ready-diagnostics-freeze-v1','file_count':len(files),
        'total_bytes':sum(x.stat().st_size for x in files),'files':[desc(x) for x in files],
        'new_diagnostics_viewed':False,'status':'Unscaled source crop evidence only; hand measurements pending explicit visual review.'}
p=out/'diagnostic-freeze-v001.json';p.write_text(json.dumps(freeze,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'freeze':desc(p),'feet':[{k:r[k] for k in ['frame','near_boot','far_boot','dual_visible_contact_center_x']} for r in rows]},ensure_ascii=False))
