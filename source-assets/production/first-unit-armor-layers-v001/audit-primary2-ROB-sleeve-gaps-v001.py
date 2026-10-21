"""Read-only pixel comparison of existing robe candidates; never edits media."""
from pathlib import Path
from collections import Counter
import json
from PIL import Image, ImageChops, ImageFilter

P = Path(__file__).resolve().parent
script = P/'select-primary2-ROB-sleeves-v005.py'
ns = {'__file__': str(script)}
exec(compile(script.read_text('utf-8').split("prior=P/")[0], str(script), 'exec'), ns)
r, tr = ns['r'], ns['tr']
old = r.read(P/'manifests/import-armor-primary2-four-v001.json')
c = r.read(P/'manifests/primary2-ROB-real-sleeves-candidate-v005.json')
report = []

def regions(points):
    remaining = set(points); result = []
    while remaining:
        start = remaining.pop(); group = [start]; todo = [start]
        while todo:
            x, y = todo.pop()
            for pt in [(x-1,y),(x+1,y),(x,y-1),(x,y+1)]:
                if pt in remaining:
                    remaining.remove(pt); group.append(pt); todo.append(pt)
        if len(group) >= 4:
            result.append({'pixels':len(group), 'bbox':[min(x for x,y in group),min(y for x,y in group),max(x for x,y in group)+1,max(y for x,y in group)+1],
                           'sample':group[len(group)//2]})
    return sorted(result,key=lambda x:-x['pixels'])

for i,(body,row) in enumerate(zip(old['common_body'],c['frames'])):
    far=Image.open(body['body_far']['path']).convert('RGBA')
    hand=Image.open(body['body_near']['path']).convert('RGBA')
    front=Image.open(row['parts']['armor_front']['path']).convert('RGBA')
    near=Image.open(row['parts']['armor_near']['path']).convert('RGBA')
    source=Image.open(row['source_path']).convert('RGBA')
    image=far.copy();image.alpha_composite(front);image.alpha_composite(near);image.alpha_composite(hand)
    masks=tr.masks_for(i)
    zone=ImageChops.lighter(masks['weapon_forearm'],masks['other_forearm']).filter(ImageFilter.MaxFilter(17))
    envelopes=ImageChops.lighter(tr.w.poly(ns['ARM_CLOTH_ENVELOPES'][i]),tr.w.poly(ns['OTHER_CLOTH_ENVELOPES'][i])).filter(ImageFilter.MaxFilter(7))
    fist=ImageChops.lighter(tr.w.poly(ns['FISTS'][i]),tr.w.poly(ns['OTHER_FISTS'][i])).filter(ImageFilter.MaxFilter(7))
    causes=Counter();points=[];samples=[]
    for y in range(512):
        for x in range(512):
            if not zone.getpixel((x,y)):continue
            rr,gg,bb,aa=image.getpixel((x,y));sr,sg,sb,sa=source.getpixel((x,y))
            gold=aa>240 and rr>gg*1.2 and gg>bb*1.15 and gg>65
            source_cloth=sa>240 and sr<=sg*1.12 and sb>=sg*.75 and sg>45
            if not (gold and source_cloth):continue
            points.append((x,y));flags=[]
            for name,mask in [('head',masks['head'].filter(ImageFilter.MaxFilter(7))),('belt',masks['belt']),('pouch',masks['pouch']),('fist_clearance',fist),('old_hand_top',hand.getchannel('A'))]:
                if mask.getpixel((x,y)):flags.append(name)
            if not envelopes.getpixel((x,y)):flags.append('outside_cloth_envelope')
            if not flags:flags=['unclassified_mask_gap']
            causes.update(flags)
            if len(samples)<10:samples.append({'xy':[x,y],'final':list(image.getpixel((x,y))),'native66':list(source.getpixel((x,y))),'causes':flags})
    report.append({'frame':i,'detected_pixels':len(points),'causes':dict(causes),'regions':regions(points),'samples':samples})

output=P/'reviews/primary2-ROB-sleeve-gap-pixel-audit-v001.json'
assert not output.exists()
r.write(output,{'schema':'read-only-sleeve-pixel-difference-audit-v1','candidate':str(P/'manifests/primary2-ROB-real-sleeves-candidate-v005.json'),
    'method':'Find visible warm underclothes where same-coordinate native66 is gray/blue cloth, within original arm neighborhood. Classifier is diagnostic only; every change needs semantic image review.',
    'frames':report,'media_changed':False,'generation_calls_added':0})
r.archive(output,output.relative_to(P),'read_only_pixel_gap_diagnostic_not_semantic_acceptance')
print(json.dumps(report,ensure_ascii=False))
