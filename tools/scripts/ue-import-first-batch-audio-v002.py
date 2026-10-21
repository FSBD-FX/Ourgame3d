"""Five CC0-derived SoundWaves; new package only, no network/playback.

Ordinary Python: --validate-only. UE Editor: py absolute-path, or graphical
UnrealEditor.exe -ExecutePythonScript=<this file>; omit --validate-only.
Preflight is stdlib only. Binding, audition and final mix remain unfulfilled.
"""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import math
import struct
import sys

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT/'source-assets/production/first-batch-audio-v002'
MANIFEST = SOURCE/'manifest.json'
MANIFEST_SHA256 = '0ea6f59b5bbb8cf32d9c6d6fbe45579de016974df049d558004fc59fe3d70e93'
PACKAGE = '/Game/Production/FirstBatch/v024/AudioDedicated'
DESTINATION = ROOT/'UnrealGame/Content/Production/FirstBatch/v024/AudioDedicated'
IDS = ('AUD-XBW-RELOAD-DRAW-01','AUD-XBW-RELOAD-INSERT-01','AUD-XBW-RELOAD-COMPLETE-01','AUD-EQUIP-ARMOR-CLOTH-01','AUD-EQUIP-ARMOR-METAL-01')
ORIGINALS = {
 IDS[0]:('source-assets/third-party/preparation-2026-10-10-v1/kenney-rpg-audio/extracted/Audio/creak3.ogg','f9638787f95004b9d2d06f8eff8e99d4e594c21b51947daf562856fbcec905d1'),
 IDS[1]:('source-assets/third-party/preparation-2026-10-10-v1/kenney-rpg-audio/extracted/Audio/metalClick.ogg','9851a69d0c613e13bceef08060ecc4148f098ef487927cbebe270d642398a3b3'),
 IDS[2]:('source-assets/third-party/preparation-2026-10-10-v1/kenney-rpg-audio/extracted/Audio/metalLatch.ogg','ba9ba60b172b3ebc131a940f25793cd2e207aca7af73dc80d637277f060f1708'),
 IDS[3]:('source-assets/third-party/preparation-2026-10-10-v1/kenney-rpg-audio/extracted/Audio/cloth2.ogg','8a7451193c38bc05483aec25dd193e163a15d44cf7fff04ac7912573231b0201'),
 IDS[4]:('source-assets/third-party/kenney/2026-10-10/kenney-impact-sounds/Audio/impactPlate_light_000.ogg','6e797cf8a5bfc52d7ed5eb47c227974c1cf2a674954fec5b539cea7d62c7282c')}
LICENSE_HASHES = {'rpg':'5735dfd72cb64cbbceda4ebc00c380c41ca680edb82ff153aa7c9ab97614c539','impact':'b49aa9c56b04528b95913de13e506a0f7c5e807b9925db9bfef86af1f91120db'}
ARCHIVE_TOPIC = '2026-10-15_猎弩装填与换甲专用音效_v002'
ARCHIVES = (ROOT/'过程图稿与视频'/ARCHIVE_TOPIC,Path('E:/OurGame/Knight/过程图稿与视频')/ARCHIVE_TOPIC)
OLD17_MANIFEST = ROOT/'source-assets/production/audio-v001/manifest.json'
OLD17_MANIFEST_SHA = 'a2ebc87a2671f58ed12d1bb03616601dc5d8ae26f8d00ae6b2a7e200c1274e62'


def require(condition,message):
    if not condition:raise ValueError(message)


def finite(value):
    return isinstance(value,(int,float)) and not isinstance(value,bool) and math.isfinite(value)


def require_unused(path):
    require(not path.exists() or not any(p.is_file() for p in path.rglob('*')),'Target occupied; refusing overwrite')


def require_exact_set(actual,expected):
    require(len(actual)==len(expected) and set(actual)==set(expected),'Missing/extra/duplicate objects')


def db(value):
    return 20*math.log10(value) if value else None


