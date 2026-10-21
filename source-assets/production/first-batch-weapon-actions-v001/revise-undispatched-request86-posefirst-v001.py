"""Parent pose-first steering arrived before dispatch; preserve planned prompt history."""
from pathlib import Path
import importlib.util
P=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('record',P/'production-record.py');r=importlib.util.module_from_spec(s);s.loader.exec_module(r)
ledger=r.read(r.LEDGER);e=next(x for x in ledger['requests'] if x['request_number']==86)
assert e['status']=='requested' and 'raw_path' not in e and ledger['requested_count']==86
e.setdefault('undispatched_plan_history',[]).append({'asset':e['asset'],'prompt_path':e['prompt_path'],'prompt':e['prompt'],'references':e['references'],
 'status':'superseded_before_any_API_dispatch','reason':'parent requires validated single mechanical keyposes before six-frame sequence','recorded_utc':r.now()})
prompt=P/'prompts/86-XBW-direct-string-start-keypose.txt'
refs=[P/'references/XBW-ready-assembled-cell0-v001.png',P.parent/'first-batch-weapon-components-v001/components/XBW001-neutral-component-v002.png',P/'references/XBW-direct-string-four-keypose-geometry-v001.png']
e.update(asset='XBW-direct-string-start-keypose',prompt_path=str(prompt),prompt=prompt.read_text('utf-8'),references=[{'path':str(p),'sha256':r.sha(p)} for p in refs],
 dispatch_pending=True,dispatch_scope='single_keypose_only_no_grid_API_was_issued_for_old_prompt')
r.write(r.LEDGER,ledger)
for p in [prompt,P/'prompts/86-XBW-direct-string-reload-source.txt']:r.archive(p,p.relative_to(P),'prompt_history_single_pose_steering_before_dispatch')
print({'request':86,'pending':True,'registered_count':ledger['requested_count'],'actual_completed_API_count':sum('raw_path'in x for x in ledger['requests']),'remaining':ledger['remaining_batch_requests']})
