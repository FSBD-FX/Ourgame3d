from pathlib import Path
P=Path(__file__).resolve().parent
source=(P/'prompts/62-common-base-primary2.txt').read_text('utf-8')
source=source.replace('sword-primary2','sword-primary3').replace('low preparatory fist, torso turned back, raised forward swing, overhead extended arm, high returning arm, guard return','high side preparation, overhead raised preparation, downward turning execution, low forward followthrough, low returning arm, guard return')
path=P/'prompts/67-common-base-primary3.txt';assert not path.exists();path.write_text(source,'utf-8')
for number,key in enumerate(['LGT','MED','HVY','ROB'],68):
    old=number-5
    source=(P/f'prompts/{old}-{key}-primary2-same-pose-source.txt').read_text('utf-8')
    source=source.replace('sword-primary2','sword-primary3').replace('low preparatory fist, torso turned back, raised forward swing, overhead extended arm, high returning arm, guard return','high side preparation, overhead raised preparation, downward turning execution, low forward followthrough, low returning arm, guard return')
    path=P/f'prompts/{number}-{key}-primary3-same-pose-source.txt';assert not path.exists();path.write_text(source,'utf-8')
print('Prepared five P3 prompts, no calls made.')
