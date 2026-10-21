"""Private stdlib source checks and unused-package import for new0.96 XBW walk only.

No Pillow, network, image generation, resampling or UE dependency in preflight.
The existing native PNG helper is read-only. Engine APIs are imported lazily.
"""
from pathlib import Path
from datetime import datetime, timezone
import copy
import importlib.util
import json
import math
import struct
import sys
import zlib

ROOT = Path(__file__).resolve().parents[2]
PRODUCTION = (ROOT / "source-assets/production").resolve()
TOPIC = PRODUCTION / "first-batch-XBW-walk-v001"
BODY_MANIFEST = TOPIC / "manifests/import-XBW-common-walk-v002.json"
ARMOR_MANIFEST = TOPIC / "manifests/import-XBW-walk-four-armors-v002.json"
NEUTRAL_MANIFEST = TOPIC / "manifests/XBW-walk-neutral-state-minus1-extension-v003.json"
BODY_MANIFEST_SHA256 = "901e9e307a0654ae8c6f8385af2a9b4be94b063e06bfde2ca77cf43db1d1deab"
ARMOR_MANIFEST_SHA256 = "c14a031fbd674dadb11f4a4d363f9e65e6bac2b724e39533625f2df24f59cac2"
NEUTRAL_MANIFEST_SHA256 = "f7c0a4d77528b361208fd72185063ff64f0354a0ac222e27ebbac04bdf4678e1"
BODY_TRACKS = ("body_far", "body_support", "body_near")
ARMOR_TRACKS = ("armor_far", "armor_near")
ARMORS = ("ARM-LGT-001", "ARM-MED-001", "ARM-HVY-001", "ARM-ROB-001")
JOBS = {
    "body": (BODY_MANIFEST, BODY_MANIFEST_SHA256, "/Game/Production/FirstBatch/v022/XBWWalk", 18),
    "armor": (ARMOR_MANIFEST, ARMOR_MANIFEST_SHA256, "/Game/Production/FirstBatch/v023/XBWArmorWalk", 48),
}
OLD_PINS = {
    "body094": (TOPIC / "manifests/import-XBW-common-walk-v001.json", "7185df2ad077ec92d020788f84f2f9b890dc7d042ceb7656d0a9576177d471a5"),
    "armor094": (TOPIC / "manifests/import-XBW-walk-four-armors-v001.json", "35b3a0cffc9fb731a40ff4a08cde7d5e89b5f7fceff67824feb08f31849e7ff4"),
    "lifecycle": (PRODUCTION / "first-batch-weapon-actions-v001/manifests/weapon-state-lifecycle-v001.json", "94f2d3b6163f620babe8d5d550cacbeb7204ca69f8b3942ebdc27f512e72fffe"),
    "components": (PRODUCTION / "first-batch-weapon-components-v001/manifests/import-weapon-components-v001.json", "275794953add2f130f0b7912fa9e01a16c21e4e017957af4c4d9c7793c240d68"),
    "reload": (PRODUCTION / "first-batch-weapon-actions-v001/manifests/import-XBW-reload-four-keyposes-v001.json", "9a0f99a5b32a5b898b9fa98d4b40812daf5e532a73954f13df91a7c166297ee8"),
}
PROCESSOR = Path("C:/Users/22499/.codex/skills/generate2dsprite/scripts/generate2dsprite.py").resolve()
PROCESSOR_SHA256 = "7b7451a711f9dbf806db1586567920dbe2a487d481b7f016e14db66d8050997b"
ARCHIVE_TOPICS = {
    "first-batch-XBW-walk-v001": "2026-10-15_猎弩真实持握步行与四甲_v001",
    "first-batch-weapon-actions-v001": "2026-10-15_首批武器专属动作_v001",
    "first-batch-weapon-components-v001": "2026-10-15_首批独立武器组件_v001",
}
spec = importlib.util.spec_from_file_location("xbw_v002_native_png", Path(__file__).with_name("ue-import-armor-primary2-four-v001.py"))
native = importlib.util.module_from_spec(spec)
spec.loader.exec_module(native)
require = native.require


