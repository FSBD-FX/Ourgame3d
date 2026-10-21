# Dodge / Hurt / Death 持物与遮挡候选合同

事实：已审13身体帧及Root认可的source-pose继续保留；没有装备/registration/native验收。五武器实际模板为SWD/GSW/SPR/XBW/STF，四甲为LGT/MED/HVY/ROB；None不在20格里。当前Binding仍只接受SWD+None/LGT，当前其他三状态仍bareReady0，不能将此文字合同算作修好。精确依据与before pins见final-source-pins JSON；13curated与5prop均按已有SHA独立两遍核对零差。

| 家族 | 实际持握结构 | 当前可复用范围 |
|---|---|---|
| SWD | 一手短柄、副手平衡 | Dodge4闭合近手和Hurt0/2/3可作接触测量起点；Hurt1张手须纠错；均未认证真握 |
| GSW | 双手同一长柄，副握在主握后方 | 躯干/下肢及脱手Death身体候选；不能拿SWD一只手托重剑 |
| SPR | 双手导杆，前支撑远于后主握 | 躯干/下肢及脱手Death身体候选；握距/方向不同于GSW |
| XBW | 后握把＋前垂直握把，真实中立/空弦/拉弦/装填外观 | 旧prop/生命周期结构可引用，旧圆盔body不可贴；新Dodge/Hurt需两手源 |
| STF | 主握缠皮杆，副手支撑在manifest中明确optional | 可以先试单手非施法分支，但长度/灯头/手腕与遮挡须独立审；不冒认共用SWD或必须双手 |

旧prop上的主/副握测量只能描述物体，不能变成新身体socket。五家的Dodge/Hurt上肢没有哪两家已被实际证实完全共用。Death从age0纯表现脱手后，现5身体可最大共用；每武器prop/每甲遮挡仍各自审，不能据此接受20格。

推理：最小首片SWD+None/LGT。Dodge四相全程真近手握柄，不因画面难做放开/隐藏。先测每相握柄几何与原像素NearHand，无法合理接触的相位才走NEW完整Dodge4纠错row。Hurt装备始终保留；Hurt1近手展开是明确源纠错项，不能把Ready手/mask贴过去。最少提出NEW Hurt4标准row，保留收缩/后仰/回身/站稳，只纠正pose1的近手握持语义；真实手/肘/腕随各姿势，不锁旧Ready坐标。整行shared提取、另保全、再审，旧13帧不改。精确真实握导向未供齐前不生成。

Death采用现5张逐关节collapse。原Death0已张手，所以提案在age0即释放；独立武器从作者化手旁起点落到角色同ground-Y的外侧，建议.2下降、.4表现落定、.6/.8及其后保持。这些是美术提案，没有新增gameplaydeadline或物理碰撞；所有transform、倾角、落地点/接触像素和遮挡仍null。武器不假装握在撑地掌里；不生成Actor、entity/source、拾取物、damage、投射物、装填、音频事件或库存Drop，不改变ammo/focus/甲/HP/碰撞。刚性旧prop作为地面图也只是候选：若静态合成暴露地面透视错误，仅为实际失败家族补一张ground-prop，不为省请求硬贴。

死亡轨道由既有Dead/AnimationName/AnimationTime/Facing/Ground及已提交装备和profile直接求值，避免未保存lastAliveVisualMatrix；合法快照恢复按现有年龄seek，绝不重放释放。实际FighterSnapshot.h:52–54,69–72已保留死亡/装备/动画年龄，Fighter.cpp:449/549实际捕获恢复年龄；1799–1805终端展示时间独立于冻结SimTime。此方案不扩RootV2合法范围或改验证。死亡前是攻击/Shift/受击/空中时的首帧连续性仍须真正录制，不预称无跳变。

Registration仍是硬前置：Death1–4的连续standing root无法从尸体重心或单掌推断，必须作者化，现保持null。全部canvas固定72*512/416=88.6153846；尸体源高416/360/267/165/156对应显示约72/62.3/46.2/28.6/27，不逐帧放回72。

遮挡：每相BodyRest/真实可见近臂近手/必要盔前景从该相原RGBA独占分区并精确重构；双手家族另有真实FarHand/支持臂，隐蔽手不编坐标。武器若需前后分层必须分配同一源像素所有权，不画两次wholeprop。胸/近肩/远肩、袖/裙摆按真实交叠给每相depth，不能套一张全局Ready mask。整体反射一次，Root/Grip/Axis/prop/甲/mask同镜像，近远解剖角色不交换。

四甲边界：当前新LGT沿已准入紧凑胸/双肩材料构造，不因旧design_only褐皮衣文字擅自改款，也不扩为尚未当前绘制的护臂/胫层。MED旧路线有环甲、短罩衣、前后开衩和中等肩片；HVY有横梁胸、大方肩、裙片、厚胫；ROB有长前后布片、窄袖且实际P2/P3确需near sleeve层。它们只是旧源结构参考，不是新钟盔像素；分别补新低姿/倒地甲层，不能缩放LGT认证。

最少下一轮候选清单：先1条Hurt4纠错body，握持验证后最多3条Dodge4 LGT组件row（Chest/NearShoulder/FarShoulder），最多4请求16位，仅首片准备。完整SWD+当前LGT三状态上限为Hurt4＋9条LGT row/39组件位，共10请求43位；真实完全遮挡部位应明确author-null而非强画，visibility未定前不锁最终计数。Dodge/Death身体和五刚性prop暂不重画，不生成20套整身。GSW/SPR/XBW后续各自Dodge4/Hurt4上肢导向，STF先比较单手可行性；其他三甲数量留null，先立真实新风格设计/层级来源。

风险与可执行交接：state-equipment-contract JSON给13相逐字段null表、20格未配置矩阵、状态时钟/释放边界、配置门和后续真试玩判据；next-generation-queue JSON给分阶段清单。下一步先用真实prop测接触/本相mask/甲visibility并作者化Death根/释放轨道，再按sprite-gen wholecomponent/sharedrow生成纠错及组件；先F/E保全后View，Root随后试装正常Shift、真实poise-break及Death/合法存续。共享body、旧gameplayGREEN和此冻结都不等于20套/全状态72通过。本轮只写NEW候选文本/JSON，无Source/Content/tools/ledger/native/UE/生成/新图。
