"""Check/export design data only. This is not a UE gameplay implementation."""
from __future__ import annotations

import csv
import hashlib
import itertools
import json
import math
import re
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parent
BASE = ROOT.parent / "equipment-v1"
PROJECT = ROOT.parents[2]
FAMILIES = "KNF DAO SWD GSW SPR HAL XBW PST SGN RFL STF".split()
ROMAN = ("I", "II", "III", "IV", "V")
errors = []
checks = 0


def check(condition, message):
    global checks
    checks += 1
    if not condition:
        errors.append(message)


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write(name, obj):
    (ROOT / name).write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def clamp(value, lower, upper):
    return max(lower, min(upper, value))


def legal_range(item, affix, tier):
    kind = "weapon" if item["id"].startswith("WPN-") else "armor"
    if kind not in affix["eligible_kinds"]:
        return None
    if kind == "weapon" and item["family"] not in affix["eligible_weapon_families"]:
        return None
    band = next(t for t in affix["tiers"] if t["tier"] == tier)
    lo, hi = band["min"], band["max"]
    if kind == "armor" and affix["direction"] == -1:
        limits = {"armor_flat": item["armor"], "ward_flat": item["ward"], "poise_flat": item["poise_bonus"]}
        if affix["stat"] in limits:
            hi = min(hi, limits[affix["stat"]])
    if kind == "weapon":
        def still_legal(magnitude):
            signed = magnitude * affix["direction"]
            if affix["stat"] == "reach_pct":
                # The inner dead-zone is not scaled. Primary and skill need a
                # nonempty forward range after shrinking the maximum only.
                for action in (item, item["secondary"]):
                    minimum = action.get("min_range_cm", 0)
                    if action["range_cm"] * (1+signed/100) <= minimum:
                        return False
            if affix["stat"] == "focus_cost_pct":
                for action in (item, item["secondary"]):
                    cost = action.get("focus_cost", 0) * (1+signed/100)
                    if cost > 100 or (action.get("focus_cost", 0) > 0 and cost <= 0):
                        return False
            return True
        legal_values = [m for m in range(lo, hi+1) if still_legal(m)]
        if not legal_values:
            return None
        lo, hi = min(legal_values), max(legal_values)
    return (lo, hi) if lo <= hi else None


def sample_enchant(item, by_id):
    # Examples are independent of the actual random pool; all are grade-II mixed.
    templates = {
        "KNF": ("P-010", "P-005", "N-001"),
        "DAO": ("P-001", "P-003", "N-002"),
        "SWD": ("P-005", "P-006", "N-016"),
        "GSW": ("P-001", "P-003", "N-002"),
        "SPR": ("P-004", "P-002", "N-001"),
        "HAL": ("P-013", "P-003", "N-002"),
        "XBW": ("P-008", "P-001", "N-016"),
        "PST": ("P-005", "P-002", "N-006"),
        "SGN": ("P-008", "P-003", "N-001"),
        "RFL": ("P-005", "P-001", "N-002"),
        "STF": ("P-009", "P-011", "N-001"),
        "LGT": ("P-020", "P-014", "N-011"),
        "MED": ("P-014", "P-015", "N-016"),
        "HVY": ("P-014", "P-016", "N-015"),
        "ROB": ("P-018", "P-015", "N-014"),
    }
    family = item.get("family", item.get("type"))
    ids = list(templates[family])
    if item["id"] == "WPN-STF-002":
        ids[1] = "P-012"
    elif item["id"] == "WPN-STF-003":
        ids[1] = "P-013"
    rows = []
    for short in ids:
        a = by_id["AFF-" + short]
        band = legal_range(item, a, 2)
        check(band is not None, f"{item['id']}: invalid example affix {a['id']}")
        if band is None:
            continue
        lo, hi = band
        count = hi - lo + 1
        magnitude = lo + count // 2
        q_num = 2 * (magnitude - lo) + 1
        q_den = 2 * count
        rows.append({"affix_id": a["id"], "magnitude": magnitude, "signed_value": magnitude * a["direction"], "original_quantile": {"numerator": q_num, "denominator": q_den}})
    return {"tier": 2, "package_type": "mixed", "affixes": rows, "status": "design_example_only"}


def modifiers(enchant, by_id):
    result = defaultdict(float)
    for row in enchant["affixes"]:
        result[by_id[row["affix_id"]]["stat"]] += row["signed_value"]
    return result


