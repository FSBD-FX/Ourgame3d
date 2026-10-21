from pathlib import Path
import datetime, hashlib, json, shutil

R=Path('F:/Ourgame')
def desc(p):
    b=p.read_bytes(); return dict(path=p.as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def write(p,v):
    assert not p.exists(),p
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def retain(source,topic,present):
    out=R/'过程图稿与视频'/topic; assert not out.exists(),out
    (out/'原件').mkdir(parents=True); (out/'展示副本').mkdir()
    files=[]
    for p in sorted(source.rglob('*')):
        if not p.is_file(): continue
        q=out/'原件'/p.relative_to(source); q.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(p,q); assert desc(p)['sha256']==desc(q)['sha256']
        files.append(dict(source=desc(p),copy=desc(q)))
    for p in present:
        q=out/'展示副本'/p.name; assert not q.exists(); shutil.copy2(p,q)
        assert desc(p)['sha256']==desc(q)['sha256']
    write(out/'source-version-status-index.json',dict(files=files,status='candidate before semantic review; exact original copies; not acceptance',formal_complete_units=0))
    (out/'README.md').write_text('原件与展示副本逐字节复制；分层重建一致不等于语义正确，待审盔下沿、袖口与手套。非正式完成。\n',encoding='utf-8')
    return out

P=R/'source-assets/production/fairytale-sword-primary2-body-partition-v001'
f=json.loads((P/'partition-freeze-v001.json').read_text())
for row in f['files']: assert desc(Path(row['path']))==row
present=[P/'diagnostics'/f'frame-{i}-ownership-overlay.png' for i in range(6)]
present += [P/'layers'/part/f'frame-{i}.png' for part in ['NearHand','HelmetForeground'] for i in range(6)]
# Layer filenames overlap, preserve component prefixes in the presentation copies.
A=retain(P,'2026-10-16_军剑上挑四归属分层审阅_v001',present[:6])
for part in ['NearHand','HelmetForeground']:
    for i in range(6):
        p=P/'layers'/part/f'frame-{i}.png';q=A/'展示副本'/f'{part}-frame-{i}.png'
        shutil.copy2(p,q);assert desc(p)['sha256']==desc(q)['sha256']

B=R/'source-assets/production/fairytale-armor-sword-primary2-v001'
D=B/'generation-prompts-v002'
draft=json.loads((D/'draft-handoff-v002.json').read_text())
original=B/'primary2-macro-native-handoff-draft-v001.json'
assert desc(original)==draft['original_handoff']
handoff=json.loads(original.read_text(encoding='utf-8-sig'))
for row in handoff['rows']:
    revised=next(x for x in draft['rows'] if x['component']==row['component'])
    assert row['reference_images_in_order']==revised['reference_images_in_order']
    row['original_prepared_prompt']=row['prompt'];row['prompt']=revised['prompt']
    assert desc(Path(row['prompt']['path']))==row['prompt']
    for ref in row['reference_images_in_order']: assert desc(Path(ref['file']['path']))==ref['file']
    row['generation_ready']=True
review=B/'root-three-armor-input-review-v002.json'
write(review,dict(created_local=datetime.datetime.now().astimezone().isoformat(),
    canonical_prompts=[desc(D/n) for n in ['chest-canonical-v002.txt','nearshoulder-canonical-v002.txt','farshoulder-canonical-v002.txt']],
    draft=desc(D/'draft-handoff-v002.json'),original=desc(original),
    explicit_reference_review='Root viewed all11 references after F/E214 retention; read three canonical prompts fully',
    approval_scope='one native six-view row each Chest/NearShoulder/FarShoulder for existing native171 body; no externalAPI; no body changes',
    far_family='approved topstrap rivet, old163 centralboss failure retained',
    future_feature_A_measured=False,geometry_design_only=True,formal_complete_units=0,
    host_fee_usd=None,authorization_events=['EV-040','EV-041']))
handoff['generation_ready']=True;handoff['root_review_required_before_generation']=False
handoff['root_input_review']=desc(review);handoff['concise_prompt_draft']=desc(D/'draft-handoff-v002.json')
approved=B/'primary2-macro-native-handoff-approved-v002.json';write(approved,handoff)
print(json.dumps(dict(partition_archive=A.as_posix(),approved_handoff=desc(approved),root_review=desc(review)),ensure_ascii=False))
