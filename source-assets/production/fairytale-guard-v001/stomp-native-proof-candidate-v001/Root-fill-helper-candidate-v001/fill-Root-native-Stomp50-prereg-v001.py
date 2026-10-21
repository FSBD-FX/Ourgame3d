"""Root-executed fill helper. Actual approved/imported/compiled inputs only; no UE launch."""
from pathlib import Path
from datetime import datetime, timezone
import argparse, hashlib, json, runpy, tempfile

R=Path('F:/Ourgame').resolve()
HERE=Path(__file__).resolve().parent
C=HERE.parent
WHOLE_SHA='523b70ca762090ee58a9ec607598fa47e4e32c2b54d5df81e8e573dd88900c8d'
CURRENT_SOURCE=tuple('UnrealGame/Source/CodexDungeon/'+n for n in [
 'DungeonFairytaleGuardStompProfileV004.h','DungeonFairytaleGuardStompDataV004.inl',
 'Tests/DungeonFairytaleGuardStompV004Tests.cpp','DungeonFairytaleGuardFullProfileV003.h',
 'DungeonFairytaleGuardFullDrawStateV003.h','DungeonFairytaleGuardFullPresentationV003.cpp',
 'DungeonHUD.h','DungeonHUD.cpp','DungeonGuardStompProbeV001.h','DungeonGuardStompProbeV001.cpp'])

def need(value,why):
 if not value:raise ValueError(why)

def resolve(value):
 p=Path(value);return(p if p.is_absolute()else R/p).resolve()

def read(path):return json.loads(Path(path).read_text(encoding='utf-8-sig'))

def fact(path):
 path=resolve(path);b=path.read_bytes();return dict(path=path.as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())

def checked(value):
 need(isinstance(value,dict)and set(value)=={'path','bytes','sha256'},'An exact actual input pin is required')
 p=resolve(value['path']);actual=fact(p);need(actual['bytes']==value['bytes']and actual['sha256']==value['sha256'],'Actual pin changed: '+str(p));return p

def normalized(value):return fact(checked(value))

def historical(value):
 need(isinstance(value,dict)and set(value)=={'path','bytes','sha256'}and type(value['bytes'])is int and value['bytes']>=0 and isinstance(value['sha256'],str)and len(value['sha256'])==64,'Exact historical pin value required')
 # The pinned Stage0 manifest is historical authority. Its old Data path now
 # contains approved production bytes, so do not compare that old hash to disk.
 return dict(value,path=resolve(value['path']).as_posix())

def approved(value,schema):
 need(value['schema']==schema and value['is_template']is False and value['RootApproved']is True and value['FinalAccepted']is False,'Actual limited Root-approved non-template input required: '+schema)

def dump_new(path,value):
 with Path(path).open('x',encoding='utf-8')as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n')

