"""Exact original pure functions; no historical source wrapper import."""
from pathlib import Path
import json, math, zlib, sys
import numpy as np
from PIL import Image
C=sys.modules[__name__]

def need(value, why):
    if not value:
        raise ValueError(why)


def read(path):
    def pairs(items):
        result = {}
        for k, v in items:
            need(k not in result, 'Duplicate JSON key')
            result[k] = v
        return result
    return json.loads(Path(path).read_text(encoding='utf-8-sig'), object_pairs_hook=pairs,
                      parse_constant=lambda x: (_ for _ in ()).throw(ValueError('Nonfinite JSON')))


def finite(x):
    return type(x) in (int, float) and math.isfinite(x)


def near(a, b, tol=1e-4):
    return finite(a) and finite(b) and abs(a - b) <= tol


def file_under(directory, relative):
    need(isinstance(relative, str) and relative and '\\' not in relative and ':' not in relative
         and not relative.startswith('/') and all(x not in ('', '.', '..') for x in relative.split('/')), 'Evidence file path traversal')
    p = directory / Path(relative)
    need(p.resolve().is_relative_to(directory.resolve()) and not p.is_symlink(), 'Evidence path alias')
    for a in p.parents:
        if a == directory.parent:
            break
        need(not a.is_symlink(), 'Evidence parent alias')
    return p


def project(slot, source):
    x, y = slot['top']; w, h = slot['size']; u, v = slot['uv']; du, dv = slot['uv_size']
    px, py = slot['rotation_pivot']; qx = (source[0] / 512 - u) / du * w - px * w
    qy = (source[1] / 512 - v) / dv * h - py * h
    a = math.radians(slot['rotation']); co, si = math.cos(a), math.sin(a)
    return [x + px * w + co * qx - si * qy, y + py * h + si * qx + co * qy]


def verify_png_fifo(original, r):
    metadata = C.read(original / 'native-lossless-capture.json')
    C.need(metadata['mode'] == 'native_viewport_BGRA8_lossless_PNG_zlib0'
           and all(metadata[k] is False for k in ('pixel_mutations', 'simulation_pacing_changed', 'audio_changed')),
           'Native original capture metadata differs')
    C.need(metadata['async_movie_writer_requested'] is True and metadata['async_movie_writer_active'] is True
           and metadata['prewarm_synchronous'] is True
           and metadata['movie_filename_reservation'] == 'Windows_CreateFileW_CREATE_NEW_exact_engine_request_before_enqueue', 'Actual exclusive async writer required')
    rows = [json.loads(line) for line in (original / 'native-frame-pixels.jsonl').read_text(encoding='utf-8-sig').splitlines() if line]
    names = [x['file'] for x in rows]; movie = [x for x in rows if x['file'].startswith('MovieFrame')]
    C.need(len(set(names)) == len(names) and set(names) == {p.name for p in original.glob('MovieFrame*.png')} | {'prewarm-viewport.png'}, 'Exact original PNG membership/unique FIFO differs')
    C.need(len(movie) == len(r['observations']) > 1 and [x['file'] for x in movie] == sorted(x['file'] for x in movie)
           and [x['writer_sequence'] for x in movie] == list(range(1, len(movie) + 1)), 'Actual one PNG per callback serial FIFO differs')
    timing = r['capture_timing']; start = timing['capture_start_monotonic_s']; stop = timing['capture_stop_monotonic_s']
    for row in rows:
        C.need(Path(row['file']).name == row['file'] and row['saved'] is True, 'Actual preserved PNG receipt required')
        with Image.open(C.file_under(original, row['file'])) as im:
            C.need(im.format == 'PNG' and im.size == (1280, 720) == (row['width'], row['height']), 'Original native1280x720 PNG required')
            rgba = np.asarray(im.convert('RGBA'))
        C.need(np.all(rgba[..., 3] == 255) and zlib.crc32(rgba[..., [2, 1, 0, 3]].tobytes()) & 0xffffffff == row['native_BGRA8_crc32'], 'Original native PNG viewport CRC mismatch')
    for row, offset in zip(movie, timing['frame_wall_offsets_s']):
        C.need(row['async_writer'] is True and row['copy_crc_matches'] is True and row['filename_reserved'] is True
               and row['filename_reservation_mode'] == 'Windows_CreateFileW_CREATE_NEW'
               and row['copied_BGRA8_crc32'] == row['native_BGRA8_crc32'], 'Actual native original copy/reservation receipt differs')
        values = [row[k] for k in ('capture_callback_monotonic_s', 'reservation_completed_monotonic_s', 'enqueued_monotonic_s', 'save_started_monotonic_s', 'save_completed_monotonic_s')]
        C.need(all(C.finite(x) for x in values) and 0 < start <= values[0] <= stop
               and values[0] <= values[1] <= values[2] <= values[3] <= values[4]
               and values[0] <= start + offset + 1e-6 and C.near(row['save_wall_s'], values[4] - values[3], 1e-6), 'Actual async original capture/reserve/enqueue/save timing differs')
    prewarm = next(x for x in rows if x['file'] == 'prewarm-viewport.png')
    C.need(prewarm.get('async_writer', False) is False, 'Prewarm must remain synchronous')
    summary = C.read(original / 'native-async-write-summary.json'); count = len(movie)
    C.need(all(summary[k] is True for k in ('requested', 'active', 'closed', 'flushed', 'success'))
           and all(summary[k] == count for k in ('movie_reserved', 'movie_enqueued', 'movie_saved', 'movie_completed', 'receipts_saved'))
           and all(summary[k] == 0 for k in ('movie_reservation_failed', 'movie_failed', 'rejected', 'pending')), 'Actual async final writer counts differ')
    C.need(r['native_async_capture_writes_flushed'] is True
           and summary['flush_completed_monotonic_s'] >= stop >= start + timing['frame_wall_offsets_s'][-1]
           and summary['last_save_completed_monotonic_s'] <= summary['flush_completed_monotonic_s']
           and C.near(summary['first_capture_callback_monotonic_s'], movie[0]['capture_callback_monotonic_s'], 1e-6)
           and C.near(summary['last_capture_callback_monotonic_s'], movie[-1]['capture_callback_monotonic_s'], 1e-6), 'Final actual callback/audio Stop must precede completed PNG flush')
    return movie


def fixed_optical_gate(error, opaque, blade):
    bc, sc = int(np.count_nonzero(opaque)), int(np.count_nonzero(blade))
    C.need(bc >= 150 and sc >= 8, 'Fixed original source-pixel body/blade minimum count failed')
    bm, bg = float(np.median(error[opaque])), float(np.mean(error[opaque] <= 55))
    sm, sg = float(np.median(error[blade])), float(np.mean(error[blade] <= 65))
    C.need(all(C.finite(x) for x in (bm, bg, sm, sg)) and bm <= 40 and bg >= .60 and sm <= 50 and sg >= .60,
           'Fixed source-pixel registration error gate failed; never search/relax after failure')
    return bc, sc, bm, bg, sm, sg


