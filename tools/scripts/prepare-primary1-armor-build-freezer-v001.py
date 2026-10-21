"""Extend the established freeze protocol to include exact new42 source inputs."""
from pathlib import Path
R=Path('F:/Ourgame');T=R/'tools/scripts'
s=(T/'freeze-first-unit-build.py').read_text(encoding='utf-8-sig')
needle='args = parser.parse_args()';assert s.count(needle)==1
s=s.replace(needle,"parser.add_argument('--candidate-freeze', required=True)\nparser.add_argument('--candidate-freeze-sha256', required=True)\n"+needle)
needle='rows = []\nfor source in sorted(set(paths)):';assert s.count(needle)==1
extra='''# Exact candidate source files used by the new namespace are part of this snapshot.
candidate_freeze = (root / args.candidate_freeze).resolve()
candidate_freeze.relative_to(root)
if hashlib.sha256(candidate_freeze.read_bytes()).hexdigest() != args.candidate_freeze_sha256:
    raise RuntimeError('Candidate freeze pin changed')
for row in json.loads(candidate_freeze.read_text(encoding='utf-8-sig'))['files']:
    source = Path(row['path']).resolve()
    source.relative_to(root)
    value = source.read_bytes()
    if len(value) != row['bytes'] or hashlib.sha256(value).hexdigest() != row['sha256']:
        raise RuntimeError('Candidate source changed: ' + str(source))
    paths.append(source)
paths.append(candidate_freeze)
primary_runtime = root / 'source-assets/production/fairytale-sword-armor-primary1-runtime-v001'
paths.extend(p for p in primary_runtime.rglob('*') if p.is_file())
paths.extend((root / 'UnrealGame/Saved/Bootstrap').glob('sword-armor-primary1-v001-import-*.json'))
paths.extend([Path(__file__), root / '钟盔军剑首斩穿甲试装.cmd'])
rows = []
for source in sorted(set(paths)):'''
s=s.replace(needle,extra)
out=T/'freeze-primary1-armor-build-v001.py';assert not out.exists();compile(s,str(out),'exec');out.write_text(s,encoding='utf-8')
print('Prepared candidate-inclusive immutable build freezer; no freeze/build invoked.')
