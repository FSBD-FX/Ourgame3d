from pathlib import Path
R=Path('F:/Ourgame');T=R/'tools/scripts'
def new(p,s):
 assert not p.exists(),p
 if p.suffix=='.py':compile(s,str(p),'exec')
 p.write_text(s,encoding='utf-8')
ps=(T/'verify-sword-armor-ready-v001.ps1').read_text(encoding='utf-8-sig')
ps=ps.replace('[int]$Version=1','[int]$Version=2')
needle="$index['status']='native_pixel_and_normal_input_checks_passed_visual_review_pending'"
assert needle in ps
ps=ps.replace(needle,"""& $python -B -X utf8 (Join-Path $PSScriptRoot 'verify-ready-body-pixel-presence-v001.py') --archive $archive
if($LASTEXITCODE -ne 0){throw 'Visible Ready helmet presence failed; native originals retained.'}
$index['status']='native_pixels_real_input_and_visible_ready_head_passed_art_review_pending'""")
new(T/'verify-sword-armor-ready-v002.ps1',ps)
s=(T/'postprocess-sword-armor-ready-v001.py').read_text(encoding='utf-8-sig')
for a,b in [('2026-10-16_钟盔军剑低位胸肩真实按键试装_v001','2026-10-16_钟盔军剑低位胸肩真实按键试装_v002'),('2026-10-16_SwordReadyArmor24-actual126GREEN-v100','2026-10-16_SwordReadyArmor24-preloadFix-actual126GREEN-v101'),('v100-source-binding-audit-v001.json','v101-source-binding-audit-v001.json'),('postprocess-sword-armor-ready-v001.py','postprocess-sword-armor-ready-v002.py'),('Native158/159 lowguard actual normal-input trial, v099 Source/DLL.','Native158/159 lowguard and161/162/163 Ready-only armor actual normal-input trial, v101 Source/DLL. Attack armor remains absent by design.'),('source_native_movies\':174','source_native_movies\':len(frames)'),('native_original_including_prewarm\':175','native_original_including_prewarm\':len(frames)+1')]:s=s.replace(a,b)
s=s.replace("assert len(rows)==len(frames)==174 and len(list(O.glob('*.png')))>=175","assert len(rows)==len(frames) and len(frames)>120 and len(list(O.glob('*.png')))==len(frames)+1")
s=s.replace("assert load(O/'sword-armor-runtime-verification.json')['kernel_phase_sampling_exact']","assert load(O/'sword-armor-runtime-verification.json')['kernel_phase_sampling_exact']\nassert load(O/'visible-ready-head-gate-v001.json')['passed']")
new(T/'postprocess-sword-armor-ready-v002.py',s)
print('New postfix wrapper and postprocessor prepared; failurev001 unchanged')
