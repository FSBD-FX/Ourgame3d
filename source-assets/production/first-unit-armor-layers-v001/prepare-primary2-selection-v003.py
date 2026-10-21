from pathlib import Path
P=Path(__file__).resolve().parent
source=(P/'extract-primary2-four-armors-v002.py').read_text('utf-8')
source=source.replace('components/primary2-four-armors-v002','components/primary2-four-armors-v003').replace('primary2-four-armors-candidate-v002.json','primary2-four-armors-candidate-v003.json')
source=source.replace('-{i}-v002.png','-{i}-v003.png').replace('selection-v002.png','selection-v003.png')
source=source.replace("if key=='ROB':\n                for name in ['weapon_forearm','other_forearm']:q=ImageChops.lighter(q,masks[name])", "# ROB native changed wrist/cuff geometry: do not import its wrap or invented forearm coverage.")
source=source.replace("exclusions=['head','weapon_hand','other_hand','belt','pouch']+([] if key=='ROB' else ['weapon_forearm','other_forearm'])", "exclusions=['head','weapon_hand','other_hand','belt','pouch','weapon_forearm','other_forearm']")
source=source.replace("'robe_scope':'actual_native_gray_sleeve_surface_may_cover_preserved_bare_forearm_in_far; source_wrap_material_excluded'", "'robe_scope':'only_real_torso_upper_sleeve_and_hem_outside_original_forearms; full_long_sleeve_coverage_unfulfilled'")
source=source.replace("'Native robe changes cuff position in raised poses; source-specific wrap material removed within traced arm zones. Actual sleeve/old wrist seam remains a candidate limitation, not complete clothing acceptance.'", "'ROB source changes raised forearm/cuff/wrap shape; whole traced original forearm excluded from armor. Only torso/upper-sleeve/hem candidate; full robe sleeve coverage remains unfulfilled.'")
target=P/'extract-primary2-four-armors-v003.py';assert not target.exists();target.write_text(source,'utf-8');print(target)