def calculate(weapon, armor, wm, am):
    mods = defaultdict(float)
    for values in (wm, am):
        for key, value in values.items():
            mods[key] += value
    ar = clamp((armor["armor"] if armor else 0) + mods["armor_flat"], 0, 150)
    ward = clamp((armor["ward"] if armor else 0) + mods["ward_flat"], 0, 150)
    reduction = min(.6, ar / (100 + ar))
    magic_reduction = min(.6, ward / (100 + ward))
    move = clamp((armor["move_multiplier"] if armor else 1) * (1 + clamp(mods["move_speed_pct"], -25, 25) / 100), .65, 1.25)
    result = {
        "max_health": clamp(100 * (1 + mods["max_health_pct"] / 100), 60, 150),
        "armor": ar, "ward": ward,
        "physical_reduction_pct": 100 * reduction,
        "magic_reduction_pct": 100 * magic_reduction,
        "physical_damage_taken_multiplier": (1 - reduction) * (1 + clamp(mods["physical_vulnerability_pct"], 0, 25) / 100),
        "magic_damage_taken_multiplier": (1 - magic_reduction) * (1 + clamp(mods["magic_vulnerability_pct"], 0, 25) / 100),
        "poise_threshold": clamp(30 + (armor["poise_bonus"] if armor else 0) + mods["poise_flat"], 30, 120),
        "idle_move_cm_s": 265 * move,
        "crit_chance_pct": clamp(5 + mods["crit_chance_pct"], 0, 20),
        "crit_multiplier": clamp(1.5 + mods["crit_damage_bonus_pct"] / 100, 1, 2),
        "focus_regen_per_s": (armor["focus_regen_per_s"] if armor else 12) * (1 + clamp(mods["focus_regen_pct"], -25, 25) / 100),
        "focus_regen_delay_s": armor["focus_regen_delay_s"] if armor else 1,
        "healing_received_multiplier": 1 + clamp(mods["healing_received_pct"], -25, 25) / 100,
    }
    if weapon:
        speed = 1 + clamp(mods["action_speed_pct"], -20, 20) / 100
        direct = weapon["damage_total"] * (1 + clamp(mods["damage_pct"], -30, 50) / 100)
        result.update({
            "nominal_primary_noncrit_damage": direct,
            "nominal_primary_crit_damage": direct * result["crit_multiplier"],
            "primary_windup_s": weapon["windup_s"] / speed,
            "primary_active_s": weapon["active_s"] / speed,
            "primary_recovery_s": weapon["recovery_s"] / speed,
            "primary_cycle_s": weapon["cycle_s"] / speed,
            "range_cm": weapon["range_cm"] * (1 + clamp(mods["reach_pct"], -15, 15) / 100),
            "depth_halfwidth_cm": weapon["depth_halfwidth_cm"],
            "stagger_total": weapon["stagger_total"] * (1 + clamp(mods["stagger_pct"], -25, 25) / 100),
            "skill_cooldown_s": weapon["secondary"]["cooldown_s"] * (1 + clamp(mods["skill_cooldown_pct"], -20, 25) / 100),
            "reload_s": weapon["reload_s"] / (1 + clamp(mods["reload_speed_pct"], -25, 25) / 100),
            "focus_cost": weapon["focus_cost"] * (1 + clamp(mods["focus_cost_pct"], -20, 25) / 100),
            "attack_move_cm_s": 265 * move * weapon["move_multiplier"],
            "lifesteal_pct": clamp(mods["lifesteal_pct"], 0, 5),
        })
    return {k: round(v, 6) for k, v in result.items()}


