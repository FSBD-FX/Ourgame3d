"""Syntax/synthetic and actual read-only package audit only; no preparation/snapshot execute."""
from pathlib import Path
import ast
import importlib.util
import json
import subprocess
import sys
sys.dont_write_bytecode=True

HERE=Path(__file__).resolve().parent
ROOT=Path("F:/Ourgame").resolve()
PYTHON=ROOT/"tools/runtime/asset-gen/Scripts/python.exe"
spec=importlib.util.spec_from_file_location("author_common_v002",HERE/"checkpoint_v126_common_v002.py")
C=importlib.util.module_from_spec(spec);spec.loader.exec_module(C)
def new(path,value):
    with path.open("x",encoding="utf-8",newline="\n") as stream:stream.write(value if isinstance(value,str) else json.dumps(value,ensure_ascii=False,indent=2)+"\n")

files=sorted(HERE.glob("*.py"))
for candidate in files:compile(candidate.read_text(encoding="utf-8-sig"),str(candidate),"exec")
unit=subprocess.run([str(PYTHON),"-B","-X","utf8",str(HERE/"test_current_freezer_v126_v002.py")],capture_output=True,text=True,encoding="utf-8")
new(HERE/"unit-final-v001.log",unit.stdout+unit.stderr)
if unit.returncode:raise SystemExit("Synthetic failures preserved; no freeze")
negative=subprocess.run([str(PYTHON),"-B","-X","utf8",str(HERE/"prepare-current-build-v126-v002.py"),"--project",str(ROOT),"--input",(HERE/"preparation-input-TEMPLATE-v002.json").relative_to(ROOT).as_posix()],capture_output=True,text=True,encoding="utf-8")
new(HERE/"template-rejected-readonly-v001.log",negative.stdout+negative.stderr)
assert negative.returncode==1 and "Root-filled concrete preparation input required" in negative.stderr
old_common=HERE.parent/"current-freezer-v001/checkpoint_v126_common_v001.py"
def functions(candidate):return {node.name:ast.dump(node,include_attributes=False) for node in ast.parse(candidate.read_text(encoding="utf-8")).body if isinstance(node,ast.FunctionDef)}
old_functions,new_functions=functions(old_common),functions(HERE/"checkpoint_v126_common_v002.py")
unchanged=("inventory","source_changes","affected_translation_units","check_translation_units","strict_automation","validate_build_history","assembly_closure","import_values","copy_new_snapshot")
assert all(old_functions[name]==new_functions[name] for name in unchanged)
old_freeze=C.read(HERE.parent/"current-freezer-v001/tooling-freeze-v001.json")
for row in old_freeze["files"]+old_freeze["inputs"]:C.match(ROOT,row)
draft=C.read(HERE/"preparation-input-TEMPLATE-v002.json");base=C.read(C.path(ROOT,draft["base_manifest"]["path"]))
old_prod={row["path"]:row for row in base["files"] if row["path"].startswith("UnrealGame/Content/Production/")}
prod={}
for candidate in (ROOT/"UnrealGame/Content/Production").rglob("*"):
    if candidate.is_file():row=C.desc(ROOT,candidate);prod[row["path"]]=row
assert len(old_prod)==1115 and all(prod.get(key)==row for key,row in old_prod.items())
new_prod={}
for clip in ("Primary2","Primary3"):
    receipt=C.read(C.path(ROOT,draft["imports"][clip]["path"]));assets=C.import_values(receipt,clip,1115)
    assembly_pin=C.native_pin(ROOT,draft["assemblies"][clip]);members,member_paths=C.assembly_closure(ROOT,assembly_pin)
    for key,asset in assets.items():
        expected={"path":key,"bytes":asset["saved_bytes"],"sha256":asset["saved_sha256"]}
        assert prod[key]==expected;new_prod[key]=expected
        source=Path(asset["source"]).resolve();assert source.relative_to(ROOT).as_posix() in member_paths
        C.match(ROOT,{"path":source.relative_to(ROOT).as_posix(),"bytes":asset["source_bytes"],"sha256":asset["source_sha256"]})
