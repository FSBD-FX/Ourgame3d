from pathlib import Path
P=Path(__file__).resolve().parent
source=(P/'select-primary2-ROB-sleeves-v001.py').read_text('utf-8')
source=source.replace('primary2-ROB-real-sleeves-v001','primary2-ROB-real-sleeves-v002').replace('primary2-ROB-real-sleeves-candidate-v001','primary2-ROB-real-sleeves-candidate-v002')
source=source.replace('-{i}-v001.png','-{i}-v002.png').replace('sleeves-v001.png','sleeves-v002.png')
old="""for image in [front,near,other_cloth]:
        assert all(a==b for a,b in zip(image.get_flattened_data(),source.get_flattened_data()) if a[3])
        assert ImageChops.multiply(image.getchannel('A'),forbidden).getbbox() is None"""
new="""for image in [front,near,other_cloth]:
        assert all(a==b for a,b in zip(image.get_flattened_data(),source.get_flattened_data()) if a[3])
    # Prior front was frozen against exact anatomy traces, not the new sleeve's
    # extra selection clearance. Validate both contracts explicitly.
    for image in [near,other_cloth]:
        assert ImageChops.multiply(image.getchannel('A'),forbidden).getbbox() is None
    for name in ['head','weapon_hand','other_hand','belt','pouch']:
        assert ImageChops.multiply(front.getchannel('A'),masks[name]).getbbox() is None"""
assert old in source;source=source.replace(old,new)
target=P/'select-primary2-ROB-sleeves-v002.py';assert not target.exists();target.write_text(source,'utf-8');print(target)
