"""Prepare only a pinned Root-executed Hurt32 import candidate. No UE invocation."""
from pathlib import Path
import hashlib,json
ROOT=Path('F:/Ourgame').resolve()
HERE=Path(__file__).resolve().parent
OUT=HERE/'prepared-v002'
def fact(p):
 p=Path(p).resolve();b=p.read_bytes();return {'path':p.as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,v):
 with Path(p).open('x',encoding='utf-8',newline='\n')as f:f.write(v)
def frozen(p,sha):
 r=fact(p)
 if r['sha256']!=sha:raise ValueError('Frozen prerequisite changed: '+str(p))
 return r
v1=HERE.parent/'hurt-runtime-prepared-v001/prepared-v001'
guard=ROOT/'source-assets/production/fairytale-guard-v001/root-full-registration-v001'
manifest=frozen(v1/'import-Hurt32-v001.json','bca13780eec91568e53609e366aa06b201efeeed9256c53ef83d6a6d2ad9eb1f')
profile=frozen(v1/'Hurt-runtime-profile-data-v001.json','108bae16b479dc466feee9885875be9e5655482fb7a96ab29863c7ff127a1af3')
lock=frozen(v1/'Hurt-source-review-lock-and-32-source-proof-v001.json','e8ae64a02e443becbfafb4f10594cdd284ef9ba4345b6522c4647a29ab209a92')
oldmanifest=frozen(guard/'import-manifest.json','db45cd90f253ccd33986915db1fa67f40fab95260fb04bfffd7e866d79252fbb')
oldverify=fact(guard/'independent-import-verification-v001.json')
oldreceipt=read(oldverify['path'])['receipt']
if fact(oldreceipt['path'])!=oldreceipt:raise ValueError('Guard actual receipt differs')
oldnative=read(oldreceipt['path'])
settings=oldnative['assets'][0]['actual_settings']
if any(a['actual_settings']!=settings for a in oldnative['assets']):raise ValueError('Proven Guard UI settings are inconsistent')
m=read(manifest['path'])
OUT.mkdir(exist_ok=False)
cfg={
 'schema':'Hurt32-native-import-validator-candidate-v002','namespace':m['namespace'],
 'import_manifest':manifest,'profile':profile,'source_review_lock':lock,
 'old_guard_manifest':oldmanifest,'old_guard_independent_verification':oldverify,'old_guard_actual_receipt':oldreceipt,
 'proven_native_importer':fact(ROOT/'tools/scripts/ue-import-guard-full28-v001.py'),
 'proven_powershell_launcher':fact(ROOT/'tools/scripts/import-guard-full28-v001.ps1'),
 'expected_old_count':1254,'expected_new_count':32,'expected_final_count':1286,
 'old1254_basis':'Pinned old1226 inventory plus pinned actual saved Guard28 receipt; exact Production file set and byte/SHA twice.',
 'manifest_texture_settings':m['texture_settings'],'expected_native_settings_raw':settings,
 'filter_authority':'Proven Guard full28 TF_BILINEAR; original Hurt manifest UI settings unchanged.',
 'known_optional_empty':[{'component':'FarHandForeground','frame':i}for i in [1,2,3]],
 'source_RGBA_authority':'Host decoded exact PNG; native GPU/source-mip RGBA has not been queried.',
 'validation_directory':(HERE/'validation-runs').as_posix(),
 'actual_import_performed':False,'actual_import_receipt':None,'independent_native_verification_receipt':None,
 'actual_preload_finish_receipt':None,'actual_runtime_receipt':None,'FinalAccepted':False
}
config=OUT/'import-validator-config-v002.json'
write(config,json.dumps(cfg,ensure_ascii=False,indent=2)+'\n')
template=(HERE/'ue-import-Hurt32-v002.template.py').read_text(encoding='utf-8')
rendered=template.replace('__CONFIG_PATH__',config.as_posix()).replace('__CONFIG_SHA__',fact(config)['sha256'])
compile(rendered,str(OUT/'ue-import-Hurt32-v002.py'),'exec')
write(OUT/'ue-import-Hurt32-v002.py',rendered)
write(OUT/'import-Hurt32-v002.ps1',(HERE/'import-Hurt32-v002.template.ps1').read_text(encoding='utf-8'))
write(OUT/'HANDOFF.md', '''# Hurt32 import candidate v002

Only the existing E454 reviewed 32 source PNGs are selected: five exclusive body owners and three LGT parts, four frames each. No WholeBody, proof composite, sword copy, or regenerated art is imported. The accepted independent sword stays reused.

FarHandForeground frames 1–3 are deliberately all-transparent original owners. All 32 Texture2D objects must load at 512×512; only those three may have zero alpha. Rendering skips their empty draw slots (9 / 8 / 8 / 8 nonempty layers including the sword). Do not apply a blanket used-pixels > 0 gate.

Default `import-Hurt32-v002.ps1` performs host-only checks. Root may explicitly pass `-ExecuteNative` after retaining/reviewing this candidate and closing UE/UBT. This uses the proven hidden editor launch, no-overwrite tasks, exact destination names, native class/dimension/source filename/UI-setting readback, saved package pins, registry exact32, and independent host verification. Failed or partial results are preserved; there is no cleanup or overwrite retry. Old1254 must remain byte/SHA unchanged twice; expected final Production file count is 1286. v017/HeroLeatherHurt must be physically and registry empty before import.

Native import records the exact absolute source filename and host decoded RGBA hash, not a measurement of UE GPU/source-mip pixels. Texture settings are TC_EDITOR_ICON, TMGS_NO_MIPMAPS, TEXTUREGROUP_UI, never_stream, sRGB, and proven TF_BILINEAR. Explicit destination names prevent identical frame-0.png basenames from colliding.

Preload/finish recommendation for the HUD owner: load and retain all 32 objects, including the three empty owners, alongside the reused sword. Add the 32 selected textures to the existing WITH_EDITOR FTextureCompilingManager::Get().FinishCompilation(...) path and FlushRenderingCommands before the first Hurt draw, following the current Ready/Guard path. Importer object-load success alone does not prove compilation or first-draw readiness; obtain a separate actual preload/finish and native room receipt.

This package does not activate Hurt, change its kernel clock, or certify motion/foot lock/no pop. The original profile remains 416→72, sword .50, authored per-frame axes/grips and ground roots, nine stack slots, four 100 ms nonloop samples with actual Hurt-state authority. Source QA warnings and Hurt1 buckle / Ready join residuals remain preserved in the v001 source lock. Config actual import / preload / runtime receipts remain null until Root performs and records them separately.
''')
freeze={'schema':'Hurt32-import-validator-prepared-freeze-v002','files':[fact(p)for p in sorted(OUT.iterdir())],
 'preparer':fact(__file__),'templates':[fact(HERE/n)for n in ['ue-import-Hurt32-v002.template.py','import-Hurt32-v002.template.ps1']],
 'actual_import_receipt':None,'actual_preload_finish_receipt':None,'actual_runtime_receipt':None,'FinalAccepted':False}
write(OUT/'prepared-package-freeze-v002.json',json.dumps(freeze,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'prepared':OUT.as_posix(),'files':len(list(OUT.iterdir())),'freeze':fact(OUT/'prepared-package-freeze-v002.json'),'UE_started':False},ensure_ascii=False))
