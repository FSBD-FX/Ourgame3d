"""Small synthetic AV/timeline/rectangle checks. No native PASS or View."""
from pathlib import Path
from datetime import datetime,timezone
import copy
import hashlib
import importlib.util
import json
import math
import unittest
import wave
import numpy as np
from PIL import Image

HERE=Path(__file__).resolve().parent
RUN=HERE/'validation-runs'/('s'+datetime.now(timezone.utc).strftime('%H%M%S%f'))
spec=importlib.util.spec_from_file_location('air_media_candidate',HERE/'prepare-Air-production-media-v001.py')
M=importlib.util.module_from_spec(spec);spec.loader.exec_module(M)


class PresentationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.frames=[]
        for i in range(6):
            p=RUN/f'SYNTHETIC-frame-{i}.png'
            im=Image.new('RGB',(1280,720),(20+i*20,90,150))
            im.save(p);cls.frames.append(p)

    def test_01_full_VFR_mux_offset_and_full_AAC_decode_on_synthetic_only(self):
        work=RUN/'encoding';display=RUN/'presentation';work.mkdir();display.mkdir()
        offsets=[.01234567,.04666677,.08333333,.12123456,.1723456,.20678901];duration=.25;rate=48000;channels=2;frames=int(duration*rate)
        time=np.arange(frames)/rate;samples=(np.sin(time*440*2*math.pi)*5000).astype('<i2')
        stereo=np.repeat(samples[:,None],channels,axis=1).tobytes();wav=RUN/'SYNTHETIC-sine-only-NOT-native.wav'
        with wave.open(str(wav),'wb') as f:f.setnchannels(channels);f.setsampwidth(2);f.setframerate(rate);f.writeframes(stereo)
        r=M.encode_with_full_native_mix(work,display,self.frames,offsets,duration,wav,dict(sample_rate_hz=rate,channels=channels,frames=frames))
        self.assertEqual(r['muxed_VFR']['decoded_frames'],6)
        self.assertTrue(r['full_AV_decoded']);self.assertFalse(r['native_audio_trimmed_or_replaced'])
        self.assertAlmostEqual(r['first_video_PTS_s'],offsets[0],places=5)
        self.assertLessEqual(abs(r['decoded_AAC_samples']-frames),2048)
        self.assertEqual(M.pin(wav)['sha256'],hashlib.sha256(wav.read_bytes()).hexdigest())

    def test_02_drop_retime_or_wrong_timebase_rejected(self):
        valid='#tb 0: 1/1000000\n0,0,0,100,10,hash\n0,1,100,100,10,hash\n'
        M.timing_rows(valid,2,[0,.0001])
        for text,count,expected in ((valid,3,[0,.0001,.0002]),(valid,2,[0,.1]),(valid.replace('1/1000000','1/1000'),2,[0,.0001])):
            with self.assertRaises(ValueError):M.timing_rows(text,count,expected)

    def test_03_crops_labels_and_fullwidth_game_rectangles_do_not_overlap(self):
        before=[M.pin(p) for p in self.frames]
        obs=[dict(observed_air_transition_ordinal=2,physical_visual_key=i,wall_offset_s=i*.04,ground=[0,0],camera_ground=[0,0],
                  new_air_draw=dict(drawn=True,context_ground=[640,490])) for i in range(6)]
        samples=[dict(observation=i) for i in range(6)];report=dict(observations=obs)
        cropped=M.make_board(RUN/'SYNTHETIC-crop-board.png',samples,self.frames,report,3,True)
        full=M.make_board(RUN/'SYNTHETIC-full-board.png',samples,self.frames,report,1,False)
        self.assertGreaterEqual(cropped['cell_size'][1],320+32+12)
        self.assertGreaterEqual(full['cell_size'][1],720+32+12)
        self.assertEqual(before,[M.pin(p) for p in self.frames])
        self.assertTrue(all(x['source_pixels_resized'] is False and x['label_inside_game_rect'] is False for x in cropped['details']+full['details']))
        self.assertTrue(cropped['exact_RGB_source_crops_redecoded_and_equal'] and full['exact_RGB_source_crops_redecoded_and_equal'])
        with self.assertRaises(ValueError):M.rectangles_nonoverlap([[0,0,256,320],[0,265,256,585]])

    def test_04_immutable_copy_and_output_fail_closed(self):
        target=RUN/'SYNTHETIC-copy.png';p=M.copy_exact(self.frames[0],target)
        self.assertEqual(p['sha256'],M.pin(self.frames[0])['sha256'])
        with self.assertRaises(FileExistsError):M.copy_exact(self.frames[1],target)
        self.assertEqual(p,M.pin(target))
        p=RUN/'exclusive.json';M.write_new(p,{'first':True})
        with self.assertRaises(FileExistsError):M.write_new(p,{'overwritten':True})

    def test_05_record_actual_binary_and_package_versions(self):
        env=M.runtime_environment()
        self.assertEqual(M.pin(env['ffmpeg_binary']['path']),env['ffmpeg_binary'])
        self.assertIn('ffmpeg version',env['ffmpeg_version_output'])
        self.assertTrue(env['Pillow_version'] and env['imageio_ffmpeg_version'])
        M.write_new(RUN/'actual-synthetic-test-environment.json',env)


if __name__=='__main__':
    RUN.mkdir(parents=True,exist_ok=False)
    source=M.pin(HERE/'prepare-Air-production-media-v001.py')
    with (RUN/'synthetic-tests.log').open('x',encoding='utf-8') as stream:
        result=unittest.TextTestRunner(stream=stream,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(PresentationTests))
    unchanged=M.pin(source['path'])==source
    report=dict(schema='Air-production-presentation-synthetic-host-tests-v001',passed=result.wasSuccessful() and unchanged,
                tests=result.testsRun,failures=len(result.failures),errors=len(result.errors),sources_unchanged=unchanged,source=source,
                synthetic_AV_only=True,actual_native_evidence=False,UE_calls=0,E_calls=0,View=False,FinalAccepted=False)
    p=M.write_new(RUN/'synthetic-tests-result.json',report)
    print(json.dumps(dict(result=p,**report)));raise SystemExit(0 if report['passed'] else 1)
