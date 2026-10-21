"""D-12 static design validator. Does not run UE or certify art/audio quality."""
from pathlib import Path
from collections import Counter
import hashlib
import json
import re
import struct
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
errors = []
checks = Counter()
cache = {}


def check(ok, category, label):
    checks[category] += 1
    if not ok:
        errors.append(f"{category}: {label}")


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def sha(path):
    path = path.resolve()
    if path not in cache:
        cache[path] = hashlib.sha256(path.read_bytes()).hexdigest()
    return cache[path]


def ids(rows, key="id"):
    return {row[key] for row in rows}


def unique(rows, label, key="id"):
    check(len(ids(rows, key)) == len(rows), "identity", label)


def resolve_ref(ref):
    name, _, pointer = ref.partition("#")
    path = (HERE / name).resolve()
    if not path.is_file():
        raise ValueError(f"missing {ref}")
    value = read(path)
    if pointer:
        if not pointer.startswith("/"):
            raise ValueError(f"bad pointer {ref}")
        for part in pointer[1:].split("/"):
            part = part.replace("~1", "/").replace("~0", "~")
            value = value[int(part)] if isinstance(value, list) else value[part]
    return value


def walk(value):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk(child)


def strings(value):
    if isinstance(value, dict):
        for child in value.values():
            yield from strings(child)
    elif isinstance(value, list):
        for child in value:
            yield from strings(child)
    elif isinstance(value, str):
        yield value


