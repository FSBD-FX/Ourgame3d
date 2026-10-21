"""Close a filled accounting window; use existing EV040/041 follow-on authority."""
from pathlib import Path
import datetime
import hashlib
import json
import shutil

root = Path('F:/Ourgame').resolve()
base = root / 'source-assets/production/first-unit-animation-v003'
ledger_path = base / 'generation-ledger.json'
out = base / 'reviews/window009-accounting-close-v001'
assert not out.exists()
out.mkdir(parents=True)


def fact(path):
    path = Path(path).resolve()
    data = path.read_bytes()
    return {'path': path.as_posix(), 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}


def write(path, value):
    assert not path.exists()
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


ledger = json.loads(ledger_path.read_text(encoding='utf-8-sig'))
assert ledger['current_window']['number'] == 9 and ledger['current_window']['requested_count'] == 24
assert ledger['requested_count'] == 216 and ledger['remaining_batch_requests'] == 0
assert ledger['automatic_follow_on_batches_authorized'] and ledger['external_api_calls'] == 0
frozen = base / 'generation-ledger-window009-frozen.json'
assert not frozen.exists()
shutil.copy2(ledger_path, frozen)
rows = [row for row in ledger['requests'] if 193 <= row['request_number'] <= 216]
assert len(rows) == 24 and all(row['status'] != 'requested_pending' for row in rows)
for repeat in range(2):
    for row in rows:
        assert fact(row['canonical_raw']['path']) == row['canonical_raw']
review = {
    'schema': 'window009-filled-accounting-close-v001',
    'utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'authorization_events': ['EV-040', 'EV-041'],
    'frozen_ledger': fact(frozen), 'requests': 24, 'retained_source_hash_passes': 2,
    'source_hash_mismatches': 0, 'external_api_calls': 0, 'host_fee_usd': None,
    'source_QC_not_all_complete': True, 'runtime_acceptance_not_implied': True,
    'formal_complete_units': 0,
    'rows': [{'number': row['request_number'], 'status': row['status'],
              'root_source_review': row.get('root_source_review'), 'raw': row['canonical_raw']} for row in rows],
    'next_work': 'Retain and review full Guard action rows; new window is accounting only, not approval of unresolved pixels.',
}
review_path = out / 'review.json'
write(review_path, review)
closed = dict(ledger['current_window'], status='accounting_filled_all_outputs_retained_source_QC_runtime_pending', frozen_ledger=frozen.as_posix(), frozen_ledger_sha256=fact(frozen)['sha256'], review_path=review_path.as_posix(), review_sha256=fact(review_path)['sha256'])
ledger['completed_windows'].append(closed)
ledger['current_window'] = {'number': 10, 'first_request_number': 217, 'last_request_number': 240, 'request_limit': 24, 'requested_count': 0, 'status': 'auto_authorized_active'}
ledger['accounting_window_id'] = 'window010'
ledger['batch_requested_count'] = 0
ledger['remaining_batch_requests'] = 24
ledger_path.write_text(json.dumps(ledger, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
write(out / 'after-open-window010-ledger.json', ledger)
progress_path = root / 'docs/production/first-batch-v2/progress.json'
shutil.copy2(progress_path, out / 'before-progress.json')
progress = json.loads(progress_path.read_text(encoding='utf-8-sig'))
progress['generation_accounting_current'] = {'requested_count': 216, 'current_window': 10, 'window_requested': 0, 'window_remaining': 24, 'lifetime_requested_count': 240, 'external_api_calls': 0, 'host_fee_usd': None, 'authorization_events': ['EV-040', 'EV-041']}
progress['generation'].update({'current_window': ledger['current_window'], 'current_window_remaining': 24, 'EV039_and_later_requested': 216, 'production_generation_requested_excluding_initial_references': 240, 'total_host_image_requests_including_initial3_references': 243})
progress['next_native_request'] = 217
progress['next_media_retention_batch'] = 379
progress['next_retention_batch'] = 379
progress['updated_utc'] = review['utc']
progress_path.write_text(json.dumps(progress, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
write(out / 'state-change-receipt.json', {'ledger_after': fact(ledger_path), 'progress_after': fact(progress_path), 'review': fact(review_path), 'formal_complete_units': 0})
print(json.dumps({'current_window': ledger['current_window'], 'next_request': 217, 'lifetime_requested': 240, 'external_api_calls': 0, 'review': fact(review_path)}, ensure_ascii=False))
