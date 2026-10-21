# Native160 Chest4：固定朝向失败，保留拒绝

2026-10-16，scale_tests。E148保全后实际独立view原2172×724 raw（工具显示时缩至2048×683，未据此作像素挂点量测）。0–2片外展肩带、较大的侧armhole集中在image-LEFT；第4片相反，在image-RIGHT，板体压缩侧同时交换。属于透视/朝向逆转，不能当呼吸变化或仅换明暗。固定nativeFacing+1四片合同失败，整row拒绝导入；不mirror第4片，不覆盖raw/原prompt/旧freeze。

本次只按原request标准shared-row提取四片、atlas、curated、preview。结构QA不能推翻视觉拒绝。新派生待另批E保全才view；actual component A均null。原0可在保全/审阅后仅作下一次正向造型/材料参考，不能宣称当前四帧已可用。现胸两侧strap bolt不是body中央cloth A259271的同一feature，不把左bolt盲贴中央或以bbox-center造假；下一候选若加入清晰中央boss须生成后再测。无导入/UE/Source/台账/新native调用，完整内容仍0/15。