def signal_metrics(values,rate,channels):
    require(bool(values) and len(values)%channels==0 and all(finite(x) for x in values),'Invalid actual samples')
    peak=max(abs(x) for x in values);rms=math.sqrt(math.fsum(x*x for x in values)/len(values))
    return {'sample_rate_hz':rate,'channels':channels,'frames':len(values)//channels,'duration_s':len(values)/channels/rate,
            'sample_peak_linear':peak,'sample_peak_dbfs':db(peak),'rms_linear':rms,'rms_dbfs':db(rms),
            'dc_mean':math.fsum(values)/len(values),'samples_abs_ge_1':sum(abs(x)>=1 for x in values),
            'first_sample_absmax':max(abs(x) for x in values[:channels]),'last_sample_absmax':max(abs(x) for x in values[-channels:])}


def inspect_pcm16_wav(data):
    require(len(data)>=44 and data[:4]==b'RIFF' and data[8:12]==b'WAVE','Not actual RIFF WAVE')
    require(struct.unpack_from('<I',data,4)[0]+8==len(data),'RIFF length mismatch/trailing bytes')
    chunks={};offset=12
    while offset<len(data):
        require(offset+8<=len(data),'Truncated chunk')
        name=data[offset:offset+4];size=struct.unpack_from('<I',data,offset+4)[0]
        require(offset+8+size+(size%2)<=len(data) and name not in chunks,'Truncated/duplicate WAV chunk')
        chunks[name]=data[offset+8:offset+8+size];offset+=8+size+(size%2)
    require(set(chunks)=={b'fmt ',b'data'} and len(chunks[b'fmt '])==16,'Unexpected WAV format chunks')
    require(struct.unpack('<HHIIHH',chunks[b'fmt '])==(1,1,48000,96000,2,16),'Require PCM16 mono48kHz')
    pcm=chunks[b'data'];require(len(pcm)>0 and len(pcm)%2==0,'Empty/odd PCM payload')
    values=[x[0]/32768 for x in struct.iter_unpack('<h',pcm)];metrics=signal_metrics(values,48000,1)
    require(.05<=metrics['duration_s']<=.5,'Dedicated cue duration outside50..500ms')
    require(metrics['sample_peak_dbfs'] is not None and -6<=metrics['sample_peak_dbfs']<=-3,'Require3..6dBFS sample headroom')
    require(metrics['rms_linear']>0 and metrics['samples_abs_ge_1']==0,'Silent/clipped audio')
    require(values[0]==values[-1]==0,'Fade endpoints must be exactly zero')
    return metrics


def same_metrics(actual,expected):
    require(set(actual)==set(expected),'Metric fields differ')
    for key,value in actual.items():
        other=expected[key]
        if value is None:require(other is None,'Metric null mismatch '+key)
        else:require(finite(other) and abs(value-other)<=1e-11,'Actual metric mismatch '+key)


def local_path(value,parent):
    p=Path(value).resolve();require(p.is_relative_to(parent.resolve()),'Path escapes allowed exact source subtree')
    return p


def validate_manifest(m):
    require(m.get('schema')=='first-batch-dedicated-audio-source-v2' and m.get('frozen') is True,'Wrong/flexible manifest')
    require(m.get('package')==PACKAGE and m.get('actual_count')==5,'Wrong package/count')
    require([c['id'] for c in m['cues']]==list(IDS),'Missing/duplicate/wrong cue roles')
    for k in ('auditioned','engine_imported','runtime_bound','final_mix_accepted','timing_authority_changed','old17_replaced'):
        require(m.get(k) is False,'Unverified status/authority promotion '+k)
    for k in ('external_api_calls','paid_supplier_calls','image_generation_calls'):require(m.get(k)==0,'Unexpected external/generated inputs')
    require([Path(x).resolve() for x in m['archive_roots']]==[x.resolve() for x in ARCHIVES],'Wrong retained roots')
    for cue in m['cues']:
        cue_id=cue['id'];name='SW_'+cue_id.replace('-','_')+'_v002'
        require(Path(cue['file']).resolve()==(SOURCE/'wav'/f'{cue_id}__v002.wav').resolve(),'Wrong actual WAV path')
        require(cue['ue_name']==name and cue['object_path']==PACKAGE+'/'+name+'.'+name,'Wrong exact import object')
        for k in ('binding_authoritative','engine_imported','runtime_bound','auditioned','final_mix_accepted'):require(cue.get(k) is False,'Unverified cue claim '+k)
        s=cue['source'];require(s['license_id']=='CC0-1.0','No explicit CC0 provenance')
        rel,digest=ORIGINALS[cue_id]
        require(Path(s['original_path']).resolve()==(ROOT/rel).resolve() and s['original_sha256']==digest,'Wrong frozen OGG provenance')
        require(s['pack'] in LICENSE_HASHES and s['license_sha256']==LICENSE_HASHES[s['pack']],'Wrong license hash')
        p=cue['processing'];require(finite(p['gain_linear']) and p['gain_linear']>0,'Nonfinite gain')
        require(p['target_sample_peak_dbfs']==-4.5 and p['trim_start_frame']==0,'Wrong processing contract')
        require(p['fade_in_frames']==240 and p['fade_out_frames']==960,'Wrong endpoints/fade contract')
        require(p['trim_end_frame_exclusive']==cue['metrics']['frames'],'Wrong frame trim')


