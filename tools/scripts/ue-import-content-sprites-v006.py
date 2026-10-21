"""Import68 unique frozen round-helmet frames as74 logical Texture2D assets."""
from pathlib import Path
import hashlib
import runpy
root=Path(__file__).resolve().parents[2]
manifest=root/'source-assets/production/first-unit-animation-v003/import-subset-v005.json'
assert hashlib.sha256(manifest.read_bytes()).hexdigest()=='cd35fa43412f8fcf6fcd074e9f4f8ff85c20615e2d99863f15c6f5504e0a7c7d'
runpy.run_path(str(Path(__file__).with_name('ue-import-content-sprites.py')),
              init_globals={'SPRITE_VERSION':'v006','SPRITE_MANIFEST':manifest,'SPRITE_REUSE_EXISTING_COMPONENTS':True})
