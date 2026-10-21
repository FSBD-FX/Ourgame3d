from pathlib import Path
P=Path(__file__).resolve().parent
source=(P/'extract-walk-four-armors-v001.py').read_text('utf-8')
source=source.replace("components/walk-four-armors-v001","components/walk-four-armors-v002")
source=source.replace("walk-four-armors-candidate-v001.json","walk-four-armors-candidate-v002.json")
source=source.replace("-{i}-v001.png","-{i}-v002.png").replace("selection-v001.png","selection-v002.png")
source=source.replace("belt = relative([(-76,-7),(-59,-14),(-9,-6),(26,-9),(32,7),(10,18),(-34,11),(-76,8)],BELTS[i])", "belt = relative([(-82,-15),(29,-18),(35,7),(17,20),(-80,14)],BELTS[i])")
corrections='''
# Actual isolated-layer review v001 found exposed elbow skin, trousers in the
# fifth hem and boot wedges below diagonal robe panels. Re-trace those surfaces;
# source RGBA remains untouched. The folded far shin in pose2 has no visible plate.
NEAR[4]=[(103,307),(118,306),(134,313),(143,329),(136,346),(125,361),
         (122,377),(110,389),(93,389),(80,382),(75,369),(79,353),(90,333),(97,317)]
SHORT_HEMS[4]=[(153,368),(216,368),(235,375),(254,375),(269,388),(260,391),
               (237,379),(212,391),(170,402),(152,388)]
MED_HEMS[4]=[(152,367),(226,367),(224,383),(212,395),(211,413),(171,415),(152,405)]
ROB_PANELS[1]=[[(267,361),(334,362),(328,390),(301,443),(275,414),(250,398)],
               [(262,365),(249,389),(222,410),(229,407),(248,395),(263,375)],
               [(347,360),(366,355),(391,422),(358,441)]]
ROB_PANELS[3]=[[(189,353),(252,352),(231,436),(174,407),(189,386)],
               [(186,362),(177,388),(158,405),(163,411),(178,395)],
               [(268,351),(293,349),(319,436),(280,444)]]
HVY_SHINS[2]=[HVY_SHINS[2][0]]
HVY_SHINS[4][0]=[(140,399),(164,401),(178,417),(169,428),(145,431)]
HVY_HEM4=[[(151,365),(169,370),(167,386),(154,393),(139,380)],
          [(173,376),(204,375),(201,403),(170,402)],
          [(208,374),(238,370),(246,394),(215,398)],
          [(245,366),(258,362),(269,385),(252,391)]]

'''
source=source.replace('\ndef poly(points):', '\n'+corrections+'def poly(points):')
source=source.replace("hems=ROB_PANELS[i] if key=='ROB' else [MED_HEMS[i] if key=='MED' else SHORT_HEMS[i]]", "hems=ROB_PANELS[i] if key=='ROB' else [MED_HEMS[i] if key=='MED' else SHORT_HEMS[i]]\n            if i==4 and key=='MED':hems += [[(239,366),(260,360),(278,388),(268,399),(247,394)]]\n            if i==4 and key=='HVY':hems=HVY_HEM4")
target=P/'extract-walk-four-armors-v002.py'; assert not target.exists();target.write_text(source,'utf-8')
print(target)
