from pathlib import Path
R=Path('F:/Ourgame');p=R/'tools/scripts/capture-leather-ready-trial-v001.ps1';o=R/'tools/scripts/capture-leather-primary1-trial-v001.ps1';assert not o.exists();s=p.read_text(encoding='utf-8-sig')
for a,b in [('_软皮轻甲左右待机试装_','_软皮轻甲左右第一刀试装_'),("'-DungeonFairytaleLeatherReadyPreview','-DungeonFairytaleLeatherReadyOnlyProof'","'-DungeonFairytaleLeatherReadyPreview','-DungeonFairytaleLeatherPrimary1Preview','-DungeonFairytaleLeatherPrimary1OnlyProof'")]:
 assert a in s;s=s.replace(a,b)
o.write_text(s,encoding='utf-8');print(o.as_posix())
