from pathlib import Path
p=Path(__file__).resolve().parent
t=(p/'extract-primary1-LGT-v004.py').read_text('utf-8')
t=t.replace('primary1-LGT-selection-v004','primary1-LGT-selection-v005').replace('selection-v004.png','selection-v005.png').replace('candidate-v004.json','candidate-v005.json').replace('-{i}-v004.png','-{i}-v005.png')
t=t.replace("if q[xx,yy] and g[xx,yy] and rr>180 and gg>130 and bb>65:q[xx,yy]=0", """skin_or_under_sleeve=g[xx,yy] and rr>180 and gg>130 and bb>65
                gray_wrist=g[xx,yy] and bb>rr*.8 and bb>gg*.9 and rr<150
                sampled_muted_trousers=yy>360 and rr<150 and gg>rr*.68 and bb>gg*.45
                if q[xx,yy] and (skin_or_under_sleeve or gray_wrist or sampled_muted_trousers):q[xx,yy]=0""")
t=t.replace("'complete_armor':False", "'complete_armor':False,'source_material_assist':'LGT_only_sampled_native_skin_gray_wrist_and_muted_trouser_colors_with_manual_limb_and_hem_scope_no_visible_RGB_changes'")
q=p/'extract-primary1-LGT-v005.py';assert not q.exists();q.write_text(t,'utf-8')
print('v005 LGT material-assisted actual pixel selections')
