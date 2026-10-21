def pin_path(pin, label, snapshot_rows=None):
    require(isinstance(pin, dict) and {"path", "bytes", "sha256"} <= set(pin), "Missing exact " + label + " pin")
    path = (ROOT / pin["path"]).resolve()
    require(path.is_relative_to(ROOT) and type(pin["bytes"]) is int and pin["bytes"] > 0 and isinstance(pin["sha256"], str) and len(pin["sha256"]) == 64, "Unsafe/invalid " + label + " pin")
    same_pin(path, pin)
    if snapshot_rows is not None:
        key = path.relative_to(ROOT).as_posix()
        require(key in snapshot_rows and snapshot_rows[key]["bytes"] == pin["bytes"] and snapshot_rows[key]["sha256"] == pin["sha256"], label + " is not a frozen compiled input")
    return path


def check_automation(automation, expected):
    count, names = expected["expected_count"], expected["full_test_paths"]
    require(type(count) is int and count >= 157 and isinstance(names, list) and len(names) == len(set(names)) == count and all(isinstance(name, str) and name for name in names), "Explicit current complete test-name set/count invalid")
    tests = automation["tests"]
    require(automation["succeeded"] == len(tests) == count and {row["fullTestPath"] for row in tests} == set(names), "Current automation differs from explicit frozen full test-name set")
    require(all(automation.get(key, 0) == 0 for key in ("failed", "succeededWithWarnings", "notRun", "inProcess")), "Current full suite incomplete or RED")
    require(all(row["state"] == "Success" and row["errors"] == row["warnings"] == 0 for row in tests), "Current full suite entries not clean Success")
    return count


