"""Original technical pose diagram only; never a game-art drawing/editing tool."""
from pathlib import Path
import hashlib
import json
import math
import shutil
from PIL import Image, ImageDraw

root = Path("F:/Ourgame")
base = root / "source-assets/production/fairytale-hero-v001"
source, run = base / "sprite-run-walk-v002", base / "sprite-run-walk-v003"
assert not run.exists(), "Never overwrite an earlier candidate"
for relative in ("base-source.png", "sprite-request.json", "prompts/walk.txt", "references/layout-guides/walk.png"):
    target = run / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source / relative, target)
(run / "raw").mkdir()

near, far, torso = (198, 44, 55), (43, 102, 190), (100, 100, 100)
hip, shoulder = (256, 310), (256, 205)
# Six successive phases: near contact/support/push, far contact/support/push.
front, rear, stance, passing, reach = (350, 455), (175, 455), (245, 455), (300, 414), (350, 443)
legs = [(front, rear), (stance, passing), (rear, reach),
        (rear, front), (passing, stance), (reach, rear)]
back_hand, front_hand, neutral_hand = (183, 292), (329, 283), (250, 315)
arms = [(back_hand, front_hand), (neutral_hand, (270, 312)),
        (front_hand, back_hand), (front_hand, back_hand),
        ((270, 312), neutral_hand), (back_hand, front_hand)]
labels = ["NEAR heel contact", "NEAR support / FAR passes", "NEAR push / FAR reaches",
          "FAR heel contact", "FAR support / NEAR passes", "FAR push / NEAR reaches"]


def joint(start, end, length, bend_right=True):
    dx, dy = end[0] - start[0], end[1] - start[1]
    distance = math.hypot(dx, dy)
    assert 0 < distance <= 2 * length
    offset = math.sqrt(max(0., length * length - distance * distance / 4))
    sign = 1 if bend_right else -1
    return ((start[0] + end[0]) / 2 + sign * dy / distance * offset,
            (start[1] + end[1]) / 2 - sign * dx / distance * offset)


guide = Image.new("RGB", (3072, 512), (248, 248, 248))
draw = ImageDraw.Draw(guide)
for index, (feet, hands) in enumerate(zip(legs, arms)):
    x = index * 512
    def xy(p): return (p[0] + x, p[1])
    draw.rectangle((x + 1, 1, x + 510, 510), outline=(130, 130, 130), width=2)
    draw.text((x + 55, 12), f"{index + 1}: {labels[index]}", fill=(30, 30, 30))
    draw.text((x + 55, 30), "RED=near limb  BLUE=far limb (guide only)", fill=(30, 30, 30))
    draw.line((x + 48, 464, x + 464, 464), fill=(130, 130, 130), width=2)
    draw.ellipse((x + 210, 70, x + 302, 162), outline=torso, width=4)
    draw.line([xy((256, 162)), xy(shoulder), xy(hip)], fill=torso, width=8)
    for is_near in (False, True):
        color = near if is_near else far
        foot, hand = feet[0 if is_near else 1], hands[0 if is_near else 1]
        knee, elbow = joint(hip, foot, 90), joint(shoulder, hand, 76, not is_near)
        draw.line([xy(hip), xy(knee), xy(foot)], fill=color, width=10 if is_near else 7)
        draw.line([xy(shoulder), xy(elbow), xy(hand)], fill=color, width=9 if is_near else 6)
        for p in (knee, elbow):
            xx, yy = xy(p);draw.ellipse((xx - 5, yy - 5, xx + 5, yy + 5), fill=color)
        xx, yy = xy(foot)
        draw.line((xx - 13, yy, xx + 22, yy + 4), fill=color, width=5)
        if foot in (front, rear, stance):
            draw.ellipse((xx - 4, 460, xx + 4, 468), fill=color)
guide_path = run / "references/layout-guides/walk-six-phase-technical-v001.png"
guide.save(guide_path)
correction = """\nCRITICAL REGENERATION CORRECTION: the rejected previous row repeated the same
near-side leg/arm arrangement in both half-strides. That is forbidden.
Use the red/blue technical stick diagram ONLY as motion/limb-role truth, NEVER
as the character style or palette. RED means camera-NEAR, BLUE camera-FAR;
the final character must retain its original charcoal clothing/brown gloves.
Frames 1 and 4 must show OPPOSITE legs in front and OPPOSITE arm counter-swing.
Frames 2 and 5 must lift OPPOSITE knees/boots while the other foot supports.
Frame 3 reaches the FAR heel; frame 6 reaches the NEAR heel. Keep limb shading
and occlusion consistent, so the swapped near/far roles are visible. Do not
reuse a three-pose cycle twice, do not leave the near hand permanently behind,
do not mirror the complete character for the second half. All six face RIGHT.
Match the attached canonical idle helmet, proportions, gloves and boots.
Output six full, separated figures in one strip on solid GREEN #00FF00.
No diagram lines, colored bones, phase labels, foot dots or text in final art.
"""
prompt_path = run / "prompts/walk.txt"
prompt_path.write_text(prompt_path.read_text(encoding="utf-8") + correction, encoding="utf-8")
request_path = run / "sprite-request.json"
request = json.loads(request_path.read_text(encoding="utf-8-sig"))
request["states"]["walk"]["action"] += correction
request["project_motion_guide"] = {"path": str(guide_path),
    "sha256": hashlib.sha256(guide_path.read_bytes()).hexdigest(),
    "role": "original technical six-phase near/far diagram only, not artwork or identity"}
request_path.write_text(json.dumps(request, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"run": str(run), "native_prompt": str(prompt_path),
    "native_references": [str(run / "base-source.png"), str(guide_path)],
    "source_art_modified": False, "native_generation_performed": False,
    "motion_accepted": False}, ensure_ascii=False))
