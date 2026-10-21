"""Preserve failed v001; restrict its reset match to the normal DrawHUD block."""
from pathlib import Path
p=Path('F:/Ourgame/tools/scripts/prepare-guard-room-warning-v001.py')
source=p.read_text(encoding='utf-8')
source=source.replace('stone-guard-room-warning-root-v001','stone-guard-room-warning-root-v002')
old="('    RenderedTextDrawCalls=0;RenderedActorSpriteSizes.Reset();',"
new="('    RenderedTextDrawCalls=0;RenderedActorSpriteSizes.Reset();\\n    UIScale=',"
assert source.count(old)==1;source=source.replace(old,new)
old="'    RenderedTextDrawCalls=0;RenderedActorSpriteSizes.Reset();RenderedGuardRoomWarningSlots.Reset();'),"
new="'    RenderedTextDrawCalls=0;RenderedActorSpriteSizes.Reset();RenderedGuardRoomWarningSlots.Reset();\\n    UIScale='),"
assert source.count(old)==1;source=source.replace(old,new)
exec(compile(source,str(Path(__file__)), 'exec'))
