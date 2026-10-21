"""Strict value/file gates for the prospective v125 checkpoint. Never launches UE.
No source fix, import, implicit latest artifact lookup, or green-data synthesis.
"""
from pathlib import Path, PurePosixPath
import hashlib,json,math,re
from datetime import datetime

RESTORE_PATHS={"UnrealGame/Source/CodexDungeon/"+n for n in (
    "DungeonStoneGuard.h","DungeonStoneGuard.cpp","Tests/DungeonStoneGuardRestoreTests.cpp","Tests/StoneGuardRestoreCases.h")}
ART_PATHS={"UnrealGame/Source/CodexDungeon/"+n for n in (
    "DungeonFairytaleSwordPresentation.cpp","DungeonFairytaleEquipmentBoundProbe.h","DungeonFairytaleEquipmentBoundProbe.cpp")}
RESTORE_TESTS={"CodexDungeon.Content.StoneGuardRestore."+n for n in (
    "RealStagesAndFutureContinuation","ClosedWindowsSameCursorDeathAndIndependentObligations","CorruptionAtomicityPolicyAndDeepOwnership")}
FOLDERS=("UnrealGame/Source","UnrealGame/Config","UnrealGame/Content/Production")
DLL="UnrealGame/Binaries/Win64/UnrealEditor-CodexDungeon.dll"
READY="/Game/Production/ArtTrials/EV048/v012/HeroLeatherReady/"
P1="/Game/Production/ArtTrials/EV048/v013/HeroLeatherPrimary1/"
CANVAS=72.*512./416.

class GateError(ValueError):pass
def require(ok,why):
    if not ok:raise GateError(why)
def exact_keys(obj,keys,why):
    require(type(obj) is dict and set(obj)==set(keys),why)
def integer(v,minimum=0):return type(v) is int and v>=minimum
def finite(v):return type(v) in (int,float) and math.isfinite(v)
def pairs(rows):
    out={}
    for k,v in rows:
        require(k not in out,"Duplicate JSON key: "+k);out[k]=v
    return out
def read(p):
    require(p.stat().st_size<=64*1024*1024,"JSON artifact exceeds64MiB")
    with p.open("r",encoding="utf-8-sig") as f:
        return json.load(f,object_pairs_hook=pairs,parse_constant=lambda x:(_ for _ in ()).throw(GateError("Nonfinite JSON token "+x)))
def relative(value):
    require(type(value) is str and value and "\\" not in value and ":" not in value,"Expected relative POSIX path")
    p=PurePosixPath(value)
    require(not p.is_absolute() and all(x not in (".","..","") for x in p.parts) and p.as_posix()==value,"Unsafe/noncanonical relative path")
    return value
def path(root,value):
    value=relative(value);p=(root/value).resolve();require(p.is_relative_to(root.resolve()),"Path escapes root: "+value);return p
def pin(row):
    exact_keys(row,("path","bytes","sha256"),"Invalid file descriptor fields")
    relative(row["path"]);require(integer(row["bytes"]) and type(row["sha256"]) is str and re.fullmatch("[0-9a-f]{64}",row["sha256"]),"Invalid size/SHA descriptor")
    return row
def desc(root,p):
    p=p.resolve();require(p.is_relative_to(root.resolve()) and p.is_file(),"Expected existing in-project file: "+str(p))
    h=hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""):h.update(chunk)
    return {"path":p.relative_to(root.resolve()).as_posix(),"bytes":p.stat().st_size,"sha256":h.hexdigest()}
def match(root,row):
    pin(row);require(desc(root,path(root,row["path"]))==row,"Size/SHA mismatch: "+row["path"])
def table(rows):
    require(type(rows) is list and rows,"Empty/missing file table");out={};folded=set()
    for row in rows:
        pin(row);k=row["path"];require(k.casefold() not in folded,"Duplicate/case-colliding file path: "+k);folded.add(k.casefold());out[k]=row
    return out
def inventory(root,folders=FOLDERS):
    out={}
    for folder in folders:
        directory=path(root,folder);require(directory.is_dir(),"Missing inventory root: "+folder)
        for p in directory.rglob("*"):
            if p.is_file():
                d=desc(root,p);require(d["path"] not in out,"Repeated inventory path");out[d["path"]]=d
    table(list(out.values()));return out
