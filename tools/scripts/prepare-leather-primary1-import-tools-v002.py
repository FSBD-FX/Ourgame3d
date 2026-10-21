from pathlib import Path
import json,hashlib,re
R=Path('F:/Ourgame');T=R/'tools/scripts';O=R/'source-assets/production/fairytale-lgt-readability-v003/primary1-import-v001';M=O/'import-leather-primary1-v001.json'
def pin(p):
 b=p.read_bytes();return dict(path=p.as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def write(p,s):assert not p.exists();p.write_text(s,encoding='utf-8')
def counts(s):return re.sub(r'\b1085\b','1097',re.sub(r'\b12\b','18',s))
s=(T/'ue_leather_ready_v001_checks.py').read_text(encoding='utf-8');s=s.replace('ready-import-v001/import-leather-ready-v001.json','primary1-import-v001/import-leather-primary1-v001.json').replace('f6c8a947158c1f957cc77ad5412362a2c1cadb0acc18685e85278033936d6b36',pin(M)['sha256']).replace('v012/HeroLeatherReady','v013/HeroLeatherPrimary1').replace('old-production1085-before-import','old-production1097-before-import');s=counts(s).replace('frozen-leather-ready-18-v1','frozen-leather-primary1-18-v1').replace('T_Fairytale_LeatherReady','T_Fairytale_LeatherPrimary1').replace('range(4)','range(6)').replace("d['frame_seconds']==.167","d['durations_ms']==[85,85,60,60,155,155]")
# Literal hash strings and 512px geometry must survive count substitutions.
assert "[512,512]" in s and '72*512/416' in s and '5c667edbeb81eac54648d14ff92b8883d1b15a39a05cc3b56c17933dd29eb49a' in s
cp=T/'ue_leather_primary1_v002_checks.py';write(cp,s)
s=(T/'ue-import-leather-ready-v001.py').read_text(encoding='utf-8').replace('ue_leather_ready_v001_checks.py','ue_leather_primary1_v002_checks.py').replace('leather-ready','leather-primary1-v002').replace('Ready4 opt-in','Primary1 six-phase opt-in');s=counts(s);s=s.replace('"scope":"','"assembly_freeze":document["references"]["assembly_freeze"],\n    "scope":"');assert '[512,512]' in s
ip=T/'ue-import-leather-primary1-v002.py';write(ip,s)
s=(T/'import-leather-ready-v001.ps1').read_text(encoding='utf-8-sig').replace('ue-import-leather-ready-v001.py','ue-import-leather-primary1-v002.py').replace('leather-ready-v001-import','leather-primary1-v002-v001-import');s=counts(s);pp=T/'import-leather-primary1-v002.ps1';write(pp,s)
failure=O/'first-tools-v001-preflight-failure-preserved.json';write(failure,json.dumps(dict(actual_exit=1,reason='Unbounded 12→18 replacement changed 512px to518px; strict preflight rejected before any UE launch or asset write. V001 frozen tools remain untouched. V002 uses bounded numeric substitutions and asserts both512geometry and exact decoder hash.',game_assets_written=False,UE_launched=False),ensure_ascii=False,indent=2)+'\n')
f=O/'import-tool-freeze-v002.json';write(f,json.dumps(dict(files=[pin(M),pin(cp),pin(ip),pin(pp),pin(failure)],actual_imported=False),ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(checks=pin(cp),importer=pin(ip),wrapper=pin(pp),freeze=pin(f)),ensure_ascii=False))
