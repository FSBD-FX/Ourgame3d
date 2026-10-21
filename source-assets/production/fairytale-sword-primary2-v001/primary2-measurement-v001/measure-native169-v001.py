"""Native169 readonly measurements; writes only this fresh measurement directory.

All manual coordinates are visible-feature candidates, never recovered anatomy.
No segmentation/repainting/resizing/retiming or modification of source art occurs.
New exact crops are not opened by this script and need Root E retention first.
"""
from pathlib import Path
from datetime import datetime
import hashlib
import json
import math
import sys

import numpy as np
from PIL import Image

sys.stdout.reconfigure(encoding="utf-8")
HERE = Path(__file__).resolve().parent
FAMILY = HERE.parent
PROJECT = Path("F:/Ourgame")
E_ROOT = Path("E:/OurGame/Knight/过程图稿与视频/2026-10-16-OurgameUE-primary2-native169-standard-derived-v194")
E_INDEX = E_ROOT / "source-size-SHA256.json"
PIXEL_SCALE = 72 / 416  # Existing fixed display convention, not per-pose fitting.


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fact(path):
    return {"path": path.as_posix(), "bytes": path.stat().st_size, "sha256": digest(path)}


def write_json(path, obj):
    if path.exists():
        raise RuntimeError(f"Refuse to overwrite measurement artifact: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def rgba_at(a, p):
    return {"xy": list(p), "rgba": a[p[1], p[0]].astype(int).tolist()}


def check_old_freezes():
    records = []
    for relative in ("preparation-freeze-v001.json", "preparation-freeze-v002.json",
                     "primary2-extraction-v001/extracted-freeze-v001.json",
                     "primary2-extraction-v002/extracted-freeze-v002.json"):
        path = FAMILY / relative
        document = json.loads(path.read_text(encoding="utf-8-sig"))
        mismatches = []
        for row in document["files"]:
            src = Path(row["path"])
            if not src.is_file() or src.stat().st_size != row["bytes"] or digest(src) != row["sha256"]:
                mismatches.append(row["path"])
        if mismatches:
            raise RuntimeError(f"Existing frozen sources changed: {mismatches}")
        records.append({"manifest": fact(path), "checked_files": len(document["files"]),
                        "mismatches": mismatches, "modified_by_measurement": False})
    return records


def retained_source(path, e_index):
    source = fact(path)
    rows = [r for r in e_index["files"] if r["sha256"] == source["sha256"] and r["bytes"] == source["bytes"]]
    if not rows:
        raise RuntimeError(f"Expected at least one exact E194 source copy: {path}")
    retained_copies = []
    for row in rows:
        retained = E_ROOT / row["retained_relative"]
        if not retained.is_file() or fact(retained)["sha256"] != source["sha256"] or retained.stat().st_size != source["bytes"]:
            raise RuntimeError(f"E194 copy mismatch: {retained}")
        retained_copies.append(fact(retained))
    return {"source": source, "e194_copies": retained_copies, "bytes_and_sha_equal": True}


# Manual observations of the actual E194-retained original PNGs; not old guide points.
# Polygons follow the fist/glove, excluding the brown cuff where its visible seam permits.
# They are uncertain silhouette proposals, NOT complete binary ownership or thumb masks.
MANUAL = [
    {"grip": [224, 318], "uncertainty": 3,
     "polygon": [[205,300],[222,297],[238,301],[249,310],[252,322],[247,334],[240,337],[229,341],[218,341],[207,337],[200,329],[197,319],[198,309]],
     "crop": [188,287,261,350],
     "observation": "Low image-left fist; palm center brown patch; dark lower finger folds. Wrist/cuff seam is oblique and partly merged with outline.",
     "axis_design": [0.94,-0.341]},
    {"grip": [252, 274], "uncertainty": 3,
     "polygon": [[239,255],[249,250],[263,252],[273,259],[275,273],[272,287],[265,294],[249,298],[237,296],[229,288],[230,269]],
     "crop": [218,240,285,307],
     "observation": "Fist folded in front of chest; broad opaque brown palm with right-side finger curves; cuff boundary partly obscured at image-left.",
     "axis_design": [0.98,0.15]},
    {"grip": [358, 277], "uncertainty": 4,
     "polygon": [[341,260],[349,256],[360,258],[371,263],[379,271],[380,283],[375,294],[366,299],[354,298],[345,293],[338,282],[338,268]],
     "crop": [325,245,389,307],
     "observation": "Forward fist extends to near the visible helmet front; forearm silhouette remains nearly horizontal. Palm folds do not prove a vertical handle grip or bent elbow.",
     "axis_design": [1.0,0.0]},
    {"grip": [345, 277], "uncertainty": 4,
     "polygon": [[329,255],[347,255],[361,259],[370,267],[374,278],[370,290],[360,297],[346,298],[332,294],[322,287],[318,275],[319,264]],
     "crop": [309,244,385,307],
     "observation": "Forward fist with visible finger/knuckle curves along lower edge; cloth hides the elbow. Brown palm feature is observable but grasp cylinder is absent.",
     "axis_design": [0.995,-0.10]},
    {"grip": [250, 301], "uncertainty": 3,
     "polygon": [[235,280],[247,280],[260,285],[271,293],[279,303],[277,314],[270,322],[259,327],[249,325],[241,320],[232,312],[225,300],[226,289]],
     "crop": [215,270,287,336],
     "observation": "Hand returns toward waist in front of belt; finger curves and cuff form a diagonal wrist boundary. Belt pixels are not included intentionally, but boundary remains uncertain.",
     "axis_design": [0.99,0.10]},
    {"grip": [224, 318], "uncertainty": 3,
     "polygon": [[205,300],[223,297],[239,301],[250,310],[253,322],[248,334],[241,338],[230,342],[218,342],[207,337],[200,329],[197,319],[198,309]],
     "crop": [188,287,262,351],
     "observation": "Low image-left fist returns close to phase0; pixel values and contour are independently sampled, not copied as an identity or loop-lock proof.",
     "axis_design": [0.94,-0.341]},
]


def sole_band(a, label, x0, x1):
    # Half-open x ROI; manually chosen visible boot regions. No anatomy inferred.
    region = a[400:465, x0:x1, 3] >= 128
    yy, xx = np.nonzero(region)
    if not len(yy):
        raise RuntimeError("No actual boot alpha in chosen ROI")
    max_y = int(yy.max()) + 400
    ys, xs = np.nonzero(a[max_y-3:max_y+1, x0:x1, 3] >= 128)
    px, py = xs + x0, ys + max_y - 3
    middle = (int(px.min()) + int(px.max())) // 2
    bottom_xs = np.flatnonzero(a[max_y, x0:x1, 3] >= 128) + x0
    sample_x = int(bottom_xs[len(bottom_xs)//2])
    return {"label": label, "semantic_roi_xyxy_half_open": [x0,400,x1,465],
            "alpha_threshold": 128, "lowest_solid_y": max_y,
            "lowest_pixel_sample": rgba_at(a, [sample_x,max_y]),
            "band_rows_inclusive": [max_y-3,max_y], "band_solid_pixel_count": int(len(px)),
            "band_x_interval_inclusive": [int(px.min()),int(px.max())],
            "band_unweighted_x_centroid": float(px.mean()),
            "band_alpha_weighted_x_centroid": float(np.average(px, weights=a[py,px,3])),
            "display_root_y_minus_lowest_pixel_index": 464-max_y,
            "not": "Not a foot bone, contact solver, ground truth ground contact, or replacement display pivot."}


def helmet_front(a, label, y0, y1):
    # Manually selected already-viewed helmet contour band; not a silhouette classifier.
    ys, xs = np.nonzero(a[y0:y1,150:386,3] >= 128)
    front_x = int(xs.max()) + 150
    at_front = ys[xs == xs.max()] + y0
    sample_y = int(at_front[len(at_front)//2])
    return {"label": label, "manual_helmet_roi_xyxy_half_open": [150,y0,386,y1],
            "alpha_threshold": 128, "frontmost_solid_x": front_x,
            "frontmost_y_values": at_front.astype(int).tolist(),
            "sample": rgba_at(a,[front_x,sample_y]),
            "aa_threshold_uncertainty_px": 1, "semantic_band_selection_uncertainty_px": 2,
            "not": "No whole-body bbox anchor; contour-band fact only, not skull position or bone."}


def exact_crop(im, crop, path):
    out = im.crop(crop)
    out.save(path)
    with Image.open(path) as saved:
        eq = np.array_equal(np.asarray(saved), np.asarray(im)[crop[1]:crop[3],crop[0]:crop[2]])
        if not eq or saved.mode != "RGBA":
            raise RuntimeError("Exact crop byte-pixel readback mismatch")
    return {**fact(path), "source_roi_xyxy_half_open": crop,
            "native_pixels": True, "resized": False, "annotated": False,
            "all_rgba_channels_exact": True, "viewed_before_E_retention": False}


def main():
    # Prevent script accidentally overwriting previously frozen results on rerun.
    if (HERE / "measurement-v001.json").exists() or (HERE / "measurement-freeze-v001.json").exists():
        raise RuntimeError("Measurement already frozen; use a separately authorized new version")
    e_index = json.loads(E_INDEX.read_text(encoding="utf-8-sig"))
    old_before = check_old_freezes()
    crop_dir = HERE / "unscaled-crops"
    crop_dir.mkdir(exist_ok=True)
    if any(crop_dir.iterdir()):
        raise RuntimeError("Refuse to overwrite existing measurement crops")
    frames = []
    for index, manual in enumerate(MANUAL):
        path = FAMILY / "run-primary2-v002/curated" / f"frame-{index}.png"
        source = retained_source(path,e_index)
        with Image.open(path) as im:
            if im.size != (512,512) or im.mode != "RGBA":
                raise RuntimeError("Unexpected actual source dimensions/mode")
            a = np.asarray(im).copy()
            center = manual["grip"]
            if a[center[1],center[0],3] != 255:
                raise RuntimeError("Manual palm sample must be in observed opaque surface")
            samples = [rgba_at(a,[center[0]+dx,center[1]+dy]) for dx,dy in [(0,0),(-6,0),(6,0),(0,-6),(0,6)]]
            crops = [exact_crop(im,manual["crop"],crop_dir/f"frame-{index}-near-glove-unscaled.png"),
                     exact_crop(im,[128,398,385,465],crop_dir/f"frame-{index}-boots-unscaled.png"),
                     exact_crop(im,[150,140,386,240],crop_dir/f"frame-{index}-helmet-front-unscaled.png")]
            near = sole_band(a,"near/image-left boot",128,240)
            far = sole_band(a,"far/image-right boot",260,385)
            front = [helmet_front(a,"upper brim",145,180),helmet_front(a,"lower front lip",214,239)]
            vertices = [rgba_at(a,p) for p in manual["polygon"]]
            frames.append({"frame": index, **source,
                "observed_by_reviewer": "Actual original512 and E194 native-size body/hand ROI; no new crop viewed.",
                "grip_candidate": {"xy": center, "uncertainty_plus_minus_px": manual["uncertainty"],
                    "type": "MANUAL visible glove palm feature candidate; not actual handle center",
                    "selection_basis": manual["observation"], "source_rgba_samples": samples,
                    "bone": None, "hidden_handle_contact": None, "accepted": False},
                "near_hand_polygon_candidate": {"vertices_xy": manual["polygon"],
                    "vertex_source_rgba": vertices, "uncertainty_plus_minus_px": 4,
                    "role": "Visible fist/glove contour proposal excluding cuff; future overdraw fitting input only",
                    "complete_pixel_ownership_mask": False, "thumb_separation_proven": False,
                    "semantic_boundary_accepted": False,
                    "uncertainties": ["Wrist/cuff shared ink boundary", "Finger folds versus exterior ink", "Antialias samples around contour", "Some vertices may intentionally be outside opaque silhouette"]},
                "actual_blade_axis": None, "actual_elbow_angle_degrees": None,
                "actual_hidden_shoulder_elbow_wrist_bones": None,
                "future_independent_sword_fit_design": {"grip_design_input": "Measured visible palm candidate above, uncertainty retained",
                    "axis_xy_design_only": manual["axis_design"],
                    "axis_normalized_xy_design_only": [v/math.hypot(*manual["axis_design"]) for v in manual["axis_design"]],
                    "native_facing": 1,
                    "not_measured_from_source": True, "not_approved_or_fitted": True,
                    "rule": "Active2/3 point toward native+X; test blade against helmet/eyes/hand at native72px; do not treat this direction as accepted transverse motion."},
                "boot_contact_band_observations": {"near": near, "far": far},
                "helmet_front_observations": front,
                "display_root_convention": {"xy": [256,464], "type": "Existing fixed rendering pivot; not a measured foot root", "mutated": False},
                "crops": crops})
    near_x = [f["boot_contact_band_observations"]["near"]["band_unweighted_x_centroid"] for f in frames]
    far_x = [f["boot_contact_band_observations"]["far"]["band_unweighted_x_centroid"] for f in frames]
    front_x = [f["helmet_front_observations"][0]["frontmost_solid_x"] for f in frames]
    mid = [(n+f)/2 for n,f in zip(near_x,far_x)]
    old_after = check_old_freezes()
    if old_before != old_after:
        raise RuntimeError("Old freeze inputs changed during this readonly measurement")
    doc = {"schema": "fairytale-native169-primary2-visible-feature-candidates-v1",
        "created_local": datetime.now().astimezone().isoformat(),
        "status": "Measurement/candidate only; no pose, grip, transverse sweep, foot-lock or motion acceptance",
        "source_native": 169, "frame_count": 6, "source_mode": "RGBA", "source_canvas": [512,512],
        "e194_retention_index": fact(E_INDEX), "new_crops_need_root_retention_before_view": True,
        "coordinate_convention": "Original512 image x right/y down; integer coordinates identify pixel indices. ROIs are half-open, listed contour intervals inclusive.",
        "source_ratio": 0.9004329004329005, "fixed_display_body_height": 72,
        "fixed_canvas_scale": {"body_reference_height": 416, "source_to_screen": PIXEL_SCALE,
            "not": "A fixed existing display estimate, not a per-frame scale adjustment or a new UE observation."},
        "frames": frames,
        "cross_frame_visible_statistics": {
            "near_contact_band_x_centroids": near_x, "near_contact_x_span_source_px": max(near_x)-min(near_x),
            "near_contact_x_span_screen_px_at_fixed_scale": (max(near_x)-min(near_x))*PIXEL_SCALE,
            "far_contact_band_x_centroids": far_x, "far_contact_x_span_source_px": max(far_x)-min(far_x),
            "far_contact_x_span_screen_px_at_fixed_scale": (max(far_x)-min(far_x))*PIXEL_SCALE,
            "two_band_midpoint_diagnostic_x": mid, "midpoint_span_source_px": max(mid)-min(mid),
            "midpoint_is_not_pivot_or_bone": True,
            "near_lowest_solid_y": [f["boot_contact_band_observations"]["near"]["lowest_solid_y"] for f in frames],
            "far_lowest_solid_y": [f["boot_contact_band_observations"]["far"]["lowest_solid_y"] for f in frames],
            "upper_helmet_front_x": front_x,
            "upper_front_x_span_source_px": max(front_x)-min(front_x),
            "upper_front_x_span_screen_px_at_fixed_scale": (max(front_x)-min(front_x))*PIXEL_SCALE,
            "limits": "Generated pose change and shared-row placement are mixed; no continuous root-motion or foot-lock decomposition is possible from six static PNGs."},
        "old_freeze_checks_before_and_after": old_after,
        "known_standard_preview_timing": {"requested_ms": [75,75,60,60,135,135], "actual_standard_atlas_gif_ms": [100,100,100,100,100,100], "contract_passed": False, "retimed": False},
        "writes": "Only fresh primary2-measurement-v001: this script, candidate JSON/report, lossless exact ROI PNGs and freeze. No original source writes.",
        "source_art_mutated": False, "native_called": False, "ue_called": False, "import_called": False,
        "new_crops_viewed": False, "runtime_grip_validated": False, "motion_accepted": False, "foot_lock_accepted": False,
        "formal_complete_units": 0}
    write_json(HERE/"measurement-v001.json",doc)
    table = "\n".join(f"|{f['frame']}|{tuple(f['grip_candidate']['xy'])} ±{f['grip_candidate']['uncertainty_plus_minus_px']}|{f['helmet_front_observations'][0]['frontmost_solid_x']}|{f['boot_contact_band_observations']['near']['lowest_solid_y']} / {f['boot_contact_band_observations']['far']['lowest_solid_y']}|" for f in frames)
    report = f"""# Native169：第二段近手与足部像素测量候选 v001

事实：六张原512 RGBA与E194留档逐bytes/SHA相同；实际看过六原帧和已留档原尺寸手臂ROI。本包只新增数值、18张无缩放RGBA小裁图与此报告，新裁图未查看，等待Root E留档。坐标均为原图像素索引，x右/y下。

|相位|可见掌面Grip候选|盔上檐最前solid x|近/远鞋最低solid y|
|---|---|---|---|
{table}

Grip来自可见棕手套掌面与指缝位置判断，JSON列中心及邻近实际RGBA；它不是bbox中心、输入guide点或真实握柄中心。逐帧近手多边形是可见拳/手套轮廓候选，袖口共享墨边及AA约±4px，**不是完整独占像素mask**，不能直接宣称拇指分层或握柄通过。隐藏骨位/实际肘角/真实刃轴一律null；未来刀刃方向另列design-only，仍需独立剑拟合。

推理：2/3掌候选已移到(358,277)/(345,277)，不能继承guide的(259,292)/(266,296)。原帧中前臂仍向前，尤其2相拳已超过该相盔前沿；紧凑折肘、竖向侧握和横切感尚未接受，静态像素不证明90–110度实际关节角。

足部统计采用手动选定左右鞋ROI、alpha≥128最底四行：近鞋接触带横向质心跨度{max(near_x)-min(near_x):.8f} sourcepx，按固定72/416约{(max(near_x)-min(near_x))*PIXEL_SCALE:.5f}屏幕px；远鞋约{(max(far_x)-min(far_x))*PIXEL_SCALE:.5f}屏幕px。近鞋最底y463，显示pivot y464在其下一像素索引；远鞋y460（3相459）。固定(256,464)仍只是显示约定，没有改源、移动脚或重算pivot。质心/两鞋中点不是骨点或地面解算；生成姿势与shared-row放置混在一起，不能从这六张图分离根位移，更不能宣称足锁。

盔前缘在两个实际可见帽檐带采样；上檐x355/358/367/377/357/357，跨度22 sourcepx≈{(max(front_x)-min(front_x))*PIXEL_SCALE:.5f}屏幕px，只证明选定轮廓带变化，不证明头骨或身份固定。未用整个人物bbox作为握点/骨位。

风险与下一步：先E保全18裁图，再看候选多边形和袖口界线；Root选独立Sword设计轴后做实际掌心/剑柄/眼窗/刃正向拟合，保持72px和原像素，不能把guide坐标强套回源。需真正运行第二段并按内核75/75/60/60/135/135ms观察；既有标准atlas/GIF仍100×6ms，未修时序、未运行UE、未导入、未接受动作或装备。旧两代18+50+18+50清单共136项前后逐SHA/size零差。
"""
    (HERE/"measurement-review-v001.md").write_text(report,encoding="utf-8")
    files = [fact(p) for p in sorted(HERE.rglob("*")) if p.is_file()]
    freeze = {"schema": "fairytale-primary2-native169-measurement-freeze-v1",
              "created_local": datetime.now().astimezone().isoformat(),
              "file_count": len(files), "total_bytes": sum(r["bytes"] for r in files),
              "files": files, "new_crops_viewed": False,
              "retention_before_new_crop_view_required": True,
              "motion_or_equipment_acceptance": False, "source_art_unchanged": True}
    write_json(HERE/"measurement-freeze-v001.json",freeze)
    print(json.dumps({"freeze": fact(HERE/"measurement-freeze-v001.json"),
                      "files_excluding_freeze": len(files), "bytes_excluding_freeze": freeze["total_bytes"],
                      "new_crops": 18, "old_freeze_checked_files_each_pass": sum(r["checked_files"] for r in old_after),
                      "old_freeze_mismatches": 0, "near_contact_screen_span": doc["cross_frame_visible_statistics"]["near_contact_x_span_screen_px_at_fixed_scale"],
                      "report": fact(HERE/"measurement-review-v001.md"), "data": fact(HERE/"measurement-v001.json")}, ensure_ascii=False,indent=2))


if __name__ == "__main__":
    main()
