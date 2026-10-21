"""Prospective current combo snapshot gates. No UE, implicit latest lookup or green synthesis."""
from pathlib import Path, PurePosixPath
from datetime import datetime
import hashlib
import json
import os
import re
import shutil
from PIL import Image

FOLDERS=("UnrealGame/Source","UnrealGame/Config","UnrealGame/Content/Production")
DLL="UnrealGame/Binaries/Win64/UnrealEditor-CodexDungeon.dll"
NATIVE_NAMES=("DungeonFairytaleSwordPresentation.cpp","DungeonFairytaleSwordPrimary2ArmorV001.inl","DungeonFairytaleSwordPrimary3V001.inl","DungeonFairytaleEquipmentBoundProbe.h","DungeonFairytaleEquipmentBoundProbe.cpp")
CLIPS=("Ready","Primary1","Primary2","Primary3")
COMPONENTS=("Chest","ShoulderNear","ShoulderFar")
NAMESPACES={clip:f"/Game/Production/ArtTrials/EV048/v{version}/HeroLeather{clip}/" for clip,version in zip(CLIPS,("012","013","014","015"))}
REQUIRED_TOOLS={"tools/scripts/"+name for name in ("capture-leather-combo-trial-v001.ps1","postprocess-leather-combo-trial-v001.py","verify-leather-combo-proof-v001.py","verify-native-bound-capture-pixels-v001.py")}


class GateError(ValueError):pass

def require(ok,why):
    if not ok:raise GateError(why)

def exact_keys(obj,keys,why):
    require(type(obj) is dict and set(obj)==set(keys),why)

def pairs(rows):
    result={}
    for key,value in rows:
        require(key not in result,"Duplicate JSON key: "+key);result[key]=value
    return result

def read(path):
    require(path.stat().st_size<=64*1024*1024,"JSON artifact exceeds64MiB")
    return json.loads(path.read_text(encoding="utf-8-sig"),object_pairs_hook=pairs,
        parse_constant=lambda value:(_ for _ in ()).throw(GateError("Nonfinite JSON token "+value)))

def relative(value):
    require(type(value) is str and value and "\\" not in value and ":" not in value,"Expected project-relative POSIX path")
    candidate=PurePosixPath(value)
    require(not candidate.is_absolute() and candidate.as_posix()==value and all(part not in (".","..","") for part in candidate.parts),"Unsafe/noncanonical relative path")
    return value

def path(root,value):
    candidate=(root/relative(value)).resolve();require(candidate.is_relative_to(root.resolve()),"Path escapes root: "+value);return candidate

def pin(row):
    exact_keys(row,("path","bytes","sha256"),"Invalid file pin fields");relative(row["path"])
    require(type(row["bytes"]) is int and row["bytes"]>=0 and type(row["sha256"]) is str and re.fullmatch("[0-9a-f]{64}",row["sha256"]),"Invalid file pin size/SHA")
    return row

def desc(root,candidate):
    candidate=candidate.resolve();require(candidate.is_relative_to(root.resolve()) and candidate.is_file(),"Expected existing project file: "+str(candidate))
    digest=hashlib.sha256()
    with candidate.open("rb") as stream:
        for block in iter(lambda:stream.read(1024*1024),b""):digest.update(block)
    return {"path":candidate.relative_to(root.resolve()).as_posix(),"bytes":candidate.stat().st_size,"sha256":digest.hexdigest()}

def bytes_pin(root,candidate,payload):
    require(candidate.resolve().is_relative_to(root.resolve()),"Virtual input escapes project")
    return {"path":candidate.resolve().relative_to(root.resolve()).as_posix(),"bytes":len(payload),"sha256":hashlib.sha256(payload).hexdigest()}

def match(root,row,virtual=None):
    pin(row)
    if virtual and row["path"] in virtual:
        require(bytes_pin(root,path(root,row["path"]),virtual[row["path"]])==row,"Virtual future contract pin differs")
    else:require(desc(root,path(root,row["path"]))==row,"Size/SHA mismatch: "+row["path"])

def native_pin(root,row):
    exact_keys(row,("path","bytes","sha256"),"Invalid native reference pin")
    candidate=Path(row["path"]);candidate=(candidate if candidate.is_absolute() else root/candidate).resolve()
    require(candidate.is_relative_to(root.resolve()),"Native reference escapes project")
    result={"path":candidate.relative_to(root.resolve()).as_posix(),"bytes":row["bytes"],"sha256":row["sha256"]};match(root,result);return result

