"""Air48 immutable input/receipt contracts. Importing this module performs no IO.

Host source decoding is separate from Unreal's embedded Python: the latter must
bind an exact host validation receipt and rehash every input, not pretend Pillow
was run inside UE. A host receipt never proves native object metadata by itself.
"""
from pathlib import Path
import hashlib
import json
import re
import stat
import zipfile

ROOT = Path('F:/Ourgame')
E_ROOT = Path('E:/OurGame/Knight/过程图稿与视频')
NAMESPACE = '/Game/Production/ArtTrials/EV048/v020/HeroLeatherAir6'
COMPONENTS = ('BodyRest', 'NearArmWithoutHand', 'HelmetForeground', 'NearHand',
              'FarHandForeground', 'ShoulderFar', 'Chest', 'ShoulderNear')
BODY_COMPONENTS = frozenset(COMPONENTS[:5])
LAYER_ORDER = ('BodyRest', 'ShoulderFar', 'Chest', 'NearArmWithoutHand',
               'ShoulderNear', 'HelmetForeground', 'FarHandForeground', 'NearHand')
SWORD_OBJECT = '/Game/Production/FirstBatch/v002/CandidateComponents/T_military_sword_v002.T_military_sword_v002'
BASELINE_SHA256 = '4f55684c044c1b5fde8edf0a1b7f378d22e16e9a87b7407ee878c6552e2fb85d'
OLD_COUNT, NEW_COUNT, FINAL_COUNT = 1371, 48, 1419
HASH_RE = re.compile(r'[0-9a-f]{64}\Z')
PRODUCTION_PREFIX = 'UnrealGame/Content/Production/'
SCOPE_FALSE = ('runtime_verified', 'native_draw_verified', 'TrialAllowed', 'FinalAccepted')


def need(value, reason):
    if not value:
        raise ValueError(reason)


def integer(value):
    return type(value) is int


def hash256(value):
    return isinstance(value, str) and HASH_RE.fullmatch(value) is not None


def _unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        need(key not in result, 'Duplicate JSON key: ' + key)
        result[key] = value
    return result


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'),
                      object_pairs_hook=_unique_pairs,
                      parse_constant=lambda x: (_ for _ in ()).throw(ValueError('Nonfinite JSON: ' + x)))


def canonical_bytes(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'),
                      ensure_ascii=False, allow_nan=False).encode('utf-8')


def safe_member(value):
    need(isinstance(value, str) and value and '\\' not in value and ':' not in value,
         'Unsafe ZIP member')
    need(not value.startswith('/') and all(p not in ('', '.', '..') for p in value.split('/')),
         'ZIP traversal/alias rejected')
    need(all(ord(c) >= 32 for c in value), 'ZIP member has control character')
    return value


def resolve(value, root=ROOT, within=None):
    """Reject traversal/ADS/reparse aliases before accepting canonical paths."""
    need(isinstance(value, (str, Path)), 'Path must be text')
    raw = str(value)
    need(raw and all(ord(c) >= 32 for c in raw) and not any(c in raw for c in '*?\"<>|'),
         'Poisoned path')
    p = Path(raw)
    need(not raw.startswith(('\\\\', '//')), 'UNC path rejected')
    need(not p.drive or p.is_absolute(), 'Drive-relative Windows path rejected')
    need(all(part not in ('.', '..') for part in raw.replace('\\', '/').split('/')), 'Dot path alias rejected')
    for part in p.parts:
        if part == p.anchor:
            continue
        need(part not in ('.', '..') and not part.endswith((' ', '.')) and ':' not in part,
             'Traversal/ADS/trailing-dot path rejected')
        need(re.fullmatch(r'(?i)(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])(?:\..*)?', part) is None,
             'Reserved Windows path rejected')
    p = p if p.is_absolute() else Path(root) / p
    # A junction can resolve inside a scope too; reject it rather than bless an alias.
    for ancestor in [p, *p.parents]:
        try:
            info = ancestor.lstat()
        except FileNotFoundError:
            continue
        attrs = getattr(info, 'st_file_attributes', 0)
        need(not stat.S_ISLNK(info.st_mode) and not (attrs & getattr(stat, 'FILE_ATTRIBUTE_REPARSE_POINT', 1024)),
             'Symlink/junction path rejected: ' + str(ancestor))
    p = p.resolve()
    if within is not None:
        need(p.is_relative_to(Path(within).resolve()), 'Path escapes required scope: ' + str(p))
    return p