def prepare(args):
 snapshot=resolve(args.snapshot);manifest_path=snapshot/'compiled-source-manifest.json';m=read(manifest_path)
 profile_path=resolve(args.profile);profile=read(profile_path);approved(profile,'Root-GuardStomp50-profile-contract-v001')
 need(profile['profile_id']=='GuardStomp50V004'and profile['source_count']==50 and profile['logical_budget']==57 and len(profile['rows'])==13,'Actual complete normalized50 profile required')
 need(m['strict_registered_tests']==193 and m['production_files']==1332 and m['source_files']>=262,'Actual fresh compiled193/old1326+new6/current Source262+ required')
 suite=read(checked(m['full_suite']));need(suite['succeeded']==193 and len(suite['tests'])==193 and all(suite[k]==0 for k in ['succeededWithWarnings','failed','notRun','inProcess'])and all(t['state']=='Success'and t['errors']==t['warnings']==0 for t in suite['tests']),'Actual fresh full193 is not strictly GREEN')
 files={x['path'].replace('\\','/'):x for x in m['files']};need(len(files)==len(m['files']),'Compiled snapshot repeats paths')
 for key in CURRENT_SOURCE:need(key in files,'Current compiled Source input absent: '+key);checked(files[key])
 observer_path=resolve(args.observer_admission);observer=read(observer_path)
 need(observer['schema']=='Root-GuardStomp-observer-admission-v001'and observer['success']is True and observer['FinalAccepted']is False,'Actual Root observer admission required')
 data_path=resolve(args.data_admission);data=read(data_path);approved(data,'Root-GuardStomp-approved-Data-admission-v001')
 need(data['success']is True and data['Source_count']==m['source_files']and len(data['admitted'])==1,'Actual one-file approved Data admission/readback required')
 data_key='UnrealGame/Source/CodexDungeon/DungeonFairytaleGuardStompDataV004.inl'
 need(checked(data['admitted'][0]).relative_to(R).as_posix()==data_key and normalized(data['admitted'][0])==normalized(files[data_key]),'Admitted approved Data is not the exact compiled current Data')
 stage=read(checked(observer['stage0_snapshot']));stage_files={x['path'].replace('\\','/'):x for x in stage['files']}
 need(historical(data['previous_Data_pin'])==historical(stage_files[data_key]),'Approved Data admission skipped/replaced a different Stage0 stub')
 import_path=resolve(args.import_manifest);native_path=resolve(args.native_import);independent_path=resolve(args.independent_import)
 im=read(import_path);native=read(native_path);independent=read(independent_path)
 need(im['schema']=='Root-GuardStomp6-import-v001'and(im['expected_old_count'],im['expected_new_count'],im['expected_final_count'])==(1326,6,1332),'Actual bounded new6 manifest required')
 trial=read(checked(im['root_trial_registration']));need(trial['limited_import_approved']is True and trial['FinalAccepted']is False,'Actual Root limited import approval required')
 need(native['schema']=='guard-Stomp6-actual-import-v001'and native['success']is True and native['actual_total']==1332 and native['verification_passes']==2 and native['old1326_unchanged']is True and len(native['assets'])==6 and normalized(native['manifest'])==fact(import_path),'Actual successful native6 import required')
 need(independent['schema']=='Stomp6-independent-import-twoSHA-v001'and independent['success']is True and independent['verification_passes']==2 and independent['hash_mismatches']==0 and independent['old1326_unchanged_twice']is True and independent['new6_saved_twice']is True and independent['exact_total']==1332 and normalized(independent['receipt'])==fact(native_path)and normalized(independent['manifest'])==fact(import_path),'Actual independent old/new two-SHA import verification required')
 whole=C/'Stomp-native-proof-freeze-v001.json';need(fact(whole)['sha256']==WHOLE_SHA,'Frozen native proof candidate changed')
 template=read(C/'Root-Stomp50-prereg-TEMPLATE-NOT-APPROVED-v001.json')
 need(template['is_template']is True and template['RootApproved']is False,'Original pending template was modified')
 preregs={}
 for side,label in [(-1,'left'),(1,'right')]:
  p=dict(template)
  p.update(is_template=False,RootApproved=True,pre_registered_before_capture=True,
   candidate_freeze_pin=fact(whole),source_freeze_pin=fact(C/'source-boundary-fix-v002/Stomp-source-boundary-fix-freeze-v002.json'),
   compiled_manifest_pin=fact(manifest_path),expected_source_files=m['source_files'],expected_production_files=m['production_files'],expected_strict_registered_tests=m['strict_registered_tests'],approach_side=side,
   Root_source_admission_pin=fact(observer_path),Root_data_admission_pin=fact(data_path),admitted_source_files=[files[k]for k in CURRENT_SOURCE],
   profile_contract_pin=fact(profile_path),actual_import_manifest_pin=fact(import_path),actual_import_receipt_pin=fact(native_path),independent_import_receipt_pin=fact(independent_path),actual_importer_pin=normalized(native['importer']),
   created_UTC=datetime.now(timezone.utc).isoformat(),created_by_Root_fill_helper=fact(__file__),native_started=False,native_passed=False,visual_reviewed=False,FinalAccepted=False)
  preregs[label]=p
 # Only actual approved input facts can reach this point. Run the entire frozen
 # source-only gate against private temporary JSONs before publishing any Root file.
 checker=runpy.run_path(str(C/'tooling/verify-Stomp-native-v001.py'))
 with tempfile.TemporaryDirectory(prefix='Root-Stomp50-prereg-validate-')as folder:
  for label,p in preregs.items():
   temp=Path(folder)/(label+'.json');dump_new(temp,p);checker['source_check'](snapshot,temp)
 return snapshot,preregs

def main():
 parser=argparse.ArgumentParser()
 for key in ['snapshot','profile','import-manifest','native-import','independent-import','observer-admission','data-admission']:parser.add_argument('--'+key,required=True)
 parser.add_argument('--output-dir',default='source-assets/production/fairytale-guard-v001/root-Stomp-native-prereg-v139-v001')
 args=parser.parse_args();output=resolve(args.output_dir)
 need(output.is_relative_to(R/'source-assets/production/fairytale-guard-v001')and not output.exists(),'Use a NEW Root output directory within this Guard production tree')
 snapshot,preregs=prepare(args)
 output.mkdir(parents=True,exist_ok=False)
 receipt=dict(schema='Root-Stomp50-native-prereg-fill-v001',success=False,UE_started=False,native_passed=False,FinalAccepted=False,helper=fact(__file__),source_only_validation_before_publication=True,files=[])
 try:
  checker=runpy.run_path(str(C/'tooling/verify-Stomp-native-v001.py'))
  for label,p in preregs.items():
   path=output/('Root-Stomp-native-'+label+'-prereg-v139-v001.json');dump_new(path,p);checker['source_check'](snapshot,path);receipt['files'].append(fact(path))
  receipt['success']=True
 except Exception as error:
  receipt['failure']=str(error);raise
 finally:dump_new(output/'Root-native-prereg-fill-receipt-v001.json',receipt)
 print(json.dumps(dict(output=output.as_posix(),receipt=fact(output/'Root-native-prereg-fill-receipt-v001.json'),left=receipt['files'][0],right=receipt['files'][1],source_only_verified=True,UE_started=False),ensure_ascii=False))
if __name__=='__main__':main()
