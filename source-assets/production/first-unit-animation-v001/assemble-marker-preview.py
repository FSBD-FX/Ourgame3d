"""Deterministic assembly debug from existing art/markers. No image generation.

This is a review contact sheet, not a new sprite/layer asset or runtime evidence.
"""
from pathlib import Path
import hashlib
import json
import math
from PIL import Image, ImageDraw

ROOT=Path(__file__).resolve().parent

def main():
    data=json.loads((ROOT/'assembly-markers-v001.json').read_text(encoding='utf-8'))
    weapon=Image.open(data['weapon_component']['path']).convert('RGBA')
    scale=data['weapon_component']['uniform_scale_candidate']
    wx,wy=data['weapon_component']['grip_px']
    sheet=Image.new('RGB',(6*384,5*410),'#252525')
    draw=ImageDraw.Draw(sheet)
    for row,action in enumerate(data['actions']):
        for index,frame in enumerate(action['frames']):
            body=Image.open(frame['path']).convert('RGBA')
            assert hashlib.sha256(Path(frame['path']).read_bytes()).hexdigest()==frame['sha256']
            preview=Image.new('RGBA',(768,768),(0,0,0,0))
            preview.alpha_composite(body,(128,128))
            bx,by=[value+128 for value in frame['grip_px']]
            angle=math.radians(frame['weapon_angle_deg_clockwise_screen'])
            c,s=math.cos(angle),math.sin(angle)
            # Inverse transform: output coordinate -> original weapon pixels.
            affine=(c/scale,s/scale,wx-(c*bx+s*by)/scale,
                    -s/scale,c/scale,wy-(-s*bx+c*by)/scale)
            placed=weapon.transform((768,768),Image.Transform.AFFINE,affine,Image.Resampling.BICUBIC)
            preview.alpha_composite(placed)
            mask=Image.new('L',(512,512),0)
            ImageDraw.Draw(mask).polygon([tuple(point) for point in frame['near_hand_occlusion']['polygon_px']],fill=255)
            # Reuse original pixels only. Polygon remains approximate, not a true layer.
            hand=Image.new('RGBA',(512,512),(0,0,0,0));hand.paste(body,(0,0),mask)
            preview.alpha_composite(hand,(128,128))
            background=Image.new('RGBA',preview.size,'#252525');background.alpha_composite(preview)
            sheet.paste(background.convert('RGB').resize((384,384),Image.Resampling.LANCZOS),(index*384,row*410))
            draw.text((index*384+8,row*410+388),f'{action["id"]} {index+1}: candidate assembly only',fill='white')
    target=ROOT/'reviews'/'assembly-preview-v001.png'
    assert not target.exists()
    sheet.save(target)
    print(target)

if __name__=='__main__':main()
