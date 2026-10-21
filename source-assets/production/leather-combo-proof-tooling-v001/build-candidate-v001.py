from pathlib import Path
import json

HERE = Path(__file__).resolve().parent
BASE = Path("F:/Ourgame/tools/scripts/postprocess-leather-primary1-trial-v001.py")
SOURCE = Path("F:/Ourgame/source-assets/production/fairytale-lgt-readability-v003/leather-combo-source-v001")
text = BASE.read_text(encoding="utf-8-sig")
helpers = text[text.index("def require("):text.index("def expected_stack(")]
pixels = text[text.index("def verify_pixels("):text.index("def write_whole_phase_view(")]
scope = "Opt-in soft-leather combo-only trial: normal Enter/E/A cancel/E single actual LGT commit, normal J three-stage chain, actual post-chain Ready, native chain expiry, normal opposite direction, second fresh normal J three-stage chain and final actual Ready. Six actual distinct attack IDs, each facing/stage mask63; original body layers plus matching new3 armor per clip. No forced pose/frame/clock/gear or invented phase counters. QA registered source is not lawful loot/shop/reward. No full unit, all actions, armor compatibility, complete equip animation, grasp/clearance, audio or Save acceptance. Default proof remains separate."
head = '''"""Unapplied combo-only proof tooling. Root capture/technical verification only.
Original Source, native PNGs, clocks and original RGBA stay unchanged; no art acceptance.
"""
from pathlib import Path
import argparse, hashlib, json, math, os, subprocess, zlib
from urllib.parse import quote
import imageio_ffmpeg
import numpy as np
from PIL import Image
ROOT = Path("F:/Ourgame").resolve()
CLIPS = ("Ready", "Primary1", "Primary2", "Primary3")
COMPONENTS = ("Chest", "ShoulderNear", "ShoulderFar")
NEW_NS = {"Ready":"/Game/Production/ArtTrials/EV048/v012/HeroLeatherReady/", "Primary1":"/Game/Production/ArtTrials/EV048/v013/HeroLeatherPrimary1/", "Primary2":"/Game/Production/ArtTrials/EV048/v014/HeroLeatherPrimary2/", "Primary3":"/Game/Production/ArtTrials/EV048/v015/HeroLeatherPrimary3/"}
OLD_NS = {"Ready":"/Game/Production/ArtTrials/EV048/v006/HeroSwordArmorReady/", "Primary1":"/Game/Production/ArtTrials/EV048/v007/HeroSwordArmorPrimary1/", "Primary2":"/Game/Production/ArtTrials/EV048/v010/HeroSwordPrimary2Armor/", "Primary3":"/Game/Production/ArtTrials/EV048/v011/HeroSwordPrimary3/"}
BODY_NS = {"Ready":"/Game/Production/ArtTrials/EV048/v005/HeroSwordBody/", "Primary1":"/Game/Production/ArtTrials/EV048/v005/HeroSwordBody/", "Primary2":"/Game/Production/ArtTrials/EV048/v009/HeroSwordPrimary2/", "Primary3":"/Game/Production/ArtTrials/EV048/v011/HeroSwordPrimary3/"}
SWORD = "/Game/Production/FirstBatch/v002/CandidateComponents/T_military_sword_v002.T_military_sword_v002"
CANVAS = 72. * 512. / 416.
PHASES = ["start", "baseline_no_armor", "light_pending_cancel", "light_canceled", "light_pickup_commit", "light_ready", "light_three_stage"]
NATIVE_NAMES = ("DungeonFairytaleSwordPresentation.cpp", "DungeonFairytaleSwordPrimary2ArmorV001.inl", "DungeonFairytaleSwordPrimary3V001.inl", "DungeonFairytaleEquipmentBoundProbe.h", "DungeonFairytaleEquipmentBoundProbe.cpp")
TOOL_FILES = ("capture-leather-combo-trial-v001.ps1", "postprocess-leather-combo-trial-v001.py", "verify-leather-combo-proof-v001.py", "verify-native-bound-capture-pixels-v001.py")
'''
head += "COMBO_SCOPE = " + repr(scope) + "\n\n"
stack = '''def expected_stack(frame, stage=-1):
    clip = "Ready" if stage < 0 else "Primary" + str(stage + 1)
    components = ["BodyRest", "ShoulderFar", "Chest", "NearArmWithoutHand", "ShoulderNear"]
    if stage >= 0: components.append("HelmetForeground")
    components.append("NearHand")
    result = []
    for component in components:
        if component == "NearHand": result.append(SWORD)
        armor = component in COMPONENTS
        result.append(object_path(NEW_NS[clip] if armor else OLD_NS[clip], f"T_Fairytale_{'Leather' if armor else 'Sword'}{clip}{component}_{frame:03d}_v001"))
    return result

def body_path(clip, frame):
    name = f"T_Fairytale_Sword{clip}{'Body' if clip == 'Primary3' else ''}_{frame:03d}_{'v001' if clip == 'Primary3' else 'v002'}"
    return object_path(BODY_NS[clip], name)

def identifier(value, label, allow_zero=False):
    require(isinstance(value,str) and value.isascii() and value.isdigit() and str(int(value)) == value and (0 if allow_zero else 1) <= int(value) <= 2**64-1, "Invalid canonical native ID: " + label)
    return int(value)

'''
main = text[text.index("def write_whole_phase_view("):]
main = main.replace("leather-primary1", "leather-combo").replace("P1-only", "Combo-only")
main = main.replace('    parser.add_argument("--expected-automation-count", type=int, default=157)\n', '')
main = main.replace('verify_sources(snapshot, index, args.expected_automation_count)', 'verify_sources(snapshot, index)')
begin = main.index('    for facing in (-1, 1):\n', main.index('def main('))
end = main.index('    whole_view =', begin)
part = main[begin:end]
part = part.replace('        for frame in range(6):', '        for stage in range(3):\n            for frame in range(6):')
lines = part.splitlines()
lines = [line if idx < 3 else '    ' + line for idx, line in enumerate(lines)]
part = '\n'.join(lines) + '\n'
part = part.replace('selection[(facing, frame)]', 'selection[(facing, stage, frame)]')
part = part.replace("-phase-{frame}-", "-stage-{stage+1}-phase-{frame}-")
main = main[:begin] + part + main[end:]
main = main.replace('"selected_unscaled_crops": 12', '"selected_unscaled_crops": 36')
main = main.replace('"actual_primary1_masks_left_right": [63, 63]', '"actual_combo_masks_left_right_by_stage": report["leather_combo_masks_left_right_by_stage"]')
main = main.replace("实际软皮 P1", "实际软皮三段连击").replace("左右各六阶段", "左右各三段、每段六阶段")
main = main.replace("(e.facing<0?'左':'右')+' / '+e.frame", "(e.facing<0?'左':'右')+' / P'+(e.stage+1)+' / '+e.frame")
main = main.replace("facing:e.facing,frame:e.frame", "facing:e.facing,stage:e.stage,frame:e.frame")
main = main.replace('actual_leather_P1_6_both_facings_technical_verified_visual_review_pending', 'actual_leather_combo_36_phases_technical_verified_visual_review_pending')
old_readme = main[main.index('    new(archive / "README.md",'):main.index('    print(json.dumps(', main.index('    new(archive / "README.md",'))]
new_readme = '    new(archive / "README.md", "真实软皮Ready/P1/P2/P3连击技术留档：正常Enter/E/A取消/E单次提交LGT；每面正常J三段缓冲连击，六个不同实际ActionId，左右每段6阶段。首面实际Ready>=3、链过期后正常转向并重新J；另一面末段结束后实际Ready>=3。36张原生无缩放裁图、完整阶段视图和墙钟CFR30静音视频仅供实看。原PNG、Source/DLL、1151包合同和原始RGBA均前后绑定。技术通过不授予美术、完整装备、全动作、音频、存档或完整单位接受。\\n")\n'
main = main.replace(old_readme, new_readme)
(HERE / "postprocess-leather-combo-trial-v001.py").write_text(head + helpers + stack + (HERE / "source-contract-v001.py.inc").read_text(encoding="utf-8") + "\n\n" + (HERE / "flow-contract-v001.py.inc").read_text(encoding="utf-8") + "\n\n" + pixels + main, encoding="utf-8", newline="\n")
