"""Static byte-scope check only; actual UE compilation and draw remain Root gates."""
from pathlib import Path
import argparse
import ast
import hashlib
import json

C = Path(__file__).resolve().parent.parent


def pin(path):
    path = Path(path).resolve()
    data = path.read_bytes()
    return dict(path=path.as_posix(), bytes=len(data), sha256=hashlib.sha256(data).hexdigest())


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--expected-current', choices=('before', 'after'), default='before')
    p.add_argument('--output')
    a = p.parse_args()
    s = json.loads((C / 'source/exact-seams-v001.json').read_text(encoding='utf-8'))
    before = (C / 'source/before-DungeonFairytaleSwordPresentation.cpp').read_bytes()
    after = (C / 'source/after-DungeonFairytaleSwordPresentation.cpp').read_bytes()
    checks = []

    def need(name, passed):
        if not passed:
            raise AssertionError(name)
        checks.append(dict(check=name, passed=True))

    need('before copy exact original pin', len(before) == s['target']['bytes'] and hashlib.sha256(before).hexdigest() == s['target']['sha256'])
    need('after copy exact declared pin', pin(C / 'source/after-DungeonFairytaleSwordPresentation.cpp') == s['candidate_after'])
    current = Path(s['target']['path']).read_bytes()
    need('actual current target exact selected state', current == (before if a.expected_current == 'before' else after))
    patched = before.decode('utf-8')
    for seam in s['seams']:
        need('unique exact seam ' + seam['id'], patched.count(seam['before_text']) == 1)
        patched = patched.replace(seam['before_text'], seam['after_text'], 1)
    need('two seams reproduce whole candidate', patched.encode('utf-8') == after)
    restored = patched
    for seam in reversed(s['seams']):
        need('unique reverse seam ' + seam['id'], restored.count(seam['after_text']) == 1)
        restored = restored.replace(seam['after_text'], seam['before_text'], 1)
    need('reverse exactly reproduces every old byte', restored.encode('utf-8') == before)
    anchor = b'    UTexture2D* Body=GetFairytaleSwordTexture(Record.Clip,Record.Frame);'
    need('entire Body readiness/projection/actual draw/sword/hand suffix unchanged', before[before.index(anchor):] == after[after.index(anchor):])
    need('no new Source/header/tests declared', s['new_source_files'] == [] and s['new_headers'] == [] and s['new_registered_tests'] == 0)
    need('candidate line endings retained', after.count(b'\r\n') == after.count(b'\n'))
    ast.parse((C / 'import/ue-import-primary1-bridge258-v001.py').read_text(encoding='utf-8'))
    need('actual importer parses as Python AST', True)
    result = dict(schema='request258-source-static-check-v002', passed=True, verifier=pin(__file__), checks=checks,
                  current_source_expectation=a.expected_current, current_source=pin(s['target']['path']),
                  actual_source_changed=False, UE_started=False, compilation_verified=False, native_verified=False)
    if a.output:
        out = Path(a.output)
        with out.open('x', encoding='utf-8', newline='\n') as stream:
            json.dump(result, stream, ensure_ascii=False, indent=2)
            stream.write('\n')
        print(json.dumps(dict(passed=True, checks=len(checks), report=pin(out))))
    else:
        print(json.dumps(result))


if __name__ == '__main__':
    main()
