"""XBW armor topic retention, using the existing single visual ledger."""
from pathlib import Path
import importlib.util
P=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('shared_record',P.parent/'first-batch-weapon-actions-v001/production-record.py')
r=importlib.util.module_from_spec(s);s.loader.exec_module(r)
r.ROOT=P
r.ARCHIVES=[Path('F:/Ourgame/过程图稿与视频/2026-10-15_猎弩四甲分层动作适配_v001'),Path('E:/OurGame/Knight/过程图稿与视频/2026-10-15_猎弩四甲分层动作适配_v001')]
if __name__=='__main__':r.main()
