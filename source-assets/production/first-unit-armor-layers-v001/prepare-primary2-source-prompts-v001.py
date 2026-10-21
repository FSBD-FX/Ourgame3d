from pathlib import Path
P=Path(__file__).resolve().parent
DESIGNS={
 'LGT':"flexible warm brown padded leather outer coat: broad stitched padded chest panels, low soft rounded shoulder flaps, short split upper-thigh front/back hem. No chainmail, metal breastplate, shin plates or long robe.",
 'MED':"medium armor: muted deep teal short surcoat with a narrow ochre vertical chest stripe; actual iron ringmail at neck, sleeves and lower-thigh hem; rounded steel shoulder caps edged in muted brass. No heavy horizontal chestbar, square plate skirt or full-length robe.",
 'HVY':"heavy armor: rigid warm-iron breastplate with one horizontal dark doorbar across the chest and muted brass end brackets; broad angular layered squared pauldrons; short segmented plate skirt and steel shin guards over the original leg poses. No robe, teal surcoat, ringmail chest or rounded leather padding. Preserve the original boots outside actually worn shin plates.",
 'ROB':"smokegray straight split long robe: soft gray torso and narrow sleeves, muted orange inner lining and cuff edges, single small pale candle chest emblem, long divided front/back cloth panels ending above the boots. Keep the same enclosed round helmet; no hood, metal shoulder caps or steel breastplate. Follow the actual turned torso and raised arm poses, do not let robe invent new legs or cover fists."
}
for number,key in enumerate(['LGT','MED','HVY','ROB'],63):
 text=f'''Use case: precise-object-edit. Asset type: six fixed-canvas same-pose armor source frames for later actual visible-garment selection.
Edit Image1 ONLY so its SAME six exact sword-primary2 poses wear ARM-{key}-001 from Image2. Image1 is the immutable pose/cell/scale/camera/head/hands/legs/boots template; Image2 supplies ONLY clothing design and material. EXACT1536x1024 output, two rows of three512cells, no recentering, resizing, rearrangement or new poses. This is a full-body SAME-POSE SOURCE, not an isolated/recentered costume.

Replace Image1's plain under-vest with Image2's {DESIGNS[key]} Keep the original waist belt, buckle and small pouch once, at the actual Image1 coordinates. Keep the plain ochre under-sleeves only where they genuinely remain uncovered by the new wearable. Distinct garment edges must permit actual armor-surface masks later; don't draw a duplicate body or fake transparent clothing.

The actual six Image1 poses stay unchanged: low preparatory fist, torso turned back, raised forward swing, overhead extended arm, high returning arm, guard return. Shoulders/sleeves follow those exact real upper-arm angles, never neutralidle or a substitute punch loop. Preserve every empty gripping fist and bluegray wrist wrap at its original coordinate. No sword, handle, hilt, shield, magic, FX, shadows or floor.

Keep the identical round steel enclosed helmet, brass brow, dark faceplate slit and small amber eyes. No visible human face or hair; no helmet redesign. Same squat2.6-head proportions,3/4-right fixed side camera, bold handpainted outlines and celshade. Adding armor must not change head/boot positions or body height. Solid flat exact#FF00FF background, no magenta materials. No grid lines, borders, labels, marks or text. Full original figures remain safely within their original512cells and original support boots/groundline. Only outer clothing changes.
'''
 path=P/f'prompts/{number}-{key}-primary2-same-pose-source.txt';assert not path.exists();path.write_text(text,'utf-8')
print('Prepared four P2 native source prompts, no calls made.')
