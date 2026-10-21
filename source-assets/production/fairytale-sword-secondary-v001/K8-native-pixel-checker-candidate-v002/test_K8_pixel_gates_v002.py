"""Host malformed-input tests only; never actual native evidence."""
import importlib.util, unittest, math, zlib
from copy import deepcopy
from pathlib import Path
import numpy as np
P=Path(__file__).with_name('verify-K8-native-pixels-v002.py')
s=importlib.util.spec_from_file_location('K8_pixels',P);K=importlib.util.module_from_spec(s);s.loader.exec_module(K)

class Gates(unittest.TestCase):
 def setUp(self):
  self.contract,self.resources,self.sources=K.source_inputs()
  self.r={'requested_facing':1,'owner':'17','run':'abc','weapon_instance':'31','armor_instance':'41','armor_version':'1','weapon_version':'2','weapon_version_end':'3'}
  f=0;g=K.expected_geometry(self.contract['frames'][f],1,[640.,500.],1.)
  stack=K.frame_stack(self.contract,f)
  slots=[]
  for i,path in enumerate(stack):
   sword=i==6
   slots.append(dict(slot=i,component=i,texture=path,selected=True,texture_ready=True,drawn=True,top=list(g['sword_top'] if sword else g['body_top']),size=[g['sword_width'] if sword else g['body_width']]*2,uv=[g['u'],0.],uv_size=[g['du'],1.],rotation=g['angle'] if sword else 0.,rotation_pivot=list(g['sword_pivot'] if sword else [0.,0.]),draw_scale=1.,scale_position=False,tint=[1.,1.,1.,1.]))
  self.o={'sim':1.,'secondary':dict(draw_id='9',player_entity_id='17',opt_in=True,owns_branch=True,profile_ready=True,atomic_preflight_ready=True,drawn=True,missing_reason='',profile_id=self.contract['profile_id'],source_contract_sha256=K.CONTRACT['sha256'],sample={'decision':2,'reason':0,'frame':0,'facing':1},binding=dict(run='abc',owner='17',weapon_instance='31',armor_instance='41',armor_version='1',weapon_version='2',active_slot=0,weapon_content='WPN-SWD-001',armor_content='ARM-LGT-001',armor=1),geometry=dict(g,ground_screen={'x':640.,'y':500.},ui_scale=1.),expected_draw_count=8,actual_stack=stack,slots=slots,residents=[dict(texture=x['texture'],ready=True,pending_initialization=False,**{'class':'Texture2D'},width=512,height=512) for x in self.resources if x['group']=='K']), 'common_draw':dict(draw_id='9',clip='sword_secondary',frame=0,facing=1,supported=True,active=True,gear_placeholder=False,actual_stack=stack)}
  for key in ('body_top','grip_screen','sword_top','sword_pivot'):self.o['secondary']['geometry'][key]=dict(zip(('x','y'),g[key]))
 def validate(self):return K.typed_slots(self.o,self.r,self.contract,self.resources)
 def test_real_source_inputs(self):self.assertEqual((len(self.resources),len(self.sources)),(81,81))
 def test_nominal_typed(self):self.assertEqual(len(self.validate()),8)
 def test_missing_slot(self):self.o['secondary']['slots'].pop();self.assertRaises(ValueError,self.validate)
 def test_swapped_depth(self):self.o['secondary']['slots'][5],self.o['secondary']['slots'][6]=self.o['secondary']['slots'][6],self.o['secondary']['slots'][5];self.assertRaises(ValueError,self.validate)
 def test_double_uv_mirror(self):self.o['secondary']['slots'][0]['uv_size'][0]=-1.;self.assertRaises(ValueError,self.validate)
 def test_extra_tint(self):self.o['secondary']['slots'][0]['tint'][0]=.8;self.assertRaises(ValueError,self.validate)
 def test_nan_geometry(self):self.o['secondary']['slots'][0]['top'][0]=float('nan');self.assertRaises(ValueError,self.validate)
 def test_unknown_draw_scale(self):self.o['secondary']['slots'][0]['draw_scale']=2.;self.assertRaises(ValueError,self.validate)
 def test_changed_display_scale(self):self.o['secondary']['geometry']['ui_scale']=2.;self.assertRaises(ValueError,self.validate)
 def test_stale_draw_id(self):self.o['common_draw']['draw_id']='8';self.assertRaises(ValueError,self.validate)
 def test_wrong_resource(self):self.o['secondary']['residents'][0]['texture']='other';self.assertRaises(ValueError,self.validate)
 def test_unmeasured_metadata(self):del self.o['secondary']['slots'][6]['rotation_pivot'];self.assertRaises((ValueError,KeyError),self.validate)
 def test_left_single_uv(self):
  self.r['requested_facing']=-1;d=self.o['secondary'];d['sample']['facing']=-1;self.o['common_draw']['facing']=-1;g=K.expected_geometry(self.contract['frames'][0],-1,[640.,500.],1.)
  d['geometry'].update(g)
  for k in ('body_top','grip_screen','sword_top','sword_pivot'):d['geometry'][k]=dict(zip(('x','y'),g[k]))
  for i,q in enumerate(d['slots']):
   q.update(top=list(g['sword_top'] if i==6 else g['body_top']),uv=[1.,0.],uv_size=[-1.,1.],rotation=g['angle'] if i==6 else 0.,rotation_pivot=list(g['sword_pivot'] if i==6 else [0.,0.]))
  self.assertEqual(len(self.validate()),8)
 def test_original_gate_rejects_wrong_pixels(self):
  error=np.ones((20,20))*255;opaque=np.ones((20,20),dtype=bool);self.assertRaises(ValueError,K.P.fixed_optical_gate,error,opaque,opaque)
 def test_original_path_escape(self):self.assertRaises(ValueError,K.P.file_under,Path(__file__).parent,'../fake.png')
 def resource(self):
  p=self.resources[0];return p,dict(texture=p['texture'],frame=p['frame'],component=p['component'],source_SHA_metadata=p['sha256'],source_RGBA_SHA_metadata=p['rgba_sha256'],resource_ready=True,pending_initialization=False,**{'class':'Texture2D'},width=512,height=512,sRGB=True,RHI_format=2,editor_source_format='TSF_BGRA8',read_flags='RCM_UNorm/Mip0/LinearToGamma=false; BGRA8/RGBA8 UNORM(_SRGB) byte copy',read_start_monotonic_s=1.,read_stop_monotonic_s=2.)
 def test_readback_metadata(self):p,x=self.resource();K.resource_metadata(x,p,3.)
 def test_false_srgb(self):p,x=self.resource();x['sRGB']=False;self.assertRaises(ValueError,K.resource_metadata,x,p,3.)
 def test_changed_source_metadata(self):p,x=self.resource();x['source_SHA_metadata']='0'*64;self.assertRaises(ValueError,K.resource_metadata,x,p,3.)
 def test_lossy_gpu_format(self):p,x=self.resource();x['RHI_format']=5;self.assertRaises(ValueError,K.resource_metadata,x,p,3.)
 def test_readback_after_startup(self):p,x=self.resource();self.assertRaises(ValueError,K.resource_metadata,x,p,1.5)
 def test_actual_readback_bytes(self):
  b=self.sources[self.resources[0]['texture']][...,[2,1,0,3]].tobytes();K.full_readback_bytes(b,b,zlib.crc32(b)&0xffffffff)
 def test_changed_gpu_byte_with_correct_crc(self):
  b=self.sources[self.resources[0]['texture']][...,[2,1,0,3]].tobytes();bad=bytes([b[0]^1])+b[1:];self.assertRaises(ValueError,K.full_readback_bytes,bad,b,zlib.crc32(bad)&0xffffffff)
 def test_wrong_gpu_crc(self):
  b=self.sources[self.resources[0]['texture']][...,[2,1,0,3]].tobytes();self.assertRaises(ValueError,K.full_readback_bytes,b,b,(zlib.crc32(b)^1)&0xffffffff)
 def test_original_source_model_has_no_unknown_background_in_gate(self):
  roi,color,alpha,visible=K.projection(self.validate(),self.sources);opaque=(alpha>=.999)&(np.max(color,axis=-1)>=32);blade=(visible[6]>=.98)&(np.min(color,axis=-1)>=45);result=K.P.fixed_optical_gate(np.zeros(alpha.shape),opaque,blade);self.assertGreaterEqual(result[0],150);self.assertGreaterEqual(result[1],8)
 def test_forged_viewport_pixels_fail_model_gate(self):
  roi,color,alpha,visible=K.projection(self.validate(),self.sources);opaque=(alpha>=.999)&(np.max(color,axis=-1)>=32);blade=(visible[6]>=.98)&(np.min(color,axis=-1)>=45);bad=255.-color.astype(float);error=np.mean(np.abs(bad-color),axis=-1);self.assertRaises(ValueError,K.P.fixed_optical_gate,error,opaque,blade)
 def test_missing_helmet_can_pass_global_but_fails_visible_ROI(self):
  roi,color,alpha,visible=K.projection(self.validate(),self.sources);opaque=(alpha>=.999)&(np.max(color,axis=-1)>=32);blade=(visible[6]>=.98)&(np.min(color,axis=-1)>=45);error=np.zeros(alpha.shape);error[(visible[5]>=.98)&opaque]=100.;K.P.fixed_optical_gate(error,opaque,blade);self.assertRaises(ValueError,K.component_evidence,error,opaque,visible)
 def test_small_far_shoulder_stays_low_evidence(self):
  roi,color,alpha,visible=K.projection(self.validate(),self.sources);opaque=(alpha>=.999)&(np.max(color,axis=-1)>=32);out=K.component_evidence(np.zeros(alpha.shape),opaque,visible);self.assertTrue(out[1]['low_evidence_less_than8_pixels']);self.assertFalse(out[1]['ROI_error_gate_applied'])

 def test_actual_production_content_ID_allowed(self):
  self.assertEqual(self.o['secondary']['binding']['weapon_content'],'WPN-SWD-001');self.assertEqual(len(self.validate()),8)
 def test_short_nonproduction_content_ID_rejected(self):
  self.o['secondary']['binding']['weapon_content']='SWD-001';self.assertRaises(ValueError,self.validate)

if __name__=='__main__':unittest.main()
