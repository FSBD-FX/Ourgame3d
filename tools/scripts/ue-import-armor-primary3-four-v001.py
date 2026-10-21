"""Import the frozen 36-texture four-armor primary3 candidate into an unused v012 package.

Ordinary Python: --validate-only performs source/pixel checks without importing UE.
UE Editor Python: execute this file without that flag. No existing asset is edited.
Canvas/root coordinates are preserved; this tool never crops, fits or resamples.
"""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import struct
import sys
import zlib

ROOT = Path(__file__).resolve().parents[2]
SOURCE_ROOT = (ROOT / "source-assets/production").resolve()
MANIFEST = SOURCE_ROOT / "first-unit-armor-layers-v001/manifests/import-armor-primary3-four-v001.json"
MANIFEST_SHA256 = "e97f2958f624e8d27c0942931e48a293c5bee6b33ebfd42148956dfd3f288497"
PACKAGE = "/Game/Production/FirstBatch/v012/ArmorPrimary3"
ARMOR_IDS = ("ARM-LGT-001", "ARM-MED-001", "ARM-HVY-001", "ARM-ROB-001")
EXPECTED_COUNT = 36


def require(condition, message):
    if not condition:
        raise ValueError(message)


def source_path(value):
    path = Path(value).resolve()
    require(path.is_relative_to(SOURCE_ROOT), f"Source escapes production root: {path}")
    require(path.is_file(), f"Missing source: {path}")
    return path


def checked_hash(path, expected):
    data = path.read_bytes()
    actual = hashlib.sha256(data).hexdigest()
    require(actual == expected, f"Changed frozen source: {path}: {actual} != {expected}")
    return data


def inspect_rgba_png(data):
    """Decode native 8-bit RGBA PNG pixels using stdlib, including all five filters.

    UE's bundled Python need not contain Pillow. Chunk CRC, pixel extent and alpha
    are checked from the actual file, rather than trusting the artist metadata.
    """
    require(data[:8] == b"\x89PNG\r\n\x1a\n", "Not a PNG")
    offset, header, payload, ended = 8, None, [], False
    while offset + 12 <= len(data):
        length = struct.unpack_from(">I", data, offset)[0]
        kind = data[offset + 4:offset + 8]
        stop = offset + 12 + length
        require(stop <= len(data), "Truncated PNG chunk")
        body = data[offset + 8:offset + 8 + length]
        crc = struct.unpack_from(">I", data, offset + 8 + length)[0]
        require(zlib.crc32(kind + body) & 0xffffffff == crc, "PNG chunk CRC mismatch")
        if header is None:
            require(kind == b"IHDR" and length == 13, "PNG must begin with IHDR")
            header = struct.unpack(">IIBBBBB", body)
            require(header == (512, 512, 8, 6, 0, 0, 0),
                    f"Expected native 512x512 8-bit RGBA/noninterlaced PNG, got {header}")
        elif kind == b"IHDR":
            raise ValueError("Duplicate PNG header")
        elif kind == b"IDAT":
            payload.append(body)
        elif kind == b"IEND":
            require(length == 0 and stop == len(data), "Invalid PNG end or trailing bytes")
            ended = True
            break
        offset = stop
    require(ended and payload, "Incomplete PNG")
    decoder = zlib.decompressobj()
    raw = decoder.decompress(b"".join(payload)) + decoder.flush()
    require(decoder.eof and not decoder.unused_data and not decoder.unconsumed_tail,
            "Invalid PNG zlib stream")
    stride, height = 512 * 4, 512
    require(len(raw) == (stride + 1) * height, "PNG decompressed extent mismatch")
    previous = bytearray(stride)
    minimum, maximum, left, top, right, bottom = 255, 0, 512, 512, -1, -1
    corners = []
    for y in range(height):
        start = y * (stride + 1)
        filtering = raw[start]
        require(0 <= filtering <= 4, "Unknown PNG row filter")
        row = bytearray(raw[start + 1:start + 1 + stride])
        if filtering:
            for i in range(stride):
                a = row[i - 4] if i >= 4 else 0
                b = previous[i]
                c = previous[i - 4] if i >= 4 else 0
                if filtering == 1:
                    predictor = a
                elif filtering == 2:
                    predictor = b
                elif filtering == 3:
                    predictor = (a + b) // 2
                else:
                    p = a + b - c
                    pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                    predictor = a if pa <= pb and pa <= pc else b if pb <= pc else c
                row[i] = (row[i] + predictor) & 255
        if y == 0 or y == 511:
            corners.extend((row[3], row[stride - 1]))
        alpha = row[3::4]
        minimum, maximum = min(minimum, min(alpha)), max(maximum, max(alpha))
        nonzero = [x for x, value in enumerate(alpha) if value]
        if nonzero:
            left, top = min(left, nonzero[0]), min(top, y)
            right, bottom = max(right, nonzero[-1]), y
        previous = row
    return {"canvas_px": [512, 512], "mode": "RGBA", "bit_depth": 8,
            "alpha_extrema": [minimum, maximum], "corner_alpha": corners,
            "corners_transparent": corners == [0, 0, 0, 0],
            "bbox_px": [left, top, right + 1, bottom + 1] if right >= 0 else None,
            "nonempty": right >= 0, "canvas_transformed": False}


