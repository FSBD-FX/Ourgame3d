"""UE commandlet entry for the frozen122-frame candidate snapshot; no v001 replacement."""
from pathlib import Path
import runpy
runpy.run_path(str(Path(__file__).with_name('ue-import-content-sprites.py')),
               init_globals={'SPRITE_VERSION': 'v002'})
