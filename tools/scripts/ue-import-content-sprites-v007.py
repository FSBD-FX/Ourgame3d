"""Import only six round-helmet opposite-step walk frames, preserving v006."""
from pathlib import Path
import hashlib
import runpy
root=Path(__file__).resolve().parents[2]
manifest=root/'source-assets/production/first-unit-animation-v003/import-subset-v007.json'
assert hashlib.sha256(manifest.read_bytes()).hexdigest()=='3a35ea2aacde0115947daf4b51ff023ca36d50b42e343b0b048c07c8e72d1905'
runpy.run_path(str(Path(__file__).with_name('ue-import-content-sprites.py')),
              init_globals={'SPRITE_VERSION':'v007','SPRITE_MANIFEST':manifest,'SPRITE_REUSE_EXISTING_COMPONENTS':True})
