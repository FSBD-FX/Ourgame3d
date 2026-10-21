from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
R=Path('F:/Ourgame');old=R/'tools/scripts/prepare-hero-bridge258-extraction-review-v001.py';new=R/'tools/scripts/prepare-hero-bridge258-extraction-review-v002.py'
text=old.read_text(encoding='utf-8')
changes={"assert len(f['members'])==17":"assert len(f['members'])==7 and len(f['source_dependencies'])==10", "for row in f['members']:":"for row in f['members']+f['source_dependencies']:","member_count=17,verification_passes=2":"member_count=len(f['members']),source_dependency_count=len(f['source_dependencies']),verification_passes=2"}
for before,after in changes.items():assert text.count(before)==1;text=text.replace(before,after)
assert not new.exists()
with new.open('x',encoding='utf-8') as f:f.write(text)
O=R/'docs/production/first-batch-v2/evidence/HeroAirDiskRestore-v144-v001/Root-extraction-member-dependency-count-repair-v001';O.mkdir()
with (O/'failure-and-repair.json').open('x',encoding='utf-8') as f:json.dump(dict(utc=datetime.now(timezone.utc).isoformat(),failed_script=old.as_posix(),failed_script_sha256=hashlib.sha256(old.read_bytes()).hexdigest(),failure='Root archival draft mistook17totalpins for17freeze members; actual schema is7members+10source_dependencies. Archive never created, subsequentretention rejected missingleaf beforeEwrite.',new_script=new.as_posix(),change='Check exact7+10 schema and verify both arrays/twoSHA; copy all candidatefiles unchanged. No waiver ofactualsourceevidence.',old_script_preserved=True,raw_and_derived_pixels_modified=False,E637_created_by_failed_attempt=False),f,ensure_ascii=False,indent=2)
print(new.as_posix())
