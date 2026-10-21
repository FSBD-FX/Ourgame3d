import unittest,copy
from dodge_manual_contract_v001 import apply_chain,preserve193,STAGE_NEW,PROD_NEW,OBSERVER_NEW
P='UnrealGame/Source/CodexDungeon/'
def pin(name,h='a'):return dict(path=P+name,bytes=1,sha256=h*64)
def suite():
 names=['HOST_OLD.'+str(i) for i in range(193)]+['HOST_DODGE.'+str(i) for i in range(3)]
 return dict(succeeded=196,failed=0,succeededWithWarnings=0,notRun=0,inProcess=0,tests=[dict(fullTestPath=n,state='Success',errors=0,warnings=0,entries=[]) for n in names])
def chain():
 names=['DungeonFighter.h','DungeonFighter.cpp','DungeonHUD.h','DungeonHUD.cpp','DungeonFairytaleSwordPresentation.cpp','DungeonStoneGuard.h']
 base={P+n:pin(n) for n in names};state=copy.deepcopy(base);receipts=[]
 groups=[('stage0',STAGE_NEW|{P+'DungeonFighter.h',P+'DungeonFighter.cpp',P+'DungeonHUD.h'},'b'),
  ('production',PROD_NEW|{P+'DungeonFairytaleSwordDodgePlan.cpp',P+'DungeonFairytaleSwordDodgeProfile.cpp',P+'DungeonFighter.cpp',P+'DungeonHUD.cpp',P+'DungeonFairytaleSwordPresentation.cpp'},'c'),
  ('observer',OBSERVER_NEW|{P+'DungeonHUD.cpp'},'d')]
 for role,paths,h in groups:
  before=len(state);previous=[copy.deepcopy(state[n]) for n in sorted(paths) if n in state]
  after=[pin(n.removeprefix(P),h) for n in sorted(paths)];state.update({x['path']:x for x in after})
  receipts.append((role,dict(schema='Root-Dodge-'+role+'-admission-v001',success=True,FinalAccepted=False,
   previous_Source_count=before,Source_count=len(state),previous=previous,admitted=after,unaffected_Source_unchanged=True)))
 return base,receipts
class Contracts(unittest.TestCase):
 def test_three_real_admission_roles_preserve_unrelated_source_and_bind_last_hud(self):
  base,receipts=chain();out=apply_chain(base,receipts)
  self.assertEqual(len(out),17);self.assertEqual(out[P+'DungeonStoneGuard.h'],pin('DungeonStoneGuard.h'))
  self.assertEqual(out[P+'DungeonHUD.cpp'],pin('DungeonHUD.cpp','d'))
 def test_valid193_plus3_then_reject_replaced_old_target_and_hidden_error(self):
  s=suite();old={'HOST_OLD.'+str(i) for i in range(193)};new={'HOST_DODGE.'+str(i) for i in range(3)};preserve193(s,old,new)
  for change in [lambda s:s['tests'][0].update(fullTestPath='HOST_WRONG'),lambda s:s['tests'][0].update(entries=[{'event':{'type':'Error'}}])]:
   q=copy.deepcopy(s);change(q)
   with self.assertRaises(ValueError):preserve193(q,old,new)
 def test_reject_count_only_source_admission_without_previous_binding(self):
  base,receipts=chain();receipts[0][1]['previous'].pop()
  with self.assertRaises(ValueError):apply_chain(base,receipts)
 def test_reject_unrelated_kernel_source_even_with_valid_counts(self):
  base,receipts=chain();r=receipts[1][1]
  r['previous'].append(pin('DungeonStoneGuard.h'));r['admitted'].append(pin('DungeonStoneGuard.h','c'))
  with self.assertRaises(ValueError):apply_chain(base,receipts)
if __name__=='__main__':unittest.main(verbosity=2)