def table(rows,allow_empty=False):
    require(type(rows) is list and (rows or allow_empty),"Empty/missing pin list")
    result={};folded=set()
    for row in rows:
        pin(row);require(row["path"].casefold() not in folded,"Duplicate/case-colliding pin: "+row["path"])
        folded.add(row["path"].casefold());result[row["path"]]=row
    return result

def inventory(root):
    result={}
    for folder in FOLDERS:
        directory=path(root,folder);require(directory.is_dir(),"Missing inventory root: "+folder)
        for candidate in directory.rglob("*"):
            if candidate.is_file():
                row=desc(root,candidate);require(row["path"] not in result,"Duplicate inventory path");result[row["path"]]=row
    table(list(result.values()));return result

def strict_automation(report,count,names):
    require(type(count) is int and count>0 and type(names) is list and len(names)==len(set(names))==count and all(type(name) is str and name for name in names),"Explicit complete unique test-name set/count invalid")
    require(type(report.get("succeeded")) is int and report["succeeded"]==count,"Current automation Success count differs")
    for key in ("failed","succeededWithWarnings","notRun","inProcess"):
        require(type(report.get(key)) is int and report[key]==0,"Current full suite incomplete/dirty: "+key)
    for key in ("errors","warnings"):
        if key in report:require(type(report[key]) is int and report[key]==0,"Current automation top-level "+key)
    tests=report.get("tests");require(type(tests) is list and len(tests)==count,"Current test list count differs")
    found=set()
    for item in tests:
        name=item.get("fullTestPath");require(type(name) is str and name and name not in found,"Duplicate/missing registered test name");found.add(name)
        require(item.get("state")=="Success" and type(item.get("errors")) is int and item["errors"]==0 and type(item.get("warnings")) is int and item["warnings"]==0,"Test not clean Success: "+name)
        require(type(item.get("entries")) is list and all(entry.get("event",{}).get("type") not in ("Error","Warning") for entry in item["entries"]),"Hidden Error/Warning test entry: "+name)
    require(found==set(names),"Current automation differs from explicit complete registry")
    return found

def source_changes(old,current,approved):
    before={key:value for key,value in old.items() if key.startswith(("UnrealGame/Source/","UnrealGame/Config/"))}
    after={key:value for key,value in current.items() if key.startswith(("UnrealGame/Source/","UnrealGame/Config/"))}
    require(set(before)<=set(after),"Historical Source/Config removal is not authorized")
    changed={key for key,row in after.items() if before.get(key)!=row};explicit=table(approved,allow_empty=True)
    require(set(explicit)==changed and all(explicit[key]==after[key] for key in changed),"Root source_deltas must exactly pin all actual current Source/Config changes")
    return changed

def affected_translation_units(root,current,changed):
    """Project-local quoted includes, transitively; engine/generated headers remain UBT-owned."""
    code={key for key in current if key.startswith("UnrealGame/Source/")};graph={key:set() for key in code}
    roots=[root/"UnrealGame/Source/CodexDungeon",root/"UnrealGame/Source"]
    for key in code:
        if Path(key).suffix.lower() not in (".cpp",".h",".hpp",".inl"):continue
        candidate=path(root,key)
        for name in re.findall(r'^\s*#\s*include\s*"([^"\r\n]+)"',candidate.read_text(encoding="utf-8-sig"),re.M):
            options=[candidate.parent/name]+[base/name for base in roots]
            for option in options:
                target=option.resolve()
                if target.is_relative_to(root.resolve()) and target.relative_to(root.resolve()).as_posix() in code:
                    graph[key].add(target.relative_to(root.resolve()).as_posix());break
    affected={}
    for key in code:
        if not key.endswith(".cpp"):continue
        seen={key};pending=[key]
        while pending:
            for target in graph[pending.pop()]:
                if target not in seen:seen.add(target);pending.append(target)
        dependencies=seen&changed
        if dependencies:affected[key]=dependencies
    non_cpp={key for key in changed if key.startswith("UnrealGame/Source/") and not key.endswith(".cpp")}
    mapped=set().union(*affected.values()) if affected else set()
    require(non_cpp<=mapped,"Changed non-CPP Source is not resolved to any project translation unit; explicit new gate needed: "+", ".join(sorted(non_cpp-mapped)))
    return affected

