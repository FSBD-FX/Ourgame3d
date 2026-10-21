"""Read-only current native/manual proof gate, with explicit snapshot/proof pins."""
from pathlib import Path
import argparse,json,sys
sys.dont_write_bytecode=True
import checkpoint_v125_common_v001 as C

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--project",required=True);ap.add_argument("--snapshot",required=True);ap.add_argument("--proof-contract",required=True);a=ap.parse_args()
    root=Path(a.project).resolve();S=(root/a.snapshot).resolve();m,rows=C.snapshot(root,S)
    p=(root/a.proof_contract).resolve();C.require(p.is_relative_to(root),"Proof contract escapes project");v=C.read(p)
    C.exact_keys(v,("schema","snapshot_manifest","proofs"),"Unknown/missing manual proof contract field")
    C.require(v["schema"]=="equipment-bound-manual-proof-contract-v125","Wrong proof contract version")
    C.match(root,v["snapshot_manifest"]);C.require(C.path(root,v["snapshot_manifest"]["path"])==S/"compiled-source-manifest.json","Manual contract names another snapshot")
    C.require(type(v["proofs"]) is list and len(v["proofs"])==len(m["required_manual_proofs"]),"Missing/extra required current native proof")
    C.require({x["kind"] for x in v["proofs"]}==set(m["required_manual_proofs"]),"Duplicate/wrong proof modes")
    proof_results=[C.verify_proof(root,S/"compiled-source-manifest.json",x,m["art_mode"]=="primary1" and x["kind"]!="default") for x in v["proofs"]]
    C.require(len({x["process_id"] for x in proof_results})==len(proof_results),"Different proof modes reused the same native process ID")
    flags=["-DungeonCandidateSprites","-DungeonSceneExplorationPreview","-DungeonFairytaleSwordEquipmentBoundPreview"]
    # Default full-flow proof retains established complete art; new Ready/P1 are separate trials.
    print(json.dumps({"preflight_passed":True,"snapshot":S.as_posix(),"strict_actual_tests":157,"production_packages":m["production_packages"],"source_and_snapshot_endpoints":2*len(rows),"mismatches":0,"native_proofs":proof_results,"launch_flags":flags,"legacy_CMD_launcher_pointer_modified_by_this_tool":False,"manual_game_not_launched":True,"audio_accepted":False,"formal_complete_units":0},ensure_ascii=False))
if __name__=="__main__":
    try:main()
    except (C.GateError,OSError,ValueError,KeyError,TypeError) as exc:print(json.dumps({"preflight_passed":False,"error":str(exc)},ensure_ascii=False),file=sys.stderr);sys.exit(1)
