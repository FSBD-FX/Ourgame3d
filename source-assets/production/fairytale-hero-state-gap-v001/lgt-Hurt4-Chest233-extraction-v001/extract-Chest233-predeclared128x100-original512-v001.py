from pathlib import Path
import ast
BASE=Path('F:/Ourgame/source-assets/production/fairytale-hero-state-gap-v001')
SOURCE=BASE/'lgt-hurt4-far231-extraction-v001/extract-Far231-shared-original256-v001.py'
code=SOURCE.read_text(encoding='utf-8')
changes=[
 ("STATE='leather_farshoulder_hero_hurt'","STATE='leather_chest_hero_hurt_correction'"),
 ("RUN=HERE/'run-Hurt4-far-native231-shared-HD-v001'","RUN=HERE/'run-Hurt4-Chest-native233-shared-HD-v001'"),
 ("MEDIA=ROOT/'过程图稿与视频/2026-10-18_钟盔Hurt远肩薄tab231共享四相标准提取_v001'","MEDIA=ROOT/'过程图稿与视频/2026-10-18_钟盔Hurt胸衣233统一128x100共享四相标准提取_v001'"),
 ("inp=BASE/'lgt-hurt4-far-correction-standard-input-v002/prepared-input-v002'","inp=BASE/'lgt-Hurt4-Chest233-correction-standard-input-v003/prepared-input-v003'"),
 ("Root-Far-Hurt4-thin-tab-no-gold-correction-input-handoff-v002.json","Root-Chest233-unified-fourphase-source-correction-handoff-v003.json"),
 ("generation-request231-v001.json","generation-request233-v001.json"),
 ("b853ac48f3e446eb7809e0f12608dc058b129826db43f136924db918584627ce","b87d65d627a9884306360da6fd75d02cb05a1daa38b04001d49c60ab7f3210f7"),
 ("1212294","1346957"),
 ("2026-10-18-OurgameUE-LGT-Hurt-far231-raw-v437",next(Path('E:/OurGame/Knight/过程图稿与视频').glob('*v452/source-size-SHA256.json')).parent.name),
 ("Exact Root v003 prompt used by actual native231, not stale v002 ordinal prelude","Exact formal128x100-fourphase prompt used by actual native233; all prepared inputs preserved"),
 ("'--min-used-pixels','256'","'--min-used-pixels','512'"),
 ("'schema':'Far231-original32x30-shared-extraction-v001','native':231","'schema':'Chest233-predeclared128x100-original512-shared-extraction-v001','native':233"),
 ("'Root_E437_notification_received'","'Root_E452_notification_received'"),
 ("'raw_semantic_review':'Correct narrow curved brown thin tab; no230 gold rivet, broad cup or strap. Source candidate only, fit and QA unknown before commands.'","'raw_semantic_review':'Four samebrownvest/pouch perspectives withgreenarm/neckapertures. Phase1hasstrongerdiagonaltilt. Actualposefit/densitynotyetaccepted.'"),
 ("'original_v002_prompt_preserved'","'original_formal_v003_prompt_preserved'"),
 ("'fit_window':[32,30],'extract_and_compose_min_used_pixels':256","'fit_window':[128,100],'extract_and_compose_min_used_pixels':512"),
 ("'schema':'Far231-extracted-files-freeze-v001'","'schema':'Chest233-extracted-files-freeze-v001'"),
 ("'topic':'Hurt远肩薄tab231共享四相标准提取'","'topic':'Hurt胸衣233统一128x100共享四相标准提取'"),
 ("RuntimeError(stage+' failed; original256 gate retained')","RuntimeError(stage+' failed; original512 gate retained')")]
for before,after in changes:
 assert before in code,before;code=code.replace(before,after)
tree=ast.parse(code);tree.body=[n for n in tree.body if not isinstance(n,ast.If)]
scope={'__file__':str(Path(__file__).resolve()),'__name__':'Chest233_independent_shared_original512_extraction'}
exec(compile(tree,str(Path(__file__).resolve()),'exec'),scope)
scope['main']()
