"""Import only18 corrected SWD body frames; frozen v002 sword stays referenced."""
from pathlib import Path
import runpy
root=Path(__file__).resolve().parents[2]
runpy.run_path(str(Path(__file__).with_name('ue-import-content-sprites.py')),
              init_globals={'SPRITE_VERSION':'v003',
                            'SPRITE_MANIFEST':root/'source-assets/production/first-unit-animation-v002/import-subset-v002.json',
                            'SPRITE_REUSE_EXISTING_COMPONENTS':True})