def strict_automation(report,count,names=None):
    require(type(report) is dict and report.get("succeeded")==count and integer(report["succeeded"]),"Automation Success count differs")
    for k in ("failed","succeededWithWarnings","notRun","inProcess"):
        require(k in report and type(report[k]) is int and report[k]==0,"Automation incomplete or dirty: "+k)
    for k in ("errors","warnings"):
        if k in report:require(type(report[k]) is int and report[k]==0,"Automation top-level "+k)
    tests=report.get("tests");require(type(tests) is list and len(tests)==count,"Automation test list count differs")
    found=set()
    for t in tests:
        name=t.get("fullTestPath");require(type(name) is str and name and name not in found,"Duplicate/missing test registration");found.add(name)
        require(t.get("state")=="Success" and type(t.get("errors")) is int and t["errors"]==0 and type(t.get("warnings")) is int and t["warnings"]==0,"Test not clean Success: "+name)
        require(type(t.get("entries")) is list and all(e.get("event",{}).get("type") not in ("Error","Warning") for e in t["entries"]),"Dirty hidden automation entry: "+name)
    if names is not None:require(found==set(names),"Automation registry differs from approved baseline154 + Restore3")
    return found

def validate_request(root,request):
    exact_keys(request,("schema","base_manifest","source_deltas","build_log","last_build","automation_report","dll","build_history","art_mode","import_receipt","import_manifest","additional_files"),"Unknown/missing freeze request field")
    require(request["schema"]=="checkpoint-v125-freeze-request-v1" and request["art_mode"] in ("unchanged","primary1"),"Unknown checkpoint request or art mode")
    for k in ("base_manifest","build_log","last_build","automation_report","dll"):match(root,request[k])
    require(request["dll"]["path"]==DLL and request["last_build"]["path"]=="UnrealGame/Saved/Bootstrap/last-build.json","Wrong DLL/build receipt target")
    base_path=path(root,request["base_manifest"]["path"])
    require(base_path.name=="compiled-source-manifest.json" and base_path.parent.is_relative_to(root/"source-assets/production/backups"),"Base is not an explicit project snapshot")
    base=read(base_path);old=table(base["files"])
    require(base["current_automation_succeeded"]==154 and base["production_packages"]==1097 and base["mismatches"]==0 and base["formal_complete_units"]==0,"Base must be actual clean v124154/1097")
    require(base["copied_files"]==len(old) and base["bytes"]==sum(x["bytes"] for x in old.values()),"Base snapshot counters differ")
    for row in old.values():match(base_path.parent,row)
    old_report=relative(base["current_automation_report"]);require(old_report in old,"Base automation was not frozen")
    baseline_names=strict_automation(read(path(base_path.parent,old_report)),154)
    require(not (baseline_names&RESTORE_TESTS),"Restore tests unexpectedly already in baseline")
    current=inventory(root);source={k:v for k,v in current.items() if k.startswith(("UnrealGame/Source/","UnrealGame/Config/"))}
    old_source={k:v for k,v in old.items() if k.startswith(("UnrealGame/Source/","UnrealGame/Config/"))}
    require(set(old_source)<=set(source),"Source/config deletion is forbidden")
    changed={k for k,v in source.items() if old_source.get(k)!=v}
    allowed=RESTORE_PATHS|(ART_PATHS if request["art_mode"]=="primary1" else set())
    deltas=table(request["source_deltas"]);require(set(deltas)==changed==allowed,"Source delta set is not the exact approved whitelist")
    require(all(source[k]==v for k,v in deltas.items()),"Approved Source pins differ from actual source")
    # Reject an old report or DLL even if numeric summaries look green.
    names=baseline_names|RESTORE_TESTS;strict_automation(read(path(root,request["automation_report"]["path"])),157,names)
    history=request["build_history"];require(type(history) is list,"Explicit build history must be a list")
    chain=[];build_extras=[]
    for entry in history:
        exact_keys(entry,("receipt","log"),"Unknown build history descriptor")
        match(root,entry["receipt"]);match(root,entry["log"]);chain.append(entry);build_extras.extend((entry["receipt"],entry["log"]))
    chain.append({"receipt":request["last_build"],"log":request["build_log"]})
    logs=set();coverage={};previous=-1.
    for entry in chain:
        require(entry["log"]["path"] not in logs,"Repeated build log in chain");logs.add(entry["log"]["path"])
        build=read(path(root,entry["receipt"]["path"]))
        require(type(build.get("ExitCode")) is int and build["ExitCode"]==0 and build.get("Target")=="CodexDungeonEditor","Build history receipt is not actual exit0 editor target")
        require(Path(build["Log"]).resolve()==path(root,entry["log"]["path"]),"Build history receipt names another log")
        stamp=datetime.fromisoformat(build["Utc"].replace("Z","+00:00"));require(stamp.tzinfo is not None,"Build UTC receipt missing timezone");finished=stamp.timestamp()
        require(finished>previous,"Build history is not strictly chronological");previous=finished
        log=path(root,entry["log"]["path"]).read_text(encoding="utf-8-sig",errors="strict")
        compiled=set(re.findall(r"^\[\d+/\d+\] Compile \[[^\]]+\] ([^\r\n]+)$",log,re.M))
        require(re.search(r"^\[\d+/\d+\] Link \[[^\]]+\] UnrealEditor-CodexDungeon\.dll\s*$",log,re.M),"Build history log lacks DLL link action")
        for name in compiled:coverage.setdefault(name,[]).append(finished)
    # Incremental final builds may retain genuine previously compiled objects.
    # Every changed CPP must have an actual Compile after its current write time,
    # under an explicit preserved exit0 receipt. Never infer a prior build from filename.
    for k in allowed:
        name=Path(k).name
        if k.endswith(".cpp"):
            require(any(t>=path(root,k).stat().st_mtime for t in coverage.get(name,[])),"Build chain lacks post-write Compile for "+name)
    dll=path(root,DLL);report_path=path(root,request["automation_report"]["path"])
    require(report_path.stat().st_mtime_ns>=dll.stat().st_mtime_ns,"Automation report predates final DLL")
    require(all(path(root,k).stat().st_mtime_ns<=dll.stat().st_mtime_ns for k in allowed),"Source was written after final linked DLL; obtain a new build")
    header_cpp={"DungeonStoneGuard.h":"DungeonStoneGuard.cpp","StoneGuardRestoreCases.h":"DungeonStoneGuardRestoreTests.cpp","DungeonFairytaleEquipmentBoundProbe.h":"DungeonFairytaleEquipmentBoundProbe.cpp"}
    for k in allowed:
        if k.endswith(".h"):
            require(any(t>=path(root,k).stat().st_mtime for t in coverage.get(header_cpp[Path(k).name],[])),"Build chain lacks post-header-write dependent Compile: "+k)
    require(dll.stat().st_mtime<=previous,"DLL timestamp follows the final exit0 receipt")
    old_prod={k:v for k,v in old.items() if k.startswith("UnrealGame/Content/Production/")}
    prod={k:v for k,v in current.items() if k.startswith("UnrealGame/Content/Production/")}
    require(len(old_prod)==1097 and all(prod.get(k)==v for k,v in old_prod.items()),"An original1097Production package changed or disappeared")
    extras=build_extras
    ready_pin=base["new_production_import_receipt"];match(root,ready_pin);extras.append(ready_pin)
    ready_import=read(path(root,ready_pin["path"]))
    require(ready_import["namespace"]==READY.rstrip("/") and ready_import["success"] is True and all(ready_import[k]==12 for k in ("actual_count","saved_count","expected_count")),"Base Ready12 native import is not retained")
    ready_manifest=Path(ready_import["manifest"]).resolve();ready_manifest_pin=desc(root,ready_manifest)
    require(ready_manifest_pin["sha256"]==ready_import["manifest_sha256"],"Old Ready import manifest changed");extras.append(ready_manifest_pin)
    ready_assemblies=[v for k,v in old.items() if "/ready-integer-assembly-" in k and Path(k).name=="assembly-freeze-v001.json"]
    require(len(ready_assemblies)==1,"Base snapshot missing unique old Ready assembly freeze")
    ready_assembly_pin=ready_assemblies[0];match(root,ready_assembly_pin);extras.append(ready_assembly_pin)
    ready_assembly=path(root,ready_assembly_pin["path"]);ready_data=read(ready_assembly);ready_rows=table(ready_data["files"])
    require(ready_data["file_count_excluding_manifest"]==len(ready_rows) and ready_data["total_bytes_excluding_manifest"]==sum(x["bytes"] for x in ready_rows.values()),"Old Ready assembly counters differ")
    for row in ready_rows.values():
        match(ready_assembly.parent,row);ready_source=path(ready_assembly.parent,row["path"])
        extras.append({"path":ready_source.relative_to(root).as_posix(),"bytes":row["bytes"],"sha256":row["sha256"]})
    require(len(ready_import["assets"])==12 and {(a["component"],a["frame"]) for a in ready_import["assets"]}=={(c,f) for c in ("Chest","ShoulderNear","ShoulderFar") for f in range(4)},"Old Ready native slot set differs")
    for a in ready_import["assets"]:
        require(a["actual_object_type"]=="Texture2D","Old Ready object class differs")
        ready_asset=Path(a["saved_uasset"]).resolve();ready_asset_pin={"path":ready_asset.relative_to(root).as_posix(),"bytes":a["saved_bytes"],"sha256":a["saved_sha256"]}
        require(prod.get(ready_asset_pin["path"])==ready_asset_pin,"Old Ready asset differs from its original native import")
    if request["art_mode"]=="unchanged":
        require(request["import_receipt"] is None and request["import_manifest"] is None and prod==old_prod,"No-art mode has an asset delta")
    else:
        match(root,request["import_receipt"]);match(root,request["import_manifest"]);extras+=[request["import_receipt"],request["import_manifest"]]
        imported=read(path(root,request["import_receipt"]["path"]));require(imported.get("success") is True and imported.get("namespace")==P1.rstrip("/"),"Actual import failed or targets wrong namespace")
        require(all(type(imported.get(k)) is int and imported[k]==18 for k in ("actual_count","saved_count","expected_count")),"Import is not exactly18saved native objects")
        require(Path(imported["manifest"]).resolve()==path(root,request["import_manifest"]["path"]) and imported["manifest_sha256"]==request["import_manifest"]["sha256"],"Native receipt is not bound to approved import manifest")
        require(type(imported.get("old_packages_unchanged")) is int and imported["old_packages_unchanged"]==1097 and imported.get("registry_exact_set_passed") is True and imported.get("disk_exact_set_passed") is True,"Native import old/registry/disk gate did not pass")
        approved=read(path(root,request["import_manifest"]["path"]))
        assembly=imported.get("assembly_freeze");require(type(assembly) is dict and assembly==approved.get("assembly_freeze")==approved.get("references",{}).get("assembly_freeze"),"Receipt and manifest top/reference assembly pins differ")
        def native_pin(value):
            exact_keys(value,("path","bytes","sha256"),"Invalid native reference descriptor")
            candidate=Path(value["path"]);candidate=(candidate if candidate.is_absolute() else root/candidate).resolve()
            require(candidate.is_relative_to(root),"Native reference escapes project")
            converted={"path":candidate.relative_to(root).as_posix(),"bytes":value["bytes"],"sha256":value["sha256"]};match(root,converted);return converted
        assembly_pin=native_pin(assembly);extras.append(assembly_pin);assembly_path=path(root,assembly_pin["path"])
        assembly_data=read(assembly_path);assembly_rows=table(assembly_data["files"])
        require(assembly_data["file_count_excluding_manifest"]==len(assembly_rows) and assembly_data["total_bytes_excluding_manifest"]==sum(x["bytes"] for x in assembly_rows.values()),"Assembly freeze counters differ")
        for row in assembly_rows.values():
            match(assembly_path.parent,row);candidate=path(assembly_path.parent,row["path"])
            extras.append({"path":candidate.relative_to(root).as_posix(),"bytes":row["bytes"],"sha256":row["sha256"]})
        for value in approved["references"].values():extras.append(native_pin(value))
        assets=imported.get("assets");require(type(assets) is list and len(assets)==18,"Actual import asset list incomplete")
        slots=set();new_prod={}
        for a in assets:
            require(a.get("component") in ("Chest","ShoulderNear","ShoulderFar") and type(a.get("frame")) is int and 0<=a["frame"]<6,"Bad component/frame slot")
            slot=(a["component"],a["frame"]);require(slot not in slots,"Duplicate import slot");slots.add(slot)
            require(a.get("actual_object_type")=="Texture2D","Native imported object is not Texture2D")
            name=f"T_Fairytale_LeatherPrimary1{slot[0]}_{slot[1]:03d}_v001";package=P1+name
            require(a["name"]==name and a["package_path"]==package and a["object_path"]==package+"."+name,"Actual package/object identity differs")
            saved=Path(a["saved_uasset"]).resolve();expected="UnrealGame/Content/"+package[len("/Game/"):]+".uasset"
            require(saved==path(root,expected) and expected not in old_prod and expected not in new_prod,"Imported path overwrites/duplicates old assets")
            d={"path":expected,"bytes":a["saved_bytes"],"sha256":a["saved_sha256"]};match(root,d);new_prod[expected]=d
            source=Path(a["source"]).resolve();require(source.is_relative_to(root/"source-assets/production"),"Import source is outside approved production candidates")
            sd={"path":source.relative_to(root).as_posix(),"bytes":a["source_bytes"],"sha256":a["source_sha256"]};match(root,sd);extras.append(sd)
        require(len(slots)==18 and prod=={**old_prod,**new_prod} and len(prod)==1115,"Production is not exact unchanged1097 plus18")
    additional=request["additional_files"];require(type(additional) is list,"Additional frozen inputs must be explicit list")
    for row in additional:match(root,row)
    return base,current,names,extras+additional

