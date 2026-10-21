"""Restrict a source-pixel component bake to common opaque surfaces only."""
from pathlib import Path
P=Path(__file__).resolve().parent
text=(P/'trial-loading-shared-native-panel-v001.py').read_text('utf-8')
text=text.replace("out=P/'decomposition-trials/loading-shared-panel-v001'","out=P/'decomposition-trials/loading-shared-panel-v002'")
text=text.replace('loading-shared-panel-contact-v001.png','loading-shared-panel-contact-v002.png')
text=text.replace("mask=Image.new('L',(512,512),0);ImageDraw.Draw(mask).polygon(poly,fill=255)",
 "mask=Image.new('L',(512,512),0);ImageDraw.Draw(mask).polygon(poly,fill=255)\ncommon=ImageChops.multiply(base.getchannel('A').point(lambda a:255 if a==255 else 0),shared.getchannel('A').point(lambda a:255 if a==255 else 0))\nmask=ImageChops.multiply(mask,common)")
text=text.replace("outside_changed=sum(1", "assert canvas.getchannel('A').tobytes()==base.getchannel('A').tobytes()\noutside_changed=sum(1")
text=text.replace("'semantic_material_selection_review_pending':True", "'semantic_material_selection_review_pending':True,'entire_source90_alpha_unchanged':True,'every_replacement_pixel_from_actual_opaque_source89':True")
out=P/'trial-loading-shared-native-panel-v002.py';assert not out.exists();out.write_text(text,'utf-8');print(out)