def verify_sources(snapshot, index):
    manifest_path = snapshot / "compiled-source-manifest.json"
    manifest = read(manifest_path)
    require(index["source_manifest_SHA256"] == desc(manifest_path)["sha256"] and (ROOT / index["snapshot"]).resolve() == snapshot, "Capture/snapshot binding differs")
    rows = manifest["files"]; by_path = {row["path"]: row for row in rows}
    require(len(rows) == len(by_path) > 0 and manifest["mismatches"] == 0, "Empty/duplicate/unclean current snapshot")
    for row in rows:
        relative = Path(row["path"])
        require(not relative.is_absolute() and ".." not in relative.parts and relative.as_posix() == row["path"], "Unsafe/noncanonical snapshot path")
        for base in (ROOT, snapshot):
            path = (base / relative).resolve(); require(path.is_relative_to(base), "Snapshot path escapes root"); same_pin(path, row)
    for prefix in ("UnrealGame/Source/", "UnrealGame/Config/", "UnrealGame/Content/Production/"):
        actual = {path.relative_to(ROOT).as_posix() for path in (ROOT / prefix).rglob("*") if path.is_file()}
        require(actual == {key for key in by_path if key.startswith(prefix)}, "Current snapshot omits/invents inputs: " + prefix)
    require("UnrealGame/Binaries/Win64/UnrealEditor-CodexDungeon.dll" in by_path, "Current compiled DLL missing")
    for name in TOOL_FILES:
        require("tools/scripts/" + name in by_path, "Combo tool absent from frozen inputs: " + name)
    same_pin(Path(__file__), by_path["tools/scripts/postprocess-leather-combo-trial-v001.py"])
    contract_path = pin_path(manifest.get("combo_proof_contract"), "combo_proof_contract", by_path)
    contract = read(contract_path)
    require(contract["schema"] == "leather-combo-runtime-proof-contract-v001" and contract["template_only"] is False, "Concrete Root-filled combo runtime contract required")
    require(contract["scope"] == "Ready/P1/P2/P3 matching leather, normal two-facing six-attack proof only", "Wrong runtime contract scope")
    base_path = pin_path(contract["base_snapshot_manifest"], "historical v125 baseline", by_path)
    base = read(base_path)
    old = {row["path"]: row for row in base["files"] if row["path"].startswith("UnrealGame/Content/Production/")}
    production = {key: row for key, row in by_path.items() if key.startswith("UnrealGame/Content/Production/")}
    expected = contract["production"]
    require(len(old) == base["production_packages"] == expected["baseline_count"] == 1115, "Historical v125 old1115 baseline differs")
    require(all(production.get(key) == row for key, row in old.items()), "Historical old1115 package bytes changed")
    require(manifest["production_packages"] == len(production) == expected["expected_total"] and expected["new_packages"] == len(production) - len(old), "Current production count differs from explicit frozen contract")
    require(manifest["old_production_unchanged"] is True and manifest["old_production_packages"] == len(old) and manifest["new_production_packages"] == len(production) - len(old), "Snapshot production delta audit differs")
    native_freeze_path = pin_path(contract["native_source_freeze"], "combo native source freeze", by_path)
    native_freeze = read(native_freeze_path)
    source_candidates = {Path(item["path"]).name: item for item in native_freeze["files"] if Path(item["path"]).resolve().parent == native_freeze_path.parent and Path(item["path"]).name in NATIVE_NAMES}
    require(set(source_candidates) == set(NATIVE_NAMES), "Combo native source freeze missing five production candidates")
    for name, pin in source_candidates.items():
        key = "UnrealGame/Source/CodexDungeon/" + name
        require(key in by_path and by_path[key]["bytes"] == pin["bytes"] and by_path[key]["sha256"] == pin["sha256"], "Current native Source is not exact combo candidate: " + name)
        pin_path(pin, "native source candidate " + name, by_path)
    # Parallel Guard work is allowed when its exact current changes are explicit.
    base_code = {row["path"]: row for row in base["files"] if row["path"].startswith(("UnrealGame/Source/", "UnrealGame/Config/"))}
    current_code = {key: row for key, row in by_path.items() if key.startswith(("UnrealGame/Source/", "UnrealGame/Config/"))}
    require(set(base_code) <= set(current_code), "Historical Source/Config was removed without a new contract")
    native_keys = {"UnrealGame/Source/CodexDungeon/" + name for name in NATIVE_NAMES}
    changed = {key for key, row in current_code.items() if base_code.get(key) != row} - native_keys
    additions = contract["additional_source_pins"]
    require(len({item["path"] for item in additions}) == len(additions) and {item["path"] for item in additions} == changed, "Current non-combo Source changes need explicit additional_source_pins")
    for item in additions: pin_path(item, "additional current Source", by_path)
    report_path = pin_path(contract["current_automation"]["report"], "current full automation report", by_path)
    count = check_automation(read(report_path), contract["current_automation"])
    require((ROOT / manifest["current_automation_report"]).resolve() == report_path and manifest["current_automation_succeeded"] == count and len(manifest["actual_expected_test_names"]) == count and set(manifest["actual_expected_test_names"]) == set(contract["current_automation"]["full_test_paths"]), "Current snapshot/report/test-name contract differs")
    require(set(contract["assemblies"]) == set(CLIPS), "All four assembly source freezes required")
    assembly_sources, assembly_members = [], {}
    for clip, pin in contract["assemblies"].items():
        path = pin_path(pin, clip + " assembly freeze", by_path); assembly = read(path)
        require(assembly["files"] and len({item["path"] for item in assembly["files"]}) == len(assembly["files"]), "Empty/duplicate assembly source freeze")
        assembly_members[clip] = set()
        for item in assembly["files"]:
            relative = Path(item["path"]); source = (path.parent / relative).resolve()
            require(not relative.is_absolute() and ".." not in relative.parts and source.is_relative_to(path.parent), "Unsafe assembly source path")
            current = desc(source); require(current["bytes"] == item["bytes"] and current["sha256"] == item["sha256"], "Assembly source bytes changed")
            pin_path(current, clip + " assembly member", by_path)
            assembly_members[clip].add(source); assembly_sources.append(current)
    imports = contract["imports"]
    require(set(imports) == set(CLIPS), "All four Ready/P1/P2/P3 import pins are required")
    require(imports["Ready"] == base["ready_production_import_receipt"] and imports["Primary1"] == base["new_production_import_receipt"], "Historical actual Ready/P1 receipt pins changed")
    receipt_groups = {}
    for clip, pin in imports.items():
        path = pin_path(pin, clip + " import receipt", by_path)
        receipt_groups.setdefault(path, []).append(clip)
    new_packages, rgba_sources, receipts = set(), [], []
    for path, clips in receipt_groups.items():
        imported = read(path); assets = imported["assets"]
        expected_objects = {object_path(NEW_NS[clip], f"T_Fairytale_Leather{clip}{component}_{frame:03d}_v001") for clip in clips for component in COMPONENTS for frame in range(4 if clip == "Ready" else 6)}
        require(imported["success"] is True and imported["actual_count"] == imported["saved_count"] == imported["expected_count"] == len(assets) == len(expected_objects), "Actual import did not save its full explicit stage set")
        require({asset["object_path"] for asset in assets} == expected_objects, "Receipt object set differs from its referenced clip namespaces")
        for asset in assets:
            clip = next(clip for clip in clips if asset["object_path"].startswith(NEW_NS[clip]))
            require(type(asset["frame"]) is int and asset["component"] in COMPONENTS and asset["actual_object_type"] == "Texture2D", "Actual imported component/frame/type invalid")
            require(asset["object_path"] == object_path(NEW_NS[clip], f"T_Fairytale_Leather{clip}{asset['component']}_{asset['frame']:03d}_v001"), "Imported object metadata differs")
            source = Path(asset["source"]).resolve(); require(source.is_relative_to(ROOT / "source-assets/production") and source in assembly_members[clip], "RGBA import source outside corresponding frozen assembly")
            same_pin(source, {"bytes": asset["source_bytes"], "sha256": asset["source_sha256"]})
            with Image.open(source) as image: require(image.format == "PNG" and image.mode == "RGBA" and image.size == (512, 512), "Original import source is not untouched512 RGBA")
            rgba_sources.append(desc(source)); package = package_file(asset["object_path"])
            require(package in production and production[package]["bytes"] == asset["saved_bytes"] and production[package]["sha256"] == asset["saved_sha256"], "Actual package/receipt bytes differ")
            if clip in ("Primary2", "Primary3"):
                require(package not in old, "New leather stage overwrites historical package"); new_packages.add(package)
        receipts.append(desc(path))
    require(len(new_packages) == expected["new_packages"] == 36 and new_packages == set(production) - set(old) and expected["expected_total"] == expected["baseline_count"] + len(new_packages), "Current new package delta is not exact receipted P2/P3 set")
    return manifest, by_path, {"snapshot": snapshot.as_posix(), "snapshot_files": len(rows), "source_endpoint_checks": 2 * len(rows), "source_mismatches": 0,
        "runtime_proof_contract": desc(contract_path), "base_snapshot_manifest": desc(base_path), "native_source_freeze": desc(native_freeze_path),
        "production_packages": len(production), "old_production_packages_unchanged": len(old), "new_receipted_P2_P3_packages": len(new_packages),
        "current_full_automation_succeeded": count, "actual_complete_test_names": sorted(contract["current_automation"]["full_test_paths"]),
        "actual_import_receipts": receipts, "original_RGBA_source_pins": rgba_sources, "assembly_source_pins": assembly_sources,
        "explicit_additional_source_count": len(additions), "source_and_DLL_unchanged_during_proof": True, "formal_complete_units": 0}
