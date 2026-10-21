from pathlib import Path
import datetime, difflib, hashlib, json, re

ROOT=Path(__file__).resolve().parent
def pin(p):
    b=p.read_bytes()
    return {"path":p.as_posix(),"bytes":len(b),"sha256":hashlib.sha256(b).hexdigest()}
def save(name,value):
    p=ROOT/name
    if p.exists():
        raise RuntimeError(f"Refusing overwrite: {p}")
    p.write_text(json.dumps(value,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")

sources=[
"F:/Ourgame/docs/production/first-batch-v2/evidence/stone-guard-native-v001/save-reward-audit-v001/audit.md",
"F:/Ourgame/docs/production/first-batch-v2/evidence/stone-guard-native-v001/save-reward-audit-v001/candidate-contract.json",
"F:/Ourgame/docs/production/first-batch-v2/evidence/stone-guard-native-v001/save-reward-audit-v001/audit-freeze.json",
"F:/Ourgame/docs/design/economy-v1/reward-sources.json",
"F:/Ourgame/docs/design/economy-v1/common-rules.json",
"F:/Ourgame/docs/design/enemies-v1/common-rules.json",
"F:/Ourgame/docs/design/enemies-v1/stone-forest.json",
]
old_audit=json.loads(Path(sources[2]).read_text(encoding="utf-8-sig"))
freeze_pins=[]
def visit(x):
    if isinstance(x,dict):
        if {"path","bytes","sha256"}.issubset(x):freeze_pins.append(x)
        for y in x.values():visit(y)
    elif isinstance(x,list):
        for y in x:visit(y)
visit(old_audit)
relevant=[]
for p in freeze_pins:
    if p["path"].replace("\\","/") in sources:
        actual=pin(Path(p["path"]))
        relevant.append({"path":p["path"],"size_and_hash_match":actual["bytes"]==p["bytes"] and actual["sha256"]==p["sha256"]})
assert all(p["size_and_hash_match"] for p in relevant)
save("input-pins-v001.json",{"observed_at":datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "sources":[pin(Path(p)) for p in sources],"frozen_audit_relevant_pin_checks":relevant,
    "current_runtime_formal_binding":None,"design_status":"design_only_assistant_proposed_unplaytested"})

assert (ROOT/"stage0/DungeonRoomCoinAllocation.h").read_bytes()==(ROOT/"candidate-source/DungeonRoomCoinAllocation.h").read_bytes()
stage=(ROOT/"stage0/DungeonRoomCoinAllocation.cpp").read_text(encoding="utf-8").splitlines(keepends=True)
prod=(ROOT/"candidate-source/DungeonRoomCoinAllocation.cpp").read_text(encoding="utf-8").splitlines(keepends=True)
patch="".join(difflib.unified_diff(stage,prod,fromfile="a/DungeonRoomCoinAllocation.cpp",tofile="b/DungeonRoomCoinAllocation.cpp"))
(ROOT/"preallocation-stage0-to-production-v001.patch").write_text(patch,encoding="utf-8")

expected={"stage0-RED-v001":(68,44,1),"production-GREEN-v001":(197,0,0),
    "mutation-tie-reversed-v001":(197,6,1),"mutation-float-remainder-v001":(197,1,1),
    "mutation-partial-output-v001":(197,23,1),"mutation-floor-only-v001":(197,36,1)}
runs=[]
for name,(checks,failures,exit_code) in expected.items():
    r=ROOT/"runs"/name
    build=(r/"build.log").read_text(encoding="utf-8-sig")
    run=(r/"run.log").read_text(encoding="utf-8-sig")
    m=re.search(r"GROUPS=(\d+) CHECKS=(\d+) FAILURES=(\d+)",run)
    assert m and tuple(map(int,m.groups()))==(3,checks,failures)
    assert "BUILD_EXIT_CODE=0" in build and f"RUN_EXIT_CODE={exit_code}" in run
    runs.append({"name":name,"build_exit":0,"run_exit":exit_code,"groups":3,"checks":checks,"failures":failures,
                 "build_log":pin(r/"build.log"),"run_log":pin(r/"run.log")})
save("standalone-results-v001.json",{"actual_runs":runs,"UE_UBT_run":False,"ActualSource_edited":False,
    "current_runtime_formal_binding":None,"reward_claim_pickup_wallet_Save_integration":False})
all_files=sorted(p for p in ROOT.rglob("*") if p.is_file() and p.name!="final-freeze-v001.json")
pins=[pin(p) for p in all_files]
save("final-freeze-v001.json",{"created_at":datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "status":"standalone_candidate_GREEN_not_admitted_or_runtime_integrated",
    "file_count":len(pins),"bytes":sum(p["bytes"] for p in pins),"files":pins,
    "UE_tests_candidate_count":3,"UE_tests_actually_run":0,"formal_runtime_binding":None,
    "full_content_unit_completed":False})
for p in pins:
    a=pin(Path(p["path"]))
    assert a["bytes"]==p["bytes"] and a["sha256"]==p["sha256"]
print(json.dumps({"files":len(pins),"bytes":sum(p["bytes"] for p in pins),
    "freeze":pin(ROOT/"final-freeze-v001.json"),"pin_mismatches":0},ensure_ascii=False))
