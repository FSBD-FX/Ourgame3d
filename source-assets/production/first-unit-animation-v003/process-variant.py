"""Deterministic skill-processor invocation and archival; never creates raw art."""
from pathlib import Path
import argparse
import importlib.util
import json
import subprocess
import sys
from PIL import Image

P = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('record', P/'production-record.py')
record = importlib.util.module_from_spec(spec)
spec.loader.exec_module(record)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--number', type=int, required=True)
    ap.add_argument('--profile', required=True)
    ap.add_argument('--slug', required=True)
    ap.add_argument('--mode', default='attack')
    ap.add_argument('--cols', type=int, default=3)
    a = ap.parse_args()
    entry = next(e for e in record.read(P/'generation-ledger.json')['requests'] if e['request_number'] == a.number)
    out = P/'processed'/a.slug
    if out.exists():
        raise ValueError('Will not overwrite a prior processed version')
    command = [sys.executable, '-X', 'utf8', '-B',
        'C:/Users/22499/.codex/skills/generate2dsprite/scripts/generate2dsprite.py', 'process',
        '--input', entry['raw_path'], '--target', 'player', '--mode', a.mode,
        '--rows', '2', '--cols', str(a.cols), '--output-dir', str(out),
        '--scale-profile', str(P/'profiles'/a.profile), '--threshold', '180',
        '--edge-threshold', '260', '--strict-qc', '--max-profile-scale-drift', '.08', '--duration', '100',
        '--prompt-file', entry['prompt_path']]
    result = subprocess.run(command, capture_output=True, text=True, encoding='utf-8')
    log = P/'reviews'/f'{a.slug}-processor-log.txt'
    log.write_text('COMMAND '+json.dumps(command)+'\nEXIT '+str(result.returncode)+'\nSTDOUT\n'+result.stdout+'\nSTDERR\n'+result.stderr, encoding='utf-8')
    record.archive(log, Path('reviews')/log.name, 'real_processor_execution_log')
    if not out.exists():
        raise RuntimeError(result.stderr or result.stdout)
    for f in sorted(out.iterdir()):
        if f.is_file():
            record.archive(f, Path('processed')/out.name/f.name, 'static_candidate_needs_manual_visual_and_assembly_review')
    pixels = []
    for f in sorted(out.glob(a.mode+'-*.png')):
        with Image.open(f) as im:
            rgba = im.convert('RGBA')
            alpha = rgba.getchannel('A')
            corners = [rgba.getpixel(x)[3] for x in [(0,0),(511,0),(0,511),(511,511)]]
            opaque = [p for p in rgba.getdata() if p[3] >= 128]
            bad = sum(r > 180 and b > 150 and g < 120 for r,g,b,_ in opaque)
            pixels.append({'path':str(f),'sha256':record.sha(f),'canvas':list(im.size),
                'mode':im.mode,'alpha_extrema':list(alpha.getextrema()),'corner_alpha':corners,
                'opaque_magenta_fraction':bad/max(1,len(opaque))})
    meta = record.read(out/'pipeline-meta.json')
    report = {'request_number':a.number,'processor_exit_code':result.returncode,
        'qc_summary':meta.get('qc_summary'), 'frames':pixels,
        'pixel_pass':len(pixels)==2*a.cols and all(x['canvas']==[512,512] and x['mode']=='RGBA'
            and x['alpha_extrema']==[0,255] and x['corner_alpha']==[0,0,0,0]
            and x['opaque_magenta_fraction']<.001 for x in pixels),
        'visual_acceptance':False,'runtime_acceptance':False,'armor_representation':'whole_dressed_body_atlas_variant'}
    report_path = P/'reviews'/f'{a.slug}-pixel-qc.json'
    record.write(report_path,report)
    record.archive(report_path,Path('reviews')/report_path.name,'real_png_pixel_qc_not_visual_acceptance')
    print(json.dumps({k:report[k] for k in ['request_number','processor_exit_code','pixel_pass','qc_summary']}))
    return result.returncode

if __name__ == '__main__':
    raise SystemExit(main())
