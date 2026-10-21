"""Local EV038 bookkeeping only. Does not generate or edit artwork."""
from pathlib import Path
import argparse
import datetime
import hashlib
import json
import shutil

ROOT = Path(__file__).resolve().parent
ARCHIVE = ROOT.parents[2] / '过程图稿与视频' / '2026-10-14_首单元动作生产_v001'

def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()

def read(path):
    return json.loads(path.read_text(encoding='utf-8'))

def write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def archive_file(source, relative):
    paths = [ARCHIVE / '原件' / relative, ARCHIVE / '展示副本' / relative]
    for target in paths:
        if target.exists():
            if sha(target) != sha(source):
                raise ValueError(f'Cannot overwrite archived version: {target}')
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
    return paths

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('operation', choices=['register', 'complete', 'review', 'archive'])
    parser.add_argument('--number', type=int)
    parser.add_argument('--asset')
    parser.add_argument('--prompt-file', type=Path)
    parser.add_argument('--references', nargs='*', default=[])
    parser.add_argument('--source', type=Path)
    parser.add_argument('--relative')
    parser.add_argument('--status')
    parser.add_argument('--notes')
    args = parser.parse_args()
    ledger_path = ROOT / 'generation-ledger.json'
    ledger = read(ledger_path)
    if args.operation == 'register':
        number = ledger['requested_count'] + 1
        if number > 24 or number > ledger['current_subtask_request_limit']:
            raise ValueError('Authorized call limit reached')
        entry = dict(request_number=number, asset=args.asset, status='requested',
                     requested_utc=now(), prompt=args.prompt_file.read_text(encoding='utf-8'),
                     prompt_path=str(args.prompt_file), reference_paths=args.references,
                     transparent_background=False, backend='image_gen.imagegen', host_fee_usd=None)
        ledger['requests'].append(entry)
        ledger['requested_count'] = number
        ledger['remaining_total_authorization'] = 24 - number
        write(ledger_path, ledger)
        print(json.dumps({'registered_request': number}))
        return
    if args.operation == 'archive':
        targets = archive_file(args.source, Path(args.relative))
        index_path = ARCHIVE / 'index.json'
        index = read(index_path)
        index.setdefault('derived_outputs', []).append({'source': str(args.source),
            'original': str(targets[0]), 'presentation': str(targets[1]),
            'sha256': sha(args.source), 'status': args.status or 'derived_pending_review'})
        write(index_path, index)
        print(json.dumps({'original': str(targets[0]), 'presentation': str(targets[1]), 'sha256': sha(args.source)}))
        return
    entry = next(e for e in ledger['requests'] if e['request_number'] == args.number)
    if args.operation == 'complete':
        from PIL import Image
        name = f'{args.number:02d}-{entry["asset"]}-v001.png'
        target = ROOT / 'raw' / name
        if target.exists():
            raise ValueError(f'Refusing to overwrite {target}')
        shutil.copy2(args.source, target)
        original, presentation = archive_file(target, name)
        entry.update(status='generated_pending_visual_review', completed_utc=now(),
                     tool_original_path=str(args.source), source_path=str(target),
                     archive_original_path=str(original), presentation_path=str(presentation),
                     sha256=sha(target), image_size=list(Image.open(target).size))
    else:
        entry.update(status=args.status, visual_review_notes=args.notes, reviewed_utc=now())
    write(ledger_path, ledger)
    index_path = ARCHIVE / 'index.json'
    index = read(index_path)
    index['status'] = 'in_progress'
    index['outputs'] = ledger['requests']
    write(index_path, index)
    print(json.dumps({k: entry[k] for k in ('request_number', 'status', 'source_path') if k in entry}))

if __name__ == '__main__':
    main()
