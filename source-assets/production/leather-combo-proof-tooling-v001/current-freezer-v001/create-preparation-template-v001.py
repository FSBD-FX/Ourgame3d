"""Author-only generation of a non-executable Root input template in this new candidate folder."""
from pathlib import Path
import hashlib
import json

HERE=Path(__file__).resolve().parent
ROOT=Path("F:/Ourgame")
def read(path):return json.loads(path.read_text(encoding="utf-8-sig"))
def pin(path):
    data=path.read_bytes();return {"path":path.relative_to(ROOT).as_posix(),"bytes":len(data),"sha256":hashlib.sha256(data).hexdigest()}
contract=read(HERE.parent/"combo-proof-contract-template-v001.json")
tooling=read(HERE.parent/"tooling-freeze-v001.json")
tools=[{**row,"path":"tools/scripts/"+Path(row["path"]).name} for row in tooling["public_tools"]]
tools.append(pin(ROOT/"tools/scripts/verify-native-bound-capture-pixels-v001.py"))
draft={"schema":"checkpoint-v126-preparation-input-v001","template_only":True,
    "snapshot_name":"v126-combo-161G","output_input_directory":"source-assets/production/checkpoint-v126-root-input-v001",
    "expected_test_count":161,"base_manifest":contract["base_snapshot_manifest"],"native_source_freeze":contract["native_source_freeze"],
    "production":contract["production"],"current_automation":{"report":None,"expected_count":161,"full_test_paths":[]},
    "source_deltas":[],"translation_units":[],"build_log":None,"last_build":None,"dll":None,"build_history":[],
    "new_import_order":["Primary2","Primary3"],"imports":contract["imports"],"assemblies":contract["assemblies"],
    "proof_tools":tools,"additional_files":[pin(HERE.parent/"tooling-freeze-v001.json")],
    "fill_instructions":[
        "Copy to a NEW Root-owned input file, fill real pins then set template_only=false; never mutate this frozen template.",
        "Only final actually compiled production + exact full161 strictGREEN report can pass. Current actual157 or Stage0 RED is not substituted.",
        "Use --inspect-source for a read-only UNAPPROVED current delta/include-consumer plan; Root must independently approve every source_deltas pin and full translation_units set.",
        "build_history contains preserved prior exit0 receipt/log pairs in chronological order. build_log/last_build are the final exit0 linked build and must not be duplicated in build_history.",
        "Fill actual Primary2/Primary3 two distinct18 receipts and all four exact assemblies. new_import_order must follow real sequential old-package counts1115 then1133.",
        "current_automation.report exact pin, expected_count and full_test_paths are the final actual full report with all old157 retained plus the approved new groups.",
        "proof_tools contains actual admitted combo3 + unchanged pixel verifier pins. Include other new Ready/P1/default tools, import/checker tools, production/admission evidence and this current-freezer tooling freeze in additional_files.",
        "All import manifests/reference pins, registration proof pins, four assembly freeze files closures and native source freeze files are traversed automatically; no future snapshot manifest pin is an input.",
        "Preparer/freezer default read-only. --execute writes NEW input directory/NEW short snapshot only, preserves failure and never runs UE/UBT/import/media or awards acceptance."
    ],"formal_complete_units":0}
with (HERE/"preparation-input-TEMPLATE-v001.json").open("x",encoding="utf-8",newline="\n") as stream:json.dump(draft,stream,ensure_ascii=False,indent=2);stream.write("\n")
