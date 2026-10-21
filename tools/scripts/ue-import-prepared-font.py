"""Import the pinned, unmodified Noto Sans CJK SC Regular into UE 5.5.

Inside the already-open Editor: py "F:/Ourgame/tools/scripts/ue-import-prepared-font.py"
Ordinary Python --preflight validates source bytes/cmap only; it cannot import UE assets.
No network access, level edits, Editor launch, or existing-asset replacement occurs.

Epic 5.5 references: FontFileImportFactory, AssetImportTask, Font, CompositeFont,
StructBase.import_text; native serialized fields verified in CompositeFont.h.
"""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import struct
import sys
import traceback

ROOT = Path(__file__).resolve().parents[2]
SOURCE_DIR = ROOT / 'source-assets/third-party/fonts/noto-sans-cjk-sc/2026-10-10-v1'
FONT_FILE = SOURCE_DIR / 'NotoSansCJKsc-Regular.otf'
EXPECTED_SHA256 = '2c76254f6fc379fddfce0a7e84fb5385bb135d3e399294f6eeb6680d0365b74b'
LICENSE_SHA256 = '6a73f9541c2de74158c0e7cf6b0a58ef774f5a780bf191f2d7ec9cc53efe2bf2'
DESTINATION = '/Game/ThirdParty/Fonts/NotoSansCJKsc'
FACE_NAME = 'FF_NotoSansCJKsc_Regular'
FONT_NAME = 'F_NotoSansCJKsc_Regular'
PROBE_TEXT = '简体中文测试生命金币背包攻击防御开始继续退出设置音量失落城堡0123456789，。！？：%+-'


def preflight():
    data = FONT_FILE.read_bytes()
    digest = hashlib.sha256(data).hexdigest()
    if digest != EXPECTED_SHA256:
        raise RuntimeError('Font SHA256 differs from the pinned source manifest')
    license_file = SOURCE_DIR / 'LICENSE'
    if hashlib.sha256(license_file.read_bytes()).hexdigest() != LICENSE_SHA256:
        raise RuntimeError('Font license SHA256 differs from the pinned source manifest')
    if data[:4] != b'OTTO':
        raise RuntimeError('Expected a single OpenType CFF font')
    count = struct.unpack_from('>H', data, 4)[0]
    tables = {}
    for index in range(count):
        tag, checksum, offset, length = struct.unpack_from('>4sIII', data, 12 + index * 16)
        if offset + length > len(data):
            raise RuntimeError('Font table exceeds file bounds')
        tables[tag.decode('ascii')] = (offset, length)
    name_offset = tables['name'][0]
    name_count, storage_offset = struct.unpack_from('>HH', data, name_offset + 2)
    names = {}
    for index in range(name_count):
        platform, encoding, language, name_id, length, offset = struct.unpack_from(
            '>HHHHHH', data, name_offset + 6 + index * 12)
        if name_id not in (0, 1, 2, 5, 13, 14) or platform not in (0, 3):
            continue
        begin = name_offset + storage_offset + offset
        value = data[begin:begin + length].decode('utf-16-be')
        names.setdefault(str(name_id), [])
        if value not in names[str(name_id)]:
            names[str(name_id)].append(value)
    cmap_offset = tables['cmap'][0]
    cmap_count = struct.unpack_from('>H', data, cmap_offset + 2)[0]
    groups = []
    for index in range(cmap_count):
        platform, encoding, offset = struct.unpack_from('>HHI', data, cmap_offset + 4 + index * 8)
        begin = cmap_offset + offset
        fmt = struct.unpack_from('>H', data, begin)[0]
        if fmt == 12 and (platform == 0 or (platform == 3 and encoding == 10)):
            group_count = struct.unpack_from('>I', data, begin + 12)[0]
            groups = [struct.unpack_from('>III', data, begin + 16 + row * 12)
                      for row in range(group_count)]
            break
    if not groups:
        raise RuntimeError('Expected Unicode cmap format 12 in this pinned font')
    missing = []
    for char in sorted(set(PROBE_TEXT)):
        point = ord(char)
        if not any(start <= point <= end and glyph + point - start != 0
                   for start, end, glyph in groups):
            missing.append(char)
    if missing:
        raise RuntimeError('Probe characters missing from source cmap: ' + ''.join(missing))
    return {
        'source_file': str(FONT_FILE), 'bytes': len(data), 'sha256': digest,
        'sfnt_signature': 'OTTO', 'font_names_by_name_id': names,
        'glyph_count': struct.unpack_from('>H', data, tables['maxp'][0] + 4)[0],
        'unicode_cmap_format': 12, 'unicode_mapped_codepoints': sum(end - start + 1 for start, end, _ in groups),
        'probe_text': PROBE_TEXT, 'probe_missing_characters': missing,
        'scope': 'Source structure and selected glyph coverage; no UE rendering or localization proof',
    }


