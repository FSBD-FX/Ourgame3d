"""Reconstruct a listening WAV from actual native HUD play-request receipts.
This is NOT captured UE audio, not an audition and not a runtime mix acceptance.
"""
import argparse,hashlib,json,math,struct,wave
from pathlib import Path
HERE=Path(__file__).resolve().parent;CANDIDATE=HERE.parent
def need(v,m):
 if not v:raise RuntimeError(m)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--native-report',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
 r=json.loads(args.native_report.read_text(encoding='utf-8-sig'));need(r['schema']=='guard-feedback-native-request-report-v1' and r['native_requests'] is True,'Actual native request schema required')
 rows=r['requests'];need(rows,'No actual audio requests');assets=json.loads((CANDIDATE/'audio-v001/manifest.json').read_text(encoding='utf-8'))['assets'];bank={x['cue']:x for x in assets};seen=set();loaded={};last=-math.inf
 for x in rows:
  key=(x['entity_id'],x['sequence']);need(key not in seen,'Repeated native request identity');seen.add(key);need(int(x['event_id'])>0 and int(x['entity_id'])>0 and int(x['sequence'])>0,'Missing exact native source IDs')
  cue=x['cue'];need(cue in bank and x['sound_path']==bank[cue]['object_path'],'Unknown or substituted native SoundWave');need(x['pitch']==1.,'This reconstruction supports exact native pitch1 only');need(0<x['volume']<=1.,'Unexpected native gain')
  need(math.isfinite(x['requested_at']) and math.isfinite(x['at_time']) and 0<=x['requested_at']-x['at_time']<=.25,'Native stale/future request');need(x['requested_at']>=last,'Native request order changed');last=x['requested_at']
  if cue not in loaded:
   a=bank[cue];p=CANDIDATE/'audio-v001'/a['file'];need(hashlib.sha256(p.read_bytes()).hexdigest()==a['sha256'],'Changed source WAV')
   with wave.open(str(p),'rb') as w:need((w.getnchannels(),w.getsampwidth(),w.getframerate())==(1,2,48000),'Source PCM changed');b=w.readframes(w.getnframes());loaded[cue]=[v/32768 for v in struct.unpack('<'+'h'*(len(b)//2),b)]
 start=rows[0]['requested_at'];end=max(x['requested_at']-start+len(loaded[x['cue']])/48000 for x in rows)+.15;n=math.ceil(end*48000);mix=[0.]*n
 for x in rows:
  offset=round((x['requested_at']-start)*48000)
  for i,v in enumerate(loaded[x['cue']]):mix[offset+i]+=v*x['volume']
 peak=max(abs(v) for v in mix);need(peak<1.,'Actual request reconstruction clips; preserve evidence and adjust mix proposal separately')
 args.output.mkdir(parents=True,exist_ok=False);p=args.output/'actual-request-timeline-reconstruction.wav'
 with wave.open(str(p),'wb') as w:w.setparams((1,2,48000,0,'NONE','not compressed'));w.writeframes(struct.pack('<'+'h'*n,*[round(v*32767) for v in mix]))
 report={'schema':'guard-offline-native-request-reconstruction-v1','source_report':str(args.native_report.resolve()),'source_report_sha256':hashlib.sha256(args.native_report.read_bytes()).hexdigest(),'output':p.name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'native_request_count':len(rows),'first_simulation_request':start,'duration_s':n/48000,'sample_peak_dBFS':20*math.log10(peak),'normalization':False,'clipping':False,'recorded_engine_audio':False,'audio_device_auditioned':False,'final_mix_accepted':False,'limits':'Dry mono sum of native requested gains and timestamps. Omits UE output latency, compression, spatial/device processing, and interruption Stop timing unless explicitly captured; no claim of loopback audio.'}
 (args.output/'manifest.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(report))
if __name__=='__main__':main()