def main():
    docs = {p.stem: read(p) for p in HERE.glob("*.json") if p.name != "validation-report.json"}
    for name, data in docs.items():
        check(data["module"] == "D-12" and data["source_event"] == "EV-030", "metadata", name)
        check(data["status"] == "design_only" and data["runtime_implemented"] is False, "metadata", name + " scope")
        check(data["design_date"] == "2026-10-14", "metadata", name + " date")
        for ref in set(strings(data)):
            if re.fullmatch(r"\.\./[^\s#]+\.json(?:#/[\w/~.\-]+)?", ref):
                try:
                    resolve_ref(ref)
                    check(True, "source_reference", ref)
                except (KeyError, ValueError, IndexError) as exc:
                    check(False, "source_reference", str(exc))

    weapon = docs["weapon-motion"]
    enemies = docs["enemy-environment-fx"]
    audio = docs["audio-and-assets"]
    visual = docs["visual-rules"]
    plan = docs["production-plan"]
    cases = docs["presentation-cases"]
    index = docs["design-index"]
    weapons = read(HERE / "../equipment-v1/weapons.json")
    armor = read(HERE / "../equipment-v1/armor.json")
    enemy_source = read(HERE / "../enemies-v1/enemies.json")
    boss_source = read(HERE / "../bosses-v1/bosses.json")["bosses"]
    regions = read(HERE / "../dungeon-v1/regions-and-routes.json")["regions"]
    family_ids = {w["family"] for w in weapons}
    check(ids(weapon["families"]) == family_ids and len(family_ids) == 11, "coverage", "11 weapon families")
    check(ids(weapon["weapon_variants"]) == ids(weapons) and len(weapons) == 33, "coverage", "33 weapons")
    check(ids(weapon["armor_profiles"]) == ids(armor) and len(armor) == 12, "coverage", "12 armor")
    for key in ["families", "weapon_variants", "armor_profiles"]:
        unique(weapon[key], key)
    motion_ids = []
    by_weapon = {w["id"]: w for w in weapons}
    for w in weapon["weapon_variants"]:
        original = by_weapon[w["id"]]
        check(w["family"] == original["family"] and w["name"] == original["name"], "weapon_binding", w["id"])
        check(w["secondary"]["name"] == original["secondary"]["name"], "weapon_binding", w["id"] + " skill")
        check(resolve_ref(w["source_ref"])["id"] == w["id"], "weapon_binding", w["id"] + " pointer")
        motion_ids += [w["primary"]["motion_profile_id"], w["secondary"]["motion_profile_id"]]
    check(len(motion_ids) == len(set(motion_ids)) == 66, "coverage", "66 unique action bindings")
    for family in weapon["families"]:
        check(set(family["weapon_ids"]) == {w["id"] for w in weapons if w["family"] == family["id"]}, "weapon_binding", family["id"])
    for a in weapon["armor_profiles"]:
        original = resolve_ref(a["source_ref"])
        check(original["id"] == a["id"] and original["name"] == a["name"], "weapon_binding", a["id"])
        check(set(a["compatible_weapon_families"]) == family_ids and not a["new_block_or_movement"], "weapon_binding", a["id"] + " compatibility")

    source_actors = {e["id"]: e for e in enemy_source["enemies"] + enemy_source["elite_variants"]}
    source_bosses = {b["id"]: b for b in boss_source}
    attacks = {}
    expected_bindings = {}
    for actor in enemy_source["enemies"] + boss_source:
        expected_bindings[actor["id"]] = ids(actor["attacks"])
        for attack in actor["attacks"]:
            attacks[attack["id"]] = attack
    for elite in enemy_source["elite_variants"]:
        extra = elite.get("extra_attack", elite.get("attack_override"))
        attacks[extra["id"]] = extra
        expected_bindings[elite["id"]] = expected_bindings[elite["parent_id"]] | {extra["id"]}
        if extra.get("original_attack_retained") is False:
            expected_bindings[elite["id"]].remove(extra["replaces_attack_id"])
    check(ids(enemies["enemy_profiles"]) == set(source_actors), "coverage", "28 base + 9 elite")
    check(ids(enemies["boss_profiles"]) == set(source_bosses), "coverage", "7 bosses")
    check(ids(enemies["region_profiles"]) == ids(regions), "coverage", "5 regions")
    check(ids(enemies["enemy_family_profiles"]) == {e["family"] for e in source_actors.values()}, "coverage", "9 enemy families")
    check(ids(enemies["attack_cue_profiles"], "attack_id") == set(attacks) and len(attacks) == 92, "coverage", "65 + 27 source attack definitions")
    for key in ["enemy_profiles", "boss_profiles", "region_profiles", "enemy_family_profiles", "attack_cue_profiles", "fx_events"]:
        unique(enemies[key], key)
    cues = {c["id"]: c for c in enemies["attack_cue_profiles"]}
    for actor in enemies["enemy_profiles"] + enemies["boss_profiles"]:
        bindings = actor["attack_bindings"]
        check(ids(bindings, "attack_id") == expected_bindings[actor["id"]], "enemy_binding", actor["id"])
        for binding in bindings:
            check(cues.get(binding["cue_id"], {}).get("attack_id") == binding["attack_id"], "enemy_binding", binding["attack_id"])
    fx_ids = ids(enemies["fx_events"])
    for cue in cues.values():
        check(resolve_ref(cue["source_attack_ref"]) == attacks[cue["attack_id"]], "enemy_binding", cue["id"] + " source")
        check(set(cue["fx_event_ids"]) <= fx_ids, "enemy_binding", cue["id"] + " FX")

    unique(audio["audio_events"], "audio events")
    check(len(audio["audio_events"]) == 40, "coverage", "40 audio events")
    check(ids(audio["weapon_family_profiles"], "family_id") == family_ids, "coverage", "audio weapon families")
    check(ids(audio["music_regions"], "region_id") == ids(regions), "coverage", "audio regions")
    check(ids(audio["music_bosses"], "boss_id") == set(source_bosses), "coverage", "audio bosses")
    for a in audio["audio_events"]:
        check(a["source_event_contract"]["writes_gameplay_state"] is False, "audio_authority", a["id"])
    for profile in audio["weapon_family_profiles"]:
        check(set(profile["common_event_ids"]) <= ids(audio["audio_events"]), "audio_authority", profile["family_id"])

    audit = audio["local_asset_audit"]
    file_records = {}
    for record in walk(audit):
        if {"path", "bytes", "sha256"} <= record.keys():
            file_records[record["path"]] = record
    for rel, record in file_records.items():
        path = ROOT / rel
        check(path.is_file(), "asset_evidence", rel + " exists")
        if path.is_file():
            check(path.stat().st_size == record["bytes"] and sha(path) == record["sha256"], "asset_evidence", rel + " bytes/hash")
    packages = audit["packages"]
    check(len(packages) == 8 and sum(p["archive"]["bytes"] for p in packages) == 94920296, "asset_inventory", "8 original ZIPs / bytes")
    extracted_count = 0
    for p in packages:
        actual_count = sum(f.is_file() for f in (ROOT / p["extracted_root"]).rglob("*"))
        extracted_count += actual_count
        check(actual_count == p["actual_counts"]["extracted_files"], "asset_inventory", p["id"] + " extracted file count")
        check(bool(p["license_evidence"]), "asset_inventory", p["id"] + " local license evidence")
    check(extracted_count == 1007, "asset_inventory", "1007 extracted files")
    source_ogg = {p.relative_to(ROOT).as_posix() for p in (ROOT / "source-assets").rglob("*.ogg")}
    check(source_ogg == {a["path"] for a in audit["audio_files"]} and len(source_ogg) == 205, "asset_inventory", "exact 205 OGG file set")
    header_counts = Counter()
    for record in audit["audio_files"]:
        header = (ROOT / record["path"]).read_bytes()[:512]
        offset = header.find(b"\x01vorbis")
        check(header.startswith(b"OggS") and offset >= 0, "audio_header", record["path"])
        if offset >= 0:
            channels = header[offset + 11]
            rate = struct.unpack_from("<I", header, offset + 12)[0]
            header_counts[rate] += 1
            check(channels == record["channels"] == 2 and rate == record["sample_rate_hz"], "audio_header", record["path"] + " format")
    check(header_counts == {44100: 153, 48000: 52}, "asset_inventory", "audio headers; not decode/listening")
    check(sum(a["preview_only"] for a in audit["audio_files"]) == 1, "asset_inventory", "one preview not individual SFX")
    pngs = audit["prototype_2D"]["files"]
    check(len(pngs) == 69 and sum('/items/' in p['path'] for p in pngs) == 5, "asset_inventory", "64 frames + 5 icons")
    for record in pngs:
        header = (ROOT / record["path"]).read_bytes()[:26]
        check(header[:8] == b"\x89PNG\r\n\x1a\n" and struct.unpack(">II", header[16:24]) == (256, 256) and header[24:26] == bytes([8, 6]), "image_header", record["path"])

    projection = visual["spatial_contract"]["projection_trial"]
    for c in cases["projection_reference_cases"]:
        x, y, z = c["point"]
        cx, cy = c["camera"]
        ox, oy = projection["origin_px"]
        actual = [ox + (x-cx)*projection["x_px_per_cm"], oy - (y-cy)*projection["depth_px_per_cm"] - z*projection["height_px_per_cm"]]
        check(all(abs(a-b) < 1e-9 for a, b in zip(actual, c["expected"])), "reference_arithmetic", c["id"])
    for c in cases["attachment_reference_cases"]:
        px, py = c["pivot"]
        u, v = c["local_cm"]
        scale = c["scale"]
        point = [px + c["facing"]*u*scale, py-v*scale]
        trimmed = [a-b for a, b in zip(point, c["trim_offset"])]
        check(point == c["expected_untrimmed"] and trimmed == c["expected_trimmed"], "reference_arithmetic", c["id"])
    coverage = {c["id"]: c for c in plan["coverage_targets"]}
    check(coverage["COV-HERO-ACTIONS"]["semantic_count"] == len(set(coverage["COV-HERO-ACTIONS"]["channels"])) == 17, "production", "shared pose channels")
    check(coverage["COV-ICONS"]["semantic_count"] == 33+12+36, "production", "icon identity bindings")
    check(coverage["COV-WEAPONS"]["motion_bindings"] == len(motion_ids), "production", "motion binding count")
    combo = plan["combination_cost_model"]
    check(combo["weapon_armor_identity_pairs"] == len(weapons)*len(armor) and combo["left_right_standing_pair_checks"] == len(weapons)*len(armor)*2, "production", "combination cost arithmetic")
    for example in plan["memory_estimate_examples"]:
        value = example["frames"]*example["width"]*example["height"]*example["bytes_per_pixel"]*example["layers"]
        check(value == example["raw_rgba_bytes"] and value/1048576 == example["raw_mib"], "reference_arithmetic", example["id"])
    clock = visual["animation_clock_contract"]
    check(clock["hit_accent_s"]["maximum"] == weapon["presentation_hitstop"]["ceiling_s"] == .08, "timing_contract", "local accent ceiling")
    check(weapon["presentation_hitstop"]["simulation_clock_paused"] is False and weapon["presentation_hitstop"]["gameplay_modified"] is False, "timing_contract", "no gameplay pause")
    check(visual["spatial_contract"]["jump_height_changes_ground_depth_key"] is False and visual["spatial_contract"]["sprite_bounds_drive_body_or_hurtbox"] is False, "spatial_contract", "no art collision/depth authority")
    unique(cases["cases"], "future cases")
    check(len(cases["cases"]) == 24, "coverage", "24 future runtime cases; not executed")

    for group in ["historical_design_sha256", "observed_existing_code_and_manifest_sha256"]:
        for rel, digest in index[group].items():
            path = ROOT / rel
            check(path.is_file() and sha(path) == digest, "preservation", rel)
    for rel in [index["overview"]] + index["reading_order"]:
        check((HERE / rel).is_file(), "navigation", rel)
    overview = (HERE / index["overview"]).resolve()
    for path in [overview] + list(HERE.glob("*.md")):
        for target in re.findall(r"\]\(([^)]+)\)", path.read_text(encoding="utf-8-sig")):
            if not re.match(r"(?:https?:|#)", target):
                local = target.split("#")[0].strip("<>")
                if local and not local.endswith("validation-report.json"):
                    check((path.parent / local).is_file(), "navigation", path.name + " -> " + target)
    ledger = (ROOT / "项目需求台账.md").read_text(encoding="utf-8-sig")
    events = re.findall(r"^\| EV-(\d{3}) \|", ledger, re.M)
    check(events == [f"{n:03d}" for n in range(1, 31)], "bookkeeping", "EV-001..030 continuous")
    row = next(line for line in ledger.splitlines() if line.startswith("| EV-030 |"))
    check('“ok”' in row and '2026-10-14' in row and '不新增独立REQ' in row, "bookkeeping", "exact user event and scope")
    check('下一事件EV-031' in ledger, "bookkeeping", "next event")
    for name in ["README.md", "AGENTS.md", "整体设计清单与推进顺序.md"]:
        body = (ROOT/name).read_text(encoding="utf-8-sig")
        check('EV-030' in body and 'D-13' in body and '美术动画特效与音频规范.md' in body, "bookkeeping", name)
    check('v1.12' in (ROOT/'整体设计清单与推进顺序.md').read_text(encoding='utf-8-sig'), "bookkeeping", "roadmap version")
    return docs


