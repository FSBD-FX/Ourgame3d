from pathlib import Path
import ast,hashlib
HERE=Path(__file__).resolve().parent
SOURCE=HERE/'process-Dodge218-LGT-component-row-v001.py'
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()=='5d238881e0c1d036c1f2c575111aa24a63881270a0644d4bdd76d3ccf4749608'
code=SOURCE.read_text(encoding='utf-8-sig')
before="armor-standard-input-v001/Root-Dodge218-three-LGT-official-input-handoff-v001.json"
after="Chest240-geometry-correction-standard-input-v001/Root-Chest240-Dodge4-geometry-correction-official-input-handoff-v001.json"
assert code.count(before)==1
code=code.replace(before,after)
tree=ast.parse(code)
tree.body=[n for n in tree.body if not isinstance(n,ast.If)]
scope={'__file__':str(Path(__file__).resolve()),'__name__':'Chest240_readonly_shared_pipeline_adapter'}
exec(compile(tree,str(Path(__file__).resolve()),'exec'),scope)
scope['main']()
