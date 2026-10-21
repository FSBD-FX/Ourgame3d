# Native175四owner候选

以已E228保全并实际view过的175六原512重新描各相完整brown cuff+glove、灰近袖和完整钟盔；没有直接把测量glove polygon冒充完整手mask，没有复用171坐标/层或用bbox/yband/材质阈值替语义。NearHand优先，其次Helmet、NearArm，其余及farhand/低领/腰带/裤靴归BodyRest。Helmet各相独立外侧包络与下盔沿控制；隐藏轮廓/骨不补。

24原RGBA层、24坐标assignment masks、24技术诊断。原每坐标恰一owner；PNG读回各值相同，四层uint16求和还原整张RGBA逐字节，premultiplied合成相同，alpha0非零RGB也完整保留。这仅证明数值保全，不接受语义/外沿/握柄/甲剑遮挡。局部控制点只是sanity，无法替代Root图审。

重点风险：1拳盔共享墨线，2近远手交叠，3/4低腕与裤/膝以及袖口边缘。每相保留±2/3px原RGBA边界采样与技术风险带。新图未view/emit/display；先RootF/E保全再审24层。无Source/公共tools/台账/媒体/UE/生成/导入改动，正式0/15。
