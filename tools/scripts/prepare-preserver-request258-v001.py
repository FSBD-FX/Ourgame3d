from pathlib import Path
R=Path('F:/Ourgame')
old=R/'tools/scripts/preserve-hero-request257-v001.py'
out=R/'tools/scripts/preserve-hero-request258-v001.py'
assert not out.exists()
text=old.read_text(encoding='utf-8')
changes={
 'request257-primary1-body':'request258-primary1-body-correction',
 'exec-14702cb0-efbc-445b-a1e9-77729797b10c.png':'exec-ec87b0ca-9471-40ab-8cd4-a2e3895f6adc.png',
 'primary1-bridge-body.png':'primary1-bridge-correction.png',
 'window11_requested=17':'window11_requested=18',
 'window11_remaining=7':'window11_remaining=6',
 'lifetime_requested=281':'lifetime_requested=282',
}
for before,after in changes.items():
 assert before in text,before
 text=text.replace(before,after)
text=text.replace('257','258')
with out.open('x',encoding='utf-8') as f:f.write(text)
print(out.as_posix())
