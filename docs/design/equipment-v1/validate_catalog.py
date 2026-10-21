"""Validate and export the design catalogue; does not test or modify the game."""
from __future__ import annotations

import csv
import json
import math
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FAMILIES = ("KNF", "DAO", "SWD", "GSW", "SPR", "HAL", "XBW", "PST", "SGN", "RFL", "STF")
ARMOR_TYPES = ("LGT", "MED", "HVY", "ROB")
WEAPON_FIELDS = "id name family role damage_total damage_expression windup_s active_s recovery_s cycle_s range_cm depth_halfwidth_cm min_range_cm move_multiplier stagger_total magazine reload_s ammo_per_trigger focus_cost projectile_speed_cm_s primary_pattern secondary trait tradeoff animation audio_vfx acquisition status".split()
SECONDARY_FIELDS = "name action damage_total windup_s active_s recovery_s cycle_s cooldown_s range_cm depth_halfwidth_cm stagger_total ammo_cost focus_cost tradeoff".split()
ARMOR_FIELDS = "id name type role armor ward move_multiplier poise_bonus focus_regen_per_s focus_regen_delay_s trait tradeoff appearance acquisition status".split()


def read(name: str):
    return json.loads((ROOT / name).read_text(encoding="utf-8-sig"))


def write(name: str, data):
    (ROOT / name).write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main():
    weapons = read("weapons-melee.json") + read("weapons-ranged.json")
    armor = read("armor.json")
    errors = []
    checks = 0

    def check(condition, message):
        nonlocal checks
        checks += 1
        if not condition:
            errors.append(message)

    def number(obj, key, context, minimum=0, maximum=None):
        value = obj.get(key)
        good = isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)
        check(good, f"{context}: {key} must be a finite number")
        if good:
            check(value >= minimum and (maximum is None or value <= maximum), f"{context}: {key} outside allowed bounds")
        return good

    def fields(obj, expected, context):
        check(isinstance(obj, dict), f"{context}: not an object")
        for key in expected:
            check(key in obj, f"{context}: missing {key}")
            if key in obj and isinstance(obj[key], str):
                check(bool(obj[key].strip()), f"{context}: empty {key}")

    def timing(obj, context):
        good = all(number(obj, key, context) for key in ("windup_s", "active_s", "recovery_s", "cycle_s"))
        if good:
            check(obj["windup_s"] > 0 and obj["active_s"] > 0 and obj["recovery_s"] > 0, f"{context}: timing phases must be positive")
            check(abs(obj["windup_s"] + obj["active_s"] + obj["recovery_s"] - obj["cycle_s"]) < 0.00001, f"{context}: timing phases do not sum to cycle")

    check(len(weapons) == 33, "expected 33 weapons")
    check(len(armor) == 12, "expected 12 armor sets")
    ids = [w.get("id") for w in weapons + armor]
    check(len(set(ids)) == 45, "IDs must be unique across all 45 entries")
    check(len({w.get("name") for w in weapons + armor}) == 45, "names must be unique across all 45 entries")
    check(Counter(w.get("family") for w in weapons) == Counter({f: 3 for f in FAMILIES}), "expected 3 weapons per family")
    check(Counter(a.get("type") for a in armor) == Counter({f: 3 for f in ARMOR_TYPES}), "expected 3 armor sets per type")

    for w in weapons:
        ident = w.get("id", "unknown weapon")
        fields(w, WEAPON_FIELDS, ident)
        check(ident in {f"WPN-{f}-{n:03}" for f in FAMILIES for n in (1, 2, 3)}, f"{ident}: invalid stable ID")
        check(w.get("status") == "design_only", f"{ident}: must not claim implementation")
        timing(w, ident)
        for key in ("damage_total", "range_cm", "depth_halfwidth_cm", "stagger_total", "projectile_speed_cm_s"):
            number(w, key, ident)
        number(w, "min_range_cm", ident)
        number(w, "move_multiplier", ident, maximum=1)
        number(w, "magazine", ident)
        number(w, "reload_s", ident)
        number(w, "ammo_per_trigger", ident)
        number(w, "focus_cost", ident, maximum=100)
        check(w["range_cm"] > w["min_range_cm"], f"{ident}: invalid minimum range")
        check(w["depth_halfwidth_cm"] > 0, f"{ident}: no depth tolerance")
        for key in ("magazine", "ammo_per_trigger"):
            check(isinstance(w[key], int), f"{ident}: {key} must be an integer")
        s = w.get("secondary", {})
        fields(s, SECONDARY_FIELDS, ident + " secondary")
        timing(s, ident + " secondary")
        for key in ("damage_total", "cooldown_s", "range_cm", "depth_halfwidth_cm", "stagger_total", "ammo_cost"):
            number(s, key, ident + " secondary")
        number(s, "focus_cost", ident + " secondary", maximum=100)
        check(isinstance(s["ammo_cost"], int), f"{ident}: secondary ammo cost must be integer")
        check(s["cooldown_s"] > 0, f"{ident}: secondary cooldown must be positive")
        if w["family"] in FAMILIES[:6]:
            check(all(w[k] == 0 for k in ("magazine", "reload_s", "ammo_per_trigger", "focus_cost", "projectile_speed_cm_s")), f"{ident}: melee has ranged resource fields")
            check(s["ammo_cost"] == 0 and s["focus_cost"] == 0, f"{ident}: melee secondary unexpectedly uses resources")
        elif w["family"] == "STF":
            check(all(w[k] == 0 for k in ("magazine", "reload_s", "ammo_per_trigger")), f"{ident}: staff has magazine fields")
            check(w["focus_cost"] > 0 and s["focus_cost"] > 0 and s["ammo_cost"] == 0, f"{ident}: staff resource mismatch")
        else:
            check(w["magazine"] > 0 and w["reload_s"] > 0 and 0 < w["ammo_per_trigger"] <= w["magazine"], f"{ident}: invalid magazine/reload")
            check(w["focus_cost"] == 0 and s["focus_cost"] == 0 and 0 <= s["ammo_cost"] <= w["magazine"], f"{ident}: firearm/crossbow resource mismatch")
            check(s["ammo_cost"] > 0 or ident == "WPN-RFL-003", f"{ident}: only the explicitly melee bayonet secondary is ammo-free")
            check(w["projectile_speed_cm_s"] == 0 if w["family"] == "SGN" else w["projectile_speed_cm_s"] > 0, f"{ident}: expected instant shotgun rays or a positive flying-projectile speed")

    for a in armor:
        ident = a.get("id", "unknown armor")
        fields(a, ARMOR_FIELDS, ident)
        check(ident in {f"ARM-{f}-{n:03}" for f in ARMOR_TYPES for n in (1, 2, 3)}, f"{ident}: invalid stable ID")
        check(a.get("status") == "design_only", f"{ident}: must not claim implementation")
        for key in ("armor", "ward", "poise_bonus", "focus_regen_per_s", "focus_regen_delay_s"):
            number(a, key, ident)
        number(a, "move_multiplier", ident, minimum=0.5, maximum=1.15)
        check(a["armor"] <= 150 and a["ward"] <= 150, f"{ident}: base stat already exceeds reduction cap threshold")

    # Check local links in the design entry and design documents, without network access.
    import re
    md_files = [ROOT.parents[2] / "武器与防具设计总览.md", *ROOT.glob("*.md")]
    for md in md_files:
        check(md.is_file(), f"missing design document: {md.name}")
        if not md.is_file():
            continue
        for link in re.findall(r"\]\(([^)]+)\)", md.read_text(encoding="utf-8-sig")):
            if "://" in link or link.startswith("#"):
                continue
            target = (md.parent / link.split("#")[0]).resolve()
            # Exports below are intentionally not present on the initial run.
            check(target.is_file() or target.name in {"weapons.json", "weapons.csv", "armor.csv", "validation-report.json"}, f"{md.name}: broken link {link}")

    report = {
        "schema_version": 1,
        "checked_at": datetime.now(timezone(timedelta(hours=8))).isoformat(timespec="seconds"),
        "status": "passed" if not errors else "failed",
        "checks": checks,
        "weapon_count": len(weapons),
        "armor_count": len(armor),
        "weapon_families": dict(Counter(w["family"] for w in weapons)),
        "armor_types": dict(Counter(a["type"] for a in armor)),
        "errors": errors,
        "scope": "Design data completeness, uniqueness, resource bounds, time sums and local document links only. No game build, runtime, artwork, audio, balance or player-feel validation.",
    }
    write("validation-report.json", report)
    if errors:
        print(json.dumps(report, ensure_ascii=False, indent=2))
        raise SystemExit(1)

    weapons.sort(key=lambda w: (FAMILIES.index(w["family"]), w["id"]))
    armor.sort(key=lambda a: (ARMOR_TYPES.index(a["type"]), a["id"]))
    write("weapons.json", weapons)

    weapon_headers = {
        "id": "编号", "name": "名称", "family": "动作家族", "role": "定位", "damage_total": "主攻总伤害", "damage_expression": "伤害构成",
        "windup_s": "前摇s", "active_s": "有效窗s", "recovery_s": "后摇s", "cycle_s": "完整周期s", "range_cm": "前向距离cm", "depth_halfwidth_cm": "纵深半宽cm", "min_range_cm": "最小距离cm",
        "move_multiplier": "攻击移动倍率", "stagger_total": "主攻削韧", "magazine": "弹匣容量", "reload_s": "装填s", "ammo_per_trigger": "主攻耗弹", "focus_cost": "主攻专注", "projectile_speed_cm_s": "弹速cm每s",
        "primary_pattern": "主攻规则", "trait": "特性", "tradeoff": "代价", "animation": "动作制作", "audio_vfx": "音效与特效", "acquisition": "获取池建议", "status": "状态",
    }
    secondary_headers = {
        "name": "武器技", "action": "武器技规则", "damage_total": "技总伤害", "windup_s": "技前摇s", "active_s": "技有效窗s", "recovery_s": "技后摇s", "cycle_s": "技完整周期s", "cooldown_s": "技冷却s", "range_cm": "技前向距离cm", "depth_halfwidth_cm": "技纵深半宽cm", "stagger_total": "技削韧", "ammo_cost": "技耗弹", "focus_cost": "技专注", "tradeoff": "技代价",
    }
    with (ROOT / "weapons.csv").open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[*weapon_headers.values(), *secondary_headers.values()])
        writer.writeheader()
        for w in weapons:
            row = {label: w[key] for key, label in weapon_headers.items()}
            row.update({label: w["secondary"][key] for key, label in secondary_headers.items()})
            writer.writerow(row)

    armor_headers = {"id": "编号", "name": "名称", "type": "防具类别", "role": "定位", "armor": "物理护甲", "ward": "魔法抗性", "move_multiplier": "移动倍率", "poise_bonus": "韧性加成", "focus_regen_per_s": "专注每秒恢复", "focus_regen_delay_s": "专注恢复延迟s", "trait": "特性", "tradeoff": "代价", "appearance": "外观制作", "acquisition": "获取池建议", "status": "状态"}
    with (ROOT / "armor.csv").open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[*armor_headers.values(), "物理减伤百分比", "魔法减伤百分比", "非攻击移动cm每s", "总韧性阈值"])
        writer.writeheader()
        for a in armor:
            row = {label: a[key] for key, label in armor_headers.items()}
            row.update({"物理减伤百分比": round(min(0.6, a["armor"] / (100 + a["armor"])) * 100, 2), "魔法减伤百分比": round(min(0.6, a["ward"] / (100 + a["ward"])) * 100, 2), "非攻击移动cm每s": round(265 * a["move_multiplier"], 2), "总韧性阈值": 30 + a["poise_bonus"]})
            writer.writerow(row)
    print(json.dumps({k: report[k] for k in ("status", "checks", "weapon_count", "armor_count", "errors")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
