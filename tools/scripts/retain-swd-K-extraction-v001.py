from pathlib import Path
import hashlib,json,shutil
R=Path('F:/Ourgame'); C=R/'source-assets/production/fairytale-sword-secondary-v001'
freeze=C/'request259-extraction-qc-v001/extraction-freeze-v001.json'
def d(p):
 b=p.read_bytes();return dict(path=p.as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
assert d(freeze)['sha256']=='6dad3b4ba041954237916ab765027e59b1f4c24137741ddeccba666b45481e59'
data=json.loads(freeze.read_text(encoding='utf-8-sig'))
A=R/'过程图稿与视频/2026-10-19_军剑副攻K259提取与宽漂移_v001'
assert not A.exists();(A/'原件').mkdir(parents=True);(A/'展示副本').mkdir()
rows=[]
for row in data['members']+[d(freeze)]:
 p=Path(row['path']);assert d(p)==row,p
 rel=p.relative_to(freeze.parent);t=A/'原件'/rel;t.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,t)
 assert d(t)['sha256']==row['sha256'];rows.append(dict(source=row,retained=d(t)))
 if p.parent.name=='aligned512':
  v=A/'展示副本'/p.name;shutil.copy2(p,v);assert d(v)['sha256']==row['sha256']
master=C/'references/ready-body-master.png';v=A/'展示副本/accepted-ready-body-master.png';shutil.copy2(master,v)
rows.append(dict(source=d(master),retained=d(v)))
(A/'source-version-status-index.json').write_text(json.dumps(dict(schema='K259-technical-extraction-before-review-v001',files=rows,freeze=d(freeze),status='Rejected lower-body width drift; pending Root processed-image review; no runtime admission',formal_complete_units=0),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(A/'README.md').write_text('request259原627格、chroma、统一512/627缩放、整数Y对齐、alpha与边缘掩码全部原样保留。展示4张512姿态和Ready基准。脚底末6行跨度240/239/240/259，相对基准184过宽；禁止逐帧缩放掩盖比例。仅技术候选，未导入或正式动作验收；先E655逐字节保全后Root审阅。\n',encoding='utf-8')
print(json.dumps(dict(archive=A.as_posix(),members=len(data['members']),source_hash_mismatches=0),ensure_ascii=False))
