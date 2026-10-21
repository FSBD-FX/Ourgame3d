"""Prepare one pinned first-K exploratory preregistration. Never launch UE/capture."""
from pathlib import Path
from datetime import datetime, timezone
import argparse, copy, hashlib, importlib.util, json, re, sys

ROOT=Path('F:/Ourgame')
HERE=Path(__file__).resolve().parent
C=ROOT/'source-assets/production/fairytale-sword-secondary-v001'
DOCS=ROOT/'docs/production/first-batch-v2/evidence'
OBS=C/'forward-step-native-observer-candidate-v002'
ARCHIVE=ROOT/'过程图稿与视频/2026-10-19_军剑K右侧前踏首次原生试验_v001'
OLD_REPORT=ROOT/'UnrealGame/Saved/Automation/FirstRoomNativeRHI-20261019-063714/index.json'
FIXED={
 'template':(OBS/'prereg-current81-NotReady-template-v002.json',78307,'1a81aad6465175a8afa7cbf2effed7d7fe8a99873f1ce73f8e60a6236dbf67d7'),
 'observer_freeze':(OBS/'candidate-freeze-v002-current81.json',10431,'13ab5c9e13643ddaccc71377a66dfe022185e8a666f26fadbb895400ba81305c'),
 'resource_table':(C/'Root-native-resource-inputs-v001/K57-plus-Ready24-source-uasset-pins-v001.json',72590,'b5f3d6689ed3cb43ded9f4bbbd25036352bf948270b123bae3c21e1521574961'),
 'compound_freeze':(C/'Root-K8-compound-source-candidate-v002/candidate-freeze-v002.json',9667,'b559dfd33c34216f6cde7601346a27c1282011bede8eadc2aa6b60d4833f90e4'),
 'source_projection':(C/'Root-K8-compound-source-candidate-v002/source-projection-v001.json',24155,'588c76e5463021df621f13be4d6822d5f4f610bbb0373135086c6b61d46ea447'),
 'namefix_freeze':(C/'forward-step-observer-name-fix-candidate-v003/candidate-freeze-v003.json',4671,'12d340c27e1c6187f00749cccbacd75439941aa2a5b0b497edcf3e61d46fef12'),
 'review':(ROOT/'.superpowers/sdd/2026-10-19-swd-secondary-v147/K8-compound-runtime-observer-source-review-v002.md',8226,'4d357efa022c48ebed703225a72b56aaab607555ec559a686fc2a55b25fc78c0'),
 'old_report':(OLD_REPORT,407740,'e508a9555760ef800309d7f67b47627f3f44968db711f9710d13183930c4f7bb'),
}

class NotReady(ValueError): pass
def need(ok,why):
 if not ok:raise NotReady(why)
