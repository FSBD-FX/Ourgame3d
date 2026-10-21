# 159首斩六帧：四owner原RGBA分层候选

仅从E149保全的六张159原图逐坐标复制。每帧包含BodyRest、HelmetForeground、NearArmWithoutHand、NearHand四个512×512 RGBA层，以及四个二值归属mask。没有重绘、位移、缩放、旋转、修姿态或补隐藏身体。

数值证明：每个原坐标恰一owner；各层拥有处的RGBA等于原图，未拥有处四通道为零；逐字节求和重组完整等于原图；独占alpha合成的premultiplied RGBA精确相同。六张实际原图的alpha0非零RGB像素计数均为0；实现复制完整RGBA、不以alpha裁掉RGB，当前实图证明不冒充存在非零隐藏RGB样本。

HelmetForeground覆盖原钟盔壳、眼窗/眼睛、顶铆钉/柄与原墨边AA；原帽檐以下领圈留BodyRest。手层包含棕袖口、整手套及墨边AA，未把既有拳心重放polygon当完整mask。外包线允许经过透明背景以保留实际AA，背景坐标归属只作全域记账，不宣称解剖。

数值精确不等于语义接受。可见帽檐/领圈边界约±2sourcepx；袖/躯干、袖/棕袖口、手/其他身体边界约±3px，见每帧不确定带。特别复核：phase1近拳靠后帽檐处的共享暗墨；phase2前臂跨胸、近袖口下缘靠远腕；phase3棕袖口右缘靠腰带、近拳右下缘靠裤面；phase0/4/5近拳下缘与裤面的黑墨交界。无隐藏骨点，未接受拇指结构。

新层、mask及诊断图尚未显式查看，须根线程先E保全再逐图审查。未来可试BodyRest→FarShoulder→Chest→NearArmWithoutHand→NearShoulder→HelmetForeground→独立Sword→NearHand；本包无甲片/剑合成，也未改变该层序的运行实现。没有生成、导入、UE运行或完整内容单元通过声明。
