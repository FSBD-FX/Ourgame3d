"""Freeze only this NEW candidate, with exact membership and two SHA/size passes."""
import argparse
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
FREEZE = HERE / 'HeroLocomotionAudio-Candidate-freeze-v001.json'
INDEX = HERE / 'HeroLocomotionAudio-Candidate-index-v001.json'


def pin(path):
    data = path.read_bytes()
    return {'relative_path': path.relative_to(HERE).as_posix(), 'bytes': len(data),
            'sha256': hashlib.sha256(data).hexdigest()}


def write_new(path, obj):
    assert path.resolve().is_relative_to(HERE)
    with path.open('xb') as handle:
        handle.write((json.dumps(obj, ensure_ascii=False, indent=2) + '\n').encode('utf-8'))


def members():
    return sorted((p for p in HERE.rglob('*') if p.is_file() and p not in (FREEZE, INDEX)),
                  key=lambda p: p.relative_to(HERE).as_posix())


def check(freeze):
    actual = [pin(p) for p in members()]
    assert actual == freeze['files'], 'Exact membership or SHA/size mismatch'
    for row in freeze['files']:
        assert pin(HERE / row['relative_path']) == row, 'Second SHA/size pass mismatch'
    return len(actual)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--verify-only', action='store_true')
    args = parser.parse_args()
    if args.verify_only:
        freeze = json.loads(FREEZE.read_text('utf-8'))
        count = check(freeze)
        index = json.loads(INDEX.read_text('utf-8'))
        assert index['freeze'] == pin(FREEZE)
        assert index['manifest'] == pin(HERE / 'manifest.json')
        print(json.dumps({'pass': True, 'members': count, 'two_SHA_size_mismatch': 0,
                          'freeze': pin(FREEZE), 'index': pin(INDEX)}, ensure_ascii=False))
        return
    assert not FREEZE.exists() and not INDEX.exists(), 'Frozen versions are immutable'
    verified = json.loads((HERE / 'standalone-verification-v001.json').read_text('utf-8'))
    assert verified['pass'] is True and verified['complete_decode_count'] == 6
    assert verified['manifest']['sha256'] == pin(HERE / 'manifest.json')['sha256']
    assert all(v is False for v in verified['acceptance'].values())
    rows = [pin(p) for p in members()]
    freeze = {
        'schema': 'HeroLocomotionAudioCandidateFreeze-v001',
        'status': 'LOCAL_CANDIDATE_FROZEN_NOT_AUDITIONED_NOT_ADMITTED',
        'ownership': 'Only NEW hero-locomotion-audio-candidate-v001; no actual game/tool/ledger/media/E writes',
        'file_count': len(rows), 'member_total_bytes': sum(row['bytes'] for row in rows),
        'files': rows, 'all_acceptance_remains_false': verified['acceptance'],
        'immutable_version': True,
    }
    check(freeze)
    write_new(FREEZE, freeze)
    write_new(INDEX, {
        'schema': 'HeroLocomotionAudioCandidateIndex-v001', 'freeze': pin(FREEZE),
        'manifest': pin(HERE / 'manifest.json'),
        'source_plan': pin(HERE / '音色与来源计划-v001.md'),
        'report': pin(HERE / '交接报告-v001.md'),
        'standalone_verification': pin(HERE / 'standalone-verification-v001.json'),
        'assets': [pin(p) for p in sorted((HERE / 'wav').glob('*.wav'))],
        'two_SHA_size_mismatch': 0, 'exact_membership': True,
        'Root_F_E_retention_completed': False, 'Root_approval': False,
        'auditioned': False, 'UE_imported': False, 'event_bound': False,
        'formal_unit_complete': False,
    })
    check(freeze)
    print(json.dumps({'pass': True, 'members': len(rows), 'two_SHA_size_mismatch': 0,
                      'freeze': pin(FREEZE), 'index': pin(INDEX)}, ensure_ascii=False))


if __name__ == '__main__':
    main()
