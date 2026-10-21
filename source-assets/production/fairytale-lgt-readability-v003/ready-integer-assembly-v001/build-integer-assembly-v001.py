"""Register supplied visible A to artist B by integer RGBA translation only."""
from pathlib import Path
import datetime
import hashlib
import json
import platform
import shutil
import sys

import PIL
import numpy as np
from PIL import Image


OUT = Path(__file__).resolve().parent
FAMILY = Path("F:/Ourgame/source-assets/production/fairytale-lgt-readability-v003")
MOUNTS = FAMILY / "ready-visible-mounts-v001/mounts-v001.json"
PYTHON = Path("C:/Users/22499/.codex/skills/sprite-gen/.venv/Scripts/python.exe")
BODY_NAMES = ["BodyRest", "NearArmWithoutHand", "NearHand"]
ARMOR_NAMES = ["FarShoulder", "Chest", "NearShoulder"]
STATIC_ORDER = ["BodyRest", "FarShoulder", "Chest", "NearArmWithoutHand", "NearShoulder", "NearHand"]
WATCHED = {}


def pin(path, watch=True):
    data = path.read_bytes()
    result = {"path": path.as_posix(), "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}
    if watch and not path.is_relative_to(OUT):
        WATCHED[path] = result
    return result


def require_pin(expected):
    path = Path(expected["path"])
    actual = pin(path)
    if actual != expected:
        raise RuntimeError(f"Source pin changed: {path}")
    return path


def write(relative, data):
    path = OUT / relative
    if not path.is_relative_to(OUT):
        raise RuntimeError("Ownership boundary")
    path.parent.mkdir(parents=True, exist_ok=True)
    text = data if isinstance(data, str) else json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(text)
    return path


def copy_exact(source, relative):
    path = OUT / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise RuntimeError(f"Existing output: {path}")
    before = pin(source)
    shutil.copy2(source, path)
    if pin(path)["sha256"] != before["sha256"] or path.stat().st_size != before["bytes"]:
        raise RuntimeError("Byte copy changed")
    return path


def rgba(path):
    with Image.open(path) as image:
        if image.mode != "RGBA" or image.size != (512, 512):
            raise RuntimeError(f"Expected 512 RGBA: {path}")
        return np.asarray(image).copy()


def pixel_bbox(array, alpha_only=False):
    mask = array[:, :, 3] > 0 if alpha_only else np.any(array != 0, axis=2)
    ys, xs = np.where(mask)
    return [int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1] if len(xs) else None


def translate(array, dx, dy):
    height, width = array.shape[:2]
    if type(dx) is not int or type(dy) is not int or abs(dx) >= width or abs(dy) >= height:
        raise RuntimeError("Integer delta out of range")
    bbox = pixel_bbox(array)
    if bbox is None or bbox[0] + dx < 0 or bbox[1] + dy < 0 or bbox[2] + dx > width or bbox[3] + dy > height:
        raise RuntimeError("Translation would clip nonzero RGBA, including hidden RGB")
    sx0, sx1 = max(0, -dx), min(width, width - dx)
    sy0, sy1 = max(0, -dy), min(height, height - dy)
    result = np.zeros_like(array)
    result[sy0 + dy:sy1 + dy, sx0 + dx:sx1 + dx] = array[sy0:sy1, sx0:sx1]
    return result


def save_rgba(array, relative):
    path = OUT / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise RuntimeError("Existing diagnostic image")
    Image.fromarray(array).save(path)
    if not np.array_equal(rgba(path), array):
        raise RuntimeError("PNG round trip changed RGBA")
    return path


def compose(layers, omit=None):
    image = Image.new("RGBA", (512, 512), (0, 0, 0, 0))
    for name in STATIC_ORDER:
        if name != omit:
            image = Image.alpha_composite(image, Image.fromarray(layers[name]))
    return np.asarray(image).copy()


def main():
    if Path(sys.executable).resolve() != PYTHON.resolve():
        raise RuntimeError("Use sprite-gen venv")
    if OUT != FAMILY / "ready-integer-assembly-v001" or (OUT / "assembly-proof-v001.json").exists():
        raise RuntimeError("Unexpected or existing output")
    mounts_pin = pin(MOUNTS)
    mounts = json.loads(MOUNTS.read_text(encoding="utf-8"))
    if mounts["fit_accepted"] is not False or len(mounts["rows"]) != 12:
        raise RuntimeError("Expected 12 candidate mounts, no existing fit acceptance")
    index_path = require_pin(mounts["source_index"])
    inventory = json.loads(index_path.read_text(encoding="utf-8"))
    copy_exact(MOUNTS, "inputs/mounts-v001.json")
    copy_exact(index_path, "inputs/ready-three-component-source-list-v001.json")
    keyed = {(row["frame"], row["component"]): row for row in mounts["rows"]}
    if len(keyed) != 12 or set(keyed) != {(i, name) for i in range(4) for name in ARMOR_NAMES}:
        raise RuntimeError("Duplicate or missing mount")
    registrations = []
    frames = []
    for frame in range(4):
        source_frame = inventory["frames"][frame]
        if source_frame["frame"] != frame or source_frame["duration_ms"] != 167:
            raise RuntimeError("Unexpected frame contract")
        body_path = require_pin(source_frame["common_body158"])
        original_body = rgba(body_path)
        layers, masks, body_copies = {}, {}, []
        for entry in source_frame["existing_body_layers_to_keep_unchanged"]:
            owner = entry["owner"]
            if owner not in BODY_NAMES or owner in layers:
                raise RuntimeError("Unexpected body layer")
            source = require_pin(entry["current_texture"])
            partition = require_pin(entry["partition_layer"])
            mask_path = require_pin(entry["ownership_mask"])
            if source.read_bytes() != partition.read_bytes():
                raise RuntimeError("Current body layer is not original partition bytes")
            copy = copy_exact(source, f"body-layers/{owner}/frame-{frame}.png")
            layers[owner] = rgba(copy)
            with Image.open(mask_path) as image:
                values = np.asarray(image).copy()
                if image.mode != "L" or image.size != (512, 512) or not set(np.unique(values)).issubset({0, 255}):
                    raise RuntimeError("Unexpected binary ownership mask")
                masks[owner] = values > 0
            body_copies.append({"owner": owner, "source": pin(source), "copy": pin(copy),
                                "original_partition_layer": pin(partition), "source_ownership_mask": pin(mask_path),
                                "byte_identical_copy": True,
                                "mask_role": "Original source RGBA ownership, not semantic armor protection"})
        if set(layers) != set(BODY_NAMES):
            raise RuntimeError("Incomplete body partition")
        ownership_count = np.sum(np.stack([masks[name] for name in BODY_NAMES]), axis=0)
        if not np.all(ownership_count == 1):
            raise RuntimeError("Existing source ownership is not exclusive and exhaustive")
        recovered = np.sum(np.stack([layers[name] for name in BODY_NAMES]), axis=0, dtype=np.uint16)
        if not np.array_equal(recovered, original_body.astype(np.uint16)):
            raise RuntimeError("Unchanged body layers fail full RGBA reconstruction")

        frame_registrations = []
        for name in ARMOR_NAMES:
            row = keyed[(frame, name)]
            if row["body"] != source_frame["common_body158"] or row["duration_ms"] != 167:
                raise RuntimeError("Mount is not matched to this Body158 frame")
            source = require_pin(row["source"])
            array = rgba(source)
            a, b, delta = row["A_source_px"], row["B_body_design_source_px"], row["integer_delta_xy"]
            if not all(type(value) is int for value in a + b + delta):
                raise RuntimeError("Mount coordinates must be explicit integers")
            if delta != [b[0] - a[0], b[1] - a[1]]:
                raise RuntimeError("Supplied delta does not map A to B")
            source_pixel = array[a[1], a[0]].tolist()
            if source_pixel != row["A_observed_rgba"] or source_pixel[3] < 128:
                raise RuntimeError("Observed actual source A pixel changed")
            placed = translate(array, *delta)
            inverse = translate(placed, -delta[0], -delta[1])
            if not np.array_equal(inverse, array):
                raise RuntimeError("RGBA translation inverse is not exact")
            if placed[b[1], b[0]].tolist() != source_pixel:
                raise RuntimeError("A did not map exactly to B")
            translated = save_rgba(placed, f"armor-layers/{name}/frame-{frame}.png")
            layers[name] = placed
            intersections = []
            for owner in BODY_NAMES:
                source_visible = layers[owner][:, :, 3] > 0
                intersections.append({"source_owner": owner,
                                      "intersection_ownership_coordinates_any_alpha": int(np.count_nonzero((placed[:, :, 3] > 0) & masks[owner])),
                                      "intersection_visible_source_pixels_any_alpha": int(np.count_nonzero((placed[:, :, 3] > 0) & source_visible)),
                                      "intersection_both_alpha_ge128": int(np.count_nonzero((placed[:, :, 3] >= 128) & (layers[owner][:, :, 3] >= 128))),
                                      "semantic_protection_inference": False})
            record = {"frame": frame, "component": name, "source": pin(source), "translated": pin(translated),
                      "A_source_px": a, "A_observed_rgba": source_pixel, "A_feature": row["A_feature"],
                      "A_visual_uncertainty_source_px": row["A_manual_visual_uncertainty_px"],
                      "B_body_design_source_px": b, "B_role": row["B_role"],
                      "B_design_uncertainty_source_px": row["B_design_uncertainty_px"],
                      "B_actual_original_body_rgba_diagnostic_only": original_body[b[1], b[0]].tolist(),
                      "integer_delta_xy": delta, "A_maps_exactly_to_B": True,
                      "source_nonzero_RGBA_bbox": pixel_bbox(array), "translated_nonzero_RGBA_bbox": pixel_bbox(placed),
                      "source_alpha_bbox": pixel_bbox(array, True), "translated_alpha_bbox": pixel_bbox(placed, True),
                      "nonzero_RGBA_clipped_pixels": 0, "inverse_RGBA_all_bytes_equal": True,
                      "source_RGBA_pixels_sha256": hashlib.sha256(array.tobytes()).hexdigest(),
                      "inverse_RGBA_pixels_sha256": hashlib.sha256(inverse.tobytes()).hexdigest(),
                      "rescaled_rotated_recolored_or_redrawn": False, "intersections": intersections,
                      "fit_accepted": False}
            registrations.append(record)
            frame_registrations.append(record)

        composite = compose(layers)
        output = save_rgba(composite, f"diagnostics/static-no-sword/right/frame-{frame}.png")
        mirrored = np.asarray(Image.fromarray(composite).transpose(Image.Transpose.FLIP_LEFT_RIGHT)).copy()
        mirror_path = save_rgba(mirrored, f"diagnostics/static-no-sword/left-whole-image-mirror/frame-{frame}.png")
        inverse_mirror = np.asarray(Image.fromarray(mirrored).transpose(Image.Transpose.FLIP_LEFT_RIGHT))
        if not np.array_equal(inverse_mirror, composite):
            raise RuntimeError("Whole-image mirror inverse changed pixels")
        pair_intersections = []
        for i, first in enumerate(ARMOR_NAMES):
            for second in ARMOR_NAMES[i + 1:]:
                pair_intersections.append({"first": first, "second": second,
                                           "both_any_alpha": int(np.count_nonzero((layers[first][:, :, 3] > 0) & (layers[second][:, :, 3] > 0))),
                                           "both_alpha_ge128": int(np.count_nonzero((layers[first][:, :, 3] >= 128) & (layers[second][:, :, 3] >= 128)))})
        contributions = []
        for component in ARMOR_NAMES:
            omitted = compose(layers, omit=component)
            contributions.append({"component": component,
                                  "final_RGBA_difference_pixels_when_omitted": int(np.count_nonzero(np.any(omitted != composite, axis=2))),
                                  "meaning": "Numeric visible contribution only; does not certify fit or semantic protection"})
        frames.append({"frame": frame, "duration_ms": 167, "common_body158": pin(body_path),
                       "body_layers": body_copies, "body_partition_full_RGBA_reconstruction_equal": True,
                       "ownership_exclusive_and_exhaustive": True, "armor_components": [r["translated"] for r in frame_registrations],
                       "static_no_sword_right": pin(output), "static_whole_image_mirror_left": pin(mirror_path),
                       "whole_image_mirror_inverse_RGBA_equal": True, "individual_components_mirrored": False,
                       "pairwise_armor_alpha_intersections": pair_intersections,
                       "omit_one_numeric_contributions": contributions,
                       "semantic_regions_pending_actual_Root_review": {name: None for name in ["helmet", "eyes", "neck", "near_hand", "far_hand", "belt_and_waist"]},
                       "fit_accepted": False, "new_outputs_viewed": False})

    mismatches = [path.as_posix() for path, before in WATCHED.items() if pin(path, False) != before]
    if mismatches:
        raise RuntimeError(f"Read-only source changed: {mismatches}")
    report = write("assembly-proof-v001.json", {
        "schema": "ready-soft-leather-integer-source-RGBA-assembly-candidate-v001",
        "created_local": datetime.datetime.now().astimezone().isoformat(), "mounts": mounts_pin,
        "source_index": pin(index_path), "script": pin(Path(__file__).resolve()),
        "toolchain": {"python_executable": sys.executable, "python_version": platform.python_version(),
                      "pillow_version": PIL.__version__, "numpy_version": np.__version__},
        "frames": frames, "registrations": registrations,
        "armor_layer_count": 12, "body_layer_byte_copies": 12, "right_static_count": 4,
        "left_whole_image_mirror_diagnostic_count": 4, "durations_ms": [167] * 4,
        "static_layer_order_no_sword": STATIC_ORDER,
        "future_independent_Sword_slot": {"after": "NearShoulder", "before": "NearHand", "included_now": False},
        "native_facing": 1, "maximum_body_height_screen_px": 72,
        "all_translations_integer_RGBA_reversible": True, "all_nonzero_RGBA_clipped_pixels": 0,
        "all_existing_body_layer_bytes_unchanged": True,
        "read_only_sources_rechecked": len(WATCHED), "source_mismatches": mismatches,
        "new_outputs_viewed": False, "Root_retention_required_before_visual_review": True,
        "fit_accepted": False, "semantic_protection_mask_accepted": False,
        "runtime_imported": False, "ready_all_states_or_complete_equipment_accepted": False,
        "formal_complete_units": 0,
        "limitations": [
            "Actual A was visually selected by Root and verified against this pinned source pixel. B is an artist placement proposal with uncertainty, not skeleton/bone truth or accepted fit.",
            "Integer translation/inverse equality proves RGBA fidelity and absence of clipping, not anatomical alignment or attractive overlap.",
            "Old binary masks are exclusive source ownership, not semantically accepted armor protection. No helmet/eyes/neck/far-hand/belt semantic mask was invented.",
            "Raw alpha intersection and omit-one difference counts are numeric diagnostics, not semantic cover approval. Helmet, eyes, neck, near hand, far hand and belt/waist remain pending Root actual visual review.",
            "No independent Sword is included. Static right/mirrored pictures do not prove motion continuity, actual runtime facings, all action states or four-armor compatibility.",
            "Far187 retains the prior standard-inspect low-motion warning; this rigid attachment diagnostic does not certify a full animation.",
        ],
    })
    write("HANDOFF.md", """# Ready 软皮轻甲整数贴合候选 v001

按 Root 的12个 actual visible A 与 artist B，只作原512 RGBA整数平移。输出12个甲层、12个旧body层逐字节副本、4个无剑静态组合与4个整张组合水平镜像诊断。没有二次缩放、旋转、重绘、填补或改色，没有接剑/导入。

`assembly-proof-v001.json` 逐项记录原件SHA、A像素、B设计角色、delta、无非零RGBA裁切、逆平移全RGBA相等及旧body层byte exact。原Body158通过旧三层全RGBA复原。数值覆盖表仅为旧ownership坐标/可见像素交集；不是语义protected mask。头盔/眼/颈/近手/远手/腰带覆盖均待Root实际审图，fit仍未验收。

层序 BodyRest → FarShoulder → Chest → NearArmWithoutHand → NearShoulder →（未来独立Sword）→ NearHand。左向只对同一最终静态图整体翻转一次，未单独镜像部件。

执行者未查看新图。Root必须先E归档，再查看 `diagnostics/static-no-sword/right/` 与左镜像组。Ready其它动作、适配、整套装备及运行结果均未声明完成。旧文件、ActualSource/UE/README/ledger/媒体目录没有改动。
""")
    files = [pin(path, False) for path in sorted(OUT.rglob("*")) if path.is_file()]
    for entry in files:
        entry["path"] = Path(entry["path"]).relative_to(OUT).as_posix()
    freeze = write("assembly-freeze-v001.json", {"schema": "ready-integer-assembly-freeze-v001", "files": files,
                   "file_count_excluding_manifest": len(files), "total_bytes_excluding_manifest": sum(entry["bytes"] for entry in files),
                   "fit_accepted": False, "viewed": False})
    print(json.dumps({"report": pin(report), "freeze": pin(freeze), "armor_layers": len(registrations),
                      "body_layer_byte_copies": 12, "static_right": 4, "static_mirror_left": 4,
                      "frozen_files": len(files), "frozen_bytes": sum(entry["bytes"] for entry in files),
                      "source_rechecks": len(WATCHED), "source_mismatches": [], "viewed": False}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
