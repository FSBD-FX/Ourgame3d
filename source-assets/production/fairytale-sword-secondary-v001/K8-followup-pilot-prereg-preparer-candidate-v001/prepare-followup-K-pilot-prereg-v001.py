"""Prepare one UNVERIFIED LGT follow-up pilot; never launch UE or create archive."""
from pathlib import Path
from types import SimpleNamespace
import argparse,copy,hashlib,importlib.util,json,re,sys
HERE=Path(__file__).resolve().parent
C=HERE.parent;ROOT=Path('F:/Ourgame');DOCS=ROOT/'docs/production/first-batch-v2/evidence'
TEMPLATE=C/'forward-step-native-observer-candidate-v002/prereg-current81-NotReady-template-v002.json'
CASES=('full_left','partial_right','partial_left','blocked_zero_right','blocked_zero_left')
PINS={
 'base_helper':(C/'K8-pilot-prereg-preparer-candidate-v002/prepare-first-K-pilot-prereg-v002.py',18811,'969bb99343dcb8c55e399d12e7e8ed4bf8574bca1b1a003a423c3be5144c2b45'),
 'base_freeze':(C/'K8-pilot-prereg-preparer-candidate-v002/candidate-freeze-v002.json',9187,'6e3cc9e38f0ff178bd002fbe62a31a016ae8f5eaba18bfd14f031b66f105bdc8'),
 'base_review':(ROOT/'.superpowers/sdd/2026-10-19-swd-secondary-v147/K8-pilot-prereg-preparer-review-v002.md',4375,'ca78aaae1ae0dd64d87e3ae205351d0a316954cbed4f8db4afa2f52b5a88984e'),
 'first_prereg':(DOCS/'HeroSwordSecondary-v147-v001/Root-first-K-pilot-prereg-v001/full-right.json',77773,'30b7508cd9d96248a6d227a2f0ef19bc4e8c776ac48c1a0ac000e870b2298dad'),
 'template':(TEMPLATE,78307,'1a81aad6465175a8afa7cbf2effed7d7fe8a99873f1ce73f8e60a6236dbf67d7'),
 'compiled_manifest':(ROOT/'source-assets/production/backups/v148-SWDSecondary8-308-1495-203GREEN-v001/compiled-source-manifest.json',436892,'8936717c38f67a3bb08791537f38a60d953fd5df8132c642112a507f4eeb8772'),
 'source_admission':(DOCS/'HeroSwordSecondary-v147-v001/Root-K8-source-admission-v001/actual-source-admission.json',5916,'fe3adc65ffb903fb8b2dfdc9f7d57ca72ee0ac7d31844ac29a0259a898d01a67'),
}
class NotReady(ValueError):pass
def need(ok,why):
 if not ok:raise NotReady(why)
