from pathlib import Path
import ast,hashlib,json,shutil
b=Path('F:/Ourgame/source-assets/production/fairytale-sword-primary3-v001');d=b/'tooling-draft-v001'
def desc(p):
    data=p.read_bytes();return {'path':p.as_posix(),'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}
freeze=d/'tooling-freeze-v001.json'
assert desc(freeze)['sha256']=='3498bf04cbf39cd4faaf6bf630e50c44807529b3bf515b7f7c8fcf206b1906a7'
expected=[('extract-primary3-v001.py','f8f1fec979fc74a49b9c5056b1b5d7040a1191e63ff85bba01b6a54a843dced3',b/'extract-primary3-v001.py'),('retain-primary3-derived-v001.py','5e2192840b017d7a7bde43bee7b93044b6d4556588ba0038738bce46aa2481c9',Path('F:/Ourgame/tools/scripts/retain-primary3-derived-v001.py'))]
rows=[]
for name,sha,target in expected:
    p=d/name;assert desc(p)['sha256']==sha and not target.exists();ast.parse(p.read_text(encoding='utf-8'))
for name,sha,target in expected:
    p=d/name;shutil.copy2(p,target);assert p.read_bytes()==target.read_bytes();rows.append({'candidate':desc(p),'admitted':desc(target)})
out=b/'root-extractor-admission-v001.json';assert not out.exists()
out.write_text(json.dumps({'tooling_freeze':desc(freeze),'files':rows,'root_review':'Reviewed standard four tool order, no request changes, originalRGBA diagnostic crops, explicit660 vs standard600 timing limitation and fresh-only files. No artwork or runtime acceptance.','executed_by_this_script':False,'formal_complete_units':0},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'admission':desc(out)},ensure_ascii=False))
