from pathlib import Path
R=Path('F:/Ourgame');p=R/'tools/scripts/retain-leather-integer-assembly-v001.py';o=R/'tools/scripts/retain-leather-primary1-integer-assembly-v002.py';assert not o.exists();s=p.read_text(encoding='utf-8')
for a,b in [('ready-integer-assembly-v001','primary1-integer-assembly-v002'),('2026-10-17_软皮轻甲四帧整数试装_v001','2026-10-17_软皮轻甲首刀六帧整数试装_v002'),('assembly-freeze-v001.json','delivery-freeze-v002.json'),('804ec889a031fd0cffec806ce5764eb701fa4be0c20dc767b9ed797f13aaa682','d97d35bebcf85d3f054377262912c1319a933cd8f325d622e579cb27978b5257'),('range(4)','range(6)'),('eight exact','twelve exact'),('body3layers unchanged','actual Body159v003 four layers unchanged'),('各四帧','各六帧'),('原Body158三身体层','实际Body159v003四身体层')]:
 assert a in s;s=s.replace(a,b)
o.write_text(s,encoding='utf-8');print(o.as_posix())