def load(p):return json.loads(Path(p).read_text('utf-8-sig'))
def filepin(p):
 p=Path(p).resolve();b=p.read_bytes();return dict(path=p.as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def check(row):
 p=Path(row['path']);need(p.is_absolute(),'absolute immutable input path required');got=filepin(p);need(got['bytes']==row['bytes'] and got['sha256']==row['sha256'],'input pin differs: '+str(p));return p
def fixed(name):
 p,b,s=PINS[name];row=dict(path=p.as_posix(),bytes=b,sha256=s);check(row);return row
def module(p,name):
 spec=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def select_case(template,case):
 need(case in CASES,'only five original unverified LGT follow-up cases are supported')
 route=copy.deepcopy(template['cases'][case])
 need(route['facing']==(-1 if case.endswith('_left') else 1) and route['normal_route_native_verified'] is False and route['route_native_verification'] is None and route['enemy_diagnostic_used'] is False,'follow-up must preserve real facing and unverified non-diagnostic route')
 return route
def validate_output(output,archive):
 need(output.is_absolute() and output.suffix.lower()=='.json' and not output.exists(),'one unused absolute NEW JSON output required')
 need(output.resolve().is_relative_to(HERE) or output.resolve().is_relative_to(DOCS),'output must be owned follow-up directory or explicitly supplied docs evidence path')
 need(archive.is_absolute() and archive.resolve().is_relative_to(ROOT/'过程图稿与视频') and not archive.exists(),'one NEW project archive required; helper never creates it')
 need(not output.resolve().is_relative_to(archive.resolve()) and not archive.resolve().is_relative_to(output.resolve()),'prereg must remain outside archive')
def prepare(ns):
 validate_output(ns.output,ns.archive)
 base_path=check(fixed('base_helper'));freeze=load(check(fixed('base_freeze')))
 for row in freeze['members']:check(row)
 review=check(fixed('base_review')).read_text('utf-8-sig');need(re.findall(r'^Decision:[ \t]*(.*?)[ \t]*$',review,re.M)==['Approved'],'exact prerequisite helper independent approval required')
 first=load(check(fixed('first_prereg')));template=load(check(fixed('template')));route=select_case(template,ns.case)
 need(first['ready'] is True and first['route_mode']=='exploratory_pilot' and list(first['cases'])==['full_right'],'exact first full_right exploratory prereg required')
 need(first['compiled_manifest']==fixed('compiled_manifest') and first['source_admission']==fixed('source_admission'),'current closed compiled/source inputs differ from original first pilot')
 base=module(base_path,'approvedFirstKPrereq')
 # Reuse the approved complete evidence gate without copying or relaxing it.
 # Its original full_right preflight is prerequisites only, never a new run.
 gate_output=ns.output if ns.output.resolve().is_relative_to(DOCS) else DOCS/('HeroSwordSecondary-v147-v001/Root-followup-K-readonly-gate-v001/never-written-'+ns.case+'.json')
 binary=lambda key,field:first[key][field]
 pixel=first['checker_dependencies'].get('K_pixel_composition');pixel_freeze=first['checker_dependencies'].get('K_pixel_composition_freeze')
 args=SimpleNamespace(compiled_manifest=Path(first['compiled_manifest']['path']),compiled_manifest_sha=first['compiled_manifest']['sha256'],source_admission=Path(first['source_admission']['path']),source_admission_sha=first['source_admission']['sha256'],editor_executable=Path(binary('editor_executable','path')),editor_sha=binary('editor_executable','sha256'),game_dll=Path(binary('game_dll','path')),game_dll_sha=binary('game_dll','sha256'),uproject=Path(binary('uproject','path')),uproject_sha=binary('uproject','sha256'),output=gate_output,archive=ns.archive,validate_only=True,pixel_checker=Path(pixel['path']) if pixel else None,pixel_checker_sha=pixel['sha256'] if pixel else None,pixel_freeze=Path(pixel_freeze['path']) if pixel_freeze else None,pixel_freeze_sha=pixel_freeze['sha256'] if pixel_freeze else None)
 gate=base.prepare(args);need(gate['status']=='ValidatedOnly' and gate['output_written'] is False and gate['native_run_attempted'] is False and gate['archive_created'] is False,'reviewed prerequisite gate must remain read-only')
 p=copy.deepcopy(first);p.update(cases={ns.case:route},route_cases=[ns.case],route_data={ns.case:copy.deepcopy(template['route_data'][ns.case])},route_mode='exploratory_pilot',planned_archive=ns.archive.resolve().as_posix(),actual_native_K_run=False,actual_GPU_pixels_verified=False,formal_accepted=False,checker_accepted=False,FinalAccepted=False)
 p['pending']=['This selected normal route is UNVERIFIED; exploratory collection only. Actual target-case placement, K8, pixels/audio and formal acceptance require the later real run.']
 p['preparation_provenance'].update(helper=filepin(__file__),schema='followup-K-pilot-preparation-provenance-v001',prior_full_right_prereg=fixed('first_prereg'),approved_prerequisite_helper=fixed('base_helper'),approved_prerequisite_helper_review=fixed('base_review'),original_route_template=fixed('template'),selected_case=ns.case,armor_scope='LGT_ONLY_EXISTING_NATIVE_OBSERVER',archive_created=False,UE_launched=False)
 driver=module(base.check(first['driver']),'originalKFollowupDriver');original_load=driver.load
 driver.load=lambda q:copy.deepcopy(p) if Path(q).resolve()==ns.output.resolve() else original_load(q)
 got,_,_=driver.preflight(ns.output,ns.case,'exploratory_pilot');need(got==p,'original target-case driver preflight changed prereg')
 # Recheck current closed manifest and every actual file after target preflight.
 cm=load(check(fixed('compiled_manifest')))
 for row in cm['files']:base.check(row)
 check(fixed('source_admission'));check(fixed('first_prereg'));check(fixed('template'));validate_output(ns.output,ns.archive)
 argv=[sys.executable,'-B','-X','utf8',str(base.check(first['driver'])),'--prereg',ns.output.resolve().as_posix(),'--mode','exploratory_pilot','--case',ns.case,'--run','--archive',ns.archive.resolve().as_posix()]
 if not ns.validate_only:
  data=(json.dumps(p,ensure_ascii=False,indent=2)+'\n').encode('utf8');ns.output.parent.mkdir(parents=True,exist_ok=True)
  with ns.output.open('xb') as stream:stream.write(data)
 return dict(status='ValidatedOnly' if ns.validate_only else 'PreparedForExploratoryCollection',case=ns.case,output_written=not ns.validate_only,output=None if ns.validate_only else filepin(ns.output),native_run_attempted=False,archive_created=False,normal_route_native_verified=False,armor_scope='LGT_ONLY',None_armor_supported=False,formal_accepted=False,checker_accepted=False,driver_argv=argv,driver_powershell='& '+' '.join("'"+str(x).replace("'","''")+"'" for x in argv))
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--case',choices=CASES,default='full_left');ap.add_argument('--output',type=Path,required=True);ap.add_argument('--archive',type=Path,required=True);ap.add_argument('--validate-only',action='store_true');ns=ap.parse_args()
 try:print(json.dumps(prepare(ns),ensure_ascii=False,indent=2));return 0
 except (NotReady,OSError,ValueError,KeyError,TypeError,ImportError,AttributeError) as error:
  print(json.dumps(dict(status='NotReady',reason=str(error),output_written=False,native_run_attempted=False,archive_created=False,formal_accepted=False,checker_accepted=False),ensure_ascii=False,indent=2));return 2
if __name__=='__main__':sys.exit(main())
