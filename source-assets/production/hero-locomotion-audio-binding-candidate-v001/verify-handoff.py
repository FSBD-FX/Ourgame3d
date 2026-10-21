"""Read-only current-source/exact-overlay/source-WAV validation; no UE."""
from pathlib import Path
import ast,hashlib,json,subprocess,sys
HERE=Path(__file__).resolve().parent
sha=lambda b:hashlib.sha256(b).hexdigest()
m=json.loads((HERE/'exact-seams.json').read_text(encoding='utf-8'))
for row in m['files']:
 source=Path(row['actual_source']).read_bytes()
 assert len(source)==row['source_bytes'] and sha(source)==row['source_sha256'],('Actual source drift',row['actual_source'])
 nl='\r\n' if row['line_ending']=='CRLF' else '\n';result=source.decode('utf-8')
 for op in row['operations']:
  old=op['before'].replace('\n',nl);new=op['after'].replace('\n',nl)
  assert result.count(old)==1,('Seam changed',row['actual_source'])
  result=result.replace(old,new,1)
 assert len(result.encode('utf-8'))==row['result_bytes'] and sha(result.encode('utf-8'))==row['result_sha256']
for p in HERE.rglob('*.py'):ast.parse(p.read_text(encoding='utf-8'),filename=str(p))
r=subprocess.run([sys.executable,str(HERE/'import/ue-import-hero-locomotion-v001.py'),'--validate-only'],capture_output=True,text=True)
assert r.returncode==0,r.stdout+r.stderr
print(r.stdout.strip())
print(json.dumps({'exact_seam_files':len(m['files']),'new_source_files':len(m['new_source_files']),'source_drift':False,'python_syntax':True,'actual_source_written':False,'UE_run':False}))
