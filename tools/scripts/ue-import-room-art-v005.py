"""Import the frozen far/mid/floor scenery subset after alpha/source review."""
from pathlib import Path
import runpy
root=Path(__file__).resolve().parents[2]
runpy.run_path(str(Path(__file__).with_name('ue-import-room-art.py')),
              init_globals={'ROOM_ART_MANIFEST':root/'source-assets/production/room-art-v001/manifests/import-subset-v005.json'})
