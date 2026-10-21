"""Host syntax/pure-oracle checks only. Never launches UE or decodes native/art PNGs."""
from pathlib import Path
import ast, copy, hashlib, json, math, runpy
C=Path(__file__).resolve().parent.parent
R=Path('F:/Ourgame')

def need(value,why):
 if not value:raise AssertionError(why)

def fact(p):
 p=Path(p).resolve();b=p.read_bytes();return dict(path=p.as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())

def functions(p,names):
 tree=ast.parse(Path(p).read_text(encoding='utf-8-sig'))
 return {n.name:ast.dump(n,include_attributes=False)for n in tree.body if isinstance(n,ast.FunctionDef)and n.name in names}

def main():
 checks={};compiled=[]
 for p in sorted((C/'tooling').glob('*.py')):
  compile(p.read_text(encoding='utf-8-sig'),str(p),'exec');compiled.append(p.name)
 checks['Python_in_memory_compile']=compiled
 d=runpy.run_path(str(C/'tooling/verify-Stomp-native-v001.py'))
 for path in ['Stomp-native-source-freeze-v001.json','source-boundary-fix-v002/Stomp-source-boundary-fix-freeze-v002.json']:d['frozen'](path)
 checks['original_frozen_Source_members_unchanged']=True
 try:d['source_check'](Path('HOST_SYNTHETIC_NONEXISTENT_SNAPSHOT'),C/'Root-Stomp50-prereg-TEMPLATE-NOT-APPROVED-v001.json')
 except ValueError as e:need('Actual typed Root approval required'in str(e),'Pending gate failed for wrong reason')
 else:raise AssertionError('Unapproved template admitted')
 checks['unapproved_template_rejected_before_snapshot_or_UE']=True
 oldcrc=R/'source-assets/production/fairytale-hero-state-gap-v001/death-state-preparation-v001/Death40-native-observer-candidate-v001/tooling/verify-Death-native-pixels-v001.py'
 oldtree=ast.parse(oldcrc.read_text(encoding='utf-8-sig'));newtree=ast.parse((C/'tooling/verify-Stomp-native-pixels-v001.py').read_text(encoding='utf-8-sig'))
 if isinstance(oldtree.body[0],ast.Expr):oldtree.body.pop(0)
 if isinstance(newtree.body[0],ast.Expr):newtree.body.pop(0)
 need(ast.dump(oldtree,include_attributes=False)==ast.dump(newtree,include_attributes=False),'CRC/FIFO/stop-flush helper changed beyond docstring')
 checks['CRC_FIFO_ast_identical_to_retained_Death_helper']=fact(oldcrc)
 oldoptics=R/'source-assets/production/fairytale-hero-state-gap-v001/hurt-native-observer-candidate-v001/tooling/verify-Hurt-source-pixels-v001.py'
 names=['linear','srgb','sample'];need(functions(oldoptics,names)==functions(C/'tooling/verify-Stomp-source-pixels-v001.py',names),'Fixed bilinear/sRGB primitives differ')
 checks['fixed_optics_primitive_ast_identical_to_retained_Hurt_helper']=fact(oldoptics)
 a=dict(start=13.,active_at=13.9,active_end=14.05,recovery_end=15.55)
 bins=0;rejects=0
 for clip in ['StompWindup','StompActive','StompRecovery']:
  lo,hi,starts,_=d['phase_interval'](clip,a)
  for frame,offset in enumerate(starts):
   t=lo+offset;need(d['phase_frame'](clip,a,t)==frame,'Exact actual-formula phase boundary differs');bins+=1
   if frame:need(d['phase_frame'](clip,a,math.nextafter(t,lo))==frame-1,'Previous representable sample crosses phase boundary');bins+=1
  need(d['phase_frame'](clip,a,math.nextafter(hi,lo))==len(starts)-1,'Last representable in-window sample differs');bins+=1
  for t in [math.nextafter(lo,-math.inf),hi]:
   try:d['phase_frame'](clip,a,t)
   except ValueError:rejects+=1
   else:raise AssertionError('Half-open phase endpoint accepted')
 checks['synthetic_phase_boundary_positive_checks']=bins
 checks['synthetic_half_open_endpoint_rejections']=rejects
 row=dict(native_source_id=99001,standing_extent=400,trial_approval_record='HOST_SYNTHETIC_ONLY',registration_evidence={'sha256':'a'*64},source_index={'sha256':'b'*64},frames=[dict(object_path='HOST_SYNTHETIC_ONLY/'+str(i),source={'sha256':'c'*64},RGBA_sha256='d'*64,floor_pivot=[231,464],pivot_authority=2)for i in range(6)])
 o=dict(guard_ground=[-800,-160],camera_ground=[-1000,0]);ground=[770,550.8];scale=100.8/400;bad=[];positives=0
 for facing in [-1,1]:
  f=row['frames'][1];top=[ground[0]-(231 if facing>0 else 512-231)*scale,ground[1]-464*scale]
  draw=dict(Selection=dict(Clip='StompWindup',Frame=1,Facing=facing),RequestedClip='StompWindup',AssetClip='StompWindup',AssetFrame=1,ProfileId='GuardStomp50V004',OptIn=True,TrialAllowed=True,RequestedRowTrialAllowed=True,FinalAccepted=False,RegistrationReady=True,TextureReady=True,Drawn=True,QuadSubmitted=True,ProceduralFallback=False,WholebodyIncludesAxe=True,MissingReason='',TexturePath=f['object_path'],SourceSHA256='c'*64,SourceRGBASHA256='d'*64,NativeSourceId=99001,SourceFloorPivot=[231,464],PivotAuthority=2,DrawStack=[f['object_path']],TrialApprovalRecord='HOST_SYNTHETIC_ONLY',RegistrationEvidenceSHA256='a'*64,SourceIndexSHA256='b'*64,StandingExtent=400,TargetBodyHeight=100.8,RowScale=scale,CanvasSize=512*scale,UIScale=1,GroundScreen=ground,TopScreen=top,QuadTop=top,QuadSize=[512*scale]*2,QuadUV=[0 if facing>0 else 1,0],QuadUVSize=[facing,1],QuadRotationDegrees=0,QuadRotationPivot=[0,0],QuadDrawScale=1,QuadScalePosition=False,QuadTint=[1,1,1,1],RowResidents=[dict(TexturePath=q['object_path'],ClassName='Texture2D',Width=512,Height=512,ResourceReady=True,PendingInitialization=False)for q in row['frames']])
  d['verify_draw'](draw,o,row,f);positives+=1
  cases=[('row-substitution',lambda q:q.update(AssetClip='AxeWindup')),('wrong-source-frame',lambda q:q.update(AssetFrame=0)),('double-UV-mirror',lambda q:q.update(QuadUVSize=[-facing,1])),('wrong-floor',lambda q:q.update(SourceFloorPivot=[232,464])),('wrong-body-scale',lambda q:q.update(RowScale=scale*1.1)),('partial-row',lambda q:q['RowResidents'].pop()),('permanent-red',lambda q:q.update(QuadTint=[1.45,.85,.62,1])),('procedural-fallback',lambda q:q.update(ProceduralFallback=True)),('not-submitted',lambda q:q.update(QuadSubmitted=False)),('approval-off',lambda q:q.update(RequestedRowTrialAllowed=False))]
  for label,change in cases:
   q=copy.deepcopy(draw);change(q)
   try:d['verify_draw'](q,o,row,f)
   except ValueError:bad.append(dict(facing=facing,case=label))
   else:raise AssertionError('Invalid synthetic draw admitted: '+label)
 checks['synthetic_both_facing_positive_draws']=positives
 checks['synthetic_rejected_draws']=bad
 importer=R/'tools/scripts/ue-import-guard-stomp6-v001.py';text=importer.read_text(encoding='utf-8-sig');compile(text,str(importer),'exec')
 for key in ['actual_dimensions','actual_import_filenames','actual_settings']:need(key in text,'Actual importer final schema missing '+key)
 need("('replace_existing', False)"in text,'Actual importer lost no-replacement task flag')
 checks['actual_importer_current_interface_only_not_executed']=fact(importer)
 result=dict(schema='Stomp50-host-static-verification-v001',passed=True,checks=checks,synthetic_draws_are_not_native_evidence=True,actual50_source_inputs_pending_Root=True,UE_or_UBT_started=False,PNG_decoded=False,media_viewed=False,native_GREEN_claimed=False,FinalAccepted=False)
 print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
