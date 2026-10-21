"""Current combo freezer. Read-only plan by default; --execute creates a NEW short snapshot."""
from pathlib import Path
import argparse
import json
import sys
sys.dont_write_bytecode=True
import checkpoint_v126_common_v002 as C


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project",required=True);parser.add_argument("--request",required=True)
    parser.add_argument("--name",default="v126-combo-161G");parser.add_argument("--execute",action="store_true")
    args=parser.parse_args();root=Path(args.project).resolve();request_path=C.path(root,args.request);request=C.read(request_path)
    C.require(args.name==request["snapshot_name"],"Explicit request and output snapshot name differ")
    out=root/"source-assets/production/backups"/args.name
    C.require(not out.exists(),"Never overwrite/reuse existing snapshot, including failed ones")
    C.require(request["combo_proof_contract"]["path"]!=request_path.relative_to(root).as_posix(),"Request cannot be its own proof contract")
    plan=C.validate_request(root,request)
    core_rows=list(plan["rows"])
    extra=[C.desc(root,request_path),C.desc(root,Path(__file__)),C.desc(root,Path(C.__file__))]
    by_path=C.table(plan["rows"])
    for row in extra:
        C.require(row["path"] not in by_path or by_path[row["path"]]==row,"Conflicting author/tool input pin");by_path[row["path"]]=row
    plan["rows"]=[by_path[key] for key in sorted(by_path)];C.table(plan["rows"])
    print(json.dumps({"preflight_passed":True,"executed":False,"prospective_snapshot":out.as_posix(),
        "prospective_files":len(plan["rows"]),"prospective_bytes":sum(row["bytes"] for row in plan["rows"]),
        "actual_full_test_count":len(plan["names"]),"production_packages":plan["production_packages"],
        "old1115_unchanged":True,"new_actual_saved_packages":plan["new_production_packages"],
        "source_deltas":plan["changed"],"build_audit":plan["build_audit"],"formal_complete_units":0},ensure_ascii=False))
    if not args.execute:return
    def revalidate():
        repeated=C.validate_request(root,request)
        for field in ("current","names","changed","source_mtimes_ns","contract_pin","imports","import_manifests","build_audit","joint_import_audit"):
            C.require(repeated[field]==plan[field],"Current endpoint changed while copying: "+field)
        C.require(repeated["rows"]==core_rows,"Referenced closure changed while copying")
        for row in extra:C.match(root,row)
    def manifest():
        return {"schema":"equipment-bound-current-build-strict-v126-combo","snapshot":out.as_posix(),
            "status":f"current{len(plan['names'])}GREEN_before_new_native_manual_proofs","files":plan["rows"],
            "copied_files":len(plan["rows"]),"bytes":sum(row["bytes"] for row in plan["rows"]),
            "production_packages":plan["production_packages"],"old_production_packages":1115,"old_production_unchanged":True,
            "new_production_packages":36,"new_production_import_receipts":{clip:plan["imports"][clip] for clip in request["new_import_order"]},
            "primary1_production_import_receipt":plan["imports"]["Primary1"],"ready_production_import_receipt":plan["imports"]["Ready"],
            "production_import_receipts":plan["imports"],"production_import_manifests":plan["import_manifests"],
            "base_snapshot":str(C.path(root,request["base_manifest"]["path"]).parent),"base_manifest":request["base_manifest"],
            "freeze_request":C.desc(root,request_path),"combo_proof_contract":request["combo_proof_contract"],"joint_import_audit":plan["joint_import_audit"],
            "current_automation_report":request["automation_report"]["path"],"current_automation_succeeded":len(plan["names"]),
            "actual_expected_test_names":plan["names"],"build_log":request["build_log"]["path"],
            "build_binding":{"last_build":request["last_build"],"build_log":request["build_log"],"automation_report":request["automation_report"],
                "dll":request["dll"],"source_deltas":request["source_deltas"],"translation_units":request["translation_units"],
                "source_mtimes_ns":plan["source_mtimes_ns"],"build_history":request["build_history"],"actual_build_audit":plan["build_audit"]},
            "art_mode":"combo","required_manual_proofs":["default","ready","primary1","combo"],
            "source_and_copy_checks":2*len(plan["rows"]),"mismatches":0,"formal_complete_units":0}
    C.copy_new_snapshot(root,out,plan,manifest,revalidate)
    print(json.dumps({"snapshot_created":True,"manifest":C.desc(root,out/"compiled-source-manifest.json"),
        "files":len(plan["rows"]),"endpoint_checks":2*len(plan["rows"]),"mismatches":0,"native_manual_proofs_pending":True},ensure_ascii=False))


if __name__=="__main__":
    try:main()
    except (C.GateError,OSError,ValueError,KeyError,TypeError) as exc:
        print(json.dumps({"preflight_passed":False,"error":str(exc)},ensure_ascii=False),file=sys.stderr);sys.exit(1)
