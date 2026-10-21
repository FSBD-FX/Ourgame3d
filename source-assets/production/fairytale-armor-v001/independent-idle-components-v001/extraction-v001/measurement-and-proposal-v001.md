# 147四胸片：提取与整数挂接提案（未通过）

2026-10-16。已实际看E092/093保全的raw与两guide；没有看任何新透明图、contact、GIF或composite。只有新素材目录后处理，未改UnrealSource、旧图、ledger，未Native/UE/导入。

标准sprite-gen自己的venv＋现有shared-row wrapper：RGB绿键#00FF00，原生默认96/180/18、unmix4/spill.005、components无slotfallback。提取/atlas/export4/preview均exit0，原生QA0errors/0warnings。四个原生组件318×270/316×270/316×270/316×271，共用60/271=.22140221402214022；输出70×60、原512cell、bbox[221,226,291,286]。原4×167ms未改；GIF预览量化为170ms，不作运行时轴。四RGBA来源各异，非复制四份；尚不代表四pose配准或运动通过。

**固定量测含义：** collar是甲片U形颈口上边界在固定中心40%–70%横向ROI内最深的alpha≥128平台中点；waist是组件bbox中心X采样柱上的实际alpha≥128下沿，不是全图最低点、身体根或自动足根。领口约±1px、腰沿约±1–2px选择歧义。完整ROI、轮廓profile与真实坐标在registration-receipt。

四件甲片U槽点为[260,237]/[259,237]/[259,237]/[259,237]，腰沿点均[256,283]。仅按衣服waist目标作整数平移[7,20]/[8,20]/[7,21]/[7,20]。拷贝用无mask的RGBA整数paste，不重采样、旋转、缩放或改画；四件croppedRGBA逐字节不变，非透明裁切0，131输入原字节不变，composite在甲alpha0处保持原RGBA。

**不能混同两个领口feature。** 131表中的collar是衣服挂接设计点，甲片量测的是U槽最低轮廓；技术guide的红点本身高于蓝色U槽约4–5px（phase1红点另有上移）。因此二者整数差[1,8]/[0,12]/[1,9]/[0,8]是描述性配准信息。直接把两点当同一点的原预检约束不成立，本提案保留“未通过/未接受”，不能为过门换landmark，也不能由这个差单独裁定必须重生或改变共用比例。腰误差0是平移构造的结果，不是双点适配证明。

原shared60px基线、合同和提取文件保持。新`registration-proposed-v001/armor-front`四件只是整数位置提案；`composite-preview`四张只是把真实甲片叠到未改131后的观察素材，不能当新body或已导入素材。root先E094保全，再实际查看各帧领肩/腋边/腰带、四帧衔接和72px读图，之后明确决定是否接受位置、另立合同调整形状或共同尺度。本轮不先行重拟合，也不宣布最终穿戴fit失败或成功。

新增helper实际exit0，Pillow的`getdata`有一条弃用提示；这与原生提取QA0警告是不同结果，保留原执行脚本，不修改像素掩盖提示。背片、肩片、护臂、护胫、近臂/近手分区、武器及walk/全动作未由胸片补齐；仍0/15，Production869。
