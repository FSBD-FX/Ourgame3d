from pathlib import Path
p=Path(__file__).resolve().parent
t=(p/'extract-idle-four-armors-v002.py').read_text('utf-8')
t=t.replace('v002','v003').replace("'version':2","'version':3")
# Under-sleeve pixels are common body, not ringmail or plate surfaces.
t=t.replace('(302,290),(307,309),(301,331),(287,320),(282,290)','(302,290),(307,304),(301,311),(288,308),(282,290)')
t=t.replace('(205,337),(190,318),(184,292)','(205,337),(202,318),(201,292)')
t=t.replace('(209,283),(201,301),(177,301)','(209,283),(201,293),(177,295)')
q=p/'extract-idle-four-armors-v003.py';assert not q.exists();q.write_text(t,'utf-8')
print('New masks only; source pixels and v002 unchanged')
