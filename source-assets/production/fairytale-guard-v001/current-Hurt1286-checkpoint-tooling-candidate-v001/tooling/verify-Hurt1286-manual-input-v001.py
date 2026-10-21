"""Actual compiled source/profile/import readiness only; no native gameplay proof."""
import argparse,runpy
from checkpoint_common_v001 import *
def verify(p):
 own=own_freeze();m=read(p);need(m['schema']=='Hurt1286-Root-manual-input-v001' and m['RootApproved'] is True and m['is_template'] is False,'NEW real Root manual input required')
 need(check(m['checkpoint_tooling_freeze_pin'])==own,'Manual input uses another candidate')
 q=read(check(m['checkpoint_root_request_pin']));need(q['RootApproved'] is True and q['is_template'] is False,'Actual Root request approval missing')
 snapshot=resolve(m['snapshot_directory']);manifest=check(m['snapshot_manifest_pin']);need(manifest==snapshot/'compiled-source-manifest.json','Manual snapshot path differs')
 profile=check(m['source_profile_prereg_pin']);approval=check(m['production_extension_approval_pin']);checker=check(m['profile_source_checker_pin'])
 need(checker==EXT/'verify-known44-profile-extension-v004.py','Only exact approved extension checker supported')
 cp=read(profile);need(check(cp['production_extension_pin'])==approval,'Source profile and extension approval differ')
 actual,facts,protocol=runpy.run_path(str(checker))['source_check'](snapshot,profile);strict_suite(read(resolve(actual['full_suite']['path'])))
 files={x['path']:x for x in actual['files']};needed={x['path']:x for x in m['admitted_Hurt_source_files']};need(set(needed)==set(HURT_SOURCES),'Exact Hurt source interface omitted')
 for n,x in needed.items():need(files[n]==x,'Compiled Hurt source differs');check(x)
 for k in ['strict_registered_tests','source_files','production_files']:need(type(m[k]) is int and m[k]==actual[k],'Actual dynamic checkpoint count differs: '+k)
 need(m['strict_registered_tests']==187 and m['production_files']==1286 and m['Hurt_flag']==HURT_FLAG and m['Guard_known_unique']==44 and m['Hurt_imported_textures']==32,'Manual scope differs')
 need(not m['automatic_inputs'] and not m['diagnostic_damage'] and not m['new_native_capture_claimed'] and m['FinalAccepted'] is False,'Source readiness must not fabricate native/final acceptance')
 dll=R/'UnrealGame/Binaries/Win64/UnrealEditor-CodexDungeon.dll';sources=[resolve(n) for n in files if n.startswith('UnrealGame/Source/')];need(dll.stat().st_mtime>=max(p.stat().st_mtime for p in sources),'Current DLL is older than current Source')
 return dict(compiled_inputs_verified=True,strict_registry=187,source_files=actual['source_files'],production_files=1286,Guard_known_unique=44,Hurt_imported_textures=32,Hurt_flag=HURT_FLAG,automatic_inputs=False,diagnostic_damage=False,native_or_visual_acceptance=False,UE_started=False)
def main():
 p=argparse.ArgumentParser();p.add_argument('--manual-input',required=True);a=p.parse_args();print(json.dumps(verify(resolve(a.manual_input))))
if __name__=='__main__':main()