def load(p):return json.loads(Path(p).read_text('utf-8-sig'))
def filepin(p):
 p=Path(p).resolve();b=p.read_bytes();return dict(path=p.as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def check(row):
 need(isinstance(row,dict) and {'path','bytes','sha256'}<=row.keys(),'complete path/bytes/SHA pin required')
 p=Path(row['path']);p=p if p.is_absolute() else ROOT/p
 got=filepin(p);need(type(row['bytes']) is int and got['bytes']==row['bytes'] and got['sha256']==row['sha256'],'pin mismatch: '+str(p));return p.resolve()
def supplied(path,sha):
 need(path.is_absolute() and re.fullmatch('[0-9a-f]{64}',sha or '') is not None,'absolute path and full SHA required')
 row=filepin(path);need(row['sha256']==sha,'supplied SHA mismatch: '+str(path));return row
def fixed(name):
 p,b,s=FIXED[name];row=dict(path=p.as_posix(),bytes=b,sha256=s);check(row);return row
def same_pin(a,b):return check(a)==check(b) and a['bytes']==b['bytes'] and a['sha256']==b['sha256']
def frozen_members(row):
 p=check(row);j=load(p)
 # Historical dependency_pins can name pre-admission actual Source. Validate
 # immutable candidate members, then current Source through AD/new CM below.
 for member in j['members']:
  need(check(member).is_relative_to(p.parent),'frozen candidate member escaped its own directory')
 return j

def validate_green203(cm,suite,expected_ids):
 for k,want in dict(registered_tests=203,passed=203,failed=0,notRun=0,inProcess=0,warnings=0).items():
  need(type(cm.get(k)) is int and cm[k]==want,'new CM complete GREEN counter required: '+k)
 for k,want in dict(succeeded=203,succeededWithWarnings=0,failed=0,notRun=0,inProcess=0).items():
  need(type(suite.get(k)) is int and suite[k]==want,'actual Automation index not wholly GREEN: '+k)
 tests=suite.get('tests');need(isinstance(tests,list) and len(tests)==203,'actual203 test rows required')
 ids=[t['fullTestPath'] for t in tests]
 need(len(set(ids))==203 and set(ids)==set(expected_ids) and len(expected_ids)==203,'actual registered203 test ID set changed or duplicated')
 for t in tests:
  need(t.get('state')=='Success' and type(t.get('warnings')) is int and t['warnings']==0 and type(t.get('errors')) is int and t['errors']==0,'actual test not clean Success: '+t['fullTestPath'])
  for entry in t.get('entries',[]):
   event=entry.get('event',{});kind=event.get('type',entry.get('type',''))
   need(str(kind).lower() not in ('error','warning','fatal'),'actual test entry contains an error/warning')
 return True

def validate_output(output,archive):
 output=Path(output);archive=Path(archive)
 need(output.is_absolute() and output.suffix.lower()=='.json' and not output.exists(),'one unused absolute NEW JSON output required')
 p=output.resolve();need(p.is_relative_to(HERE) or p.is_relative_to(DOCS),'output must be owned candidate or explicit docs evidence path')
 need(archive.is_absolute() and archive.resolve().is_relative_to(ROOT/'过程图稿与视频') and not archive.exists(),'one NEW project capture archive required; helper never creates it')
 need(not p.is_relative_to(archive.resolve()) and not archive.resolve().is_relative_to(p),'preregistration must be outside capture archive')
 return True

def validate_current(cm,ad,projection,ad_pin,exe_pin,dll_pin,project_pin):
 need(cm.get('source_files')==308 and cm.get('production_files')==1495,'new compiled manifest must describe actual Source308/Production1495')
 need(cm.get('regression_GREEN') is True and cm.get('verification_passes')==2 and cm.get('twoSHA_mismatches')==0,'actual two-pass GREEN compiled manifest required')
 need(same_pin(cm['source_admission_pin'],ad_pin),'compiled manifest admission pin differs')
 need(ad.get('schema')=='Root-K8-actual-source-admission-v001' and ad.get('actual_Source_admitted') is True and ad.get('source_before')==303 and ad.get('source_after')==308 and ad.get('production_files')==1495,'actual successful reviewed K8 source admission required')
 need(ad.get('verification_passes')==2 and ad.get('twoSHA_mismatches')==0,'actual admission verification incomplete')
 for key,known in [('candidate_freeze','compound_freeze'),('source_projection','source_projection'),('independent_review','review')]:
  need(same_pin(ad[key],fixed(known)),'actual admission wrong '+key)
 files=cm['files'];paths={}
 for row in files:
  p=check(row);need(p not in paths,'duplicate CM path');paths[p]=row
 def closure(rel,n):
  base=ROOT/rel;actual={p.resolve() for p in base.rglob('*') if p.is_file()};covered={p for p in paths if p.is_relative_to(base)}
  need(len(actual)==n and actual==covered,'new CM does not cover complete current '+rel)
 closure('UnrealGame/Source',308);closure('UnrealGame/Content/Production',1495)
 expected={x['path']:x for x in projection['existing_files']+projection['new_files']}
 need(len(ad['files'])==len(expected)==12 and sum(x['new_file'] is True for x in ad['files'])==5,'actual admission12 with5new required')
 need({r['path'] for r in ad['files']}==set(expected),'actual admission source set differs')
 for row in ad['files']:
  p=(ROOT/row['path']).resolve();need(check(row['actual'])==p and same_pin(row['actual'],paths[p]),'AD/current CM/source differ')
  need(same_pin(row['actual'],{**expected[row['path']]['after'],'path':p.as_posix()}),'actual Source differs from reviewed compound output')
 cpp=ROOT/'UnrealGame/Source/CodexDungeon/DungeonSwdForwardStepProbeV002.cpp'
 need(filepin(cpp)['sha256']=='5f0d0a978a4defb61ec338bc4d77a31ae51f45a68bba1b284d143eecb60044a9','actual fixed observer5f0d source required')
 body=(ROOT/'UnrealGame/Source/CodexDungeon/DungeonFairytaleSwordSecondaryPresentationV001.cpp').read_bytes()
 need(body.count(b'P.RuntimeReady=true;')==1 and b'P.RuntimeReady=false;' not in body,'actual complete K profile not enabled')
 need(check(dll_pin)==(ROOT/'UnrealGame/Binaries/Win64/UnrealEditor-CodexDungeon.dll').resolve(),'actual game DLL path required')
 need(same_pin(paths[check(dll_pin)],dll_pin),'actual DLL differs from compiled manifest')
 need(check(exe_pin)==Path('G:/UE_5.5/Engine/Binaries/Win64/UnrealEditor.exe').resolve(),'actual configured UE5.5 editor executable required')
 need(check(project_pin)==(ROOT/'UnrealGame/CodexDungeon.uproject').resolve() and same_pin(paths[check(project_pin)],project_pin),'actual uproject differs from compiled manifest')
 build=load(check(cm['build']));check(cm['build_log'])
 need(build.get('ExitCode')==0 and build.get('Target')=='CodexDungeonEditor','actual successful Editor build receipt required')
 need(Path(build['Log']).resolve()==check(cm['build_log']),'actual build log lineage differs')
 return build

def validate_resources(template,table):
 from PIL import Image
 rows=table['resources'];need(template['resource_pins']==rows,'template must use exact real current81 table')
 need(len(rows)==len({r['texture'] for r in rows})==81 and sum(r['group']=='K' for r in rows)==57 and sum(r['group']=='Ready' for r in rows)==24,'real K57 + retained Ready24 unique objects required')
 for row in rows:
  png=check(dict(path=row['source_png'],bytes=row['bytes'],sha256=row['sha256']));uasset=check(row['uasset'])
  package=row['texture'].split('.')[0];need(row['texture']==package+'.'+package.rsplit('/',1)[1],'exact UE object name required')
  need(uasset==(ROOT/'UnrealGame/Content'/Path(package.removeprefix('/Game/')+'.uasset')).resolve(),'resource UE path/package mismatch')
  with Image.open(png) as im:
   need(im.mode=='RGBA' and im.size==(512,512),'real source must be512 RGBA');need(hashlib.sha256(im.tobytes()).hexdigest()==row['rgba_sha256'],'actual PNG RGBA pin differs')
 need(len({(r['frame'],r['component']) for r in rows if r['group']=='K'})==57,'K frame/component closure duplicated')
 for key in ['actual_texture_import_verification','actual_native_receipt','Ready24_pin','source_contract']:check(table[key])

def prepare(ns):
 validate_output(ns.output,ns.archive)
 cm_pin=supplied(ns.compiled_manifest,ns.compiled_manifest_sha);ad_pin=supplied(ns.source_admission,ns.source_admission_sha)
 cm=load(check(cm_pin));need(cm.get('source_files')==308 and cm.get('production_files')==1495,'new compiled manifest must describe actual Source308/Production1495')
 template=load(check(fixed('template')));table=load(check(fixed('resource_table')))
 for name in ['compound_freeze','namefix_freeze']:frozen_members(fixed(name))
 # Original v002 source freeze dependencies include old pre-admission Source;
 # only its own frozen members are current artifacts, never old actual deps.
 frozen_members(fixed('observer_freeze'))
 review=check(fixed('review')).read_text('utf-8-sig')
 need(re.findall(r'^Decision:[ \t]*(.*?)[ \t]*$',review,re.M)==['Approved'],'exact independent source review must contain one Approved decision')
 old=load(check(fixed('old_report')));suite_path=check(cm['full_suite']);need(suite_path!=OLD_REPORT.resolve(),'historical203 report cannot stand in for new K build regression')
 suite=load(suite_path);validate_green203(cm,suite,{t['fullTestPath'] for t in old['tests']})
 exe_pin=supplied(ns.editor_executable,ns.editor_sha);dll_pin=supplied(ns.game_dll,ns.game_dll_sha);project_pin=supplied(ns.uproject,ns.uproject_sha)
 projection=load(check(fixed('source_projection')));ad=load(check(ad_pin));build=validate_current(cm,ad,projection,ad_pin,exe_pin,dll_pin,project_pin)
 build_time=datetime.fromisoformat(build['Utc'].replace('Z','+00:00'));ad_time=datetime.fromisoformat(ad['utc'].replace('Z','+00:00'))
 report_time=datetime.strptime(suite['reportCreatedOn'],'%Y.%m.%d-%H.%M.%S').replace(tzinfo=timezone.utc)
 need(report_time>=build_time>=ad_time,'actual regression must follow actual admission and successful build')
 validate_resources(template,table)
 driver_pin=filepin(OBS/'drive-swd-forward-step-native-v002.py');checker_pin=filepin(OBS/'check-swd-forward-step-native-v002.py')
 frozen=load(check(fixed('observer_freeze')));members={check(r):r for r in frozen['members']}
 for row in [driver_pin,checker_pin]:need(same_pin(row,members[check(row)]),'original frozen V002 Python entry changed')
 for key in ['main_mix','native_png']:check(template['checker_dependencies'][key])
 pixel_fields=[ns.pixel_checker,ns.pixel_checker_sha,ns.pixel_freeze,ns.pixel_freeze_sha]
 need(all(pixel_fields) or not any(pixel_fields),'pixel checker/freeze require both complete path/SHA pairs')
 pixel=None;pixel_freeze=None
 if all(pixel_fields):
  pixel=supplied(ns.pixel_checker,ns.pixel_checker_sha);pixel_freeze=supplied(ns.pixel_freeze,ns.pixel_freeze_sha)
  pf=frozen_members(pixel_freeze);need(check(pixel) in {check(r) for r in pf['members']},'optional checker must be frozen member')
 p=copy.deepcopy(template);route=copy.deepcopy(template['cases']['full_right'])
 need(route['facing']==1 and route['normal_route_native_verified'] is False and route['enemy_diagnostic_used'] is False and route['route_native_verification'] is None,'first full_right must remain genuinely unverified')
 p.update(ready=True,pending=['Independent actual normal route verification and K native pixels/audio remain pending; this enables exploratory collection only'],route_mode='exploratory_pilot',cases={'full_right':route},route_cases=['full_right'],route_data={'full_right':template['route_data']['full_right']},compiled_manifest=cm_pin,review_report=fixed('review'),editor_executable=exe_pin,game_dll=dll_pin,uproject=project_pin,K_profile_runtime_ready=True,observer_editor_compile_verified=True,observer_fresh_review_approved=True,placement_witness_source_ready=True)
 p['checker_dependencies']['K_pixel_composition']=pixel;p['K_pixel_composition_freeze']=pixel_freeze
 p.update(source_admission=ad_pin,compound_source_freeze=fixed('compound_freeze'),observer_namefix_freeze=fixed('namefix_freeze'),python_observer_freeze=fixed('observer_freeze'),driver=driver_pin,native_checker=checker_pin,planned_archive=ns.archive.resolve().as_posix(),actual_native_K_run=False,actual_GPU_pixels_verified=False,formal_accepted=False,checker_accepted=False,FinalAccepted=False)
 p['preparation_provenance']=dict(schema='first-K-pilot-preparation-provenance-v001',helper=filepin(__file__),resource_table=fixed('resource_table'),template=fixed('template'),actual_full203_report=cm['full_suite'],actual_build=cm['build'],old203_IDs_baseline_only=fixed('old_report'),archive_created=False,UE_launched=False)
 # Exercise the exact frozen driver's preflight without first writing an output:
 # only its initial prereg load is supplied from this validated in-memory value.
 spec=importlib.util.spec_from_file_location('originalKpilotDriver',check(driver_pin));driver=importlib.util.module_from_spec(spec);spec.loader.exec_module(driver)
 original_load=driver.load;driver.load=lambda q:copy.deepcopy(p) if Path(q).resolve()==ns.output.resolve() else original_load(q)
 got,_,_=driver.preflight(ns.output,'full_right','exploratory_pilot');need(got==p,'frozen driver preflight changed prereg')
 # Recheck roots + all CM pins after preflight, before exclusive output creation.
 check(cm_pin);check(ad_pin)
 for row in cm['files']:check(row)
 validate_output(ns.output,ns.archive)
 launch=[sys.executable,'-B','-X','utf8',str(check(driver_pin)),'--prereg',ns.output.resolve().as_posix(),'--mode','exploratory_pilot','--case','full_right','--run','--archive',ns.archive.resolve().as_posix()]
 if not ns.validate_only:
  data=(json.dumps(p,ensure_ascii=False,indent=2)+'\n').encode('utf-8');ns.output.parent.mkdir(parents=True,exist_ok=True)
  with ns.output.open('xb') as stream:stream.write(data)
 return dict(status='ValidatedOnly' if ns.validate_only else 'PreparedForExploratoryCollection',output_written=not ns.validate_only,output=None if ns.validate_only else filepin(ns.output),native_run_attempted=False,archive_created=False,route_native_verified=False,formal_accepted=False,checker_accepted=False,driver_argv=launch,driver_powershell='& '+ ' '.join("'"+str(x).replace("'","''")+"'" for x in launch))

def main():
 ap=argparse.ArgumentParser(description=__doc__)
 for name in ['compiled-manifest','source-admission','editor-executable','game-dll','uproject']:ap.add_argument('--'+name,required=True,type=Path)
 for name in ['compiled-manifest-sha','source-admission-sha','editor-sha','game-dll-sha','uproject-sha']:ap.add_argument('--'+name,required=True)
 ap.add_argument('--output',required=True,type=Path);ap.add_argument('--archive',type=Path,default=ARCHIVE);ap.add_argument('--validate-only',action='store_true')
 ap.add_argument('--pixel-checker',type=Path);ap.add_argument('--pixel-checker-sha');ap.add_argument('--pixel-freeze',type=Path);ap.add_argument('--pixel-freeze-sha')
 ns=ap.parse_args()
 try:result=prepare(ns);print(json.dumps(result,ensure_ascii=False,indent=2));return 0
 except (NotReady,OSError,KeyError,TypeError,ValueError,ImportError,AttributeError) as error:
  print(json.dumps(dict(status='NotReady',reason=str(error),output_written=False,native_run_attempted=False,archive_created=False,formal_accepted=False,checker_accepted=False),ensure_ascii=False,indent=2));return 2
if __name__=='__main__':sys.exit(main())
