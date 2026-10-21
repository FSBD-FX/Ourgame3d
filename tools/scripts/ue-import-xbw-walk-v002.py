"""Import new0.96XBW walk18 into unusedv022/XBWWalk; ordinary Python--validate-only.

UE5.5: -ExecutePythonScript=<absolute path> or py "<absolute path>".
Source math/pixels/Texture2D import do not accept runtime grip/footlock/gameplay.
"""
from pathlib import Path
import importlib.util
import sys

spec = importlib.util.spec_from_file_location("xbw_walk_v002_checks", Path(__file__).with_name("ue_xbw_walk_v002_checks.py"))
job = importlib.util.module_from_spec(spec)
spec.loader.exec_module(job)

if __name__ == "__main__":
    job.run("body", "--validate-only" in sys.argv)
