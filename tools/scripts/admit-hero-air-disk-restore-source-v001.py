"""Root-only reviewed v144 source admission; byte-exact overlays, no UE launch."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import shutil

R = Path('F:/Ourgame')
C = R / 'source-assets/production/fairytale-hero-air-v001/air-disk-restore-candidate-v001'
O = R / 'docs/production/first-batch-v2/evidence/HeroAirDiskRestore-v144-v001/Root-source-admission-v001'

def need(value, message):
    if not value:
        raise ValueError(message)

def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))

def pin(path, relative=False):
    path = Path(path).resolve()
    data = path.read_bytes()
    return dict(path=path.relative_to(R).as_posix() if relative else path.as_posix(),
                bytes=len(data), sha256=hashlib.sha256(data).hexdigest())

def check(row):
    path = Path(row['path'])
    if not path.is_absolute():
        path = R / path
    actual = pin(path)
    need((actual['bytes'], actual['sha256']) == (row['bytes'], row['sha256']),
         'Pinned file drift: ' + str(path))
    return path

def inventory(folder):
    return {p.relative_to(R).as_posix() for p in folder.rglob('*') if p.is_file()}

freeze = C / 'HeroAirDiskRestore-source-freeze-v001.json'
index_path = C / 'Root-admit-index-v001.json'
review = R / '.superpowers/sdd/2026-10-19-hero-air-disk-restore-v144/task-1-source-review-v001.md'
need(pin(freeze)['sha256'] == '9df684be66301d86ede42996e46809829a6e3a1844139732f287b87a1c8cc8c6', 'Unreviewed freeze')
need(pin(index_path)['sha256'] == '9f6dec922347fd09c5a9efb8d5528d84658ef6d036427aa71589364e0e9df70f', 'Unreviewed admit index')
need(pin(review)['sha256'] == '4480f49f54c3c29c3ae8bcddfdd6fc5e21aa5f88c9ee5de51e31431c013ad352', 'Fresh approved review drift')
need('Approved for this bounded source review. Critical: 0. Important: 0.' in review.read_text(encoding='utf-8'), 'Review not approved')
index = read(index_path)
need(check(index['source_freeze_pin']) == freeze.resolve(), 'Freeze linkage differs')
cm = check(index['before_compiled_manifest_pin'])
need(pin(cm)['sha256'] == '5ddd83f5a16919c084870a29705ee1c0da3fbd13dec7f480330d8e61a4ac95ee', 'Wrong compiled predecessor')
compiled = read(cm)
need(compiled['passed'] == 203 and compiled['failed'] == 0, 'Predecessor not full203 GREEN')
before = inventory(R / 'UnrealGame/Source')
production = inventory(R / 'UnrealGame/Content/Production')
need(before == {x['path'] for x in compiled['files'] if x['path'].startswith('UnrealGame/Source/')}, 'Source membership drift')
need(production == {x['path'] for x in compiled['files'] if x['path'].startswith('UnrealGame/Content/Production/')}, 'Production membership drift')
need(len(before) == compiled['source_files'] == index['before_Source_count'], 'Source count drift')
need(len(production) == compiled['production_files'] == index['Production_count'], 'Production count drift')
for _ in range(2):
    for row in read(freeze)['members']:
        check(row)
    for row in compiled['files']:
        check(row)

pending = []
for row in index['new_source_mappings']:
    destination = Path(row['destination']).resolve()
    need(destination.is_relative_to((R / 'UnrealGame/Source').resolve()), 'New destination outside Source')
    need(row['must_be_absent_before_Root_admission'] is True and not destination.exists(), 'New source occupied')
    source = check(row['candidate_pin'])
    need(source == Path(row['candidate']).resolve(), 'Candidate linkage differs')
    pending.append((destination, source.read_bytes(), False))
for row in index['existing_source_overlay']:
    destination = check(row['before'])
    need(destination == Path(row['destination']).resolve(), 'Overlay linkage differs')
    need(destination.is_relative_to((R / 'UnrealGame/Source').resolve()), 'Overlay outside Source')
    data = destination.read_bytes()
    for edit in row['edits']:
        needle = edit['needle'].encode('utf-8')
        need(data.count(needle) == edit['expected_occurrences'] == 1, 'Overlay seam not unique')
        data = data.replace(needle, edit['replacement'].encode('utf-8'), 1)
    need((len(data), hashlib.sha256(data).hexdigest()) == (row['after_bytes'], row['after_sha256']), 'Overlay after bytes differ')
    pending.append((destination, data, True))
need(len({p for p, _, _ in pending}) == len(pending) == 4, 'Admission scope differs')
new_paths = {p.relative_to(R).as_posix() for p, _, existed in pending if not existed}
need(len(before | new_paths) == index['derived_Source_count'], 'Derived Source count differs')
need(not O.exists(), 'Preserve prior admission')
O.mkdir(parents=True)
(O / 'before').mkdir()
(O / 'after-preview').mkdir()
for path, data, existed in pending:
    if existed:
        shutil.copy2(path, O / 'before' / path.name)
    with (O / 'after-preview' / path.name).open('xb') as stream:
        stream.write(data)
for path, data, existed in pending:
    if existed:
        path.write_bytes(data)
    else:
        with path.open('xb') as stream:
            stream.write(data)
after = inventory(R / 'UnrealGame/Source')
need(after == before | new_paths, 'Unexpected Source membership after admission')
changed = {p.relative_to(R).as_posix() for p, _, _ in pending}
for _ in range(2):
    for row in compiled['files']:
        if row['path'] not in changed:
            check(row)
    for path, data, _ in pending:
        need(path.read_bytes() == data, 'Admitted bytes drift')
    need(inventory(R / 'UnrealGame/Content/Production') == production, 'Production membership changed')
result = dict(schema='Root-hero-air-disk-restore-source-admission-v001',
              utc=datetime.now(timezone.utc).isoformat(), RootApproved=True, is_template=False,
              actual_applied=True, source_candidate_freeze=pin(freeze), source_admit_index=pin(index_path),
              predecessor_compiled_manifest=pin(cm), fresh_source_review=pin(review),
              actual_source_files=len(after), actual_production_files=len(production), new_source_files=len(new_paths),
              after_files=[pin(p, True) for p, _, _ in pending], verification_passes=2,
              unrelated_source_tests_content_byte_mismatches=0, UE_compiled=False, FinalAccepted=False)
out = O / 'actual-source-admission.json'
with out.open('x', encoding='utf-8') as stream:
    json.dump(result, stream, ensure_ascii=False, indent=2)
print(json.dumps(pin(out), ensure_ascii=False))