def verify_paired_references(node, hashes):
    """Check all explicit path/hash pairs, including editable/provenance references.

    Unhashed descriptive references are not import inputs. Every imported row must
    carry an expected hash independently of this recursive provenance check.
    """
    if isinstance(node, dict):
        for key, value in node.items():
            hash_key = "sha256" if key == "path" else key[:-5] + "_sha256" if key.endswith("_path") else key + "_sha256"
            if isinstance(value, str) and hash_key in node:
                path = source_path(value)
                expected = node[hash_key]
                require(path not in hashes or hashes[path] == expected, f"Contradictory hashes for {path}")
                if path not in hashes:
                    checked_hash(path, expected)
                    hashes[path] = expected
            verify_paired_references(value, hashes)
    elif isinstance(node, list):
        for value in node:
            verify_paired_references(value, hashes)


def preflight():
    manifest_data = checked_hash(MANIFEST, MANIFEST_SHA256)
    manifest = json.loads(manifest_data.decode("utf-8-sig"))
    require(manifest.get("frozen") is True and manifest.get("clip") == "primary_3", "Not frozen primary3")
    require(manifest.get("frame_count") == 6 and manifest.get("runtime_texture_count_total") == EXPECTED_COUNT, "Total P3 count changed")
    require(manifest.get("runtime_texture_count_new") == 36, "P3 texture count changed")
    require(manifest.get("phase_seconds") == [.22, .12, .32] and manifest.get("phase_frames") == [2, 2, 2], "Frozen phase timing changed")
    require(set(manifest["armors"]) == set(ARMOR_IDS), "Unexpected armor catalogue")
    require([row["index"] for row in manifest["common_body"]] == list(range(6)), "Common frame indices changed")
    hashes, expected = {}, []
    verify_paired_references(manifest, hashes)
    def add(record, name, armor_id, layer, frame, pose):
        path = source_path(record["path"])
        pixels = inspect_rgba_png(checked_hash(path, record["sha256"]))
        for key in ("canvas_px", "mode", "alpha_extrema", "bbox_px"):
            require(pixels[key] == record[key], f"Pixel/manifest mismatch {key}: {path}")
        require(pixels["alpha_extrema"] == [0, 255] and pixels["corners_transparent"] and pixels["nonempty"], f"Invalid actual alpha: {path}")
        require(pose["root_px"] == [256,472] and pose["grip_px"] == [[183,189],[181,143],[253,398],[300,401],[164,316],[173,350]][frame] and pose["weapon_angle_image_clockwise_deg"] == [-70,-55,25,15,-20,35][frame] and pose["weapon_scale"] == .4, "Frozen P3 pose metadata changed")
        expected.append({"armor_id":armor_id,"layer":layer,"frame":frame,"source":str(path),"source_sha256":record["sha256"],"source_bytes":path.stat().st_size,"pixels":pixels,"package_path":PACKAGE+"/"+name,"object_path":PACKAGE+"/"+name+"."+name,"texture_name":name,"root_px":pose["root_px"],"grip_px":pose["grip_px"],"time_start_s":pose["time_start_s"],"time_end_s":pose["time_end_s"],"weapon_angle_image_clockwise_deg":pose["weapon_angle_image_clockwise_deg"],"weapon_scale":pose["weapon_scale"]})
    for pose in manifest["common_body"]:
        index=pose["index"]
        for layer in ("body_far","body_near"):
            add(pose[layer],f"T_ArmorP3_{layer}_{index:03d}_v001","",layer,index,pose)
    for armor_id in ARMOR_IDS:
        frames=manifest["armors"][armor_id]
        require([row["index"] for row in frames]==list(range(6)),"Armor indices changed")
        for row in frames:
            index=row["index"];pose=manifest["common_body"][index]
            require(row["root_px"]==pose["root_px"] and row["grip_px"]==pose["grip_px"],"Armor/body pose mismatch")
            require(row["armor_back"] is None and row.get("armor_back_visibility"),"Do not invent hidden back layer")
            add(row["armor_front"],f"T_ArmorP3_{armor_id.replace('-', '_')}_front_{index:03d}_v001",armor_id,"front",index,pose)
    require(len(expected)==EXPECTED_COUNT and len({r["package_path"] for r in expected})==EXPECTED_COUNT,"Unique destination count mismatch")
    require(len({r["source"] for r in expected})==EXPECTED_COUNT,"Duplicate import source")
    return manifest,expected,hashes


