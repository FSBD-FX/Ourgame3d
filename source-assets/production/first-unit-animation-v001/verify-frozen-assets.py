"""Repeatable read-only validation of actual frozen source pixels and markers."""
from pathlib import Path
import hashlib
import json
from PIL import Image

ROOT=Path(__file__).resolve().parent

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    manifest=json.loads((ROOT/'import-subset-v002.json').read_text(encoding='utf-8'))
    markers=json.loads((ROOT/'assembly-markers-v002.json').read_text(encoding='utf-8'))
    ledger=json.loads((ROOT/'generation-ledger.json').read_text(encoding='utf-8'))
    frames={f['sha256']:f for action in manifest['actions'] for f in action['frames']}
    assert len(frames)==122 and len(manifest['actions'])==22
    for expected,frame in frames.items():
        path=Path(frame['path'])
        assert sha(path)==expected,str(path)
        with Image.open(path) as image:
            image.load()
            assert image.format=='PNG' and image.mode=='RGBA' and image.size==(512,512)
            assert image.getchannel('A').getextrema()==(0,255)
            assert all(image.getpixel(p)[3]==0 for p in [(0,0),(511,0),(0,511),(511,511)])
        assert len(frame['root_px'])==2
    count=0
    for action in markers['actions']:
        for frame in action['frames']:
            assert frame['sha256'] in frames and sha(Path(frame['path']))==frame['sha256']
            with Image.open(frame['path']) as image:
                assert image.getpixel(tuple(frame['grip_px']))[3]>=128
            count+=1
    assert count==68
    assert ledger['requested_count']==24 and ledger['remaining_total_authorization']==0
    for request in ledger['requests']:
        for key in ['tool_original_path','source_path','archive_original_path','presentation_path']:
            assert sha(Path(request[key]))==request['sha256']
    print(json.dumps({'status':'source_checks_passed_runtime_not_asserted',
        'unique_frames':122,'logical_actions':22,'hand_markers':68,'generation_calls':24,
        'generation_calls_remaining':0,'external_api_calls':0,'runtime_verified_by_this_script':False}))

if __name__=='__main__':main()