def check_translation_units(affected,explicit):
    require(type(explicit) is list and len(explicit)==len(set(explicit)) and set(explicit)==set(affected),"Root translation_units must equal all changed CPP and transitive header/inl consumers")
    require(len({Path(key).name for key in explicit})==len(explicit),"Ambiguous duplicate CPP basename needs a new build-log gate")
    for key in explicit:relative(key)

def validate_build_history(root,chain,affected,dll_pin,report_pin):
    require(type(chain) is list and chain,"Explicit actual build_history/final build required")
    previous=-1.;logs=set();coverage={};extras=[]
    for entry in chain:
        exact_keys(entry,("receipt","log"),"Invalid build history entry")
        match(root,entry["receipt"]);match(root,entry["log"]);extras.extend((entry["receipt"],entry["log"]))
        require(entry["log"]["path"] not in logs,"Repeated build log");logs.add(entry["log"]["path"])
        receipt=read(path(root,entry["receipt"]["path"]))
        require(type(receipt.get("ExitCode")) is int and receipt["ExitCode"]==0 and receipt.get("Target")=="CodexDungeonEditor","Actual build receipt is not exit0 CodexDungeonEditor")
        require(Path(receipt["Log"]).resolve()==path(root,entry["log"]["path"]),"Build receipt/log identity differs")
        stamp=datetime.fromisoformat(receipt["Utc"].replace("Z","+00:00"));require(stamp.tzinfo is not None,"Build receipt UTC lacks timezone");finished=stamp.timestamp()
        require(finished>previous,"Build history is not strictly chronological");previous=finished
        log=path(root,entry["log"]["path"]).read_text(encoding="utf-8-sig")
        require(re.search(r"^\[\d+/\d+\] Link \[[^\]]+\] UnrealEditor-CodexDungeon\.dll\s*$",log,re.M),"Actual build log lacks final module DLL link")
        for name in re.findall(r"^\[\d+/\d+\] Compile \[[^\]]+\] ([^\r\n]+)$",log,re.M):coverage.setdefault(name,[]).append(finished)
    for unit,dependencies in affected.items():
        # An included changed header/inl must precede its consumer's real Compile.
        threshold=max(path(root,key).stat().st_mtime for key in {unit}|set(dependencies))
        require(any(finished>=threshold for finished in coverage.get(Path(unit).name,[])),"Build history lacks post-write actual Compile: "+unit)
    dll=path(root,dll_pin["path"]);report=path(root,report_pin["path"])
    require(dll.stat().st_mtime<=previous,"Final DLL timestamp follows exit0 build receipt")
    require(report.stat().st_mtime_ns>=dll.stat().st_mtime_ns,"Current full automation report predates final DLL")
    require(all(path(root,key).stat().st_mtime_ns<=dll.stat().st_mtime_ns for values in affected.values() for key in values),"Changed Source written after final DLL")
    return extras,{"chronological_exit0_linked_builds":len(chain),"actual_translation_units":sorted(affected),"translation_unit_count":len(affected),"final_build_receipt_utc":read(path(root,chain[-1]["receipt"]["path"]))["Utc"]}

def assembly_closure(root,assembly_pin):
    match(root,assembly_pin);assembly_path=path(root,assembly_pin["path"]);assembly=read(assembly_path);members=table(assembly["files"])
    if "file_count_excluding_manifest" in assembly:require(assembly["file_count_excluding_manifest"]==len(members),"Assembly file count differs")
    if "total_bytes_excluding_manifest" in assembly:require(assembly["total_bytes_excluding_manifest"]==sum(row["bytes"] for row in members.values()),"Assembly byte count differs")
    result=[]
    for row in members.values():
        candidate=path(assembly_path.parent,row["path"]);match(assembly_path.parent,row)
        result.append({"path":candidate.relative_to(root.resolve()).as_posix(),"bytes":row["bytes"],"sha256":row["sha256"]})
    return result,{row["path"] for row in result}