def import_in_unreal(manifest, expected, hashes):
    import unreal
    project_root = Path(unreal.Paths.project_dir()).resolve().parent
    require(project_root == ROOT, f"Wrong UE project: {project_root}")
    on_disk = ROOT / "UnrealGame/Content/Production/FirstBatch/v012/ArmorPrimary3"
    require(not on_disk.exists() or not any(p.is_file() for p in on_disk.rglob("*")),
            f"Destination has files; refusing to overwrite: {on_disk}")
    if unreal.EditorAssetLibrary.does_directory_exist(PACKAGE):
        require(not unreal.EditorAssetLibrary.list_assets(PACKAGE, recursive=True, include_folder=False),
                f"Destination has registered assets; refusing to overwrite: {PACKAGE}")
    receipt = {"schema": "armor-primary3-four-import-receipt-v2", "utc": datetime.now(timezone.utc).isoformat(),
               "manifest": str(MANIFEST), "manifest_sha256": MANIFEST_SHA256, "destination": PACKAGE,
               "expected_count": EXPECTED_COUNT, "actual_count": 0, "saved_count": 0, "assets": expected,
               "verified_reference_count": len(hashes), "success": False,
               "formal_content_accepted": False, "runtime_verified": False,
               "scope": "Native primary3 candidate import/pixels/Texture2D/settings only; no armor motion or gameplay acceptance",
               "draw_order": manifest["draw_order"], "mirror_policy": manifest["mirror_policy"],
               "empty_armor_variant": manifest["no_armor_variant"], "canvas_refit": False}
    destination = ROOT / "UnrealGame/Saved/Bootstrap"
    receipt_path = destination / ("armor-primary3-four-v001-import-" + datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S-%f") + ".json")
    try:
        tasks = []
        for row in expected:
            require(not unreal.EditorAssetLibrary.does_asset_exist(row["package_path"]), "Destination collision")
            task = unreal.AssetImportTask()
            for key, value in (("filename", row["source"]), ("destination_path", PACKAGE),
                               ("destination_name", row["texture_name"]), ("automated", True),
                               ("save", False), ("replace_existing", False)):
                task.set_editor_property(key, value)
            tasks.append(task)
        unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks(tasks)
        settings = {"compression_settings": unreal.TextureCompressionSettings.TC_EDITOR_ICON,
                    "mip_gen_settings": unreal.TextureMipGenSettings.TMGS_NO_MIPMAPS,
                    "lod_group": unreal.TextureGroup.TEXTUREGROUP_UI,
                    "never_stream": True, "srgb": True}
        for row, task in zip(expected, tasks):
            imported_paths = list(task.get_editor_property("imported_object_paths"))
            require(imported_paths == [row["object_path"]], f"Unexpected import output: {imported_paths}")
            texture = unreal.load_asset(row["package_path"])
            require(isinstance(texture, unreal.Texture2D), f"Not Texture2D: {row['package_path']}")
            for key, value in settings.items():
                texture.set_editor_property(key, value)
                require(texture.get_editor_property(key) == value, f"UE setting mismatch: {key}")
            size = [texture.blueprint_get_size_x(), texture.blueprint_get_size_y()]
            require(size == [512, 512], f"UE changed native canvas: {row['package_path']}")
            row["ue_config"] = {key: (value if isinstance(value, bool) else str(texture.get_editor_property(key)))
                                for key, value in settings.items()}
            row["ue_config"]["size_px"] = size
            row["imported_object_paths"] = imported_paths
            receipt["actual_count"] += 1
        checked_hash(MANIFEST, MANIFEST_SHA256)
        for path, digest in hashes.items():
            checked_hash(path, digest)
        for row in expected:
            require(unreal.EditorAssetLibrary.save_loaded_asset(unreal.load_asset(row["package_path"]), False),
                    f"Could not save new texture: {row['package_path']}")
            row["saved"] = True
            receipt["saved_count"] += 1
        actual_paths = set(unreal.EditorAssetLibrary.list_assets(PACKAGE, recursive=True, include_folder=False))
        require(actual_paths == {row["object_path"] for row in expected}, "UE package contains unexpected assets")
        receipt["success"] = receipt["actual_count"] == receipt["saved_count"] == EXPECTED_COUNT
    except Exception as error:
        receipt["error"] = str(error)
        raise
    finally:
        destination.mkdir(parents=True, exist_ok=True)
        with receipt_path.open("x", encoding="utf-8") as output:
            json.dump(receipt, output, ensure_ascii=False, indent=2)
        unreal.log("Armor primary3 import receipt: " + str(receipt_path))


if __name__ == "__main__":
    frozen, textures, reference_hashes = preflight()
    if "--validate-only" in sys.argv:
        print(json.dumps({"source_validation_success": True, "manifest_sha256": MANIFEST_SHA256,
                          "actual_native_rgba_textures": len(textures), "verified_reference_count": len(reference_hashes),
                          "destination": PACKAGE, "unreal_import_run": False}, ensure_ascii=False))
    else:
        import_in_unreal(frozen, textures, reference_hashes)