def _pin_resolved(p):
    h = hashlib.sha256()
    size = 0
    with p.open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            size += len(block)
            h.update(block)
    return dict(path=p.as_posix(), bytes=size, sha256=h.hexdigest())


def pin(path):
    return _pin_resolved(resolve(path))


def check(value, root=ROOT, within=None):
    need(isinstance(value, dict) and set(value) == {'path', 'bytes', 'sha256'}, 'Exact file pin required')
    need(integer(value['bytes']) and value['bytes'] >= 0 and hash256(value['sha256']), 'Invalid file pin')
    p = resolve(value['path'], root, within)
    actual = _pin_resolved(p)
    need((actual['bytes'], actual['sha256']) == (value['bytes'], value['sha256']), 'File pin changed: ' + str(p))
    return p


def write_new(path, value):
    """Exclusive create; preserve any partial output on IO failure, never retry."""
    p = resolve(path)
    data = (json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n').encode('utf-8')
    with p.open('xb') as f:
        written = f.write(data)
        need(written == len(data), 'Short JSON write; retained partial file')
        f.flush()
        import os
        os.fsync(f.fileno())
    return pin(p)


def identity(component, frame):
    need(component in COMPONENTS and integer(frame) and 0 <= frame < 6, 'Invalid component/phase')
    name = f'T_Fairytale_Air_{component}_{frame:03d}_v001'
    package = NAMESPACE + '/' + name
    return name, package, package + '.' + name


def saved_path(package, root=ROOT):
    need(package.startswith(NAMESPACE + '/'), 'Package outside new namespace')
    return resolve(Path(root) / 'UnrealGame/Content' / (package[6:] + '.uasset'), root,
                   Path(root) / 'UnrealGame/Content/Production')


def validate_layout(m, root=ROOT):
    need(m['schema'] == 'Root-Air48-native-import-v001', 'Wrong import schema')
    need(tuple(m[k] for k in ('expected_old_count', 'expected_new_count', 'expected_final_count'))
         == (OLD_COUNT, NEW_COUNT, FINAL_COUNT), 'Exact1371+48=1419 required')
    need(all(integer(m[k]) for k in ('expected_old_count', 'expected_new_count', 'expected_final_count')),
         'Integer counts required')
    need(m['namespace'] == NAMESPACE and m['replace_existing'] is False, 'Exact unused namespace/no replacement required')
    assets = m['assets']
    need(isinstance(assets, list) and len(assets) == NEW_COUNT, 'Exactly48 assets required')
    need({(x['component'], x['frame']) for x in assets} == {(c, f) for c in COMPONENTS for f in range(6)},
         'Exact eight components times six phases required')
    need(len({x['object_path'] for x in assets}) == NEW_COUNT and len({x['saved_path'] for x in assets}) == NEW_COUNT,
         'Duplicate object or saved package')
    need(len({x['source']['path'] for x in assets}) == NEW_COUNT, 'Duplicate source path')
    for x in assets:
        name, package, obj = identity(x['component'], x['frame'])
        need((x['name'], x['package_path'], x['object_path'], x['destination_path']) == (name, package, obj, NAMESPACE),
             'Destination identity changed')
        need(resolve(x['saved_path'], root) == saved_path(package, root), 'Saved package path substituted')
        source = resolve(x['source']['path'], root, Path(root) / 'source-assets/production')
        need(source.name == name + '.png' and source.parent.name == 'sources48', 'Exact native source filename required')
        need(hash256(x['source_RGBA_sha256']) and x['known_optional_empty'] is False, 'Nonempty source contract required')


def decode_png(path, row):
    from PIL import Image
    with Image.open(path) as im:
        need(im.format == 'PNG' and im.mode == 'RGBA' and im.size == (512, 512), 'Actual PNG RGBA512 required')
        im.load()
        rgba = im.tobytes()
        alpha = im.getchannel('A')
        histogram = alpha.histogram()
        actual = dict(source_RGBA_sha256=hashlib.sha256(rgba).hexdigest(), source_mode='RGBA',
                      source_canvas=[512, 512], source_alpha_nonzero_pixels=sum(histogram[1:]),
                      source_alpha128_pixels=sum(histogram[128:]), source_alpha255_pixels=histogram[255],
                      source_alpha_bbox=list(alpha.getbbox()) if alpha.getbbox() else None)
    need(actual['source_alpha_nonzero_pixels'] > 0, 'Empty source alpha rejected')
    need(all(row[k] == v for k, v in actual.items()), 'Decoded RGBA/alpha facts differ: ' + str(path))
    return actual


def verify_e_retention(retentions, root=ROOT, e_root=E_ROOT):
    """Verify real v002 ZIP indexes and every original F source/member twice."""
    groups = {}
    for source_pin, retention, expected_suffix in retentions:
        need(retention['current_twoSHA_byte_equal'] is True and retention.get('individual_E_PNG_path') is None,
             'Retention cannot substitute a loose E PNG or an unchecked claim')
        index_path = check(retention['E_index'], root, e_root)
        packet_path = check(retention['E_packet'], root, index_path.parent)
        member = safe_member(retention['E_member'])
        need(member.startswith('原件/') and member.endswith(expected_suffix), 'Retained component/phase member substituted')
        need((retention['E_member_bytes'], retention['E_member_sha256']) == (source_pin['bytes'], source_pin['sha256']),
             'Retained member differs from source')
        key = index_path.as_posix()
        group = groups.setdefault(key, (index_path, packet_path, []))
        need(group[1] == packet_path, 'One retention index has different packets')
        group[2].append((source_pin, retention))
    for index_path, packet_path, wanted in groups.values():
        index = read(index_path)
        need(index['schema'] == 'native-media-exact-original-zip-retention-v001'
             and index['retainer_version'] == 'v002' and index['compression_level'] == 1,
             'Actual v002 ZIP retention index required')
        need(index['verification_passes'] == 2 and index['source_and_member_hash_mismatches'] == 0
             and index['source_deleted'] is False and index['reencoded_originals'] is False,
             'E index facts changed')
        need(index['packet'] == pin(packet_path), 'E index packet pin differs')
        archive = resolve(index['source_archive'], root, Path(root) / '过程图稿与视频')
        rows = index['files']
        need(len(rows) == index['file_count'] and rows, 'E index count mismatch')
        names = [safe_member(r['member']) for r in rows]
        need(len(set(names)) == len(names), 'Duplicate E index ZIP member')
        need(sum(r['bytes'] for r in rows) == index['source_bytes'], 'E index byte total mismatch')
        indexed = {r['member']: r for r in rows}
        with zipfile.ZipFile(packet_path) as z:
            infos = z.infolist()
            need(len(infos) == len(rows) and {i.filename for i in infos} == set(names), 'Exact ZIP membership differs')
            for info in infos:
                need(not info.is_dir() and not info.flag_bits & 1 and ((info.external_attr >> 16) & 0o170000) != 0o120000,
                     'Directory/encrypted/symlink ZIP entry rejected')
                need(info.file_size == indexed[info.filename]['bytes'], 'ZIP declared size differs')
            for repeat in range(2):
                for row in rows:
                    source = resolve(row['source'], root, archive)
                    need(source == archive / Path(row['member']), 'E indexed F source path/member alias')
                    source_pin = {k: row[k] for k in ('bytes', 'sha256')}
                    source_pin['path'] = row['source']
                    check(source_pin, root, archive)
                    data = z.read(row['member'])  # Also performs ZIP CRC validation.
                    need(len(data) == row['bytes'] and hashlib.sha256(data).hexdigest() == row['sha256'],
                         'Actual ZIP member bytes differ')
                    need(data == source.read_bytes(), 'Actual F original and ZIP member differ')
                for source_pin, retention in wanted:
                    row = indexed.get(retention['E_member'])
                    need(row is not None and (row['bytes'], row['sha256']) == (source_pin['bytes'], source_pin['sha256']),
                         'Source absent from actual E packet')
                    need(z.read(retention['E_member']) == check(source_pin, root).read_bytes(),
                         'Native-ready source and actual E member differ')


def verify_freeze(freeze_pin, manifest_path, root=ROOT):
    freeze_path = check(freeze_pin, root, Path(root) / 'source-assets/production')
    candidate = manifest_path.parent
    need(freeze_path.parent == candidate, 'Freeze belongs to another candidate')
    frozen = read(freeze_path)
    need(frozen['schema'] == 'Air48-native-ready-freeze-v001' and frozen['two_SHA_verification_passes'] == 2
         and frozen['mismatches'] == 0 and frozen['native_imports'] == 0 and frozen['FinalAccepted'] is False,
         'Native-ready freeze facts changed')
    members = frozen['members']
    need(len(members) == frozen['member_count'] and members, 'Freeze count mismatch')
    paths = [resolve(v['path'], root, candidate) for v in members]
    need(len(set(paths)) == len(paths) and manifest_path in paths and freeze_path not in paths, 'Freeze membership alias')
    actual = set()
    for p in candidate.rglob('*'):
        checked = resolve(p, root, candidate)
        if p.is_file():
            actual.add(checked)
    need(actual == set(paths) | {freeze_path}, 'Candidate has unlisted/absent frozen files')
    for repeat in range(2):
        for v in members:
            check(v, root, candidate)
    return frozen


def load_prepared(manifest_pin, freeze_pin, root=ROOT, e_root=E_ROOT, decode_rgba=True):
    manifest_path = check(manifest_pin, root, Path(root) / 'source-assets/production')
    m = read(manifest_path)
    frozen = verify_freeze(freeze_pin, manifest_path, root)
    need(m['schema'] == 'frozen-Air48-scoped-native-import-prepared-v001'
         and m['asset_count'] == NEW_COUNT and m['unique_mandatory_texture_total'] == 49,
         'Exact source48/new plus existing sword49 required')
    need(m['namespace'] == NAMESPACE and m['native_imported'] is False and m['GPU_ready'] is False
         and m['FinalAccepted'] is False, 'Source preparation scope changed')
    closure_pin = m['source_closure']
    need(m.get('source_closure_descriptor', closure_pin) == closure_pin, 'Closure aliases differ')
    closure_path = check(closure_pin, root, manifest_path.parent)
    closure = read(closure_path)
    need(closure_path.read_bytes() == canonical_bytes(closure), 'Source closure is not exact canonical UTF8 JSON')
    need(closure_pin['sha256'] == m['source_closure_digest'] == frozen['source_closure_digest'], 'Closure digest mismatch')
    need(closure['assets48'] == m['assets'] and closure['existing_sword49'] == m['existing_sword']
         and closure['namespace'] == NAMESPACE and closure['ProfileId'] == m['profile_id'], 'Descriptor source identity differs')
    assets, retentions = [], []
    need(len(m['assets']) == NEW_COUNT, 'Prepared source count differs')
    for row in m['assets']:
        name, package, obj = identity(row['component'], row['frame'])
        source = dict(path=row['source'], bytes=row['source_bytes'], sha256=row['source_sha256'])
        path = check(source, root, manifest_path.parent / 'sources48')
        need(path == manifest_path.parent / 'sources48' / (name + '.png'), 'Prepared source path/name substituted')
        need((row['name'], row['package_path'], row['object_path'], row['source_filename']) == (name, package, obj, name + '.png'),
             'Prepared identity changed')
        need(row['expected_object_class'] == 'Texture2D' and row['known_optional_empty'] is False
             and row['empty_reason'] is None and row['source_mode'] == 'RGBA' and row['source_canvas'] == [512, 512],
             'Prepared Texture2D512 nonempty contract changed')
        need(integer(row['source_alpha_nonzero_pixels']) and 0 < row['source_alpha_nonzero_pixels'] <= 512 * 512
             and hash256(row['source_RGBA_sha256']), 'Invalid alpha/RGBA source fact')
        if decode_rgba:
            decode_png(path, row)
        folder = 'body-layers' if row['component'] in BODY_COMPONENTS else 'armor-layers'
        retentions.append((source, row['retention'], f'/{folder}/{row["component"]}/frame-{row["frame"]}.png'))
        assets.append(dict(component=row['component'], frame=row['frame'], name=name, source=source,
                           source_RGBA_sha256=row['source_RGBA_sha256'], known_optional_empty=False,
                           destination_path=NAMESPACE, package_path=package, object_path=obj,
                           saved_path=saved_path(package, root).as_posix(), retention=row['retention']))
    sword = m['existing_sword']
    need(sword['object_path'] == SWORD_OBJECT and sword['import_new'] is False and sword['reuses_existing_object'] is True,
         'Existing independent sword must not be reimported')
    sword_path = check(sword['source'], root, manifest_path.parent / 'existing-sword-source49')
    if decode_rgba:
        decode_png(sword_path, sword)
    retentions.append((sword['source'], sword['retention'], '/source-copied/military-sword-clean-v001.png'))
    verify_e_retention(retentions, root, e_root)
    validate_layout(dict(schema='Root-Air48-native-import-v001', namespace=NAMESPACE, replace_existing=False,
                         expected_old_count=OLD_COUNT, expected_new_count=NEW_COUNT, expected_final_count=FINAL_COUNT,
                         assets=assets), root)
    return m, assets


def baseline(snapshot_pin, root=ROOT):
    path = check(snapshot_pin, root, Path(root) / 'source-assets/production/backups')
    need(snapshot_pin['sha256'] == BASELINE_SHA256, 'Wrong authoritative Source292/Production1371 baseline')
    snap = read(path)
    need((snap['source_files'], snap['production_files'], snap['registered_tests'], snap['passed'], snap['failed'], snap['notRun'])
         == (292, OLD_COUNT, 203, 200, 3, 0), 'Baseline counts changed')
    need(snap['old200_all_green'] is True and snap['three_unique_expected_TARGET_RED'] is True,
         'Baseline semantic proof changed')
    old = [v for v in snap['files'] if v['path'].startswith(PRODUCTION_PREFIX)]
    need(len(old) == OLD_COUNT and len({v['path'] for v in old}) == OLD_COUNT, 'Exact1371 old Production pins required')
    return old


def verify_old(old, root=ROOT):
    need(len(old) == OLD_COUNT and len({v['path'] for v in old}) == OLD_COUNT, 'Exact1371 old Production pins required')
    for value in old:
        need(value['path'].startswith(PRODUCTION_PREFIX), 'Old package path outside Production')
        check(value, root, Path(root) / 'UnrealGame/Content/Production')


def exact_membership(m, after, root=ROOT):
    expected = {resolve(v['path'], root) for v in m['old_production_files']}
    if after:
        expected |= {resolve(v['saved_path'], root) for v in m['assets']}
    actual = set()
    for p in (Path(root) / 'UnrealGame/Content/Production').rglob('*'):
        checked = resolve(p, root, Path(root) / 'UnrealGame/Content/Production')
        if p.is_file():
            actual.add(checked)
    need(actual == expected and len(actual) == (FINAL_COUNT if after else OLD_COUNT),
         'Exact Production membership differs from1371' + ('+48' if after else ''))


def validate_approval(approval, manifest_pin, freeze_pin, closure, root=ROOT):
    need(approval['schema'] == 'Root-Air48-limited-source-import-approval-v001' and approval['RootApproved'] is True
         and approval['limited_import_approved'] is True and approval['is_template'] is False, 'Explicit Root approval missing')
    need(approval['source_manifest'] == manifest_pin and approval['candidate_freeze'] == freeze_pin
         and approval['source_closure_digest'] == closure and approval['namespace'] == NAMESPACE,
         'Root approval binds different immutable inputs')
    need(tuple(approval[k] for k in ('expected_old_count', 'expected_new_count', 'expected_final_count'))
         == (OLD_COUNT, NEW_COUNT, FINAL_COUNT), 'Approval count mismatch')
    need(approval['TrialAllowed'] is False and approval['FinalAccepted'] is False, 'Import approval cannot grant runtime/art acceptance')


def verify_approval_retention(approval, prepared, manifest_pin, freeze_pin, root=ROOT, e_root=E_ROOT):
    """If Root supplied the source-package E index, verify that real ZIP too.

    E599 proves each original fit layer. E600 additionally binds the exact NEW
    sources48 copies, manifest, freeze, canonical descriptor and typed data.
    """
    if 'E600_actual_retention' not in approval:
        return  # Synthetic host fixtures need no invented E600 record.
    index_pin = approval['E600_actual_retention']
    index_path = check(index_pin, root, e_root)
    index = read(index_path)
    base = Path(manifest_pin['path']).parent
    required = [manifest_pin, freeze_pin, prepared['source_closure']]
    if 'typed_data' in approval:
        check(approval['typed_data'], root, base)
        required.append(approval['typed_data'])
    required.extend(dict(path=r['source'], bytes=r['source_bytes'], sha256=r['source_sha256']) for r in prepared['assets'])
    required.append(prepared['existing_sword']['source'])
    prefix = '原件/四十八源四十九纹理准备完整包/'
    retentions = []
    for source_pin in required:
        source = check(source_pin, root, base)
        member = prefix + source.relative_to(base).as_posix()
        retention = dict(E_index=index_pin, E_packet=index['packet'], E_member=member,
                         E_member_bytes=source_pin['bytes'], E_member_sha256=source_pin['sha256'],
                         current_twoSHA_byte_equal=True, individual_E_PNG_path=None)
        retentions.append((source_pin, retention, '/' + source.relative_to(base).as_posix()))
    verify_e_retention(retentions, root, e_root)


def validate_receipt_assets(m, receipt, root=ROOT):
    validate_layout(m, root)
    actual = receipt['assets']
    need(len(actual) == NEW_COUNT, 'Receipt requires48 actual saved textures')
    indexed = {(a['component'], a['frame']): a for a in actual}
    need(len(indexed) == NEW_COUNT, 'Duplicate native receipt identity')
    expected = {(a['component'], a['frame']): a for a in m['assets']}
    need(set(indexed) == set(expected), 'Native receipt component/phase mismatch')
    enums = dict(compression_settings=('TextureCompressionSettings', 'TC_EDITOR_ICON'),
                 mip_gen_settings=('TextureMipGenSettings', 'TMGS_NO_MIPMAPS'),
                 lod_group=('TextureGroup', 'TEXTUREGROUP_UI'), filter=('TextureFilter', 'TF_BILINEAR'))
    for key, row in expected.items():
        a = indexed[key]
        need(a['source'] == row['source'] and a['actual_object_path'] == row['object_path'], 'Receipt provenance/object substituted')
        need(a['actual_class'] == 'Texture2D' and a['actual_dimensions'] == [512, 512], 'Actual Texture2D512 required')
        filenames = a['actual_import_filenames']
        need(len(filenames) == 1 and resolve(filenames[0], root) == resolve(row['source']['path'], root), 'Actual import filename differs')
        need(resolve(a['saved']['path'], root) == resolve(row['saved_path'], root)
             and integer(a['saved']['bytes']) and a['saved']['bytes'] > 0 and hash256(a['saved']['sha256']), 'Invalid saved package receipt pin')
        settings = a['actual_settings']
        need(set(settings) == set(enums) | {'never_stream', 'srgb'}, 'Missing/extra texture setting')
        need(settings['never_stream'] is True and settings['srgb'] is True, 'UI neverstream/sRGB differs')
        for field, (enum, member) in enums.items():
            need(isinstance(settings[field], str) and re.fullmatch(r'<' + enum + r'\.' + member + r': [0-9]+>', settings[field]),
                 'Native texture setting differs: ' + field)


def load_import(path, root=ROOT, e_root=E_ROOT, decode_rgba=True):
    path = resolve(path, root, Path(root) / 'source-assets/production')
    m = read(path)
    validate_layout(m, root)
    prepared, assets = load_prepared(m['source_manifest'], m['candidate_freeze'], root, e_root, decode_rgba)
    need(m['assets'] == assets and m['source_closure_digest'] == prepared['source_closure_digest'], 'Import manifest source closure differs')
    approval = read(check(m['Root_source_approval'], root, root))
    validate_approval(approval, m['source_manifest'], m['candidate_freeze'], m['source_closure_digest'], root)
    if 'old_compiled_snapshot' in approval:
        need(approval['old_compiled_snapshot'] == m['old_compiled_snapshot'], 'Approval baseline pin differs')
    verify_approval_retention(approval, prepared, m['source_manifest'], m['candidate_freeze'], root, e_root)
    need(m['old_production_files'] == baseline(m['old_compiled_snapshot'], root), 'Old membership changed from authoritative baseline')
    need(all(m[k] is False for k in SCOPE_FALSE), 'Import manifest exceeds limited scope')
    host = read(check(m['host_source_validation'], root, path.parent))
    need(host['schema'] == 'Air48-host-source-validation-v001' and host['success'] is True
         and host['source_manifest'] == m['source_manifest'] and host['candidate_freeze'] == m['candidate_freeze']
         and host['Root_source_approval'] == m['Root_source_approval'] and host['source_closure_digest'] == m['source_closure_digest']
         and host['source48_RGBA512_decoded'] is True and host['existing_sword_source_RGBA512_decoded'] is True
         and host['actual_E_ZIPmember_twoSHA_verified'] is True and host['UE_started'] is False,
         'Exact host source decode/ZIP validation receipt required')
    need(host['contract'] == pin(__file__)
         and host['preparer'] == pin(Path(__file__).with_name('prepare-Air48-Root-import-v001.py')),
         'Host source validation binds different contract/preparer')
    need(all(host[k] is False for k in SCOPE_FALSE), 'Host validation receipt scope changed')
    return m
