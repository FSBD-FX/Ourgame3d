from pathlib import Path
import hashlib
R=Path('F:/Ourgame');old=R/'tools/scripts/retain-primary1-extraction-features-v001.py';new=R/'tools/scripts/retain-primary1-extraction-features-v002.py';assert not new.exists()
s=old.read_text(encoding='utf-8')
for a,b in [
 ('primary1-leather-extraction-v001','primary1-chest192-extraction-v001'),
 ('2026-10-17_软皮第一刀十八帧挂点审阅_v001','2026-10-17_软皮第一刀192胸衣挂点审阅_v002'),
 ('daca1868be1f5201bbbac9974a947d4576bfc0c3119e424c9bec681678fcf1a5',hashlib.sha256((R/'source-assets/production/fairytale-lgt-readability-v003/primary1-chest192-extraction-v001/extraction-freeze-v001.json').read_bytes()).hexdigest()),
 ('primary1-eighteen-source-index-v001.json','combined-18-source-index-Chest192-Near189-Far190-v001.json'),
 ('Chest4反向视角重点检查。E289后才Root看新图。','192六相视角已原图初审，但挂点尚未测；189近肩／190远肩保留实际Source。新E295后才Root看新图。')]:
 assert a in s;s=s.replace(a,b)
new.write_text(s,encoding='utf-8');print(new.as_posix())
