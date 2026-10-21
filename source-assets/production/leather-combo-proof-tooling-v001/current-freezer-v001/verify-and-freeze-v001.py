"""Author verification/freeze only inside this NEW candidate folder. Never runs UE or actual freezer execute."""
from pathlib import Path
import importlib.util
import json
import subprocess
import sys
sys.dont_write_bytecode=True

HERE=Path(__file__).resolve().parent
ROOT=Path("F:/Ourgame").resolve()
PYTHON=ROOT/"tools/runtime/asset-gen/Scripts/python.exe"
spec=importlib.util.spec_from_file_location("current_freezer_author",HERE/"checkpoint_v126_common_v001.py")
C=importlib.util.module_from_spec(spec);spec.loader.exec_module(C)

def new(path,value):
    with path.open("x",encoding="utf-8",newline="\n") as stream:stream.write(value if isinstance(value,str) else json.dumps(value,ensure_ascii=False,indent=2)+"\n")

python_files=sorted(HERE.glob("*.py"))
for candidate in python_files:compile(candidate.read_text(encoding="utf-8-sig"),str(candidate),"exec")
unit=subprocess.run([str(PYTHON),"-B","-X","utf8",str(HERE/"test_current_freezer_v126_v001.py")],capture_output=True,text=True,encoding="utf-8")
new(HERE/"unit-final-v002.log",unit.stdout+unit.stderr)
if unit.returncode:raise SystemExit("Synthetic gates failed; preserved log; not frozen")
negative=subprocess.run([str(PYTHON),"-B","-X","utf8",str(HERE/"prepare-current-build-v126-v001.py"),"--project",str(ROOT),"--input",(HERE/"preparation-input-TEMPLATE-v001.json").relative_to(ROOT).as_posix()],capture_output=True,text=True,encoding="utf-8")
assert negative.returncode==1 and "Root-filled concrete preparation input required" in negative.stderr
new(HERE/"template-rejected-readonly-v001.log",negative.stdout+negative.stderr)
template=C.read(HERE/"preparation-input-TEMPLATE-v001.json")
historical_checks=0;assembly_members_checked=0
for clip in ("Ready","Primary1"):
    assembly_pin=C.native_pin(ROOT,template["assemblies"][clip]);rows,members=C.assembly_closure(ROOT,assembly_pin);assembly_members_checked+=len(rows)
    receipt=C.read(C.path(ROOT,C.native_pin(ROOT,template["imports"][clip])["path"]));assets=C.import_values(receipt,clip)
    manifest_path=Path(receipt["manifest"]).resolve();assert C.desc(ROOT,manifest_path)["sha256"]==receipt["manifest_sha256"]
    approved=C.read(manifest_path);slots={item["object_path"]:item for item in approved["assets"]}
    for asset in assets.values():
        source=Path(asset["source"]).resolve();assert source.relative_to(ROOT).as_posix() in members
        expected=slots[asset["object_path"]]
        for field in ("component","frame","name","package_path","object_path","source_bytes","source_sha256"):assert expected[field]==asset[field]
        historical_checks+=1
new(HERE/"author-verification-v001.json",{"python_syntax_files":len(python_files),"synthetic_unit_methods":6,
    "template_default_readonly_rejected":True,"historical_actual_Ready_P1_import_slots_checked":historical_checks,
    "historical_assembly_members_size_SHA_checked":assembly_members_checked,"current161_GREEN_not_claimed":True,
    "actual_preparation_execute_run":False,"actual_snapshot_execute_run":False,"UE_UBT_import_media_run":False,"formal_complete_units":0})
input_paths=[ROOT/"tools/scripts/freeze-current-build-v125-v001.py",ROOT/"tools/scripts/checkpoint_v125_common_v001.py",
    ROOT/template["base_manifest"]["path"],HERE.parent/"tooling-freeze-v001.json",HERE.parent/"combo-proof-contract-template-v001.json"]
for clip in ("Ready","Primary1"):input_paths.extend((C.path(ROOT,C.native_pin(ROOT,template["imports"][clip])["path"]),C.path(ROOT,C.native_pin(ROOT,template["assemblies"][clip])["path"])))
public=[HERE/name for name in ("prepare-current-build-v126-v001.py","freeze-current-build-v126-v001.py","checkpoint_v126_common_v001.py")]
files=sorted(candidate for candidate in HERE.iterdir() if candidate.is_file())
freeze={"schema":"leather-combo-current-freezer-candidate-freeze-v001","public_tools":[C.desc(ROOT,candidate) for candidate in public],
    "files":[C.desc(ROOT,candidate) for candidate in files],"inputs":[C.desc(ROOT,candidate) for candidate in input_paths],
    "verification":{"python_syntax_files":len(python_files),"synthetic_unit_methods":6,"template_rejected_readonly":True,
        "historical_actual_import_slots":historical_checks,"historical_assembly_members":assembly_members_checked},
    "contract":{"default_execution":"read_only_plan","new_snapshot_name":"v126-combo-161G","current_test_count":"Explicit complete unique161 or later Root set; full strictGREEN; old157 retained",
        "production":"Historical old1115 unchanged + actual two18 P2/P3 receipts =1151",
        "build_coverage":"All changed CPP and transitive project-local quoted header/inl consumers; explicit chronological exit0 receipts + actual post-write Compile + DLL Link",
        "publication":"Current/frozen endpoint hashes and repeated full gates; pending manifest renamed only after successful validation; failed partial copies retained",
        "no_hash_cycle":"Existing inputs -> runtime contract -> request -> future snapshot manifest"},
    "actual_source_or_tools_admitted":False,"actual_UE_UBT_run":False,"actual_snapshot_created":False,"native_manual_proofs_pending":True,"formal_complete_units":0}
new(HERE/"tooling-freeze-v001.json",freeze)
for row in freeze["files"]+freeze["inputs"]:C.match(ROOT,row)
print(json.dumps({"freeze":C.desc(ROOT,HERE/"tooling-freeze-v001.json"),"public_tools":freeze["public_tools"],
    "syntax_files":len(python_files),"synthetic_methods_passed":6,"candidate_and_input_pin_mismatches":0,
    "actual_current161_or_snapshot_claimed":False},indent=2))
