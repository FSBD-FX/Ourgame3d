"""Host negatives using retained readonly native metadata, never rewriting evidence."""
from pathlib import Path
import ast,copy,json,math,runpy,unittest
C=Path(__file__).resolve().parent.parent;A=runpy.run_path(str(C/'tooling/verify-Dodge-native-v002.py'));B=A['base_api']()
archive=Path('F:/Ourgame/过程图稿与视频/2026-10-18_钟盔真实Shift向外闪避四相试样_left_v001')
R=json.loads((archive/'原件/runtime-report.json').read_text(encoding='utf-8-sig'));O=R['observations']
def accepted(obs):
 first=next((i for i,o in enumerate(obs)if o['dodge_record']['record_count']==1 and o['dodge_record'].get('finish')==1),None);edges=[]
 for i in range(len(obs)-1):
  a,b=obs[i:i+2]
  if a['dodge_query_ok']and a['dodge_draw']['frame']==3 and B['join'](b,R,False):edges.append(('Dodge3_to_Ready',i,i+1))
  if B['join'](a,R,False)and B['join'](b,R,True)and A['post_ready_walk_window'](a,b,R,i,first):edges.append(('Ready_to_Walk',i,i+1))
 return [x[0]for x in edges]==['Dodge3_to_Ready','Ready_to_Walk']and edges[0][2]==first

class Repairs(unittest.TestCase):
 def test_normalized_source_exact_and_raw_rejected(self):
  p=json.loads((C.parent/'read-only-input-pins-v001.json').read_text());profile=json.loads(Path(p['inputs']['prepared_profile_pin']['path']).read_text())
  for f in range(4):
   d=next(o['dodge_draw']for o in O if o['dodge_query_ok']and o['dodge_draw']['frame']==f);self.assertTrue(B['point'](d['axis_artist'],A['source_axis'](profile['frames'][f]),0))
   if f in[1,2]:self.assertFalse(B['point'](d['axis_artist'],profile['frames'][f]['Axis_artist_raw_xy'],0))
 def test_original_post_join_passes_and_prior_is_excluded(self):
  self.assertTrue(accepted(O));self.assertTrue(B['join'](O[287],R,False)and B['join'](O[288],R,True));self.assertFalse(A['post_ready_walk_window'](O[287],O[288],R,287,300))
 def test_only_prior_staging_cannot_replace_post_walk(self):
  obs=copy.deepcopy(O)
  for o in obs:
   if o['phase']==11 and o['join_draw']['walk']:o['join_draw']['active']=False
  self.assertTrue(B['join'](obs[287],R,False)and B['join'](obs[288],R,True));self.assertFalse(accepted(obs))
 def test_missing_first_completed_ready_cannot_use_later_ready(self):
  obs=copy.deepcopy(O);obs[300]['join_draw']['supported']=False;self.assertTrue(B['join'](obs[301],R,False));self.assertFalse(accepted(obs))
 def test_wrong_action_or_finish_or_window_refused(self):
  for key,value in [('action','2'),('finish',0),('finished_at',R['dodge_end']+.1),('record_count',0)]:
   a,b=copy.deepcopy(O[304:306]);a['dodge_record'][key]=value;self.assertFalse(A['post_ready_walk_window'](a,b,R,304,300))
  a,b=copy.deepcopy(O[304:306]);a['phase']=8;self.assertFalse(A['post_ready_walk_window'](a,b,R,304,300));a['phase']=11;b['phase']=12;self.assertFalse(A['post_ready_walk_window'](a,b,R,304,300))
if __name__=='__main__':unittest.main()
