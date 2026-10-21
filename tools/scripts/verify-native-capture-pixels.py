"""Verify opt-in proof PNGs against CRCs of UE's actual viewport BGRA8 buffers."""
from pathlib import Path
import argparse
import json
import zlib
import numpy as np
from PIL import Image

parser=argparse.ArgumentParser()
parser.add_argument('--archive',required=True)
parser.add_argument('--write-receipt',action='store_true')
args=parser.parse_args()
archive=Path(args.archive).resolve()
original=archive/'原件'
metadata=json.loads((original/'native-lossless-capture.json').read_text(encoding='utf-8-sig'))
assert metadata['mode']=='native_viewport_BGRA8_lossless_PNG_zlib0'
assert all(metadata[k] is False for k in ['pixel_mutations','simulation_pacing_changed','audio_changed'])
rows=[json.loads(line) for line in (original/'native-frame-pixels.jsonl').read_text(encoding='utf-8-sig').splitlines() if line]
names=[r['file'] for r in rows]
assert len(names)==len(set(names)) and 'prewarm-viewport.png' in names
actual={p.name for p in original.glob('MovieFrame*.png')}|{'prewarm-viewport.png'}
assert set(names)==actual and len(rows)>1, 'Native receipt must cover every original PNG exactly once'
for row in rows:
    assert row['saved'] is True
    assert Path(row['file']).name==row['file'] and row['file'].endswith('.png')
    with Image.open(original/row['file']) as im:
        assert im.format=='PNG' and im.size==(row['width'],row['height'])==(1280,720)
        rgba=np.asarray(im.convert('RGBA'))
        assert np.all(rgba[:,:,3]==255)
        crc=zlib.crc32(rgba[:,:,[2,1,0,3]].tobytes())&0xffffffff
        assert crc==row['native_BGRA8_crc32'], f'Viewport pixels changed: {row["file"]}'
async_verified=False
async_summary=None
if metadata.get('async_movie_writer_requested') is True:
    assert metadata.get('async_movie_writer_active') is True and metadata.get('prewarm_synchronous') is True
    assert metadata.get('movie_filename_reservation')=='Windows_CreateFileW_CREATE_NEW_exact_engine_request_before_enqueue'
    async_summary=json.loads((original/'native-async-write-summary.json').read_text(encoding='utf-8-sig'))
    assert all(async_summary[k] is True for k in ('requested','active','closed','flushed','success'))
    movie=[r for r in rows if r['file'].startswith('MovieFrame')]
    count=len(movie)
    assert count>0 and [r['file'] for r in movie]==sorted(r['file'] for r in movie)
    assert [r['writer_sequence'] for r in movie]==list(range(1,count+1)), 'Serial writer sequence lost or reordered a frame'
    assert all(async_summary[k]==count for k in ('movie_reserved','movie_enqueued','movie_saved','movie_completed','receipts_saved'))
    assert all(async_summary[k]==0 for k in ('movie_reservation_failed','movie_failed','rejected','pending'))
    report=json.loads((original/'runtime-report.json').read_text(encoding='utf-8-sig'))
    assert report['native_async_capture_requested'] is True and report['native_async_capture_writes_flushed'] is True
    assert report['native_async_flush_after_audio_stop'] is True
    timing=report['capture_timing'];offsets=timing['frame_wall_offsets_s']
    assert len(offsets)==count, 'Every capture event must retain its original PNG'
    for row,offset in zip(movie,offsets):
        assert row['async_writer'] is True and row['copy_crc_matches'] is True
        assert row['filename_reserved'] is True and row['filename_reservation_mode']=='Windows_CreateFileW_CREATE_NEW'
        assert row['copied_BGRA8_crc32']==row['native_BGRA8_crc32']
        capture=row['capture_callback_monotonic_s'];reserved=row['reservation_completed_monotonic_s'];queued=row['enqueued_monotonic_s']
        started=row['save_started_monotonic_s'];completed=row['save_completed_monotonic_s']
        assert 0<capture<=reserved<=queued<=started<=completed
        assert capture<=timing['capture_start_monotonic_s']+offset+1e-6, 'Write completion must not replace capture-event time'
        assert abs(row['save_wall_s']-(completed-started))<1e-6
    prewarm=next(r for r in rows if r['file']=='prewarm-viewport.png')
    assert prewarm.get('async_writer',False) is False, 'Prewarm retains the synchronous completion contract'
    assert async_summary['last_save_completed_monotonic_s']<=async_summary['flush_completed_monotonic_s']
    assert abs(async_summary['first_capture_callback_monotonic_s']-movie[0]['capture_callback_monotonic_s'])<1e-6
    assert abs(async_summary['last_capture_callback_monotonic_s']-movie[-1]['capture_callback_monotonic_s'])<1e-6
    async_verified=True
result=dict(passed=True,mode=metadata['mode'],verified_original_PNG_count=len(rows),
            every_source_viewport_pixel_crc_matches=True,maximum_PNG_save_wall_s=max(r['save_wall_s'] for r in rows),
            native_async_writer_verified=async_verified, native_async_writer_summary=async_summary,
            scope='Lossless native viewport pixel equality only; gameplay, motion, audio and sync require separate actual checks.')
if args.write_receipt:
    output=original/'native-pixel-verification.json'
    assert not output.exists(),'Never overwrite prior verification'
    output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result,ensure_ascii=False))
