"""Preserve actual three semantic REDs, admit frozen presenter, authorize scoped known44 trial."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os,re,shutil,subprocess
R=Path('F:/Ourgame');B=R/'source-assets/production/fairytale-guard-v001';C=B/'presentation-full-candidate-v003'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def pin(p):return dict(path=p.relative_to(R).as_posix(),bytes=p.stat().st_size,sha256=sha(p))
def write(p,v):
 assert not p.exists(),p;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
out=R/'docs/production/first-batch-v2/evidence/guard-full-v004/root-production-admission-v001';assert not out.exists();out.mkdir(parents=True)
report=R/'UnrealGame/Saved/Automation/FirstRoom-20261018-125001/index.json';r=read(report)
assert len(r['tests'])==3 and r['failed']==3 and r['succeeded']==0
assert all(t['state']=='Fail' and t['errors']==1 and t['warnings']==0 for t in r['tests'])
assert all(any(e['event']['type']=='Error' and 'Stage0:' in e['event']['message'] for e in t['entries']) for t in r['tests'])
build=R/'UnrealGame/Saved/Bootstrap/last-build.json';b=read(build);assert b['ExitCode']==0
test=R/'UnrealGame/Source/CodexDungeon/Tests/DungeonFairytaleGuardFullV003Tests.cpp';assert sha(test)=='50e7611d1d34c89b00438eb329d7da2affa2b192a4e9dc702dce9e81743f0adf'
files=sorted(p for p in (R/'UnrealGame/Source').rglob('*') if p.is_file());assert len(files)==227
files += [report,build,Path(b['Log']),R/'UnrealGame/Binaries/Win64/UnrealEditor-CodexDungeon.dll',Path(__file__)]
rows=[]
for p in files:
 row=pin(p);q=out/'actual-three-semantic-RED/files'/row['path'];q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q);rows.append(row)
for repeat in range(2):
 for row in rows:
  p=R/row['path'];q=out/'actual-three-semantic-RED/files'/row['path'];assert pin(p)==row and q.stat().st_size==row['bytes'] and sha(q)==row['sha256']
write(out/'actual-three-semantic-RED/manifest.json',dict(status='ACTUAL_UE_THREE_SELECTOR_TARGET_SEMANTIC_REDS',files=rows,verification_passes=2,tests=[dict(name=t['fullTestPath'],errors=t['errors'],warnings=t['warnings']) for t in r['tests']]))
for source in ['DungeonFairytaleGuardFullPoseV003.h','DungeonFairytaleGuardFullDrawStateV003.h','DungeonFairytaleGuardFullPresentationV003.cpp']:
 src=C/'production-source'/source;dst=R/'UnrealGame/Source/CodexDungeon'/source
 if source!='DungeonFairytaleGuardFullPoseV003.h':assert not dst.exists()
 shutil.copy2(src,dst);os.utime(dst,None);assert sha(src)==sha(dst)
patch=C/'patches/minimal-HUD-full-versioned-entry-v003.patch'
for mode in ['--check',None]:
 p=subprocess.run(['git','apply','-p0']+([mode] if mode else [])+[str(patch)],cwd=R,capture_output=True,text=True,encoding='utf-8');(out/('HUD-check.log' if mode else 'HUD-apply.log')).write_text(p.stdout+p.stderr,encoding='utf-8');assert p.returncode==0
for name in ['DungeonHUD.h','DungeonHUD.cpp']:os.utime(R/'UnrealGame/Source/CodexDungeon'/name,None)
registration=B/'root-full-registration-v001';assert not registration.exists();registration.mkdir()
trial=read(B/'presentation-full-candidate-v004/root-templates/full-known44-row-trial-record-TEMPLATE-NOT-APPROVED-v004.json')
stamp=datetime.now(timezone.utc).isoformat();record='Root.GuardKnown44.v004.20261018.ScopedTrial'
trial.update(schema='guard-full-known44-Root-scoped-trial-v001',is_template=False,RootApproved=True,approved_by='Root',approved_at_utc=stamp,RecordId=record,FinalAccepted=False,scope='Known source poses/registration admitted for real runtime review only. No final joins, footlock, complete enemy, normal full combat or audio acceptance.',blocked_clips=['Move','StompActive','StompRecovery'])
approved=[]
for row in trial['rows']:
 allowed=row['native_source_id']>0 and row['clip'] not in trial['blocked_clips']
 row.update(trial_allowed=allowed,final_accepted=False,trial_approval_record=record+'.'+row['clip'] if allowed else None,approved_by_Root=allowed,approved_at_utc=stamp if allowed else None,join_visual_review_passed=None,footlock_certified=False)
 if allowed:approved.append(row['clip'])
assert len(approved)==10 and sum(len(x['frames']) for x in trial['rows'])==44
trial['material_limits']='StompWindup222 is FAR foot lift/NEAR support source variant. Death floors after upright are artist standing-root propagation. Axe joins and all states need real native review; rejected Move221/223/226 and Stomp224/225 remain closed.'
write(registration/'row-trial-approval.json',trial)
data=R/'UnrealGame/Source/CodexDungeon/DungeonFairytaleGuardFullDataV003.inl';text=data.read_text(encoding='utf-8-sig');changed=[]
def open_row(match):
 block=match.group();clip=re.search(r'R\.Clip=EClip::(\w+);',block)[1]
 if clip not in approved:return block
 needle='R.TrialAllowed=false;R.FinalAccepted=false;R.TrialApprovalRecord=TEXT("");';assert block.count(needle)==1
 changed.append(clip);return block.replace(needle,'R.TrialAllowed=true;R.FinalAccepted=false;R.TrialApprovalRecord=TEXT("'+record+'.'+clip+'");')
text=re.sub(r'\{FRow R;.*?A\.Add\(MoveTemp\(R\)\);\}',open_row,text,flags=re.S);assert set(changed)==set(approved)
data.write_text(text,encoding='utf-8');os.utime(data,None)
prepared=read(B/'presentation-full-candidate-v004/prepared-import/import-manifest-28-PREPARED-NOT-APPROVED-v004.json')
old=sorted(p for p in (R/'UnrealGame/Content/Production').rglob('*') if p.is_file());assert len(old)==1226
oldrows=[pin(p) for p in old]
for repeat in range(2):
 for row in oldrows:assert pin(R/row['path'])==row
assert len(prepared['assets'])==28 and all(not Path(x['saved_path']).exists() for x in prepared['assets'])
for asset in prepared['assets']:
 p=Path(asset['source']['path']);assert p.stat().st_size==asset['source']['bytes'] and sha(p)==asset['source']['sha256']
manifest=dict(schema='guard-full-known44-Root-native-import28-v001',RootImportApproved=True,prepared_only=False,expected_old_count=1226,expected_new_count=28,expected_final_count=1254,namespace=prepared['namespace'],root_trial_registration=dict(path=(registration/'row-trial-approval.json').as_posix(),bytes=(registration/'row-trial-approval.json').stat().st_size,sha256=sha(registration/'row-trial-approval.json')),old_production_files=oldrows,assets=prepared['assets'],existing_reuse_assets=prepared.get('existing_reuse_assets',prepared.get('existing_reuse',[])),settings=prepared['settings'],runtime_verified=False,formal_complete_units=0)
write(registration/'import-manifest.json',manifest)
assert sha(test)=='50e7611d1d34c89b00438eb329d7da2affa2b192a4e9dc702dce9e81743f0adf'
assert len([p for p in (R/'UnrealGame/Source').rglob('*') if p.is_file()])==229
write(out/'admission.json',dict(status='SAME_THREE_NATIVE_REDS_RETAINED_PRODUCTION_FULL_KNOWN44_SCOPED_TRIAL_ADMITTED',test_unchanged=pin(test),full_trial=pin(registration/'row-trial-approval.json'),import_manifest=pin(registration/'import-manifest.json'),source_files=229,expected_registry_only_plan=184,production_files_before_import=1226,new_imports_pending=28,formal_complete_units=0))
print(json.dumps(dict(production_admitted=True,Source229=True,same3test_unchanged=True,full_known44_trial_record=record,import_manifest_sha256=sha(registration/'import-manifest.json'))))
