"""Import fourarmor walk48 over frozen new0.96body into unusedv023/XBWArmorWalk.

Ordinary Python--validate-only; UE5.5-ExecutePythonScript or py absolute path.
No source geometry edits, overwrite, lifecycle changes or runtime acceptance.
"""
from pathlib import Path
import importlib.util
import sys

spec = importlib.util.spec_from_file_location("xbw_armor_walk_v002_checks", Path(__file__).with_name("ue_xbw_walk_v002_checks.py"))
job = importlib.util.module_from_spec(spec)
spec.loader.exec_module(job)

if __name__ == "__main__":
    job.run("armor", "--validate-only" in sys.argv)
