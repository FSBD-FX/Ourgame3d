"""D10 static story checks and abstract event model; never runs gameplay or storage."""
from collections import Counter
from copy import deepcopy
from pathlib import Path
import hashlib
import json
import re

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
counts = Counter()
errors = []


def read(p):
    return json.loads(p.read_text(encoding="utf-8-sig"))


def check(ok, group, label):
    counts[group] += 1
    if not ok:
        errors.append(f"{group}: {label}")


def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def walk(value):
    if isinstance(value, dict):
        yield value
        for v in value.values():
            yield from walk(v)
    elif isinstance(value, list):
        for v in value:
            yield from walk(v)


class StoryReference:
    """Small acceptance model, not a persistence implementation or UE subsystem."""
    def __init__(self, flow):
        self.flow=flow
        self.facts=set()
        self.seen=set()
        self.world_liberated=False
        self.current=None
        self.runs={}
        self.boss_events=set()
        self.discovery_events=set()
        self.reward_account_keys=set()
        self.ending_receipts={}
        self.first_ending=None

    def new_run(self, rid):
        if rid in self.runs:
            return self.runs[rid]
        if self.current and self.runs[self.current]["active"]:
            raise ValueError("unfinished_run")
        row={"id":rid,"active":True,"context":"recorded_echo_expedition" if self.world_liberated else "live_expedition","bosses":[],"optional":set()}
        self.runs[rid]=row; self.current=rid
        return row

    def fail(self):
        self.runs[self.current]["active"]=False

    def boss_success(self, boss, player_alive=True):
        run=self.runs[self.current]
        key=(self.current,boss)
        if key in self.boss_events:
            return "same_receipt"
        if not run["active"]:
            return "inactive"
        if not player_alive:
            self.fail(); return "death_first"
        primary=next((x for x in self.flow["main_facts"] if x["boss_id"]==boss),None)
        optional=next((x for x in self.flow["optional_boss_facts"] if x["boss_id"]==boss),None)
        if primary:
            expected=self.flow["main_facts"][len(run["bosses"])]["boss_id"]
            if boss!=expected:
                return "current_run_route_incomplete"
            run["bosses"].append(boss)
            self.facts.add(primary["id"])
        elif optional:
            run["optional"].add(boss)
            self.facts.add(optional["id"])
        else:
            return "unknown_boss"
        self.boss_events.add(key)
        self.reward_account_keys.add(("existing_first_Boss",boss))
        if boss==self.flow["main_facts"][-1]["boss_id"]:
            self.world_liberated=True
            receipt={"RunID":self.current,"EndingID":self.flow["ending"]["id"],"context":run["context"],"side_ids":sorted(i for i in self.facts if i.startswith("STORY-S"))}
            self.ending_receipts[self.current]=receipt
            if self.first_ending is None:
                self.first_ending=deepcopy(receipt)
            run["active"]=False
        return "committed"

    def discover(self, sid, actual_interaction=True, safe=True, alive=True):
        x=next(x for x in self.flow["side_facts"] if x["id"]==sid)
        run=self.runs[self.current]
        if not alive or not safe or not actual_interaction or not run["active"]:
            return "rejected"
        optional=next((o for o in self.flow["optional_boss_facts"] if o["node_id"]==x["node_id"]),None)
        if optional and optional["boss_id"] not in run["optional"]:
            return "uncleared_optional_encounter"
        if x["discovery_id"] in self.discovery_events:
            return "same_receipt"
        self.discovery_events.add(x["discovery_id"])
        self.reward_account_keys.add(("existing_discovery",x["discovery_id"]))
        self.facts.add(sid)
        return "committed"

    def view(self, id):
        self.seen.add(id)


