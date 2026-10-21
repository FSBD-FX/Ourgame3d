from pathlib import Path
import importlib.util
import sys
spec=importlib.util.spec_from_file_location('xbw_armor_import',Path(__file__).with_name('ue-import-xbw-armor-layers-v001.py'))
job=importlib.util.module_from_spec(spec);spec.loader.exec_module(job)
job.run('ready_idle','093d6b15a44dadc485b28584784c888b2df7f1a88261891632ef836e128925a1',
    '/Game/Production/FirstBatch/v021/XBWArmorReady','Ready',6,'--validate-only' in sys.argv)