assert len(new_prod)==36 and len(prod)==1151 and prod=={**old_prod,**new_prod}
joint_template=C.read(HERE/"joint-import-proof-TEMPLATE-v001.json")
log_path=C.path(ROOT,joint_template["process"]["log"]["path"])
C.joint_log_values(log_path.read_text(encoding="utf-8-sig"),C.path(ROOT,joint_template["importer"]["path"]),[C.path(ROOT,draft["imports"][clip]["path"]) for clip in ("Primary2","Primary3")])
new(HERE/"actual-readonly-joint-package-audit-v001.json",{"schema":"candidate-read-only-joint-package-audit-v001",
    "Root_process_PID_exit0_not_claimed":True,"Root_joint_proof_not_created":True,"current_full161_not_claimed":True,
    "actual_original_receipts":[draft["imports"][clip] for clip in ("Primary2","Primary3")],
    "actual_old_packages_unchanged":1115,"actual_new_saved_hashes_matched":36,"actual_current_production_packages":1151,
    "actual_P2_saved_hashes_unchanged_after_P3":True,"original_source_and_assembly_membership_checked":36,
    "single_UE_log_two_ordered_receipts_checked":True,"mismatches":0,"new_package_files":[new_prod[key] for key in sorted(new_prod)],
    "native_art_or_motion_accepted":False,"formal_complete_units":0})
input_paths=[HERE.parent/"current-freezer-v001/tooling-freeze-v001.json",old_common,
    HERE.parent/"current-freezer-v001/prepare-current-build-v126-v001.py",HERE.parent/"current-freezer-v001/freeze-current-build-v126-v001.py",
    HERE.parent/"tooling-freeze-v001.json",C.path(ROOT,draft["base_manifest"]["path"]),log_path]
for key in ("importer","decoder","import_contract"):input_paths.append(C.path(ROOT,joint_template[key]["path"]))
for clip in ("Primary2","Primary3"):input_paths.append(C.path(ROOT,draft["imports"][clip]["path"]))
public=[HERE/name for name in ("prepare-current-build-v126-v002.py","freeze-current-build-v126-v002.py","checkpoint_v126_common_v002.py")]
all_files=sorted(candidate for candidate in HERE.iterdir() if candidate.is_file())
freeze={"schema":"leather-combo-current-freezer-candidate-freeze-v002","public_tools":[C.desc(ROOT,candidate) for candidate in public],
    "files":[C.desc(ROOT,candidate) for candidate in all_files],"inputs":[C.desc(ROOT,candidate) for candidate in input_paths],
    "verification":{"python_syntax_files":len(files),"synthetic_methods":8,"unchanged_core_gate_functions":list(unchanged),
        "old_v001_frozen_pins_unchanged":True,"actual_old1115_and_new36_hash_mismatches":0,"actual_two_receipts_fixed1115_validated":True,
        "real_single_UE_log_invocation_receipt_order_exit_validated":True,"default_template_rejected_readonly":True},
    "joint_import_semantics":"Reviewed one-process P2/P3 two18 receipts share fixed old1115 baseline; require Root process/external final36 proof; final1151 saved hashes independently checked",
    "actual_source_or_tools_mutated":False,"actual_native_receipts_mutated":False,"actual_preparation_snapshot_execute":False,
    "current_full161_claimed":False,"Root_PID_exit0_inferred":False,"native_manual_proofs_pending":True,"formal_complete_units":0}
new(HERE/"tooling-freeze-v002.json",freeze)
for row in freeze["files"]+freeze["inputs"]:C.match(ROOT,row)
print(json.dumps({"freeze":C.desc(ROOT,HERE/"tooling-freeze-v002.json"),"public_tools":freeze["public_tools"],
    "synthetic_methods_passed":8,"unchanged_core_gate_functions":len(unchanged),"pin_mismatches":0,
    "actual_preparation_snapshot_run":False,"current_full161_claimed":False},indent=2))
