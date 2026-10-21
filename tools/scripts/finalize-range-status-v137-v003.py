"""Preserve failed v002 evidence; recognize actual ZIP retention index name."""
from pathlib import Path
old=Path('F:/Ourgame/tools/scripts/finalize-range-status-v137-v002.py').read_text(encoding='utf-8')
assert old.count("source-preparation-status-v137-v002")==1
assert old.count("['source-size-SHA256.json','retention-verification-v001.json']")==1
code=old.replace('source-preparation-status-v137-v002','source-preparation-status-v137-v003').replace("['source-size-SHA256.json','retention-verification-v001.json']","['source-size-SHA256.json','E-retention-index-v001.json','retention-verification-v001.json']")
assert code.count('report=dict(schema=')==1
code=code.replace('report=dict(schema=',"state.update(Dodge_known_defect='241 exact EDIT protection failed, protected0/3 foregroundRGBA drift99.29/99.32percent; phase1/2 belt-anchored artist target residual22.53/24.66sourcepx, minimax11.50/12.66with buckle displacement. Root viewed E509 full/torso/controls/fixed72 and allows finite native preparation only; original gates remain failed.',Dodge_limited_source_preparation_allowed=True,Root_Dodge32_source_review=pin(H/'Root-Dodge32-finite-source-review-native-preparation-v001.json'),next='Prepare actual Dodge32 finite optional native candidate preserving failures; prioritize Death40 real terminal-state integration and genuine enemy fatal-hit bilateral proof. No additional native generation this turn.')\nreport=dict(schema=")
exec(compile(code,__file__,'exec'))
