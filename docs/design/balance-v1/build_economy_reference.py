"""D-14 pure reference arithmetic; no gameplay/save implementation or old-source writes.

Run from any directory. --check compares the committed audit with this reference.
All amounts/prices/route IDs are read from preserved D-03/07/08/09/10 sources.
Manual spending and damage inputs are explicit paper assumptions, not player data.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
TARGET = HERE / "economy-progression-audit.json"


def read(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8-sig"))


def sha(path: str) -> str:
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


REFS = [
    ("SRC-D01-HEAL", "整体框架与单局循环设计.md", None, "主线跨章一次当前MaxHP20%恢复，存活/治疗效率/缺血截断"),
    ("SRC-D03-POTION", "docs/design/items-v1/items.json", "/items", "ITM-REC-001基础30HP、stack3、8sCD，实际使用与过量舍弃"),
    ("SRC-D03-CAPS", "docs/design/items-v1/common-rules.json", "/stat_merge", "治疗效率[-25,25]%与最大HP60..150，不因产出绕过封顶"),
    ("SRC-D04-PICKUP", "docs/design/inventory-v1/inventory-rules.json", "/currency_pickup", "真实存活拾取才入账，结算不再加一次"),
    ("SRC-D04-EXIT", "docs/design/inventory-v1/inventory-rules.json", "/exit", "普通免费出口不要求收费交易完整安全；过场不清DoT/CD"),
    ("SRC-D07-ROUTE", "docs/design/dungeon-v1/regions-and-routes.json", "/regions", "五区35主节点、免费主路、每章只选一免费战斗支路"),
    ("SRC-D07-CONTRACT", "docs/design/dungeon-v1/regions-and-routes.json", "/route_contract", "免费通行、无必需随机钥匙/隐藏路、只有四次主线跨章恢复"),
    ("SRC-D08-BUDGET", "docs/design/economy-v1/reward-sources.json", "/currency_budget", "旧预算汇总，另从sources独立重算核对"),
    ("SRC-D08-SOURCES", "docs/design/economy-v1/reward-sources.json", "/sources", "既有金币/碎片/保证药/首次奖励来源，不新增收益"),
    ("SRC-D08-PARTITION", "docs/design/economy-v1/reward-sources.json", "/gold_partition", "全部有限manifest总金币只分一次，不按波次另发"),
    ("SRC-D08-DELIVERY", "docs/design/economy-v1/reward-sources.json", "/delivery_and_idempotency", "来源落地、领取与永久入账区别"),
    ("SRC-D08-FACILITIES", "docs/design/economy-v1/facilities.json", "/facilities", "原55报价/九设施/有限库存/轮盘次数/门票价格"),
    ("SRC-D08-GROWTH", "docs/design/economy-v1/equipment-growth.json", None, "基础强化步费、章cap与共享属性封顶"),
    ("SRC-D08-OLD-CASES", "docs/design/economy-v1/budget-scenarios.json", "/ordered_wallets", "旧BUD-001/002/003按事件重新核账；补足已持甲假设"),
    ("SRC-V2-COST", "docs/design/equipment-v2/enchant-rules.json", "/operations", "觉醒/重洗/升阶/洗净原费，不把随机投入当确定增益"),
    ("SRC-D09-TALENTS", "docs/design/progression-v1/talents.json", "/nodes", "九天赋27等级逐级实付合计280"),
    ("SRC-D09-RESEARCH", "docs/design/progression-v1/unlocks.json", "/unlocks", "14研究原价合计130及样品现金价格"),
    ("SRC-D09-HUB", "docs/design/progression-v1/hub-rules.json", "/new_run", "20金币起始一次、冻结成长/样品、继续不重置"),
    ("SRC-D09-REFUND", "docs/design/progression-v1/hub-rules.json", "/talent_reset", "原实付退款不算新earned，研究和样品已购不重置"),
    ("SRC-D09-SAMPLE", "docs/design/progression-v1/unlocks.json", "/research_sample_order", "每研究账号一次现金样品、首匹配N04，不增加主线收入"),
    ("SRC-D10-END", "docs/design/narrative-v1/story-flow.json", "/ending", "普通结局无金币/天赋/支线门槛，终局不重复奖励"),
    ("SRC-D13-COMMIT", "docs/design/save-data-v1/save-rules.json", "/single_root_authority", "账号与Run完整同代恢复，续局/故障不能复制收益"),
]


def build():
    rewards = read("docs/design/economy-v1/reward-sources.json")
    source = {x["id"]: x for x in rewards["sources"]}
    facilities = read("docs/design/economy-v1/facilities.json")
    fac = {x["id"]: x for x in facilities["facilities"]}
    routes = read("docs/design/dungeon-v1/regions-and-routes.json")
    talents = read("docs/design/progression-v1/talents.json")
    unlocks = read("docs/design/progression-v1/unlocks.json")
    enchant = read("docs/design/equipment-v2/enchant-rules.json")
    hub = read("docs/design/progression-v1/hub-rules.json")
    old = read("docs/design/economy-v1/budget-scenarios.json")
    items = read("docs/design/items-v1/items.json")
    small = next(x for x in items["items"] if x["id"] == "ITM-REC-001")
    small_heal = next(x["amount"] for x in small["effects"] if x["type"] == "heal_hp")
    assert small_heal == 30 and small["stack_max"] == 3 and small["cooldown_s"] == 8
    start_gold = hub["new_run"]["starter"]["gold"]
    main_ids = [x for r in routes["regions"] for x in r["mainline_node_ids"]]
    assert len(main_ids) == len(set(main_ids)) == 35
    assert all(e["access"] == "free" for r in routes["regions"] for e in r["edges"] if e["edge_kind"] in ("mainline_forward", "chapter_exit"))
    chapter_exits = [e for r in routes["regions"] for e in r["edges"] if e["edge_kind"] == "chapter_exit"]
    assert len(chapter_exits) == 4
    for r in routes["regions"]:
        assert len(r["mainline_node_ids"]) == 7
    shop = {x["node_id"]: x for x in fac["FAC-MERCHANT"]["instances"]}
    supply = {x["node_id"]: x for x in fac["FAC-SUPPLY"]["instances"]}
    def offer(node, content):
        stock = shop if node.endswith("N04") else supply
        return next(x for x in stock[node]["offers"] if x["content_id"] == content)
    potion_prices = [offer(f"REG-{c:02d}-{n}", "ITM-REC-001")["price_gold"] for c in range(1, 6) for n in ("N04", "N06")]
    assert potion_prices == [18] * 10
    forge = fac["FAC-FORGE"]
    armor_offer = offer("REG-02-N04", "ARM-MED-001")
    assert armor_offer["basic_upgrade_grade"] == 1 and armor_offer["price_gold"] == 43
    research = {x["id"]: x for x in unlocks["unlocks"]}
    sample = research["UNL-REC-002"]["research_sample"]
    toll = {x["node_id"]: x["price_gold"] for x in fac["FAC-INTEL-ENTRY"]["entry_tolls"]}
    rows = []
    for reg in routes["regions"]:
        c = reg["order"]
        boss = reg["mainline_boss_id"]
        golds = {n: source[f"RWD-REG-{c:02d}-{n}-GOLD"]["quantity"] for n in ("N02", "N03", "N05")}
        boss_gold = source[f"RWD-{boss}-GOLD"]["quantity"]
        ordinary_shards = source[f"RWD-REG-{c:02d}-N05-FRAG"]["quantity"]
        boss_shards = source[f"RWD-{boss}-FRAG"]["quantity"]
        first_shards = source[f"RWD-FIRST-{boss}"]["quantity"]
        rows.append({"chapter": c, "region_id": reg["id"], "mainline_node_ids": reg["mainline_node_ids"], "mainline_boss_id": boss,
                     "ordinary_ground_gold_by_node": golds, "ordinary_ground_gold": sum(golds.values()), "boss_ground_gold_if_actually_picked": boss_gold,
                     "gold_excluding_start": sum(golds.values()) + boss_gold, "ordinary_ground_shards_if_picked": ordinary_shards,
                     "boss_direct_shards_on_qualified_success": boss_shards, "first_boss_extra_if_unclaimed": first_shards,
                     "repeat_shards_if_ground_picked_and_success": ordinary_shards + boss_shards,
                     "free_small_potion_produced_at_N02": source[f"RWD-REG-{c:02d}-N02-REC"]["quantity"],
                     "paid_small_potion_stock_units": 2, "paid_small_potion_total_gold": sum(potion_prices[(c - 1)*2:c*2]),
                     "transition_after_main_Boss_count": int(c < 5)})
    ordinary_gold = sum(x["ordinary_ground_gold"] for x in rows)
    boss_gold = sum(x["boss_ground_gold_if_actually_picked"] for x in rows)
    ordinary_shards = sum(x["ordinary_ground_shards_if_picked"] for x in rows)
    boss_shards = sum(x["boss_direct_shards_on_qualified_success"] for x in rows)
    first_extra = sum(x["first_boss_extra_if_unclaimed"] for x in rows)
    gross = start_gold + ordinary_gold + boss_gold
    repeat = ordinary_shards + boss_shards
    assert (start_gold, ordinary_gold, boss_gold, gross, ordinary_shards, boss_shards, repeat, first_extra) == (20, 460, 220, 700, 20, 40, 60, 10)
    assert gross == rewards["currency_budget"]["mainline_gross_all_pickup_total"]
    assert repeat == rewards["currency_budget"]["mainline_repeat_collectible_total"]
    assert [x["gold_excluding_start"] for x in rows] == rewards["currency_budget"]["mainline_gold_by_chapter_excluding_start"]
    assert sum(x["max_rank"] for x in talents["nodes"]) == 27
    talent_total = sum(sum(x["cost_by_next_rank"]) for x in talents["nodes"])
    research_total = sum(x["cost_shards"] for x in unlocks["unlocks"])
    assert (len(talents["nodes"]), talent_total, len(unlocks["unlocks"]), research_total) == (9, 280, 14, 130)
    old_checks = []
    for x in old["ordered_wallets"]:
        balance = 0
        for ev in x["events"]:
            balance += ev["amount"]
            assert balance == ev["balance"] and balance >= 0
        old_checks.append({"scenario_id": x["id"], "ordered_balance_checks_pass": True,
                           "gross_gold": x["gross_gold"], "spent_gold": x["spent_gold"], "pre_end_balance": balance,
                           "additional_ownership_assumption": "BUD-001/BUD-002若锻造甲，必须已合法取得相应初始甲；未计购甲费用不能当成保证掉甲。" if any("armor" in e.get("service", "") for e in x["events"]) else None})

    plans = []
    for plan_id, name in [("PLAN-SUPPLY", "保守补给：十瓶固定小药"), ("PLAN-EQUIP", "装备投入：固定剑与已明价商人甲"), ("PLAN-EXPLORE", "可选探索：五支路/五隐藏加有限设施")]:
        balance = 0
        shard_repeat = 0
        shard_first = 0
        events = []
        purchases = []
        paid_potions = 0
        free_potions = 0
        def event(node, kind, gold=0, repeat_delta=0, first_delta=0, **extra):
            nonlocal balance, shard_repeat, shard_first
            before = balance
            balance += gold
            shard_repeat += repeat_delta
            shard_first += first_delta
            assert balance >= 0, (plan_id, node, kind, before, gold)
            row = {"ordinal": len(events), "node_id": node, "kind": kind, "gold_delta": gold,
                   "gold_before": before, "gold_after": balance, "repeat_shards_delta": repeat_delta,
                   "first_shards_delta": first_delta, "run_earned_shards_if_all_firsts_available": shard_repeat + shard_first}
            row.update(extra)
            events.append(row)
        def spend(node, service, price, **extra):
            event(node, "spend", -price, service_id=service, **extra)
            purchases.append({"node_id": node, "service_id": service, "gold": price, **extra})
        def buy_small(node):
            nonlocal paid_potions
            o = offer(node, "ITM-REC-001")
            spend(node, "buy_small_potion", o["price_gold"], offer_id=o["offer_id"], quantity=1)
            paid_potions += 1
        def do_forge(node, target, from_grade, to_grade):
            c = int(node[4:6])
            assert to_grade == from_grade + 1 and to_grade <= forge["max_grade_by_chapter"][c - 1]
            spend(node, "basic_forge", forge["step_prices_gold"][f"{from_grade}_to_{to_grade}"],
                  target=target, from_grade=from_grade, to_grade=to_grade)
        event("new_run", "initialize_once", start_gold, source_id="D09_deterministic_starter", initialization_count=1)
        end_rows = []
        for reg, ch in zip(routes["regions"], rows):
            c = reg["order"]
            for node in reg["mainline_node_ids"]:
                short = node[-3:]
                event(node, "mainline_arrival", required_fee_gold=0)
                if short in ("N02", "N03", "N05"):
                    sid = f"RWD-REG-{c:02d}-{short}-GOLD"
                    event(node, "actual_ground_gold_pickup_assumed", source[sid]["quantity"], source_id=sid)
                if short == "N02":
                    free_potions += 1
                    event(node, "free_small_potion_produced_not_healed", source_id=f"RWD-REG-{c:02d}-N02-REC", quantity=1)
                if short == "N03" and plan_id == "PLAN-EXPLORE":
                    branch = f"REG-{c:02d}-B01"
                    gs, ss = f"RWD-REG-{c:02d}-BCHOICE-GOLD", f"RWD-REG-{c:02d}-BCHOICE-FRAG"
                    event(branch, "selected_single_B_branch_clear_and_actual_pickups", source[gs]["quantity"],
                          repeat_delta=source[ss]["quantity"], source_ids=[gs, ss], other_B_branch_selected=False)
                if short == "N04":
                    if plan_id == "PLAN-EXPLORE":
                        if c == 1:
                            spend(node, "research_sample_cash", sample["price_gold"], unlock_id="UNL-REC-002", quantity=1,
                                  eligibility="previously_researched_and_not_previously_sample_purchased; two_quick_slot_capacity_assumed")
                        spend(node, "optional_intelligence", fac["FAC-INTEL-ENTRY"]["intel"]["price_gold"],
                              eligibility="current_H01_unrevealed_generated_reachable; paid_before_free_clue_discovery")
                        hidden = f"REG-{c:02d}-H01"
                        if hidden in toll:
                            spend(node, "optional_hidden_entry_entitlement", toll[hidden], destination_node_id=hidden)
                        if c <= 2:
                            bid = "BOS-GOB-001" if c == 1 else "BOS-BST-001"
                            event(hidden, "optional_Boss_success_and_actual_ground_gold_pickup", source[f"RWD-{bid}-GOLD"]["quantity"],
                                  repeat_delta=source[f"RWD-{bid}-FRAG"]["quantity"], first_delta=source[f"RWD-FIRST-{bid}"]["quantity"],
                                  source_ids=[f"RWD-{bid}-GOLD", f"RWD-{bid}-FRAG", f"RWD-FIRST-{bid}"])
                        disc = f"RWD-DISCOVERY-REG-{c:02d}-H01"
                        event(hidden, "actual_safe_discovery_interaction", first_delta=source[disc]["quantity"], source_id=disc,
                              account_discovery_unclaimed_assumption=True)
                    if plan_id == "PLAN-EQUIP":
                        if c == 1:
                            do_forge(node, "starting_WPN-SWD-001", 0, 1)
                        if c == 2:
                            spend(node, "known_merchant_armor", armor_offer["price_gold"], offer_id=armor_offer["offer_id"],
                                  target="ARM-MED-001", purchased_grade=1, natural_enchant_not_assumed_beneficial=True)
                        if c == 3:
                            do_forge(node, "starting_WPN-SWD-001", 1, 2)
                            do_forge(node, "bought_ARM-MED-001", 1, 2)
                        if c == 4:
                            spend(node, "enchant_awaken", enchant["operations"]["awaken"]["cost_gold"],
                                  target="starting_WPN-SWD-001", random_improvement_guaranteed=False)
                            spend(node, "enchant_reroll_I", enchant["operations"]["reroll"]["cost_gold_by_tier"]["1"],
                                  target="starting_WPN-SWD-001", random_improvement_guaranteed=False)
                        if c == 5:
                            do_forge(node, "starting_WPN-SWD-001", 2, 3)
                            do_forge(node, "bought_ARM-MED-001", 2, 3)
                    buy_small(node)
                    if plan_id == "PLAN-EXPLORE":
                        if c in (3, 5):
                            choice = fac["FAC-CHOICE-WHEEL"]
                            spend(node, "deterministic_choice_wheel", choice["price_gold"], choice_id="CHOICE-HEAL", quantity=2,
                                  capacity_assumption="whole_two_potion_bundle_fits_stack3_after_prior_legal_use_or_explicit_drop")
                        if c in (2, 4):
                            wheel = fac["FAC-ROULETTE"]
                            spend(node, "roulette_one_use", wheel["price_gold"], outcome_assumption="ROU-EMPTY",
                                  outcome_is_paper_example_not_guarantee_or_measured_frequency=True)
                if short == "N05":
                    sid = f"RWD-REG-{c:02d}-N05-FRAG"
                    event(node, "actual_ground_shard_pickup_assumed", repeat_delta=source[sid]["quantity"], source_id=sid)
                if short == "N06":
                    buy_small(node)
                if short == "N07":
                    bid = reg["mainline_boss_id"]
                    if ch["boss_ground_gold_if_actually_picked"]:
                        sid = f"RWD-{bid}-GOLD"
                        event(node, "qualified_Boss_success_then_actual_ground_gold_pickup", source[sid]["quantity"], source_id=sid)
                    event(node, "qualified_Boss_direct_shards", repeat_delta=ch["boss_direct_shards_on_qualified_success"],
                          first_delta=ch["first_boss_extra_if_unclaimed"], source_ids=[f"RWD-{bid}-FRAG", f"RWD-FIRST-{bid}"])
                    end_rows.append({"chapter": c, "gold_before_end_of_run_destruction": balance,
                                     "repeat_shards_earned": shard_repeat, "earned_with_all_available_firsts": shard_repeat + shard_first})
        pre_end = balance
        event("REG-05-N07", "victory_terminal_local_gold_ends", -balance, no_shard_second_credit=True)
        income = sum(e["gold_delta"] for e in events if e["gold_delta"] > 0)
        spent = sum(x["gold"] for x in purchases)
        assert income - spent == pre_end
        assert len([e for e in events if e["kind"] == "initialize_once"]) == 1
        assert len([e for e in events if e["kind"] == "mainline_arrival"]) == 35
        assert paid_potions == 10 and free_potions == 5
        assert (income, spent, pre_end) == {"PLAN-SUPPLY": (700, 180, 520), "PLAN-EQUIP": (700, 568, 132), "PLAN-EXPLORE": (920, 408, 512)}[plan_id]
        assert (shard_repeat, shard_first) == ((78, 24) if plan_id == "PLAN-EXPLORE" else (60, 10))
        plans.append({"id": plan_id, "name": name, "kind": "ordered_paper_wallet_not_playtest",
                      "assumptions": ["每个所列战斗真实清完且玩家存活；全部所列地面金币/碎片实际拾取；Boss成功不自动等于拾金币。",
                                      "所有购买均在原完整安全/报价/实例版本与整包容量动作满足时；药及时合法使用或明确丢弃腾出stack3，不能因满包先扣费。",
                                      "不依赖随机额外掉落、售卖、无限刷新、功能券折扣或专注/弹匣付费恢复。",
                                      "首次总数是所有所列账号首次尚可领取时的上限式情景；已领则对应first_delta为0，金币轨迹不变。"],
                      "extra_plan_assumption": "预先已研究UNL-REC-002且样品未购；历史6碎片研究费用不冒充本局免费所得。选择每章一个B01、不选B02；5隐藏均可跳过，本例选择全探索。" if plan_id == "PLAN-EXPLORE" else None,
                      "gross_gold_including_start": income, "spent_gold": spent, "pre_end_gold": pre_end, "post_end_gold": balance,
                      "repeat_shards": shard_repeat, "extra_if_all_account_firsts_available": shard_first,
                      "earned_shards_if_all_firsts_available": shard_repeat + shard_first, "fixed_small_potions_produced": free_potions,
                      "paid_small_potions_bought": paid_potions, "additional_small_potions_from_choice": 4 if plan_id == "PLAN-EXPLORE" else 0,
                      "sample_content_if_bought": "ITM-REC-002" if plan_id == "PLAN-EXPLORE" else None,
                      "mainline_nodes_covered": main_ids, "chapter_end_snapshots": end_rows, "purchases": purchases, "events": events,
                      "source_ref_ids": ["SRC-D07-ROUTE", "SRC-D08-SOURCES", "SRC-D08-FACILITIES", "SRC-D09-HUB", "SRC-D09-SAMPLE", "SRC-V2-COST"]})

    failures = []
    for c in range(1, 6):
        previous = rows[:c - 1]
        prior_repeat = sum(x["repeat_shards_if_ground_picked_and_success"] for x in previous)
        current_ground = rows[c - 1]["ordinary_ground_shards_if_picked"]
        failures.append({"id": f"FAIL-BOSS-{c}", "death_point": f"REG-{c:02d}-N07_before_qualified_success",
                         "assumptions": "此前主路金币/碎片拾全且Boss合法成功；本章N05已清。可选支路与旧账号余额不计；本章Boss死亡/双死都不成功。",
                         "repeat_shards_retained_if_current_N05_picked": prior_repeat + current_ground,
                         "repeat_shards_retained_if_current_N05_unpicked": prior_repeat,
                         "extra_if_each_prior_Boss_first_unclaimed": (c - 1) * 2,
                         "retained_if_current_N05_picked_and_prior_firsts_available": prior_repeat + current_ground + (c - 1) * 2,
                         "current_Boss_new_shards": 0, "gold_and_local_items_after_end": 0,
                         "source_ref_ids": ["SRC-D04-PICKUP", "SRC-D08-SOURCES", "SRC-D13-COMMIT"]})
    failures.extend([
        {"id": "FAIL-ABANDON-AFTER-CH3", "assumptions": "前三章主路碎片拾全、三Boss合法成功后明确放弃。", "repeat_shards_retained": 27,
         "extra_if_three_firsts_available": 6, "new_abandon_award": 0, "gold_and_local_items_after_end": 0,
         "source_ref_ids": ["SRC-D04-PICKUP", "SRC-D08-SOURCES", "SRC-D13-COMMIT"]},
        {"id": "CONTINUE-SAME-RUN", "assumptions": "PLAN-EQUIP第三章Boss后最后完整代被正常保存。", "saved_gold": 95,
         "saved_repeat_shards": 27, "continue_gold": 95, "new_start_gold_award": 0, "new_free_potion_or_transition_heal_from_load": 0,
         "rule": "同Run沿原余额/物品/解锁快照/时间/随机与样品标志；未结束局不能局外改天赋或另开局。",
         "source_ref_ids": ["SRC-D09-HUB", "SRC-D13-COMMIT"]},
        {"id": "CONTINUE-FAILED-PUBLISH", "assumptions": "最后完整代在本次碎片拾取前；新候选未发布就异常退出。",
         "rule": "只能恢复最后完整已发布账号+Run；可能回退未发布收入/动作，不能拼接较新余额。5秒请求不是零损或绝对5秒保证。",
         "source_ref_ids": ["SRC-D13-COMMIT", "SRC-D04-PICKUP"]},
        {"id": "SAMPLE-BOUGHT-THEN-DEAD", "assumptions": "已在合法N04现金买样品整代发布，再死亡。",
         "rule": "局内物品结束，账号该研究样品已购保持true；无金币/研究碎片退款，不重获一次样品资格。没买结束则资格仍false但下局须重选。",
         "source_ref_ids": ["SRC-D09-SAMPLE", "SRC-D13-COMMIT"]},
    ])

    def hp_case(cid, name, damage_rows):
        hp = 100.0
        out = []
        heal_total = 0.0
        damage_total = 0.0
        overheal = 0.0
        alive = True
        for c, ds in enumerate(damage_rows, 1):
            for n, d in zip(("N02", "N03", "N05", "N07"), ds):
                if not alive:
                    break
                before = hp
                actual_loss = min(hp, d)
                hp = max(0.0, hp - d)
                damage_total += actual_loss
                out.append({"chapter": c, "node_id": f"REG-{c:02d}-{n}", "kind": "assumed_postmitigation_HP_loss",
                            "assumed_incoming_HP_loss": d, "actual_HP_lost_until_zero": actual_loss, "HP_before": before, "HP_after": hp})
                if hp == 0:
                    alive = False
                    break
                if n in ("N02", "N03", "N05"):
                    before = hp
                    actual = min(small_heal, 100 - hp)
                    hp += actual
                    heal_total += actual
                    overheal += small_heal - actual
                    out.append({"chapter": c, "node_id": f"REG-{c:02d}-" + {"N02": "N02_after_clear", "N03": "N04_after_purchase", "N05": "N06_after_purchase"}[n],
                                "kind": "one_legal_small_potion_used", "nominal_after_efficiency": small_heal, "actual_heal": actual,
                                "overheal_discarded": small_heal - actual, "HP_before": before, "HP_after": hp})
            if not alive:
                break
            if c < 5:
                before = hp
                actual = min(100 * 0.2, 100 - hp)
                hp += actual
                heal_total += actual
                out.append({"chapter": c, "node_id": f"REG-{c:02d}-N07_to_next_chapter", "kind": "once_transition_heal",
                            "nominal_after_efficiency": 20, "actual_heal": actual, "HP_before": before, "HP_after": hp})
        assert abs(100 + heal_total - damage_total - hp) < 1e-9
        return {"id": cid, "name": name, "kind": "explicit_HP_input_sensitivity_not_enemy_simulation", "max_HP": 100,
                "healing_received_pct": 0, "initial_HP": 100, "assumed_damage_by_chapter_N02_N03_N05_Boss": damage_rows,
                "assumptions": ["损血输入是人为指定的实际HP扣除（已含减伤、章乘数与打法后果），不是敌人原始伤害、击中次数或实测。若采用D14后章伤害曲线，不再次乘本表；仍须重新实测承伤。",
                                "每次所列损血先判死亡；只有活着才用药/跨章恢复。三次用药分别来自本章N02保证产出、N04已买、N06已买。",
                                "假定药均实际拾取/携带且每次使用满足动作、缺血、相隔至少8活跃模拟秒和安全窗口；无DoT/其他治疗/吸血/药理/装备词条介入。",
                                "输入为单个聚合损血事件；实战同点多发、时间分布、无法安全饮用或未拾药可以更坏，不能由总量证明存活。"],
                "survives_under_only_these_assumptions": alive, "final_HP": hp, "actual_HP_lost_until_terminal": damage_total,
                "actual_total_heal": heal_total, "potion_overheal_discarded": overheal, "events": out,
                "source_ref_ids": ["SRC-D01-HEAL", "SRC-D03-POTION", "SRC-D03-CAPS", "SRC-D08-FACILITIES"]}
    hp_cases = [hp_case("HP-A", "均匀低承伤：药量充足也有过量损耗", [[10, 25, 30, 35]] * 5),
                hp_case("HP-B", "后章压力增加：买齐固定补给仍可能在终局归零", [[10,25,30,35],[12,27,32,40],[14,29,34,45],[16,31,36,50],[18,33,38,55]])]
    assert hp_cases[0]["final_HP"] == 65 and hp_cases[0]["survives_under_only_these_assumptions"]
    assert hp_cases[1]["final_HP"] == 0 and not hp_cases[1]["survives_under_only_these_assumptions"]

    refs = [{"id": rid, "path": path, "json_pointer": ptr, "sha256": sha(path), "purpose": purpose} for rid, path, ptr, purpose in REFS]
    all_optional_gold = sum(source[f"RWD-REG-{c:02d}-BCHOICE-GOLD"]["quantity"] for c in range(1, 6)) + source["RWD-BOS-GOB-001-GOLD"]["quantity"] + source["RWD-BOS-BST-001-GOLD"]["quantity"]
    assert all_optional_gold == 220
    return {
        "schema_version": "1.0", "design_date": "2026-10-14", "timezone": "Asia/Shanghai", "module": "D-14", "source_event": "EV-032",
        "status": "design_only", "runtime_implemented": False, "authority": "assistant_proposal_not_individually_approved", "parameter_status": "unplaytested",
        "scope": "只复核既有经济/恢复/成长预算与边界；不改旧收益、药产出、概率、天赋价格，不实现玩法/存档。",
        "reference_builder": "build_economy_reference.py", "source_refs": refs,
        "independent_check": {"facts": "从D07五区35主节点、D08 sources/设施与D09逐级价格重算，未以汇总自证；现有数值皆设计值。",
                              "reasoning": "预算按事件先后验证可支付，产出/拾取/携带/实际使用/治疗分开；以当前样品和首次资格决定永久收益。",
                              "risks": "资金可支付不证明战斗可通或强化最优；缺少运行承伤、时长、饮用窗口与掉落实测，不能给每小时效率、保证回血或固定几局升满。"},
        "baseline": {"start_once_gold": start_gold, "ordinary_ground_gold": ordinary_gold, "first_four_Boss_ground_gold": boss_gold, "gross_gold_if_all_picked": gross,
                     "ordinary_ground_shards_if_picked": ordinary_shards, "Boss_direct_shards": boss_shards, "repeat_shards": repeat,
                     "five_main_Boss_first_extra_if_unclaimed": first_extra, "first_full_mainline_shards_if_all_eligible": repeat + first_extra,
                     "all_optional_gross_gold_if_one_B_each_and_both_optional_Bosses": all_optional_gold,
                     "main_and_all_optional_gold_gross": gross + all_optional_gold, "known_optional_tolls_total": sum(toll.values()),
                     "fixed_free_small_potions_produced": 5, "fixed_paid_small_potion_units": 10, "paid_small_potions_total_gold": sum(potion_prices),
                     "mainline_chapter_crossings": len(chapter_exits), "new_sources_or_rewards_added": 0,
                     "conditions": ["所有必需战斗合法成功且玩家存活；普通/前四Boss地面币与N05碎片实际全拾。", "不含消费、支路、轮盘金币或旧账号余额；首次额外只查当前账号未领键。", "最终Boss金币0；终局先直接入永久奖励再结束Run，剩余局内币不是结算兑换。"]},
        "chapter_rows": rows, "prior_budget_cases_recomputed": old_checks, "ordered_full_run_plans": plans,
        "zero_wallet_mainline": {"kind": "structural_affordability_only", "all_mainline_forward_and_chapter_edges_free": True,
                                 "required_mainline_nodes": 35, "required_random_key_toll_purchase_or_research": False,
                                 "example_actual_zero_wallet_checkpoint": "PLAN-EQUIP REG-01-N04买18小药并锻30后余额0，仍可免费走N05/N06/主Boss；只有可选消费需等新拾取。",
                                 "starting20_is_removed_or_replaced_with0": False,
                                 "claim": "零金币不造成主路通行/普通结局经济锁；零天赋或零消费实战通关仍未验证。",
                                 "source_ref_ids": ["SRC-D07-CONTRACT", "SRC-D04-EXIT", "SRC-D10-END"]},
        "recovery_and_HP": {"formula_potion": "alive ? min(30*(1+clamp(healing_received_pct,-25,25)/100), current_missing_HP) : 0；且必须先合法携带/动作/提交。",
                            "formula_transition": "合法主线跨章且alive ? min(current_MaxHP*.20*(1+clamp(healing_received_pct,-25,25)/100),current_missing_HP) : 0；每条主线跨章一次，共四次。",
                            "not_sources": ["N01入口满血刷新", "N06到达或NPC对白即时治疗", "可选Boss胜利跨章恢复", "返回旧房/暂停/离线/CD重置", "锻造/附魔/换甲抬最大HP直接补血"],
                            "nominal_limits_not_guarantees": {"free5_small_potions_base_HP": 150, "free5_if_all_used_efficiency075_to125_before_missing_HP": [112.5,187.5],
                                                             "all15_fixed_small_potions_base_HP": 450, "all15_efficiency075_to125_before_missing_HP": [337.5,562.5],
                                                             "four_transitions_fixed_maxHP100_eff1_before_missing_HP": 80, "zero_actual_healing_is_possible_if_unpicked_unused_or_no_legal_window": True},
                            "chapter_damage_curve_boundary": "后章普通/精英伤害若按D14曲线增加，不增加D08药产出；实际损血还依赖减伤/闪避/命中/时间。HP模型用显式扣HP输入，不把该输入说成章伤害实测。",
                            "HP_cases": hp_cases},
        "failure_abandon_continue_cases": failures,
        "progression": {"talent_nodes": 9, "talent_ranks": 27, "talent_all_cost_shards": talent_total, "research_nodes": 14, "research_all_cost_shards": research_total,
                        "combined_catalog_cost_shards": talent_total + research_total,
                        "talent_cost_rows": [{"id": x["id"], "cost_by_next_rank": x["cost_by_next_rank"], "total": sum(x["cost_by_next_rank"]), "prerequisites": x["prerequisites"]} for x in talents["nodes"]],
                        "research_cost_rows": [{"id": x["id"], "cost_shards": x["cost_shards"], "prerequisite_unlock_ids": x["prerequisite_unlock_ids"], "sample_cash_gold": x["research_sample"]["price_gold"]} for x in unlocks["unlocks"]],
                        "early_example": "第一章主路普通碎片2已拾且Boss首次合法成功4+2，新增8可局外买根基一级2＋UNL-REC-002研究6；若Boss未成功仅已拾2，不算8。",
                        "no_fixed_run_count_or_duration_claim": True,
                        "earnings_equation": "当前余额=旧余额+本次实际已入账奖励-实际购买+有效原实付退款；只退款不增加earned_total或新永久财富。",
                        "sample_boundary": "研究是解锁资格而非赠物；每研究现金样品账号最多成功买一次，死亡/退款天赋不恢复，未购买不得把报价当已持物。样品不增加700金币或60重复主线碎片。",
                        "active_run_lock": "暂停/继续/故障仍锁局外购买/全退/样品选择/新局；只新Run读取新成长快照。"},
        "opportunity_cost": [
            {"id": "COST-START48", "comparison": "第一章首次N04拾全时只有48币：18小药+30初锻恰0；20觉醒+30初锻需50，不能同刻全买。", "numbers": {"available": 48, "small_plus_forge": 48, "awaken_plus_forge": 50}},
            {"id": "COST-DUALFORGE", "comparison": "已有两件+0双装备全锻+3需340；本审计固定买+1甲43后，剑0→3为170、甲1→3为140，买甲与锻造总353。原免费掉甲不是保证。", "numbers": {"dual0to3": 340, "fixed_armor_purchase_and_sword_armor_forge": 353}},
            {"id": "COST-ENCHANT", "comparison": "觉醒20+I→V四次升阶480=500；与已有两件+0双锻340共840，超过700且未含药180。升阶需合法区间，随机包不保证收益。", "numbers": {"awaken": 20, "all_upgrade": 480, "awaken_to_V": 500, "dual_forge_plus_to_V": 840, "with10_potions": 1020}},
            {"id": "COST-OPTIONAL", "comparison": "所有支路/可选Boss额外地面币220需额外战斗和实际拾取；两门票55，净增最多式165未含情报/其他消费。第四章35门票已发现后无新经济收益，仍可跳过。", "numbers": {"extra_gold": 220, "tolls": 55, "net_before_other_spends": 165}},
            {"id": "COST-RANDOM", "comparison": "轮盘一次20，10%出40币、30%小药、30%炸弹、30%empty；金币输出期望4不等每转返4，物品标价不当现金。确定转轮30是明确整包而非增加主线收入。", "numbers": {"roulette_fee": 20, "expected_gold_output": 4, "choice_fee": 30}},
            {"id": "COST-SAMPLE", "comparison": "UNL-REC-002先付研究6碎片，之后可选样品再付33金币；不是研究后免费大药。功能样品票可节省原一次服务2/3币，但不增服务次数、不可无限重复、不变成碎片收益。", "numbers": {"research": 6, "large_potion_sample_gold": 33}}
        ],
        "findings": [
            {"id": "ECON-F01", "severity": "assumption_gap", "fact": "旧BUD-001/002列甲强化但未列购甲；N03固定产装备不等固定产甲。", "minimal_revision": "在D14审计/主稿补已合法取得相应甲的条件；本轮固定已知商人43币甲方案给出可支付替代，不改旧收益/概率。"},
            {"id": "ECON-F02", "severity": "runtime_validation_required", "fact": "固定5免费+10付费药是产出/报价，不是实际治疗；同点死亡、满包、未拾、8sCD和动作窗口都能减少用量。", "minimal_revision": "D14以可检查HP假设/未来承伤与饮用窗口验收表述；不凭总药量提高章伤害或宣称保证通关。"},
            {"id": "ECON-F03", "severity": "boundary", "fact": "每小时碎片/几局买满缺少实测时长和成功率。", "minimal_revision": "仅列280/130/410与已入账公式，不给固定刷取局数/时长承诺。"}
        ],
        "verification": {"kind": "reference_arithmetic_and_source_identity_only", "source_hashes_captured": True, "all35_main_nodes_covered_per_plan": True,
                         "all_event_gold_balances_nonnegative": True, "start20_exactly_once_per_plan": True, "three_prior_D08_ordered_wallets_recomputed": True,
                         "three_new_full_run_plans_recomputed": True, "two_explicit_HP_input_cases_recomputed": True, "gameplay_simulation_or_runtime_playtest": False,
                         "claims_not_verified": ["零天赋/零消费实际通关", "章节通过率/平均局时", "药实际可拾/可饮/实际治疗分布", "设施选择最优/金币闲置率", "实际存档故障恢复与D14章伤害曲线"]}
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--check", action="store_true")
    args = p.parse_args()
    value = build()
    encoded = json.dumps(value, ensure_ascii=False, indent=2) + "\n"
    if args.check:
        assert TARGET.read_text(encoding="utf-8") == encoded, "audit differs from reference or source hashes changed"
    else:
        TARGET.write_text(encoded, encoding="utf-8")
    print(json.dumps({"ok": True, "mode": "check" if args.check else "build", "plans": len(value["ordered_full_run_plans"]),
                      "source_refs": len(value["source_refs"]), "failure_continue_cases": len(value["failure_abandon_continue_cases"]),
                      "gold": 700, "repeat_shards": 60, "first_mainline_shards": 70}, ensure_ascii=True))


if __name__ == "__main__":
    main()
