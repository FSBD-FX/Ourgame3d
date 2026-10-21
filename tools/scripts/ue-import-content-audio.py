"""Run in UE Editor Python. Owns only /Game/Production/FirstBatch/v001/Audio.
Imports numeric-checked candidates; this is not an audition or final mix approval.
"""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import unreal

ROOT = Path(unreal.Paths.project_dir()).resolve().parent
SOURCE = ROOT / 'source-assets/production/audio-v001'
manifest = json.loads((SOURCE / 'manifest.json').read_text(encoding='utf-8-sig'))
report_path = ROOT / 'UnrealGame/Saved/Bootstrap/content-audio-v001-import.json'
previous = json.loads(report_path.read_text(encoding='utf-8-sig')) if report_path.exists() else {}
previous_hashes = {row['asset']: row['source_sha256'] for row in previous.get('assets', [])}
tasks, expected = [], []
for cue in manifest['cues']:
    source = SOURCE / cue['file']
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    assert digest == cue['sha256'], f'Changed source: {source}'
    name = 'SW_' + cue['id'].replace('-', '_') + '_v001'
    destination = '/Game/Production/FirstBatch/v001/Audio'
    asset_path = destination + '/' + name
    expected.append({'id': cue['id'], 'source': str(source), 'source_sha256': digest, 'asset': asset_path})
    if unreal.EditorAssetLibrary.does_asset_exist(asset_path):
        assert previous_hashes.get(asset_path) == digest, f'Existing asset without matching receipt: {asset_path}'
        continue
    task = unreal.AssetImportTask()
    for prop, value in [('filename', str(source)), ('destination_path', destination),
                        ('destination_name', name), ('automated', True), ('save', True), ('replace_existing', False)]:
        task.set_editor_property(prop, value)
    tasks.append(task)
if tasks:
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks(tasks)
for row in expected:
    sound = unreal.load_asset(row['asset'])
    assert isinstance(sound, unreal.SoundWave), f'SoundWave missing: {row["asset"]}'
    row['duration_s'] = sound.get_editor_property('duration')
    row['channels'] = sound.get_editor_property('num_channels')
    assert row['channels'] == 1 and row['duration_s'] > 0, row
report = {'utc': datetime.now(timezone.utc).isoformat(), 'assets': expected,
          'success': len(expected) == manifest['actual_count'], 'actual_count': len(expected),
          'auditioned': False, 'final_mix_accepted': False, 'scope': 'Candidate import and class/metadata verification only'}
report_path.parent.mkdir(parents=True, exist_ok=True)
report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
unreal.log('Content audio candidate import receipt: ' + str(report_path))
