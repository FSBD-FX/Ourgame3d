"""Recalculate the D-09 talent design against preserved source catalogues.

This is a design-data validator. It does not run Unreal or prove balance.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
DESIGN = ROOT / "docs" / "design"


def validate() -> dict[str, Any]:
    result: dict[str, Any] = {"checks": 0, "errors": [], "examples_checked": 0}

    def check(condition: bool, label: str) -> None:
        result["checks"] += 1
        if not condition:
            result["errors"].append(label)

    paths = {
        "talents": DESIGN / "progression-v1" / "talents.json",
        "player": DESIGN / "player-combat-v1" / "player-combat-rules.json",
        "stats": DESIGN / "equipment-v2" / "stat-definitions.json",
        "affixes": DESIGN / "equipment-v2" / "affixes.json",
        "weapons": DESIGN / "equipment-v1" / "weapons.json",
        "armor": DESIGN / "equipment-v1" / "armor.json",
        "items": DESIGN / "items-v1" / "items.json",
        "item_rules": DESIGN / "items-v1" / "common-rules.json",
        "growth": DESIGN / "economy-v1" / "equipment-growth.json",
        "economy": DESIGN / "economy-v1" / "common-rules.json",
    }
    data: dict[str, Any] = {}
    failures = []
    for name, path in paths.items():
        try:
            data[name] = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            failures.append(f"{path.name}: {exc}")
    check(not failures, "Source JSON load failed: " + "; ".join(failures))
    if failures:
        return result

    def keyed(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
        return {row["id"]: row for row in rows}

    talents = data["talents"]
    nodes = keyed(talents["nodes"])
    stats = keyed(data["stats"])
    affixes = keyed(data["affixes"])
    weapons = keyed(data["weapons"])
    armor = keyed(data["armor"])
    items = keyed(data["items"]["items"])
    caps = data["item_rules"]["stat_merge"]["caps"]
    player = data["player"]
    baseline = player["baseline"]
    growth = data["growth"]

    # Independent specification of this proposed catalogue, not copied rows.
    spec = {
        "TAL-VIT": (3, [2, 6, 12], {"max_health_pct": 4}, []),
        "TAL-GRD": (3, [6, 10, 16], {"armor_flat": 2, "ward_flat": 2}, [("TAL-VIT", 1)]),
        "TAL-MED": (3, [8, 14, 22], {"healing_received_pct": 2}, [("TAL-VIT", 2)]),
        "TAL-ATK": (4, [2, 6, 12, 20], {"damage_pct": 2}, []),
        "TAL-BRK": (3, [6, 10, 16], {"stagger_pct": 2}, [("TAL-ATK", 1)]),
        "TAL-CRT": (2, [10, 18], {"crit_chance_pct": 1}, [("TAL-ATK", 2)]),
        "TAL-MOV": (3, [2, 6, 12], {"move_speed_pct": 1}, []),
        "TAL-FOC": (3, [6, 10, 16], {"focus_regen_pct": 3}, [("TAL-MOV", 1)]),
        "TAL-RLD": (3, [6, 10, 16], {"reload_speed_pct": 3}, [("TAL-MOV", 1)]),
    }
    check(len(talents["nodes"]) == 9 and set(nodes) == set(spec), "Nine unique expected talent IDs required")
    if set(nodes) != set(spec):
        return result
    check(
        talents["status"] == "design_only"
        and talents["runtime_implemented"] is False
        and talents["scope"]["zero_talent_mainline_win_verified"] is False,
        "Design-only scope must not claim runtime or zero-talent victory",
    )
    for tid, (ranks, costs, contribution, requirements) in spec.items():
        n = nodes[tid]
        actual_requirements = [(p["talent_id"], p["minimum_owned_rank"]) for p in n["prerequisites"]]
        check(
            n["max_rank"] == ranks
            and n["cost_by_next_rank"] == costs
            and n["per_rank_contributions"] == contribution
            and actual_requirements == requirements
            and n["max_total_cost_shards"] == sum(costs),
            f"{tid}: rank limits, incremental costs, contributions or prerequisites differ",
        )

    rank_total = sum(n["max_rank"] for n in nodes.values())
    scheduled_cost = sum(sum(n["cost_by_next_rank"]) for n in nodes.values())
    check(rank_total == 27 and scheduled_cost == 280, "Expected 27 purchased ranks and 280 scheduled shards")
    expected_rows = {
        tid: [
            {
                "rank": rank,
                "incremental_cost_shards": n["cost_by_next_rank"][rank - 1],
                "cumulative_cost_shards": sum(n["cost_by_next_rank"][:rank]),
                "contributions": {s: value * rank for s, value in n["per_rank_contributions"].items()},
            }
            for rank in range(1, n["max_rank"] + 1)
        ]
        for tid, n in nodes.items()
    }
    check(all(n["rank_rows"] == expected_rows[tid] for tid, n in nodes.items()), "Cumulative rank rows must not replace incremental prices or multiply active sources")

    colors: dict[str, int] = {}

    def visit(tid: str) -> None:
        if tid not in nodes:
            raise ValueError(f"Unknown prerequisite {tid}")
        if colors.get(tid) == 1:
            raise ValueError(f"Prerequisite cycle at {tid}")
        if colors.get(tid) == 2:
            return
        colors[tid] = 1
        for req in nodes[tid]["prerequisites"]:
            parent = req["talent_id"]
            if parent not in nodes or not 1 <= req["minimum_owned_rank"] <= nodes[parent]["max_rank"]:
                raise ValueError(f"Invalid prerequisite on {tid}: {req}")
            visit(parent)
        colors[tid] = 2

    try:
        for tid in nodes:
            visit(tid)
        dependency_error = ""
    except (KeyError, TypeError, ValueError) as exc:
        dependency_error = str(exc)
    check(not dependency_error, "Prerequisite graph: " + dependency_error)

    branch_rows = []
    covered = []
    for branch in talents["branches"]:
        members = [nodes[tid] for tid in branch["talent_ids"]]
        covered.extend(branch["talent_ids"])
        branch_rows.append((sum(n["max_rank"] for n in members), sum(sum(n["cost_by_next_rank"]) for n in members)))
    check(
        branch_rows == [(9, 96), (9, 100), (9, 84)]
        and sorted(covered) == sorted(nodes)
        and all(b["exclusive"] is False for b in talents["branches"]),
        "Three nonexclusive branches must partition nodes with rank/cost totals 9/96, 9/100 and 9/84",
    )

    def contributions(ranks: dict[str, int]) -> dict[str, float]:
        output: dict[str, float] = {}
        for tid, rank in ranks.items():
            if tid not in nodes or not isinstance(rank, int) or not 0 <= rank <= nodes[tid]["max_rank"]:
                raise ValueError(f"Invalid owned rank {tid}={rank}")
            for stat, value in nodes[tid]["per_rank_contributions"].items():
                output[stat] = output.get(stat, 0) + rank * value
        return output

    full = contributions({tid: n["max_rank"] for tid, n in nodes.items()})
    check(full == talents["max_total_contributions"], "Full talent contribution totals differ from rank data")
    v2_bounds = {stat: [stats[stat]["min_value"], stats[stat]["max_value"]] for stat in full}
    expected_bounds = {
        "max_health_pct": [-40, 50], "armor_flat": [0, 150], "ward_flat": [0, 150],
        "healing_received_pct": [-25, 25], "damage_pct": [-30, 50], "stagger_pct": [-25, 25],
        "crit_chance_pct": [0, 20], "move_speed_pct": [-25, 25],
        "focus_regen_pct": [-25, 25], "reload_speed_pct": [-25, 25],
    }
    check(v2_bounds == expected_bounds, "Legacy v2 bounds differ from this design's cap contract")
    check(talents["stat_merge_contract"]["caps_inherited_from_D03"] == caps, "D-09 copied caps must equal D-03 source caps")
    scope = talents["scope"]
    check(
        scope["talent_equipment_slots"] == 0
        and scope["talent_mutex_groups"] == 0
        and scope["infinite_scaling"] is False
        and talents["rank_semantics"]["cumulative_rank_rows_are_reference_not_separate_active_sources"] is True
        and talents["economy_and_unlock_boundary"]["D08_amounts_and_sources_unchanged"] is True,
        "No added talent slots, exclusivity, infinite ranks, cumulative-row stacking or economy multipliers allowed",
    )

    def close(actual: Any, expected: Any) -> bool:
        if isinstance(expected, bool):
            return actual is expected
        if isinstance(expected, (int, float)) and not isinstance(actual, bool):
            return isinstance(actual, (int, float)) and math.isclose(actual, expected, rel_tol=1e-9, abs_tol=1e-8)
        return actual == expected

    def fields(row: dict[str, Any], expected: dict[str, Any]) -> None:
        differences = [f"{key}: got {row.get(key)!r}, expected {value!r}" for key, value in expected.items() if not close(row.get(key), value)]
        if differences:
            raise ValueError("; ".join(differences))

    def clamp(value: float, lower: float, upper: float) -> float:
        return max(lower, min(upper, value))

    def capped(stat: str, value: float) -> float:
        return clamp(value, *v2_bounds[stat])

    def item_stat(iid: str, stat: str) -> float:
        matches = [effect["value"] for effect in items[iid]["effects"] if effect.get("stat") == stat]
        if len(matches) != 1:
            raise ValueError(f"{iid}: expected exactly one {stat} modifier")
        return matches[0]

    heal_effects = [e for e in items["ITM-REC-001"]["effects"] if e["type"] == "heal_hp"]
    potion_base = heal_effects[0]["amount"]
    examples = keyed(talents["paper_examples"])
    expected_examples = {f"TAL-EX-{number:03d}" for number in range(1, 16)}
    check(len(talents["paper_examples"]) == 15 and set(examples) == expected_examples, "Expected 15 unique paper example IDs")

    def example(number: int, calculator: Any) -> None:
        eid = f"TAL-EX-{number:03d}"
        result["checks"] += 1
        if eid not in examples:
            result["errors"].append(f"{eid}: missing example")
            return
        result["examples_checked"] += 1
        try:
            calculator(examples[eid])
        except (AssertionError, KeyError, IndexError, TypeError, ValueError, ZeroDivisionError) as exc:
            result["errors"].append(f"{eid}: {exc}")

    def profile(e: dict[str, Any]) -> None:
        ranks = e["ranks"]
        c = contributions(ranks)
        for tid, rank in ranks.items():
            if rank:
                for req in nodes[tid]["prerequisites"]:
                    if ranks.get(req["talent_id"], 0) < req["minimum_owned_rank"]:
                        raise ValueError(f"Missing prerequisite for {tid}")
        fields(e, {
            "total_ranks": sum(ranks.values()),
            "actual_scheduled_cost_shards": sum(sum(nodes[tid]["cost_by_next_rank"][:rank]) for tid, rank in ranks.items()),
        })
        w = weapons[e["context"]["weapon"]]
        fields(e["expected"], {
            "max_hp": baseline["max_hp"] * (1 + capped("max_health_pct", c.get("max_health_pct", 0)) / 100),
            "armor": capped("armor_flat", c.get("armor_flat", 0)),
            "ward": capped("ward_flat", c.get("ward_flat", 0)),
            "healing_received_pct": capped("healing_received_pct", c.get("healing_received_pct", 0)),
            "weapon_primary_damage": w["damage_total"] * (1 + capped("damage_pct", c.get("damage_pct", 0)) / 100),
            "weapon_primary_stagger": w["stagger_total"] * (1 + capped("stagger_pct", c.get("stagger_pct", 0)) / 100),
            "crit_chance_pct": capped("crit_chance_pct", baseline["crit_chance_pct"] + c.get("crit_chance_pct", 0)),
            "idle_move_cm_s": baseline["move_cm_s"] * (1 + capped("move_speed_pct", c.get("move_speed_pct", 0)) / 100),
            "unarmored_focus_regen_per_s": baseline["focus_regen_per_s"] * (1 + capped("focus_regen_pct", c.get("focus_regen_pct", 0)) / 100),
        })

    for number in (1, 2, 3):
        example(number, profile)

    def negative(e: dict[str, Any]) -> None:
        signed = {}
        for a in e["negative_affixes"]:
            definition = affixes[a["id"]]
            interval = definition["tiers"][a["tier"] - 1]
            value = a["signed_value"]
            if definition["direction"] != -1 or not interval["min"] <= -value <= interval["max"]:
                raise ValueError(f"Illegal negative magnitude {a}")
            signed[definition["stat"]] = value
        fields(e, {"cases_are_separate_legal_gear_states": True})
        health_pct = capped("max_health_pct", full["max_health_pct"] + signed["max_health_pct"])
        heal_pct = capped("healing_received_pct", full["healing_received_pct"] + signed["healing_received_pct"])
        damage_pct = capped("damage_pct", full["damage_pct"] + signed["damage_pct"])
        fields(e["expected"], {
            "max_hp_with_health_curse": baseline["max_hp"] * (1 + health_pct / 100),
            "healing_received_pct_with_healing_curse": heal_pct,
            "REC001_base30_before_missing_HP_clip": potion_base * (1 + heal_pct / 100),
            "KNF001_grade0_damage_with_damage_curse": weapons["WPN-KNF-001"]["damage_total"] * (1 + damage_pct / 100),
        })

    example(4, negative)

    def damage_cap(e: dict[str, Any]) -> None:
        grow = growth["stat_merge"]["weapon"]["contribution_by_grade"][3]
        affix = affixes["AFF-P-001"]["tiers"][-1]["max"]
        source_id = e["other_damage_source_id"]
        other = item_stat(source_id, "damage_pct")
        subtotal = full["damage_pct"] + grow + affix
        total = subtotal + other
        final = capped("damage_pct", total)
        fields(e, {
            "base_segment": weapons[e["content_id"]]["damage_total"],
            "talent_damage_pct": full["damage_pct"], "basic_grade3_damage_pct": grow,
            "affix_damage_pct": affix, "subtotal_pct": subtotal,
            "headroom_pct_points": stats["damage_pct"]["max_value"] - subtotal,
            "with_other_legally_active_damage_pct": other, "raw_sum_with_other_pct": total,
            "clamped_pct": final, "direct_before_other_factors": e["base_segment"] * (1 + final / 100),
            "inactive_backup_damage_contributes": False,
        })

    example(5, damage_cap)

    def negative_interval(e: dict[str, Any]) -> None:
        intrinsic = armor[e["content_id"]]["armor"]
        interval = affixes[e["negative_affix_id"]]["tiers"][e["tier"] - 1]
        next_interval = affixes[e["negative_affix_id"]]["tiers"][4]
        legal = [interval["min"], min(interval["max"], intrinsic)]
        if legal[0] > legal[1]:
            legal = []
        fields(e, {
            "intrinsic_armor": intrinsic, "talent_guard_armor_ward_each": full["armor_flat"],
            "unarmored_final_armor_ward_each": capped("armor_flat", full["armor_flat"]),
            "grade3_growth_armor_flat": intrinsic * growth["stat_merge"]["armor"]["per_grade_ratio_of_intrinsic"] * 3,
            "armor_before_enchant_with_talent": intrinsic * 1.15 + full["armor_flat"],
            "tier_interval": [interval["min"], interval["max"]],
            "legal_interval_using_original_base": legal,
            "tier5_interval": [next_interval["min"], next_interval["max"]],
            "tier5_legal_interval": [] if next_interval["min"] > intrinsic else [next_interval["min"], min(next_interval["max"], intrinsic)],
        })

    example(6, negative_interval)

    def critical_stagger(e: dict[str, Any]) -> None:
        crit_affix = affixes["AFF-P-005"]["tiers"][-1]["max"]
        stagger_affix = affixes["AFF-P-003"]["tiers"][-1]["max"]
        raw_crit = baseline["crit_chance_pct"] + full["crit_chance_pct"] + crit_affix
        raw_stagger = full["stagger_pct"] + stagger_affix
        direct = weapons["WPN-KNF-001"]["stagger_total"] * (1 + capped("stagger_pct", raw_stagger) / 100)
        shock = stats["shock_flat"]["max_value"]
        fields(e, {
            "raw_crit_pct": raw_crit, "final_crit_pct": capped("crit_chance_pct", raw_crit),
            "raw_stagger_pct": raw_stagger, "final_stagger_pct": capped("stagger_pct", raw_stagger),
            "KNF001_final_direct_stagger": direct, "eligible_shock_flat": shock,
            "nominal_direct_plus_independent_shock": direct + shock,
            "one_crit_draw_per_AttackID": True, "shock_not_multiplied_by_stagger_pct": True,
            "target_poise_protection_and_shock_ICD_still_apply": True,
        })

    example(7, critical_stagger)

    def healing(e: dict[str, Any]) -> None:
        budgets = [int(n) for n in re.findall(r"最多(\d+)HP", stats["lifesteal_pct"]["cap_scope"])]
        if len(budgets) != 2:
            raise ValueError("Could not read the two explicit legacy lifesteal source budgets")
        candidate = e["actual_eligible_direct_hp_loss"] * stats["lifesteal_pct"]["max_value"] / 100 * (1 + full["healing_received_pct"] / 100)
        fields(e, {
            "snapshot_lifesteal_pct": stats["lifesteal_pct"]["max_value"],
            "current_healing_received_pct": full["healing_received_pct"],
            "candidate_heal": candidate, "attack_heal_budget_remaining": budgets[0],
            "rolling_1s_budget_remaining": budgets[1],
            "actual_heal": min(candidate, budgets[0], budgets[1], e["hp_missing"]),
            "dead_recipient_actual_heal": 0, "dead_consumes_budget": False,
        })

    example(8, healing)

    def reload(e: dict[str, Any]) -> None:
        w = weapons[e["content_id"]]
        modifier = affixes["AFF-P-008"]["tiers"][-1]["max"]
        total = full["reload_speed_pct"] + modifier
        fields(e, {
            "base_reload_s": w["reload_s"], "talent_reload_speed_pct": full["reload_speed_pct"],
            "talent_only_reload_s": w["reload_s"] / (1 + full["reload_speed_pct"] / 100),
            "with_affix_reload_speed_pct": modifier, "raw_sum_pct": total,
            "clamped_sum_pct": capped("reload_speed_pct", total),
            "capped_reload_s": w["reload_s"] / (1 + capped("reload_speed_pct", total) / 100),
            "KNF_and_STF_effective_reload_benefit": 0,
            "primary_recovery_unchanged_s": w["recovery_s"],
            "XBW_primary_windup_unchanged_s": w["windup_s"],
            "magazine_capacity_unchanged": w["magazine"],
        })

    example(9, reload)

    def focus(e: dict[str, Any]) -> None:
        a = armor[e["armor_id"]]
        trait_rate = re.search(r"替换为([0-9.]+)/s", a["trait"])
        standing = re.search(r"连续维持([0-9.]+)\s*s", a["trait"])
        if not trait_rate or not standing:
            raise ValueError("Could not read the legacy robe's replacement rate/standing requirement")
        conditional = float(trait_rate.group(1))
        scale = 1 + full["focus_regen_pct"] / 100
        fields(e, {
            "talent_focus_regen_pct": full["focus_regen_pct"],
            "unarmored_base_rate": baseline["focus_regen_per_s"],
            "unarmored_rate": baseline["focus_regen_per_s"] * scale,
            "unarmored_delay_s": baseline["focus_delay_s"],
            "armor_normal_base_rate": a["focus_regen_per_s"],
            "armor_conditional_replacement_base_rate": conditional,
            "normal_rate": a["focus_regen_per_s"] * scale, "conditional_rate": conditional * scale,
            "armor_delay_s": a["focus_regen_delay_s"], "standing_condition_s": float(standing.group(1)),
            "focus_cap": baseline["focus"], "changes_last_spend_time": False,
        })

    example(10, focus)

    def movement(e: dict[str, Any]) -> None:
        a = armor[e["armor_id"]]
        other = 2 * affixes["AFF-P-020"]["tiers"][-1]["max"]
        total = full["move_speed_pct"] + other
        stat_bonus = capped("move_speed_pct", total)
        raw_idle = a["move_multiplier"] * (1 + stat_bonus / 100)
        idle = clamp(raw_idle, *caps["normal_move_multiplier_final"])
        move = baseline["move_cm_s"] * idle
        jump = player["jump"]
        fields(e, {
            "base_move_cm_s": baseline["move_cm_s"], "talent_move_speed_pct": full["move_speed_pct"],
            "other_move_speed_pct": other, "raw_sum_pct": total, "clamped_bonus_pct": stat_bonus,
            "current_armor_multiplier": a["move_multiplier"], "raw_idle_multiplier_after_stat_cap": raw_idle,
            "final_idle_multiplier": idle, "final_idle_move_cm_s": move,
            "air_move_constraint": jump["air_move_multiplier"],
            "air_XY_speed_with_same_context_cm_s": move * jump["air_move_multiplier"],
            "dodge_duration_s": player["dodge"]["duration_s"], "dodge_distance_cm": player["dodge"]["distance_cm"],
            "jump_launch_speed_cm_s": jump["launch_speed_cm_s"], "jump_gravity_cm_s2": jump["gravity_cm_s2"],
            "jump_apex_cm": jump["launch_speed_cm_s"] ** 2 / (2 * jump["gravity_cm_s2"]),
            "jump_height_and_dodge_not_scaled": True,
        })

    example(11, movement)

    def headroom(e: dict[str, Any]) -> None:
        a = armor[e["armor_id"]]
        grade_bonus = a["armor"] * growth["stat_merge"]["armor"]["per_grade_ratio_of_intrinsic"] * 3
        positive = affixes["AFF-P-014"]["tiers"][-1]["max"]
        total = capped("armor_flat", a["armor"] + grade_bonus + full["armor_flat"] + positive)
        fields(e, {"base_armor": a["armor"], "grade3_growth_flat": grade_bonus,
                   "guard_talent_flat": full["armor_flat"], "positive_affix_flat": positive,
                   "final_armor_without_other": total, "armor_headroom_points": stats["armor_flat"]["max_value"] - total})
        expected = {s: stats[s]["max_value"] - full[s] for s in ("damage_pct", "stagger_pct", "max_health_pct", "healing_received_pct", "move_speed_pct", "focus_regen_pct", "reload_speed_pct")}
        expected["crit_chance_pct_final"] = stats["crit_chance_pct"]["max_value"] - baseline["crit_chance_pct"] - full["crit_chance_pct"]
        fields(e["full_talent_headroom_without_other"], expected)

    example(12, headroom)

    def cost(e: dict[str, Any]) -> None:
        fields(e, {"branch_rank_totals": [r for r, _ in branch_rows], "branch_cost_totals": [c for _, c in branch_rows],
                   "total_ranks": rank_total, "full_catalogue_cost_shards": scheduled_cost,
                   "full_reset_refund_if_all_paid_at_this_catalogue_schedule": scheduled_cost,
                   "partial_example_paid_and_refund": examples["TAL-EX-002"]["actual_scheduled_cost_shards"]})

    example(13, cost)

    def synthetic(e: dict[str, Any]) -> None:
        health = capped("max_health_pct", e["non_talent_max_health_pct"] + full["max_health_pct"])
        fields(e, {"talent_max_health_pct": full["max_health_pct"], "final_max_health_pct": health,
                   "final_max_hp": baseline["max_hp"] * (1 + health / 100),
                   "talent_healing_received_pct": full["healing_received_pct"],
                   "final_healing_received_pct": capped("healing_received_pct", e["non_talent_healing_received_pct"] + full["healing_received_pct"]),
                   "talent_armor_flat": full["armor_flat"],
                   "final_armor": capped("armor_flat", e["non_talent_armor_total"] + full["armor_flat"]),
                   "direct_stat_clamp_once": True})

    example(14, synthetic)

    def economy_scope(e: dict[str, Any]) -> None:
        econ = data["economy"]["baseline_totals"]
        fields(e, {"THR001_base_damage_talent_multiplier": 1, "burn_base6_dps_talent_multiplier": 1,
                   "shock_flat10_talent_multiplier": 1, "D08_main_gross_gold": econ["gross_gold"],
                   "D08_repeat_main_fragments": econ["repeat_shards"],
                   "D08_first_main_extra_fragments": econ["first_main_boss_extra"],
                   "permanent_economy_multiplier": 1, "extra_inventory_or_talent_slots": 0,
                   "revival_count_granted": 0, "action_speed_pct_granted": 0,
                   "drop_probability_delta": 0, "shop_discount_pct_granted": 0})

    example(15, economy_scope)

    changed = []
    for source in talents["source_preservation"]:
        path = ROOT / source["path"]
        try:
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            if digest != source["sha256"]:
                changed.append(source["path"])
        except OSError:
            changed.append(source["path"])
    check(not changed, "Preserved source hashes changed: " + ", ".join(changed))
    return result


if __name__ == "__main__":
    print(json.dumps({"scope": "static_design_reference_calculations_not_UE_tests", **validate()}, ensure_ascii=False, indent=2))
