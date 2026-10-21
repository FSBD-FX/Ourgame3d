"""Read-only Walk proof verifier; external measured profile and compiled snapshot required.
This independently counts actual motion, frames, held key edges and real melee actions.
"""
from pathlib import Path
import argparse,hashlib,importlib.util,json,math,struct,subprocess,sys
ROOT=Path("F:/Ourgame").resolve()
HERE=Path(__file__).resolve().parent
PHASES=["start","baseline","pickup","light_ready","left_cycle","left_release_idle","left_combo","left_after_combo_walk","turn_idle","right_cycle","right_release_idle","right_combo","right_after_combo_walk","final_idle","complete"]
def need(v,why):
    if not v:raise ValueError(why)
def pairs(rows):
    v={}
    for k,x in rows:
        need(k not in v,"Duplicate JSON key: "+k);v[k]=x
    return v
def read(p):return json.loads(Path(p).read_text(encoding="utf-8-sig"),object_pairs_hook=pairs,parse_constant=lambda x:(_ for _ in ()).throw(ValueError(x)))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def uint(v):
    need(isinstance(v,str) and v.isascii() and v.isdecimal() and str(int(v))==v and 0<=int(v)<2**64,"Noncanonical native uint");return int(v)
def finite(v):return isinstance(v,(int,float)) and not isinstance(v,bool) and math.isfinite(v)
def profile_check(p):
    need(p["configured"] is True and p["source_closure_verified"] is True,"Measured compiled Walk profile remains unconfigured")
    need(p["cycle_distance"]==80. and p["cycle_seconds"]==.498,"Expected current80world/.498profile differs")
    d=p["durations"];need(len(d)==6 and all(finite(x) and x>0 for x in d) and math.isclose(sum(d),p["cycle_seconds"],abs_tol=1e-12),"Six phase durations differ")
    need(len(p["frames"])==6,"Six measured profile frames required")
    paths=[]
    for f in p["frames"]:
        need(f["measurements_supplied"] is True,"Native measured markers absent")
        for k in ("root","grip","axis"):
            need(len(f[k])==2 and all(finite(x) for x in f[k]),"Measured marker malformed")
        need(f["axis"]!=[0,0] and all(0<=x<=512 for k in ("root","grip") for x in f[k]),"Measured marker invalid")
        for k in ("Body","BodyRest","NearArmWithoutHand","HelmetForeground","NearHand","ShoulderFar","Chest","ShoulderNear"):
            need(isinstance(f[k],str) and f[k].startswith("/Game/Production/") and "." in f[k],"Frozen production object path absent");paths.append(f[k])
    need(len(set(paths))==48,"Exactly48 unique Walk object paths required")
    return p

def source_check(manifest_path):
    path=Path(manifest_path).resolve();m=read(path);rows=m["files"]
    need(rows and m.get("mismatches",0)==0,"Compiled snapshot empty or mismatched")
    mapping={r["path"]:r for r in rows};need(len(mapping)==len(rows),"Duplicate compiled snapshot inputs")
    for row in rows:
        rel=Path(row["path"]);need(not rel.is_absolute() and ".." not in rel.parts,"Unsafe snapshot path")
        for base in (ROOT,path.parent):
            file=(base/rel).resolve();need(file.is_relative_to(base),"Snapshot escape")
            need(file.stat().st_size==row["bytes"] and sha(file)==row["sha256"],"Current/frozen compiled input differs: "+row["path"])
    for rel in ("UnrealGame/Binaries/Win64/UnrealEditor-CodexDungeon.dll","UnrealGame/Source/CodexDungeon/DungeonFairytaleWalkProbe.cpp","UnrealGame/Source/CodexDungeon/DungeonFairytaleWalkProbe.h","UnrealGame/Source/CodexDungeon/DungeonFairytaleSwordWalkDataV001.inl"):
        need(rel in mapping,"Compiled snapshot omits Walk build input: "+rel)
    frozen=read(HERE.parent/"native-code-freeze-v003.json")
    for row in frozen["files"]:
        if row["path"].endswith(("DungeonFairytaleWalkProbe.cpp","DungeonFairytaleWalkProbe.h")):
            key="UnrealGame/Source/CodexDungeon/"+Path(row["path"]).name
            need(mapping[key]["sha256"]==row["sha256"] and mapping[key]["bytes"]==row["bytes"],"Compiled probe not exact frozen candidate")
    for row in frozen["old_probe_and_tools_unchanged_pins"]:
        p=ROOT/row["path"];need(p.stat().st_size==row["bytes"] and sha(p)==row["sha256"],"Legacy bound Probe/tool changed")
    return mapping

