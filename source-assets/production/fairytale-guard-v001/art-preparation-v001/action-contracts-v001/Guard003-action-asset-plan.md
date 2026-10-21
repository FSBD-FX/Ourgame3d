事实：正式Guard003为185HP/60甲/15抗/85韧/160世界单位每秒，身体与受击半宽40×28。Kernel只有Dormant/Waking/Idle/Windup/Active/Recovery/Stunned/Dead；Move是Idle真实位移，普通Hurt不是阶段。当前灰块是明确占位，82px不决定新美术高度。当前Hero实际72px，候选Guard100.8px(1.4倍)、约81.5px宽；定义碰撞投影52×21.28px保持，镜头Ground(.65,-.38)保持。206底图已Root内部锁定，不等于最终审美通过。

推理：两种攻击均全程站定，粗短宽石板轮廓应与冲锋石骑分开。优先Idle4、Wake6，再斧Windup6与Follow6两行。A1锁0.50/前摇1.00/有效0.20/后摇1.40/CD3.10；A2锁0.45/前摇0.90/有效0.15/后摇1.50/CD3.00。Follow行前2格仅Active，后4格仅Recovery，真实截止不被默认fps延长。Recovery结束后额外IdleReady门0.30，既不加有效窗也不重写CD。

完整资产：Dormant1/Wake6/Idle4/Move6/AxeWindup6/AxeFollow6/StompWindup6/StompFollow6/Stunned4/Death6/InterruptedRecovery4，共11行55身体帧；Hurt4为220ms材质/局部FX，不覆写有效攻击姿态；独立重斧至少1帧，斧/脚击/命中/破韧FX按真实EventID另行制作。Death视觉1s只是提案，死亡/移除身体阻挡/奖励资格即时按Kernel，不等动画。Stunned恰0.4s，1s是韧保护；中断只恢复原OccupiedUntil剩余，不能重播Active。

风险：现SG标准compose只按均匀fps输出时长；Wake6@6fps=1002ms，并非Kernel1000ms。独立native-art mapping为权威，工具原输出保留并标识，不改工具或玩法。Move6的600ms/96world仅艺术调参，未实测步幅/足锁；撞墙不能原地踏步。206细碎斑块稍多，后续不新增微纹；纯magenta保护苔藓绿色。

身体不烘焙斧。近手、远手都须明确闭合；斧柄两个实际A与身体两个实际B、可见轴/柄长都暂null，待Root保全/curated真实像素量测。一把斧固定scale后只能刚体旋转/平移，不逐帧拉伸或画补手指；若双手长度/视角不合用native修正。身体5独占层与斧前后2层须原RGBA重组，盔与两拳正确盖柄。Native地面矩形/椭圆警示继续使用真实几何，不拿装饰FX替换判定；miss无命中特效，Poise/death关闭有效FX，禁止新飞石/持续伤害。

左右默认整套runtime镜像，浅俯3/4camera一致，锁朝之后用A.Facing。完整展示/导入/UE/native生成均Root负责。所有原Source/tools/ledger/README未改，本目录只生产候选数据/提示词；仍需动作行真实生成、shared提取/curated、双手柄量测、互斥闭合、实际native双向与恢复/受击/死亡录像。
