"""Source/hash/retention checkpoint. Does not generate, import, or edit media."""
from pathlib import Path
import importlib.util, json
from PIL import Image
P=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('record',P/'production-record.py');r=importlib.util.module_from_spec(s);s.loader.exec_module(r)
j=r.read(r.LEDGER);assert j['requested_count']==71 and len(j['requests'])==71
window=[];errors=[]
for entry in j['requests']:
    if entry['request_number']<49:continue
    paths=[Path(entry['raw_path'])]+[Path(x) for x in entry['archive_paths']]
    checks=[{'path':str(p),'exists':p.exists(),'sha256':r.sha(p) if p.exists() else None} for p in paths]
    valid=len(checks)==5 and all(x['sha256']==entry['sha256'] for x in checks)
    tool=Path(entry['tool_original_path']);tool_ok=tool.exists() and r.sha(tool)==entry['sha256']
    if not valid or not tool_ok:errors.append({'request':entry['request_number'],'raw_retention':valid,'tool_original':tool_ok})
    window.append({'request_number':entry['request_number'],'asset':entry['asset'],'status':entry['status'],'raw_path':entry['raw_path'],'sha256':entry['sha256'],
                   'raw_and_four_F_E_copies_match':valid,'tool_original_exists_and_matches':tool_ok})

names=['import-armor-idle-v001.json','import-armor-primary1-four-v002.json','import-armor-walk-four-v001.json',
       'import-armor-primary2-four-v001.json','import-armor-primary3-four-v001.json',
       'import-armor-primary2-four-sleeves-v002.json','import-armor-primary3-four-sleeves-v002.json']
contracts=[];all_files=set();current_files=set()
latest=set(names)-{'import-armor-primary2-four-v001.json','import-armor-primary3-four-v001.json'}
for name in names:
    path=P/'manifests'/name;manifest=r.read(path);files={}
    for row in manifest['common_body']:
        for key in ['body_far','body_near']:files[row[key]['path']]=row[key]
    for rows in manifest['armors'].values():
        for row in rows:
            for key in ['armor_back','armor_front','armor_near']:
                item=row.get(key)
                if item:files[item['path']]=item
    for namepath,item in files.items():
        p=Path(namepath)
        if not p.exists() or r.sha(p)!=item['sha256']:
            errors.append({'manifest':name,'path':namepath,'error':'missing_or_hash_mismatch'});continue
        with Image.open(p) as im:
            if im.mode!='RGBA' or im.size!=(512,512) or im.getchannel('A').getextrema()!=(0,255):errors.append({'path':namepath,'error':'PNG_canvas_mode_alpha'})
    all_files.update(files)
    if name in latest:current_files.update(files)
    contracts.append({'name':name,'path':str(path),'sha256':r.sha(path),'actual_unique_referenced_PNGs':len(files),'clip':manifest['clip'] if 'clip' in manifest else 'idle',
         'new_PNGs_in_version':manifest['runtime_texture_count_new'],'runtime_verified_by_asset_writer':manifest.get('runtime_verified',False),
         'complete_armor':manifest.get('complete_armor','not_asserted_in_older_schema')})
report={'schema':'armor-production-source-checkpoint-v2','recorded_utc':r.now(),'ledger':str(r.LEDGER),'ledger_sha256_at_check':r.sha(r.LEDGER),
 'EV039_requested_count':71,'EV038_prior_requested_count':24,'lifetime_requested_count':95,'current_window':j['current_window'],'remaining_current_window_requests':1,
 'new_generation_requests_during_sleeve_revision':0,'external_api_calls':0,'host_fee_usd':None,
 'window3_completed_raws_verified':len(window),'window3_four_F_E_raw_copies_verified':len(window)*4,'window3_tool_originals_verified':len(window),'window3_requests':window,
 'frozen_contracts':contracts,'current_latest_contract_unique_PNG_paths':len(current_files),'all_listed_frozen_versions_unique_PNG_paths':len(all_files),
 'PNG_count_scope':'Runtime source body/armor paths in listed contracts, excluding independent sword, masks, diagnostic previews, raw sheets and other action artwork. Historical versions not added to active action counts.',
 'runtime_or_engine_executed_by_this_writer':False,'errors':errors}
out=P/'reviews/armor-production-source-checkpoint-v002.json';assert not out.exists();r.write(out,report);r.archive(out,out.relative_to(P),'actual_source_hash_retention_checkpoint_not_runtime_acceptance')
assert not errors,errors
print(json.dumps({k:report[k] for k in ['EV039_requested_count','window3_completed_raws_verified','window3_four_F_E_raw_copies_verified','current_latest_contract_unique_PNG_paths','all_listed_frozen_versions_unique_PNG_paths','errors']},ensure_ascii=False))
