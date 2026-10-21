from pathlib import Path
import difflib,hashlib,json
HERE=Path(__file__).resolve().parent
ROOT=Path("F:/Ourgame")
BASE=HERE/"baseline-source"
OUT=HERE/"stage0-source"
header=(BASE/"DungeonFighter.h").read_text(encoding="utf-8-sig")
header=header.replace('#include "DungeonFighterSnapshot.h"','#include "DungeonFighterSnapshot.h"\n#include "DungeonCompletedGroundMotion.h"')
needle='    bool CaptureOwnerSnapshot(FDungeonFighterOwnerSnapshot& Out, FString& Diagnostic,'
assert needle in header
header=header.replace(needle,'    bool QueryCompletedGroundMotion(FDungeonCompletedGroundMotion& Out) const;\n'+needle)
cpp=(BASE/"DungeonFighter.cpp").read_text(encoding="utf-8-sig")
needle='void ADungeonFighter::MoveOnGround(FVector2D Direction, float DeltaSeconds)'
assert needle in cpp
cpp=cpp.replace(needle,'bool ADungeonFighter::QueryCompletedGroundMotion(FDungeonCompletedGroundMotion&) const {return false;}\n\n'+needle)
for name,text in (("DungeonFighter.h",header),("DungeonFighter.cpp",cpp)):
    with (OUT/name).open("x",encoding="utf-8",newline="\n") as stream:stream.write(text)
patch=''
for name in ("DungeonFighter.h","DungeonFighter.cpp"):
    patch+=''.join(difflib.unified_diff((BASE/name).read_text(encoding="utf-8-sig").splitlines(True),(OUT/name).read_text(encoding="utf-8").splitlines(True),
        fromfile='a/UnrealGame/Source/CodexDungeon/'+name,tofile='b/UnrealGame/Source/CodexDungeon/'+name))
with (HERE/"stage0-existing-source.patch").open("x",encoding="utf-8",newline="\n") as stream:stream.write(patch)
def pin(path):
    data=path.read_bytes();return {"path":path.relative_to(ROOT).as_posix(),"bytes":len(data),"sha256":hashlib.sha256(data).hexdigest()}
tests=HERE/"new-tests/DungeonFairytaleGroundWalkTests.cpp"
groups=["CompletedNormalMovementAndDistancePhase","RealWallBlockedAndClippedMovement","ActionsTransactionsAndSavedContinuity"]
value={"schema":"fairytale-ground-walk-stage0-freeze-v001","baseline":pin(HERE/"baseline-pins-v001.json"),"files":[pin(path) for path in sorted(OUT.iterdir())]+[pin(tests),pin(HERE/"stage0-existing-source.patch")],
    "new_test_groups":["CodexDungeon.Content.FairytaleGroundWalk."+name for name in groups],
    "expected_clean_RED_assertion_per_group":"Expected production completed-ground-motion witness after actual normal-input Tick",
    "expected_RED_failures":3,"test_bytes_must_remain_unchanged_in_production":True,"UE_UBT_compiled_or_run":False,
    "actual_Source_mutated":False,"art_profile_configured":False,"formal_complete_units":0}
with (HERE/"stage0-freeze-v001.json").open("x",encoding="utf-8",newline="\n") as stream:json.dump(value,stream,ensure_ascii=False,indent=2);stream.write("\n")
print(json.dumps({"stage0_freeze":pin(HERE/"stage0-freeze-v001.json"),"frozen_test":pin(tests),"expected_clean_RED":3},indent=2))
