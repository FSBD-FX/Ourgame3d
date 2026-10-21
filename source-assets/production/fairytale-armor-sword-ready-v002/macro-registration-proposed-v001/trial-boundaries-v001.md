# 实际肩特征＋24原像素候选

E160后实际view近/远各4curated＋各4原像素bbox crop和胸only四组合。胸only未见明显大块压盔/手/腰，但这是512静态观察，不是72px运行或语义零覆盖。近肩central washer/黑圆孔center候选257261/259261/258261/259261；远肩NEW TopStrapRivetTrialV1候选251252/253252/254252/254252，人工墨线/小椭圆AA误差±2px。远肩原prompt中央boss不存在，保持未满足，topstrap是明确新试装feature，不改旧prompt或把它叫中央boss，不取全甲bbox/亮点中心。

首轮body衣面设计target保持，Near207248/205244/205249/204244（±3），Far300266/302270/300267/298264（±5），非骨/实际body rivet事实；仅整数平移，无perframe scale/rotate/warp。Near顶部strap在盔下邻近区，原点精确映射不代表零穿插，必须新E保全后实际审全stack；当前不暗改target。如需移动必须保本版并明确新target trial。

输出24个512RGBA：Chest4为此前整数registered文件逐字节copy，Near4/Far4为原curated整数平移，另BodyRest/NearArmWithoutHand/NearHand各4为source ownership候选逐字节copy。三body层在无甲时全RGBA exact复原原158；各新甲逆平移全RGBA exact，所有非零RGBA/AA无裁切。精确只指源像素/构造保真，分层语义仍候选。

静态无剑层序BodyRest→FarShoulder→Chest→NearArmWithoutHand→NearShoulder→NearHand；各甲与omit-one比较的实际差异像素数只证明此候选static stack有可见贡献，不证明好看、attach正确或UE真的画出。future Sword在NearShoulder之后/NearHand之前，需root绑定158实际新grip数据；本输出没有剑，不借155/157回退或宣称武器遮挡已验。新组合未显式view，等保全。72px/整装一次mirror/四pose同167ms/旧原件均保持；无Source/UE/import/ledger/native写入，完整内容0/15。
