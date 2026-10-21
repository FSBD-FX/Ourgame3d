# Native171四owner分区候选

参考P1工具的“逐坐标独占、原RGBA复制”策略，重新按171六原512的可见轮廓选取各相明确像素归属。没有复用159/158mask，没有把measurement±4拳心polygon直接当全手。NearHand包括棕袖口及完整可见glove/黑边/AA；NearArm只近侧灰袖；HelmetForeground用各相下盔沿/领圈曲线及外侧head envelope，包括原盔、眼窗、顶栓、墨边AA，灰领圈留BodyRest。BodyRest还保留躯干、腰带扣、远臂/手及腿靴。

24层+24二值坐标assignment mask+24技术诊断，所有图均新派生、尚未显式查看。每坐标恰一owner，PNG保存读回像素与各owner原值一致；四层uint16求和恢复原整张RGBA逐字节，包括alpha0非零RGB，premultiplied合成相同。这证明像素保全与独占，不证明艺术语义或甲/剑遮挡正确。

重点待Root保全后实图审查：0/5拳与裤/腰带共享墨边，1闭拳外沿/袖口和左腿边缘，2灰袖/躯干及近袖口/远手，3抬拳上缘与盔下黑线，4袖口右下贴腰带扣。每相candidate-boundaries有原RGBA采样及±2/3px风险带。局部掌/袖/远手/领圈等owner控制只是sanity；不能冒称完整边缘已接受。隐藏骨/颈/胸面全不补画。

未动Source/tools公共文件、输入、旧freeze、UE/UBT/import/nativegen或台账。没有把新技术图写到媒体目录，也没有view/emit；须Root先E保全再图审。没有动作、足锁、握柄或完整内容接受。
