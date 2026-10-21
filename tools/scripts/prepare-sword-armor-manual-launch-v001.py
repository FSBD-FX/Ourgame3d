from pathlib import Path
R=Path('F:/Ourgame');T=R/'tools/scripts'
s=(T/'launch-fairytale-sword-body-v002.ps1').read_text(encoding='utf-8-sig')
for a,b in [('verify-fairytale-sword-body-v002.py','verify-sword-armor-ready-v001.py'),('Imported V002 body trial preflight failed.','Imported Ready armor24 trial preflight failed.'),('play-fairytale-sword-body-v002-','play-fairytale-sword-armor-ready-v001-'),("'-DungeonFairytaleSwordBodyV002Preview',","'-DungeonFairytaleSwordBodyV002Preview', '-DungeonFairytaleSwordArmorReadyPreview',"),('Low-guard sword body V002 preview started:','Ready-only chest and shoulders preview started:'),('Only Ready and grounded first primary use V002 sword art. Other states use Ready0/noSword placeholders; armor and full combos remain unfinished.','Chest and shoulders are trial Ready-only layers. They disappear during attack because matching attack armor is unfinished. Other states remain placeholders; real equipment IDs, complete states and combos are unfinished.')]:s=s.replace(a,b)
p=T/'launch-fairytale-sword-armor-ready-v001.ps1';assert not p.exists();p.write_text(s,encoding='utf-8')
c=R/'钟盔军剑胸肩试装.cmd';assert not c.exists()
c.write_text('@echo off\nchcp 65001 >nul\npwsh.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0tools\\scripts\\launch-fairytale-sword-armor-ready-v001.ps1"\nif errorlevel 1 pause\n',encoding='utf-8')
print('Prepared explicit Ready-only armor manual launcher; not executed')
