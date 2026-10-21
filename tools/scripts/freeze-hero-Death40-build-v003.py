"""Fresh full-GREEN snapshot also binds frozen production, observer and manual tooling."""
from pathlib import Path
_template=Path(__file__).with_name('freeze-hero-Death40-build-v001.py')
_prior_wrapper=Path(__file__).with_name('freeze-hero-Death40-build-v002.py')
_source=_template.read_text(encoding='utf-8')
for _old,_new in [
 ("with p.open('rb') as f:","with io(p).open('rb') as f:"),
 ('bytes=p.stat().st_size,sha256=sha(p)', 'bytes=io(p).stat().st_size,sha256=sha(p)'),
 ("assert p.stat().st_size==x['bytes'] and sha(p)==x['sha256'],p", "assert io(p).stat().st_size==x['bytes'] and sha(p)==x['sha256'],p"),
 ('files={Path(__file__),report,build,log,dll,', 'files={_template,_prior_wrapper,Path(__file__),report,build,log,dll,'),
 ("(['Death40-native-observer-candidate-v001'] if a.mode=='green' else [])", "(['Death40-native-observer-candidate-v001','Death40-runtime-production-v001','Death40-manual-checkpoint-tooling-candidate-v001'] if a.mode=='green' else [])"),
 ("out=R/'source-assets/production/backups'/a.version", "if a.mode=='green':\n for _extra in ['docs/production/first-batch-v2/evidence/hero-Death40-v001/root-observer-admission-v002/source-admission-v001.json','tools/scripts/admit-hero-Death40-observer-v001.py','tools/scripts/admit-hero-Death40-observer-v002.py']:\n  _q=R/_extra;assert _q.exists();files.add(_q)\nout=R/'source-assets/production/backups'/a.version")]:
 assert _source.count(_old)==1,_old
 _source=_source.replace(_old,_new)
exec(compile(_source,str(_template),'exec'),globals())
