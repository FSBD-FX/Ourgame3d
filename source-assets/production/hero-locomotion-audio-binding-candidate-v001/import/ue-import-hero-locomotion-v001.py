"""Root-only UE import proposal; ordinary Python --validate-only is read-only.

Imports six frozen WAVs to an unused package; never overwrites or substitutes.
No generation, processing, playback, middleware migration or mix acceptance.
"""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,sys,wave,math
HERE=Path(__file__).resolve().parent
MANIFEST=HERE/'import-manifest.json'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def require(ok,message):
 if not ok:raise ValueError(message)
def preflight():
 job=json.loads(MANIFEST.read_text(encoding='utf-8'))
 freeze_path=Path(job['asset_freeze']);require(sha(freeze_path)==job['asset_freeze_sha256'],'Frozen source candidate changed')
 frozen=json.loads(freeze_path.read_text(encoding='utf-8-sig'));members={r['relative_path']:r for r in frozen['files']}
 require(job['status']=='NOT_IMPORTED_NOT_AUDITIONED','Proposal status changed')
 rows=job['rows'];require(len(rows)==job['soundwave_count']==6,'Need exactly six WAVs')
 expected={'HERO_STEP_LIGHT_01','HERO_STEP_LIGHT_02','HERO_TAKEOFF_LIGHT_01','HERO_LAND_LIGHT_01','HERO_LAND_FIRM_01','HERO_DODGE_SHORT_01'}
 require({r['cue'] for r in rows}==expected and len({r['object_path'] for r in rows})==6,'Cue/object set mismatch')
 for r in rows:
  p=Path(r['source_wav']);member=members.get('wav/'+p.name,{})
  require(p.parent.resolve()==(freeze_path.parent/'wav').resolve(),'WAV outside frozen source candidate')
  require(p.stat().st_size==r['source_bytes']==member.get('bytes') and sha(p)==r['source_sha256']==member.get('sha256'),'WAV SHA/size mismatch')
  require(r['asset_name']=='SW_AUD_'+r['cue']+'_v001','Wrong unique asset name')
  require(r['package_path']==job['package']+'/'+r['asset_name'] and r['object_path']==r['package_path']+'.'+r['asset_name'],'Object path mismatch')
  with wave.open(str(p),'rb') as w:
   require((w.getnchannels(),w.getsampwidth(),w.getframerate(),w.getcomptype())==(1,2,48000,'NONE'),'Not mono48kPCM16')
   r['frames']=w.getnframes();r['duration']=w.getnframes()/48000
   require(w.getnframes()>0 and len(w.readframes(w.getnframes()))==w.getnframes()*2,'Incomplete source PCM')
  require(r['compression']=='ADPCM' and r['loading']=='FORCE_INLINE' and r['volume']==r['pitch']==1. and r['looping'] is False,'Import defaults changed')
 dest=Path(job['destination']);require(not dest.exists() or not any(p.is_file() for p in dest.rglob('*')),'Destination occupied; no overwrite')
 return job
def execute(job):
 import unreal
 rows=job['rows'];package=job['package'];dest=Path(job['destination'])
 receipt={'schema':'HeroLocomotionAudioUEImportReceipt-v001','started_utc':datetime.now(timezone.utc).isoformat(),'manifest_sha256':sha(MANIFEST),'rows':rows,'actual_imported':0,'actual_saved':0,'success':False,'auditioned':False,'event_binding_verified':False,'final_mix_accepted':False}
 receipt_path=HERE.parent/'reports'/('ue-import-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')+'.json')
 try:
  registry=list(unreal.EditorAssetLibrary.list_assets(package,recursive=True,include_folder=False)) if unreal.EditorAssetLibrary.does_directory_exist(package) else []
  require(not registry,'Registry target occupied; no overwrite');tasks=[]
  for r in rows:
   require(not unreal.EditorAssetLibrary.does_asset_exist(r['package_path']),'Existing asset; refusing overwrite')
   t=unreal.AssetImportTask()
   for k,v in [('filename',r['source_wav']),('destination_path',package),('destination_name',r['asset_name']),('automated',True),('save',False),('replace_existing',False),('replace_existing_settings',False),('factory',unreal.SoundFactory())]:t.set_editor_property(k,v)
   tasks.append(t)
  unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks(tasks)
  for r,t in zip(rows,tasks):
   require(list(t.get_editor_property('imported_object_paths'))==[r['object_path']],'Imported object mismatch')
   s=unreal.load_asset(r['package_path']);require(isinstance(s,unreal.SoundWave),'Not a SoundWave')
   for k,v in [('looping',False),('volume',1.),('pitch',1.),('priority',r['priority']),('loading_behavior',unreal.SoundWaveLoadingBehavior.FORCE_INLINE)]:s.set_editor_property(k,v)
   s.set_sound_asset_compression_type(unreal.SoundAssetCompressionType.ADPCM)
   for k,v in [('looping',False),('volume',1.),('pitch',1.),('priority',r['priority']),('loading_behavior',unreal.SoundWaveLoadingBehavior.FORCE_INLINE)]:require(s.get_editor_property(k)==v,'Import property failed '+k)
   require(s.get_editor_property('sound_asset_compression_type')==unreal.SoundAssetCompressionType.ADPCM,'ADPCM not applied')
   require(s.get_editor_property('num_channels')==1 and s.get_editor_property('imported_sample_rate')==48000,'Imported source format mismatch')
   duration=s.get_editor_property('duration');require(math.isfinite(duration) and abs(duration-r['duration'])<=1.5/48000,'Imported duration mismatch')
   require(sha(Path(r['source_wav']))==r['source_sha256'],'Source changed during import')
   r['actual_duration']=duration;r['imported']=True;receipt['actual_imported']+=1
  for r in rows:
   s=unreal.load_asset(r['package_path']);require(unreal.EditorAssetLibrary.save_loaded_asset(s,False),'SoundWave save failed')
   p=dest/(r['asset_name']+'.uasset');require(p.is_file() and p.stat().st_size>0,'Saved SoundWave absent')
   r['saved_uasset']=str(p);r['saved_bytes']=p.stat().st_size;r['saved_sha256']=sha(p);receipt['actual_saved']+=1
  registry=list(unreal.EditorAssetLibrary.list_assets(package,recursive=True,include_folder=False))
  require(set(registry)=={r['object_path'] for r in rows} and len(registry)==6,'Registry exact set mismatch')
  actual={p.name for p in dest.rglob('*') if p.is_file()};require(actual=={r['asset_name']+'.uasset' for r in rows},'Disk exact set mismatch')
  receipt['success']=receipt['actual_imported']==receipt['actual_saved']==6
 except Exception as e:
  receipt['error']=str(e);raise
 finally:
  with receipt_path.open('x',encoding='utf-8') as f:json.dump(receipt,f,ensure_ascii=False,indent=2)
  unreal.log('Hero locomotion audio import receipt: '+str(receipt_path))
if __name__=='__main__':
 job=preflight()
 if '--validate-only' in sys.argv:print(json.dumps({'preflight':True,'WAVs':len(job['rows']),'source_PCM_bytes':sum(r['frames']*2 for r in job['rows']),'UE_run':False,'actual_imported':0}))
 else:execute(job)
