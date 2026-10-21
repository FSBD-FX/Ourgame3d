"""Strict prospective v125 freezer. Default is read-only; --execute copies NEW snapshot only."""
from pathlib import Path
import argparse,json,re,shutil,sys
sys.dont_write_bytecode=True
import checkpoint_v125_common_v001 as C

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--project",required=True);ap.add_argument("--request",required=True);ap.add_argument("--name",required=True);ap.add_argument("--execute",action="store_true");a=ap.parse_args()
    root=Path(a.project).resolve();request_path=(root/a.request).resolve();C.require(request_path.is_relative_to(root),"Request outside project")
    C.require(re.fullmatch(r"[A-Za-z0-9_-]+",a.name),"Unsafe new snapshot name")
    out=root/"source-assets/production/backups"/a.name;C.require(not out.exists(),"Never overwrite/reuse an existing snapshot")
    request=C.read(request_path);base,current,names,extras=C.validate_request(root,request)
    paths=set(current)
    pins=extras+[request[k] for k in ("base_manifest","build_log","last_build","automation_report","dll")]
    paths.update(row["path"] for row in pins)
    paths.update((C.desc(root,request_path)["path"],C.desc(root,Path(__file__))["path"],C.desc(root,Path(C.__file__))["path"]))
    rows=[C.desc(root,C.path(root,k)) for k in sorted(paths)];C.table(rows)
    print(json.dumps({"preflight_passed":True,"executed":False,"prospective_snapshot":out.as_posix(),"prospective_files":len(rows),"prospective_bytes":sum(x["bytes"] for x in rows),"strict_actual_tests":157,"production_packages":1115 if request["art_mode"]=="primary1" else 1097,"source_deltas":sorted(C.RESTORE_PATHS|(C.ART_PATHS if request["art_mode"]=="primary1" else set()))},ensure_ascii=False))
    if not a.execute:return
    out.mkdir(parents=False,exist_ok=False)
    try:
        for row in rows:
            source=C.path(root,row["path"]);target=C.path(out,row["path"]);target.parent.mkdir(parents=True,exist_ok=True)
            with source.open("rb") as reader,target.open("xb") as writer:shutil.copyfileobj(reader,writer,1024*1024)
            shutil.copystat(source,target);C.match(out,row)
        for row in rows:C.match(root,row);C.match(out,row)
        # Repeat complete source set/assets/report gates after copying; a racing change invalidates publication.
        C.validate_request(root,request)
        m={"schema":"equipment-bound-current-build-strict-v125","snapshot":out.as_posix(),"status":"current157GREEN_before_new_native_manual_proofs","files":rows,"copied_files":len(rows),"bytes":sum(x["bytes"] for x in rows),"production_packages":1115 if request["art_mode"]=="primary1" else 1097,"old_production_packages":1097,"old_production_unchanged":True,"new_production_packages":18 if request["art_mode"]=="primary1" else 0,"new_production_import_receipt":request["import_receipt"],"ready_production_import_receipt":base["new_production_import_receipt"],"base_snapshot":str(C.path(root,request["base_manifest"]["path"]).parent),"base_manifest":request["base_manifest"],"freeze_request":C.desc(root,request_path),"current_automation_report":request["automation_report"]["path"],"current_automation_succeeded":157,"actual_expected_test_names":sorted(names),"build_log":request["build_log"]["path"],"build_binding":{"last_build":request["last_build"],"build_log":request["build_log"],"automation_report":request["automation_report"],"dll":request["dll"],"source_deltas":request["source_deltas"],"build_history":request["build_history"]},"art_mode":request["art_mode"],"required_manual_proofs":["default","ready","primary1"] if request["art_mode"]=="primary1" else ["default"],"source_and_copy_checks":2*len(rows),"mismatches":0,"formal_complete_units":0}
        with (out/"compiled-source-manifest.json").open("x",encoding="utf-8",newline="\n") as f:json.dump(m,f,ensure_ascii=False,indent=2);f.write("\n")
        print(json.dumps({"snapshot_created":True,"manifest":C.desc(root,out/"compiled-source-manifest.json"),"files":len(rows),"endpoint_checks":2*len(rows),"mismatches":0,"manual_ready":False},ensure_ascii=False))
    except Exception as exc:
        # Preserve partial copies as failure evidence; never delete, retry into or publish them.
        with (out/"freeze-failure-v001.json").open("x",encoding="utf-8") as f:json.dump({"complete_manifest_published":False,"error":str(exc)},f,ensure_ascii=False)
        raise

if __name__=="__main__":
    try:main()
    except (C.GateError,OSError,ValueError,KeyError,TypeError) as exc:print(json.dumps({"preflight_passed":False,"error":str(exc)},ensure_ascii=False),file=sys.stderr);sys.exit(1)
