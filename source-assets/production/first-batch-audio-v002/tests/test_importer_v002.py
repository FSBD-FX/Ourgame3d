"""Ordinary-Python contract probes; no Unreal import or device playback."""
from pathlib import Path
import copy
import io
import importlib.util
import json
import math
import struct
import tempfile
import unittest
import wave

ROOT = Path(__file__).resolve().parents[4]
SCRIPT = ROOT / 'tools/scripts/ue-import-first-batch-audio-v002.py'
spec = importlib.util.spec_from_file_location('audio_v002_contract', SCRIPT)
job = importlib.util.module_from_spec(spec)
spec.loader.exec_module(job)


class DedicatedAudioContract(unittest.TestCase):
    def test_preflight_has_five_real_dedicated_wavs(self):
        result = job.preflight()
        self.assertEqual(len(result['assets']), 5)

    def test_preflight_captures_existing_seventeen_packages(self):
        self.assertEqual(len(job.preflight()['old17']), 17)

    def test_valid_real_pcm_profile(self):
        meta = job.inspect_pcm16_wav(self.fixture())
        self.assertEqual(meta['frames'], 4800)
        self.assertTrue(-6 <= meta['sample_peak_dbfs'] <= -3)

    @staticmethod
    def fixture(rate=48000, channels=1, width=2, frames=4800, peak=19518):
        b=io.BytesIO()
        with wave.open(b,'wb') as w:
            w.setnchannels(channels);w.setsampwidth(width);w.setframerate(rate)
            values=[0 if i in (0,frames-1) else round(peak*math.sin(i*.13)) for i in range(frames)]
            if width==2:w.writeframes(struct.pack('<'+'h'*(frames*channels),*[x for x in values for _ in range(channels)]))
            else:w.writeframes(b'\0'*(frames*channels*width))
        return b.getvalue()

    def test_reject_wrong_rate(self):
        with self.assertRaises(ValueError):job.inspect_pcm16_wav(self.fixture(rate=44100))

    def test_reject_stereo(self):
        with self.assertRaises(ValueError):job.inspect_pcm16_wav(self.fixture(channels=2))

    def test_reject_wrong_width(self):
        with self.assertRaises(ValueError):job.inspect_pcm16_wav(self.fixture(width=1))

    def test_reject_no_headroom(self):
        with self.assertRaises(ValueError):job.inspect_pcm16_wav(self.fixture(peak=32767))

    def test_reject_silent(self):
        with self.assertRaises(ValueError):job.inspect_pcm16_wav(self.fixture(peak=0))

    def test_reject_long_cue(self):
        with self.assertRaises(ValueError):job.inspect_pcm16_wav(self.fixture(frames=25000))

    def test_reject_truncated(self):
        with self.assertRaises(ValueError):job.inspect_pcm16_wav(self.fixture()[:-2])

    def test_reject_trailing_bytes(self):
        with self.assertRaises(ValueError):job.inspect_pcm16_wav(self.fixture()+b'bad')

    def test_reject_float_format(self):
        x=bytearray(self.fixture());struct.pack_into('<H',x,20,3)
        with self.assertRaises(ValueError):job.inspect_pcm16_wav(bytes(x))

    def test_reject_nonzero_endpoint(self):
        x=bytearray(self.fixture());struct.pack_into('<h',x,44,1000)
        with self.assertRaises(ValueError):job.inspect_pcm16_wav(bytes(x))

    def test_reject_populated_target(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as t:
            p=Path(t);job.require_unused(p);(p/'old.uasset').write_bytes(b'x')
            with self.assertRaises(ValueError):job.require_unused(p)

    def test_reject_extra_registry_object(self):
        with self.assertRaises(ValueError):job.require_exact_set(['a','b'],['a'])

    def test_reject_duplicate_registry_object(self):
        with self.assertRaises(ValueError):job.require_exact_set(['a','a'],['a'])

    def test_reject_missing_registry_object(self):
        with self.assertRaises(ValueError):job.require_exact_set([],['a'])

    def test_reject_manifest_semantic_mutations(self):
        p=ROOT/'source-assets/production/first-batch-audio-v002/manifest.json'
        original=json.loads(p.read_text('utf-8-sig'))
        changes=[
            lambda m:m.update(package='/Game/Production/FirstBatch/v001/Audio'),
            lambda m:m.update(auditioned=True),
            lambda m:m.update(runtime_bound=True),
            lambda m:m.update(timing_authority_changed=True),
            lambda m:m.update(old17_replaced=True),
            lambda m:m['cues'][0].update(id=m['cues'][1]['id']),
            lambda m:m['cues'][0].update(file='C:/Windows/anything.wav'),
            lambda m:m['cues'][0]['source'].update(license_id='unknown'),
            lambda m:m['cues'][0]['processing'].update(gain_linear=math.nan),
            lambda m:m['cues'][0].update(binding_authoritative=True),
        ]
        for change in changes:
            with self.subTest(change=changes.index(change)):
                m=copy.deepcopy(original);change(m)
                with self.assertRaises(ValueError):job.validate_manifest(m)


if __name__ == '__main__':
    unittest.main(verbosity=2)
