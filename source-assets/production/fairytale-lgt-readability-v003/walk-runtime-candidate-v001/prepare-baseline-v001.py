"""Copy only into this new candidate; never writes ActualSource or old freezes."""
from pathlib import Path
import hashlib,json
ROOT=Path("F:/Ourgame")
HERE=Path(__file__).resolve().parent
SNAPSHOT=ROOT/"source-assets/production/backups/v126-combo-161G/compiled-source-manifest.json"
manifest=json.loads(SNAPSHOT.read_text(encoding="utf-8-sig"));pins={row["path"]:row for row in manifest["files"]}
assert manifest["current_automation_succeeded"]==161 and manifest["production_packages"]==1151 and manifest["mismatches"]==0
names=("DungeonFighter.h","DungeonFighter.cpp","DungeonGameMode.cpp","DungeonHUD.h","DungeonHUD.cpp","DungeonFairytaleSwordPresentation.cpp","DungeonFairytaleSwordDrawState.h")
rows=[]
for name in names:
    key="UnrealGame/Source/CodexDungeon/"+name;data=(ROOT/key).read_bytes();row=pins[key]
    assert len(data)==row["bytes"] and hashlib.sha256(data).hexdigest()==row["sha256"],"Current Source is no longer exact full161 checkpoint: "+name
    destination=HERE/"baseline-source"/name;destination.parent.mkdir(parents=True,exist_ok=True)
    with destination.open("xb") as stream:stream.write(data)
    rows.append(row)
value={"schema":"fairytale-ground-walk-runtime-baseline-v001","base_snapshot_manifest":{"path":SNAPSHOT.relative_to(ROOT).as_posix(),"bytes":SNAPSHOT.stat().st_size,"sha256":hashlib.sha256(SNAPSHOT.read_bytes()).hexdigest()},
    "actual_Source_matches_current_full161":True,"actual_source_files":rows,"actual_source_mutated":False,"formal_complete_units":0}
with (HERE/"baseline-pins-v001.json").open("x",encoding="utf-8") as stream:json.dump(value,stream,ensure_ascii=False,indent=2);stream.write("\n")
