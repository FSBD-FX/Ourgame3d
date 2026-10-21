from pathlib import Path
p=Path(__file__).resolve().parent
t=(p/'extract-primary1-other-armors-v006.py').read_text('utf-8')
t=t.replace('primary1-other-armors-v006','primary1-other-armors-v007').replace('front-{i}-v006.png','front-{i}-v007.png').replace('-{suffix}-v006.png','-{suffix}-v007.png').replace('candidate-v006.json','candidate-v007.json')
t=t.replace('armor=tr.sel.extract(src,q);assert',"""# Remove only tiny detached selection fragments, never retain-largest.
            # All meaningful shoulder/torso/hem/shin components remain independent.
            points={(xx,yy) for yy in range(512) for xx in range(512) if q.getpixel((xx,yy)) and src.getpixel((xx,yy))[3]}
            pruned=[]
            while points:
                seed=points.pop();stack=[seed];group=[seed]
                while stack:
                    xx,yy=stack.pop()
                    for n in [(xx-1,yy),(xx+1,yy),(xx,yy-1),(xx,yy+1)]:
                        if n in points:points.remove(n);stack.append(n);group.append(n)
                if len(group)<=24:
                    pruned.append(len(group))
                    for pt in group:q.putpixel(pt,0)
            armor=tr.sel.extract(src,q);assert""")
t=t.replace("'visible_RGBA_equals_source':True", "'visible_RGBA_equals_source':True,'pruned_detached_fragment_sizes':pruned,'tiny_fragment_threshold_px':24")
q=p/'extract-primary1-other-armors-v007.py';assert not q.exists();q.write_text(t,'utf-8')
print('v007 prune only detached <=24px selection fragments; keep every meaningful armor component')
