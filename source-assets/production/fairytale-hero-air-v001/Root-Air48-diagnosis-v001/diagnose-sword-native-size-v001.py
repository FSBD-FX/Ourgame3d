"""Read existing sword before/after UE's synchronous compilation barrier; no imports/saves."""
from pathlib import Path
import hashlib,json,sys
sys.dont_write_bytecode=True
import unreal
ROOT=Path('F:/Ourgame')
OUT=Path(__file__).parent/'actual-sword-size-diagnosis.json'
OBJ='/Game/Production/FirstBatch/v002/CandidateComponents/T_military_sword_v002.T_military_sword_v002'
PKG=ROOT/'UnrealGame/Content/Production/FirstBatch/v002/CandidateComponents/T_military_sword_v002.uasset'
def pin(p):
 b=p.read_bytes();return dict(path=p.as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
before_file=pin(PKG)
t=unreal.load_asset(OBJ)
assert isinstance(t,unreal.Texture2D) and t.get_path_name()==OBJ
def facts():
 return dict(dimensions=[t.blueprint_get_size_x(),t.blueprint_get_size_y()],settings={k:str(t.get_editor_property(k)) for k in ['compression_settings','mip_gen_settings','lod_group','never_stream','srgb']})
before=facts()
unreal.SystemLibrary.execute_console_command(None,'Editor.AsyncTextureCompilationFinishAll')
after=facts()
after_file=pin(PKG)
assert before_file==after_file
d=dict(schema='Root-existing-sword-compilation-size-diagnosis-v001',before=before,after=after,package=before_file,package_unchanged=True,imports=0,saves=0,actual_source_modified=False,FinalAccepted=False)
with OUT.open('x',encoding='utf-8') as f:json.dump(d,f,ensure_ascii=False,indent=2)
unreal.log('Root sword native diagnosis '+json.dumps(d))
