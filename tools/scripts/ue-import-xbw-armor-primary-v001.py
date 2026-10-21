from pathlib import Path
import importlib.util
import sys
spec=importlib.util.spec_from_file_location('xbw_armor_import',Path(__file__).with_name('ue-import-xbw-armor-layers-v001.py'))
job=importlib.util.module_from_spec(spec);spec.loader.exec_module(job)
job.run('primary','0acc811b8633f8d3b165ea588ad38c8f95372f4bd13ab37ec7ece7174ecc0a82',
    '/Game/Production/FirstBatch/v019/XBWArmorPrimary','Primary',6,'--validate-only' in sys.argv)
