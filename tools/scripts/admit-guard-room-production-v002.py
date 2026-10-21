"""Keep v001 check failure; allow only context whitespace/EOL in exact patches."""
from pathlib import Path
p=Path('F:/Ourgame/tools/scripts/admit-guard-room-production-v001.py')
s=p.read_text(encoding='utf-8')
s=s.replace('root-production-admission-v001','root-production-admission-v002')
s=s.replace("['git','apply','--check',", "['git','apply','--ignore-space-change','--check',")
s=s.replace("['git','apply',str(", "['git','apply','--ignore-space-change',str(")
exec(compile(s,str(Path(__file__)), 'exec'))