def snapshot(root,snapshot_path):
    snapshot_path=snapshot_path.resolve();require(snapshot_path.is_relative_to(root/"source-assets/production/backups"),"Snapshot outside project backups")
    m=read(snapshot_path/"compiled-source-manifest.json");require(m["schema"]=="equipment-bound-current-build-strict-v125" and m["current_automation_succeeded"]==157 and m["production_packages"] in (1097,1115) and m["mismatches"]==0,"Wrong strict checkpoint version/count")
    require(Path(m["snapshot"]).resolve()==snapshot_path and m["old_production_packages"]==1097 and m["old_production_unchanged"] is True and m["formal_complete_units"]==0,"Snapshot identity/old-assets/acceptance metadata differs")
    require(m["art_mode"] in ("unchanged","primary1") and m["new_production_packages"]==(18 if m["art_mode"]=="primary1" else 0) and m["required_manual_proofs"]==(["default","ready","primary1"] if m["art_mode"]=="primary1" else ["default"]),"Snapshot art/proof requirement was weakened")
    rows=table(m["files"]);require(m["source_and_copy_checks"]==2*len(rows),"Snapshot endpoint audit count differs")
    require(m["copied_files"]==len(rows) and m["bytes"]==sum(x["bytes"] for x in rows.values()),"Snapshot counters differ")
    for row in rows.values():match(root,row);match(snapshot_path,row)
    expected={k:v for k,v in rows.items() if any(k.startswith(f+"/") for f in FOLDERS)}
    require(inventory(root)==expected,"Current Source/Config/Production set changed after checkpoint")
    request_pin=m["freeze_request"];require(rows.get(request_pin["path"])==request_pin,"Freeze request not part of snapshot")
    request=read(path(root,request_pin["path"]));base,current,names,_=validate_request(root,request)
    require(m["actual_expected_test_names"]==sorted(names) and m["art_mode"]==request["art_mode"] and m["production_packages"]==len([k for k in current if k.startswith(FOLDERS[2]+"/")]),"Checkpoint metadata differs from its audited request")
    return m,rows

