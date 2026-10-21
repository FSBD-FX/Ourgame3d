"""Separate versioned runtime presentation tool; does not capture or render."""
from pathlib import Path
R=Path('F:/Ourgame');T=R/'tools/scripts'
s=(T/'postprocess-sword-armor-ready-v002.py').read_text(encoding='utf-8-sig')
s=s.replace('import hashlib,json,math,shutil,subprocess','import argparse,hashlib,json,math,shutil,subprocess')
s=s.replace("S=R/'source-assets/production/backups/2026-10-16_SwordReadyArmor24-preloadFix-actual126GREEN-v101'", "p=argparse.ArgumentParser();p.add_argument('--snapshot',required=True);args=p.parse_args()\nS=(R/args.snapshot).resolve();assert S.is_relative_to((R/'source-assets/production/backups').resolve())")
s=s.replace('2026-10-16_钟盔军剑低位胸肩真实按键试装_v002','2026-10-16_钟盔军剑首斩穿甲真实按键试装_v001')
s=s.replace('sword-armor-runtime-verification.json','sword-armor-primary1-runtime-verification.json').replace('visible-ready-head-gate-v001.json','visible-ready-primary-head-gate-v001.json')
s=s.replace('v101-source-binding-audit-v001.json','compiled-source-binding-audit-v001.json').replace('fairytale-sword-lowguard-armor-ready-silent.mp4','fairytale-sword-primary1-armor-silent.mp4').replace('tool-postprocess-sword-armor-ready-v002.py','tool-postprocess-sword-armor-primary1-v001.py')
old='Native158/159 lowguard and161/162/163 Ready-only armor actual normal-input trial, v101 Source/DLL. Attack armor remains absent by design. 72px body/UIoff; silent. Actual174observations/175PNGs and kernelphase/nativepixel checks passed. Selectedframes and video not visually reviewed yet; armor/thumb/fullmotion/allstates/combos/audio remain unfinished.'
assert old in s
s=s.replace(old,'Native158/159 lowguard+Primary1six body, native161/162/163 Ready-only armor and164/165/167 Primary1 matching armor actual normal-input trial. Source/DLL bound to supplied compiled snapshot. 72px body/UIoff; silent. All recorded observations/PNGs, kernel phases, actual Ready7/Primary8 stacks/nativepixel/visiblehead gates passed. Selectedframes/video await explicit art review; equipment IDs/thumb/fullmotion/allstates/combos/audio remain unfinished.')
out=T/'postprocess-sword-armor-primary1-v001.py';assert not out.exists();compile(s,str(out),'exec');out.write_text(s,encoding='utf-8')
print('Prepared actual-runtime-only postprocessor; not run/no video yet.')
