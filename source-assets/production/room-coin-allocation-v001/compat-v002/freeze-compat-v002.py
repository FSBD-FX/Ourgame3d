from pathlib import Path
import datetime,difflib,hashlib,json,re

ROOT=Path(__file__).resolve().parent
def pin(p):
    b=p.read_bytes()
    return {"path":p.as_posix(),"bytes":len(b),"sha256":hashlib.sha256(b).hexdigest()}
def save(name,value):
    p=ROOT/name
    if p.exists():raise RuntimeError(f"Refusing overwrite: {p}")
    p.write_text(json.dumps(value,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")

old=ROOT.parent
old_freeze=json.loads((old/"final-freeze-v001.json").read_text(encoding="utf-8"))
for p in old_freeze["files"]:
    a=pin(Path(p["path"]))
    assert a["bytes"]==p["bytes"] and a["sha256"]==p["sha256"]
for name in ["DungeonRoomCoinAllocation.h","DungeonRoomCoinAllocation.cpp"]:
    assert (ROOT/"original-v001"/name).read_bytes()==(old/"candidate-source"/name).read_bytes()
    before=(ROOT/"original-v001"/name).read_text(encoding="utf-8").splitlines(keepends=True)
    after=(ROOT/"candidate-source"/name).read_text(encoding="utf-8").splitlines(keepends=True)
    patch="".join(difflib.unified_diff(before,after,fromfile=f"a/{name}",tofile=f"b/{name}"))
    path=ROOT/"compatibility-v001-to-v002.patch"
    if name.endswith(".h"):
        if path.exists():raise RuntimeError("Refusing patch overwrite")
        path.write_text(patch,encoding="utf-8")
    else:
        with path.open("a",encoding="utf-8") as out:out.write(patch)

orig_cpp=(ROOT/"original-v001/DungeonRoomCoinAllocation.cpp").read_text(encoding="utf-8")
new_cpp=(ROOT/"candidate-source/DungeonRoomCoinAllocation.cpp").read_text(encoding="utf-8")
assert orig_cpp[:orig_cpp.index("EStatus TryAllocate")] == new_cpp[:new_cpp.index("EStatus TryAllocate")]
names=["original-EHoff-compile-boundary-v001","original-EHoff-UnrealSTL-compile-boundary-v002",
       "compat-EHon-GREEN-v002","compat-EHoff-UnrealSTL-GREEN-v002"]
runs=[]
for name in names:
    folder=ROOT/"runs"/name
    build=(folder/"build.log").read_text(encoding="utf-8-sig")
    expected=2 if name.startswith("original") else 0
    assert f"BUILD_EXIT_CODE={expected}" in build
    if expected:
        assert "C4530" in build and "DungeonRoomCoinAllocation.cpp(88)" in build
    else:
        log=(folder/"run.log").read_text(encoding="utf-8-sig")
        assert "GROUPS=3 CHECKS=197 FAILURES=0" in log and "RUN_EXIT_CODE=0" in log
    runs.append({"name":name,"build_exit":expected,"run_exit":None if expected else 0,
        "build_log":pin(folder/"build.log"),"original_tests_unchanged":True})
save("results-and-input-pins-v002.json",{"created_at":datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "v001_frozen_file_checks":len(old_freeze["files"]),"v001_mismatches":0,
    "integer_Build_body_unchanged":True,"original_tests":pin(old/"tests/RoomCoinAllocationStandalone.cpp"),
    "unchanged_UE_test_candidate":pin(old/"tests/DungeonRoomCoinAllocationTests.cpp"),
    "source_policy_pins":[pin(Path("F:/Ourgame/UnrealGame/Source/CodexDungeon/CodexDungeon.Build.cs")),
                          pin(Path("G:/UE_5.5/Engine/Source/Programs/UnrealBuildTool/Platform/Windows/VCToolChain.cs"))],
    "runs":runs,"UE_UBT_run":False,"ActualSource_edited":False,"full_content_unit_completed":False})
files=sorted(p for p in ROOT.rglob("*") if p.is_file() and p.name!="final-freeze-v002.json")
pins=[pin(p) for p in files]
save("final-freeze-v002.json",{"status":"standalone_EHon_EHoff_compatible_candidate_only_not_UE_compiled_or_admitted",
    "created_at":datetime.datetime.now(datetime.timezone.utc).isoformat(),"file_count":len(pins),
    "bytes":sum(p["bytes"] for p in pins),"files":pins,"UE_UBT_run":False,"ActualSource_edited":False})
for p in pins:
    a=pin(Path(p["path"]))
    assert a["bytes"]==p["bytes"] and a["sha256"]==p["sha256"]
print(json.dumps({"files":len(pins),"bytes":sum(p["bytes"] for p in pins),
    "freeze":pin(ROOT/"final-freeze-v002.json"),"candidate_sources":[pin(p) for p in sorted((ROOT/"candidate-source").glob("*"))],
    "pin_mismatches":0},ensure_ascii=False))
