import copy,importlib.util,json,sys,unittest
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('k56',HERE/'K56_import_common_v001.py');M=importlib.util.module_from_spec(spec);spec.loader.exec_module(M)
OWNERS=('BodyRest','ShoulderFar','Chest','NearArmWithoutHand','ShoulderNear','HelmetForeground','NearHand')
def fixture():
 rows=[]
 for f in range(8):
  for owner in OWNERS:
   sf=0 if f==6 else f;name=f'T_SWD001_K_{owner}_{f:02d}_v001';pkg='/Game/Production/ArtTrials/SWDSecondary/v001/'+name
   rows.append({'frame':f,'owner':owner,'source':{'path':f'F:/fixture/{owner}{sf}.png','bytes':100,'sha256':str(sf)*64},'source_rgba_sha256':str(sf)*64,'asset_name':name,'package_name':pkg,'object_path':pkg+'.'+name,'class':'Texture2D','canvas':[512,512],'source_alias_frame':0 if f==6 else None,'source_frame':sf})
 settings={'compression_settings':'TC_EDITOR_ICON','mip_gen_settings':'TMGS_NO_MIPMAPS','lod_group':'TEXTUREGROUP_UI','filter':'TF_BILINEAR','never_stream':True,'srgb':True}
 m={'schema':'SWD001-K8-texture-import-manifest-v001','source_contract':{'path':'F:/fixture/contract.json','bytes':100,'sha256':'a'*64},'expected_new_texture_count':56,'destination_root':'/Game/Production/ArtTrials/SWDSecondary/v001','replace_existing':False,'texture_settings':settings,'textures':rows,'reused_sword':{'object_path':'/Game/Old/Sword.Sword','source':{'path':'F:/fixture/sword.png','bytes':100,'sha256':'b'*64},'pivot':[99,256],'scale':.5}}
 contract={'layers':copy.deepcopy(rows),'frames':[{'frame':f,'source_frame':0 if f==6 else f,'source_alias_frame':0 if f==6 else None,'canonical_ready':f==7} for f in range(8)]}
 return m,contract
class ShapeGates(unittest.TestCase):
 def test_complete56_and_K6_alias(self):
  m,c=fixture();self.assertEqual(len(M.validate_shape(m,c)),56)
 def rejection(self,change):
  m,c=fixture();change(m,c)
  with self.assertRaises((AssertionError,KeyError,ValueError)):M.validate_shape(m,c)
 def test_missing_owner(self):self.rejection(lambda m,c:m['textures'].pop())
 def test_duplicate_target_key(self):self.rejection(lambda m,c:m['textures'].__setitem__(1,copy.deepcopy(m['textures'][0])))
 def test_replace_existing(self):self.rejection(lambda m,c:m.__setitem__('replace_existing',True))
 def test_wrong_srgb(self):self.rejection(lambda m,c:m['texture_settings'].__setitem__('srgb',False))
 def test_sword_in_texture_rows(self):self.rejection(lambda m,c:m['textures'][0].__setitem__('owner','IndependentSword'))
 def test_target_escape(self):self.rejection(lambda m,c:m['textures'][0].__setitem__('package_name','/Game/Else/Texture'))
 def test_source_contract_mismatch(self):self.rejection(lambda m,c:c['layers'][0]['source'].__setitem__('sha256','f'*64))
 def test_K6_alias_other_frame(self):self.rejection(lambda m,c:m['textures'][42].__setitem__('source_alias_frame',1))
 def test_K6_changed_source(self):self.rejection(lambda m,c:m['textures'][42]['source'].__setitem__('sha256','f'*64))
 def test_non_Texture2D(self):self.rejection(lambda m,c:m['textures'][0].__setitem__('class','Material'))
 def test_source_digest_missing(self):self.rejection(lambda m,c:m['textures'][0].pop('source_rgba_sha256'))
class ProcessGates(unittest.TestCase):
 def test_same_PID_zero_exit(self):self.assertTrue(M.validate_exit(42,{'process_id':42},{'schema':'Root-K56-native-import-exit-v001','process_id':42,'exit_code':0,'os_exit_confirmed':True}))
 def test_nonzero_OS_exit_rejected(self):
  with self.assertRaises(AssertionError):M.validate_exit(42,{'process_id':42},{'schema':'Root-K56-native-import-exit-v001','process_id':42,'exit_code':1,'os_exit_confirmed':True})
 def test_different_PID_rejected(self):
  with self.assertRaises(AssertionError):M.validate_exit(42,{'process_id':43},{'schema':'Root-K56-native-import-exit-v001','process_id':42,'exit_code':0,'os_exit_confirmed':True})
 def test_missing_exit_rejected(self):
  with self.assertRaises((AssertionError,KeyError)):M.validate_exit(42,{'process_id':42},{})
if __name__=='__main__':unittest.main()
