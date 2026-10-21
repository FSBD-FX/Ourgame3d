from pathlib import Path
import importlib.util
import sys
spec=importlib.util.spec_from_file_location('xbw_armor_import',Path(__file__).with_name('ue-import-xbw-armor-layers-v001.py'))
job=importlib.util.module_from_spec(spec);spec.loader.exec_module(job)
job.run('reload','963d74e304894088492b205fb9b113b0e5b6d9acf52785724c6d400271722002',
    '/Game/Production/FirstBatch/v020/XBWArmorReload','Reload',4,'--validate-only' in sys.argv)
