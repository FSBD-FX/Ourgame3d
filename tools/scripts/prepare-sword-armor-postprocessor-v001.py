from pathlib import Path
R=Path('F:/Ourgame');T=R/'tools/scripts'
s=(T/'postprocess-sword-real-input-v002.py').read_text(encoding='utf-8-sig')
for a,b in [('2026-10-16_钟盔军剑低位真实按键双向动作_v001','2026-10-16_钟盔军剑低位胸肩真实按键试装_v001'),('2026-10-16_LowGuard158159-actual126GREEN-v099','2026-10-16_SwordReadyArmor24-actual126GREEN-v100'),('sword-runtime-verification.json','sword-armor-runtime-verification.json'),('v099-source-binding-audit-v001.json','v100-source-binding-audit-v001.json'),('fairytale-sword-lowguard-normal-input-silent.mp4','fairytale-sword-lowguard-armor-ready-silent.mp4'),('postprocess-sword-real-input-v002.py','postprocess-sword-armor-ready-v001.py')]:s=s.replace(a,b)
p=T/'postprocess-sword-armor-ready-v001.py';assert not p.exists();compile(s,str(p),'exec');p.write_text(s,encoding='utf-8')
print('New postprocessor prepared; prior tool and evidence untouched')
