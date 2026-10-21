"""Quality checks and retained contact sheet for the offline sprite conversion."""
from pathlib import Path
import hashlib
import json
import shutil

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent
PROJECT = ROOT.parents[2]
manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
archive = PROJECT / "过程图稿与视频/2026-10-12_首房间二维角色动作检查_v002"
if archive.exists():
    raise SystemExit("Archive exists; use a fresh version instead of overwriting.")
(archive / "原件").mkdir(parents=True)
(archive / "展示副本").mkdir()
report = {"frames": [], "all_rgba": True, "all_nonblank": True, "all_have_transparency": True}
sheet = Image.new("RGB", (8 * 170, 10 * 190), (34, 39, 45))
draw = ImageDraw.Draw(sheet)
row = 0
for kind, character in manifest["characters"].items():
    for clip, detail in character["clips"].items():
        for col, relative in enumerate(detail["frames"]):
            path = ROOT / relative
            im = Image.open(path)
            alpha = im.getchannel("A")
            bounds = alpha.getbbox()
            extrema = alpha.getextrema()
            report["all_rgba"] &= im.mode == "RGBA" and im.size == (256, 256)
            report["all_nonblank"] &= bounds is not None
            report["all_have_transparency"] &= extrema[0] == 0 and extrema[1] > 0
            report["frames"].append({"path": relative, "size": list(im.size), "mode": im.mode,
                "alpha_bounds": list(bounds) if bounds else None,
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
            destination = archive / "原件" / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, destination)
            preview = im.resize((160, 160), Image.Resampling.LANCZOS)
            sheet.paste(preview, (col * 170 + 5, row * 190 + 20), preview)
            draw.text((col * 170 + 5, row * 190 + 3), f"{kind} {clip} {col:03d}", fill=(230, 230, 230))
        row += 1
report["frame_count"] = len(report["frames"])
report["expected_count"] = 64
report["passed"] = all(report[k] for k in ("all_rgba", "all_nonblank", "all_have_transparency")) and report["frame_count"] == 64
(ROOT / "quality-report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
sheet.save(archive / "展示副本/character-actions-contact-sheet.png")
shutil.copy2(ROOT / "manifest.json", archive / "原件/manifest.json")
shutil.copy2(ROOT / "quality-report.json", archive / "原件/quality-report.json")
(archive / "来源与状态.json").write_text(json.dumps({
    "version": "v002", "date": "2026-10-12", "status": "已转绘并通过像素结构检查；等待视觉检查",
    "source": str(ROOT), "license": "Kenney Mini Dungeon CC0 1.0",
    "generation": "本地 Blender 5.2.2 Workbench 转绘，无付费生成",
    "originals": "原件/sprites/**", "presentation": "展示副本/character-actions-contact-sheet.png",
    "bounds": "原型动画素材检查；不是实际游戏运行证明；尚非最终画风",
    "frame_count": report["frame_count"], "checks_passed": report["passed"],
}, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps({"passed": report["passed"], "frame_count": report["frame_count"], "archive": str(archive)}, ensure_ascii=False))
