"""Use Git's explicit minimal-context mode for the frozen one-line startup patch."""
from pathlib import Path
_template=Path(__file__).with_name('admit-hero-Death40-observer-v001.py')
_source=_template.read_text(encoding='utf-8')
for _old,_new in [
 ('root-observer-admission-v001', 'root-observer-admission-v002'),
 ("['git','apply','--check',str(patch)]", "['git','apply','--check','--unidiff-zero',str(patch)]"),
 ("['git','apply',str(patch)]", "['git','apply','--unidiff-zero',str(patch)]")]:
 assert _source.count(_old)==1,_old
 _source=_source.replace(_old,_new)
exec(compile(_source,str(_template),'exec'),globals())
