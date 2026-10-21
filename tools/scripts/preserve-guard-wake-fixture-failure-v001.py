from pathlib import Path
import hashlib,json,shutil
R=Path('F:/Ourgame');out=R/'docs/production/first-batch-v2/evidence/guard-art-v001/root-wake-rounding-stage0-v003/actual-fixture-premise-RED-v001';assert not out.exists();out.mkdir()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def pin(p):return dict(path=p.relative_to(R).as_posix(),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
report=R/'UnrealGame/Saved/Automation/FirstRoom-20261018-113329/index.json';r=read(report);t=r['tests'];assert len(t)==1 and t[0]['state']=='Fail' and t[0]['errors']==1 and t[0]['warnings']==0
errors=[e['event']['message'] for e in t[0]['entries'] if e['event']['type']=='Error'];assert len(errors)==1 and 'Independent positive premise' in errors[0]
build=R/'UnrealGame/Saved/Bootstrap/last-build.json';b=read(build);assert b['ExitCode']==0
files=sorted(p for p in (R/'UnrealGame/Source').rglob('*') if p.is_file());assert len(files)==223
files += [report,build,Path(b['Log']),R/'UnrealGame/Binaries/Win64/UnrealEditor-CodexDungeon.dll',Path(__file__)]
rows=[]
for f in files:
 row=pin(f);target=out/'files'/row['path'];target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(f,target);rows.append(row)
for repeat in range(2):
 for row in rows:
  source=R/row['path'];dest=out/'files'/row['path'];assert pin(source)==row and dest.stat().st_size==row['bytes'] and hashlib.sha256(dest.read_bytes()).hexdigest()==row['sha256']
(out/'manifest.json').write_text(json.dumps(dict(status='ACTUAL_FIXTURE_PREMISE_RED_PRESERVED_NOT_TARGET_DRIVER_SEMANTIC_RED',errors=errors,semantic_N_Accepted_assertion_reached=False,driver_production_patch_applied=False,files=rows,verification_passes=2,formal_complete_units=0),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
review=out.parent/'Root-17-native-samples-visible-review-v002.json';assert not review.exists()
review.write_text(json.dumps(dict(status='ALL17_AVAILABLE_NATIVE_SAMPLES_VIEWED_BUT_COVERAGE_STILL_RED',actual_visible_samples=17,missing_Wake_frame=1,WakeMask=61,ReadyMask=15,WindupMask=63,scope='Dormant1/Wake5/Ready4/Windup6/proceduralgap1 source-bound native samples; body-size and wholeaxe silhouette clear. Does not repair missing Wake or validate remaining states.',media_retention='E396',browser_retention='E400',browser_duration_s=53.52,browser_ended=True,browser_error=None,all_movie_frames_human_reviewed=False,audio_reviewed=False,formal_complete_units=0),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(files=len(rows),semantic_driver_RED=False,fixture_premise_RED=True,source223_preserved=True)))
