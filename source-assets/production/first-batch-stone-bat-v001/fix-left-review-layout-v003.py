"""Mirror each diagnostic cell, retaining play order; original v002 pages retained."""
from pathlib import Path
import importlib.util,json
from PIL import Image
P=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('record_wrapper',P/'production-record.py');w=importlib.util.module_from_spec(s);s.loader.exec_module(w);r=w.r
rows=[]
for action in['wake','wing','hurt','death','peck']:
 src=P/f'reviews/{action}-origin-assembled-right-v002.png';im=Image.open(src).convert('RGBA');out=Image.new('RGBA',im.size)
 for y in range(0,im.height,512):
  for x in range(0,im.width,512):out.alpha_composite(im.crop((x,y,x+512,y+512)).transpose(Image.Transpose.FLIP_LEFT_RIGHT),(x,y))
 q=P/f'reviews/{action}-origin-assembled-left-v003.png';assert not q.exists();out.save(q);r.archive(q,q.relative_to(P),'correct_percell_left_mirror_diagnostic_play_order_preserved_source_PNG_unchanged')
 rows.append({'action':action,'path':str(q),'sha256':r.sha(q),'source_right_preview':str(src),'source_sha256':r.sha(src)})
j=P/'reviews/bat-subset-v002-preview-errata-v001.json';assert not j.exists();r.write(j,{'schema':'bat_preview_layout_errata_v1','manifest':str(P/'manifests/import-stone-bat-subset-v002.json'),
 'manifest_sha256':r.sha(P/'manifests/import-stone-bat-subset-v002.json'),'problem':'v002left_contact_pages_mirrored_whole_atlas_so_columns_reverse; unsuitable_for_left_temporal_order_review',
 'scope':'diagnostic_page_only; frozen_individual_right_PNGs_and_manifest_play_order_and_runtime_mirror_policy_are_unchanged',
 'corrected_left_contact_pages':rows,'new_generation_calls':0,'runtime_verified':False});r.archive(j,j.relative_to(P),'explicit_diagnostic_only_mirror_page_order_correction_not_changed_frozen_contract');print(json.dumps({'errata':str(j),'sha256':r.sha(j)}))
