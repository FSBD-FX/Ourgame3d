"""Import24 frozen EV042 round-helmet idle/primary frames; reuse separate sword."""
from pathlib import Path
import hashlib
import runpy
root=Path(__file__).resolve().parents[2]
manifest=root/'source-assets/production/first-unit-animation-v003/import-subset-v003.json'
assert hashlib.sha256(manifest.read_bytes()).hexdigest()=='96e97a29e7c41fda3856b8e9de47b15ec60d67709291df1a5277080fe7f22ef2'
runpy.run_path(str(Path(__file__).with_name('ue-import-content-sprites.py')),
              init_globals={'SPRITE_VERSION':'v005','SPRITE_MANIFEST':manifest,'SPRITE_REUSE_EXISTING_COMPONENTS':True})
