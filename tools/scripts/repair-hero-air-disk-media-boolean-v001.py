from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
R=Path('F:/Ourgame')
old=R/'tools/scripts/prepare-hero-air-disk-native-media-v001.py'
new=R/'tools/scripts/prepare-hero-air-disk-native-media-v002.py'
text=old.read_text(encoding='utf-8');needle="o['completed_callback']==i"
assert text.count(needle)==1 and not new.exists()
with new.open('x',encoding='utf-8') as f:f.write(text.replace(needle,"o['completed_callback'] is True"))
O=R/'docs/production/first-batch-v2/evidence/HeroAirDiskRestore-v144-v001/Root-media-completed-boolean-repair-v001'
O.mkdir()
receipt=dict(utc=datetime.now(timezone.utc).isoformat(),failed_script=old.as_posix(),failed_script_sha256=hashlib.sha256(old.read_bytes()).hexdigest(),failure='Root media draft treated completed_callback boolean as numeric callback index; actual reports use true and list order/filename/wall offset bind index.',old_script_preserved=True,new_script=new.as_posix(),change='Require completed_callback is True; exact ordered offsets/filename/strict wall/native proof gates unchanged.',shell_prepare_failure_preserved='Initial inline shell preparation hit SyntaxError unexpected EOF due PowerShell quoting; subsequent v002 launch file absent. No output/media or actual native changed. Replaced with saved script.',native_rerun=False,native_outputs_modified=False)
with (O/'failure-and-repair.json').open('x',encoding='utf-8') as f:json.dump(receipt,f,ensure_ascii=False,indent=2)
print(new.as_posix())
