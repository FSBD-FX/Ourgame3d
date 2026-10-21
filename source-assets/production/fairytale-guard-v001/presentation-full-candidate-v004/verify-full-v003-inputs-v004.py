"""Read-only full v003 -> v004 prepared-input audit. No Unreal import or media View."""
from pathlib import Path
import hashlib,json,re
from PIL import Image
CANDIDATE=Path(__file__).resolve().parent
WORKSPACE=CANDIDATE.parents[3]
V003=CANDIDATE.parent/'presentation-full-candidate-v003'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def need(v,why):
 if not v:raise ValueError(why)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def check(p,row):need(p.is_file() and p.stat().st_size==row['bytes'] and sha(p)==row['sha256'],'Exact input pin differs: '+str(p))
def resolve(name):p=Path(name);return p if p.is_absolute() else WORKSPACE/p
def main():
 freeze=CANDIDATE/'known44-admission-milestone-freeze-v004.json'
 if freeze.exists():
  for row in read(freeze)['files']:check(CANDIDATE/row['path'],row)
 for row in read(V003/'presentation-full-freeze-v003.json')['files']:check(V003/row['path'],row)
 m=read(V003/'source-registration-resource-map-v003.json');pins=set()
 def visit(value):
  if isinstance(value,dict):
   if {'path','bytes','sha256'}<=value.keys():check(resolve(value['path']),value);pins.add(str(resolve(value['path'])))
   for x in value.values():visit(x)
  elif isinstance(value,list):
   for x in value:visit(x)
 visit(m)
 data=(V003/'production-source/DungeonFairytaleGuardFullDataV003.inl').read_text(encoding='utf-8-sig')
 blocks=dict(re.findall(r'\{FRow R;\s*R\.Clip=EClip::([A-Za-z]+);(.*?)A\.Add\(MoveTemp\(R\)\);\}',data,re.S));need(len(blocks)==13,'Full rows changed')
 frames=[];paths=set()
 for row in m['rows']:
  b=blocks[row['clip']];need('R.TrialAllowed=false;' in b and 'R.FinalAccepted=false;' in b and 'R.TrialApprovalRecord=TEXT("");' in b,'Candidate gate opened without Root record')
  fs=re.findall(r'R\.Frames.Add\(\{TEXT\("([^"]+)"\),TEXT\("([0-9a-f]{64})"\),TEXT\("([0-9a-f]{64})"\),FVector2D\(([0-9.]+),([0-9.]+)\),EPivotAuthority::([A-Za-z]+)\}\);',b)
  need(len(fs)==len(row['frames']),'Incomplete exact row: '+row['clip'])
  for a,f in zip(fs,row['frames']):
   with Image.open(resolve(f['source']['path'])) as im:
    need(im.mode=='RGBA' and im.size==(512,512) and im.getchannel('A').getextrema()==(0,255),'Non512/transparent RGBA source');rgba=hashlib.sha256(im.convert('RGBA').tobytes()).hexdigest()
   need(rgba==f['RGBA_sha256'] and a[:3]==(f['object_path'],f['source']['sha256'],rgba) and [float(a[3]),float(a[4])]==f['floor_pivot_source_px'] and a[5]==f['pivot_authority'],'Actual source/CPP/pivot/authority differs')
   frames.append(f);paths.add(f['object_path'])
 need(len(frames)==len(paths)==44 and sum(r['logical_frames'] for r in m['rows'])==57,'Full57/known44 count differs')
 prepared=read(CANDIDATE/'prepared-import/import-manifest-28-PREPARED-NOT-APPROVED-v004.json')
 need(prepared['prepared_only'] and prepared['RootImportApproved'] is False and prepared['root_approved_import_record'] is None,'Prepared manifest is not approval')
 need(len(prepared['assets'])==28 and len(prepared['existing_reuse_assets'])==16,'Exact28/16 partition differs')
 need({a['object_path'] for a in prepared['assets']}|{a['object_path'] for a in prepared['existing_reuse_assets']}==paths,'Import and reuse set differs from44 source paths')
 need({a['native_source_id'] for a in prepared['assets']}=={213,214,215,216,217,222} and all(not a['replace_existing'] for a in prepared['assets']),'Unapproved source or replacement admitted')
 trial=read(CANDIDATE/'root-templates/full-known44-row-trial-record-TEMPLATE-NOT-APPROVED-v004.json');prereg=read(CANDIDATE/'root-templates/full-known44-compiled-prereg-TEMPLATE-NOT-PREREGISTERED-v004.json')
 need(trial['is_template'] and trial['RootApproved'] is False and len(trial['rows'])==10 and all(r['trial_allowed'] is False and r['final_accepted'] is False and r['trial_approval_record'] is None and r['approved_by_Root'] is False for r in trial['rows']),'Root trial template must stay false/null')
 need(prereg['is_template'] and prereg['pre_registered_before_capture'] is False and all(prereg[k] is None for k in ['compiled_manifest_sha256','strict_registered_tests','source_files','production_files']),'No fake prereg or counts')
 gaps=read(CANDIDATE/'remaining-explicit-gaps-v004.json');need(sum(r['logical_frames'] for r in gaps['rows'])==12 and {r['clip'] for r in gaps['rows']}=={'Move','StompActive','StompRecovery'} and all(r['runtime_source_id']==0 and r['TrialAllowed'] is False and not r['frames'] for r in gaps['rows']),'Explicit gaps opened')
 print(json.dumps({'verified':True,'scope':'Candidate source, actual source PNG/RGBA and metadata only; no UE/import/native/visual result.','v003_frozen_files':36,'nested_source_registration_pins':len(pins),'known_unique_source_and_CPP_bindings':44,'new_import_proposals':28,'reuse_proposals':16,'known_logical':45,'total_logical_contract':57,'explicit_gap_entries':12,'all_trial_templates_closed':True},ensure_ascii=False))
if __name__=='__main__':main()
