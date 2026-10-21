"""D-08 source/reference and paper arithmetic checks; never runs UE gameplay."""
from pathlib import Path
from collections import Counter
from fractions import Fraction
from itertools import product
import hashlib
import json
import math
import re

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
checks = Counter()
errors = []


def check(condition, group, message):
    checks[group] += 1
    if not condition:
        errors.append(f"{group}: {message}")


def close(a, b):
    return math.isclose(a, b, abs_tol=1e-9)


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def allocate(budget, weights):
    """Independent exact-fraction model of whole-room integer apportionment."""
    total = sum(weights.values())
    exact = {k: Fraction(budget * w, total) for k, w in weights.items()}
    result = {k: v.numerator // v.denominator for k, v in exact.items()}
    order = sorted(weights, key=lambda k: (-(exact[k] - result[k]), k))
    for k in order[:budget - sum(result.values())]:
        result[k] += 1
    return result


def main():
    common = read(HERE / "common-rules.json")
    growth = read(HERE / "equipment-growth.json")
    facilities = read(HERE / "facilities.json")
    rewards = read(HERE / "reward-sources.json")
    budgets = read(HERE / "budget-scenarios.json")
    v2 = read(ROOT / "docs/design/equipment-v2/enchant-rules.json")
    weapons = read(ROOT / "docs/design/equipment-v1/weapons.json")
    armor = read(ROOT / "docs/design/equipment-v1/armor.json")
    items = read(ROOT / "docs/design/items-v1/items.json")["items"]
    routes = read(ROOT / "docs/design/dungeon-v1/regions-and-routes.json")
    bosses = read(ROOT / "docs/design/bosses-v1/bosses.json")["bosses"]
    equipment = {e["id"]: e for e in weapons + armor}
    item_ids = {i["id"] for i in items}
    item_map = {i["id"]: i for i in items}
    boss_ids = {i["id"] for i in bosses}
    node_ids = {n["id"] for r in routes["regions"] for n in r["nodes"]}
    for obj in [common, growth, facilities, rewards, budgets]:
        check(obj["module"] == "D-08" and obj["source_event"] == "EV-026", "metadata", "module/event")
        check(obj["runtime_implemented"] is False and obj["status"] == "design_only", "metadata", "design-only scope")
    check(len(growth["grades"]) == 4 and len(growth["equipment_applicability"]) == 45, "growth", "grades/45 templates")
    check("basic_upgrade_grade" in growth["instance_fields"]["stored"] and "basic_grade" not in growth["instance_fields"]["stored"], "growth", "single canonical stored grade")
    check({x["content_id"] for x in growth["equipment_applicability"]} == set(equipment), "growth", "same original equipment universe")
    step = growth["basic_upgrade"]["cost_gold_by_from_grade"]
    check([step[str(i)] for i in range(3)] == [30, 55, 85], "growth", "step costs")
    check(sum(step.values()) == 170, "growth", "full base forge cost")
    for profile in growth["chapter_profiles"]:
        c = profile["chapter"] - 1
        w = profile["natural_grade_weights"]
        check(close(sum(w.values()), 1), "probability", f"grade chapter {c+1}")
        check(profile["workshop_grade_cap"] == [1,1,2,2,3][c], "growth", "chapter forge cap")
        check(profile["natural_drop_grade_cap"] == [0,1,1,2,2][c], "growth", "chapter natural cap")
        check(all(v == 0 for k,v in w.items() if int(k) > profile["natural_drop_grade_cap"]), "growth", "grade above natural cap has no weight")
        check(profile["enchant_tier_weights"] == v2["tier_pools"][profile["enchant_tier_pool"]], "v2", "tier pool unchanged")
    enchant = growth["enchant_compatibility"]
    check(enchant["spawn_enchanted_chance"] == v2["spawn_enchant_chance"], "v2", "enchant chance")
    check(enchant["package_weights_conditional"] == v2["package_weights"], "v2", "package probabilities")
    check(enchant["operations"] == v2["operations"], "v2", "all four operation definitions")
    for record in growth["equipment_applicability"]:
        original = equipment[record["content_id"]]
        check(record["old_acquisition_suggestion"] == original["acquisition"], "growth", "old acquisition retained")
        check(record["grades_allowed"] == [0,1,2,3], "growth", "all grades applicable")
    for e in growth["paper_examples"]:
        kind = e["kind"]
        if kind == "weapon_formula":
            s = max(-30, min(50, e["other_damage_pct"] + e["growth_damage_pct"]))
            check(close(e["base_segment"]*(1+s/100),e["direct_before_crit_mitigation_vulnerability"]), "paper", e["id"])
        elif kind == "armor_formula":
            for key in ["armor", "ward"]:
                base = e[f"intrinsic_{key}"]
                final = min(150, max(0, base + base*.05*e["grade"] + e[f"other_{key}_flat"]))
                check(close(final, e[f"final_{key}"]), "paper", e["id"]+key)
        elif kind == "probability":
            check(close(e["joint_probability"],e["grade_probability"]*e["package_unconditional_probability"]), "paper", e["id"])
    # Exercise the formula boundary over every existing template and all four grades.
    for weapon, grade, extra in product(weapons, range(4), [-40,0,25,50]):
        total = max(-30,min(50,extra+5*grade))
        damage = weapon["damage_total"]*(1+total/100)
        check(weapon["damage_total"]*.7-1e-9 <= damage <= weapon["damage_total"]*1.5+1e-9, "caps", weapon["id"])
    for a, grade in product(armor, range(4)):
        for k in ["armor", "ward"]:
            final = min(150, a[k]+a[k]*.05*grade)
            check(0<=final<=150 and min(.6,final/(100+final))<=.6, "caps", a["id"]+k)
    source_ids = [x["id"] for x in rewards["sources"]]
    check(len(source_ids) == len(set(source_ids)) == rewards["source_count"], "sources", "unique source IDs")
    for source in rewards["sources"]:
        check(set(source["node_ids"]) <= node_ids, "sources", source["id"]+" node refs")
        check(0<=source["probability"]<=1 and source["quantity"]>=0, "sources", source["id"]+" amount/chance")
        if "pool_id" in source:
            check(source["pool_id"] in rewards["pools"], "sources", source["id"]+" pool")
        if "boss_id" in source:
            check(source["boss_id"] in boss_ids, "sources", source["id"]+" boss")
    for filename, obj in [("growth",growth),("facilities",facilities),("rewards",rewards)]:
        text = json.dumps(obj,ensure_ascii=False)
        for id_ in set(re.findall(r"ITM-[A-Z]{3}-\d{3}",text)):
            check(id_ in item_ids, "refs", filename+":"+id_)
        for id_ in set(re.findall(r"(?:WPN|ARM)-[A-Z]{3}-\d{3}",text)):
            check(id_ in equipment, "refs", filename+":"+id_)
    pool = rewards["pools"]["POOL-EQUIPMENT"]
    all_pool_equipment = {id_ for group in ["weapon_families","armor_classes"] for ids in pool[group].values() for id_ in ids}
    check(all_pool_equipment == set(equipment), "sources", "all45 reachable in equipment pool")
    check(len(pool["weapon_families"])==11 and len(pool["armor_classes"])==4, "sources", "family groups")
    check(all(len(v)==3 for group in ["weapon_families","armor_classes"] for v in pool[group].values()), "sources", "3 per family")
    check(close(33*(2/99)+12*(1/36),1), "probability", "equipment normalized")
    bonus = rewards["pools"]["POOL-BONUS-ITEM"]
    check(bonus["conditional_on_source_presence"] is True and bonus["does_presence_roll"] is False and "trigger_probability" not in bonus, "probability", "conditional bonus pool does not repeat presence roll")
    bonus_sources=[s for s in rewards["sources"] if s.get("pool_id")=="POOL-BONUS-ITEM"]
    check(len(bonus_sources)==20 and all(s["probability"]==.15 and s["presence_roll_owner"]=="source_once_per_whole_room" for s in bonus_sources), "probability", "15% source-owned once for15 main plus5 mutually exclusive branch source groups")
    check(sum(bonus["category_weights"].values())==100, "probability", "bonus categories")
    check(sum(bonus["no_matched_FUN_effective_category_weights"].values())==100, "probability", "FUN fallback weights")
    for cat, groups in bonus["purpose_groups"].items():
        check(sum(x["weight"] for x in groups)==100, "probability", cat+" purpose weight")
        check(any(item_map[id_]["unlock"]=="base_pool" for x in groups for id_ in x["item_ids"]), "sources", cat+" nonempty base pool")
    reachable_items = {id_ for ids in bonus["eligible_item_ids_by_category"].values() for id_ in ids}
    reachable_items |= {id_ for g in rewards["pools"]["POOL-RELIC"]["purpose_groups"] for id_ in g["item_ids"]}
    check(reachable_items == item_ids, "sources", "all36 have declared conditional source")
    b = rewards["currency_budget"]
    calculated_chapters = [sum(values[i] for values in b["mainline_room_gold"].values()) for i in range(5)]
    check(calculated_chapters==b["mainline_gold_by_chapter_excluding_start"], "budget", "chapter gold")
    check(sum(calculated_chapters)+b["new_run_gold"]==700==b["mainline_gross_all_pickup_total"], "budget", "main gold700")
    check(sum(b["mainline_N05_ground_fragments"])+sum(b["mainline_boss_automatic_fragments"])==60, "budget", "main shards60")
    check(sum(b["optional_choice_gold_by_chapter"])+sum(b["optional_boss_gold"])==220, "budget", "optional gross220")
    check(700+220-sum(b["known_hidden_entry_fees"].values())==865, "budget", "gross minus tolls")
    check(60+sum(b["optional_choice_ground_fragments_by_chapter"])+sum(b["optional_boss_fragments"])==78, "budget", "repeat all fragments78")
    check(78+7*2+5*2==102, "budget", "all firsts102")
    # Main-room sources must sum once; never multiply totals by the enemy/wave count.
    main_gold = sum(x["quantity"] for x in rewards["sources"] if x["id"]=="RWD-RUN-START-GOLD" or re.fullmatch(r"RWD-REG-\d{2}-N0[235]-GOLD",x["id"]))
    check(main_gold==480, "budget", "start plus 15 room sources")
    allocation_examples=[]
    for e in rewards["paper_examples"]:
        if "slot_threat_weights" in e:
            result=allocate(e["room_gold_budget"],e["slot_threat_weights"])
            check(result==e["allocation"], "allocation", e["id"])
            check(sum(result.values())==e["room_gold_budget"], "allocation", "conservation")
            check(allocate(e["room_gold_budget"],dict(reversed(list(e["slot_threat_weights"].items()))))==result, "allocation", "input ordering independence")
            allocation_examples.append({"id":e["id"],"computed":result})
    for amount in [0,1,8,20,24,52,56]:
        for weights in [{"s1":1},{"s1":2,"s2":2,"s3":3,"s4":2,"s5":4,"s6":2}]:
            r=allocate(amount,weights)
            check(sum(r.values())==amount and all(isinstance(x,int) and x>=0 for x in r.values()), "allocation", f"budget{amount}")
    fac = {f["id"]: f for f in facilities["facilities"]}
    check(len(fac)==9, "facilities", "9 facility groups")
    fixed_potions=0
    offers=[]
    for f in fac.values():
        check(set(f["nodes"])<=node_ids and not f["mainline_purchase_required"], "facilities", f["id"]+" free main")
        for instance in f.get("instances",[]):
            check(instance["node_id"] in node_ids and not instance["restock"], "facilities", instance["instance_id"])
            for offer in instance["offers"]:
                offers.append(offer)
                id_=offer["content_id"]
                check(id_ in item_ids|set(equipment), "facilities", offer["offer_id"])
                check(offer["stock_purchases"]==1 and offer["price_gold"]>0, "facilities", "finite price/stock")
                if id_=="ITM-REC-001":
                    fixed_potions+=offer["quantity"]
                    check(offer["price_gold"]==18, "facilities", "small potion price")
                if "basic_upgrade_grade" in offer:
                    grade=offer["basic_upgrade_grade"]
                    expected=(32 if offer["kind"]=="weapon" else 28)+math.ceil([0,30,85,170][grade]*.5)
                    check(offer["price_gold"]==expected, "facilities", "equipment price")
                    expected_pool=["early","middle","middle","advanced","advanced"][instance["chapter"]-1]
                    check(offer["equipment_generation"]["enchant_tier_pool"]==expected_pool, "facilities", "shop chapter pool matches D08 current chapter")
    check(fixed_potions==10 and len(offers)==55, "facilities", "55 offers and10 small potions")
    roulette=fac["FAC-ROULETTE"]
    check(sum(x["weight"] for x in roulette["outcomes"])==100, "probability", "wheel weight100")
    drawn=[]
    egold=eref=0
    for o in roulette["outcomes"]:
        drawn.extend(range(o["roll_min_inclusive"],o["roll_max_inclusive"]+1))
        check(o["roll_max_inclusive"]-o["roll_min_inclusive"]+1==o["weight"], "probability", o["id"])
        p=o["weight"]/100
        check(close(p,o["probability"]), "probability", o["id"]+"chance")
        if o["result"]["kind"]=="gold":egold+=p*o["result"]["amount"]
        eref+=p*o["reference_price_gold"]
    check(sorted(drawn)==list(range(100)), "probability", "disjoint exhaustive wheel intervals")
    check(close(egold,4) and close(eref,13.6), "budget", "wheel cash/item price expectations")
    check(close(eref-roulette["price_gold"],-6.4) and close(egold-roulette["price_gold"],-16), "budget", "reference versus cash expectation")
    for choice in fac["FAC-CHOICE-WHEEL"]["choices"]:
        value=sum(facilities["price_table_gold"][x["content_id"]]*x["quantity"] for x in choice["contents"])
        check(value==choice["reference_price_gold"], "facilities", choice["id"]+"reference value")
    key_objects={x["id"]:x for x in rewards["optional_keyed_supply_objects"]}
    source_map={x["id"]:x for x in rewards["sources"]}
    check(len(key_objects)==2, "boxes", "two concrete optional key matches")
    key_pool=rewards["pools"]["POOL-COMMON-SUPPLY"]
    check(sum(key_pool["category_weights"].values())==100, "boxes", "box weights normalized")
    for obj in fac["FAC-INTEL-ENTRY"]["exploration_optional_objects"]:
        reference=key_objects[obj["object_id"]]
        source=source_map[obj["reward_source_id"]]
        check(reference["node_id"]==obj["node_id"] and reference["source_id"]==source["id"], "boxes", "object/node/source binding")
        check(source["delivery"]=="source_bound_common_box_result_tray", "boxes", "one source-held instance not separate ground duplicate")
        check(obj["gold_fee"]==reference["gold_fee"]==0 and obj["consume"]["quantity"]==reference["open_cost_count"]==1, "boxes", "one key no gold")
        check(obj["category_weights"]==key_pool["category_weights"] and obj["pool_id"]==source["pool_id"], "boxes", "same box pool")
        check(not obj["required_for_mainline"] and not reference["blocks_free_passage"], "boxes", "optional free bypass")
    for toll in fac["FAC-INTEL-ENTRY"]["entry_tolls"]:
        check(toll["price_gold"]==b["known_hidden_entry_fees"][toll["node_id"]], "facilities", "toll and reward budget agree")
    wallet_results=[]
    for scenario in budgets["ordered_wallets"]:
        check("boss_gold_pickup_assumption" in scenario and all(e["kind"]!="boss_gold" for e in scenario["events"]), "wallet", "boss success is not treated as automatic gold pickup")
        wallet=0;spent=0;gross=0;forge={"weapon":0,"armor":0}
        for event in scenario["events"]:
            amount=event["amount"];wallet+=amount
            check(wallet==event["balance"] and wallet>=0, "wallet", scenario["id"]+":"+event["node"])
            if amount>=0:gross+=amount
            else:spent-=amount
            service=event.get("service","")
            match=re.fullmatch(r"(weapon|armor)_(\d)_to_(\d)",service)
            if match:
                kind,old,new=match.groups();old=int(old);new=int(new)
                check(forge[kind]==old and new==old+1, "wallet", service+" sequential grade")
                check(new<=[1,1,2,2,3][event["chapter"]-1] and -amount==step[str(old)], "wallet", service+" chapter/cost")
                forge[kind]=new
        check(gross==scenario["gross_gold"] and spent==scenario["spent_gold"] and wallet==scenario["pre_end_balance"], "wallet", "totals")
        wallet_results.append({"id":scenario["id"],"gross":gross,"spent":spent,"pre_end_balance":wallet,"final_grades":forge})
    boundary={x["id"]:x for x in budgets["boundary_cases"]}
    check(boundary["BUD-004"]["desired_spend"]==2*170+500==840, "paper", "full upgrade competing demand")
    check(math.ceil(18*.8)==boundary["BUD-007"]["discount_final_price"], "paper", "coupon rounding")
    check(close(boundary["BUD-010"]["expected_damage_before_target_and_crit"],40*(1+(.10-.12))), "paper", "bad enchant versus grade")
    check(close(boundary["BUD-012"]["reference_minus_price"],eref-20), "paper", "root matches facility EV")
    check(list(allocate(20,{str(i):v for i,v in enumerate(boundary["BUD-013"]["stable_slot_weights"])}).values())==boundary["BUD-013"]["expected_slot_allocations"], "paper", "root matches slot allocation")
    # Preserve immutable earlier designs against the preceding module's report.
    prior=read(ROOT/"docs/design/dungeon-v1/validation-report.json")
    historical={**prior["historical_design_sha256"],**prior["current_design_sha256"]}
    for name,expected in historical.items():
        check((ROOT/name).is_file() and digest(ROOT/name)==expected,"history",name)
    index=read(HERE/"design-index.json")
    check(index["counts"]["reward_sources"]==len(source_ids) and index["counts"]["ordinary_shop_offer_rows"]==len(offers), "index", "source and offer counts")
    for name in index["sources"]+index["reading_order"]:
        check((HERE/name).exists(), "index", name)
    design_files=[ROOT/"品质掉落与局内经济设计.md"]+[p for p in sorted(HERE.iterdir()) if p.is_file() and p.name!="validation-report.json"]
    links=0
    for path in design_files+[ROOT/"README.md",ROOT/"整体设计清单与推进顺序.md",ROOT/"项目需求台账.md"]:
        if path.suffix!=".md":continue
        for raw in re.findall(r"\]\(([^)]+)\)",path.read_text(encoding="utf-8-sig")):
            target=raw.strip("<>").split("#",1)[0]
            if not target or re.match(r"(?:https?|app|skill|codex)://",target):continue
            dest=(path.parent/target).resolve()
            check(dest.exists() or dest==HERE/"validation-report.json", "links",f"{path.name}:{target}")
            links+=1
    report={
        "design_date":"2026-10-14","source_event":"EV-026","module":"D-08",
        "status":"passed" if not errors else "failed","runtime_implemented":False,
        "scope":"JSON_IDs_old_source_hashes_route_refs_probability_tables_integer_allocation_ordered_wallet_arithmetic_and_local_links_only",
        "actual_drop_distribution_gameplay_balance_or_save_atomicity_verified":False,
        "checks":sum(checks.values()),"checks_by_group":dict(checks),"errors":errors,
        "counts":{"equipment_templates":len(equipment),"base_grades":4,"facility_categories":len(fac),"ordinary_offer_rows":len(offers),"reward_sources":len(source_ids),"ordered_wallets":len(wallet_results),"root_boundary_cases":len(boundary),"growth_paper_cases":len(growth["paper_examples"]),"reward_paper_cases":len(rewards["paper_examples"]),"local_links_checked":links},
        "wallet_results":wallet_results,"allocation_results":allocation_examples,
        "cross_review_resolved":[
            "keyed boxes deliver exactly one source-bound tray instance instead of separate tray and ground copies",
            "basic_upgrade_grade is the single persisted forge field shared by stock and upgrade operations",
            "700 gold baseline and ordered wallets explicitly require actual pickup of the first four Boss ground-gold rewards",
            "15 percent bonus presence is sampled once by the source; its item pool only makes conditional selection",
            "chapter2 shop enchant pool now uses the common middle pool; REG04 hidden room is explicitly noncombat discovery with no repeat economic reward"
        ],
        "wheel_expectations":{"gross_gold":egold,"net_cash_paid_spin":egold-20,"gross_item_and_coin_list_price_reference":eref,"net_list_price_reference":eref-20,"items_not_redeemable_for_cash":True},
        "historical_design_sha256":historical,
        "current_design_sha256":{str(f.relative_to(ROOT)).replace('\\','/'):digest(f) for f in design_files},
        "reproduce":"python -X utf8 docs/design/economy-v1/validate_design.py",
        "limitations":["ordered wallets assume combat survival and stated pickup ratio; no time or survival probabilities measured","boundary case text without executable arithmetic is an acceptance proposal, not a runtime pass","real RNG frequencies, player valuation, dynamic geometry, save recovery, and economic balance require later implementation and playtests"]
    }
    (HERE/"validation-report.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({k:report[k] for k in ["status","checks","counts","errors","wallet_results"]},ensure_ascii=False))
    return bool(errors)


if __name__=="__main__":
    raise SystemExit(main())
