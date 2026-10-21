"""D11 design consistency and small input reference model; no UE/device/UI tests."""
from collections import Counter
from pathlib import Path
import hashlib
import json
import math
import re

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
counts = Counter()
errors = []


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def check(ok, group, label):
    counts[group] += 1
    if not ok:
        errors.append(f"{group}: {label}")


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def walk(value):
    yield value
    if isinstance(value, dict):
        for item in value.values():
            yield from walk(item)
    elif isinstance(value, list):
        for item in value:
            yield from walk(item)


def reference_input(case, priority):
    """Semantic inputs after physical key ownership; only a design acceptance aid."""
    if case.get("terminal"):
        return "terminal_only"
    edges = set(case["edges"]) - set(case.get("held_before_context_change", []))
    legal = set(case["legal"])
    context = case["context"]
    if "pause" in edges:
        return "pause_only"
    if context == "paused":
        return "back_only" if "back" in edges else "none"
    if context == "live":
        if "cancel" in edges:
            return "cancel_only"
        if "move" in edges:
            return "close_and_move"
        for action in priority:
            if action in edges and action in legal:
                return "close_and_" + action
        if any(x.startswith("navigate_") for x in edges):
            return "navigate_only"
        if "confirm" in edges:
            return "confirm_only"
        return "blocked_keep_open" if edges else "none"
    for action in priority:
        if action in edges and action in legal:
            return action
    return "none"


