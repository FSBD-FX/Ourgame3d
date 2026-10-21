"""Synthetic tooling cases only. No actual capture, PNG, UE or acceptance receipt."""
from pathlib import Path
import copy
import importlib.util
import unittest

HERE = Path(__file__).resolve().parent
def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path); module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module); return module
tool = load("combo_candidate", HERE / "postprocess-leather-combo-trial-v001.py")
prior = load("prior_tooling_fixture", HERE.parent / "leather-primary1-proof-tooling-v001/test-tooling-contract-v001.py")


def fixture():
    report, index, _ = prior.fixture()
    rows = report["observations"][:8]
    for row in rows:
        row["needs_slot_selection"] = False
        if row["committed_armor_id"] == "8" and row["supported"]:
            row["leather_combo_side"] = 0; row["leather_combo_fresh_ready_seen_this_side"] = 0
    prototype = copy.deepcopy(rows[-1])
    schedules = [[(1.8,1.97,2.09,2.4),(2.4,2.55,2.67,2.94),(2.94,3.16,3.28,3.6)],[(4.3,4.47,4.59,4.9),(4.9,5.05,5.17,5.44),(5.44,5.66,5.78,6.1)]]
    def append(side, stage, frame, sim, count=0):
        row = copy.deepcopy(prototype); primary = stage >= 0; clip = "Primary"+str(stage+1) if primary else "Ready"
        row.update(flow_step=6, flow_phase=tool.PHASES[6], sim=sim, actual_sim=sim, wall_offset_s=sim-.4, facing=-1 if side == 0 else 1,
            stage=stage, frame=frame, action_id=str(10+side*3+stage) if primary else "0", clip=f"sword_primary_{stage+1}" if primary else "sword_ready_idle",
            texture=tool.body_path(clip,frame), draw_stack=tool.expected_stack(frame,stage), draw_id=str(100+len(rows)),
            leather_combo_side=side, leather_combo_fresh_ready_seen_this_side=count)
        if primary:
            a,b,c,d = schedules[side][stage]; row.update(start=a, active_at=b, active_end=c, end=d, melee_pending_primary=stage < 2 and sim >= d-.08)
        else: row.update(start=0, active_at=0, active_end=0, end=0, melee_pending_primary=False)
        rows.append(row)
    for side in (0,1):
        for stage, (start,active,endactive,end) in enumerate(schedules[side]):
            for frame, sim in enumerate((start+.01,start+(active-start)*.6,active+.01,active+(endactive-active)*.6,endactive+.01,end-.02)):
                append(side,stage,frame,sim)
        for count, sim in enumerate((3.65,3.75,4.) if side == 0 else (6.15,6.25,6.35),1): append(side,-1,0,sim,count)
    downs = [("Enter",.01,0.),("E",.2,.6),("A",.35,.75),("E",.8,1.2),("J",1.4,1.8),("J",1.92,2.32),("J",2.46,2.86),("D",3.7,4.1),("J",3.9,4.3),("J",4.42,4.82),("J",4.96,5.36)]
    inputs = []
    for key, wall, sim in downs: inputs.extend([{"key":key,"down":True,"wall_offset_s":wall,"sim":sim},{"key":key,"down":False,"wall_offset_s":wall+.08,"sim":sim+.08}])
    report.update(scope=tool.COMBO_SCOPE,leather_combo_only_trial=True,leather_primary1_only_trial=False,leather_primary1_masks_left_right=[0,0],
        leather_primary1_attack_ids_left_right=["0","0"],light_primary_phase_masks=[63,63,63],leather_combo_masks_left_right_by_stage=[[63,63,63],[63,63,63]],
        leather_combo_attack_ids_left_right_by_stage=[["10","11","12"],["13","14","15"]],leather_combo_fresh_ready_seen_left_right=[3,3],leather_combo_first_side=0,
        leather_combo_normal_turn_requested=True,leather_combo_second_sequence_normal_J_requested=True,observations=rows,duration_s=6.2,
        normal_input_requests=inputs,inputevents=copy.deepcopy(inputs),capture_timing={"use_fixed_time_step":False})
    report["phasechecks"][-1].update(sim=6.36,wall_offset_s=5.96)
    index["observations"] = len(rows)
    packages = {tool.package_file(path):{} for row in rows for path in row["draw_stack"]+[row["texture"]]}
    return report,index,packages


