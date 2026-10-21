"""Retain v4 fixed-ROI/20-warm-pixel gate, adding both-facing P3 coverage.

This bounded signal can include warm hands and does not identify the whole helmet,
prove eye-window clearance, or replace original-size visual review.
"""
from pathlib import Path
import argparse,json,math
from PIL import Image

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--archive',required=True);args=parser.parse_args()
    archive=Path(args.archive).resolve();original=archive/'原件'
    report=json.loads((original/'runtime-report.json').read_text(encoding='utf-8-sig'))
    assert report['primary3_fit_trial'] and report['primary3_armor_trial']
    clips=[('sword_ready_idle',4),('sword_primary_1',6),('sword_primary_2',6),('sword_primary_3',6)]
    checks=[]
    for i,d in enumerate(report['observations']):
        if not d['supported'] or d['clip'] not in [c for c,n in clips]:continue
        scale=d['canvas_size']/512.;facing=d['facing']
        rootx=d['grip_screen'][0]+facing*(256-d['grip'][0])*scale
        rooty=d['grip_screen'][1]+(464-d['grip'][1])*scale
        xs=[rootx+facing*(x-256)*scale for x in [170,350]]
        bounds=[math.floor(min(xs)),math.floor(rooty+(70-464)*scale),math.ceil(max(xs)),math.ceil(rooty+(233-464)*scale)]
        path=original/f'MovieFrame{i:05d}.png'
        with Image.open(path) as image:
            assert image.size==(1280,720)
            pixels=list(image.convert('RGB').crop(tuple(bounds)).getdata())
        warm=sum(red>115 and red>green*1.10 and green>blue*1.10 for red,green,blue in pixels)
        checks.append({'observation':i,'clip':d['clip'],'phase':d['frame'],'facing':facing,
            'path':path.as_posix(),'head_roi_px':bounds,'warm_helmet_pixels':warm,'passed':warm>=20})
    assert checks and {(x['facing'],x['clip'],x['phase']) for x in checks}=={
        (side,clip,frame) for side in (-1,1) for clip,count in clips for frame in range(count)}
    out=original/'visible-ready-primary3-head-gate-v001.json'
    result={'schema':'bell-helmet-ready-primary3-visible-pixel-gate-v1','passed':all(x['passed'] for x in checks),
        'checked_supported_observations':len(checks),'failed_observations':sum(not x['passed'] for x in checks),
        'threshold_warm_pixels':20,'source_ROI_px':[170,70,350,233],'minimum':min(x['warm_helmet_pixels'] for x in checks),
        'threshold_or_ROI_relaxed':False,'includes_both_facing_primary3_six_phases':True,
        'scope':'Fixed dark-teal scene/72px warm-pixel presence only, same ROI and20 threshold as v4. Warm hands can contribute; ROI does not cover the complete175 helmet in every pose. Not helmet attribution, eye-window/no-overlap, fit, fullmotion or generalized background acceptance.',
        'formal_complete_units':0,'checks':checks}
    with out.open('x',encoding='utf-8') as handle:handle.write(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='checks'},ensure_ascii=False))
    raise SystemExit(0 if result['passed'] else 1)

if __name__=='__main__':main()