def expected_art_stack(clip,frame):
    sword="/Game/Production/FirstBatch/v002/CandidateComponents/T_military_sword_v002.T_military_sword_v002"
    if clip=="sword_ready_idle":
        old="/Game/Production/ArtTrials/EV048/v006/HeroSwordArmorReady/";prefix="T_Fairytale_SwordReady";new=READY;fresh="T_Fairytale_LeatherReady";parts=("BodyRest","ShoulderFar","Chest","NearArmWithoutHand","ShoulderNear",None,"NearHand")
    else:
        require(clip=="sword_primary_1","No new art stack for another stage")
        old="/Game/Production/ArtTrials/EV048/v007/HeroSwordArmorPrimary1/";prefix="T_Fairytale_SwordPrimary1";new=P1;fresh="T_Fairytale_LeatherPrimary1";parts=("BodyRest","ShoulderFar","Chest","NearArmWithoutHand","ShoulderNear","HelmetForeground",None,"NearHand")
    out=[]
    for component in parts:
        if component is None:out.append(sword);continue
        armor=component in ("Chest","ShoulderNear","ShoulderFar");name=f"{fresh if armor else prefix}{component}_{frame:03d}_v001";out.append((new if armor else old)+name+"."+name)
    return out

def stack_has(x,prefix):return sum(type(v) is str and v.startswith(prefix) for v in x["draw_stack"])
def verify_proof(root,manifest_path,proof,art):
    exact_keys(proof,("kind","index","runtime","pixel"),"Unknown/missing native proof fields")
    for k in ("index","runtime","pixel"):match(root,proof[k])
    ix=read(path(root,proof["index"]["path"]));v=read(path(root,proof["runtime"]["path"]));pixel=read(path(root,proof["pixel"]["path"]))
    expected_manifest=desc(root,manifest_path)
    require(ix["source_manifest_SHA256"]==expected_manifest["sha256"] and path(root,ix["snapshot"])==manifest_path.parent,"Proof uses another compiled snapshot/DLL")
    return verify_native_values(proof["kind"],ix,v,pixel,art)

