JOINT_IMPORTER_SHA256="e431a6ca295098229ed041616fd814a4e2009db9554e0f9876251111e24e3b3a"
JOINT_DECODER_SHA256="5c667edbeb81eac54648d14ff92b8883d1b15a39a05cc3b56c17933dd29eb49a"
JOINT_CONTRACT_SHA256="3506ebdc2a46cb784366ad621bebbea0f761633c35b557b73262f82a0381de6a"


def joint_import_values(proof,imports,new_prod,final_inventory):
    require(proof.get("schema")=="root-leather-combo-joint-import-proof-v001" and proof.get("template_only") is False and proof.get("mode")=="single_process_two18_fixed_old1115" and proof.get("same_process") is True,"Explicit Root joint-two-receipt process proof required")
    process=proof.get("process",{})
    require(type(process.get("pid")) is int and process["pid"]>0 and type(process.get("exit_code")) is int and process["exit_code"]==0,"Root joint process PID/exit0 evidence missing")
    require(proof.get("receipts")=={clip:imports[clip] for clip in ("Primary2","Primary3")},"Root joint proof uses another actual receipt pair")
    require(type(proof.get("old_packages_unchanged")) is int and proof["old_packages_unchanged"]==1115 and proof.get("p2_saved_hashes_unchanged_after_p3") is True,"Root joint baseline/P2 preservation evidence differs")
    require(final_inventory.get("schema")=="root-leather-combo-final36-inventory-v001" and final_inventory.get("template_only") is False and type(final_inventory.get("mismatches")) is int and final_inventory["mismatches"]==0,"Root actual final36 inventory not clean")
    require(final_inventory.get("production_packages")==1151 and final_inventory.get("old_packages_unchanged")==1115 and final_inventory.get("new_packages")==36 and final_inventory.get("p2_saved_hashes_unchanged_after_p3") is True,"Root final36/old1115 totals differ")
    require(table(final_inventory["files"])==new_prod and len(new_prod)==36,"Root final36 inventory differs from two actual saved receipt hashes")


def joint_log_values(log,importer_path,receipt_paths):
    normalized=log.replace("\\","/").casefold()
    commands=re.findall(r"^.*loginit: command line: ([^\r\n]+)$",normalized,re.M)
    require(len(commands)==1 and "-executepythonscript="+importer_path.as_posix().casefold() in commands[0] and "--validate-only" not in commands[0],"Joint log is not one actual importer invocation")
    observed=re.findall(r"LogPython: Leather combo receipt: ([^\r\n]+)",log)
    require([Path(value).resolve() for value in observed]==receipt_paths,"Same pinned UE log must contain exactly P2 then P3 receipt once each")
    last=normalized.rfind("logpython: leather combo receipt:")
    require(last>=0 and normalized.find("logexit: exiting.",last)>last and "logpython: error" not in normalized and "traceback (most recent call last)" not in normalized,"Joint importer log incomplete or Python failed")


def validate_joint_import(root,proof_pin,contract,old_prod,new_prod,import_manifest_pins):
    match(root,proof_pin);proof=read(path(root,proof_pin["path"]));extras=[proof_pin]
    def add(value):
        row=native_pin(root,value);extras.append(row);return row
    importer=add(proof["importer"]);decoder=add(proof["decoder"]);import_contract_pin=add(proof["import_contract"])
    require(importer["path"]=="tools/scripts/ue-import-leather-combo-v001.py" and importer["sha256"]==JOINT_IMPORTER_SHA256,"Joint importer differs from independently reviewed fixed-baseline implementation")
    require(decoder["sha256"]==JOINT_DECODER_SHA256 and import_contract_pin["sha256"]==JOINT_CONTRACT_SHA256,"Joint importer decoder/approved contract binding differs")
    import_contract=read(path(root,import_contract_pin["path"]))
    require(import_contract["schema"]=="root-leather-p2p3-36-import-v1" and import_contract["new_count"]==36 and import_contract["total_packages_after"]==1151,"Joint import contract count/schema differs")
    require([native_pin(root,value) for value in import_contract["manifests"]]==[import_manifest_pins[clip] for clip in ("Primary2","Primary3")],"Joint importer did not bind these two actual import manifests")
    for value in import_contract["manifests"]:add(value)
    old_inventory_pin=add(import_contract["old_inventory"])
    require(table(read(path(root,old_inventory_pin["path"]))["files"])==old_prod and len(old_prod)==1115,"Joint importer old inventory differs from historical frozen1115")
    imports={clip:native_pin(root,contract["imports"][clip]) for clip in CLIPS}
    require(proof["receipts"]=={clip:imports[clip] for clip in ("Primary2","Primary3")},"Joint external receipt pins must use canonical project-relative descriptors")
    for value in proof["receipts"].values():add(value)
    final_pin=add(proof["final36_inventory"]);final_inventory=read(path(root,final_pin["path"]))
    joint_import_values(proof,imports,new_prod,final_inventory)
    log_pin=add(proof["process"]["log"]);log=path(root,log_pin["path"]).read_text(encoding="utf-8-sig")
    receipt_paths=[path(root,imports[clip]["path"]) for clip in ("Primary2","Primary3")]
    joint_log_values(log,path(root,importer["path"]),receipt_paths)
    require(path(root,final_pin["path"]).stat().st_mtime_ns>=max(value.stat().st_mtime_ns for value in receipt_paths),"Root final36 inventory predates the actual receipt pair")
    return extras,{"mode":"single_process_two18_fixed_old1115","root_process_id":proof["process"]["pid"],"actual_two_receipts":imports,
        "old_packages_unchanged":1115,"new_saved_packages":36,"production_packages":1151,"p2_saved_hashes_unchanged_after_p3":True,
        "root_joint_import_proof":proof_pin,"final36_inventory":final_pin,"single_UE_log":log_pin}


