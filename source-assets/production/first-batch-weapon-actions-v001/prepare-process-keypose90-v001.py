from pathlib import Path
P=Path(__file__).resolve().parent
source=(P/'process-single-mechanical-keyposes-v001.py').read_text('utf-8')
source=source.replace('for number in [87,88,89]:','for number in [90]:')
source=source.replace("if x['request_number']==89","if x['request_number']==90")
source=source.replace('XBW-mechanical-contact-89-native-crop-v001.png','XBW-mechanical-contact-90-native-crop-v001.png')
out=P/'process-single-mechanical-keypose90-v001.py';assert not out.exists();out.write_text(source,'utf-8');print(out)
