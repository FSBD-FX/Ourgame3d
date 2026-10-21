"""Authoring helper: creates only this new candidate's non-executable contract template."""
from pathlib import Path
import hashlib
import json

HERE=Path(__file__).resolve().parent
ROOT=Path("F:/Ourgame")
def read(path):return json.loads(path.read_text(encoding="utf-8-sig"))
def pin(path):
    data=path.read_bytes();return {"path":path.relative_to(ROOT).as_posix(),"bytes":len(data),"sha256":hashlib.sha256(data).hexdigest()}
base_path=ROOT/"source-assets/production/backups/v125-p1-157G/compiled-source-manifest.json"
base=read(base_path)
assert base["production_packages"]==1115 and base["current_automation_succeeded"]==157
ready_assembly=next(row for row in base["files"] if row["path"].endswith("ready-integer-assembly-v001/assembly-freeze-v001.json"))
p1=read(ROOT/base["new_production_import_receipt"]["path"])
template={"schema":"leather-combo-runtime-proof-contract-v001","template_only":True,
    "scope":"Ready/P1/P2/P3 matching leather, normal two-facing six-attack proof only",
    "base_snapshot_manifest":pin(base_path),
    "native_source_freeze":pin(ROOT/"source-assets/production/fairytale-lgt-readability-v003/leather-combo-source-v001/source-freeze-v001.json"),
    "production":{"baseline_count":1115,"new_packages":36,"expected_total":1151},
    "current_automation":{"report":None,"expected_count":None,"full_test_paths":[]},
    "additional_source_pins":[],
    "imports":{"Ready":base["ready_production_import_receipt"],"Primary1":base["new_production_import_receipt"],"Primary2":None,"Primary3":None},
    "assemblies":{"Ready":ready_assembly,"Primary1":p1["assembly_freeze"],"Primary2":None,"Primary3":None},
    "fill_instructions":["Root creates a NEW concrete contract after actual new imports/build/current full GREEN; keep this template frozen.",
        "Set template_only=false; current_automation.report exact pin, current expected_count>=157 and complete unique full_test_paths come from current report, never v125 count.",
        "List all non-five-combo Source/Config changes/new files relative to v125 in additional_source_pins. Guard work is explicitly allowed through exact pins.",
        "Primary2/Primary3 imports may be distinct18 receipts or the same combined36 receipt pin. Each referenced receipt assets must be exactly the union of its referenced namespaces.",
        "Bind all four assembly freezes and their original source files. Never guess an assembly path.",
        "New snapshot top combo_proof_contract is this concrete contract's exact pin; include the contract, every referenced pin, five native candidate files and all tools as files inputs.",
        "Current snapshot records all current Source/Config/DLL/Production, actual_expected_test_names, current_automation_report/current_automation_succeeded and production old/new counts.",
        "This template/source candidate is not proof of import, build, runtime, visual acceptance, audio or a complete unit."],
    "formal_complete_units":0}
out=HERE/"combo-proof-contract-template-v001.json"
with out.open("x",encoding="utf-8",newline="\n") as stream:json.dump(template,stream,ensure_ascii=False,indent=2);stream.write("\n")
