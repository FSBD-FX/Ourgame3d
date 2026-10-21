from pathlib import Path

HERE = Path(__file__).resolve().parent
BASE = Path("F:/Ourgame/tools/scripts/postprocess-leather-ready-trial-v001.py")
source = BASE.read_text(encoding="utf-8-sig")
helpers = source[source.index("def require("):source.index("def expected_stack(")]
pixels = source[source.index("def verify_pixels("):source.index("def main(")]
head = '''"""Strict actual native P1-only postprocess candidate. Run only after Root capture/flush.
No UE launch, Source mutation, forced pose or art acceptance. Original pixels stay untouched.
"""
from pathlib import Path
import argparse
import hashlib
import json
import math
import os
import subprocess
import zlib
from urllib.parse import quote
import imageio_ffmpeg
import numpy as np
from PIL import Image

ROOT = Path("F:/Ourgame").resolve()
PRIMARY_NEW = "/Game/Production/ArtTrials/EV048/v013/HeroLeatherPrimary1/"
PRIMARY_OLD = "/Game/Production/ArtTrials/EV048/v007/HeroSwordArmorPrimary1/"
READY_NEW = "/Game/Production/ArtTrials/EV048/v012/HeroLeatherReady/"
READY_OLD = "/Game/Production/ArtTrials/EV048/v006/HeroSwordArmorReady/"
BODY = "/Game/Production/ArtTrials/EV048/v005/HeroSwordBody/"
SWORD = "/Game/Production/FirstBatch/v002/CandidateComponents/T_military_sword_v002.T_military_sword_v002"
CANVAS = 72.0 * 512.0 / 416.0
PHASES = ["start", "baseline_no_armor", "light_pending_cancel", "light_canceled", "light_pickup_commit", "light_ready", "light_three_stage"]
PRIMARY1_SCOPE = "Opt-in new leather Primary1 trial only: same real light commit and weapon instance, two fresh normal J attacks with existing .45s combo expiry and normal direction input; six phases each facing, then actual Ready. No forced pose/frame/clock/gear, no Primary2/3 acceptance, no full locomotion/equip/hurt/death/audio/Save or full unit acceptance."
NATIVE_SOURCE_PINS = {
 "UnrealGame/Source/CodexDungeon/DungeonFairytaleSwordPresentation.cpp": {"bytes": 20146, "sha256": "d7b06d5809b0c47c2460ba42e37855ab65a44ce534931ce494d29584a478decc"},
 "UnrealGame/Source/CodexDungeon/DungeonFairytaleEquipmentBoundProbe.h": {"bytes": 1992, "sha256": "dcbfb6ac54995b361dd8e7ad0578e04bfb92ef995d45d0d905a4e8061f1e7f80"},
 "UnrealGame/Source/CodexDungeon/DungeonFairytaleEquipmentBoundProbe.cpp": {"bytes": 31228, "sha256": "446e0b6b9e83fb528e17fe3f99a3a607355ec881d81261540c0c0c9cf1e11c93"},
}

'''
output = head + helpers + (HERE / "contract-functions-v001.py.inc").read_text(encoding="utf-8") + "\n\n" + pixels + (HERE / "main-functions-v001.py.inc").read_text(encoding="utf-8")
(HERE / "postprocess-leather-primary1-trial-v001.py").write_text(output, encoding="utf-8", newline="\n")