if __name__ == "__main__":
    docs = {}
    try:
        docs = main()
    except Exception as exc:
        errors.append(f"validator_exception: {type(exc).__name__}: {exc}")
    tracked = [p for p in HERE.iterdir() if p.suffix in {".json", ".md", ".py"} and p.name != "validation-report.json"]
    tracked += [ROOT/'美术动画特效与音频规范.md']
    report = {
        "module": "D-12", "design_date": "2026-10-14", "source_event": "EV-030",
        "status": "static_design_checks_passed" if not errors else "needs_correction",
        "checks": sum(checks.values()), "check_groups": dict(checks), "errors": errors,
        "runtime_implemented": False, "runtime_tested_this_turn": False,
        "art_style_approved": False, "new_assets_generated": 0, "audio_auditioned": False,
        "future_runtime_cases": 24, "future_runtime_cases_executed": 0,
        "historical_design_sha256": docs.get('design-index', {}).get('historical_design_sha256', {}),
        "observed_existing_code_and_manifest_sha256": docs.get('design-index', {}).get('observed_existing_code_and_manifest_sha256', {}),
        "current_design_sha256": {p.relative_to(ROOT).as_posix(): sha(p) for p in sorted(tracked)},
        "limits": [
            "Checks catalogue IDs, source pointers, file hashes/counts/headers, projection/attachment and idealized memory arithmetic.",
            "Archive-to-extracted member byte equality was checked by the local asset audit; this validator rechecks archive hashes and extracted counts, not all member byte equality.",
            "Does not decode or audition audio, render assets, measure FPS/memory, run UE, certify style, balance, animation feel, dynamic room visibility, or release licensing.",
            "All future runtime cases remain unexecuted; design prose still requires runtime implementation and review."
        ]
    }
    (HERE/'validation-report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({k: report[k] for k in ['status','checks','check_groups','errors']}, ensure_ascii=False))
    sys.exit(1 if errors else 0)
