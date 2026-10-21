"""Same exact-member two-SHA retention, using faster lossless DEFLATE level1."""
from pathlib import Path
_template=Path(__file__).with_name('retain-native-media-lossless-zip-v001.py')
_source=_template.read_text(encoding='utf-8')
assert _source.count('compresslevel=6')==1
_source=_source.replace('compresslevel=6','compresslevel=1')
_old="receipt=dict(schema='native-media-exact-original-zip-retention-v001',"
assert _source.count(_old)==1
_source=_source.replace(_old,"receipt=dict(compression_level=1,retainer_version='v002',schema='native-media-exact-original-zip-retention-v001',")
exec(compile(_source,str(_template),'exec'),globals())
