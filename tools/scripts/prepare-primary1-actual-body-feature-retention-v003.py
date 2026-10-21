from pathlib import Path
R=Path('F:/Ourgame');old=R/'tools/scripts/retain-primary1-extraction-features-v002.py';new=R/'tools/scripts/retain-primary1-extraction-features-v003.py';assert not new.exists();s=old.read_text(encoding='utf-8')
for a,b in [('2026-10-17_软皮第一刀192胸衣挂点审阅_v002','2026-10-17_软皮第一刀实际修正版身体对位_v003'),('fairytale-sword-v001/run-primary1-v001/curated','fairytale-sword-v001/run-primary1-v003/curated'),('原Body159','实际Body159v003'),('新E295后才Root看新图。','此前v001身体参考不等于实际fourlayers；本批actualv003+24运行身体层在E296后审。')]:
 assert a in s;s=s.replace(a,b)
needle="(A/'source-version-status-index.json').write_text"
assert needle in s
extra="""for component in ['BodyRest','NearArmWithoutHand','HelmetForeground','NearHand']:
 for i in range(6):
  p=R/f'source-assets/production/fairytale-armor-sword-primary1-v001/macro-registration-primary1-v001/textures/{component}/frame-{i}.png';q=A/'原件'/'actual-runtime-body-layers'/component/f'frame-{i}.png';q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q);assert p.read_bytes()==q.read_bytes();rows.append(dict(source=desc(p),copy=q.relative_to(A).as_posix()))
"""
s=s.replace(needle,extra+needle);new.write_text(s,encoding='utf-8');print(new.as_posix())
