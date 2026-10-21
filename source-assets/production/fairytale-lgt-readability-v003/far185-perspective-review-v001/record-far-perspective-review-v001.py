"""Numeric source support for an actual view_image review; writes no images."""
from pathlib import Path
import datetime
import hashlib
import json

import numpy as np
from PIL import Image


OUT = Path(__file__).resolve().parent
FAMILY = OUT.parent
SOURCES = [
    (182, FAMILY / "row-preparation-v001/run-farshoulder-ready-v001/raw/leather_farshoulder_sword_ready.png",
     "eaa352de4a9eba6386985d48c5c7a07e59a70f1bc969f63ca2b1667ac5e9e4d1", "E257"),
    (185, FAMILY / "row-correction-v002/run-farshoulder-ready-v002/raw/leather_farshoulder_sword_ready.png",
     "3d682d944ee70da2ccb27a090ea1aa5c4586c75cdae9347fbd4efdf7755a5edf", "E269"),
]
# Conservative locator rectangles from the actual full-resolution visual review.
# They include safety space and may include adjoining chest pixels. Never use as
# a semantic crop/mask or derive an attachment A from a rectangle center.
ROIS = [[419, 219, 480, 310], [918, 211, 979, 303],
        [1438, 220, 1499, 311], [1946, 215, 2007, 311]]


def pin(path):
    data = path.read_bytes()
    return {"path": path.as_posix(), "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}


def write(name, value):
    path = OUT / name
    text = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False, indent=2) + "\n"
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(text)
    return path


