"""Author-only non-executable Root templates; actual process PID/exit receipt must come from Root."""
from pathlib import Path
import importlib.util
import json

HERE=Path(__file__).resolve().parent
ROOT=Path("F:/Ourgame").resolve()
spec=importlib.util.spec_from_file_location("template_common",HERE/"checkpoint_v126_common_v002.py")
C=importlib.util.module_from_spec(spec);spec.loader.exec_module(C)
def new(name,value):
    with (HERE/name).open("x",encoding="utf-8",newline="\n") as stream:json.dump(value,stream,ensure_ascii=False,indent=2);stream.write("\n")

draft=C.read(HERE.parent/"current-freezer-v001/preparation-input-TEMPLATE-v001.json")
draft["schema"]="checkpoint-v126-preparation-input-v002"
draft["output_input_directory"]="source-assets/production/checkpoint-v126-root-input-v002"
draft["joint_import_proof"]=None
for clip,name in (("Primary2","leather-primary2-combo-v001-import-20261016-194453-924659.json"),("Primary3","leather-primary3-combo-v001-import-20261016-194456-196483.json")):
    receipt_path=ROOT/"UnrealGame/Saved/Bootstrap"/name
    draft["imports"][clip]=C.desc(ROOT,receipt_path)
    draft["assemblies"][clip]=C.native_pin(ROOT,C.read(receipt_path)["assembly_freeze"])
draft["additional_files"].append(C.desc(ROOT,HERE.parent/"current-freezer-v001/tooling-freeze-v001.json"))
draft["fill_instructions"]=[
    "Copy to NEW Root input; keep this frozen template immutable. Set template_only=false only after actual final production build/full161 GREEN pins are supplied.",
    "All Source/Config delta, transitive header/inl consumers, exit0 linked build_history and strict full test registry gates stay identical to current-freezer-v001.",
    "joint_import_proof must pin a NEW Root external proof following joint-import-proof-TEMPLATE-v001.json; do not edit either actual native18 receipt.",
    "The reviewed joint importer uses one fixed old1115 inventory in one UE invocation; both real receipts legally record1115, and final disk must be exact old1115 plus actual18+18=1151.",
    "Root supplies real process PID/exit0, exact single UE log, importer/decoder/import-contract pins, both receipt pins and final36 inventory proving P2 saved hashes unchanged after P3.",
    "Root final36 inventory files must exactly equal both actual receipts' saved_uasset/bytes/SHA and actual current Production delta. No timestamp/filename inference can substitute for hash equality.",
    "Add this current-freezer-v002 tooling freeze, other new Ready/P1/default tools and preserved production/admission evidence pins to additional_files. The v002 preparer automatically pins its own executing file/common.",
    "No actual --execute preparation or snapshot is permitted before full current161 clean GREEN. Default is read-only; failures preserve new partial directories without publishing a manifest."
]
new("preparation-input-TEMPLATE-v002.json",draft)
joint={"schema":"root-leather-combo-joint-import-proof-v001","template_only":True,"mode":"single_process_two18_fixed_old1115","same_process":True,
    "importer":C.desc(ROOT,ROOT/"tools/scripts/ue-import-leather-combo-v001.py"),
    "decoder":C.desc(ROOT,ROOT/"tools/scripts/ue-import-armor-primary2-four-v001.py"),
    "import_contract":C.desc(ROOT,ROOT/"source-assets/production/fairytale-lgt-readability-v003/combo-import-v001/root-import-contract-v001.json"),
    "process":{"pid":None,"exit_code":None,"log":C.desc(ROOT,ROOT/"UnrealGame/Saved/Bootstrap/leather-combo-v001-import-20261017-034431-5778279.log")},
    "receipts":{clip:draft["imports"][clip] for clip in ("Primary2","Primary3")},"old_packages_unchanged":1115,
    "p2_saved_hashes_unchanged_after_p3":True,"final36_inventory":None,
    "fill_instructions":["Root creates a NEW external record with real launch/wait process PID and exit0; the importer does not put PID/exit0 in the native receipts.",
        "The pinned single UE log independently corroborates importer invocation, exactly two ordered receipt paths and clean Python/engine shutdown, but cannot independently recover an OS process PID.",
        "Fill/pin a NEW actual final36 inventory from current package bytes; retain all original native receipts unmodified; set template_only=false after real evidence is bound."]}
new("joint-import-proof-TEMPLATE-v001.json",joint)
new("joint-final36-inventory-TEMPLATE-v001.json",{"schema":"root-leather-combo-final36-inventory-v001","template_only":True,
    "production_packages":1151,"old_packages_unchanged":1115,"new_packages":36,"p2_saved_hashes_unchanged_after_p3":True,
    "mismatches":None,"files":[],"fill_instructions":["Root writes a NEW inventory; do not change actual native receipts.",
        "Read all36 actual new package bytes, compare to both receipts saved_bytes/saved_sha256; current fullProduction must exactly equal historical old1115 plus these36.",
        "Only real zero mismatches permits mismatches=0/template_only=false. This is package-integrity evidence, not art/runtime/audio/full-unit acceptance."]})
