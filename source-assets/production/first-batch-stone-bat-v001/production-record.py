"""Stone-bat topic retention using the one shared authoritative visual ledger."""
from pathlib import Path
import importlib.util
P=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('shared_visual_record',P.parent/'first-batch-weapon-actions-v001/production-record.py')
r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r)
r.ROOT=P
r.ARCHIVES=[Path('F:/Ourgame/过程图稿与视频/2026-10-15_灰翼石蝠动作生产_v001'),Path('E:/OurGame/Knight/过程图稿与视频/2026-10-15_灰翼石蝠动作生产_v001')]
if __name__=='__main__':r.main()