def main():
    weapons = read(BASE / "weapons.json")
    armors = read(BASE / "armor.json")
    affixes = read(ROOT / "affixes.json")
    stats = read(ROOT / "stat-definitions.json")
    rules = read(ROOT / "enchant-rules.json")
    check(len(weapons) == 33 and len(armors) == 12, "base catalogue count")
    check(len(affixes) == 36, "expected 36 affixes")
    check(Counter(a["polarity"] for a in affixes) == {"beneficial": 20, "harmful": 16}, "expected 20 beneficial and 16 harmful")
    check(len({a["id"] for a in affixes}) == 36, "affix IDs unique")
    check(len(stats) == 22 and len({s["id"] for s in stats}) == 22, "22 unique attribute definitions")
    stat_ids = {s["id"] for s in stats}
    check({a["stat"] for a in affixes} == stat_ids, "affixes cover all and only 22 stat keys")
    for stat in stats:
        check(all(k in stat for k in ("id","name","unit","owner","base_rule","formula","min_value","max_value","cap_scope","status")), f"{stat['id']}: attribute fields")
        check(stat["status"] == "design_only" and stat["min_value"] <= stat["max_value"], f"{stat['id']}: attribute bounds/status")
    expected_caps = {
        "AFF-P-001": [5,10,15,20,25], "AFF-P-002": [4,8,12,16,20], "AFF-P-003": [5,10,15,20,25],
        "AFF-P-004": [3,6,9,12,15], "AFF-P-005": [3,6,9,12,15], "AFF-P-006": [10,20,30,40,50],
        "AFF-P-007": [4,8,12,16,20], "AFF-P-008": [5,10,15,20,25], "AFF-P-009": [4,8,12,16,20],
        "AFF-P-010": [1,2,3,4,5], "AFF-P-011": [2,3,4,5,6], "AFF-P-012": [5,10,15,20,25], "AFF-P-013": [2,4,6,8,10],
        **{f"AFF-P-{i:03}": [5,10,15,20,25] for i in range(14,20)}, "AFF-P-020": [3,6,9,12,15],
        "AFF-N-001": [4,8,12,16,20], "AFF-N-002": [4,8,12,16,20], "AFF-N-003": [5,10,15,20,25], "AFF-N-004": [3,6,9,12,15],
        **{f"AFF-N-{i:03}": [5,10,15,20,25] for i in (5,6,7,12,13,14,15)},
        **{f"AFF-N-{i:03}": [4,8,12,16,20] for i in (8,9,10,11)}, "AFF-N-016": [3,6,9,12,15],
    }
    by_id = {a["id"]: a for a in affixes}
    for a in affixes:
        check(a["id"] in expected_caps, f"{a['id']}: invalid affix ID")
        check(a["stat"] in stat_ids, f"{a['id']}: missing stat definition")
        check(a["direction"] in (-1,1), f"{a['id']}: invalid direction")
        expected_direction = -1 if a["id"] in {"AFF-P-007","AFF-P-009"} else (1 if a["polarity"]=="beneficial" or a["id"] in {"AFF-N-005","AFF-N-007","AFF-N-014","AFF-N-015"} else -1)
        check(a["direction"] == expected_direction, f"{a['id']}: polarity/numeric direction mismatch")
        expected_unit = "damage_per_s" if a["stat"]=="burn_dps" else ("points" if a["stat"] in {"armor_flat","ward_flat","poise_flat","shock_flat"} else "percent")
        check(a["unit"] == expected_unit, f"{a['id']}: attribute unit mismatch")
        check(a["status"] == "design_only", f"{a['id']}: implementation claim")
        check(a["group"] == ("elemental" if a["stat"] in ("burn_dps", "slow_pct", "shock_flat") else a["stat"]), f"{a['id']}: inconsistent conflict group")
        check([t["tier"] for t in a["tiers"]] == [1,2,3,4,5], f"{a['id']}: tiers")
        check([t["max"] for t in a["tiers"]] == expected_caps[a["id"]], f"{a['id']}: maxima disagree with brief")
        for t in a["tiers"]:
            check(isinstance(t["min"], int) and isinstance(t["max"], int) and 1 <= t["min"] <= t["max"], f"{a['id']}/{t['tier']}: invalid integer interval")
        fixed = a["id"] in {"AFF-P-010", "AFF-P-011", "AFF-P-012", "AFF-P-013"}
        for i, t in enumerate(a["tiers"]):
            expected_min = t["max"] if fixed else (a["tiers"][i-1]["max"]+1 if i else 1)
            check(t["min"] == expected_min, f"{a['id']}/{t['tier']}: overlapping or incorrect tier minimum")
        if a["stat"] == "reload_speed_pct":
            check(set(a["eligible_weapon_families"]) == {"XBW","PST","SGN","RFL"}, f"{a['id']}: reload eligibility")
        if a["stat"] == "focus_cost_pct":
            check(a["eligible_weapon_families"] == ["STF"], f"{a['id']}: focus eligibility")
        if a["stat"] == "reach_pct":
            check("SGN" not in a["eligible_weapon_families"], f"{a['id']}: shotgun reach exclusion")

    # Design contract checks; tiers keep their UI labels in the source JSON.
    check(rules.get("status") == "design_only", "rules status")
    check(rules.get("spawn_enchant_chance") == .4, "spawn chance")
    check([t["tier"] for t in rules.get("tiers", [])] == [1,2,3,4,5], "rule tiers")
    weights = rules.get("package_weights", {})
    check(weights == {"beneficial": .6, "mixed": .3, "cursed": .1}, "conditional package probabilities")
    check(abs(sum(weights.values()) - 1) < 1e-12, "package sum")
    check(rules["sign_rule"]["polarity_values"] == ["beneficial", "harmful"], "affix polarity vocabulary")
    check(set(rules["exclusivity"]["element_members"]) == {"burn_dps", "slow_pct", "shock_flat"}, "element stat vocabulary")
    check(rules["packages"] == {"beneficial":{"positive_affixes":1,"negative_affixes":0},"mixed":{"positive_affixes":2,"negative_affixes":1},"cursed":{"positive_affixes":0,"negative_affixes":1}}, "package sizes")
    expected_pools = {"early":[.7,.25,.05,0,0], "middle":[.15,.4,.35,.1,0], "advanced":[0,.1,.4,.35,.15]}
    for pool, values in expected_pools.items():
        actual = [rules["tier_pools"][pool][str(i)] for i in range(1,6)]
        check(actual == values and abs(sum(actual)-1) < 1e-12, f"{pool}: tier pool weights")
    ops = rules["operations"]
    check(ops["awaken"]["cost_gold"] == 20 and ops["awaken"]["result_tier"] == 1, "awaken fee/tier")
    check(ops["reroll"]["cost_gold_by_tier"] == dict(zip(map(str,range(1,6)),[15,30,55,85,120])), "reroll fees")
    check(ops["upgrade"]["cost_gold_by_from_tier"] == dict(zip(map(str,range(1,5)),[40,80,140,220])), "upgrade fees")
    check(ops["cleanse"]["cost_gold_by_tier"] == dict(zip(map(str,range(1,6)),[10,20,35,55,80])), "cleanse fees")
    check(ops["upgrade"]["negative_affixes_upgrade_too"] and ops["upgrade"]["prevalidate_all_next_tier_intervals"], "upgrade negative/eligibility contract")
    check(rules["generation"]["quantile"]["preserve_original_across_all_upgrades"], "preserve original rational q")

    profiles = []
    mixed_combination_count = 0
    upgrade_mapping_count = 0
    all_items = weapons + armors
    for item in all_items:
        kind = "weapon" if item["id"].startswith("WPN-") else "armor"
        candidates = []
        for a in affixes:
            bands = []
            for tier in range(1,6):
                band = legal_range(item,a,tier)
                if band:
                    bands.append({"tier": tier, "min": band[0], "max": band[1]})
            if bands:
                candidates.append({"affix_id": a["id"], "legal_tier_ranges": bands})
        for tier in range(1,6):
            legal = [a for a in affixes if legal_range(item,a,tier)]
            pos = [a for a in legal if a["polarity"] == "beneficial"]
            neg = [a for a in legal if a["polarity"] == "harmful"]
            check(bool(pos) and bool(neg), f"{item['id']}/{tier}: positive or negative pool empty")
            mixed = sum(p["group"] != q["group"] and n["group"] not in (p["group"],q["group"]) for p,q in itertools.combinations(pos,2) for n in neg)
            mixed_combination_count += mixed
            check(mixed > 0, f"{item['id']}/{tier}: cannot form mixed package")
        # Exhaustively map every legal starting integer to every later legal band.
        # An empty later band is an explicitly refused upgrade, not a clamped value.
        for affix in affixes:
            for start in range(1,5):
                old_band = legal_range(item, affix, start)
                if old_band is None:
                    continue
                lo, hi = old_band
                for magnitude in range(lo, hi+1):
                    q_num, q_den = 2*(magnitude-lo)+1, 2*(hi-lo+1)
                    previous = magnitude
                    for target in range(start+1,6):
                        new_band = legal_range(item, affix, target)
                        if new_band is None:
                            break
                        nlo, nhi = new_band
                        mapped = nlo + q_num*(nhi-nlo+1)//q_den
                        upgrade_mapping_count += 1
                        check(nlo <= mapped <= nhi and mapped >= previous, f"{item['id']}/{affix['id']}: upgrade mapping bounds/monotonicity")
                        previous = mapped
        example = sample_enchant(item, by_id)
        chosen = [by_id[r["affix_id"]] for r in example["affixes"]]
        check(Counter(a["polarity"] for a in chosen) == {"beneficial":2,"harmful":1}, f"{item['id']}: example counts")
        check(len({a["group"] for a in chosen}) == 3, f"{item['id']}: example conflict")
        mods = modifiers(example,by_id)
        preview = calculate(item if kind=="weapon" else None, item if kind=="armor" else None, mods if kind=="weapon" else {},mods if kind=="armor" else {})
        profiles.append({"id":item["id"],"name":item["name"],"kind":kind,"enchantable":True,"max_enchant_tier":5,"base_definition":item,"affix_eligibility":candidates,"example_enchant":example,"example_preview":preview,"preview_context":"Weapon example uses no armor; armor example uses no weapon. Base player crit5%, HP100. Nominal direct damage excludes enemy mitigation, misses, distance falloff and elemental DoT. Examples are not fixed drops.","status":"design_only"})

    # Cross-item formula checks for all 33 x (12 armor + no armor) example combinations.
    profile_map = {p["id"]:p for p in profiles}
    combo_count = 0
    for w,a in itertools.product(weapons, [None]+armors):
        wm = modifiers(profile_map[w["id"]]["example_enchant"],by_id)
        am = modifiers(profile_map[a["id"]]["example_enchant"],by_id) if a else {}
        out = calculate(w,a,wm,am)
        combo_count += 1
        check(all(math.isfinite(v) for v in out.values()), f"{w['id']}/{a and a['id']}: nonfinite result")
        check(60 <= out["max_health"] <= 150 and 30 <= out["poise_threshold"] <= 120, "combination HP/poise bounds")
        check(0 <= out["crit_chance_pct"] <= 20 and out["crit_multiplier"] <= 2, "combination critical bounds")
        check(265*.65 <= out["idle_move_cm_s"] <= 265*1.25, "combination movement bounds")
        check(abs(out["primary_windup_s"]+out["primary_active_s"]+out["primary_recovery_s"]-out["primary_cycle_s"]) < 4e-6, "combination phase sum")

    report = {"checked_at":datetime.now(timezone(timedelta(hours=8))).isoformat(timespec="seconds"),"status":"failed" if errors else "passed","checks":checks,"item_count":len(profiles),"tier_count":5,"item_tier_eligibility_cells":len(profiles)*5,"package_eligibility_cells":len(profiles)*5*3,"legal_mixed_combinations":mixed_combination_count,"upgrade_integer_mappings":upgrade_mapping_count,"affix_count":len(affixes),"beneficial_affixes":20,"harmful_affixes":16,"affix_tier_intervals":sum(len(a["tiers"]) for a in affixes),"attribute_count":len(stats),"example_equipment_combinations":combo_count,"errors":errors,"scope":"Design data, eligibility, integer upgrade mapping, sample calculations and source hashes only. Not random-drop statistics, UE runtime, economy, persistence, artwork, player feel or balance validation."}
    write("validation-report.json",report)
    if errors:
        print(json.dumps(report,ensure_ascii=False,indent=2))
        raise SystemExit(1)

    sources = {name:hashlib.sha256((BASE/name).read_bytes()).hexdigest() for name in ("weapons.json","armor.json")}
    write("equipment-profiles.json",{"schema_version":2,"status":"design_only","source_catalogue_sha256":sources,"shared_player_base":{"health":100,"crit_chance_pct":5,"crit_multiplier":1.5,"move_cm_s":265,"poise":30,"focus":100},"items":profiles})
    with (ROOT/"affixes.csv").open("w",encoding="utf-8-sig",newline="") as f:
        headers=["编号","名称","好坏","属性键","方向","单位","适用类型","适用武器家族","互斥组"]+[f"{t}级{edge}" for t in ROMAN for edge in ("幅度下限","幅度上限")]+["规则","排除与限制","状态"]
        writer=csv.writer(f);writer.writerow(headers)
        for a in affixes:
            writer.writerow([a["id"],a["name"],"正面" if a["polarity"]=="beneficial" else "负面",a["stat"],a["direction"],a["unit"],"/".join(a["eligible_kinds"]),"/".join(a["eligible_weapon_families"]),a["group"]]+[t[e] for t in a["tiers"] for e in ("min","max")]+[a["rule"],a["exclusions"],a["status"]])

    def label(example):
        output=[]
        for row in example["affixes"]:
            a=by_id[row["affix_id"]];value=row["signed_value"]
            unit={"percent":"%","points":"点","damage_per_s":"/s"}[a["unit"]]
            output.append(f"{'正' if a['polarity']=='beneficial' else '负'}·{a['name']}{value:+}{unit}")
        return "；".join(output)

    with (ROOT/"equipment-attributes.csv").open("w",encoding="utf-8-sig",newline="") as f:
        headers=["编号","名称","类型","家族","可附魔","最高等级","基础伤害","基础周期s","前向cm","纵深半宽cm","攻击移动倍率","削韧","弹匣","装填s","主攻专注","基础护甲","基础魔抗","防具移动倍率","防具韧性加成","专注每秒恢复","恢复等待s","II级混合示例","示例非暴击直伤","示例完整周期s","示例削韧","示例暴击率%","示例最大HP","示例护甲","示例魔抗","示例总韧性","示例待机cm每s","示例专注每秒恢复","状态"]
        writer=csv.writer(f);writer.writerow(headers)
        for p in profiles:
            b=p["base_definition"];o=p["example_preview"]
            writer.writerow([p["id"],p["name"],p["kind"],b.get("family",b.get("type")),True,5]+[b.get(k,"") for k in ("damage_total","cycle_s","range_cm","depth_halfwidth_cm","move_multiplier" if p["kind"]=="weapon" else "__none__","stagger_total","magazine","reload_s","focus_cost","armor","ward","move_multiplier" if p["kind"]=="armor" else "__none__","poise_bonus","focus_regen_per_s","focus_regen_delay_s")]+[label(p["example_enchant"]),o.get("nominal_primary_noncrit_damage",""),o.get("primary_cycle_s",""),o.get("stagger_total",""),o["crit_chance_pct"],o["max_health"],o["armor"],o["ward"],o["poise_threshold"],o["idle_move_cm_s"],o["focus_regen_per_s"],"design_only"])

    text=["# 45件装备：属性与附魔适配/示例 v2","","2026-10-12。状态：设计示例，未接入游戏。基础定义引用v1、未改变原本动作和固有特性。所有物品最高可附魔V；本页统一用II级混合方案示范，不是掉落绑定、推荐最优搭配或每件固定附魔。完整基础属性、合法等级区间及q见[equipment-profiles.json](equipment-profiles.json)，Excel见[equipment-attributes.csv](equipment-attributes.csv)。","","武器示例按无甲玩家计算；防具示例按没有手持武器附魔计算。暴击基础5%、倍率1.5；名义直伤是完整单目标非暴击、目标减伤前值，不含漏击、霰弹远距衰减、元素持续伤害。真正装备组合需要按共同规则一起重算。","","## 33把武器","","| ID / 名称 | 基础伤害 / 完整周期s / X距离cm | II级示例（好坏分列） | 示例直伤 / 周期s / 削韧 |","| --- | --- | --- | --- |"]
    for p in profiles[:33]:
        b=p["base_definition"];o=p["example_preview"]
        text.append(f"| {p['id']} {p['name']} | {b['damage_total']} / {b['cycle_s']} / {b['range_cm']} | {label(p['example_enchant'])} | {o['nominal_primary_noncrit_damage']:g} / {o['primary_cycle_s']:.4f} / {o['stagger_total']:g} |")
    text += ["","## 12套防具","","| ID / 名称 | 基础护甲 / 魔抗 / 移动倍率 | II级示例（好坏分列） | 示例护甲 / 魔抗 / HP上限 / 总韧性 |","| --- | --- | --- | --- |"]
    for p in profiles[33:]:
        b=p["base_definition"];o=p["example_preview"]
        text.append(f"| {p['id']} {p['name']} | {b['armor']} / {b['ward']} / {b['move_multiplier']} | {label(p['example_enchant'])} | {o['armor']:g} / {o['ward']:g} / {o['max_health']:g} / {o['poise_threshold']:g} |")
    text += ["","## 适配校验边界","",f"已检查45件×五级=225个资格单元：每个单元都可组成纯正、混合和纯负三种方案。还对33把武器×(12套甲+无甲)=429个示例组合进行了公式边界检查；这不是游戏运行测试或随机掉落抽样统计。","","负护甲/魔抗/韧性按各甲固有数值截取合法抽样区间。例如法袍没有韧性加成时不能抽到松散；低护甲法袍不能抽到大于其护甲的高级破损。其余负面词仍可出现，不能用无效果坏词冒充风险。","","全量资料区分原基础值与附魔示例，后续新增物品必须通过相同资格检查。生成脚本仅用于文档与表格导出，不是已接入UE的物品系统。"]
    (ROOT/"04-逐件附魔适配与示例.md").write_text("\n".join(text)+"\n",encoding="utf-8")

    # Check generated files after writing, including Excel-friendly BOM decoding.
    with (ROOT/"affixes.csv").open(encoding="utf-8-sig", newline="") as f:
        affix_rows = list(csv.DictReader(f))
    check(len(affix_rows)==36, "affix CSV row count")
    for row, affix in zip(affix_rows, affixes):
        check(row["编号"]==affix["id"] and row["名称"]==affix["name"] and row["属性键"]==affix["stat"], f"{affix['id']}: CSV identity")
        check(int(row["方向"])==affix["direction"] and row["单位"]==affix["unit"] and row["规则"]==affix["rule"] and row["排除与限制"]==affix["exclusions"], f"{affix['id']}: CSV effect rule")
        for name, band in zip(ROMAN, affix["tiers"]):
            check(int(row[f"{name}级幅度下限"])==band["min"] and int(row[f"{name}级幅度上限"])==band["max"], f"{affix['id']}/{name}: CSV interval")
    with (ROOT/"equipment-attributes.csv").open(encoding="utf-8-sig", newline="") as f:
        equipment_rows = list(csv.DictReader(f))
    check(len(equipment_rows)==45, "equipment CSV row count")
    for row, profile in zip(equipment_rows, profiles):
        b, o = profile["base_definition"], profile["example_preview"]
        check(row["编号"]==b["id"] and row["名称"]==b["name"] and row["II级混合示例"]==label(profile["example_enchant"]), f"{b['id']}: CSV identity/example")
        for col, key in {"示例最大HP":"max_health", "示例护甲":"armor", "示例魔抗":"ward", "示例总韧性":"poise_threshold", "示例待机cm每s":"idle_move_cm_s", "示例专注每秒恢复":"focus_regen_per_s", "示例暴击率%":"crit_chance_pct"}.items():
            check(float(row[col])==o[key], f"{b['id']}: CSV preview {key}")
    exported = read(ROOT/"equipment-profiles.json")
    check([p["base_definition"] for p in exported["items"]]==all_items, "exported base definitions equal v1 sources")
    check(exported["source_catalogue_sha256"]=={name:hashlib.sha256((BASE/name).read_bytes()).hexdigest() for name in sources}, "v1 source hashes match exported provenance")
    local_link_count = 0
    for document in [PROJECT/"属性与附魔设计总览.md"] + list(ROOT.glob("*.md")):
        for target in re.findall(r"\[[^\]]*\]\(([^)]+)\)", document.read_text(encoding="utf-8-sig")):
            if "://" in target or target.startswith("#"):
                continue
            dest = unquote(target.split("#")[0].strip("<>"))
            local_link_count += 1
            check((document.parent/dest).exists(), f"{document.name}: broken local link {dest}")
    report.update(checks=checks, status="failed" if errors else "passed", errors=errors, csv_roundtrip_rows={"affixes":len(affix_rows),"equipment":len(equipment_rows)}, local_document_links=local_link_count, source_catalogue_sha256=sources)
    write("validation-report.json", report)
    if errors:
        print(json.dumps(report, ensure_ascii=False, indent=2))
        raise SystemExit(1)
    print(json.dumps({k:report[k] for k in ("status","checks","item_count","item_tier_eligibility_cells","affix_count","affix_tier_intervals","attribute_count","example_equipment_combinations","errors")},ensure_ascii=False))


if __name__ == "__main__":
    main()
