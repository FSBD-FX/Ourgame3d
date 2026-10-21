"""Supplement the frozen Air core proof with actual brown Ready identity."""
from pathlib import Path
import argparse
import hashlib
import json
import shutil


def pin(p):
    p = Path(p).resolve()
    b = p.read_bytes()
    return dict(path=p.as_posix(), bytes=len(b), sha256=hashlib.sha256(b).hexdigest())


def read(p):
    return json.loads(Path(p).read_text(encoding='utf-8-sig'))


ap = argparse.ArgumentParser()
ap.add_argument('--archive', required=True)
a = ap.parse_args()
m = Path(a.archive).resolve()
r = read(m / '原件/runtime-report.json')
launch = read(m / 'launch-receipt-v001.json')
reg = read(m / 'preregistration-v001.json')
assert r['passed'] is True and r['flow_complete'] is True
assert launch['process_id'] == int(r['process_id'])
assert '-DungeonFairytaleLeatherReadyPreview' in launch['arguments']
cm = read(reg['compiled_manifest_pin']['path'])
members = {x['path']: x for x in cm['files']}
root = Path('F:/Ourgame')
rows = []
for i, o in enumerate(r['observations']):
    d = o['old_draw']
    if (o['armor_instance'] != r['armor_instance'] or o['new_air_draw']['drawn']
            or d['clip'] != 'sword_ready_idle' or not d['active'] or not d['supported']
            or not d['armor_drawn']):
        continue
    assert d['sim'] == o['sim'] and d['texture_ready'] is True and d['sword_drawn'] is True
    assert o['armor_version'] == r['armor_version'] and o['owner'] == r['owner']
    frame = d['frame']
    assert type(frame) is int and 0 <= frame < 4 and len(d['actual_stack']) == 7
    paths = []
    for slot, component in [(1, 'ShoulderFar'), (2, 'Chest'), (4, 'ShoulderNear')]:
        name = f'T_Fairytale_LeatherReady{component}_{frame:03d}_v001'
        package = '/Game/Production/ArtTrials/EV048/v012/HeroLeatherReady/' + name
        assert d['actual_stack'][slot] == package + '.' + name
        relative = 'UnrealGame/Content/' + package.removeprefix('/Game/') + '.uasset'
        current = pin(root / relative)
        assert (current['bytes'], current['sha256']) == (members[relative]['bytes'], members[relative]['sha256'])
        paths.append(current)
    rows.append(dict(observation=i, draw_id=d['draw_id'], frame=frame, armor_instance=o['armor_instance'],
                     armor_version=o['armor_version'], actual_brown_armor3=paths))
assert len(rows) >= 3
result = dict(schema='Root-Air6-brown-Ready-identity-supplement-v001', passed=True,
              source='Actual launch flags and completed native Ready draw stacks; no synthetic frame',
              native_report=pin(m / '原件/runtime-report.json'), launch=pin(m / 'launch-receipt-v001.json'),
              compiled_manifest=reg['compiled_manifest_pin'], checker=pin(__file__), verified_Ready_callbacks=rows,
              visual_reviewed=False, full_realtime_playback_reviewed=False, audio_listened=False, FinalAccepted=False)
out = m / 'brown-Ready-identity-verification-v001.json'
with out.open('x', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)
copy = m / '展示副本' / Path(__file__).name
assert not copy.exists()
shutil.copy2(Path(__file__), copy)
assert pin(copy)['sha256'] == pin(__file__)['sha256']
print(json.dumps(dict(output=pin(out), Ready_callbacks=len(rows)), ensure_ascii=False))
