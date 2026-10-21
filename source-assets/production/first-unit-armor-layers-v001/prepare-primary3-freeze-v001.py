from pathlib import Path
import ast
P=Path(__file__).resolve().parent
source=(P/'freeze-primary2-four-armors-v001.py').read_text('utf-8')
source=source.replace('primary2','primary3').replace('primary_2','primary_3').replace('P2','P3')
source=source.replace('extract-primary3-four-armors-v003.py','extract-primary3-four-armors-v002.py').replace('primary3-four-armors-candidate-v003.json','primary3-four-armors-candidate-v002.json')
source=source.replace("['head','weapon_forearm','other_forearm','weapon_hand','other_hand']:assert tr.w.sel.extract(base", "['head','weapon_hand','other_hand']:assert tr.w.sel.extract(base")
source=source.replace('range(62,67)','range(67,72)').replace('[.15,.12,.27]','[.22,.12,.32]')
source=source.replace("'head_hands_forearms_original_within_explicit_trace':True", "'head_hands_original_within_explicit_trace':True,'base_forearms_source':'native67_actual_same_pose_not_synthesized_or_rescaled'")
source=source.replace("'traced_original_head_hands_forearms_preserved':True", "'traced_original_head_hands_preserved':True,'base_forearms_from_native67':True")
source=source.replace("'Original bare forearm preservation is a conservative partial contract only, not a permanent requirement; later actual sleeve layers may cover it while preserving original hands/grips.'", "'Current torso-only sleeve boundary is a partial contract, not a permanent bare-forearm requirement. Later real sleeve layers may cover native67 same-pose forearms while preserving original hands/grips.'")
source=source.replace("['v001_mail_trouser_gap_and_ROB_source_wrap','v002_ROB_wrap_color_classifier_insufficient']", "['v001_low_followthrough_trouser_wedges_and_robe_boot_edges']")
target=P/'freeze-primary3-four-armors-v001.py';assert not target.exists();ast.parse(source);target.write_text(source,'utf-8');print(target)