def main():
    if OUT != FAMILY / "far185-perspective-review-v001" or (OUT / "perspective-review-v001.json").exists():
        raise RuntimeError("Unexpected or existing output")
    rows = []
    for number, path, expected, retention in SOURCES:
        before = pin(path)
        if before["sha256"] != expected:
            raise RuntimeError("Source pin mismatch")
        with Image.open(path) as image:
            if image.size != (2172, 724):
                raise RuntimeError("Expected exact source canvas")
            array = np.asarray(image.convert("RGB")).astype(np.int32)
            foreground = np.sum((array - np.array([0, 255, 0])) ** 2, axis=2) > 96 ** 2
            boxes = []
            for index in range(4):
                left, right = round(index * image.width / 4), round((index + 1) * image.width / 4)
                ys, xs = np.where(foreground[:, left:right])
                boxes.append([int(xs.min()) + left, int(ys.min()), int(xs.max()) + left + 1, int(ys.max()) + 1])
            rows.append({"native_request": number, "file": before, "canvas_px": list(image.size),
                         "root_reported_retention": retention,
                         "actual_view_image_called": True, "view_detail": "original",
                         "coarse_foreground_bbox_by_four_x_regions": boxes,
                         "bbox_method": "Read-only NumPy RGB distance from #00FF00 >96; canvas split into four x regions only for numeric grouping. No crop/image output. Bboxes are whole-source contents, not semantic far-cap masks."})
        if pin(path) != before:
            raise RuntimeError("Read-only image changed")
    prompt = """EDIT ONLY this exact native182 source image, canvas 2172 x 724. Keep ONLY the tiny, narrow leather FAR tabs at the IMAGE-RIGHT edge of each existing vest. Locator ROIs in zero-based [left,top,right,bottom) source pixels: first [419,219,480,310], second [918,211,979,303], third [1438,220,1499,311], fourth [1946,215,2007,311]. These rectangles locate the target; they are NOT rectangular crop masks. Within each, preserve only the slim curved leather tab outside the chest-side ink seam, including its own edge ink. Remove adjoining chest/collar pixels too. Preserve those four existing tabs' exact compressed perspectives, original image-space size, position and order. Do not retain the broad cap on the LEFT of any vest, mirror a near cap, move a cap into its place, invent a broad front cover or add a long hanging oval ring. Replace all other vest, pouch, body and grey undercloth pixels with opaque flat #00FF00. Keep four tiny original RIGHT tabs only; no text or guide boxes."""
    prompt_path = write("next-far-edit-visual-instruction-candidate-v001.txt", prompt + "\n")
    report = write("perspective-review-v001.json", {
        "schema": "far185-source-perspective-review-v001",
        "recorded_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "actual_review": {"tool": "view_image", "detail": "original", "source_images_viewed": [182, 185],
                          "retention_authority": "Root reported E257 and E269 retained and explicitly allowed viewing these two originals.",
                          "new_chest_frames_near_frames_or_guides_viewed": False},
        "sources": rows, "verdict185": "FAIL_SOURCE_FAR_PERSPECTIVE",
        "observations": [
            "Native182 has a broad image-LEFT foreground shoulder cap and a separate very narrow, compressed curved tab at the extreme image-RIGHT vest edge.",
            "Native185 instead shows broad frontal/near-style caps with long downward curved oval/ring forms. Their positions remain near each original vest's image-LEFT cap area, not the original tiny image-RIGHT tabs.",
            "Four isolated components do not establish the requested far view. Source geometry and perspective were not preserved.",
        ],
        "inference_boundary": "Visual near-style substitution is clear; exact pixel copying, model internal decisions and whether each low ring was newly generated versus altered source geometry are not provable from two images alone.",
        "next_edit_target_native": 182, "next_edit_target_sha256": SOURCES[0][2],
        "locator_roi_candidates": [{"frame": i, "source_canvas_px": [2172, 724],
                                   "roi_ltrb_exclusive": roi, "boundary_uncertainty_source_px": 8,
                                   "basis": "Actual full-resolution view of the narrow image-RIGHT tab, cross-checked with the whole vest's exact rightmost foreground bound.",
                                   "confidence": "medium locator; adjoining chest/black seam remains ambiguous",
                                   "semantic_mask": False, "actual_attachment_A": None} for i, roi in enumerate(ROIS)],
        "roi_limits": "Conservative locator rectangles intentionally include margin and may include adjoining chest pixels. They are not pixel-perfect part boundaries and must not be locally cropped into final caps. The chest/far seam needs semantic editing and later visual/mask review.",
        "prompt_instruction_candidate": pin(prompt_path), "generation_ready": False,
        "far185_extracted_or_imported": False, "source_images_modified": False,
        "final_cap_or_mask_image_written": False, "engine_or_generation_called": False,
    })
    write("HANDOFF.md", """# 185 远肩透视审核 v001

已使用 view_image 原尺寸实际查看 Root 已保留的182（E257）和185（E269）原图，未查看新Chest/Near输出或guide。185判定 FAIL：宽正面/近肩式盖与长下垂环取代了原182背心最右侧的窄弯far tab。孤立4件不代表远肩通过。无法仅凭两图证明模型是否逐像素复制近肩，或环是否完全新增。

下一次唯一target应回到原182。2172×724、零基准、右下不含的定位ROI候选：

1. [419,219,480,310]
2. [918,211,979,303]
3. [1438,220,1499,311]
4. [1946,215,2007,311]

边界不确定约±8源px；这些是技术定位窗，可能包含相邻胸甲/黑缝，不能当mask、不能本地矩形裁成最终cap，A全部null。视觉指示：仅保留胸片侧黑缝外的极窄image-RIGHT弯tab，保留原大小/位置/压缩透视；删除宽image-LEFT盖、胸/领/腰袋，禁止新增长环。

`perspective-review-v001.json` 记录原件SHA、实际查看、只读NumPy bbox依据与不确定；`next-far-edit-visual-instruction-candidate-v001.txt` 可作为Root后续短prompt的视觉补充，generation_ready=false。未生成、导入、提取185、改图或写媒体。
""")
    files = [pin(path) for path in sorted(OUT.iterdir()) if path.is_file()]
    for file in files:
        file["path"] = Path(file["path"]).relative_to(OUT).as_posix()
    freeze = write("review-freeze-v001.json", {"schema": "far185-review-freeze-v001", "files": files,
                   "file_count_excluding_manifest": len(files), "total_bytes_excluding_manifest": sum(p["bytes"] for p in files)})
    print(json.dumps({"report": pin(report), "freeze": pin(freeze), "verdict185": "FAIL_SOURCE_FAR_PERSPECTIVE",
                      "ROI": ROIS, "files_excluding_freeze": len(files), "bytes_excluding_freeze": sum(p["bytes"] for p in files)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
