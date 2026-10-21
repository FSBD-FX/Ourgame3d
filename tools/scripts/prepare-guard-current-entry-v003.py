from pathlib import Path
import hashlib,json,shutil
R=Path('F:/Ourgame');O=R/'docs/production/first-batch-v2/evidence/stone-guard-kernel-v001/root-current-entry-v003'
assert not O.exists();O.mkdir(parents=True)
for name in ['verify-equipment-bound-current-build-v002.py','launch-fairytale-equipment-bound-v002.ps1']:
 p=R/'tools/scripts'/name;shutil.copy2(p,O/name)
 q=R/'tools/scripts'/name.replace('v002','v003');assert not q.exists();s=p.read_text(encoding='utf-8-sig')
 if p.suffix=='.py':
  s=s.replace('==144','==148').replace('strict_actual_tests=144','strict_actual_tests=148').replace('v004-pendingGREEN','v005-guardKernelGREEN')
 else:
  s=s.replace('2026-10-16_PendingGear-MeleeAudio-full144GREEN-beforeNative-v121','2026-10-16_StoneGuardKernel-full148GREEN-beforeNative-v122').replace('verify-equipment-bound-current-build-v002.py','verify-equipment-bound-current-build-v003.py')
 q.write_text(s,encoding='utf-8-sig' if p.suffix=='.ps1' else 'utf-8')
p=R/'军剑真实装备绑定试玩.cmd';shutil.copy2(p,O/p.name);b=p.read_bytes();assert b.count(b'launch-fairytale-equipment-bound-v002.ps1')==1
p.write_bytes(b.replace(b'launch-fairytale-equipment-bound-v002.ps1',b'launch-fairytale-equipment-bound-v003.ps1'))
(O/'entry-change.json').write_text(json.dumps(dict(before='v002 /144 /v121 /nativev004',after='v003 /148 /v122 /nativev005',old_files_preserved=True,manual_window_launched=False,guard_kernel_only=True,leather_reference_not_imported=True),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(current_entry='v003',manual_window_launched=False)))