class ComboTooling(unittest.TestCase):
    def test_synthetic_six_actual_ids_36_phase_selection_and_ready(self):
        report,index,packages = fixture(); selected,audit = tool.verify_flow(report,index,packages)
        self.assertEqual(len(selected),36); self.assertEqual(audit["actual_fresh_ready_left_right"],[3,3]); self.assertEqual(audit["operations_committed"],1)
        self.assertTrue(any(row["melee_pending_primary"] for row in report["observations"]))

    def test_meaningful_negative_flow_variants(self):
        mutations = [
            ("P1-only flag",lambda r,i,p:r.update(leather_primary1_only_trial=True)),
            ("wrong scope",lambda r,i,p:r.update(scope="P1-only")),
            ("native RED",lambda r,i,p:r.update(passed=False)),
            ("fixed clock",lambda r,i,p:r["capture_timing"].update(use_fixed_time_step=True)),
            ("audio",lambda r,i,p:r.update(audio_recorded=True)),
            ("forced frame",lambda r,i,p:r.update(forced_frame=True)),
            ("unflushed",lambda r,i,p:r.update(native_async_capture_writes_flushed=False)),
            ("complete-unit claim",lambda r,i,p:r.update(formal_complete_units=1)),
            ("missing mask bit",lambda r,i,p:r["leather_combo_masks_left_right_by_stage"][1].__setitem__(2,31)),
            ("duplicate ID",lambda r,i,p:r["leather_combo_attack_ids_left_right_by_stage"][1].__setitem__(2,"10")),
            ("invented ready",lambda r,i,p:r.update(leather_combo_fresh_ready_seen_left_right=[99,3])),
            ("no actual turn",lambda r,i,p:r.update(leather_combo_normal_turn_requested=False)),
            ("native wrong first side",lambda r,i,p:r.update(leather_combo_first_side=1)),
            ("medium flow",lambda r,i,p:r.update(medium_instance_id="5")),
            ("sword version changed",lambda r,i,p:r["observations"][-1].update(committed_weapon_version="3")),
            ("LGT version changed",lambda r,i,p:r["observations"][-1].update(committed_armor_version="3")),
            ("owner changed",lambda r,i,p:r["observations"][-1].update(owner_id="99")),
            ("second commit",lambda r,i,p:r["observations"][-1].update(operation_count="2")),
            ("UI",lambda r,i,p:r["observations"][8].update(interface_visible=True)),
            ("body scale",lambda r,i,p:r["observations"][8].update(canvas_size=72.)),
            ("sword scale",lambda r,i,p:r["observations"][8].update(weapon_scale=.4)),
            ("marker NaN",lambda r,i,p:r["observations"][8].update(grip_screen=[float('nan'),2.])),
            ("wrong P2 wholebody",lambda r,i,p:r["observations"][14].update(texture=tool.body_path("Primary1",0))),
            ("wrong P3 wholebody",lambda r,i,p:r["observations"][20].update(texture=tool.body_path("Primary2",0))),
            ("old P2 armor",lambda r,i,p:r["observations"][14]["draw_stack"].__setitem__(1,r["observations"][14]["draw_stack"][1].replace('/v014/HeroLeatherPrimary2/','/v010/HeroSwordPrimary2Armor/'))),
            ("no HelmetForeground",lambda r,i,p:r["observations"][20]["draw_stack"].pop(5)),
            ("same action flips side",lambda r,i,p:r["observations"][9].update(facing=1)),
            ("fake per-frame ready counter",lambda r,i,p:r["observations"][8].update(leather_combo_fresh_ready_seen_this_side=3)),
            ("final is not Ready",lambda r,i,p:r["observations"][-1].update(animation="walk")),
            ("missing bound resource",lambda r,i,p:p.pop(tool.package_file(tool.SWORD))),
            ("queued final stage",lambda r,i,p:r["observations"][25].update(melee_pending_primary=True)),
            ("input alias differs",lambda r,i,p:r["inputevents"][0].update(key="J")),
            ("missing input release",lambda r,i,p:(r["normal_input_requests"].pop(),r["inputevents"].pop())),
            ("wrong stage",lambda r,i,p:r["observations"][14].update(stage=2)),
            ("native clock NaN",lambda r,i,p:r["observations"][8].update(actual_sim=float('nan'))),
        ]
        for name,mutation in mutations:
            with self.subTest(name=name):
                report,index,packages = fixture(); mutation(report,index,packages)
                with self.assertRaises(ValueError): tool.verify_flow(report,index,packages)

    def test_actual_coverage_not_only_report_masks(self):
        report,index,packages = fixture(); row=report["observations"][19]
        row.update(frame=4,texture=tool.body_path("Primary2",4),draw_stack=tool.expected_stack(4,1))
        with self.assertRaises(ValueError): tool.verify_flow(report,index,packages)

    def test_explicit_current_test_name_contract_allows_new160(self):
        names=["Synthetic.Test."+str(i) for i in range(160)]
        expected={"expected_count":160,"full_test_paths":names}
        report={"succeeded":160,"failed":0,"succeededWithWarnings":0,"notRun":0,"inProcess":0,"tests":[{"fullTestPath":name,"state":"Success","errors":0,"warnings":0} for name in names]}
        self.assertEqual(tool.check_automation(report,expected),160)
        for mutation in (lambda r:r.update(succeeded=157),lambda r:r["tests"][-1].update(fullTestPath=names[0]),lambda r:r["tests"][-1].update(state="Fail")):
            wrong=copy.deepcopy(report);mutation(wrong)
            with self.assertRaises(ValueError):tool.check_automation(wrong,expected)

    def test_real_recovery_buffer_expiry_and_final_end_gates(self):
        report,index,packages=fixture()
        for alias in ("normal_input_requests","inputevents"):
            report[alias][10].update(sim=1.9,wall_offset_s=1.5)
            report[alias][11].update(sim=1.98,wall_offset_s=1.58)
        with self.assertRaises(ValueError):tool.verify_flow(report,index,packages)
        report,index,packages=fixture()
        for alias in ("normal_input_requests","inputevents"):
            report[alias][14].update(sim=3.7,wall_offset_s=3.3)
            report[alias][15].update(sim=3.78,wall_offset_s=3.38)
        with self.assertRaises(ValueError):tool.verify_flow(report,index,packages)
        report,index,packages=fixture()
        for row in report["observations"]:
            if row["action_id"]=="15":row["end"]=6.5
        with self.assertRaises(ValueError):tool.verify_flow(report,index,packages)

    def test_pixel_FIFO_function_exactly_reused(self):
        base=Path('F:/Ourgame/tools/scripts/postprocess-leather-primary1-trial-v001.py').read_text(encoding='utf-8-sig')
        current=(HERE/'postprocess-leather-combo-trial-v001.py').read_text(encoding='utf-8')
        self.assertEqual(base[base.index('def verify_pixels('):base.index('def write_whole_phase_view(')].strip(),current[current.index('def verify_pixels('):current.index('def write_whole_phase_view(')].strip())


if __name__=='__main__':unittest.main(verbosity=2)
