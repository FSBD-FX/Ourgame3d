"""Host contract negatives only; no synthetic evidence is called native proof."""
from pathlib import Path
import json,math,runpy,tempfile,unittest
C=Path(__file__).resolve().parent.parent
A=runpy.run_path(str(C/'tooling/verify-Dodge-native-v001.py'))

class Contracts(unittest.TestCase):
 def test_original_absolute_phase_thresholds(self):
  for start in [0.,9.6074908696274122,18.040050299912693,1.e6]:
   self.assertEqual(A['frame_at'](start,start),0)
   for phase,delta in enumerate([.1,.2,.3],1):
    edge=start+delta;self.assertEqual(A['frame_at'](edge,start),phase);self.assertEqual(A['frame_at'](math.nextafter(edge,start),start),phase-1)
 def test_actual_float_quad_mirror(self):
  # Actual UV reflection reverses artist X exactly once, including sword pivot.
  for side in [-1,1]:
   p=[99/512 if side>0 else 1-99/512,.5];at=[640.,400.];width=44.;angle=36.86989764584402*side
   q=dict(uv=[0 if side>0 else 1,0],uv_size=[side,1],size=[width,width],top=[at[i]-p[i]*width for i in range(2)],rotation_pivot=p,rotation=angle)
   self.assertTrue(A['point'](A['quad_project'](q,[99,256]),at,1.e-10))
   want=[at[0]+side*.8*100/512*width,at[1]+.6*100/512*width]
   self.assertTrue(A['point'](A['quad_project'](q,[199,256]),want,1.e-10))
   q['rotation']=-q['rotation'];self.assertFalse(A['point'](A['quad_project'](q,[199,256]),want,1.e-5))
 def test_pending_prereg_rejected_before_dependencies(self):
  with tempfile.TemporaryDirectory(dir=C)as d:
   p=Path(d)/'pending.json';p.write_text(json.dumps(dict(schema='hero-Dodge4-Root-prereg-v001',is_template=True,RootApproved=False,pre_registered_before_capture=False,FinalAccepted=False)))
   with self.assertRaisesRegex(ValueError,'Actual typed Root'):A['preflight'](Path(d),p)
 def test_schema_is_explicit(self):
  protocol=json.loads((C/'proof-protocol-v001.json').read_text());self.assertEqual(protocol['runtime_report_schema'],'hero-SWD-LGT-Dodge4-native-observer-v001');self.assertEqual(protocol['session_schema'],'hero-Dodge4-native-session-v001')
  source=(C/'tooling/verify-Dodge-native-pixels-v001.py').read_text();self.assertIn("report['schema']==protocol['runtime_report_schema']",source)
 def test_old_join_counts_are_not_Dodge9(self):
  r=dict(sword_instance='2');o=dict(dodge_query_ok=False,dodge_active=False,dodge_draw=dict(drawn=False),rendered_stack=list(range(7)),join_draw=dict(active=True,supported=True,walk=False,texture_ready=True,armor_drawn=True,weapon_instance='2',stack=list(range(7)),clip='sword_ready_idle'))
  self.assertTrue(A['join'](o,r,False));o['join_draw']['stack']=o['rendered_stack']=list(range(9));self.assertFalse(A['join'](o,r,False))
if __name__=='__main__':unittest.main()
