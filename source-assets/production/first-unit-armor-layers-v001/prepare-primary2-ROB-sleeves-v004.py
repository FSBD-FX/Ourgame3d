from pathlib import Path
P=Path(__file__).resolve().parent
source=(P/'select-primary2-ROB-sleeves-v003.py').read_text('utf-8')
source=source.replace('primary2-ROB-real-sleeves-v003','primary2-ROB-real-sleeves-v004').replace('primary2-ROB-real-sleeves-candidate-v003','primary2-ROB-real-sleeves-candidate-v004')
source=source.replace('-{i}-v003.png','-{i}-v004.png').replace('sleeves-v003.png','sleeves-v004.png')
polygons='''
# Actual source arm-only contours end at wrists. The full anatomical hand outline
# is larger than a garment extent and otherwise catches robe hem below the fist.
ARM_CLOTH_ENVELOPES=[
 [(156,305),(174,303),(191,313),(205,329),(211,346),(199,354),(181,344),(165,330),(155,316)],
 [(121,284),(144,283),(157,297),(157,317),(152,332),(123,332),(116,319),(118,299)],
 [(214,245),(232,237),(255,235),(279,232),(296,231),(302,242),(299,258),(282,274),(258,282),(231,286),(215,276)],
 [(132,178),(140,156),(155,143),(173,146),(182,160),(180,184),(171,207),(171,225),(152,231),(138,220),(132,202)],
 [(118,199),(128,187),(145,188),(159,200),(165,219),(157,241),(142,251),(126,244),(116,231)],
 [(115,259),(125,243),(143,246),(157,258),(165,276),(160,292),(148,300),(130,300),(116,290),(112,276)]]
OTHER_CLOTH_ENVELOPES=[
 [(277,302),(293,304),(306,315),(314,328),(311,342),(295,345),(283,333),(275,318)],
 [(260,308),(273,297),(290,295),(302,304),(305,321),(294,337),(280,345),(266,334),(258,322)],
 [(266,292),(279,289),(285,298),(283,316),(274,329),(263,322),(260,307)],
 [(268,303),(280,304),(286,315),(285,332),(275,337),(267,325),(263,313)],
 [(267,284),(280,278),(286,287),(283,305),(273,311),(264,300)],
 [(266,298),(279,289),(285,300),(283,319),(273,326),(264,314)]]

'''
source=source.replace("prior=P/'manifests/import-armor-primary2-four-v001.json'",polygons+"prior=P/'manifests/import-armor-primary2-four-v001.json'")
source=source.replace("selection={name:masks[name].filter(ImageFilter.MaxFilter(15)) for name in ['weapon_forearm','other_forearm']}", "selection={'weapon_forearm':tr.w.poly(ARM_CLOTH_ENVELOPES[i]),'other_forearm':tr.w.poly(OTHER_CLOTH_ENVELOPES[i])}")
source=source.replace("if px[x,y] and hp[x,y] and rr>200", "if px[x,y] and rr>200")
source=source.replace("'Only actual visible cloth, no hidden full garment or limb skeleton invented.'", "'Only actual visible cloth, no hidden full garment or limb skeleton invented. Source pose0 has a narrow actual bare-skin gap at cuff; it is excluded from the cloth layer and original common skin remains. Full wrist-covering robe appearance is not asserted.'")
target=P/'select-primary2-ROB-sleeves-v004.py';assert not target.exists();target.write_text(source,'utf-8');print(target)