def frame_at(phase,profile):
    end=0.
    for i,d in enumerate(profile["durations"]):
        end+=d
        if phase<end or i==5:return i

def verify(original,profile,source_rows):
    r=read(original/"runtime-report.json")
    need(r["schema"]=="fairytale-walk-native-input-flow-v1" and r["passed"] and r["flow_complete"] and r["failure"]=="","Native Walk failed")
    need(r["compiled_walk_profile"]==profile,"Native compiled profile differs from independent measured expected profile")
    need(uint(r["restart_serial"])==0 and r["game_tick_called_manually"] is False and r["wall_stop_visually_recorded"] is False and r["art_accepted"] is False and r["formal_complete_units"]==0,"Scope/restart claim differs")
    spec=importlib.util.spec_from_file_location("legacy_combo_geometry",ROOT/"tools/scripts/postprocess-leather-combo-trial-v001.py")
    legacy=importlib.util.module_from_spec(spec);spec.loader.exec_module(legacy)
    sword=str(uint(r["sword_id"]));light=str(uint(r["light_id"]));version=str(uint(r["light_version"]))
    need(sword!="0" and light!="0" and version!="0" and uint(r["source_id"])>0,"Actual SWD/LGT/source identity absent")
    events=r["normal_input_requests"];held={};downs=[]
    for e in events:
        need(type(e["down"]) is bool and e["down"] is not held.get(e["key"],False),"Unpaired normal key edge")
        held[e["key"]]=e["down"]
        if e["down"]:downs.append(e)
    need(not any(held.values()),"Normal input remains down")
    need([x["key"] for x in downs]==["Enter","E","A","J","J","J","A","D","J","J","J","D"],"Actual held movement/pickup/twoJ3 input order differs")
    obs=r["observations"];need(obs,"No actual native observations")
    masks=[0,0];distance=[0.,0.];post=[0,0];post_distance=[0.,0.];attacks={};attack_masks={};idle={x:0 for x in (3,5,8,10,13)};pending=[]
    windows={x["step"]:x for x in r["phasechecks"]};last_motion_to=-1.
    identity=(obs[0]["run"],obs[0]["owner_id"],obs[0]["sword_id"]);last_step=-1;last_wall=-1.;last_draw=0;previous=None
    for i,o in enumerate(obs):
        step=o["flow_step"];need(type(step) is int and 0<=step<15 and step>=last_step and o["flow_phase"]==PHASES[step],"Native phase rewound/unknown")
        need(finite(o["wall_offset_s"]) and o["wall_offset_s"]>last_wall and uint(o["draw_id"])>last_draw,"Native frame time/draw ID rewound")
        last_step=step;last_wall=o["wall_offset_s"];last_draw=uint(o["draw_id"])
        need((o["run"],o["owner_id"],o["sword_id"])==identity and o["sword_id"]==sword,"Run/owner/SWD instance changed")
        need(o["active"] and o["texture_ready"] and o["binding_valid"] and not o["interface_visible"] and o["text_calls"]==0,"Native resources/binding/UI failed")
        need(o["light_id"] in ("0",light),"Unexpected native armor instance")
        if step>=3:
            need(o["light_id"]==light and o["light_version"]==version and o["armor_drawn"] and o["armor_ready"] and o["instance_id"]==sword and o["weapon"],"Committed LGT/SWD continuity lost")
            need(uint(o["next_operation"])==uint(r["initial_operation"])+1 and uint(o["operations"])==uint(r["initial_operation_count"])+1,"Single real E commit cursor changed")
        if o["pending_equipment"]:
            need(step==2 and o["pending_instance_id"]==light and math.isclose(o["equipment_deadline"]-o["equipment_start"],.5,abs_tol=1e-12),"Actual E pickup deadline/target differs");pending.append(o)
        need(o["rendered_player_stack"]==o["draw_stack"],"Actual rendered player stack differs from same-draw record")
        clip=o["clip"];f=o["frame"];side=0 if o["facing"]<0 else 1
        need(o["facing"] in (-1,1) and isinstance(f,int),"Native frame/facing invalid")
        if clip=="sword_walk":
            m=o["motion"]
            need(o["supported"] and o["walk_pose"] and o["ordinary_walk_owner"] and not o["melee_active"] and not o["pending_equipment"] and o["stage"]==-1 and uint(o["action_id"])==0,"Walk conflicts with native action")
            need(all(m[k] is True for k in ("query_ok","published","grounded","ordinary_eligible","had_move_intent")) and finite(m["walk_distance"]) and m["walk_distance"]>0. and m["accepted_distance"]>=m["walk_distance"] and m["to_time"]==o["sim"] and m["to"]==o["ground"] and m["owner_id"]==o["owner_id"],"Walk lacks native completed ground motion")
            need(m["to_time"]>last_motion_to,"Duplicate completed motion witness credited");last_motion_to=m["to_time"]
            phase=o["walk_phase"];need(0<=phase<profile["cycle_seconds"] and o["cycle_distance"]==profile["cycle_distance"] and struct.pack(">d",phase).hex()==o["animation_time_bits"] and f==frame_at(phase,profile),"Walk phase/frame/native mirror differ")
            before=previous["walk_phase"] if previous and previous["clip"]=="sword_walk" else 0.
            expected=((before/profile["cycle_seconds"]+math.fmod(m["walk_distance"],profile["cycle_distance"])/profile["cycle_distance"])%1.)*profile["cycle_seconds"]
            error=abs(phase-expected);error=min(error,profile["cycle_seconds"]-error)
            need(error<2e-6,"Walk phase not backed by accepted distance (bounded float native substeps)")
            fr=profile["frames"][f];stack=[fr[k] for k in ("BodyRest","ShoulderFar","Chest","NearArmWithoutHand","ShoulderNear","HelmetForeground")]+[o["weapon"],fr["NearHand"]]
            need(o["draw_stack"]==stack and o["rendered_player_stack"]==stack and o["rendered_armor_used"] is True and o["rendered_armor_paths"]==[fr[k] for k in ("ShoulderFar","Chest","ShoulderNear")] and o["texture"]==fr["Body"] and o["root"]==fr["root"] and o["grip"]==fr["grip"],"Walk exact new7layer/SWD/profile markers differ")
            if step in (4,7,9,12):
                expected_side=0 if step in (4,7) else 1
                need(side==expected_side and o["held_A"]==(expected_side==0) and o["held_D"]==(expected_side==1)
                     and m["from_time"]>=windows[step]["sim"] and m["from"][1]==m["to"][1]
                     and (m["to"][0]<m["from"][0] if expected_side==0 else m["to"][0]>m["from"][0]),"Walk credit crosses its phase/facing/held direction/window")
            if step in (4,9):
                need(side==(0 if step==4 else 1) and o["held_A"]==(side==0) and o["held_D"]==(side==1),"Full cycle not backed by continuous correct A/D hold")
                masks[side]|=1<<f;distance[side]+=m["walk_distance"]
            if step in (7,12):post[side]+=1;post_distance[side]+=m["walk_distance"]
        elif clip.startswith("sword_primary_"):
            need(step in (6,11) and o["supported"] and o["melee_active"] and not o["walk_pose"] and o["stage"] in range(3) and f in range(6) and not o["held_A"] and not o["held_D"],"J attack overlaps Walk/input or invalid stage")
            s=o["stage"];need(side==(0 if step==6 else 1) and o["melee_attack_id"]==o["action_id"] and o["melee_weapon_id"]==sword and o["melee_stage"]==s and o["melee_facing"]==o["facing"] and o["owner_pose_frame"]==f,"Actual melee owner/action/frame differs")
            aid=uint(o["action_id"]);entry=(side,s,o["action_start"],o["active_end"],o["action_end"])
            need(aid>0 and (aid not in attacks or attacks[aid]==entry),"Actual attack identity/deadlines changed")
            attacks[aid]=entry;attack_masks[aid]=attack_masks.get(aid,0)|(1<<f)
            need(o["draw_stack"]==legacy.expected_stack(f,s) and o["texture"]==legacy.body_path("Primary"+str(s+1),f),"Primary exact matching3LGT/oldbody/SWD stack differs")
        else:
            need(clip=="sword_ready_idle" and not o["walk_pose"] and not o["ordinary_walk_owner"],"Unexpected clip/idle still marked Walk")
            if o["light_id"]==light:
                need(f in range(4) and o["draw_stack"]==legacy.expected_stack(f,-1) and o["texture"]==legacy.body_path("Ready",f),"Ready lost exact current brown leather/body/SWD stack")
            if step in idle and o["animation"]=="idle" and not o["melee_active"] and not o["pending_equipment"] and not o["held_A"] and not o["held_D"]:idle[step]+=1
        if o["light_id"]==light:
            need(o["rendered_armor_used"] is True and o["rendered_armor_paths"]==[o["draw_stack"][x] for x in (1,2,4)],"Actual three rendered brown armor paths differ")
        need(math.isclose(o["canvas_size"],legacy.CANVAS,abs_tol=1e-9) and (not o["weapon"] or math.isclose(o["weapon_scale"],.5,abs_tol=1e-12)),"Body72/canvas/sword.5 changed")
        for path in set(o["draw_stack"]+[o["texture"]]):
            need(legacy.package_file(path) in source_rows,"Drawn resource absent from exact compiled snapshot")
        previous=o
    need(pending and masks==[63,63] and all(x>=profile["cycle_distance"] for x in distance),"Actual each-facing full distance cycle/six phases absent")
    need(all(v>=3 for v in idle.values()) and all(v>=3 for v in post) and all(v>=20 for v in post_distance),"Release Idle or true post-chain Walk absent")
    need(len(attacks)==6 and all(v==63 for v in attack_masks.values()) and sorted((v[0],v[1]) for v in attacks.values())==[(side,stage) for side in range(2) for stage in range(3)],"Six unique actual attacks/all36 phase-facing combinations absent")
    for side in range(2):
        chain=sorted((v for v in attacks.values() if v[0]==side),key=lambda x:x[1])
        need(chain[1][2]==chain[0][4] and chain[2][2]==chain[1][4],"Actual three-stage chain not contiguous at original End")
    need(obs[-1]["flow_step"]==14,"No captured final completion boundary")
    return {"schema":"independent-walk-native-proof-verification-v1","passed":True,"process_id":uint(r["process_id"]),"masks_left_right":masks,"walk_distance_left_right":distance,"post_combo_walk_observations_left_right":post,"actual_unique_attacks":6,"actual_primary_phase_facing_pairs":36,"same_actual_LGT_SWD":True,"wall_stop_visually_recorded":False,"art_accepted":False,"formal_complete_units":0}

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--original");ap.add_argument("--expected-profile",required=True);ap.add_argument("--snapshot-manifest",required=True);ap.add_argument("--preflight",action="store_true");ap.add_argument("--write-receipt",action="store_true");a=ap.parse_args()
    profile=profile_check(read(a.expected_profile));rows=source_check(a.snapshot_manifest)
    if a.preflight:need(not a.write_receipt,"Preflight is read-only");print(json.dumps({"preflight_passed":True,"native_runtime_verified":False}));return
    need(a.original,"Actual native original directory required");original=Path(a.original).resolve();result=verify(original,profile,rows)
    pixels=subprocess.run([sys.executable,"-B","-X","utf8",str(HERE/"verify-native-walk-pixels-v001.py"),"--archive",str(original.parent)],capture_output=True,text=True,encoding="utf-8")
    need(pixels.returncode==0,"Native pixel CRC/FIFO/flush verification failed: "+pixels.stderr);result["pixel_verification"]=json.loads(pixels.stdout)
    source_check(a.snapshot_manifest)
    if a.write_receipt:
        with (original/"independent-walk-proof-verification-v001.json").open("x",encoding="utf-8") as f:json.dump(result,f,indent=2);f.write("\n")
    print(json.dumps(result,ensure_ascii=False))
if __name__=="__main__":main()
