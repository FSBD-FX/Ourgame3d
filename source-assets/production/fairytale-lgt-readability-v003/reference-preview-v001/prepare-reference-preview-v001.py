from __future__ import annotations

import hashlib
import json
import math
import shutil
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parent
PROJECT = Path("F:/Ourgame").resolve()
TARGET_CORE_HEIGHT = 72
BASELINE_Y = 96
SOURCES = [
    {
        "id": "158-ready0",
        "label": "158 · 现有 Ready0",
        "description": "现有角色姿态参考",
        "source": PROJECT / "source-assets/production/fairytale-sword-v001/run-ready-v002/curated/frame-0.png",
        "copy": "158-ready0-original.png",
        "expected_sha256": "d3f766506a9cc623c38787836a9c23c0126d185d1bdf7e8946181efd554338c5",
    },
    {
        "id": "179-soft-leather",
        "label": "179 · 软皮轻甲试样",
        "description": "棕色短衣、软肩片与腰部层次参考",
        "source": PROJECT / "source-assets/production/fairytale-lgt-readability-v003/concept179-v001/raw/179-soft-leather-reference.png",
        "copy": "179-soft-leather-original.png",
        "expected_sha256": "f29ccca00cfb1095dc263240b3f554c780e421cfebf531099e2e92f5281c3c38",
    },
]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    if not ROOT.is_relative_to(PROJECT / "source-assets/production/fairytale-lgt-readability-v003"):
        raise RuntimeError("Unexpected output root")
    if (ROOT / "reference-preview.html").exists() or (ROOT / "preparation-freeze-v001.json").exists():
        raise RuntimeError("Existing version must not be overwritten")

    rows = []
    for item in SOURCES:
        source = item["source"]
        source_sha = digest(source)
        if source_sha != item["expected_sha256"]:
            raise RuntimeError(f"Source pin mismatch: {source}")
        with Image.open(source) as im:
            if im.mode != "RGBA":
                raise RuntimeError(f"RGBA expected: {source}")
            width, height = im.size
            alpha = im.getchannel("A")
            core_bbox = alpha.point(lambda value: 255 if value >= 128 else 0).getbbox()
            nonzero_bbox = alpha.getbbox()
            if core_bbox is None:
                raise RuntimeError(f"Empty core: {source}")
            core_height = core_bbox[3] - core_bbox[1]
            scale = TARGET_CORE_HEIGHT / core_height
            core_center_x = (core_bbox[0] + core_bbox[2]) / 2
            copy_path = ROOT / item["copy"]
            if copy_path.exists():
                raise RuntimeError(f"Existing output: {copy_path}")
            shutil.copy2(source, copy_path)
            if digest(copy_path) != source_sha or copy_path.stat().st_size != source.stat().st_size:
                raise RuntimeError(f"Byte copy mismatch: {copy_path}")
            css = {
                "image_width_px": width * scale,
                "image_height_px": height * scale,
                "left_offset_from_center_px": -core_center_x * scale,
                "top_px": BASELINE_Y - core_bbox[3] * scale,
                "core_top_px": BASELINE_Y - TARGET_CORE_HEIGHT,
                "core_bottom_px": BASELINE_Y,
            }
            if not math.isclose(core_height * scale, TARGET_CORE_HEIGHT, abs_tol=1e-12):
                raise RuntimeError("Core height calculation failed")
            rows.append({
                "id": item["id"],
                "label": item["label"],
                "description": item["description"],
                "source_path": str(source),
                "preview_copy": item["copy"],
                "source_and_copy_sha256": source_sha,
                "source_and_copy_bytes": source.stat().st_size,
                "mode": "RGBA",
                "image_size": [width, height],
                "alpha_nonzero_bbox_ltrb_exclusive": list(nonzero_bbox),
                "alpha_core_threshold_inclusive": 128,
                "alpha_core_bbox_ltrb_exclusive": list(core_bbox),
                "alpha_core_height": core_height,
                "css_scale": scale,
                "css_at_100_percent": css,
            })

    generated_at = datetime.now(timezone.utc).isoformat()
    measurement = {
        "schema": "ourgame-reference-preview-v001",
        "generated_at_utc": generated_at,
        "status": "reference_only_not_imported_not_complete_animation",
        "viewed_or_screenshot_by_producer": False,
        "root_retention_required_before_viewing": True,
        "target_visible_core_height_css_px": TARGET_CORE_HEIGHT,
        "baseline_y_css_px_at_100_percent": BASELINE_Y,
        "method": "Read alpha only; take alpha >= 128 bounding-box height; CSS scale = 72 / height. Original PNG bytes are copied unchanged. CSS aligns core bottom to the shared baseline and core horizontal center to the stage center.",
        "limits": [
            "Alpha threshold supplies a display measurement, not a semantic body or rig measurement.",
            "Soft alpha and isolated low-alpha pixels outside the measured core remain in the untouched source image.",
            "400% enlarges the same 72px reference layout to a 288px core for inspection; it is not an in-game character size or new image asset.",
            "The different source poses and original dimensions are not proof of a locked common body, better animation, or accepted style.",
            "No engine import, animation or playable-game change is included.",
        ],
        "images": rows,
    }
    write_json(ROOT / "reference-measurements-v001.json", measurement)

    cards = []
    for row in rows:
        css = row["css_at_100_percent"]
        box = row["alpha_core_bbox_ltrb_exclusive"]
        cards.append(f'''<article class="reference-card">
      <header><h2>{row["label"]}</h2><p>{row["description"]}</p></header>
      <div class="stage" role="img" aria-label="{row["label"]}，alpha 核心高度按 72 像素等比展示">
        <span class="baseline" aria-hidden="true"></span>
        <img src="{row["preview_copy"]}" alt="{row["label"]}原始透明 PNG 参考图" draggable="false"
          style="--image-w:{css["image_width_px"]:.12f}px;--image-h:{css["image_height_px"]:.12f}px;--left:{css["left_offset_from_center_px"]:.12f}px;--top:{css["top_px"]:.12f}px">
      </div>
      <div class="facts"><span>核心高度 <strong class="core-height">72 px</strong></span><span>原图 {row["image_size"][0]} × {row["image_size"][1]}</span></div>
      <details><summary>比例依据</summary><p>alpha ≥ 128 核心边界（右、下边界不含）：{box}；高度 {row["alpha_core_height"]} px。CSS 缩放比例为 72 ÷ {row["alpha_core_height"]} = {row["css_scale"]:.12f}。两张图只对齐核心高度与底边。</p><p class="hash">原图与副本 SHA-256：{row["source_and_copy_sha256"]}</p></details>
    </article>''')
    html = '''<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>轻甲可读性 · 小比例参考 v001</title>
<style>
*{box-sizing:border-box}body{margin:0;background:#ede9df;color:#292c2b;font-family:system-ui,"Microsoft YaHei",sans-serif;line-height:1.6}main{max-width:1060px;margin:auto;padding:32px 24px 48px}.eyebrow{font-size:12px;letter-spacing:.16em;color:#6b6e63;margin:0 0 8px}h1{font-size:25px;line-height:1.3;margin:0 0 14px}h2{font-size:17px;line-height:1.4;margin:0}.lead{max-width:780px;margin:0 0 24px;color:#555a53}.controls{display:flex;flex-wrap:wrap;align-items:center;gap:16px 28px;padding:14px 18px;margin-bottom:20px;border:1px solid #c6c7bc;border-radius:8px;background:#f7f4eb}fieldset{display:flex;gap:12px;margin:0;padding:0;border:0}legend{float:left;margin-right:12px;font-size:13px;color:#5e635b}label{font-size:14px;cursor:pointer}input{accent-color:#835c2e;vertical-align:middle;margin-right:5px}.zoom-note{font-size:12px;color:#666c63}.grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:18px;--zoom:1}.reference-card{overflow:hidden;border:1px solid #c6c7bc;border-radius:10px;background:#f7f4eb}.reference-card header{padding:20px 22px 14px}.reference-card header p{margin:5px 0 0;color:#676d61;font-size:13px}.stage{position:relative;height:calc(124px * var(--zoom));overflow:hidden;background:#dcded2;transition:background-color .15s}.grid.dark .stage{background:#292f31}.stage img{position:absolute;display:block;max-width:none;width:calc(var(--image-w) * var(--zoom));height:calc(var(--image-h) * var(--zoom));left:calc(50% + var(--left) * var(--zoom));top:calc(var(--top) * var(--zoom));image-rendering:auto}.baseline{position:absolute;left:12%;right:12%;top:calc(96px * var(--zoom));height:1px;background:#a6ad9d66}.dark .baseline{background:#8f9d9f44}.facts{display:flex;flex-wrap:wrap;justify-content:space-between;gap:6px;padding:13px 22px;font-size:12px;color:#61665d;border-top:1px solid #c6c7bc}strong{font-weight:600;color:#2f382e}details{padding:0 22px 17px;font-size:12px;color:#62675d}summary{cursor:pointer}details p{margin:9px 0 0}.hash{overflow-wrap:anywhere;font-family:ui-monospace,monospace;font-size:11px}.note{font-size:13px;color:#5c6258;margin:22px 0 0;max-width:850px}.status{display:inline-block;border:1px solid #b6b9ac;border-radius:4px;padding:3px 9px;font-size:12px;margin-bottom:12px;background:#e5e7dc}a{color:#4b654a}footer{font-size:12px;color:#74796f;margin-top:22px}@media(max-width:680px){main{padding:24px 16px}.grid{grid-template-columns:1fr}.controls{gap:12px}h1{font-size:22px}}
</style>
</head>
<body>
<main>
  <p class="eyebrow">OURGAME / EV048 / REFERENCE V001</p>
  <span class="status">参考图 · 尚未替换进游戏 · 非完整动画</span>
  <h1>同一小比例，观察盔甲与轮廓</h1>
  <p class="lead">将两张原图的 alpha 核心高度统一为 72 CSS 像素，便于观察钟盔、肩部与腰部层次。新图尝试棕色软皮轻甲；这里只比较参考图在小比例下的呈现。</p>
  <div class="controls">
    <fieldset><legend>背景</legend><label><input type="radio" name="background" value="light" checked>浅色</label><label><input type="radio" name="background" value="dark">深色</label></fieldset>
    <label><input type="checkbox" id="zoom">400% 检查</label>
    <span class="zoom-note" id="zoom-note">核心高度 72 px · 实际屏幕尺寸随浏览器缩放变化</span>
  </div>
  <section class="grid" id="comparison" aria-label="两张角色参考图比较">
__CARDS__
  </section>
  <p class="note">PNG 副本保持原始字节，页面只通过 CSS 等比缩放；没有重绘、抠图或修改颜色。400% 开关放大这份布局以检查边缘。alpha 核心仅用于测量显示尺寸，不代表骨架或身体边界；两张参考图的姿态、原图尺寸也不同，不能据此认定母体已锁定或动画已完成。</p>
  <footer>测量与文件校验：<a href="reference-measurements-v001.json">JSON</a> · 候选参考页面，待 Root 归档后查看。</footer>
</main>
<script>
const comparison=document.getElementById('comparison');
for(const option of document.querySelectorAll('input[name="background"]')){
  option.addEventListener('change',()=>comparison.classList.toggle('dark',option.value==='dark'&&option.checked));
}
document.getElementById('zoom').addEventListener('change',event=>{
  const enlarged=event.target.checked;
  comparison.style.setProperty('--zoom',enlarged?'4':'1');
  for(const label of document.querySelectorAll('.core-height'))label.textContent=enlarged?'288 px':'72 px';
  document.getElementById('zoom-note').textContent=enlarged?'400% 检查 · 核心高度 288 px · 未生成新图片':'核心高度 72 px · 实际屏幕尺寸随浏览器缩放变化';
});
</script>
</body>
</html>
'''.replace("__CARDS__", "\n".join(cards))
    (ROOT / "reference-preview.html").write_text(html, encoding="utf-8")
    handoff = """# 小比例轻甲参考比较 v001

状态：参考图，尚未替换进游戏，非完整动画。Root 必须先完成 E 过程媒体归档，再浏览、截图或展示本目录 HTML / PNG。

- `reference-preview.html` 可离线打开，无网络资源。浅 / 深背景切换；400% 放大同一布局检查。
- 两个 PNG 是原文件的逐字节副本，SHA-256 与大小已复核；没有生成、重绘或图片后处理。
- `reference-measurements-v001.json` 记录实际 alpha ≥ 128 核心 bbox / 高度和 CSS 比例。核心高度映射为 72 CSS px；底边共用基线，横向按核心中心对齐。
- 400% 时核心高度为 288 CSS px；这只是参考页面放大。浏览器缩放 / 屏幕密度会影响实际物理像素。
- 低透明度散点和半透明边缘保留。不同源图姿态与分辨率不能证明身体像素一致、动画改善或风格已验收。

范围：仅本候选目录。没有修改 ActualSource、ledger、项目 README / progress 或过程媒体；没有运行 UE / UBT，没有生成图，也没有浏览或截图。Root 可在归档后进行可视检查。
"""
    (ROOT / "HANDOFF.md").write_text(handoff, encoding="utf-8")

    pins = []
    for path in sorted(ROOT.iterdir()):
        if path.is_file() and path.name != "preparation-freeze-v001.json":
            pins.append({"path": path.name, "bytes": path.stat().st_size, "sha256": digest(path)})
    freeze = {
        "schema": "ourgame-reference-preview-freeze-v001",
        "generated_at_utc": generated_at,
        "status": "candidate_requires_root_retention_and_visual_review",
        "file_count_excluding_this_manifest": len(pins),
        "total_bytes_excluding_this_manifest": sum(item["bytes"] for item in pins),
        "viewed_or_screenshot_by_producer": False,
        "source_png_bytes_unchanged": True,
        "files": pins,
    }
    write_json(ROOT / "preparation-freeze-v001.json", freeze)
    print(json.dumps({"root": str(ROOT), "measurements": rows, "file_count": len(pins), "total_bytes": freeze["total_bytes_excluding_this_manifest"], "freeze_sha256": digest(ROOT / "preparation-freeze-v001.json"), "viewed": False}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
