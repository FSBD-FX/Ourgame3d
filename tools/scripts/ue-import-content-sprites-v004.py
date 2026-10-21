"""Import6 EV042 round-helmet idle frames; old sword component is reused."""
from pathlib import Path
import runpy
root=Path(__file__).resolve().parents[2]
runpy.run_path(str(Path(__file__).with_name('ue-import-content-sprites.py')),
              init_globals={'SPRITE_VERSION':'v004',
                            'SPRITE_MANIFEST':root/'source-assets/production/first-unit-animation-v003/import-subset-v001.json',
                            'SPRITE_REUSE_EXISTING_COMPONENTS':True})