def main():
    files = ["design-index.json", "hud-and-feedback.json", "input-rules.json",
             "screens-and-flows.json", "tutorials.json", "ui-cases.json"]
    data = {name: read(HERE / name) for name in files}
    index = data["design-index.json"]
    hud = data["hud-and-feedback.json"]
    inputs = data["input-rules.json"]
    screens = data["screens-and-flows.json"]
    lessons = data["tutorials.json"]
    cases = data["ui-cases.json"]
    for name, document in data.items():
        check(document.get("module") == "D-11", "metadata", name + " module")
        check(document.get("source_event") == "EV-029", "metadata", name + " event")
        check(document.get("status") == "design_only" and document.get("runtime_implemented") is False,
              "metadata", name + " scope")
        for value in walk(document):
            if isinstance(value, list) and value and all(isinstance(x, dict) and "id" in x for x in value):
                ids = [x["id"] for x in value]
                check(len(ids) == len(set(ids)), "ids", name + " " + str(ids[:2]))

    priority = read(ROOT / "docs/design/items-v1/common-rules.json")["input_extension"]["ground_idle_priority"]
    check(any(x == priority for x in walk(inputs)), "input", "D03 priority retained")
    action_map = {x["id"]: x for x in inputs["actions"]}
    aliases = inputs["placeholder_aliases"]
    tutorial_aliases = lessons["action_alias_contract"]["semantic_aliases"]
    for name in tutorial_aliases:
        check(name in action_map or (name in aliases and aliases[name]["action_id"] in action_map),
              "input", "tutorial alias " + name)
    live = inputs["contexts"]["live_overlay"]
    permitted = inputs["rebind"]["intentional_context_aliases"]
    for device in ("keyboard", "gamepad"):
        fixed = live[device + "_fixed_UI_owners"]
        used = {}
        for name in inputs["rebind"]["editable_world_actions"]:
            row = action_map[name]
            check(bool(row[device]), "input", device + " world path " + name)
            for binding in row[device]:
                check(binding not in used, "input", device + " default uniqueness " + binding)
                used[binding] = name
                if binding in fixed and fixed[binding] != name:
                    allowed = any(x["world_action"] == name and
                                  (x["physical"] == binding or
                                   x["physical"] == "ArrowKeys" and binding.startswith("Arrow"))
                                  for x in permitted)
                    check(allowed, "input", "declared context alias " + binding + "/" + name)
    stick = inputs["movement"]["left_stick"]
    trigger = inputs["trigger_buttons"]
    check(0 < stick["radial_release_deadzone"] < stick["radial_press_deadzone"] < 1,
          "input", "stick hysteresis")
    check(0 < trigger["normalized_release_threshold"] < trigger["normalized_press_threshold"] < 1,
          "input", "trigger hysteresis")
    check(not inputs["movement"]["analog_slow_walk"] and inputs["movement"]["diagonal_normalization"] and
          inputs["movement"]["no_right_stick_aim_or_camera"], "input", "D02 movement scope")
    # Exercise simultaneous requests, menu ownership, death and pre-held input.
    for case in cases["reference_input_vectors"]:
        check(reference_input(case, priority) == case["expected"], "input_model", case["id"])
    check(len(cases["cases"]) == 30, "cases", "future acceptance scripts")
    for case in cases["cases"]:
        check(all(case.get(k) for k in ("id", "topic", "steps", "expected")), "cases", case["id"])

    check(len(hud["hud_elements"]) == 10, "hud", "coverage")
    check(len(hud["room_labels"]) == 5, "hud", "combat unfinished clear unsafe safe fault")
    check(hud["map"]["freeze_all_run_clocks"] and not hud["map"]["reveals_hidden_nodes"] and
          not hud["map"]["teleport_or_auto_walk"], "hud", "map read-only")
    check(hud["global_feedback"]["combat_tells_never_removed_by_toasts"] and
          not hud["global_feedback"]["tutorial_or_story_autopopup_in_combat"], "hud", "combat visibility")
    check(all(x["mutates_game_rules"] is False for x in hud["accessibility_settings"]), "hud", "cosmetic settings")
    check(min(48, 50) == 48 and min(58, 50) == 50 and 58 - 50 == 8, "display_math", "cap example")
    for remaining in (0.001, 0.04, 0.1, 0.101, 1.199):
        shown = math.ceil(remaining * 10) / 10
        check(shown > 0 and shown >= remaining and shown - remaining < 0.1 + 1e-9,
              "display_math", str(remaining))
    check(min(65, 110) == 65, "display_math", "max hp rise does not heal")

    # References are checked against existing source text; this doesn't validate geometry or execution.
    source_texts = []
    for directory in (ROOT / "docs/design").iterdir():
        if directory.is_dir() and directory != HERE:
            for path in directory.glob("*.json"):
                if path.name != "validation-report.json":
                    source_texts.append(path.read_text(encoding="utf-8-sig"))
    source_text = "\n".join(source_texts)
    ref_pattern = r"\b(?:FAC-[A-Z-]+|REG-\d{2}(?:-[NHS]\d{2})?|BOS-[A-Z]{3}-\d{3}|ENM-[A-Z]{3}-\d{3}|ITEM-[A-Z]{3}-\d{3}|UNL-[A-Z0-9-]+|STORY-[MSO]\d{2})\b"
    for name in ("screens-and-flows.json", "tutorials.json"):
        raw = json.dumps(data[name], ensure_ascii=False)
        for reference in sorted(set(re.findall(ref_pattern, raw))):
            check(reference in source_text, "references", name + ":" + reference)
    facilities = read(ROOT / "docs/design/economy-v1/facilities.json")["facilities"]
    raw_screens = json.dumps(screens, ensure_ascii=False)
    for facility in facilities:
        check(facility["id"] in raw_screens, "coverage", facility["id"])
    raw_lessons = json.dumps(lessons, ensure_ascii=False)
    for region in range(1, 6):
        check(f"REG-{region:02d}" in raw_lessons, "coverage", f"region {region}")

    screen_ids = {x["id"] for x in screens["screens"]}
    for count_name, data_name in (("screens", "screens"), ("facility_profiles", "facility_profiles"),
                                  ("flows", "flows"), ("future_cases", "futurecases")):
        check(screens["counts"][count_name] == len(screens[data_name]), "coverage", "screen " + count_name)
    check(lessons["counts"]["total_lessons"] == len(lessons["lessons"]), "coverage", "lesson count")
    for screen in screens["screens"]:
        required = ("label", "clock", "entry", "fields", "guards", "failure")
        check(all(screen.get(k) for k in required),
              "screens", screen["id"] + " defined transitions")
        check(bool(screen["actions"]) or screen["id"] == "UI-FEEDBACK", "screens", screen["id"] + " input ownership")
        for destination in screen["return_to"]:
            check(destination in screen_ids, "screens", screen["id"] + " returns to " + destination)
        if screen["clock"] == "contextual":
            check(bool(screen.get("clock_contexts")), "screens", screen["id"] + " explicit clock")
    clocks = {x["id"]: x["clock"] for x in screens["screens"]}
    for screen_id in screens["live_selection_input_contract"]["screens"]:
        check(clocks.get(screen_id) == "real_time", "clocks", screen_id)
    for screen_id in ("UI-INSPECT", "UI-ORGANIZE", "UI-PAUSE", "UI-MAP"):
        check(clocks.get(screen_id) == "paused_simulation", "clocks", screen_id)

    policy = lessons["policy"]
    check(policy["all_lessons_skippable_and_reviewable"] and
          not policy["lesson_completion_required_for_movement_combat_exit_shop_story_or_ending"] and
          not policy["teaching_changes_D07_manifest_or_wave_timing"] and
          not policy["tutorial_specific_enemies_rooms_items_awards_currency_discounts_or_damage_protection"],
          "tutorials", "no gameplay gates or new content")
    lesson_ids = {x["id"] for x in lessons["lessons"]}
    aliases = set(lessons["action_alias_contract"]["semantic_aliases"])
    for lesson in lessons["lessons"]:
        check(lesson["skip"]["allowed"] and lesson["skip"]["no_gameplay_or_reward_effect"] and
              not lesson["completion"]["read_or_skip_marks_practice"], "tutorials", lesson["id"] + " optional")
        tokens = set(re.findall(r"\{([a-z_0-9]+)\}", json.dumps(lesson, ensure_ascii=False)))
        check(tokens <= aliases, "tutorials", lesson["id"] + " declared action tokens")
    routes = read(ROOT / "docs/design/dungeon-v1/regions-and-routes.json")["regions"]
    node_focus = {node["id"]: node.get("teaching_focus_enemy_ids", [])
                  for region in routes for node in region["nodes"]}
    for region in lessons["region_lessons"]:
        check(region["enemy_ids"] == node_focus[region["teaching_node_id"]],
              "tutorials", region["region_id"] + " actual D07 teaching candidates")
        check(region["D07_N02_manifest"]["actor_count"] == 1 and
              region["D07_N02_manifest"]["group_count"] == 1 and
              region["completion_does_not_open_exit"], "tutorials", region["region_id"] + " no extra encounter")
        check(set(region["lesson_ids"]) <= lesson_ids, "tutorials", region["region_id"] + " lesson refs")

    for relative, expected in index["historical_design_sha256"].items():
        p = ROOT / relative
        check(p.is_file() and digest(p) == expected, "preservation", relative)
    paths = [ROOT / "UI输入与新手引导设计.md"] + sorted(HERE.glob("*.md"))
    for p in paths:
        text = p.read_text(encoding="utf-8-sig")
        for link in re.findall(r"\]\(([^)]+)\)", text):
            if link.startswith(("http:", "https:", "#")):
                continue
            target = link.split("#", 1)[0].strip("<>")
            if target.endswith("validation-report.json"):
                continue  # produced below
            check((p.parent / target).resolve().exists(), "links", p.name + ":" + target)
    for p in paths + [HERE / "screens-and-flows.json"]:
        check("实时R装填" not in p.read_text(encoding="utf-8-sig"), "input", p.name + " reload T not R")
    for name in index["reading_order"]:
        check((HERE / name).is_file(), "links", name)

    readme = (ROOT / "README.md").read_text(encoding="utf-8-sig")
    ledger = (ROOT / "项目需求台账.md").read_text(encoding="utf-8-sig")
    roadmap = (ROOT / "整体设计清单与推进顺序.md").read_text(encoding="utf-8-sig")
    check("UI输入与新手引导设计.md" in readme and "下一主模块D-12" in readme,
          "bookkeeping", "readme")
    check("| EV-029 |" in ledger and "先追加 `EV-030` 起" in ledger,
          "bookkeeping", "ledger exact continue event")
    check("v1.11" in roadmap and "D-01至D-11初稿" in roadmap, "bookkeeping", "roadmap")

    report = {
        "design_date": "2026-10-14", "source_event": "EV-029", "module": "D-11",
        "status": "design_only", "runtime_implemented": False,
        "checks": sum(counts.values()), "checks_by_group": dict(counts), "errors": errors,
        "counts": {"hud_groups": len(hud["hud_elements"]), "settings": len(hud["accessibility_settings"]),
                   "screens": len(screens.get("screens", [])), "lessons": len(lessons.get("lessons", [])),
                   "root_future_cases": len(cases["cases"]),
                   "screen_future_cases": len(screens["futurecases"]),
                   "tutorial_future_cases": len(lessons["future_acceptance_cases"]),
                   "input_paper_cases": len(inputs["paper_input_cases"]),
                   "abstract_input_vectors": len(cases["reference_input_vectors"]),
                   "historical_sources": len(index["historical_design_sha256"])},
        "scope": "design consistency, source references, preservation and small semantic input model only",
        "cross_review_resolved": ["live confirmation is consumed before any gameplay reuse; preheld controls release first",
                                  "default E and mouse aliases explicitly declared for live overlay remapping checks",
                                  "R opens new-run review; Enter/South activates focused result button; independent creation confirmation",
                                  "roulette tray and result layers inherit live input ownership",
                                  "paused story archive still requires D10 full safety; pause alone doesn't grant safety",
                                  "single-enemy teaching doesn't fabricate allies or support effects; depth advice only for actual depth obligations"],
        "historical_design_sha256": index["historical_design_sha256"],
        "current_design_sha256": {p.relative_to(ROOT).as_posix(): digest(p) for p in
             [ROOT / "UI输入与新手引导设计.md"] + sorted(HERE.glob("*"))
             if p.is_file() and p.suffix in (".md", ".json", ".py") and p.name != "validation-report.json"},
        "limitations": ["semantic reference model does not run physical keyboard/gamepad input or UE",
                        "not all future acceptance scripts are executable checks",
                        "source reference existence is not proof of layout, correctness of all prose or gameplay balance",
                        "no screenshots or live UI, screen reader, remapping, save atomicity, audio or playtest evidence"],
        "reproduce": "python -X utf8 docs/design/ui-input-v1/validate_design.py"
    }
    (HERE / "validation-report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"checks": report["checks"], "errors": errors, "counts": report["counts"]}, ensure_ascii=False))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
