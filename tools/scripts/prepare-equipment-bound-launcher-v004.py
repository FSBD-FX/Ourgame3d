from pathlib import Path
import shutil,json,hashlib
R=Path('F:/Ourgame');T=R/'tools/scripts';O=R/'docs/production/first-batch-v2/evidence/leather-ready-v001/manual-launcher-before-v004';assert not O.exists();O.mkdir(parents=True)
cmd=R/'军剑真实装备绑定试玩.cmd';shutil.copy2(cmd,O/cmd.name)
s=(T/'verify-equipment-bound-current-build-v003.py').read_text(encoding='utf-8').replace("m['current_automation_succeeded']==148 and m['production_packages']==1085","m['current_automation_succeeded']==154 and m['production_packages']==1097").replace('2026-10-16_军剑真实换装绑定_v005-guardKernelGREEN','2026-10-17_军剑真实换装绑定_v006-guardCoinGREEN').replace('strict_actual_tests=148,production_packages=1085','strict_actual_tests=154,production_packages=1097')
p=T/'verify-equipment-bound-current-build-v004.py';assert not p.exists();p.write_text(s,encoding='utf-8')
s=(T/'launch-fairytale-equipment-bound-v003.ps1').read_text(encoding='utf-8-sig').replace('2026-10-16_StoneGuardKernel-full148GREEN-beforeNative-v122','2026-10-17_LeatherReady12-GuardCoin-full154GREEN-v124').replace('verify-equipment-bound-current-build-v003.py','verify-equipment-bound-current-build-v004.py')
p=T/'launch-fairytale-equipment-bound-v004.ps1';assert not p.exists();p.write_text(s,encoding='utf-8-sig')
b=cmd.read_bytes();assert b'launch-fairytale-equipment-bound-v003.ps1' in b;cmd.write_bytes(b.replace(b'launch-fairytale-equipment-bound-v003.ps1',b'launch-fairytale-equipment-bound-v004.ps1'))
(O/'change.json').write_text(json.dumps(dict(previous_cmd_preserved=True,new_launcher='tools/scripts/launch-fairytale-equipment-bound-v004.ps1',new_verifier='tools/scripts/verify-equipment-bound-current-build-v004.py',snapshot='v124',actual_tests=154,production_packages=1097,default_complete_preview_keeps_previous_attack_style=True,new_leather_ready_trial_is_separate=True,game_launched=False),indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(new_launcher=True,old_launcher_unchanged=True,command_updated=True)))
