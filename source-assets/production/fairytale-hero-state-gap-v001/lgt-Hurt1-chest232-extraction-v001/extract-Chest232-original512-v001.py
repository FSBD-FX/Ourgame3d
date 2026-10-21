from pathlib import Path
import ast
BASE=Path('F:/Ourgame/source-assets/production/fairytale-hero-state-gap-v001')
SOURCE=BASE/'lgt-hurt4-far231-extraction-v001/extract-Far231-shared-original256-v001.py'
code=SOURCE.read_text(encoding='utf-8')
replacements=[
 ("STATE='leather_farshoulder_hero_hurt'","STATE='leather_chest_hero_hurt1_correction'"),
 ("RUN=HERE/'run-Hurt4-far-native231-shared-HD-v001'","RUN=HERE/'run-Hurt1-Chest-native232-HD-v001'"),
 ("MEDIA=ROOT/'过程图稿与视频/2026-10-18_钟盔Hurt远肩薄tab231共享四相标准提取_v001'","MEDIA=ROOT/'过程图稿与视频/2026-10-18_钟盔Hurt1胸衣232单帧标准提取_v001'"),
 ("inp=BASE/'lgt-hurt4-far-correction-standard-input-v002/prepared-input-v002'","inp=BASE/'lgt-Hurt1-chest-source-correction-standard-input-v001/prepared-input-v001'"),
 ("Root-Far-Hurt4-thin-tab-no-gold-correction-input-handoff-v002.json","Root-Hurt1-Chest-minimal-source-correction-input-handoff-v001.json"),
 ("generation-request231-v001.json","generation-request232-v001.json"),
 ("b853ac48f3e446eb7809e0f12608dc058b129826db43f136924db918584627ce","1ec312c38f570f46c13b1abf448d3571be08be1de549b44295db702842f37aa9"),
 ("1212294","1278416"),
 ("2026-10-18-OurgameUE-LGT-Hurt-far231-raw-v437",next(Path('E:/OurGame/Knight/过程图稿与视频').glob('*v442/source-size-SHA256.json')).parent.name),
 ("Exact Root v003 prompt used by actual native231, not stale v002 ordinal prelude","Exact official single-pose prompt used by actual native232; prepared inputs preserved"),
 ("'--min-used-pixels','256'","'--min-used-pixels','512'"),
 ("'schema':'Far231-original32x30-shared-extraction-v001','native':231","'schema':'Chest232-original90x90-single-extraction-v001','native':232"),
 ("'Root_E437_notification_received'","'Root_E442_notification_received'"),
 ("'raw_semantic_review':'Correct narrow curved brown thin tab; no230 gold rivet, broad cup or strap. Source candidate only, fit and QA unknown before commands.'","'raw_semantic_review':'Same brownvest/pouch; actual neararm opening shows puregreen negative space. Neck interior remains dark. Pose compatibility and fourphasephysicaldensity notyetaccepted.'"),
 ("'original_v002_prompt_preserved'","'original_prepared_prompt_preserved'"),
 ("'fit_window':[32,30],'extract_and_compose_min_used_pixels':256","'fit_window':[90,90],'extract_and_compose_min_used_pixels':512"),
 ("im.size==(2172,724)","im.size==(1254,1254)"),
 ("row['frames']==4","row['frames']==1"),
 ("for i in range(4):","for i in range(1):"),
 ("'schema':'Far231-extracted-files-freeze-v001'","'schema':'Chest232-extracted-files-freeze-v001'"),
 ("'topic':'Hurt远肩薄tab231共享四相标准提取'","'topic':'Hurt1胸衣232单帧标准提取'"),
 ("RuntimeError(stage+' failed; original256 gate retained')","RuntimeError(stage+' failed; original512 gate retained')")]
for before,after in replacements:
 assert before in code,before;code=code.replace(before,after)
tree=ast.parse(code);tree.body=[n for n in tree.body if not isinstance(n,ast.If)]
scope={'__file__':str(Path(__file__).resolve()),'__name__':'Chest232_independent_original512_extraction'}
exec(compile(tree,str(Path(__file__).resolve()),'exec'),scope)
# E folder naming is resolved from actual E442 manifest, not an assumed translated label.
fn=scope['main']
fn()