def import_values(imported,clip,expected_old=None):
    count=12 if clip=="Ready" else 18
    require(imported.get("success") is True and imported.get("namespace")==NAMESPACES[clip].rstrip("/"),"Actual import failed/wrong namespace: "+clip)
    require(all(type(imported.get(key)) is int and imported[key]==count for key in ("actual_count","saved_count","expected_count")),"Actual native saved counts differ: "+clip)
    if expected_old is not None:
        require(type(imported.get("old_packages_unchanged")) is int and imported["old_packages_unchanged"]==expected_old and imported.get("registry_exact_set_passed") is True and imported.get("disk_exact_set_passed") is True,"New native old-packages/registry/disk gate differs: "+clip)
    assets=imported.get("assets");require(type(assets) is list and len(assets)==count,"Native import assets incomplete: "+clip)
    result={}
    for asset in assets:
        component,frame=asset.get("component"),asset.get("frame")
        require(component in COMPONENTS and type(frame) is int and 0<=frame<(4 if clip=="Ready" else 6),"Invalid actual component/frame")
        name=f"T_Fairytale_Leather{clip}{component}_{frame:03d}_v001";package=NAMESPACES[clip]+name
        require(asset.get("name")==name and asset.get("package_path")==package and asset.get("object_path")==package+"."+name and asset.get("actual_object_type")=="Texture2D","Actual imported object/Texture2D identity differs")
        key="UnrealGame/Content/"+package[len("/Game/"):]+".uasset";require(key not in result,"Duplicate imported object");result[key]=asset
    require(len(result)==count,"Incomplete actual object registry set")
    return result

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


