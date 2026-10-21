"""Root-only UE Python import. Run --validate-only in project Python for read-only WAV checks.
Fresh destination only; actual import never replaces existing assets. No audition claim.
"""
from pathlib import Path
from datetime import datetime, timezone
import hashlib,json,sys,wave,math
HERE=Path(__file__).resolve().parent;CANDIDATE=HERE.parent;ROOT=CANDIDATE.parents[2]
MANIFEST=CANDIDATE/'audio-v001/manifest.json'
MANIFEST_SHA256='77513da470c2be29948e5e793bc417d22e87653657f6b69e5b42e41367afa838'
def need(ok,message):
 if not ok:raise RuntimeError(message)
def preflight():
 need(hashlib.sha256(MANIFEST.read_bytes()).hexdigest()==MANIFEST_SHA256,'Manifest changed')
 data=json.loads(MANIFEST.read_text(encoding='utf-8'));rows=data['assets'];need(len(rows)==11,'Exact11 cues required')
 need(data['external_api_calls']==data['third_party_samples']==0,'Original procedural provenance changed')
 for row in rows:
  p=CANDIDATE/'audio-v001'/row['file'];need(hashlib.sha256(p.read_bytes()).hexdigest()==row['sha256'] and p.stat().st_size==row['bytes'],'Changed WAV '+str(p))
  with wave.open(str(p),'rb') as w:need((w.getnchannels(),w.getsampwidth(),w.getframerate(),w.getnframes())==(1,2,48000,row['metrics']['frames']),'WAV format changed')
  need(row['metrics']['clipped_samples']==0 and -9.1<row['metrics']['peak_dBFS']<-8.9,'WAV headroom changed')
  row['source']=str(p)
 return rows
def main():
 rows=preflight()
 if '--validate-only' in sys.argv:print(json.dumps({'source_valid':True,'count':len(rows),'auditioned':False,'engine_imported':False}));return
 import unreal
 need(Path(unreal.Paths.project_dir()).resolve().parent==ROOT,'Wrong actual project')
 package='/Game/Production/FirstBatch/v028/GuardAudio';destination=ROOT/'UnrealGame/Content/Production/FirstBatch/v028/GuardAudio'
 report=ROOT/'UnrealGame/Saved/Bootstrap'/('guard-audio-v001-'+datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f')+'.json')
 receipt={'schema':'guard-audio-import-v1','manifest_sha256':MANIFEST_SHA256,'success':False,'auditioned':False,'final_audio_accepted':False,'assets':[]}
 try:
  need(not destination.exists(),'Fresh destination required; preserve existing import')
  need(not unreal.EditorAssetLibrary.does_directory_exist(package),'Existing registry destination')
  tasks=[]
  for row in rows:
   need(not unreal.EditorAssetLibrary.does_asset_exist(row['package_path']),'Object collision')
   task=unreal.AssetImportTask()
   for k,v in [('filename',row['source']),('destination_path',package),('destination_name',row['name']),('automated',True),('save',False),('replace_existing',False),('replace_existing_settings',False),('factory',unreal.SoundFactory())]:task.set_editor_property(k,v)
   tasks.append(task)
  unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks(tasks)
  for row,task in zip(rows,tasks):
   need(list(task.get_editor_property('imported_object_paths'))==[row['object_path']],'Imported path mismatch');s=unreal.load_asset(row['package_path']);need(isinstance(s,unreal.SoundWave),'Not SoundWave')
   for k,v in [('looping',False),('volume',1.0),('pitch',1.0)]:s.set_editor_property(k,v);need(s.get_editor_property(k)==v,'Sound default mismatch')
   need(s.get_editor_property('num_channels')==1 and s.get_editor_property('imported_sample_rate')==48000,'Imported rate/channel mismatch')
   duration=s.get_editor_property('duration');need(math.isfinite(duration) and abs(duration-row['metrics']['duration_s'])<=1.5/48000,'Imported duration mismatch')
   need(unreal.EditorAssetLibrary.save_loaded_asset(s,False),'Save failed');disk=destination/(row['name']+'.uasset');need(disk.is_file() and disk.stat().st_size>0,'No actual saved uasset')
   receipt['assets'].append({'cue':row['cue'],'object_path':s.get_path_name(),'actual_class':s.get_class().get_name(),'actual_duration':duration,'looping':False,'volume':1.,'pitch':1.,'source_sha256':row['sha256'],'saved_path':str(disk),'saved_sha256':hashlib.sha256(disk.read_bytes()).hexdigest(),'saved_bytes':disk.stat().st_size})
  registry=list(unreal.EditorAssetLibrary.list_assets(package,recursive=True,include_folder=False));need(set(registry)=={r['object_path'] for r in rows} and len(registry)==11,'Registry exact-set mismatch');need({p.name for p in destination.rglob('*') if p.is_file()}=={r['name']+'.uasset' for r in rows},'Disk exact-set mismatch');preflight();receipt['success']=True
 except Exception as e:receipt['error']=str(e);raise
 finally:
  report.parent.mkdir(parents=True,exist_ok=True)
  with report.open('x',encoding='utf-8') as f:json.dump(receipt,f,indent=2)
  unreal.log('Guard sound trial import receipt '+str(report))
if __name__=='__main__':main()