def import_font():
    import unreal
    report = {'checked_at_utc': datetime.now(timezone.utc).isoformat(),
              'engine_version': unreal.SystemLibrary.get_engine_version(),
              'source': preflight(), 'success': False, 'assets': []}
    output = Path(unreal.Paths.project_saved_dir()) / 'Bootstrap/font-import-report.json'
    try:
        tools = unreal.AssetToolsHelpers.get_asset_tools()
        face_path = DESTINATION + '/' + FACE_NAME
        face = unreal.load_asset(face_path)
        if face is None:
            task = unreal.AssetImportTask()
            task.set_editor_property('filename', str(FONT_FILE))
            task.set_editor_property('destination_path', DESTINATION)
            task.set_editor_property('destination_name', FACE_NAME)
            task.set_editor_property('automated', True)
            task.set_editor_property('replace_existing', False)
            task.set_editor_property('save', True)
            task.set_editor_property('factory', unreal.FontFileImportFactory())
            tools.import_asset_tasks([task])
            face = unreal.load_asset(face_path)
            report['imported_object_paths'] = list(task.get_editor_property('imported_object_paths'))
        if face is None or not isinstance(face, unreal.FontFace):
            raise RuntimeError('The import did not produce the expected FontFace asset')
        report['assets'].append({'path': face.get_path_name(), 'class': face.get_class().get_name(),
                                 'source_filename': face.get_editor_property('source_filename')})
        font_path = DESTINATION + '/' + FONT_NAME
        font = unreal.load_asset(font_path)
        if font is None:
            font = tools.create_asset(FONT_NAME, DESTINATION, unreal.Font, unreal.FontFactory())
            if font is None:
                raise RuntimeError('FontFactory did not create a Font asset')
            composite = font.get_editor_property('composite_font')
            serialized = '(DefaultTypeface=(Fonts=((Name="Regular",Font=(FontFaceAsset=FontFace\'' + face.get_path_name() + '\')))))'
            if not composite.import_text(serialized):
                raise RuntimeError('CompositeFont did not accept the serialized Regular face reference')
            font.set_editor_property('font_cache_type', unreal.FontCacheType.RUNTIME)
            font.set_editor_property('composite_font', composite)
            unreal.EditorAssetLibrary.save_loaded_asset(font, False)
        composite_text = font.get_editor_property('composite_font').export_text()
        if face.get_path_name() not in composite_text:
            raise RuntimeError('Font composite does not reference the prepared FontFace; existing asset preserved')
        report['assets'].append({'path': font.get_path_name(), 'class': font.get_class().get_name(),
                                 'font_cache_type': str(font.get_editor_property('font_cache_type')),
                                 'composite_font': composite_text})
        report['success'] = True
        report['rendering_tested'] = False
        unreal.log('Prepared Noto CJK FontFace and runtime Font saved: ' + font_path)
    except Exception:
        report['error'] = traceback.format_exc()
        unreal.log_error(report['error'])
    finally:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    if not report['success']:
        raise RuntimeError('Font import incomplete; see ' + str(output))


if __name__ == '__main__':
    if '--preflight' in sys.argv:
        print(json.dumps(preflight(), ensure_ascii=False, indent=2))
    else:
        import_font()
