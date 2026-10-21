"""Read-only Source/Content checks; only optional NEW verification JSON is written."""
import argparse,sys
from pathlib import Path
from datetime import datetime,timezone
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent))
import K56_import_common_v001 as K

def main():
 p=argparse.ArgumentParser();p.add_argument('--manifest',required=True);p.add_argument('--manifest-sha',required=True);p.add_argument('--compiled-manifest',required=True);p.add_argument('--compiled-manifest-sha',required=True);p.add_argument('--receipt',required=True);p.add_argument('--host-proof',required=True);p.add_argument('--launch-receipt',required=True);p.add_argument('--exit-receipt',required=True);p.add_argument('--output');a=p.parse_args()
 m,c,rows=K.load_inputs(a.manifest,a.manifest_sha,a.compiled_manifest,a.compiled_manifest_sha,decode=True);r=K.read(a.receipt);h=K.read(a.host_proof);launch=K.read(a.launch_receipt);ex=K.read(a.exit_receipt)
 out=Path(a.receipt).resolve().parent
 K.need(all(Path(q).resolve().parent==out for q in (a.host_proof,a.launch_receipt,a.exit_receipt)),'All process evidence must share actual run directory')
 K.need(r['schema']=='Root-K56-actual-native-texture-import-v001' and r['success'] is True and r['actual_count']==56 and r['saved_count']==56 and len(r['assets'])==56,'Actual successful56 native receipt required')
 K.need(r['manifest']==K.pin(a.manifest) and r['source_contract']==m['source_contract'] and r['compiled_manifest']==K.pin(K.CM) and r['host_proof']==K.pin(a.host_proof),'Actual native input pins differ')
 K.need(r['tool_pins']==K.tool_pins() and h['tool_pins']==K.tool_pins(),'Frozen tool source differs')
 K.need(h['candidate_freeze']==r['candidate_freeze'],'Native tool freeze lineage differs');K.freeze_check(K.HERE/'candidate-freeze-v001.json',r['candidate_freeze']['sha256'])
 K.need(h['passed'] is True and h['UE_started'] is False and h['no_UE_UBT_processes']==[],'Prelaunch no-UE host proof missing')
 K.validate_exit(r['native_process_id'],launch,ex)
 K.need(launch['schema']=='Root-K56-native-import-launch-v001' and launch['manifest']==K.pin(a.manifest) and launch['host_proof']==K.pin(a.host_proof),'Launch input pins differ')
 argv=launch['arguments'];K.need(len(argv)==9 and Path(argv[0]).resolve()==K.ROOT/'UnrealGame/CodexDungeon.uproject' and argv[1:7]==['-unattended','-nosplash','-nop4','-NoLiveCoding','-AllowCommandletAudio','-run=pythonscript'],'Unapproved native argv')
 K.need(argv[7].startswith('-script=') and Path(argv[7][8:]).resolve()==out/'run-frozen-K56-import-v001.py' and argv[8].startswith('-abslog=') and Path(argv[8][8:]).resolve()==out/'native-UE-K56-import-v001.log','Wrong script/log location')
 K.checked(launch['native_wrapper']);K.checked(launch['native_arguments']);K.need(Path(launch['executable']).resolve()==Path('G:/UE_5.5/Engine/Binaries/Win64/UnrealEditor-Cmd.exe').resolve(),'Wrong native executable')
 K.need((out/'native-UE-K56-import-v001.log').is_file() and (out/'native-UE-K56-import-v001.log').stat().st_size>0,'Actual native log required')
 assets={(x['frame'],x['owner']):x for x in r['assets']};K.need(len(assets)==56,'Duplicate actual imported texture key');oldsettings=K.old_actual_settings()
 for row in rows:
  x=assets[row['frame'],row['owner']];line=x['manifest_source_lineage'];K.need(line=={'source_contract':m['source_contract'],'layer_key':str(row['frame'])+':'+row['owner'],'source':row['source'],'source_rgba_sha256':row['source_rgba_sha256'],'source_frame':row['source_frame'],'source_alias_frame':row['source_alias_frame']},'Actual manifest source lineage differs')
  K.need(x['actual_object_path']==row['object_path'] and x['actual_class']=='Texture2D' and x['actual_dimensions']==[512,512] and x['actual_settings']==oldsettings,'Actual saved Texture2D/class/dims/settings differ')
  K.need(len(x['actual_import_filenames'])==1 and Path(x['actual_import_filenames'][0]).resolve()==Path(row['source']['path']).resolve(),'Actual source filename differs')
  K.need(Path(x['saved']['path']).resolve()==K.saved_path(row).resolve(),'Wrong saved package path');K.checked(x['saved'])
 K.need(set(r['registry_added'])=={x['object_path'] for x in rows} and r['no_other_new_saved_or_registered_packages'] is True,'Extra material/package or incomplete registry delta')
 for _ in range(2):K.baseline(rows);K.check_content(h['all_Content_before'],rows)
 result={'schema':'Root-K56-readonly-actual-import-verification-v001','utc':datetime.now(timezone.utc).isoformat(),'verified':True,'actual_import':K.pin(a.receipt),'actual_launch':K.pin(a.launch_receipt),'actual_exit':K.pin(a.exit_receipt),'actual_log':K.pin(out/'native-UE-K56-import-v001.log'),'manifest':K.pin(a.manifest),'source_contract':m['source_contract'],'old1439_unchanged':True,'Source303_unchanged':True,'added56_exact':True,'actual_Production1495':True,'same_PID_exit0':True,'verification_passes':2,'twoSHA_mismatches':0,'saved_uasset_pins':[x['saved'] for x in r['assets']],'native_render_GPU_audio_verified':False,'FinalAccepted':False}
 print(K.write_new(a.output,result) if a.output else result)
if __name__=='__main__':main()
