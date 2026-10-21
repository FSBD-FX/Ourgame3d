"""Root preparer. Default validates/prints future input pins; --execute writes a NEW input directory."""
from pathlib import Path
import argparse
import json
import sys
sys.dont_write_bytecode=True
import checkpoint_v126_common_v002 as C


def payload(value):return (json.dumps(value,ensure_ascii=False,indent=2)+"\n").encode("utf-8")


def build_inputs(root,draft,draft_path):
    C.require(draft["schema"]=="checkpoint-v126-preparation-input-v002" and draft["template_only"] is False,"Root-filled concrete preparation input required")
    directory=C.path(root,draft["output_input_directory"])
    C.require(directory.is_relative_to(root/"source-assets/production") and not directory.is_relative_to(root/"source-assets/production/backups"),"New preparer inputs must be outside backup snapshots")
    C.require(not directory.exists(),"Never overwrite/reuse Root input directory")
    contract={"schema":"leather-combo-runtime-proof-contract-v001","template_only":False,
        "scope":"Ready/P1/P2/P3 matching leather, normal two-facing six-attack proof only","base_snapshot_manifest":draft["base_manifest"],
        "native_source_freeze":draft["native_source_freeze"],"production":draft["production"],"current_automation":draft["current_automation"],
        "additional_source_pins":[row for row in draft["source_deltas"] if row["path"] not in {"UnrealGame/Source/CodexDungeon/"+name for name in C.NATIVE_NAMES}],
        "imports":draft["imports"],"assemblies":draft["assemblies"],"joint_import_proof":draft["joint_import_proof"],"formal_complete_units":0}
    contract_path=directory/"combo-proof-contract-v001.json";contract_bytes=payload(contract);contract_pin=C.bytes_pin(root,contract_path,contract_bytes)
    request={"schema":"checkpoint-v126-combo-freeze-request-v002","template_only":False,"snapshot_name":draft["snapshot_name"],
        "expected_test_count":draft["expected_test_count"],"base_manifest":draft["base_manifest"],"combo_proof_contract":contract_pin,
        "source_deltas":draft["source_deltas"],"translation_units":draft["translation_units"],"build_log":draft["build_log"],
        "last_build":draft["last_build"],"automation_report":draft["current_automation"]["report"],"dll":draft["dll"],
        "build_history":draft["build_history"],"new_import_order":draft["new_import_order"],"joint_import_proof":draft["joint_import_proof"],"proof_tools":draft["proof_tools"],
        "additional_files":draft["additional_files"]+[C.desc(root,draft_path),C.desc(root,Path(__file__)),C.desc(root,Path(C.__file__))]}
    return directory,contract_path,contract_bytes,request


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project",required=True);parser.add_argument("--input",required=True)
    parser.add_argument("--inspect-source",action="store_true");parser.add_argument("--execute",action="store_true")
    args=parser.parse_args();root=Path(args.project).resolve();draft_path=C.path(root,args.input);draft=C.read(draft_path)
    if args.inspect_source:
        C.require(not args.execute,"Source inspection cannot execute preparer")
        C.match(root,draft["base_manifest"]);old=C.table(C.read(C.path(root,draft["base_manifest"]["path"]))["files"])
        current={}
        for folder in C.FOLDERS[:2]:
            for candidate in C.path(root,folder).rglob("*"):
                if candidate.is_file():row=C.desc(root,candidate);current[row["path"]]=row
        before={key:row for key,row in old.items() if key.startswith(("UnrealGame/Source/","UnrealGame/Config/"))}
        C.require(set(before)<=set(current),"Historical source removal")
        changed={key for key,row in current.items() if before.get(key)!=row}
        affected=C.affected_translation_units(root,current,changed)
        print(json.dumps({"read_only_unapproved_source_inspection":True,"build_or_GREEN_claimed":False,
            "observed_source_deltas":[current[key] for key in sorted(changed)],"required_translation_units":sorted(affected),
            "affected_changed_dependencies":{key:sorted(value) for key,value in sorted(affected.items())}},ensure_ascii=False,indent=2));return
    directory,contract_path,contract_bytes,request=build_inputs(root,draft,draft_path)
    plan=C.validate_request(root,request,{request["combo_proof_contract"]["path"]:contract_bytes})
    request_path=directory/"freeze-request-v126-v002.json";request_bytes=payload(request)
    print(json.dumps({"read_only_preparation_passed":True,"executed":False,"future_input_directory":directory.as_posix(),
        "future_contract":request["combo_proof_contract"],"future_request":C.bytes_pin(root,request_path,request_bytes),
        "current_full_tests":len(plan["names"]),"production_packages":plan["production_packages"],"formal_complete_units":0},ensure_ascii=False,indent=2))
    if not args.execute:return
    directory.mkdir(parents=False,exist_ok=False)
    try:
        with contract_path.open("xb") as stream:stream.write(contract_bytes)
        with request_path.open("xb") as stream:stream.write(request_bytes)
        C.validate_request(root,C.read(request_path))
        print(json.dumps({"input_directory_created":True,"contract":C.desc(root,contract_path),"request":C.desc(root,request_path),
            "snapshot_created":False,"native_proofs_pending":True},ensure_ascii=False,indent=2))
    except Exception as exc:
        with (directory/"preparation-failure-v001.json").open("x",encoding="utf-8") as stream:json.dump({"snapshot_created":False,"error":str(exc),"inputs_preserved":True},stream,ensure_ascii=False,indent=2)
        raise


if __name__=="__main__":
    try:main()
    except (C.GateError,OSError,ValueError,KeyError,TypeError) as exc:
        print(json.dumps({"read_only_preparation_passed":False,"error":str(exc)},ensure_ascii=False),file=sys.stderr);sys.exit(1)