def validate_request(root,request,virtual=None):
    exact_keys(request,("schema","template_only","snapshot_name","expected_test_count","base_manifest","combo_proof_contract","source_deltas","translation_units","build_log","last_build","automation_report","dll","build_history","new_import_order","joint_import_proof","proof_tools","additional_files"),"Unknown/missing current freeze request field")
    require(request["schema"]=="checkpoint-v126-combo-freeze-request-v002" and request["template_only"] is False,"Concrete Root request required")
    require(type(request["snapshot_name"]) is str and re.fullmatch(r"[A-Za-z0-9_-]{1,48}",request["snapshot_name"]),"Unsafe/long new snapshot name")
    require(type(request["expected_test_count"]) is int and request["expected_test_count"]>=161,"This current slice requires explicit full161 or later GREEN")
    extras={}
    def add(row):
        pin(row);match(root,row,virtual)
        require(row["path"] not in extras or extras[row["path"]]==row,"Conflicting explicit pins: "+row["path"]);extras[row["path"]]=row;return row
    for key in ("base_manifest","combo_proof_contract","build_log","last_build","automation_report","dll"):add(request[key])
    require(request["dll"]["path"]==DLL and request["last_build"]["path"]=="UnrealGame/Saved/Bootstrap/last-build.json","Wrong actual final DLL/build receipt")
    base_path=path(root,request["base_manifest"]["path"]);require(base_path.name=="compiled-source-manifest.json" and base_path.parent.is_relative_to(root/"source-assets/production/backups"),"Historical base must be explicit project snapshot")
    base=read(base_path);old=table(base["files"])
    require(base["production_packages"]==1115 and base["current_automation_succeeded"]==157 and base["mismatches"]==0,"Historical successful v1251115/full157 required")
    require(base["copied_files"]==len(old) and base["bytes"]==sum(row["bytes"] for row in old.values()),"Historical snapshot counters differ")
    for row in old.values():match(base_path.parent,row)
    baseline_report=base["current_automation_report"];require(baseline_report in old,"Historical full report was not frozen")
    baseline_names=base["actual_expected_test_names"];strict_automation(read(path(base_path.parent,baseline_report)),157,baseline_names)
    contract_pin=request["combo_proof_contract"]
    contract=(json.loads(virtual[contract_pin["path"]].decode("utf-8"),object_pairs_hook=pairs) if virtual and contract_pin["path"] in virtual else read(path(root,contract_pin["path"])))
    require(contract["schema"]=="leather-combo-runtime-proof-contract-v001" and contract["template_only"] is False and contract["scope"]=="Ready/P1/P2/P3 matching leather, normal two-facing six-attack proof only","Wrong concrete combo contract")
    require(contract["base_snapshot_manifest"]==request["base_manifest"] and contract["production"]=={"baseline_count":1115,"new_packages":36,"expected_total":1151},"Historical/production runtime contract differs")
    current=inventory(root);changed=source_changes(old,current,request["source_deltas"])
    affected=affected_translation_units(root,current,changed);check_translation_units(affected,request["translation_units"])
    native_freeze_pin=native_pin(root,contract["native_source_freeze"]);add(native_freeze_pin)
    native_freeze_path=path(root,native_freeze_pin["path"]);native=read(native_freeze_path);candidates={}
    for value in native["files"]:
        row=native_pin(root,value);add(row)
        if path(root,row["path"]).parent==native_freeze_path.parent and Path(row["path"]).name in NATIVE_NAMES:candidates[Path(row["path"]).name]=row
    require(set(candidates)==set(NATIVE_NAMES),"Native freeze lacks exact Combo5 candidates")
    native_keys={"UnrealGame/Source/CodexDungeon/"+name for name in NATIVE_NAMES}
    for name,row in candidates.items():
        actual=current.get("UnrealGame/Source/CodexDungeon/"+name);require(actual and actual["bytes"]==row["bytes"] and actual["sha256"]==row["sha256"],"Actual Combo5 Source differs from frozen candidate: "+name)
    additional_code=table(contract["additional_source_pins"],allow_empty=True)
    require(set(additional_code)==changed-native_keys and all(current[key]==row for key,row in additional_code.items()),"Runtime contract omits/invents non-combo Source/Config delta")
    automation=contract["current_automation"]
    require(automation["report"]==request["automation_report"] and automation["expected_count"]==request["expected_test_count"],"Request/current exact report/count contract differs")
    names=strict_automation(read(path(root,request["automation_report"]["path"])),request["expected_test_count"],automation["full_test_paths"])
    require(set(baseline_names)<=names,"Current suite omitted historical registered tests")
    chain=list(request["build_history"])+[{"receipt":request["last_build"],"log":request["build_log"]}]
    build_pins,build_audit=validate_build_history(root,chain,affected,request["dll"],request["automation_report"])
    for row in build_pins:add(row)
    old_prod={key:row for key,row in old.items() if key.startswith("UnrealGame/Content/Production/")};prod={key:row for key,row in current.items() if key.startswith("UnrealGame/Content/Production/")}
    require(len(old_prod)==1115 and all(prod.get(key)==row for key,row in old_prod.items()),"Historical old1115 package changed/disappeared")
    require(set(contract["assemblies"])==set(contract["imports"])==set(CLIPS),"Four exact assembly/import pins required")
    assembly_members={}
    for clip in CLIPS:
        assembly_pin=native_pin(root,contract["assemblies"][clip]);add(assembly_pin)
        rows,assembly_members[clip]=assembly_closure(root,assembly_pin)
        for row in rows:add(row)
    require(contract["imports"]["Ready"]==base["ready_production_import_receipt"] and contract["imports"]["Primary1"]==base["new_production_import_receipt"],"Historical Ready/P1 actual receipt pins differ")
    order=request["new_import_order"];require(type(order) is list and len(order)==2 and set(order)=={"Primary2","Primary3"},"Explicit actual two-receipt new import order required")
    require(contract["imports"]["Primary2"]["path"]!=contract["imports"]["Primary3"]["path"],"This current freeze requires two actual18 import receipts")
    require(order==["Primary2","Primary3"],"Reviewed joint importer runs P2 then P3 in one process")
    new_prod={};expected_old={clip:1115 for clip in order};import_manifest_pins={}
    for clip in CLIPS:
        receipt_pin=native_pin(root,contract["imports"][clip]);add(receipt_pin);receipt=read(path(root,receipt_pin["path"]))
        assets=import_values(receipt,clip,expected_old.get(clip))
        approved_path=Path(receipt["manifest"]).resolve();approved_pin=desc(root,approved_path);require(approved_pin["sha256"]==receipt["manifest_sha256"],"Actual native import manifest SHA changed");add(approved_pin);import_manifest_pins[clip]=approved_pin
        approved=read(approved_path)
        require(approved["namespace"]==NAMESPACES[clip].rstrip("/") and approved["asset_count"]==len(assets),"Approved native manifest namespace/count differs")
        if clip in ("Primary1","Primary2","Primary3"):
            expected_assembly=native_pin(root,contract["assemblies"][clip])
            require(native_pin(root,receipt["assembly_freeze"])==native_pin(root,approved["assembly_freeze"])==native_pin(root,approved["references"]["assembly_freeze"])==expected_assembly,"Receipt/manifest/runtime assembly pin differs")
        for value in approved.get("references",{}).values():add(native_pin(root,value))
        approved_assets={item["object_path"]:item for item in approved["assets"]};require(len(approved_assets)==len(assets),"Import manifest has duplicate/missing source objects")
        for key,asset in assets.items():
            saved=Path(asset["saved_uasset"]).resolve();require(saved==path(root,key),"Actual imported disk path differs")
            package_pin={"path":key,"bytes":asset["saved_bytes"],"sha256":asset["saved_sha256"]};require(prod.get(key)==package_pin,"Actual saved package SHA differs")
            source=Path(asset["source"]).resolve();source_pin={"path":source.relative_to(root).as_posix(),"bytes":asset["source_bytes"],"sha256":asset["source_sha256"]};add(source_pin)
            require(source_pin["path"] in assembly_members[clip],"Actual imported PNG is not in corresponding assembly closure")
            with Image.open(source) as image:require(image.format=="PNG" and image.mode=="RGBA" and image.size==(512,512),"Original import source must stay512 RGBA")
            approved_asset=approved_assets.get(asset["object_path"]);require(approved_asset is not None,"Actual object not in explicit import manifest")
            for field in ("component","frame","name","package_path","object_path","source_bytes","source_sha256"):
                require(approved_asset[field]==asset[field],"Manifest/receipt actual source slot differs: "+field)
            require(Path(approved_asset["source"]).resolve()==source,"Manifest/receipt actual source path differs")
            for field in ("registered_source","registration_proof"):
                if field in asset:
                    require(native_pin(root,asset[field])==native_pin(root,approved_asset[field]),"Native original registration pin differs");add(native_pin(root,asset[field]))
            if clip in order:
                require(key not in old_prod and key not in new_prod,"New import overwrites/duplicates historical asset");new_prod[key]=package_pin
    require(len(new_prod)==36 and len(prod)==1151 and prod=={**old_prod,**new_prod},"Production is not exact old1115 unchanged plus actual new36")
    require(contract.get("joint_import_proof")==request["joint_import_proof"],"Runtime contract and request joint import proof differ")
    joint_pins,joint_audit=validate_joint_import(root,request["joint_import_proof"],contract,old_prod,new_prod,import_manifest_pins)
    for row in joint_pins:add(row)
    tools=table(request["proof_tools"]);require(REQUIRED_TOOLS<=set(tools),"All combo capture/postprocess/verify/pixel tools must be explicit pins")
    for row in list(tools.values())+request["additional_files"]:add(row)
    rows={**current}
    for key,row in extras.items():require(key not in rows or rows[key]==row,"Conflicting closure pin");rows[key]=row
    table(list(rows.values()))
    return {"base":base,"current":current,"rows":[rows[key] for key in sorted(rows)],"names":sorted(names),"changed":sorted(changed),"contract":contract,
        "joint_import_audit":joint_audit,"contract_pin":contract_pin,"imports":{clip:native_pin(root,contract["imports"][clip]) for clip in CLIPS},"import_manifests":import_manifest_pins,"build_audit":build_audit,
        "source_mtimes_ns":{key:path(root,key).stat().st_mtime_ns for key in changed},"production_packages":len(prod),"old_production_packages":len(old_prod),"new_production_packages":len(new_prod)}

