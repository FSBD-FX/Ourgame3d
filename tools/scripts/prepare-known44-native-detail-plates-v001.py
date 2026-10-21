"""Crop retained native samples for inspection; never modify source art or PNGs."""
from pathlib import Path
from PIL import Image,ImageDraw
import hashlib,json,math,shutil
R=Path('F:/Ourgame');out=R/'过程图稿与视频/2026-10-18_守卫单斧左右原生动作与衔接对照_v001'
assert not out.exists();(out/'原件').mkdir(parents=True);(out/'展示副本').mkdir()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def pin(p):return dict(path=p.as_posix(),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
allrows=[];plates=[]
for side,suffix in [('R','sideR_v002'),('L','sideL_v001')]:
 b=R/'过程图稿与视频'/('2026-10-18_石守卫完整分期单斧周期原生试样_'+suffix);r=read(b/'原件/runtime-report.json');v=read(b/'source-version-status-index.json')
 assert r['passed'] and read(b/'原件/independent-known44-AxeCycle-v002.json')['passed']
 samples=[next(s for s in v['samples'] if s['clip']==clip and s['frame']==f) for clip in ['AxeActive','AxeRecovery'] for f in range(4)]
 def crop(s,label):
  src=Path(s['source']['path']);assert pin(src)==s['source'];o=r['observations'][s['frame_index']]
  ds=[d for d in o['guard_draws'] if str(d['EntityId'])==r['guard_entity'] and d['Selection']['Clip']==s['clip'] and d['Selection']['Frame']==s['frame']];assert len(ds)==1
  gx,gy=ds[0]['GroundScreen'];rect=[math.floor(gx)-100,math.floor(gy)-184,math.floor(gx)+150,math.floor(gy)+56]
  with Image.open(src) as im:
   assert im.size==(1280,720);cut=im.convert('RGB').crop(rect)
  dest=out/'原件'/f'{side}-{label}-MovieFrame{s["frame_index"]:05d}.png';assert not dest.exists();shutil.copy2(src,dest);assert pin(dest)['sha256']==s['source']['sha256']
  row=dict(side=side,label=label,clip=s['clip'],phase_frame=s['frame'],native_frame=s['frame_index'],source=pin(src),preserved=pin(dest),crop_rectangle=rect,original_crop_scale=1)
  allrows.append(row);tile=Image.new('RGB',(250,264),(30,33,38));tile.paste(cut,(0,24));ImageDraw.Draw(tile).text((5,5),f'{side} {label} native {s["frame_index"]}',fill='white');return tile
 plate=Image.new('RGB',(1000,528))
 for i,s in enumerate(samples):plate.paste(crop(s,s['clip']+str(s['frame'])),((i%4)*250,(i//4)*264))
 p=out/'展示副本'/f'{side}-Active4-Recovery4-native-crops-1x.png';plate.save(p);plates.append(pin(p));q=p.with_name(p.stem.replace('1x','2x-nearest')+'.png');plate.resize((2000,1056),Image.Resampling.NEAREST).save(q);plates.append(pin(q))
 joinplate=Image.new('RGB',(500,792));assert len(v['joins'])==3
 for i,j in enumerate(v['joins']):
  for k,s in enumerate(j['pair']):joinplate.paste(crop(s,'join'+str(i)+'-'+('before' if k==0 else 'after')+'-'+s['clip']+str(s['frame'])),(k*250,i*264))
 p=out/'展示副本'/f'{side}-three-native-adjacent-joins-1x.png';joinplate.save(p);plates.append(pin(p));q=p.with_name(p.stem.replace('1x','2x-nearest')+'.png');joinplate.resize((1000,1584),Image.Resampling.NEAREST).save(q);plates.append(pin(q))
index=dict(schema='guard-known44-native-detail-plates-v001',native_sources_unchanged=True,originals=allrows,presentation=plates,only_crop_and_nearest_display_enlargement=True,art_pixels_edited=False,join_visual_accepted=False,formal_complete_units=0)
(out/'source-version-status-index.json').write_text(json.dumps(index,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(out/'README.md').write_text('左右首AttackId原生Active4/Recovery4与三组原生join对照。原幅PNG逐字复制；crop坐标与2x nearest展示明确留档，不改美术、时序、原截图。新媒体仍须E两SHA保全后审阅；无声音/足锁/最终完成验收。\n',encoding='utf-8')
print(json.dumps(dict(archive=out.as_posix(),originals=len(allrows),plates=len(plates))))
