"""Independent original native viewport and finite-room diagnostic audit."""
from pathlib import Path
import argparse, hashlib, json, math, zlib
import numpy as np
from PIL import Image

def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def need(v, why):
    if not v: raise ValueError(why)
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def verify(archive):
    original=archive/'原件';report=read(original/'runtime-report.json')
    need(report['schema']=='guard-room-native-flow-diagnostic-v001','Wrong native report schema')
    need(report['passed'] and report['flow_complete'],'Actual native behavior RED retained')
    need(report['normal_J_full_clear'] is False and report['diagnostic_public_damage_used'] is True,'Diagnostic scope must remain explicit')
    need(report['silent_video'] and report['audio_recorded'] is False and report['game_tick_called_manually'] is False,'Silent/ordinary native contract')
    need(report['normal_J_accepted_attack_count']>0 and report['normal_J_native_hit_receipts']>0 and report['normal_J_actual_knight_HP_loss']>0 and report['native_Shift_dodge_observed'],'Real J HP loss/native receipt and Shift absent')
    need(1<=len(report['diagnostic_public_hits'])<=3 and all(x['api']=='ADungeonFighter::ApplyCombatHit' and x['dead'] and x['before_HP']>x['after_HP']==0 for x in report['diagnostic_public_hits']),'Diagnostic advancement facts differ')
    keys={x['key'] for x in report['normal_input_requests'] if x['down']}
    need({'Enter','E','J','LeftShift'}<=keys and bool(keys&{'A','D'}),'Actual controller inputs missing')
    metadata=read(original/'native-lossless-capture.json')
    need(metadata['mode']=='native_viewport_BGRA8_lossless_PNG_zlib0' and all(metadata[k] is False for k in ['pixel_mutations','simulation_pacing_changed','audio_changed']),'Native capture changed pixels/pacing/audio')
    rows=[json.loads(x) for x in (original/'native-frame-pixels.jsonl').read_text(encoding='utf-8-sig').splitlines() if x]
    names=[x['file'] for x in rows];actual={p.name for p in original.glob('MovieFrame*.png')}|{'prewarm-viewport.png'}
    need(len(names)==len(set(names)) and set(names)==actual,'Each original PNG needs exactly one native receipt')
    for r in rows:
        need(r['saved'] and Path(r['file']).name==r['file'],'Unsafe/missing saved native PNG')
        with Image.open(original/r['file']) as im:
            need(im.format=='PNG' and im.size==(r['width'],r['height'])==(1280,720),'Native viewport dimensions')
            rgba=np.asarray(im.convert('RGBA'));need(np.all(rgba[:,:,3]==255),'Native viewport alpha changed')
            need(zlib.crc32(rgba[:,:,[2,1,0,3]].tobytes())&0xffffffff==r['native_BGRA8_crc32'],'Native viewport CRC differs: '+r['file'])
    summary=read(original/'native-async-write-summary.json');movie=[r for r in rows if r['file'].startswith('MovieFrame')];n=len(movie)
    need(metadata['async_movie_writer_requested'] and metadata['async_movie_writer_active'] and metadata['prewarm_synchronous'],'Existing async writer required')
    need(all(summary[k] is True for k in ['requested','active','closed','flushed','success']) and all(summary[k]==n for k in ['movie_reserved','movie_enqueued','movie_saved','movie_completed','receipts_saved']) and all(summary[k]==0 for k in ['movie_reservation_failed','movie_failed','rejected','pending']),'Native async writer did not completely flush')
    need([r['writer_sequence'] for r in movie]==list(range(1,n+1)) and [r['file'] for r in movie]==sorted(r['file'] for r in movie),'Native FIFO reordered frames')
    t=report['capture_timing'];offsets=t['frame_wall_offsets_s'];obs=report['observations']
    need(t['use_fixed_time_step'] is False and report['native_async_capture_writes_flushed'] and report['capture_stop_before_flush'] and summary['flush_completed_monotonic_s']>=t['capture_stop_monotonic_s'],'Native stop/ordinary pacing/flush contract')
    need(n==len(offsets)==len(obs) and n>2 and all(math.isfinite(x) for x in offsets) and all(b>a for a,b in zip(offsets,offsets[1:])),'Actual capture-event timing lost')
    for r,offset in zip(movie,offsets):
        need(r['async_writer'] and r['copy_crc_matches'] and r['filename_reserved'] and r['filename_reservation_mode']=='Windows_CreateFileW_CREATE_NEW' and r['copied_BGRA8_crc32']==r['native_BGRA8_crc32'],'Native copied/reserved frame changed')
        need(0<r['capture_callback_monotonic_s']<=r['reservation_completed_monotonic_s']<=r['enqueued_monotonic_s']<=r['save_started_monotonic_s']<=r['save_completed_monotonic_s'],'Native queue times reordered')
        need(r['capture_callback_monotonic_s']<=t['capture_start_monotonic_s']+offset+1e-6,'Write completion replaced actual capture time')
    need(all(not x['interface_visible'] and x['text_calls']==0 for x in obs),'Traditional HUD/text rendered')
    need(any(x['LGT_drawn'] and x['hero_bound_skin'] and abs(x['hero_canvas_size']-72*512/416)<1e-9 for x in obs),'Committed actual LGT/hero72 native renderer absent')
    warnings={};births={}
    for i in [1,2]:
        warned=[x for x in obs if len(x.get('slots',[]))==3 and int(x['slots'][i]['stage'])==1 and x['slots'][i]['slot'] in x['rendered_warning_slots']]
        need(len(warned)>=2,'No actual rendered world warning for slot '+str(i))
        need(all(int(x['slots'][i]['entity'])==0 and x['slots'][i]['materialized_at']==-1 and x['slots'][i]['visibility']>.05 for x in warned),'Warning already owns hidden actor/materialization')
        born=[x for x in obs if len(x.get('slots',[]))==3 and int(x['slots'][i]['stage'])==2]
        need(bool(born),'No native materialized actor for slot '+str(i));slot=born[0]['slots'][i]
        need(slot['materialized_at']>=slot['warning_at']+1.2 and slot['warning_at']>=born[0]['slots'][i-1]['dead_at']+2.,'Breather/full1.2 warning skipped')
        actors=[a for x in born for a in x['enemies'] if a['entity']==slot['entity'] and not a['dead'] and a['actual_draw_recorded']]
        need(len(actors)>=2 and all(a['native_driver']==('StoneBat' if i==1 else 'StoneGuard') and a['initial_time']==slot['materialized_at'] for a in actors),'Birth lacks native identity/visible viewport actor')
        warnings[str(i)]=len(warned);births[str(i)]={'entity':slot['entity'],'warning_at':slot['warning_at'],'materialized_at':slot['materialized_at'],'visible_frames':len(actors)}
    final=obs[-1];need(final['phase']=='complete' and final['wallet']==40 and final['death_count']==3 and final['coin_objects']==3 and final['collections']==3 and final['room_cleared'],'Final physical coin/once-only clear continuity failed')
    need([x['amount'] for x in final['coins']]==[7,4,9] and all(x['consumed'] for x in final['coins']),'Whole finite manifest7/4/9 physical coins differ')
    files={x['file']:x for x in report['codec_files']};required={'entered-root-v2-codec.json','bat-warning-root-v2-codec.json','guard-warning-root-v2-codec.json','guard-settled-root-v2-codec.json','after-pickup-root-v2-codec.json','installed-root-v2-codec.json'}
    need(set(files)==required,'Six actual Codec boundary files missing/duplicated')
    for name,r in files.items():need((original/name).stat().st_size==r['bytes'] and sha(original/name)==r['sha256'] and r['root_schema']==2 and r['reward_schema']==2,'Actual RootV2 Codec evidence differs')
    need((original/'after-pickup-root-v2-codec.json').read_bytes()==(original/'installed-root-v2-codec.json').read_bytes(),'Grouped install changed whole saved Codec')
    need(any(x['inner_owner_schema']==2 and x['reported'] and x['claimed'] for x in files['guard-settled-root-v2-codec.json']['guard_owners']),'Settled Guard Owner2 not captured')
    return dict(passed=True,scope='Actual native room flow diagnostic; public damage advances enemies after real J/Shift. Same-process RootV2 grouped restore only. Pixel equality is technical evidence, not visual acceptance.',native_frames=n,every_source_viewport_pixel_crc_matches=True,warning_rendered_frames=warnings,births=births,final_wallet=40,preallocated_coins=[7,4,9],normal_J_full_clear=False,two_process_disk_proof=False,audio_recorded=False,visual_reviewed=False)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--archive',required=True);p.add_argument('--write-receipt',action='store_true');a=p.parse_args();archive=Path(a.archive).resolve();result=verify(archive)
    if a.write_receipt:
        dest=archive/'原件/independent-room-native-proof-v001.json';need(not dest.exists(),'Never overwrite receipt');dest.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False))