def copy_new_snapshot(root,out,plan,make_manifest,revalidate):
    require(not out.exists(),"Never overwrite/reuse existing snapshot")
    out.mkdir(parents=False,exist_ok=False)
    try:
        for row in plan["rows"]:
            source=path(root,row["path"]);target=path(out,row["path"]);target.parent.mkdir(parents=True,exist_ok=True)
            with source.open("rb") as reader,target.open("xb") as writer:shutil.copyfileobj(reader,writer,1024*1024)
            shutil.copystat(source,target);match(out,row)
        for row in plan["rows"]:match(root,row);match(out,row)
        revalidate()
        manifest=make_manifest();pending=out/"compiled-source-manifest.pending-v001.json"
        with pending.open("x",encoding="utf-8",newline="\n") as stream:
            json.dump(manifest,stream,ensure_ascii=False,indent=2);stream.write("\n");stream.flush();os.fsync(stream.fileno())
        require(not (out/"compiled-source-manifest.json").exists(),"Manifest unexpectedly exists before publication")
        pending.rename(out/"compiled-source-manifest.json")
        return manifest
    except Exception as exc:
        with (out/"freeze-failure-v001.json").open("x",encoding="utf-8",newline="\n") as stream:json.dump({"complete_manifest_published":False,"error":str(exc),"partial_files_preserved":True},stream,ensure_ascii=False,indent=2);stream.write("\n")
        raise