def preflight():
    hashes={}
    def check(path,digest):
        path=Path(path).resolve()
        require(isinstance(digest,str) and len(digest)==64 and all(x in '0123456789abcdef' for x in digest),'Malformed SHA256')
        require(path not in hashes or hashes[path]==digest,'Contradictory SHA')
        data=path.read_bytes();require(hashlib.sha256(data).hexdigest()==digest,'Changed source '+str(path))
        hashes[path]=digest;return data
    m=json.loads(check(MANIFEST,MANIFEST_SHA256).decode('utf-8-sig'));validate_manifest(m)
    check(local_path(m['inventory_path'],ROOT/'docs/production/first-batch-v1'),m['inventory_sha256'])
    require(Path(m['processing_source_path']).resolve()==(SOURCE/'prepare-local-audio-v002.py').resolve(),'Wrong processing source')
    check(m['processing_source_path'],m['processing_source_sha256'])
    require(Path(m['tool_path']).resolve()==(ROOT/'tools/runtime/asset-gen/Lib/site-packages/imageio_ffmpeg/binaries/ffmpeg-win-x86_64-v7.1.exe').resolve(),'Wrong exact FFmpeg tool')
    check(m['tool_path'],m['tool_sha256']);check(local_path(m['tool_version_path'],SOURCE),m['tool_version_sha256'])
    rows=[]
    for cue in m['cues']:
        s=cue['source'];p=cue['processing'];original=check(s['original_path'],s['original_sha256'])
        require(check(local_path(s['retained_original_path'],SOURCE/'originals'),s['retained_original_sha256'])==original,'Retained OGG differs')
        license=check(local_path(s['license'],ROOT/'source-assets/third-party'),s['license_sha256'])
        require(b'CC0' in license,'License does not declare CC0')
        require(check(local_path(s['license_copy_path'],SOURCE/'licenses'),s['license_copy_sha256'])==license,'Retained license differs')
        check(local_path(s['zip'],ROOT/'source-assets/third-party'),s['zip_sha256'])
        stereo=check(local_path(p['source_float_path'],SOURCE/'decoded-float'),p['source_float_sha256'])
        require(len(stereo)%8==0,'Wrong stereo float size')
        same_metrics(signal_metrics([x[0] for x in struct.iter_unpack('<f',stereo)],p['source_float_metrics']['sample_rate_hz'],2),p['source_float_metrics'])
        mono=check(local_path(p['mono48k_path'],SOURCE/'decoded-float'),p['mono48k_sha256'])
        require(len(mono)%4==0,'Wrong mono float size')
        whole=[x[0] for x in struct.iter_unpack('<f',mono)];same_metrics(signal_metrics(whole,48000,1),p['mono48k_metrics'])
        n=p['trim_end_frame_exclusive'];require(0<n<=len(whole),'Trim outside decoded float')
        values=[whole[i]*max(0.,min(1.,i/239,(n-1-i)/959)) for i in range(n)]
        same_metrics(signal_metrics(values,48000,1),p['pre_gain_metrics'])
        expected_pcm=struct.pack('<'+'h'*n,*[round(x*p['gain_linear']*32767) for x in values])
        wav=check(local_path(cue['file'],SOURCE/'wav'),cue['sha256']);require(len(wav)==cue['bytes'],'Wrong actual WAV bytes')
        metrics=inspect_pcm16_wav(wav);same_metrics(metrics,cue['metrics'])
        require(wav[-len(expected_pcm):]==expected_pcm,'PCM not reproduced by frozen float/cut/fade/gain/quantization')
        for cmd in p['commands']:
            require(cmd['exit_code']==0 and Path(cmd['argv'][0]).resolve()==Path(m['tool_path']).resolve(),'Bad actual processing command')
            check(local_path(cmd['stderr_path'],SOURCE/'provenance'),cmd['stderr_sha256'])
        expected_retained={str((a/c/'wav'/Path(cue['file']).name).resolve()) for a in ARCHIVES for c in ('原件','展示副本')}
        require(len(cue['retained_copies'])==4 and {str(Path(x['path']).resolve()) for x in cue['retained_copies']}==expected_retained,'Wrong F/E retained set')
        for item in cue['retained_copies']:require(check(item['path'],item['sha256'])==wav,'F/E WAV differs')
        name=cue['ue_name'];rows.append({'id':cue['id'],'role':cue['role'],'source':cue['file'],'source_sha256':cue['sha256'],
            'name':name,'package_path':PACKAGE+'/'+name,'object_path':cue['object_path'],'source_metrics':metrics,
            'source_original_sha256':s['original_sha256'],'source_license_id':s['license_id'],'saved':False})
    require(len(rows)==len({r['source'] for r in rows})==len({r['source_sha256'] for r in rows})==5,'Wrong unique five WAV count')
    old=json.loads(check(OLD17_MANIFEST,OLD17_MANIFEST_SHA).decode('utf-8-sig'))
    olddir=ROOT/'UnrealGame/Content/Production/FirstBatch/v001/Audio'
    expected_old={'SW_'+c['id'].replace('-','_')+'_v001.uasset' for c in old['cues']}
    files=[p for p in olddir.rglob('*') if p.is_file()]
    require(len(expected_old)==len(files)==17 and {p.name for p in files}==expected_old,'Existing17 exact disk set changed')
    old17={str(p.resolve()):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
    require_unused(DESTINATION)
    return {'assets':rows,'hashes':hashes,'old17':old17,'manifest':m,'summary':{
        'source_validation_success':True,'actual_WAV_count':5,'format':'PCM16 mono48000Hz','peak_gate_dbfs':[-6,-3],
        'actual_sample_peak_dbfs':[r['source_metrics']['sample_peak_dbfs'] for r in rows],
        'source_float_to_PCM_reproduced_count':5,'F_E_WAV_copies_verified':20,'verified_reference_count':len(hashes),
        'old17_baseline_count':17,'manifest_sha256':MANIFEST_SHA256,'destination':PACKAGE,
        'unreal_import_run':False,'auditioned':False,'runtime_bound':False,'final_mix_accepted':False}}


def import_in_unreal(job):
    import unreal
    require(Path(unreal.Paths.project_dir()).resolve().parent==ROOT,'Wrong actual UE project')
    stamp=datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f')
    path=ROOT/'UnrealGame/Saved/Bootstrap'/f'first-batch-audio-v002-import-{stamp}.json';rows=job['assets']
    receipt={'schema':'first-batch-dedicated-audio-import-receipt-v2','utc':datetime.now(timezone.utc).isoformat(),
        'manifest':str(MANIFEST),'manifest_sha256':MANIFEST_SHA256,'destination':PACKAGE,'expected_count':5,
        'actual_count':0,'saved_count':0,'success':False,'assets':rows,'source_validation':job['summary'],
        'unreal_import_run':True,'auditioned':False,'runtime_bound':False,'final_mix_accepted':False,
        'old17_replaced':False,'old17_unchanged':False,'timing_authority_changed':False}
    try:
        require_unused(DESTINATION)
        registry=list(unreal.EditorAssetLibrary.list_assets(PACKAGE,recursive=True,include_folder=False)) if unreal.EditorAssetLibrary.does_directory_exist(PACKAGE) else []
        require_exact_set(registry,[]);tasks=[]
        for row in rows:
            require(not unreal.EditorAssetLibrary.does_asset_exist(row['package_path']),'Existing destination asset')
            task=unreal.AssetImportTask()
            for key,value in [('filename',row['source']),('destination_path',PACKAGE),('destination_name',row['name']),('automated',True),
                              ('save',False),('replace_existing',False),('replace_existing_settings',False),('factory',unreal.SoundFactory())]:
                task.set_editor_property(key,value)
            tasks.append(task)
        unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks(tasks)
        for row,task in zip(rows,tasks):
            objects=list(task.get_editor_property('imported_object_paths'));require(objects==[row['object_path']],'Wrong actual imported objects')
            sound=unreal.load_asset(row['package_path']);require(isinstance(sound,unreal.SoundWave),'Not actual SoundWave')
            for key,value in [('looping',False),('volume',1.0),('pitch',1.0)]:
                sound.set_editor_property(key,value);require(sound.get_editor_property(key)==value,'Wrong actual sound defaults')
            duration=sound.get_editor_property('duration');channels=sound.get_editor_property('num_channels')
            imported_rate=sound.get_editor_property('imported_sample_rate');asset_rate=sound.get_editor_property('sample_rate')
            require(channels==1 and imported_rate==48000,'Wrong actual imported PCM format')
            require(finite(duration) and abs(duration-row['source_metrics']['duration_s'])<=1.5/48000,'Wrong actual sound duration')
            row.update(actual_object_type=sound.get_class().get_name(),imported_object_paths=objects,actual_duration_s=duration,
                actual_channels=channels,actual_imported_sample_rate_hz=imported_rate,actual_asset_sample_rate_hz=asset_rate,looping=False,volume=1.0,pitch=1.0)
            receipt['actual_count']+=1
        for source,digest in {**job['hashes'],**job['old17']}.items():
            require(hashlib.sha256(Path(source).read_bytes()).hexdigest()==digest,'Source or old17 changed during import')
        for row in rows:
            sound=unreal.load_asset(row['package_path']);require(unreal.EditorAssetLibrary.save_loaded_asset(sound,False),'Actual sound save failed')
            disk=DESTINATION/(row['name']+'.uasset');require(disk.is_file() and disk.stat().st_size>0,'Save without actual uasset')
            require(sound.get_editor_property('looping') is False and sound.get_editor_property('volume')==1.0 and sound.get_editor_property('pitch')==1.0,'Saved defaults changed')
            require(sound.get_editor_property('num_channels')==1 and sound.get_editor_property('imported_sample_rate')==48000,'Saved source rate/channels changed')
            require(abs(sound.get_editor_property('duration')-row['source_metrics']['duration_s'])<=1.5/48000,'Saved duration changed')
            row.update(saved=True,saved_uasset=str(disk),saved_bytes=disk.stat().st_size);receipt['saved_count']+=1
        registry=list(unreal.EditorAssetLibrary.list_assets(PACKAGE,recursive=True,include_folder=False))
        require_exact_set(registry,[r['object_path'] for r in rows])
        files=[p for p in DESTINATION.rglob('*') if p.is_file()]
        require(len(files)==5 and {p.name for p in files}=={r['name']+'.uasset' for r in rows},'Saved exact set mismatch')
        for old,digest in job['old17'].items():require(hashlib.sha256(Path(old).read_bytes()).hexdigest()==digest,'Old17 bytes changed')
        olddir=ROOT/'UnrealGame/Content/Production/FirstBatch/v001/Audio'
        require_exact_set([str(p.resolve()) for p in olddir.rglob('*') if p.is_file()],list(job['old17']))
        receipt.update(registered_object_paths=registry,registry_exact_set_passed=True,old17_unchanged=True,old17_sha256=job['old17'])
        receipt['success']=receipt['actual_count']==receipt['saved_count']==5
    except Exception as error:
        receipt['error']=str(error);raise
    finally:
        path.parent.mkdir(parents=True,exist_ok=True)
        with path.open('x',encoding='utf-8') as stream:json.dump(receipt,stream,ensure_ascii=False,indent=2)
        unreal.log('Dedicated first-batch audio v002 receipt: '+str(path))


if __name__=='__main__':
    job=preflight()
    if '--validate-only' in sys.argv:print(json.dumps(job['summary'],ensure_ascii=False))
    else:import_in_unreal(job)
