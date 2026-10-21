"""Original deterministic one-shot trials. No samples, voices, network or paid APIs.
Sound quality and in-engine mix remain unaccepted until actual device audition.
"""
import argparse, hashlib, json, math, random, struct, sys, wave
from pathlib import Path
RATE=48000
# cue, seconds, seed, bodyHz, noisy grit, modal ringing, thud, air; all are proposals.
SPECS=[
 ('GUARD_WAKE_01',.65,301,49,.60,.40,.42,.05),
 ('GUARD_STEP_01',.18,302,57,.36,.15,.85,.02),
 ('GUARD_AXE_WINDUP_01',.48,303,73,.50,.38,.20,.23),
 ('GUARD_AXE_RELEASE_01',.28,304,61,.35,.12,.36,.92),
 ('GUARD_STOMP_WINDUP_01',.36,305,43,.43,.25,.35,.08),
 ('GUARD_STOMP_IMPACT_01',.48,306,39,.70,.40,1.,.06),
 ('GUARD_HIT_STONE_01',.20,307,114,.80,.50,.30,.01),
 ('GUARD_HIT_FLESH_LEATHER_01',.14,308,92,.32,.04,.88,.06),
 ('GUARD_HIT_METAL_01',.27,309,344,.28,.95,.22,.03),
 ('GUARD_STUN_01',.46,310,84,.63,.63,.40,.04),
 ('GUARD_DEATH_01',.86,311,45,.86,.56,.75,.04),
]
PACKAGE='/Game/Production/FirstBatch/v028/GuardAudio'
def voice(spec):
 cue,duration,seed,freq,grit,modal,thud,air=spec;r=random.Random(seed);n=round(duration*RATE);x=[];low=0.;hiold=0.;phase=0.
 for i in range(n):
  t=i/RATE;u=t/duration;white=r.uniform(-1.,1.);low+=.075*(white-low);high=white-low
  phase+=2*math.pi*freq*(1.-.28*u)/RATE
  env=math.exp(-t/(duration*.27));body=math.sin(phase)*env+math.sin(phase*.503)*env*.35
  ring=sum(math.sin(2*math.pi*freq*k*t+q)*math.exp(-t/(duration*(.13+.07*j)))*v for j,(k,q,v) in enumerate([(2.17,.1,.31),(3.63,.7,.22),(5.11,1.2,.15),(7.91,.4,.09)]))
  crack=high*env*(.65+.35*math.sin(2*math.pi*(31+seed%17)*t)**8)
  sweep=high*math.sin(math.pi*min(1.,u))**1.4
  if 'WINDUP' in cue: crack*=.2+.8*u;ring*=.15+.85*u;body*=.25
  if cue=='GUARD_WAKE_01': crack*=.25+.75*math.sin(math.pi*u)**2;body*=.4+.6*u
  if cue=='GUARD_DEATH_01':
   for at,amp in [(.17,.32),(.31,.24),(.48,.16)]:
    if t>=at:crack+=high*amp*math.exp(-(t-at)/.055)
  fade=min(1.,t/.003,(duration-t)/.018);x.append((body*thud+ring*modal+crack*grit+sweep*air)*max(0.,fade)**2)
 dc=sum(x)/len(x);x=[v-dc for v in x];peak=max(abs(v) for v in x);gain=10**(-9/20)/peak
 return [max(-32767,min(32767,round(v*gain*32767))) for v in x]
def metrics(p):
 with wave.open(str(p),'rb') as w:
  assert (w.getnchannels(),w.getsampwidth(),w.getframerate())==(1,2,RATE);b=w.readframes(w.getnframes());vals=struct.unpack('<'+'h'*(len(b)//2),b)
 return {'frames':len(vals),'duration_s':len(vals)/RATE,'sample_rate':RATE,'channels':1,'bits':16,'peak_dBFS':20*math.log10(max(abs(v) for v in vals)/32768),'rms_dBFS':20*math.log10(math.sqrt(sum(v*v for v in vals)/len(vals))/32768),'clipped_samples':sum(abs(v)==32767 for v in vals)}
def main():
 a=argparse.ArgumentParser();a.add_argument('--output',type=Path,required=True);args=a.parse_args();args.output.mkdir(parents=True,exist_ok=False);rows=[]
 for spec in SPECS:
  cue=spec[0];name='SW_AUD_'+cue+'_v001';p=args.output/(name+'.wav');pcm=voice(spec)
  with wave.open(str(p),'wb') as w:w.setparams((1,2,RATE,0,'NONE','not compressed'));w.writeframes(struct.pack('<'+'h'*len(pcm),*pcm))
  rows.append({'cue':cue,'file':p.name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size,'name':name,'package_path':PACKAGE+'/'+name,'object_path':PACKAGE+'/'+name+'.'+name,'metrics':metrics(p),'parameters':spec[1:],'status':'original procedural trial; not auditioned; no final timbre or mix approval'})
 data={'schema':'guard-original-audio-trial-v1','python':sys.version,'generator_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'external_api_calls':0,'third_party_samples':0,'human_voice':False,'auditioned':False,'native_imported':False,'final_audio_accepted':False,'format':'48000 Hz mono PCM16; finite one-shots; no loops; decoded sample peak target -9 dBFS, not true peak/LUFS','provenance':'Original local mathematical synthesis created for this project. No claim of universal copyright eligibility or public-domain dedication.','assets':rows}
 (args.output/'manifest.json').write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8');print(json.dumps({'count':len(rows),'output':str(args.output),'auditioned':False,'external_api_calls':0}))
if __name__=='__main__':main()
