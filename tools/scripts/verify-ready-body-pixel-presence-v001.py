"""Bounded visible-head gate for this fixed 72px bell-helmet scene trial.

Does not infer armor fit or full animation quality from draw-call metadata.
"""
from pathlib import Path
import argparse,json,math
from PIL import Image
p=argparse.ArgumentParser();p.add_argument('--archive',required=True);a=p.parse_args()
A=Path(a.archive).resolve();O=A/'原件'
r=json.loads((O/'runtime-report.json').read_text(encoding='utf-8-sig'));checks=[]
for i,d in enumerate(r['observations']):
 if not d['supported'] or d['clip']!='sword_ready_idle':continue
 scale=d['canvas_size']/512.;facing=d['facing']
 rootx=d['grip_screen'][0]+facing*(256-d['grip'][0])*scale
 rooty=d['grip_screen'][1]+(464-d['grip'][1])*scale
 xs=[rootx+facing*(x-256)*scale for x in [170,350]]
 bounds=[math.floor(min(xs)),math.floor(rooty+(70-464)*scale),math.ceil(max(xs)),math.ceil(rooty+(233-464)*scale)]
 path=O/f'MovieFrame{i:05d}.png'
 with Image.open(path) as image:
  pixels=list(image.convert('RGB').crop(tuple(bounds)).getdata())
 warm=sum(red>115 and red>green*1.10 and green>blue*1.10 for red,green,blue in pixels)
 checks.append({'observation':i,'phase':d['frame'],'facing':facing,'path':path.as_posix(),'head_roi_px':bounds,'warm_helmet_pixels':warm,'passed':warm>=20})
assert checks and {(x['facing'],x['phase']) for x in checks}=={(s,i) for s in [-1,1] for i in range(4)}
out=O/'visible-ready-head-gate-v001.json';assert not out.exists()
result={'schema':'bell-helmet-ready-visible-pixel-gate-v1','passed':all(x['passed'] for x in checks),'checked_Ready_observations':len(checks),
 'failed_observations':sum(not x['passed'] for x in checks),'threshold_warm_pixels':20,'minimum':min(x['warm_helmet_pixels'] for x in checks),
 'scope':'Only visible warm bell helmet presence in this fixed dark teal brick scene/72px trial; not armor fit, zero overlap, all motion, or generalized background coverage.',
 'formal_complete_units':0,'checks':checks}
out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in result.items() if k!='checks'},ensure_ascii=False))
raise SystemExit(0 if result['passed'] else 1)
