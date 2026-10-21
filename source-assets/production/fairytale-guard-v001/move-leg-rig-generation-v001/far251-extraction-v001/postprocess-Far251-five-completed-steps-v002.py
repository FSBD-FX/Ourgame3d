"""Process three distinct static part roles with one shared illustration scale."""
from pathlib import Path
import hashlib,json,shutil,subprocess,sys,zipfile
import numpy as np
from PIL import Image

R=Path('F:/Ourgame');O=R/'source-assets/production/fairytale-guard-v001/move-leg-rig-generation-v001';A=R/'source-assets/production/fairytale-guard-v001/art-preparation-v001'
OUT=Path(__file__).resolve().parent;SG=Path('C:/Users/22499/.codex/skills/sprite-gen');PY=SG/'.venv/Scripts/python.exe'
PREP=O/'near-far-after-Rest249-context-input-v001';SRC=PREP/'far3kit/run-guard-far3kit-Rest249-context-v001';READY=A/'armed-ready4-extraction-v001/run-ready209-shared-HD-v001'
RAW=O/'process-batches/2026-10-18-Guard-Move-far3kit-native-v001/raw/move_far_kit.png';RUN=OUT/'run-far251-threeparts-shared-HD-v001'
MEDIA=R/'过程图稿与视频/2026-10-18_裂岩守卫Far251大腿小腿脚整kit共享提取_v001'
RETENTION=Path('E:/OurGame/Knight/过程图稿与视频/2026-10-18-OurgameUE-GuardMoveFar3-native251-v555/E-retention-index-v001.json')
assert Path(sys.executable).resolve()==PY.resolve() and RUN.exists() and not MEDIA.exists()
def pin(p):
 b=Path(p).read_bytes();return dict(path=Path(p).as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def write(n,v):
 p=OUT/n;p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x',encoding='utf-8',newline='\n') as f:f.write(v if isinstance(v,str) else json.dumps(v,ensure_ascii=False,indent=2)+'\n')
 return p
def command(n,args):
 q=subprocess.run(args,capture_output=True,text=True,encoding='utf-8');log=write('logs/'+n+'.log',q.stdout+q.stderr);record=dict(argv=args,actual_exit_code=q.returncode,log=pin(log));write('logs/'+n+'-command.json',record);assert q.returncode==0,record;return record

rawpin=pin(RAW);assert rawpin['sha256']=='50af7f91aeb278e53e6909bcfd34a37d34ae57ca0f629541602d3cc0270f7f5a' and rawpin['bytes']==1379236
assert Image.open(RAW).mode=='RGB' and Image.open(RAW).size==(2172,724)
ret=json.loads(RETENTION.read_text(encoding='utf-8-sig'));assert ret['verification_passes']==2 and ret['source_and_member_hash_mismatches']==0
member=next(x for x in ret['files'] if x['sha256']==rawpin['sha256'] and x['bytes']==rawpin['bytes'])
with zipfile.ZipFile(ret['packet']['path']) as z:assert z.read(member['member'])==RAW.read_bytes()
preparedpin=pin(SRC/'sprite-request.json');freezepin=pin(PREP/'NearFar-context-pending-input-freeze-v001.json')
actualprompt=PREP/'far3kit/Root-native-fullprompt-Rest249-context-v001.txt';assert pin(actualprompt)['sha256']=='a9d27cfd44ef680823dc4b92a8ee806615cc19746768acd6ccdfd69f1448f8e9'
assert any(x['sha256']==pin(actualprompt)['sha256'] for x in ret['files'])
commands=[json.loads((OUT/'logs'/f'{n}-command.json').read_text(encoding='utf-8')) for n in ['extract','inspect','compose','export-curated','preview']]
assert all(x['actual_exit_code']==0 for x in commands)
fm=json.loads((RUN/'frames/frames-manifest.json').read_text(encoding='utf-8'));ir=json.loads((RUN/'inspect-report.json').read_text(encoding='utf-8'));assert fm['ok'] and fm['errors']==fm['warnings']==[]
carried=[]
for i in range(4):
 old=READY/f'frames/right/idle/frame-{i}.png';new=RUN/f'frames/right/idle/frame-{i}.png';assert np.array_equal(np.array(Image.open(old)),np.array(Image.open(new)))
 carried.append(dict(frame=i,accepted=pin(old),reextracted=pin(new),RGBA_equal=True))
shared=next(x['shared_row_fit'] for x in fm['rows'] if x['state']=='right_move_far_kit');assert len(shared['frame_records'])==3 and len(set(x['shared_scale'] for x in shared['frame_records']))==1
parts=[]
for i,role in enumerate(['far_thigh','far_shin','far_foot']):
 p=RUN/f'curated/frame-{i}.png';im=Image.open(p).convert('RGBA');a=np.array(im);assert im.size==(512,512) and np.array_equal(a,np.array(Image.open(RUN/f'frames/right/move_far_kit/frame-{i}.png')))
 al=a[:,:,3];mag=np.all(a[:,:,:3]==[255,0,255],axis=2);box=list(im.getbbox());markers={'hip':None,'knee':None} if i==0 else {'knee':None,'ankle':None} if i==1 else {'ankle':None,'heel':None,'toe':None}
 parts.append(dict(role_index=i,component=role,source=pin(p),RGBA_sha256=hashlib.sha256(a.tobytes()).hexdigest(),curated_RGBA_equal=True,
  alpha_bbox_COMPONENT_ONLY_NOT_STANDING=box,safe_canvas_margins_ltrb=[box[0],box[1],512-box[2],512-box[3]],
  alpha_nonzero_pixels=int((al>0).sum()),alpha128_pixels=int((al>=128).sum()),alpha255_pixels=int((al==255).sum()),pure_magenta_any_alpha=int((mag&(al>0)).sum()),pure_magenta_core128=int((mag&(al>=128)).sum()),
  actual_transparent_View=False,artist_surface_pivots=markers,author_axis_length=None,art_unit_conversion=None,overlap_interface_fit=None,assembled_floor=None))
keyed=native.remove_chroma_background(Image.open(RAW),(255,0,255),96.,180.,18.,unmix_reach=4,spill_max_fraction=.005);ka=np.array(keyed)[:,:,3]
edges={k:dict(nonzero_alpha_pixels=int((v>0).sum()),core128_pixels=int((v>=128).sum())) for k,v in dict(left=ka[:,0],right=ka[:,-1],top=ka[0,:],bottom=ka[-1,:]).items()}
index=write('Far251-threepart-curated-source-index-v001.json',dict(schema='Guard-Far251-three-static-components-shared-kit-source-index-v001',state='right_move_far_kit',native_source_id=251,native_raw=rawpin,native_raw_pixel_size=[2172,724],native_raw_mode='RGB',
 raw_retention=dict(index=pin(RETENTION),actual_zip_member_byte_equal=True),actual_native_prompt=pin(actualprompt),official_prepared_request=preparedpin,official_prepared_freeze=freezepin,
 component_count=3,components=parts,runtime_animation_frames=0,SG_preview='One-second static-part slideshow of3differentroles; not three locomotion poses or playableMove timing.',shared_row_fit=shared,
 exact_existingReady209_four_RGBA=carried,source_outer_edge_checks=edges,source_outer_edges_clear=all(x['nonzero_alpha_pixels']==0 for x in edges.values()),
 QA=dict(extract=fm['ok'],extract_errors=fm['errors'],extract_warnings=fm['warnings'],inspect_ok=ir['ok'],inspect_errors=ir['errors'],inspect_warnings=ir['warnings']),
 source_pixels_not_painted=True,per_part_height_normalization=False,one_kit_scale_verified=True,
 density_scope='Shared extraction preserves relative raw part proportions inside Far3. It does not certify density versusRest/Far or a standing body height.',
 authority='Artist surface pivots/lengths/interfaces remainnull until actual retainedtransparent View and explicit2Dauthorship. No hiddenbones, assembledleg, footlock or wholebodyMove proof.',
 status='Official technical candidates only; newtransparent3 and previews pending RootE retention, not source/rig/runtime acceptance.',all18_pilot_markers_still_null=True,TrialAllowed=False,FinalAccepted=False,new_images_viewed=False))
proof=write('Far251-five-step-proof-v001.json',dict(schema='Guard-Far251-five-step-and-shared-kit-proof-v001',commands=commands,source_index=pin(index),native_calls=0,
 source_raw_unchanged=pin(RAW)==rawpin,prepared_request_unchanged=pin(SRC/'sprite-request.json')==preparedpin,prepared_freeze_unchanged=pin(PREP/'NearFar-context-pending-input-freeze-v001.json')==freezepin,
 Source_Content_tools_ledger_modified=False,new_images_viewed=False))
write('HANDOFF.md','Far251 three distinct static source roles(thigh/shin/foot) processed with one sharedkit scale; source-sizedifferences preserved. Ready209carry4RGBA exact. This is not three walkposes, a complete leg or footlock. Sourcepartmarkers/lengths/crosskitdensity/interfacefit remainnull. Originalinspect warnings preserved. Newtransparent3/preview must be RootE retained beforeView/measurement. No Source/Content/tools/ledger/E or nativecalls.\n')
freeze=write('Far251-extraction-freeze-v001.json',dict(schema='Guard-Far251-shared-kit-extraction-freeze-v001',files=[pin(p) for p in sorted(OUT.rglob('*')) if p.is_file()],new_images_viewed=False,native_called=False,TrialAllowed=False))
(MEDIA/'原件').mkdir(parents=True);shutil.copytree(OUT,MEDIA/'原件/提取包');(MEDIA/'展示副本').mkdir()
for p in (RUN/'qa').iterdir():
 if p.is_file() and p.suffix.lower() in ['.png','.gif']:shutil.copy2(p,MEDIA/'展示副本'/p.name)
for i,role in enumerate(['far_thigh','far_shin','far_foot']):shutil.copy2(RUN/f'curated/frame-{i}.png',MEDIA/f'展示副本/{role}-SOURCE512.png')
(MEDIA/'source-version-status-index.json').write_text(json.dumps(dict(schema='F-dated-source-version-status-v001',source=OUT.as_posix(),source_index=pin(index),proof=pin(proof),freeze=pin(freeze),
 files=[pin(p) for p in sorted(MEDIA.rglob('*')) if p.is_file()],status='UnviewedFar251static3parts awaiting RootE; not leg or Move animation acceptance.',Root_E_retention_pending=True,new_images_viewed=False),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(F_batch=MEDIA.as_posix(),source_index=pin(index),proof=pin(proof),freeze=pin(freeze),shared_row=shared,QA=dict(extract=fm['ok'],inspect_ok=ir['ok'],inspect_errors=ir['errors'],inspect_warnings=ir['warnings']),new_images_viewed=False),ensure_ascii=False,indent=2))
