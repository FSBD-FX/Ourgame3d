"""Read actual final artifacts into a NEW candidate input; only candidate files are written."""
from pathlib import Path
import importlib.util
import json
import subprocess
import sys
sys.dont_write_bytecode=True

HERE=Path(__file__).resolve().parent
ROOT=Path("F:/Ourgame").resolve()
FREEZER=HERE.parent/"current-freezer-v002"
PYTHON=ROOT/"tools/runtime/asset-gen/Scripts/python.exe"
spec=importlib.util.spec_from_file_location("current_common",FREEZER/"checkpoint_v126_common_v002.py")
C=importlib.util.module_from_spec(spec);spec.loader.exec_module(C)
def new(path,value):
    with path.open("x",encoding="utf-8",newline="\n") as stream:stream.write(value if isinstance(value,str) else json.dumps(value,ensure_ascii=False,indent=2)+"\n")

draft=C.read(FREEZER/"preparation-input-TEMPLATE-v002.json")
draft["template_only"]=False
draft["joint_import_proof"]=C.desc(ROOT,ROOT/"source-assets/production/fairytale-lgt-readability-v003/combo-import-v001/joint-import-proof-v001.json")
report_path=ROOT/"UnrealGame/Saved/Automation/FirstRoom-20261017-043640/index.json"
report=C.read(report_path);names=sorted(item["fullTestPath"] for item in report["tests"])
C.strict_automation(report,161,names)
draft["current_automation"]={"report":C.desc(ROOT,report_path),"expected_count":161,"full_test_paths":names}
draft["expected_test_count"]=161
draft["last_build"]=C.desc(ROOT,ROOT/"UnrealGame/Saved/Bootstrap/last-build.json")
last=C.read(C.path(ROOT,draft["last_build"]["path"]));assert last["ExitCode"]==0 and Path(last["Log"]).name=="build-editor-20261017-043534.log"
draft["build_log"]=C.desc(ROOT,Path(last["Log"]).resolve())
draft["dll"]=C.desc(ROOT,ROOT/C.DLL)
history_receipts=[
    "docs/production/first-batch-v2/evidence/stone-guard-owner-v002/root-actual-fixture-failure-v001/compiled-overlay/UnrealGame/Saved/Bootstrap/last-build.json",
    "docs/production/first-batch-v2/evidence/stone-guard-owner-v002/root-actual-threeRED-v002/compiled-overlay/UnrealGame/Saved/Bootstrap/last-build.json",
    "source-assets/production/leather-combo-diagnostic-root-input-v001/last-build-art-034734.json",
    "source-assets/production/leather-combo-diagnostic-root-input-v002/last-build-art-041127.json",
    "docs/production/first-batch-v2/evidence/stone-guard-owner-v002/root-core-mixed-v001/compiled-overlay/UnrealGame/Saved/Bootstrap/last-build.json",
    "docs/production/first-batch-v2/evidence/stone-guard-owner-v002/root-clean-version-RED-v002/compiled-overlay/UnrealGame/Saved/Bootstrap/last-build.json",
]
draft["build_history"]=[{"receipt":C.desc(ROOT,ROOT/name),"log":C.desc(ROOT,Path(C.read(ROOT/name)["Log"]).resolve())} for name in history_receipts]
base=C.read(C.path(ROOT,draft["base_manifest"]["path"]));old=C.table(base["files"]);current=C.inventory(ROOT)
before={key:row for key,row in old.items() if key.startswith(("UnrealGame/Source/","UnrealGame/Config/"))}
source={key:row for key,row in current.items() if key.startswith(("UnrealGame/Source/","UnrealGame/Config/"))}
assert set(before)<=set(source)
changed={key for key,row in source.items() if before.get(key)!=row}
draft["source_deltas"]=[source[key] for key in sorted(changed)]
affected=C.affected_translation_units(ROOT,current,changed);draft["translation_units"]=sorted(affected)
draft["proof_tools"]=[C.desc(ROOT,ROOT/row["path"]) for row in draft["proof_tools"]]
additional={row["path"]:row for row in draft["additional_files"]}
def add(candidate):
    row=C.desc(ROOT,candidate);assert row["path"] not in additional or additional[row["path"]]==row;additional[row["path"]]=row