def finite(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def point(m, p):
    require(isinstance(m, list) and len(m) == 6 and all(finite(x) for x in m), "Nonfinite/wrong affine")
    require(isinstance(p, (list, tuple)) and len(p) == 2 and all(finite(x) for x in p), "Nonfinite/wrong point")
    return [m[0] * p[0] + m[1] * p[1] + m[2], m[3] * p[0] + m[4] * p[1] + m[5]]


def close(a, b, message, tolerance=1e-8):
    require(len(a) == len(b) and all(finite(x) and finite(y) and abs(x - y) <= tolerance for x, y in zip(a, b)), message)


def require_unused_disk_destination(destination):
    require(not destination.exists() or not any(p.is_file() for p in destination.rglob("*")), "Destination has files; refusing overwrite")


def require_exact_registered_set(actual, expected):
    require(len(actual) == len(expected) and set(actual) == set(expected), "Registry contains missing/extra/duplicate objects")


def rgba_bytes(data):
    """Pixel decode after the existing inspector has validated header/CRC/extent.

    Keep actual RGBA for source reconstruction and hand overlap tests, which the
    existing inspector's alpha/bbox summary alone cannot prove.
    """
    chunks, offset = [], 8
    while offset + 12 <= len(data):
        length = struct.unpack_from(">I", data, offset)[0]
        kind = data[offset + 4:offset + 8]
        if kind == b"IDAT":
            chunks.append(data[offset + 8:offset + 8 + length])
        offset += length + 12
        if kind == b"IEND":
            break
    raw = zlib.decompress(b"".join(chunks))
    stride, previous, result = 2048, bytearray(2048), bytearray()
    for y in range(512):
        start = y * 2049
        filtering, row = raw[start], bytearray(raw[start + 1:start + 2049])
        if filtering:
            for i in range(stride):
                a, b, c = row[i - 4] if i >= 4 else 0, previous[i], previous[i - 4] if i >= 4 else 0
                if filtering == 1:
                    predictor = a
                elif filtering == 2:
                    predictor = b
                elif filtering == 3:
                    predictor = (a + b) // 2
                else:
                    p = a + b - c
                    aa, bb, cc = abs(p - a), abs(p - b), abs(p - c)
                    predictor = a if aa <= bb and aa <= cc else b if bb <= cc else c
                row[i] = (row[i] + predictor) & 255
        result.extend(row)
        previous = row
    return bytes(result)


class Sources:
    def __init__(self):
        self.hashes, self.bytes, self.pixels = {}, {}, {}
        self.originals = {}
        self.external_exact = {PROCESSOR: PROCESSOR_SHA256}
        self.archive_count = 0
        self.archive_indexes = {}

    def check(self, path, digest):
        path = Path(path).resolve()
        require(isinstance(digest, str) and len(digest) == 64 and all(x in "0123456789abcdef" for x in digest), "Malformed SHA256")
        require(path not in self.hashes or self.hashes[path] == digest, "Contradictory frozen source hashes")
        if path not in self.hashes:
            self.bytes[path] = native.checked_hash(path, digest)
            self.hashes[path] = digest
        return self.bytes[path]

    def production_path(self, value):
        return native.source_path(value)

    def import_path(self, value):
        path = self.production_path(value)
        require(path.is_relative_to(TOPIC.resolve()), "Import texture escapes new walk topic")
        return path

    def load(self, path, digest):
        return json.loads(self.check(path, digest).decode("utf-8-sig"))

    def add_provenance(self, record):
        require(isinstance(record, dict) and "raw_path" in record and "raw_sha256" in record and "tool_original_path" in record, "Missing frozen native provenance")
        raw, original, digest = self.production_path(record["raw_path"]), Path(record["tool_original_path"]).resolve(), record["raw_sha256"]
        require(record.get("tool_original_sha256", digest) == digest, "Tool/raw SHA mismatch")
        # Exact filenames come only from fixed-SHA historical contracts. This
        # dictionary is NOT a generated_images-root wildcard permission.
        require(original not in self.originals or self.originals[original] == digest, "Conflicting tool original")
        self.originals[original] = digest
        self.check(raw, digest)
        self.check(original, digest)

    def references(self, node):
        if isinstance(node, dict):
            for key, value in node.items():
                hk = "sha256" if key == "path" else key[:-5] + "_sha256" if key.endswith("_path") else key + "_sha256"
                if isinstance(value, str) and hk in node:
                    path, digest = Path(value).resolve(), node[hk]
                    if key == "tool_original_path":
                        require(self.originals.get(path) == digest, "Unlisted exact tool original")
                    elif path in self.external_exact:
                        require(self.external_exact[path] == digest, "Changed exact processor/timing reference")
                    else:
                        path = self.production_path(value)
                    self.check(path, digest)
                self.references(value)
        elif isinstance(node, list):
            for value in node:
                self.references(value)

    def texture(self, item, imported=False):
        path = self.import_path(item["path"]) if imported else self.production_path(item["path"])
        data = self.check(path, item["sha256"])
        if path not in self.pixels:
            meta = native.inspect_rgba_png(data)
            require(meta["nonempty"] and meta["corners_transparent"] and meta["alpha_extrema"] == [0, 255], "Invalid actual native alpha")
            self.pixels[path] = (meta, rgba_bytes(data))
        meta, pixels = self.pixels[path]
        for key in ("canvas_px", "mode", "alpha_extrema", "bbox_px", "corner_alpha"):
            if key in item:
                require(meta[key] == item[key], "Actual PNG metadata differs: " + key)
        return meta, pixels

    def archive(self, source, digest):
        source = Path(source).resolve()
        rel = source.relative_to(PRODUCTION)
        require(rel.parts[0] in ARCHIVE_TOPICS, "Archive check requires an exact known source topic")
        topic = ARCHIVE_TOPICS[rel.parts[0]]
        for archive_root in (ROOT / "过程图稿与视频", Path("E:/OurGame/Knight/过程图稿与视频")):
            folder = (archive_root / topic).resolve()
            if folder not in self.archive_indexes:
                data = json.loads((folder / "index.json").read_text("utf-8-sig"))
                self.archive_indexes[folder] = data["files"]
            matches = [x for x in self.archive_indexes[folder] if Path(x["source"]).resolve() == source and x["sha256"] == digest]
            require(len(matches) == 1, "Missing/duplicate exact archive reference: " + str(source))
            row = matches[0]
            relative = Path(row["relative"])
            require(not relative.is_absolute() and ".." not in relative.parts, "Unsafe archive relative path")
            for category in ("原件", "展示副本"):
                path = (folder / category / relative).resolve()
                require(path.is_relative_to(folder), "Archive path escaped exact topic")
                data = self.check(path, digest)
                require(len(data) == row["bytes"], "Archive byte extent differs")
                self.archive_count += 1


def validate_semantics(body, armor, neutral, historical, component):
    require(body["schema"] == "frozen-XBW-walk-three-body-track-subset-v2" and body["version"] == 2 and body["frozen"] is True, "Wrong new body schema")
    require(armor["schema"] == "frozen-XBW-pose-armor-layer-subset-v2" and armor["version"] == 2 and armor["frozen"] is True, "Wrong new armor schema")
    require(neutral["version"] == 3 and neutral["frozen"] is True and neutral["component_state_index"] == -1, "Wrong neutral extension")
    for data in (body, armor):
        require(data["clip"] == "walk" and data["weapon_id"] == "WPN-XBW-001" and data["frame_count"] == 6 and data["canvas_px"] == [512, 512] and data["root_px"] == [256, 472], "Changed walk identity/count/canvas/root")
        require(data["duration_s"] == .6 and data["loop"] is True and data["new_generation_calls"] == 0 and data["BodySize160_changed"] is False and data["movespeed_changed"] is False, "Visual import must not change timing/gameplay")
        require(data["runtime_verified"] is False and data["footlock_certified"] is False, "Source import cannot accept runtime/footlock")
    require(body["draw_order"] == ["body_far", "independent_weapon", "body_support", "body_near"], "Changed body draw order")
    require(armor["draw_order"] == ["body_far", "armor_far", "independent_weapon", "body_support", "armor_near", "body_near"], "Changed armor draw order")
    require(body["body_shared_scale"] == .96 and body["fixed_weapon_scale"] == .48 and body["support_fit_gate_px"] == 3.129 and body["initial_component_state_index"] == -1 and body["initial_Ammo1_neutral_minus1_preserved"] is True, "Changed uniform scale/gate/initialneutral")
    require(armor["shared_armor_raw_transform_scale"] == .96 / .94 and armor["all24pose_transform_is_same_root_centered_uniform"] is True and armor["semantic_full_armor_acceptance"] is False and armor["full_equipment_combinations_complete"] is False, "Changed common garment transform or acceptance")
    require(armor["source_body_contract_path"] == str(BODY_MANIFEST) and armor["source_body_contract_sha256"] == BODY_MANIFEST_SHA256 and armor["common_body"] == body["frames"], "Armor substituted common body")
    require(neutral["source_body_contract_sha256"] == BODY_MANIFEST_SHA256 and neutral["source_body_contract_path"] == str(BODY_MANIFEST) and neutral["fixed_scale"] == .48 and neutral["existing_error_ceiling_not_relaxed_px"] == 3.129 and neutral["initial_Ammo1_state_minus1_preserved"] is True and neutral["lifecycle_changes"] is False, "Changed neutral body/lifecycle")
    require(neutral["support_fit_gate_passed_all_frames"] is True and neutral["support_fit_failed_frame_indices"] == [] and neutral["runtime_verified"] is False and neutral["production_accepted"] is False, "Changed neutral source/runtime gates")
    require([f["index"] for f in body["frames"]] == list(range(6)) and [f["index"] for f in neutral["frames"]] == list(range(6)), "Missing/duplicate/reordered body or neutral indices")
    require(set(armor["armors"]) == set(ARMORS), "Wrong four armor IDs")
    props = {-1: (component["path"], component["sha256"], component["primary_grip_px"], component["support_grip_px"], component["emit_px"])}
    for state in (0, 3):
        p = historical["lifecycle"]["states"][state]
        props[state] = (p["path"], p["sha256"], p["stock_grip_px"], p["support_grip_px"], p["emit_px"])
    for frame, old in zip(body["frames"], historical["body094"]["frames"]):
        i = frame["index"]
        require(frame["root_px"] == frame["ground_root_px"] == [256, 472] and frame["phase"] == "walk" and frame["weapon_visible"] is True, "Changed frame root/phase")
        close([frame["time_start_s"], frame["time_end_s"]], [i / 10, (i + 1) / 10], "Changed walk cycle interval")
        require(frame.get("damage_or_projectile_emission_events", []) == [], "Walk image must not issue damage/projectile events")
        require(frame["native_primary_grip_px"] == old["native_primary_grip_px"] and frame["native_support_grip_px"] == old["native_support_grip_px"] and frame["source_sole_px"] == old["source_sole_px"] and frame["source_sole_measurement"] == old["source_sole_measurement"], "Moved native hand or sole/proxy")
        m = frame["source_body_transform_2x3"]
        close(m, [.96, 0, 256 - .96 * 256, 0, .96, 472 - .96 * frame["source_sole_px"][1]], "Not one0.96 native body transform")
        close(point(m, frame["native_primary_grip_px"]), frame["primary_grip_px"], "Primary marker changed")
        close(point(m, frame["native_support_grip_px"]), frame["support_grip_px"], "Support marker changed")
        close(point(m, frame["source_sole_px"]), frame["transformed_sole_px"], "Sole transform differs")
        require(abs(frame["transformed_sole_px"][1] - 472) < 1e-8, "Changed nominal root line")
        mappings = frame["weapon_state_mappings"]
        require(len(mappings) == 3 and {p["state_index"] for p in mappings} == {-1, 0, 3}, "Missing/duplicate actual component state")
        for p in mappings:
            path, digest, stock, support, emit = props[p["state_index"]]
            require((p["path"], p["sha256"], p["stock_grip_px"], p["support_grip_px"], p["virtual_emit_px"]) == (path, digest, stock, support, emit), "Substituted actual component/marker")
            require(p["weapon_scale"] == .48 and p["support_fit_gate_px"] == 3.129 and p["support_fit_gate_passed"] is True and p["runtime_verified"] is False, "Changed component scale/gate")
            angle = math.atan2(frame["support_grip_px"][1] - frame["primary_grip_px"][1], frame["support_grip_px"][0] - frame["primary_grip_px"][0]) - math.atan2(support[1] - stock[1], support[0] - stock[0])
            co, si = .48 * math.cos(angle), .48 * math.sin(angle)
            g = frame["primary_grip_px"]
            expected = [co, -si, g[0] - co * stock[0] + si * stock[1], si, co, g[1] - si * stock[0] - co * stock[1]]
            close(p["component_to_body_affine_2x3"], expected, "Not exact actual-state rigid matrix")
            close([p["weapon_angle_image_clockwise_deg"]], [math.degrees(angle)], "Wrong actual-state art angle")
            close(point(expected, stock), g, "Stock must map exactly to primary hand")
            close(point(expected, support), p["transformed_support_px"], "Support uses different matrix")
            close(point(expected, emit), p["transformed_virtual_emit_body_px"], "Emit uses different matrix")
            error = math.dist(point(expected, support), frame["support_grip_px"])
            require(error <= 3.129 and abs(error - p["support_alignment_error_px"]) < 1e-8, "Actual rigid support residual exceeds3.129")
        n = neutral["frames"][i]
        p = next(p for p in mappings if p["state_index"] == -1)
        require(n["component_state_index"] == -1 and n["component_path"] == p["path"] and n["component_sha256"] == p["sha256"] and n["primary_grip_px"] == frame["primary_grip_px"] and n["support_grip_px"] == frame["support_grip_px"], "Neutral extension differs from actual pose")
        close(n["component_to_body_affine_2x3"], p["component_to_body_affine_2x3"], "Neutral extension uses different matrix")
        close([n["support_alignment_error_px"]], [p["support_alignment_error_px"]], "Neutral extension residual differs")
        for armor_id in ARMORS:
            poses = armor["armors"][armor_id]
            require([f["index"] for f in poses] == list(range(6)), "Missing/reordered armor pose")
            af = poses[i]
            require(af["root_px"] == [256, 472] and af["primary_grip_px"] == frame["primary_grip_px"] and af["support_grip_px"] == frame["support_grip_px"] and af["armor_hidden_back"] is None, "Armor/body root/grip/hidden-layer mismatch")
            ratio = .96 / .94
            close(af["source_geometry_transform_2x3"], [ratio, 0, 256 * (1 - ratio), 0, ratio, 472 * (1 - ratio)], "Not shared garmentN096×invO094")
            require(af["native_raw_single_resampling"] is True and af["old_delivery_RGBA_used_as_resampling_input"] is False and af["source_transformed_pixels_only"] is True and af["source_native_RGBA_pixel_identity"] is False, "Wrong garment native resampling provenance")


def preflight(kind):
    require(kind in JOBS, "Unknown import job")
    sources = Sources()
    body = sources.load(BODY_MANIFEST, BODY_MANIFEST_SHA256)
    armor = sources.load(ARMOR_MANIFEST, ARMOR_MANIFEST_SHA256)
    neutral = sources.load(NEUTRAL_MANIFEST, NEUTRAL_MANIFEST_SHA256)
    history = {key: sources.load(path, digest) for key, (path, digest) in OLD_PINS.items()}
    component = history["components"]["weapons"]["WPN-XBW-001"]
    sources.add_provenance(history["body094"]["source_provenance"])
    for record in history["armor094"]["source_provenance"] + history["reload"]["source_provenance"]:
        sources.add_provenance(record)
    sources.add_provenance(component["source_provenance"])
    timing = history["reload"].get("timing_source", {})
    if isinstance(timing, dict) and "path" in timing:
        path = Path(timing["path"]).resolve()
        require(path == (ROOT / "docs/design/equipment-v1/weapons.json").resolve(), "Unexpected timing source")
        sources.external_exact[path] = timing["sha256"]
    require(Path(body["processor_path"]).resolve() == PROCESSOR and body["processor_sha256"] == PROCESSOR_SHA256, "Unexpected source processor")
    for data in (body, armor, neutral, history["body094"], history["armor094"], history["lifecycle"], history["reload"], component):
        sources.references(data)
    validate_semantics(body, armor, neutral, history, component)
    rows, all_layers, all_digests = [], [], set()
    package = JOBS[kind][2]
    for frame in body["frames"]:
        i, bp = frame["index"], {}
        for track in BODY_TRACKS:
            item = frame[track]
            meta, bp[track] = sources.texture(item, imported=True)
            all_layers.append((item["path"], item["sha256"]))
            all_digests.add(item["sha256"])
            if kind == "body":
                name = f"T_XBWWalk_{track}_{i:03d}_v002"
                rows.append({"frame": i, "track": track, "source": str(sources.import_path(item["path"])), "source_sha256": item["sha256"], "pixels": meta, "name": name, "package_path": package + "/" + name, "object_path": package + "/" + name + "." + name, "root_px": [256, 472]})
        _, source_body = sources.texture({"path": frame["source_body_path"], "sha256": frame["source_body_sha256"]})
        for offset in range(0, len(source_body), 4):
            active = [data[offset:offset + 4] for data in bp.values() if data[offset + 3]]
            require(len(active) <= 1, "Body tracks overlap instead of partitioning native body")
            require((active[0] if active else b"\0\0\0\0") == source_body[offset:offset + 4], "Body3tracks do not reconstruct actual once-transformed source")
        for armor_id in ARMORS:
            af = armor["armors"][armor_id][i]
            _, garment_source = sources.texture({"path": af["source_path"], "sha256": af["source_sha256"]})
            for track in ARMOR_TRACKS:
                item = af[track]
                meta, pixels = sources.texture(item, imported=True)
                all_layers.append((item["path"], item["sha256"]))
                all_digests.add(item["sha256"])
                for offset in range(0, len(pixels), 4):
                    if pixels[offset + 3]:
                        require(not bp["body_near"][offset + 3] and not bp["body_support"][offset + 3], "Garment overlaps actual original hand alpha")
                        require(pixels[offset:offset + 4] == garment_source[offset:offset + 4], "Garment pixel not from actual once-transformed source")
                if kind == "armor":
                    name = f"T_XBWArmorWalk_{armor_id.replace('-', '_')}_{track}_{i:03d}_v002"
                    rows.append({"armor_id": armor_id, "frame": i, "track": track, "source": str(sources.import_path(item["path"])), "source_sha256": item["sha256"], "pixels": meta, "name": name, "package_path": package + "/" + name, "object_path": package + "/" + name + "." + name, "root_px": [256, 472]})
    require(len(all_layers) == 66 and len({Path(p).resolve() for p, _ in all_layers}) == 66 and len(all_digests) == 66, "Expected66unique actual body+armor native RGBA sources")
    require(len(rows) == JOBS[kind][3] and len({r["object_path"] for r in rows}) == len(rows) and len({r["source"] for r in rows}) == len(rows), "Wrong unique import count")
    # Check every current newwalk path and every actually selected weapon prop/raw
    # against exact F/E indexes and both retained categories. C originals never
    # become import inputs and no arbitrary C/E root is accepted.
    archives = dict(all_layers)
    for data in (body, armor):
        for f in data.get("frames", []):
            if "raw_source_path" in f:
                archives[f["raw_source_path"]] = f["raw_source_sha256"]
    for record in [history["body094"]["source_provenance"], *history["armor094"]["source_provenance"], *history["reload"]["source_provenance"], component["source_provenance"]]:
        archives[record["raw_path"]] = record["raw_sha256"]
    for frame in body["frames"]:
        for p in frame["weapon_state_mappings"]:
            archives[p["path"]] = p["sha256"]
    for path, digest in archives.items():
        sources.archive(path, digest)
    destination = ROOT / "UnrealGame/Content" / package.removeprefix("/Game/")
    require_unused_disk_destination(destination)
    return {"rows": rows, "kind": kind, "hashes": sources.hashes, "manifest": body if kind == "body" else armor, "manifest_path": JOBS[kind][0], "manifest_sha256": JOBS[kind][1], "package": package, "expected_count": len(rows), "summary": {"source_validation_success": True, "actual_import_RGBA512_count": len(rows), "actual_joint_RGBA512_layers_verified": 66, "verified_reference_count": len(sources.hashes), "exact_C_tool_original_count": len(sources.originals), "F_E_retained_paths_verified": sources.archive_count, "all18_pose_state_fit_gates_passed": True, "max_support_error_px": body["max_support_alignment_error_px"], "manifest_sha256": JOBS[kind][1], "body_manifest_sha256": BODY_MANIFEST_SHA256, "armor_manifest_sha256": ARMOR_MANIFEST_SHA256, "neutral_manifest_sha256": NEUTRAL_MANIFEST_SHA256, "destination": package, "unreal_import_run": False, "runtime_verified": False, "footlock_certified": False, "full_coverage_accepted": False, "complete20equipment_combinations": False, "full_equipment_combinations_complete": False}}


def import_in_unreal(job):
    import unreal
    require(Path(unreal.Paths.project_dir()).resolve().parent == ROOT, "Wrong UE project")
    rows, package = job["rows"], job["package"]
    receipt = {"schema": "xbw-walk-native-import-receipt-v2", "kind": job["kind"], "utc": datetime.now(timezone.utc).isoformat(), "manifest": str(job["manifest_path"]), "manifest_sha256": job["manifest_sha256"], "body_manifest_sha256": BODY_MANIFEST_SHA256, "armor_manifest_sha256": ARMOR_MANIFEST_SHA256, "neutral_manifest_sha256": NEUTRAL_MANIFEST_SHA256, "destination": package, "expected_count": len(rows), "actual_count": 0, "saved_count": 0, "success": False, "assets": rows, "source_validation": job["summary"], "unreal_import_run": True, "runtime_verified": False, "footlock_certified": False, "full_coverage_accepted": False, "complete20equipment_combinations": False, "full_equipment_combinations_complete": False, "full_weapon_actions_complete": False, "draw_order": job["manifest"]["draw_order"], "canvas_refit": False, "BodySize160_changed": False, "movespeed_changed": False}
    folder = ROOT / "UnrealGame/Saved/Bootstrap"
    receipt_path = folder / ("xbw-" + ("armor-walk" if job["kind"] == "armor" else "walk") + "-v002-import-" + datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S-%f") + ".json")
    try:
        destination = ROOT / "UnrealGame/Content" / package.removeprefix("/Game/")
        require_unused_disk_destination(destination)
        registered = list(unreal.EditorAssetLibrary.list_assets(package, recursive=True, include_folder=False)) if unreal.EditorAssetLibrary.does_directory_exist(package) else []
        require_exact_registered_set(registered, [])
        tasks = []
        for row in rows:
            require(not unreal.EditorAssetLibrary.does_asset_exist(row["package_path"]), "Existing texture; refusing overwrite")
            task = unreal.AssetImportTask()
            for key, value in (("filename", row["source"]), ("destination_path", package), ("destination_name", row["name"]), ("automated", True), ("save", False), ("replace_existing", False)):
                task.set_editor_property(key, value)
            tasks.append(task)
        unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks(tasks)
        settings = {"compression_settings": unreal.TextureCompressionSettings.TC_EDITOR_ICON, "mip_gen_settings": unreal.TextureMipGenSettings.TMGS_NO_MIPMAPS, "lod_group": unreal.TextureGroup.TEXTUREGROUP_UI, "never_stream": True, "srgb": True}
        for row, task in zip(rows, tasks):
            imported = list(task.get_editor_property("imported_object_paths"))
            require(imported == [row["object_path"]], "Unexpected native import object set")
            texture = unreal.load_asset(row["package_path"])
            require(isinstance(texture, unreal.Texture2D), "Expected actual Texture2D")
            for key, value in settings.items():
                texture.set_editor_property(key, value)
                require(texture.get_editor_property(key) == value, "Wrong actual nativeUI setting: " + key)
            size = [texture.blueprint_get_size_x(), texture.blueprint_get_size_y()]
            require(size == [512, 512], "UE changed native512canvas")
            row.update(actual_object_type=texture.get_class().get_name(), imported_object_paths=imported, ue_config={key: value if isinstance(value, bool) else str(texture.get_editor_property(key)) for key, value in settings.items()}, actual_size_px=size, saved=False)
            receipt["actual_count"] += 1
        # Recheck all source + exact retained/tool-original hashes immediately
        # before saving: a concurrent source change invalidates the import.
        for path, digest in job["hashes"].items():
            native.checked_hash(path, digest)
        for row in rows:
            texture = unreal.load_asset(row["package_path"])
            require(unreal.EditorAssetLibrary.save_loaded_asset(texture, False), "Could not save new texture")
            disk = destination / (row["name"] + ".uasset")
            require(disk.is_file() and disk.stat().st_size > 0, "Save returned without actualuasset")
            for key, value in settings.items():
                require(texture.get_editor_property(key) == value, "Saved texture setting changed")
            require([texture.blueprint_get_size_x(), texture.blueprint_get_size_y()] == [512, 512], "Saved dimensions changed")
            row.update(saved=True, saved_uasset=str(disk), saved_bytes=disk.stat().st_size)
            receipt["saved_count"] += 1
        actual = list(unreal.EditorAssetLibrary.list_assets(package, recursive=True, include_folder=False))
        require_exact_registered_set(actual, [row["object_path"] for row in rows])
        require({p.stem for p in destination.glob("*.uasset")} == {r["name"] for r in rows}, "Wrong saved package set")
        receipt["registered_object_paths"] = actual
        receipt["registry_exact_set_passed"] = True
        receipt["success"] = receipt["actual_count"] == receipt["saved_count"] == job["expected_count"]
    except Exception as error:
        receipt["error"] = str(error)
        raise
    finally:
        folder.mkdir(parents=True, exist_ok=True)
        with receipt_path.open("x", encoding="utf-8") as stream:
            json.dump(receipt, stream, ensure_ascii=False, indent=2)
        unreal.log("XBW walkv002 import receipt: " + str(receipt_path))


def run(kind, validate_only=False):
    job = preflight(kind)
    if validate_only:
        print(json.dumps(job["summary"], ensure_ascii=False))
    else:
        import_in_unreal(job)


def self_test():
    body = preflight("body")
    assert len(body["rows"]) == 18, "New0.96body preflight must verify exactly18actual native textures"
    armor = preflight("armor")
    assert len(armor["rows"]) == 48, "Armor preflight must verify exactly48actual native textures"
    checks = 2
    def rejects(call, label):
        nonlocal checks
        try:
            call()
        except (ValueError, KeyError):
            checks += 1
            return
        raise AssertionError("Expected strict rejection: " + label)
    rejects(lambda: require_unused_disk_destination(TOPIC), "populateddisk")
    rejects(lambda: require_exact_registered_set(["/Game/A.A", "/Game/B.B"], ["/Game/A.A"]), "extra registry object")
    rejects(lambda: require_exact_registered_set(["/Game/A.A", "/Game/A.A"], ["/Game/A.A"]), "duplicate registry object")
    s = Sources()
    rejects(lambda: s.references({"tool_original_path": "C:/Windows/win.ini", "tool_original_sha256": "0" * 64}), "arbitraryCtooloriginal")
    rejects(lambda: s.import_path("C:/Windows/win.ini"), "Cimportsource")
    rejects(lambda: s.check(BODY_MANIFEST, "0" * 64), "changedFrozenManifestSHA")
    data = bytearray(Path(body["rows"][0]["source"]).read_bytes())
    data[-1] ^= 1
    rejects(lambda: native.inspect_rgba_png(bytes(data)), "CRCcorruption")
    h = {key: json.loads(path.read_text("utf-8-sig")) for key, (path, _) in OLD_PINS.items()}
    b = json.loads(BODY_MANIFEST.read_text("utf-8-sig")); a = json.loads(ARMOR_MANIFEST.read_text("utf-8-sig")); n = json.loads(NEUTRAL_MANIFEST.read_text("utf-8-sig")); c = h["components"]["weapons"]["WPN-XBW-001"]
    for label, mutate in (
        ("bodyroot", lambda b, a, n: b["frames"][0].update(root_px=[255, 472])),
        ("nonsinglebodyScale", lambda b, a, n: b["frames"][0]["source_body_transform_2x3"].__setitem__(0, .95)),
        ("garmentmatrix", lambda b, a, n: a["armors"][ARMORS[0]][0]["source_geometry_transform_2x3"].__setitem__(2, 0)),
        ("movingspeed", lambda b, a, n: b.update(movespeed_changed=True)),
        ("initialneutralSubstitution", lambda b, a, n: b.update(initial_component_state_index=3)),
        ("supportScale", lambda b, a, n: b["frames"][0]["weapon_state_mappings"][0].update(weapon_scale=.49)),
        ("supportResidualMatrix", lambda b, a, n: b["frames"][0]["weapon_state_mappings"][0]["component_to_body_affine_2x3"].__setitem__(2, 999)),
        ("NaNmatrix", lambda b, a, n: b["frames"][0]["weapon_state_mappings"][0]["component_to_body_affine_2x3"].__setitem__(0, float("nan"))),
        ("relaxedGate", lambda b, a, n: b.update(support_fit_gate_px=3.5)),
        ("walkDamage", lambda b, a, n: b["frames"][0].update(damage_or_projectile_emission_events=[{"damage": 1}])),
        ("changedPhaseClock", lambda b, a, n: b["frames"][0].update(time_end_s=.2)),
        ("changedNativePropMarker", lambda b, a, n: b["frames"][0]["weapon_state_mappings"][0].update(stock_grip_px=[129, 253])),
        ("missingstate", lambda b, a, n: b["frames"][0]["weapon_state_mappings"].pop()),
        ("runtimePromotion", lambda b, a, n: a.update(runtime_verified=True)),
        ("changedDraworder", lambda b, a, n: a["draw_order"].reverse()),
    ):
        bb, aa, nn = copy.deepcopy(b), copy.deepcopy(a), copy.deepcopy(n)
        mutate(bb, aa, nn)
        # Keep the exact shared-body relationship valid for these targeted
        # mutations, so each test reaches its intended semantic/matrix check.
        aa["common_body"] = copy.deepcopy(bb["frames"])
        rejects(lambda: validate_semantics(bb, aa, nn, h, c), label)
    print(json.dumps({"self_tests_passed": checks, "body_count": 18, "armor_count": 48, "actual_joint_RGBA_sources": 66, "UE_import_run": False}, ensure_ascii=False))


if __name__ == "__main__":
    require("--self-test" in sys.argv, "Privatehelper: use one of the two importer entrypoints or--self-test")
    self_test()