def main():
    world=read(HERE/"world-and-story.json")
    flow=read(HERE/"story-flow.json")
    regions=read(HERE/"region-story.json")
    npc=read(HERE/"npcs-and-dialogue.json")
    cases=read(HERE/"story-cases.json")
    index=read(HERE/"design-index.json")
    oldregions=read(ROOT/"docs/design/dungeon-v1/regions-and-routes.json")["regions"]
    oldbosses=read(ROOT/"docs/design/bosses-v1/bosses.json")["bosses"]
    oldenemies=read(ROOT/"docs/design/enemies-v1/enemies.json")["enemies"]
    oldfac=read(ROOT/"docs/design/economy-v1/facilities.json")["facilities"]
    rewards=read(ROOT/"docs/design/economy-v1/reward-sources.json")
    source_by_id={x["id"]:x for x in rewards["sources"]}
    boss_by_id={x["id"]:x for x in oldbosses}
    node_ids={n["id"] for r in oldregions for n in r["nodes"]}
    for obj in [world,flow,regions,npc,cases,index]:
        check(obj["module"]=="D-10" and obj["source_event"]=="EV-028", "metadata", "D10 EV028")
        check(obj["status"]=="design_only" and obj["runtime_implemented"] is False, "metadata", "design only")
    for x,r in zip(flow["main_facts"],oldregions):
        check(x["region_id"]==r["id"] and x["boss_id"]==r["mainline_boss_id"] and x["node_id"]==r["boss_node_id"], "main", x["id"]+" order")
        check(not x["requires_dialogue_or_collectible"] and x["required_currency"]==0, "main", x["id"]+" free automatic")
    success_key=read(ROOT/"docs/design/bosses-v1/common-rules.json")["settlement"]["key"]
    for x in flow["main_facts"]+flow["optional_boss_facts"]:
        check(x["event_key"]==success_key and x["event"]=="existing_qualifying_Boss_success_commit", "main", x["id"]+" same existing success transaction")
    check(flow["ending"]["success_event_key_fields"]==success_key,"ending","same success key")
    check(len(flow["main_facts"])==5 and len(flow["side_facts"])==5 and len(flow["optional_boss_facts"])==2, "main", "5+5+2 facts")
    story_ids=[x["id"] for group in ["main_facts","side_facts","optional_boss_facts"] for x in flow[group]]
    check(len(story_ids)==len(set(story_ids)), "main", "unique story IDs")
    for x in flow["side_facts"]:
        original=source_by_id[x["reward_source_id"]]
        check(x["discovery_id"]==original["discovery_id"] and original["node_ids"]==[x["node_id"]],"discovery",x["id"]+" original source")
        check(x["additional_shards"]==0 and not x["required_for_mainline_or_normal_ending"],"discovery",x["id"]+" no new reward or gate")
        check(x["interaction_seconds"]==.25 and "full_D04_safety" in x["requires"],"discovery",x["id"]+" explicit action")
        check(not x["entry_fee_or_arrival_or_map_reveal_or_Boss_kill_is_discovery"],"discovery",x["id"]+" actual discovery")
    end=flow["ending"]
    check(end["requires_gold"]==0 and end["requires_talent_ranks"]==0 and end["requires_research_count"]==0 and not end["requires_hidden_facts"] and not end["requires_optional_Bosses"],"ending","base ending no meta/optional gates")
    check(end["normal_ending_count"]==1 and not end["extra_reward"] and end["automatic_before_run_end"],"ending","one automatic ending no new reward")
    check(not world["repeat_contract"]["world_time_rewinds"] and not world["repeat_contract"]["within_same_run_cleared_rooms_respawn"],"repeat","no rewind or same-run respawn")
    check(set(world["repeat_contract"]["gate_carriers"])=={x["boss_id"] for x in flow["main_facts"][:-1]},"repeat","four pre-victory carriers")
    # Cross-reference every actual structured ID mention in the new documents.
    allowed_boss=set(boss_by_id)
    allowed_enemies={x["id"] for x in oldenemies}
    allowed_fac={x["id"] for x in oldfac}
    for label,obj in [("world",world),("flow",flow),("regions",regions),("NPC",npc)]:
        text=json.dumps(obj,ensure_ascii=False)
        for id in set(re.findall(r"BOS-[A-Z]{3}-\d{3}",text)):
            check(id in allowed_boss,"references",label+id)
        for id in set(re.findall(r"ENM-[A-Z]{3}-\d{3}",text)):
            check(id in allowed_enemies,"references",label+id)
        for id in set(re.findall(r"REG-\d{2}-[NBH]\d{2}",text)):
            check(id in node_ids,"references",label+id)
        for id in set(re.findall(r"FAC-[A-Z]+(?:-[A-Z]+)*",text)):
            check(id in allowed_fac,"references",label+id)
    checks_schema(regions,npc,oldregions,oldenemies,allowed_fac)
    m=StoryReference(flow)
    m.new_run("run1")
    m.boss_success(flow["main_facts"][0]["boss_id"])
    check("STORY-M01" in m.facts,"event_model","first chapter recorded")
    m.fail(); m.new_run("run2")
    check("STORY-M01" in m.facts and not m.runs["run2"]["bosses"],"event_model","account knowledge not run success")
    check(m.boss_success(flow["main_facts"][1]["boss_id"])=="current_run_route_incomplete","event_model","cannot skip new-run first Boss")
    for x in flow["main_facts"]:
        check(m.boss_success(x["boss_id"])=="committed","event_model","zero optional route "+x["id"])
    check(m.world_liberated and m.first_ending["side_ids"]==[],"event_model","base ending with no side discoveries")
    first=deepcopy(m.first_ending)
    rewarded=set(m.reward_account_keys);facts=set(m.facts)
    m.view("END-OPEN-GATE");m.view("STORY-M05")
    check(m.reward_account_keys==rewarded and m.facts==facts,"event_model","read/skip no fact/reward mutation")
    check(m.boss_success(flow["main_facts"][-1]["boss_id"])=="same_receipt" and m.reward_account_keys==rewarded,"event_model","repeated success no duplicate")
    m.new_run("echo1")
    check(m.runs["echo1"]["context"]=="recorded_echo_expedition","event_model","new echo context")
    for args in [dict(actual_interaction=False),dict(safe=False),dict(alive=False)]:
        before=deepcopy((m.facts,m.discovery_events,m.reward_account_keys))
        check(m.discover("STORY-S04",**args)=="rejected" and before==(m.facts,m.discovery_events,m.reward_account_keys),"event_model","entry/unsafe/dead not discovery")
    check(m.discover("STORY-S01")=="uncleared_optional_encounter","event_model","optional Boss first safety")
    m.boss_success("BOS-GOB-001")
    check("STORY-O01" in m.facts and "STORY-S01" not in m.facts,"event_model","Boss and discovery separated")
    m.discover("STORY-S01"); m.discover("STORY-S04")
    before=set(m.reward_account_keys)
    check(m.discover("STORY-S04")=="same_receipt" and before==m.reward_account_keys,"event_model","discovery once")
    for x in flow["main_facts"]:
        m.boss_success(x["boss_id"])
    check(m.first_ending==first and m.ending_receipts["echo1"]["side_ids"]==["STORY-S01","STORY-S04"],"event_model","later inserts do not rewrite first ending")
    m.new_run("echo2"); context=m.runs["echo2"]["context"]
    check(m.new_run("echo2")["context"]==context and not m.runs["echo2"]["bosses"],"event_model","resume same context no success initialization")
    m.fail(); check(m.world_liberated,"event_model","echo failure never reimprisons world")
    tied=StoryReference(flow);tied.new_run("tied")
    for x in flow["main_facts"][:-1]: tied.boss_success(x["boss_id"])
    before=set(tied.reward_account_keys)
    check(tied.boss_success(flow["main_facts"][-1]["boss_id"],False)=="death_first" and not tied.world_liberated and "STORY-M05" not in tied.facts and tied.first_ending is None and tied.reward_account_keys==before,"event_model","same-time final double death")
    check(len(tied.facts)==4,"event_model","old committed facts survive failure")
    historical=index["historical_design_sha256"]
    for path,h in historical.items():
        check((ROOT/path).exists() and digest(ROOT/path)==h,"preservation",path)
    current=[ROOT/"世界观NPC与叙事设计.md",*sorted(p for p in HERE.iterdir() if p.suffix in [".md",".json",".py"] and p.name!="validation-report.json")]
    for p in [*filter(lambda p:p.suffix==".md",current),ROOT/"README.md",ROOT/"整体设计清单与推进顺序.md",ROOT/"项目需求台账.md"]:
        for link in re.findall(r"\]\(([^\s)]+)\)",p.read_text(encoding="utf-8-sig")):
            if "://" in link or link.startswith("#"):continue
            target=(p.parent/link.split("#")[0]).resolve()
            check(target.exists() or target==HERE/"validation-report.json","links",p.name+":"+link)
    report={"design_date":"2026-10-14","source_event":"EV-028","module":"D-10","status":"design_only","runtime_implemented":False,"checks":sum(counts.values()),"checks_by_group":dict(counts),"errors":errors,"counts":{"regions":5,"enemy_families":9,"narrative_factions":len(regions["factions"]),"existing_Bosses":7,"NPCs":len(npc["npcs"]),"dialogues":len(npc["dialogues"]),"main_facts":5,"side_facts":5,"normal_endings":1,"optional_text_inserts":5,"documented_future_cases":len(cases["cases"])},"scope":"reference integrity and abstract narrative event invariants; production storage, UI and gameplay not run","historical_design_sha256":historical,"current_design_sha256":{p.relative_to(ROOT).as_posix():digest(p) for p in current},"cross_review_resolved":["same D06 Boss success event key for main optional and ending","final double-death carrier reconstruction with no additional gameplay gate","legacy final success projects both M05 and liberation; unknown old inserts not invented","sample quote distinguishes successful purchase from selecting an unbought order"],"limitations":["abstract model assumes legal current-room callbacks; does not validate navigation/AI/actual save atomicity","not all documented future cases are executable tests","story coherence also manually reviewed, not proven by counts","no images/voice/engine changes or playtest"],"reproduce":"python -X utf8 docs/design/narrative-v1/validate_design.py"}
    (HERE/"validation-report.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"checks":report["checks"],"errors":errors,"counts":report["counts"]},ensure_ascii=False))
    raise SystemExit(bool(errors))


def checks_schema(regions,npc,oldregions,oldenemies,allowed_fac):
    family_set={e["family"] for e in oldenemies}
    mapped=regions["enemy_family_story"]
    check(len(mapped)==9 and {x["family"] for x in mapped}==family_set,"region_schema","all9 original families")
    faction_by_id={x["id"]:x for x in regions["factions"]}
    check(len(faction_by_id)==len(regions["factions"])==6,"region_schema","6 unique narrative factions")
    for x in mapped:
        check(x["faction_id"] in faction_by_id and x["family"] in faction_by_id[x["faction_id"]]["families"],"region_schema",x["family"]+" family relation")
        check(bool(x["origin"]) and bool(x["motivation"]) and bool(x["distinction"]),"region_schema",x["family"]+" distinct role")
    check(len(regions["regions"])==5,"region_schema","5 regions")
    for x,old in zip(regions["regions"],oldregions):
        check(all(x[k]==old[k] for k in ["id","name","order","mainline_boss_id","mainline_boss_name"]),"region_schema",x["id"]+" preserve old names/order")
        check(x["story_fact_id"]=="STORY-"+x["milestone_id"],"region_schema",x["id"]+" canonical story ID")
    check(len(regions["hidden_nodes"])==5,"region_schema","5 original hidden nodes")
    for i,h in enumerate(regions["hidden_nodes"],1):
        node=f"REG-{i:02d}-H01"
        old=next(n for n in oldregions[i-1]["nodes"] if n["id"]==node)
        a=h["actual_discovery_interaction"]
        check(h["id"]==node and h["name"]==old["label"] and h["boss_id"]==old["boss_id"],"region_schema",node+" original node")
        check(h["story_fact_id"]==f"STORY-S{i:02d}" and a["discovery_id"]==f"DISC-{node}-CORE" and a["existing_reward_source_id"]==f"RWD-DISCOVERY-{node}","region_schema",node+" canonical discovery")
        check(h["entry_price_gold_inherited_D08"]==[20,0,0,35,0][i-1] and h["return_price_gold"]==0,"region_schema",node+" inherited fees")
        check(a["duration_s"]==.25 and a["new_additional_story_shards"]==0 and a["existing_first_discovery_shards"]==2 and not a["entry_fee_map_reveal_arrival_or_Boss_death_counts_as_discovery"],"region_schema",node+" no new reward")
        check(not h["epilogue_tag_is_new_reward_or_ending_gate"] and not h["new_map_node"] and not h["new_reward_source"],"region_schema",node+" optional text only")
    people={x["id"]:x for x in npc["npcs"]}
    lines={x["id"]:x for x in npc["dialogues"]}
    check(len(people)==len(npc["npcs"])==5,"NPC_schema","5 unique NPCs")
    check(len(lines)==len(npc["dialogues"])==62,"NPC_schema","62 unique lines")
    owners=Counter(f for x in people.values() for f in x["service_facility_ids"])
    check(set(owners)==allowed_fac and all(c==1 for c in owners.values()),"NPC_schema","9 old facilities each one owner")
    for x in people.values():
        check(x["available_from_start"] and not x["rescue_friendship_or_Boss_service_gate"],"NPC_schema",x["id"]+" no story service lock")
        check(not x["representation"]["combat_actor"] and not x["representation"]["damageable"] and not x["representation"]["collision_blocks_free_route"],"NPC_schema",x["id"]+" no new combat actor")
        for id in list(x["core_dialogue_ids"].values())+x["specific_service_dialogue_ids"]:
            check(id in lines and lines[id]["speaker_id"]==x["id"],"NPC_schema",id+" owner")
        for i,reaction in enumerate(x["five_milestone_reactions"],1):
            check(reaction["story_fact_id"]==f"STORY-M{i:02d}" and reaction["Boss_id"]==oldregions[i-1]["mainline_boss_id"],"NPC_schema",reaction["dialogue_id"]+" canonical phase")
        check(all(y["other_npc_id"] in people for y in x["relationships"]),"NPC_schema",x["id"]+" existing cast only")
    for x in lines.values():
        check(x["speaker_id"] in people and bool(x["text_zh"]) and x["skippable"] and not x["reward_mutations"] and not x["gameplay_or_success_flag_mutations"],"dialogue",x["id"]+" text no rewards")
    fac={x["id"]:x for x in read(ROOT/"docs/design/economy-v1/facilities.json")["facilities"]}
    cards={x["id"]:x for x in npc["service_fact_cards"]}
    for cid,fid in [("CARD-CHOICE","FAC-CHOICE-WHEEL"),("CARD-ROULETTE","FAC-ROULETTE")]:
        card=cards[cid]["facts"]
        check(all(card[k]==fac[fid][k] for k in ["price_gold","per_instance_uses","nodes"]),"service_facts",cid+" price count location")
    check([x["probability"] for x in cards["CARD-ROULETTE"]["facts"]["outcomes"]]==[x["probability"] for x in fac["FAC-ROULETTE"]["outcomes"]],"service_facts","roulette probabilities")
    forge=cards["CARD-FORGE"]["facts"]
    check(forge["step_prices_gold"]==fac["FAC-FORGE"]["step_prices_gold"] and forge["max_grade_by_chapter"]==fac["FAC-FORGE"]["max_grade_by_chapter"],"service_facts","forge prices and caps")
    v2=read(ROOT/"docs/design/equipment-v2/enchant-rules.json")
    c=cards["CARD-ENCHANT"]["facts"]
    check(c["awaken_price_gold"]==v2["operations"]["awaken"]["cost_gold"] and c["awaken_package_probabilities"]==v2["package_weights"],"service_facts","awakening price weights")
    for op,ck,oldkey in [("upgrade","upgrade_cost_by_from_tier","cost_gold_by_from_tier"),("reroll","reroll_cost_by_tier","cost_gold_by_tier"),("cleanse","cleanse_cost_by_tier","cost_gold_by_tier")]:
        check(c[ck]==list(v2["operations"][op][oldkey].values()),"service_facts",op+" original costs")


if __name__=="__main__":
    main()
