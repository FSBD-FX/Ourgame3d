"""EV039/040/041 host-native batch bookkeeping and media retention; no generation."""
from pathlib import Path
import argparse
import datetime
import hashlib
import json
import shutil

ROOT = Path(__file__).resolve().parent
LEDGER = Path('F:/Ourgame/source-assets/production/first-unit-animation-v003/generation-ledger.json')
ARCHIVES = [Path('F:/Ourgame/过程图稿与视频/2026-10-15_首批独立武器组件_v001'),
            Path('E:/OurGame/Knight/过程图稿与视频/2026-10-15_首批独立武器组件_v001')]


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def read(path):
    return json.loads(Path(path).read_text('utf-8-sig'))


def write(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def archive(source, relative, status):
    relative = Path(relative)
    if relative.is_absolute() or '..' in relative.parts:
        raise ValueError('Unsafe archive relative path')
    digest = sha(source)
    outputs = []
    for folder in ARCHIVES:
        for category in ['原件', '展示副本']:
            destination = folder/category/relative
            if destination.exists():
                if sha(destination) != digest:
                    raise ValueError(f'Will not overwrite {destination}')
            else:
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, destination)
            assert sha(destination) == digest
            outputs.append(str(destination))
        index_path = folder/'index.json'
        index = read(index_path) if index_path.exists() else {
            'schema': 'production-media-retention-v1', 'topic': folder.name,
            'source_batch': str(ROOT), 'status': 'work_in_progress_not_runtime_accepted', 'files': []}
        if not any(x['relative'] == relative.as_posix() for x in index['files']):
            index['files'].append({'source': str(source), 'relative': relative.as_posix(),
                                   'sha256': digest, 'bytes': source.stat().st_size,
                                   'status': status, 'archived_utc': now()})
        write(index_path, index)
    return outputs


def main():
    p = argparse.ArgumentParser()
    p.add_argument('operation', choices=['register', 'complete', 'review', 'archive', 'fail'])
    p.add_argument('--number', type=int)
    p.add_argument('--asset')
    p.add_argument('--prompt-file', type=Path)
    p.add_argument('--references', nargs='*', default=[])
    p.add_argument('--source', type=Path)
    p.add_argument('--relative')
    p.add_argument('--status')
    p.add_argument('--notes')
    a = p.parse_args()
    ledger_path = LEDGER
    ledger = read(ledger_path)
    if a.operation == 'register':
        window = ledger.get('current_window')
        used = window['requested_count'] if window else ledger['requested_count']
        limit = window['request_limit'] if window else ledger['batch_request_limit']
        if used >= limit:
            raise ValueError('Batch exhausted; review this batch before a follow-on batch')
        if window:
            assert window['status'].startswith('active')
        assert ledger['single_visual_writer'] == '/root/assets_prepare'
        number = ledger['requested_count']+1
        prompt = a.prompt_file.read_text('utf-8')
        record = {'request_number': number, 'asset': a.asset, 'status': 'requested',
                  'source_directory': str(ROOT), 'window_number': window['number'] if window else 1,
                  'requested_utc': now(), 'prompt_path': str(a.prompt_file), 'prompt': prompt,
                  'references': [{'path': str(Path(f)), 'sha256': sha(Path(f))} for f in a.references],
                  'transparent_background': False, 'backend': 'image_gen.imagegen', 'host_fee_usd': None}
        ledger['requests'].append(record);ledger['requested_count'] = number
        if window:
            assert number == window['first_request_number'] + used
            window['requested_count'] += 1
            ledger['batch_requested_count'] = window['requested_count']
            ledger['remaining_batch_requests'] = limit-window['requested_count']
            ledger['lifetime_requested_count'] = ledger['lifetime_prior_EV038_requests']+number
        else:
            ledger['remaining_batch_requests'] = limit-number
        write(ledger_path, ledger)
        print(json.dumps({'registered_request': number, 'remaining': ledger['remaining_batch_requests']}))
        return
    if a.operation == 'archive':
        print(json.dumps({'paths': archive(a.source, a.relative, a.status or 'derived_pending_review'), 'sha256': sha(a.source)}, ensure_ascii=False))
        return
    entry = next(e for e in ledger['requests'] if e['request_number'] == a.number)
    if a.operation == 'complete':
        from PIL import Image
        target = ROOT/'raw'/f'{a.number:02d}-{entry["asset"]}-v001.png'
        if target.exists():
            raise ValueError(f'Will not overwrite {target}')
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(a.source, target)
        copies = archive(target, Path('raw')/target.name, 'generated_pending_visual_review')
        with Image.open(target) as im:
            size, mode = list(im.size), im.mode
        entry.update(status='generated_dual_archived_pending_review', completed_utc=now(),
                     tool_original_path=str(a.source), raw_path=str(target), sha256=sha(target),
                     image_size=size, mode=mode, archive_paths=copies)
    else:
        entry.update(status=a.status or ('generation_failed' if a.operation == 'fail' else 'reviewed'),
                     review_notes=a.notes, reviewed_utc=now())
    write(ledger_path, ledger)
    for folder in ARCHIVES:
        write(folder/'generation-ledger-snapshot.json', ledger)
    print(json.dumps({k: entry[k] for k in ['request_number', 'status', 'raw_path'] if k in entry}, ensure_ascii=False))


if __name__ == '__main__':
    main()
