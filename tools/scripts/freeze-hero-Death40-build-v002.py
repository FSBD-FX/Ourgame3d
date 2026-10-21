"""Preserved v001 logic, extended Windows paths for both copy and verification."""
from pathlib import Path
_template=Path(__file__).with_name('freeze-hero-Death40-build-v001.py')
_source=_template.read_text(encoding='utf-8')
for _old,_new in [
 ('with p.open(\'rb\') as f:',"with io(p).open('rb') as f:"),
 ('bytes=p.stat().st_size,sha256=sha(p)', 'bytes=io(p).stat().st_size,sha256=sha(p)'),
 ("assert p.stat().st_size==x['bytes'] and sha(p)==x['sha256'],p", "assert io(p).stat().st_size==x['bytes'] and sha(p)==x['sha256'],p"),
 ('files={Path(__file__),report,build,log,dll,', 'files={_template,Path(__file__),report,build,log,dll,')]:
 assert _source.count(_old)==1,_old
 _source=_source.replace(_old,_new)
exec(compile(_source,str(_template),'exec'),globals())
