from pathlib import Path
import hashlib,json
HERE=Path(__file__).resolve().parent;ROOT=Path('F:/Ourgame');BIND=HERE.parent/'UE-import-binding-candidate-v001';sha=lambda b:hashlib.sha256(b).hexdigest()
hud=(ROOT/'UnrealGame/Source/CodexDungeon/DungeonHUD.cpp').read_bytes();renderer=(BIND/'source/after-DungeonFairytaleSwordPresentation.cpp').read_bytes();assert sha(renderer)=='be8afcfce07e2c02a01481a86a819d6ea516002ccce925a74873871f2a748794'
(HERE/'before/DungeonHUD.cpp').write_bytes(hud);(HERE/'before/renderer-candidate-after.cpp').write_bytes(renderer)
def block(text,start):
 a=text.index(start);opening=text.index('{',a);depth=0
 for i in range(opening,len(text)):
  depth+=(text[i]=='{')-(text[i]=='}')
  if depth==0:return text[a:i+1]
 raise ValueError(start)
h=hud.decode('utf-8').replace('\r\n','\n');start=h.index('        if(bUseFairytaleSwordArmorPrimary1Preview)');a=h.index('            for(',start);end=h.index('ReadyArmorTextures.Add(Texture);',a)+len('ReadyArmorTextures.Add(Texture);');loop=h[a:end]+'\n'
r=renderer.decode('utf-8').replace('\r\n','\n');resolver=block(r,'UTexture2D* ADungeonHUD::GetFairytaleSwordArmorPrimary1Texture(')+'\n'
p=(HERE/'before/v001-projected-DungeonHeroLandingPriorityProbeV001.cpp').read_text(encoding='utf-8');primary=block(p,'  {for(int32 Frame=0;Frame<6;++Frame)for')+'\n'
for name,text in [('actual-hud-primary1-loop.inc',loop),('actual-primary1-resolver.inc',resolver),('actual-old-primary1-readback-loop.inc',primary),('legacy-preload-under-test.inc','// Missing old fourteen preload for RED.\n')]: (HERE/'tests'/name).write_text(text,encoding='utf-8')
(HERE/'reports/host-fixture-pins.json').write_text(json.dumps({'actual_hud_source_sha256':sha(hud),'frozen_renderer_candidate_sha256':sha(renderer),'fixture_uses_actual_hud_loop':True,'fixture_uses_actual_renderer_resolver':True,'fixture_uses_actual_old_required_loop':True,'not_base115_model':True},indent=2)+'\n',encoding='utf-8')
print(json.dumps({'actual_hud_loop_resolver_and_old_readback_extracted':True,'UE_run':False}))
