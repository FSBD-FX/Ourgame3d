"""Preserve exact provenance and verified naming failure before recorder repair."""
from pathlib import Path
import collections
import hashlib
import json
import shutil

root = Path('F:/Ourgame')
archive = root/'过程图稿与视频/2026-10-15_猎弩四甲双向射击装填实际换装运行_v003'
original = archive/'原件'
snapshot = root/'source-assets/production/backups/2026-10-15_asyncNative-UE83-GREEN-v044'
index = json.loads((archive/'index.json').read_text(encoding='utf-8-sig'))
for source, name in [
    (snapshot/'compiled-source-manifest.json', 'compiled-source-manifest-v044.json'),
    (root/'tools/scripts/verify-content-combat.ps1', 'capture-script-used.ps1'),
    (root/'tools/scripts/verify-native-capture-pixels.py', 'native-pixel-verifier-used.py'),
]:
    destination = original/name
    assert not destination.exists(), destination
    if name == 'capture-script-used.ps1':
        assert hashlib.sha256(source.read_bytes()).hexdigest().upper() == index['capture_script_sha256']
    shutil.copy2(source, destination)
    assert source.read_bytes() == destination.read_bytes()
rows = [json.loads(line) for line in (original/'native-frame-pixels.jsonl').read_text(encoding='utf-8-sig').splitlines() if line]
movie = [row for row in rows if row['file'].startswith('MovieFrame')]
counts = collections.Counter(row['file'] for row in movie)
duplicates = {name: count for name, count in counts.items() if count > 1}
actual = list(original.glob('MovieFrame*.png'))
report = json.loads((original/'runtime-report.json').read_text(encoding='utf-8-sig'))
assert len(movie) == 1853 and len(actual) == 1842 and sum(n-1 for n in duplicates.values()) == 11
assert index['runtime_checks_passed'] is True and index['required_check_count'] == 29
diagnosis = dict(
    status='failed_capture_preserved; gameplay29passed does not validate missing images',
    source_snapshot=str(snapshot),
    movie_receipts=len(movie), actual_movie_files=len(actual), overwritten_frame_count=11,
    duplicated_requested_names=duplicates,
    native_pixel_verification_passed=False,
    reason='Strict unique-name assertion rejects before per-PNG CRC verification; overwritten frames cannot be recovered.',
    root_cause_source='G:/UE_5.5/Engine/Source/Runtime/Core/Private/Misc/FileHelper.cpp:697 GenerateNextBitmapFilename checks FileExists, so an asynchronously pending filename remains available.',
    next_action='Reserve the exact engine-requested filename exclusively before enqueue, keep strict uniqueness/count/CRC/timing gates and recapture.',
    no_runtime_visual_or_audio_acceptance=True,
)
(original/'capture-duplicate-name-diagnosis.json').write_text(json.dumps(diagnosis, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
index['capture_diagnosis'] = diagnosis
(archive/'index.json').write_text(json.dumps(index, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
progress_path = root/'docs/production/first-batch-v2/progress.json'
progress = json.loads(progress_path.read_text(encoding='utf-8-sig'))
progress['async_capture_pipeline']['status'] = 'v003 gameplay29/29 passed but strict capture rejected duplicate filenames1853receipts1842files; reservation repair pending'
progress['async_capture_pipeline']['actual29_verified'] = False
progress['xbw_four_armor_runtime']['status'] = 'v003 gameplay29/29 passed, capture naming collision rejected; native complete evidence pending'
progress['xbw_four_armor_runtime']['attempts'].append(dict(version='v003', archive=str(archive.relative_to(root)), whole_passed=False,
    gameplay_passed=True, required=29, executed=29, passed=29, movie_receipts=1853, movie_files=1842,
    overwritten_frames=11, native_PNGs_CRC_verified=0, audio_sync_passed=False,
    failure='native receipt duplicate filenames; strict verifier rejected before CRC', E_batch='pending'))
progress_path.write_text(json.dumps(progress, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
print(json.dumps(diagnosis, ensure_ascii=False))