def verify_native_values(kind,ix,v,pixel,art):
    """Pure semantic seam. Caller independently pins files and binds snapshot SHA."""
    require(ix.get("runtime_passed") is True and type(ix.get("exit_code")) is int and ix["exit_code"]==0 and integer(ix.get("process_id"),1),"Proof process did not pass")
    require(v.get("schema")=="fairytale-equipment-bound-native-flow-v1" and v.get("passed") is True and v.get("flow_complete") is True and v.get("mismatches")==[] and v.get("reason")==v.get("failure")=="","Native proof not cleanly complete")
    require(v.get("silent_video") is True and v.get("audio_recorded") is False and v.get("native_async_capture_writes_flushed") is True,"Native silent/flush contract differs")
    require(pixel.get("passed") is True and pixel.get("every_source_viewport_pixel_crc_matches") is True and pixel.get("native_async_writer_verified") is True,"Native pixel/FIFO proof not successful")
    obs=v.get("observations");require(type(obs) is list and obs and ix["observations"]==len(obs) and pixel["verified_original_PNG_count"]==len(obs)+1,"Native observation/PNG counts differ")
    timing=v["capture_timing"];offsets=timing["frame_wall_offsets_s"];duration=timing["requested_video_wall_duration_s"]
    require(timing["use_fixed_time_step"] is False and finite(duration) and duration>0 and len(offsets)==len(obs) and all(finite(t) for t in offsets) and offsets[0]>=0 and all(a<b for a,b in zip(offsets,offsets[1:])) and offsets[-1]<=duration,"Native real-time capture timing differs")
    require(type(v.get("formal_complete_units")) is int and v["formal_complete_units"]==0,"Proof falsely claims full content completion")
    light=v["light_instance_id"];require(type(light) is str and re.fullmatch("[1-9][0-9]*",light),"Missing actual light instance")
    first=obs[0];last=obs[-1];masks=[0,0];ids=[set(),set()];ready=[0,0];combo_masks=[0,0,0];combo_ids=[set(),set(),set()];p1end=0.;lastp1wall=-1.;final_ready=0
    for i,x in enumerate(obs):
        require(x["interface_visible"] is False and x["text_calls"]==0 and finite(x["canvas_size"]) and abs(x["canvas_size"]-CANVAS)<1e-9 and x["texture_ready"] is True and x["active"] is True,"UI/canvas/native texture contract differs")
        require(finite(x["sim"]) and x["sim"]==x["actual_sim"] and x["wall_offset_s"]==offsets[i],"Observation owner clock/offset differs")
        require((x["run"],x["owner_id"],x["committed_weapon_id"])==(first["run"],first["owner_id"],first["committed_weapon_id"]),"Proof changed run/owner/weapon instance")
        armor=x["committed_armor_id"];has=any("Chest" in p or "Shoulder" in p for p in x["draw_stack"])
        require(has==x["draw_stack_has_armor"],"Reported armor presence differs from stack")
        if armor=="0":require(not x["armor_drawn"] and not has,"NoArmor falsely draws armor")
        elif armor==light:
            if x["supported"]:
                require(x["armor_drawn"] is True and x["armor_ready"] is True and has and x["weapon"] and len(x["draw_stack"])==(7 if x["clip"]=="sword_ready_idle" else 8),"Actual light stack incomplete")
            if art and x["armor_drawn"]:
                if x["clip"] in ("sword_ready_idle","sword_primary_1"):require(x["draw_stack"]==expected_art_stack(x["clip"],x["frame"]),"Exact new armor/old body/helmet/hand/sword stack order differs")
                require(stack_has(x,READY if x["clip"]=="sword_ready_idle" else P1 if x["clip"]=="sword_primary_1" else "/Game/")== (3 if x["clip"] in ("sword_ready_idle","sword_primary_1") else len(x["draw_stack"])),"Selected new Ready/P1 paths missing")
        else:require(armor==v["medium_instance_id"] and not x["supported"] and not x["armor_drawn"] and not has and not x["weapon"],"Unsupported medium leaks sword/light armor")
        if x.get("committed_gear_placeholder_expected") is True:
            require(x["supported"] is False and x["clip"]=="sword_ready_idle" and x["frame"]==0 and x["weapon"] and x["instance_id"]==first["committed_weapon_id"] and len(x["draw_stack"])==(7 if armor==light else 3),"Pending committed gear identity lost or pose falsely accepted")
        require(finite(x["facing"]) and x["facing"] in (-1,1),"Invalid rendered facing")
        if armor in ("0",light) and x["supported"] is False and x.get("committed_gear_placeholder_expected") is not True:
            require(not x["armor_drawn"] and not has and not x["weapon"],"Unsupported pose leaks committed gear outside permitted pickup placeholder")
        side=0 if x["facing"]<0 else 1
        if armor==light and x["supported"] and x["flow_step"]==6 and x["clip"] in ("sword_primary_1","sword_primary_2","sword_primary_3"):
            stage=x["stage"];require(type(stage) is int and 0<=stage<3 and x["clip"]==f"sword_primary_{stage+1}" and type(x["frame"]) is int and 0<=x["frame"]<6,"Invalid actual combo phase")
            combo_masks[stage]|=1<<x["frame"];combo_ids[stage].add(x["action_id"])
        if armor==light and x["supported"] and x["clip"]=="sword_ready_idle" and x["flow_step"]==5:
            require(type(x["frame"]) is int and 0<=x["frame"]<4,"Invalid Ready frame");ready[side]|=1<<x["frame"]
        if armor==light and x["supported"] and x["clip"]=="sword_primary_1" and x["flow_step"]==6:
            require(x["stage"]==0 and type(x["frame"]) is int and 0<=x["frame"]<6,"Invalid P1 sample")
            masks[side]|=1<<x["frame"];ids[side].add(x["action_id"]);p1end=max(p1end,x["end"]);lastp1wall=x["wall_offset_s"]
    inputs=v["normal_input_requests"];require(inputs==v["inputevents"],"Input aliases differ")
    downs=[x["key"] for x in inputs if x["down"] is True];held=set();at=-1.
    for x in inputs:
        require(x["key"] in ("Enter","E","A","D","J") and type(x["down"]) is bool and finite(x["wall_offset_s"]) and x["wall_offset_s"]>=at,"Invalid input/key order")
        at=x["wall_offset_s"]
        if x["down"]:require(x["key"] not in held,"Duplicate held input");held.add(x["key"])
        else:require(x["key"] in held,"Unmatched release");held.remove(x["key"])
    require(not held,"Capture stopped with held inputs")
    if kind=="default":
        require(v.get("leather_ready_only_trial",False) is False and v.get("leather_primary1_only_trial",False) is False and v["light_primary_phase_masks"]==combo_masks==[63,63,63] and all(len(z)==1 for z in combo_ids) and len(set.union(*combo_ids))==3,"Default proof is a shorter trial or lacks three distinct actual six-phase stages")
        require(downs==["Enter","E","A","E","J","J","J","E","Enter","E","Enter"] and int(last["operation_count"])-int(first["operation_count"])==3 and int(last["next_operation_id"])-int(first["next_operation_id"])==3 and last["committed_armor_id"]==light,"Default real operations/three-J/final retake missing")
        phases={x["flow_phase"] for x in obs};require({"baseline_no_armor","light_pending_cancel","light_canceled","light_pickup_commit","light_ready","light_three_stage","medium_selection","medium_commit","medium_unsupported_ready","original_light_retake_selection","original_light_retake_commit","original_light_retaken_ready"}<=phases,"Default proof omitted transaction phase")
    elif kind=="ready":
        require(all(v[k]=="0" for k in ("medium_instance_id","medium_source_id","original_light_drop_source")) and last["committed_armor_id"]==light,"Ready proof entered medium/drop or lost actual light")
        require(art and v.get("leather_ready_only_trial") is True and v.get("leather_primary1_only_trial",False) is False and v["leather_ready_phase_masks_left_right"]==ready==[15,15] and v["light_primary_phase_masks"]==[0,0,0],"Ready trial masks/scope differ")
        require(len(downs)==5 and downs[:4]==["Enter","E","A","E"] and downs[4] in ("A","D"),"Ready trial input sequence differs")
        require(int(last["operation_count"])-int(first["operation_count"])==1,"Ready trial lacks one genuine commit")
    elif kind=="primary1":
        require(all(v[k]=="0" for k in ("medium_instance_id","medium_source_id","original_light_drop_source")) and last["committed_armor_id"]==light,"P1 proof entered medium/drop or lost actual light")
        require(all(x["melee_pending_primary"] is False for x in obs),"P1 proof queued a combo input")
        require(art and v.get("leather_primary1_only_trial") is True and v.get("leather_ready_only_trial") is False and v["leather_primary1_masks_left_right"]==masks==[63,63] and all(len(z)==1 for z in ids),"P1 trial scope/masks/one ID per side differ")
        actual_ids=[next(iter(z)) for z in ids];require(actual_ids==v["leather_primary1_attack_ids_left_right"] and actual_ids[0]!=actual_ids[1] and all(re.fullmatch("[1-9][0-9]*",z) for z in actual_ids),"P1 attack IDs are missing/reused")
        require(len(downs)==7 and downs[:5]==["Enter","E","A","E","J"] and downs[5] in ("A","D") and downs[6]=="J","P1 must use exactly two separate J and one turn")
        final_ready=sum(1 for x in obs if x["flow_step"]==6 and x["wall_offset_s"]>lastp1wall and x["sim"]>=p1end and x["supported"] and x["clip"]=="sword_ready_idle" and x["committed_armor_id"]==light)
        require(final_ready>=3,"P1 final Ready uses stale first-attack counter; need3fresh post-second observations")
        attacks={}
        for x in obs:
            if x["supported"] and x["clip"]=="sword_primary_1":
                fact=(x["start"],x["end"],x["facing"])
                require(x["action_id"] not in attacks or attacks[x["action_id"]]==fact,"P1 immutable action facts changed")
                attacks[x["action_id"]]=fact
        ordered=sorted(attacks.values());require(len(ordered)==2 and ordered[1][0]>=ordered[0][1]+.45,"P1 did not wait original chain expiry before the second fresh attack")
        turns=[x for x in inputs if x["down"] and x["key"] in ("A","D")]
        require(len(turns)==2 and turns[-1]["sim"]>=ordered[0][1]+.45,"P1 changed facing before existing chain expiry")
        require(int(last["operation_count"])-int(first["operation_count"])==1,"P1 trial lacks one genuine commit")
    else:raise GateError("Unknown proof kind")
    return {"kind":kind,"process_id":ix["process_id"],"observations":len(obs),"mismatches":0,"final_primary1_ready_observations":final_ready}
