from pathlib import Path
import hashlib,json,shutil
R=Path('F:/Ourgame');B=R/'source-assets/production/fairytale-armor-sword-primary1-v001'
F=B/'preparation-freeze-v001.json';A=R/'过程图稿与视频/2026-10-16_钟盔军剑首斩六相胸肩输入候选_v001'
def desc(p):
 b=p.read_bytes();return {'path':p.as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
assert desc(F)['sha256']=='bf820e073deb4453e3eaea0c2891fba78e8ce510e88140a9953601fb7d2b9a31'
d=json.loads(F.read_text(encoding='utf-8-sig'));assert len(d['files'])==33
assert not A.exists();(A/'原件').mkdir(parents=True);(A/'展示副本').mkdir();entries=[];guides=[]
for i,row in enumerate(d['files']+[desc(F)]):
 p=Path(row['path']);actual=desc(p);assert actual['bytes']==row['bytes'] and actual['sha256']==row['sha256'],p
 t=A/'原件'/f'{i:03d}-{p.name}';shutil.copy2(p,t);assert desc(t)['sha256']==actual['sha256']
 entries.append({'source':actual,'retained':desc(t)})
 if 'guides' in p.parts and p.suffix.lower()=='.png':
  q=A/'展示副本'/f'{i:03d}-{p.name}';shutil.copy2(p,q);assert desc(q)['sha256']==actual['sha256'];guides.append(desc(q))
assert len(guides)==3,len(guides)
(A/'index.json').write_text(json.dumps({'schema':'primary1-armor-preparation-pre-view-retention-v1','files':entries,'guides':guides,'status':'Input proposals only; hidden attachment points remain null, generation_ready=false, no native call/import/UE','source_pixels_changed':False,'formal_complete_units':0},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(A/'README.md').write_text('159实际首斩六相身体对应的三甲输入候选。三张技术图仅为测量/请求准备，不是游戏素材。未知遮挡挂点保留null，尚未核定为可生成输入；Root审阅后另定设计，不把Ready甲平移冒充攻击甲完成。展示前保留F/E原件和逐字节图副本。\n',encoding='utf-8')
print(json.dumps({'archive':A.as_posix(),'frozen_files':len(entries),'guide_copies':len(guides),'bytes':sum(e['retained']['bytes'] for e in entries),'mismatches':0},ensure_ascii=False))