for name in (
    "source-assets/production/leather-combo-proof-tooling-v001/current-freezer-v002/tooling-freeze-v002.json",
    "source-assets/production/stone-guard-owner-v002/production-v001/production-freeze-v001.json",
    "source-assets/production/stone-guard-owner-v002/stage0-fixture-repair-v002/fixture-repair-freeze-v002.json",
    "source-assets/production/stone-guard-owner-v002/production-v001/save-boundary-fixture-repair-v002/repair-freeze-v002.json",
    "docs/production/first-batch-v2/evidence/stone-guard-owner-v002/root-production-core-admission-v001/admission.json",
    "docs/production/first-batch-v2/evidence/stone-guard-owner-v002/root-save-fixture-admission-v002/admission.json",
    "docs/production/first-batch-v2/evidence/stone-guard-owner-v002/root-production-adapter-admission-v001/admission.json",
    "tools/scripts/ue-import-leather-combo-v001.py","tools/scripts/import-leather-combo-v001.ps1",
):add(ROOT/name)
owner_path=ROOT/"docs/production/first-batch-v2/evidence/stone-guard-owner-v002/root-owner-fourGREEN-full161-v001/manifest.json"
add(owner_path);owner=C.read(owner_path)
for item in owner["files"]:
    candidate=C.path(owner_path.parent,item["retained"]);row=C.desc(ROOT,candidate)
    assert row["bytes"]==item["bytes"] and row["sha256"]==item["sha256"];add(candidate)
draft["additional_files"]=[additional[key] for key in sorted(additional)]
draft["fill_instructions"]=[
    "This NEW candidate is concrete and filled from actual043534 final exit0/DLL and043640 full161 strictGREEN. It creates no snapshot by itself.",
    "Root reviews it, then runs v002 preparer read-only followed by --execute, then v002 freezer read-only followed by --execute. All four commands require project-relative --input/--request.",
    "All changed Source/Config pins and their exact transitive CPP consumers are sampled from current actual bytes. Any later edit requires a NEW input/version and new relevant actual compile/full report, never mutate this candidate.",
    "Actual fourth cleanRED043440 and targeted4GREEN043606 are historical validation evidence;043640 is the complete161 strictGREEN gate.",
    "The preserved chronological build_history is032107/033340/034734/041127/041957/043406; final043534 is separate last_build/build_log and is not duplicated.",
    "Former future fourth fixture/Adapter/full161 fields are now resolved by actual saved Root evidence. Native formalcombo proof and independent playable entry remain pending; old default v006 binding is historical and not upgraded here."
]
candidate=HERE/"preparation-input-current161-v001.json";new(candidate,draft)
prepare_spec=importlib.util.spec_from_file_location("prepare_tool",FREEZER/"prepare-current-build-v126-v002.py")
# The public script imports its sibling module by name.
sys.path.insert(0,str(FREEZER));prepare=importlib.util.module_from_spec(prepare_spec);prepare_spec.loader.exec_module(prepare)
directory,contract_path,contract_bytes,request=prepare.build_inputs(ROOT,draft,candidate)
plan=C.validate_request(ROOT,request,{request["combo_proof_contract"]["path"]:contract_bytes})
command=[str(PYTHON),"-B","-X","utf8",str(FREEZER/"prepare-current-build-v126-v002.py"),"--project",str(ROOT),"--input",candidate.relative_to(ROOT).as_posix()]
checked=subprocess.run(command,capture_output=True,text=True,encoding="utf-8");new(HERE/"actual-readonly-preparation-plan-v001.log",checked.stdout+checked.stderr)
assert checked.returncode==0,checked.stderr
new(HERE/"input-audit-v001.json",{"candidate":C.desc(ROOT,candidate),"read_only_public_CLI_plan_passed":True,"actual_execute_run":False,
    "actual_full161_strictGREEN":draft["current_automation"]["report"],"actual_final_build":draft["build_log"],"actual_final_DLL":draft["dll"],
    "source_delta_count":len(changed),"translation_unit_count":len(affected),"chronological_prior_builds":len(draft["build_history"]),
    "prospective_snapshot_files_before_freezer_self_inputs":len(plan["rows"]),"production_packages":plan["production_packages"],
    "joint_import_audit":plan["joint_import_audit"],"Root_full161_preserved_files":len(owner["files"]),
    "old_default_v006_upgraded":False,"formalcombo_native_proof_pending":True,"playable_entry_pending":True,"formal_complete_units":0})
print(json.dumps({"candidate":C.desc(ROOT,candidate),"readonly_plan_passed":True,"source_deltas":len(changed),"translation_units":len(affected),
    "actual_final_tests":len(names),"production_packages":plan["production_packages"],"prospective_files":len(plan["rows"]),"executed":False},indent=2))
