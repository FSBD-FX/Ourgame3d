# Dodge / 分段运动适配候选独立审查 v001

日期：2026-10-15，Asia/Shanghai。范围：只读Fighter、GameMode、StoneKnightDriver和真实UE报告/Explore原件。根代理统一构建/运行；本代理没有启动UE、UBT、编辑器或外部API。后续按根明确授权新增一个独立UE反例文件、最小Probe正常输入修复和范围文案；没有修改Actor/GameMode/Driver或原28项测试。

## 当前事实与判断

根实际运行 `F:/Ourgame/UnrealGame/Saved/Automation/FirstRoom-20261015-032344/index.json`：**27 Success /1 Fail /0未运行**。新增Dodge4与原独立SWD边界2均Success；唯一失败为原 `CodexDungeon.Content.DamageBatch.AllDueHitsResolve`，错误为GM567零进度ensure，原61HP等业务断言没有另报失败。因此可以登记六个具体回归场景通过，不能登记28 GREEN或所有连续碰撞完整。

根实际Explore26 v001位于 `F:/Ourgame/过程图稿与视频/2026-10-15_军剑技能单石骑探索记忆换房运行_v001`，74个原PNG、实际音轨/时间戳检查通过，但战斗段失败：冲锋窄线跳跃检查FAIL、首盾Y避开FAIL，随后原30秒完成项FAIL、其余未到达。音画同步通过不等于玩法通过；新房记忆流程尚未执行，不能登记探索7项通过。

## 确定问题及复现依据

### B1：正浮点尾数被当成未消费接触，产生零进度循环

源码事实：原候选GM464维护double `Remaining`，569不断减 `ToTime-FromTime`；循环只要求Remaining>0。即使本帧实际上已经到达可表示的终点，减法可留下不足当前SimulationTime一个ULP的正余数，下一次From+Remaining仍舍入成From；17次同值迭代在567触发ensure。

与失败fixture一致的IEEE754算术已独立实际重建（仅算术，非UE执行）：`.47f=0.4699999988079071`、generic前摇`.46f`、最大5ms子批及float AttackElapsed。在第94次后得到SimulationTime `0.469999998807907`、Remaining `2.7755575615628914e-17`；下一To仍等From，Remaining不变。本fixture没有石骑或skill窗可导致EarliestContact回到From，日志又仅有ensure，足以定位为数值尾数，而不是漏消费真实接触。

根已交save_state修成单帧绝对FrameEnd和 `SimulationTime<FrameEnd`，步限 `min(FrameEnd,From+.005)`，保留真实零接触门、不加epsilon、不放宽原断言。收到的修后GM SHA为 `2DB1E6178597E846766CB1960B25684F6492EBD7A7C73FB69A699E00FBA7E050`；本报告形成时仍待根重跑原测试，不能把源码改动当GREEN。

### B2：真实冲锋接触面微内陷，使合法切向/向外运动全部锁死

Explore实际输入与位置：W在sim `6.556830026209354`提出，实际盾开窗 `6.823368218441655`，提前 **266.538ms**；W保持到sim `6.959353126585484`，玩家Y多帧固定 `27.96717864649599`，随后HP100→88.59648895。故不能解释为按键太晚或地面速度不足。

真实位置PlayerX=`42.18300203853069`、KnightX=`84.18300203853049`，相差 `41.9999999999998`，比身体合并半X42内陷约2e-13cm。GM168..177的起点严格Inside为true，故Entry=0；只在“不严格Inside”的分支检查touch moving-away例外。W切向、A向外也被判BodyFraction0，已有几何微重叠没有合法脱离通道。该机制由源码和实际数值确定；Driver110..121同类BodyContact假设也需一致核查，不能仅修玩家一侧后遗留敌人同类锁死。

建议修复接触面几何的合法切向/朝外恢复，同时阻止朝内穿体；不能通过放宽盾32/冲锋24、增加无敌、直接传送或删除实体碰撞规避。新的独立第29项测试详见下节；本报告冻结时尚未取得其实际RED，不将SETUP失败当业务RED。

### B3：普通受阻移动仍缺“到达接触后静止”的时间分段

源码事实：GM217..220仅在Dodge受阻时添加移动段和静止尾段；普通移动225..227只夹取B.End，未添加MotionSegments。Driver PositionAt/RectangleContact因此把普通墙/身体截短后的起终点按整个子批线性插值，等价于降低全程速度；实际应为原速度到达接触面，然后静止。新增分段接口没有完全覆盖该路径。

12次较早接触缩短预查询不保证修好这种表示。独立几何算术例：普通玩家265cm/s，观察5ms，墙使其1ms走0.265cm后停止；盾边界在0.2649735cm处，真实入窗0.9999ms。终点直线给4.9995ms；连续12次重求仍在4.9940033ms，真实Driver按同条弦计算约4.9935039ms，迟约3.9936039ms。合法摆位例可用盾前X50、PlayerY32.2649735、向S、墙顶Y15.9999735（玩家半Y16）形成该接触，真实LOS另作SETUP验证。

这是确定的路径表示缺口；该最小几何/HP反例**尚未UE实跑**，没有新增假失败测试。GM的PendingDamage虽存AtTime并排序，真正ApplyCombatHitInternal仍使用推进后的当前核时钟；它依赖“已切到最早真实接触”的前提，因此12次不收敛时不只是日志时间偏差。建议普通受阻也保存实际接触时刻/静止尾段，并加入“接触贴近受阻位置、细分与单批结果一致”的回归。

## 尚未证实或已有公开边界

| 项目 | 独立判断与最小后续检查 |
| --- | --- |
| 技能发射与真破韧恰同点 | 新GM先提交原窗/石骑接触，再消费新ForwardStep/ActiveWindow；恰同点真破韧会压掉技能新发射，普通主攻却先排入伤害。原A只证明“更早1ms”正确，不能证明等时优先政策。D03的道具提交伤害优先不自动规定武器同点政策；需明确合同并分别测Contact=ActiveAt前一可表示点/恰等/后一可表示点。不把政策疑问列为已证bug。 |
| 非单调LOS可见岛 | 作者已公开16探针+二分只覆盖解除后持续可见。独立读取确认skill和Driver均如此；小于探针间距的中间可见岛、同一bracket内多次开闭仍可能漏早接触。旧B通过只证明本次最后窗持续解除。不是新的隐蔽发现，也未在本轮另加反例。 |
| 多移动体互相预测 | 先生成未解析Bodies、预估Knight，再解析普通/闪避；真实Knight随后对已解析玩家重新查询，预估端点可能变化。需两个冲锋/普通移动体相互迎头及“第三墙先截一体”的实跑，不凭静态推理认定已穿体。 |
| MotionSegments输入校验 | Driver ValidFrame验证有限/区间合法，未要求有序、不重叠、完整覆盖、端点连续；PositionAt倒序取段，而MotionSlices只遍历所给段。当前Dodge生产者给完整两段，未证实内部会生成缺口；公共输入若推广应补非法重叠/空隙原子拒绝测试。 |
| 观测频率与成本 | 实际录制相邻原帧最大110.172ms，首帧93.295ms；不能用30fps输出倒推30Hz实际观察。本录像不是性能基准，不能据此断定新增预查询或新场景哪个造成耗时。正常输入夹具须按真实位置/动作检查，不靠固定50ms pulse。 |

## 接入中守住的部分与未完成范围

- 较早接触：只读Driver副本和既有skill窗先预查询，缩短真实批次后才推进真核；没有倒退/重建真核。真实A已经Success，较早破韧对应的未来前踏不再逃逸。GM把AtTime带到PendingDamage排序，但上文B3说明完整准确性仍依赖切批收敛。
- 保护余窗：Driver按几何entry/exit减去旧hurt与Dodge半开区间并集，保护结束若仍在窗内会重新准入；保护覆盖完整窗不消费命中。默认legacy仍沿旧布尔合同，新Dodge余窗测试已经Success。身体阻挡与能否受伤继续分开。
- 位置交接：普通移动、实际技能前踏、普通NextRoom均调用同一Dodge核 `CommitResolvedIdlePosition`，使用NextPositionReceiptId，不重建/CD重置；位置相同不消耗新凭据。接纳闪避的资源/空攻预算没有新扣除，失败请求不先撤换甲/链。真正玩家击退路径目前没有实现，不能拿旧generic敌人24cm直接推位证明“玩家击退已合法碰撞并交接”。
- 单Focus：仍只有Fighter的SpendFocus/自然恢复是当前活路径；零成本SWD的WeaponSkillContext.FocusRegen=0，Dodge不引入第二套恢复。五武器共享专注、外部扣还、弩杖发射和D13磁盘保存仍未由本候选完成。

## 第29项独立反例冻结

新增且仅新增 `F:/Ourgame/UnrealGame/Source/CodexDungeon/Tests/DungeonBodyContactReviewTests.cpp`，唯一测试：`CodexDungeon.Content.BodyContactReview.RealChargeRoundoffAllowsTangentAndEscapeButBlocksInward`。全文件WITH_DEV_AUTOMATION_TESTS保护，不改原28项。

有限三组初始spawn X：真实录制42.18300203853069及近邻42.183/42.1。每组真实Game/Physics/Controller/StoneDriver，近距自然苏醒、自然冲锋、production StartJump避伤、真实BodyStop、正常落地；只有实际读到0<42−Gap<1e-9微内陷才进入业务段。接触后没有SetActorLocation、HP/Z覆盖、直接伤害、kill或假回调。若三组未生成该端点，明确SETUP失败，不造业务RED。

业务段真实Controller W切向应移动并交接位置凭据；D向内仍挡；A向外能脱离；再D返回不能穿体；同一Dodge身份/CD/clock保留，玩家/石骑HP与奖励无造假。这里W/A是头less真实Controller held路径，起跳使用已有production API，不冒称完整物理键盘或Shift录像。

测试SHA-256：`737DEBAE2816904A1086B2A20B31A1359FAB6D01C22B99B5411A66C755F220FF`。静态唯一名/guard/无接触后直接写位检查完成，实际RED/GREEN待根统一29项；不能预报一定业务RED。

## 探索v001夹具原因与获准最小修复

冲锋实际HP一直100、峰高109.773、真正Stop=Body；失败是锁后W在sim3.782356→3.880075把Y0移到27.967，超原窄线24。因此检查拒绝把横向已经移出窄线的过程当成“跳跃避伤”是正确的，不改检查。根明确批准改为一次正常W+D归一斜行，下一个真实Probe观察即放键；同帧长度下Y约19.78。仍从实际位置判断至少5cm锁后变化、原24窄线/65高度/HP/真实BodyStop；未来超长帧仍可能真实FAIL，不调慢角色、不设fixed delta。

Probe/PS最新范围文案按根刚导入的圆盔idle+三primary共24帧候选更新，其余walk/secondary/air等旧。实际纹理路径与尺寸仍记录供根抽帧审查，不能以26通过宣称全骑士完成。六个录音函数对失败v001保留源码快照逐函数完全相同；新26名单和charge_jump判定也逐字相同，仅正常输入路线变更。

最新冻结：Probe.h `4060B24E214C63686960904BBCCEEA1DD4564D6BD826B90B37FE8A12BF008833`；Probe.cpp `6E67A05AD7F6D33758E3785E841DFCDC70DAD5E4F8D6AB9D718F373160868BC3`；PS `8D3B2039CFD85954F19F6044FC725A7F0F4BEE003C3BB6E8CB4663E9B0346616`。该修复待统一构建/新版本实际录制，v001失败原件继续保留。

## 审查版本

Fighter.h `6DBD603E1AA727D864BCF0EC07F23B690454E8FF8B1348B891C56F651F2ED102`；Fighter.cpp `536C76D081C19D218E0872F28EE3B82B2DB6C263BC162BDCD1D4F11E92373F53`；GameMode.h `53A00EA1919577E7562AB9BA676C317A9599B234CBFC2249B06A3F3AB9EB8A53`；GameMode.cpp审查起点（只含根lambda修正）`272C0AB241187B6F8CE3745C615EED7EB154A8BEAD8EBF34AF40223D938766BF`，FrameEnd候选另列B1；Driver.h `82CD23473132B2B78337F1FAB151E8DAA88F1394FC133183184EEB9A2BD323A8`；Driver.cpp `F993602D3A99443EAC32A9ED3564BA10B00D08E4CD1177CF354FB51D047D39F0`。原DamageBatch测试SHA `3F5DB0EF64E229FC01AF5EF7221155FAC5E871CB0D68C8CAB999C2A4A39D9B88`；本代理未修改。

## 后续实际29 RED→GREEN及回访扩展

已独立读取根随后实跑报告：`F:/Ourgame/UnrealGame/Saved/Automation/FirstRoom-20261015-033944/index.json` 为28 Success/1 Fail，唯一第29项业务RED，全部SETUP通过。首seed真实Gap42.000000000000057非内陷，次seed42.183由真实冲锋得到Gap41.999999999999879（内陷1.2079226507921703e-13），W切向、位置凭据增长和A脱离三条业务失败。源码没有事后写位置制造偏差。

save_state最小修订允许最浅重叠面上的切向/朝外，保朝内阻挡、无距离epsilon；根 `FirstRoom-20261015-034706/index.json` 实际29 Success/0 Fail/0未运行，第29同一真实seed端点与原断言全部通过。该GREEN只覆盖原W切向/A脱离/D返回范围，不自动覆盖从Y范围外回访同一X面。

根Explore-v002实际冲锋跳避及首盾W避开均PASS，但`return_to_locked_line`一直卡Y36至原30s截止，HP100。真实PlayerX79.07001292197535、KnightX121.0700129219752、Gap41.99999999999985；W出Y>36后S返回，在slab重新进入Y范围时遇到微内陷X面，又把纯切向返回判成朝内新接触。这是有实录证据的另一路径，不能靠放宽原返回Y<=5或删掉身体碰撞验收。

根授权同一个第29项保留全部原断言，追加真实W-out/S-back：初次W.05s到Y约13.25，继续正常W.10s到Y39.75>36，再正常S.14s应回Y约2.65<5。全程在同一真实冲锋恢复内，没有接触后写位置。新增S业务断言若失败立即结束，避免该错误位置污染下游原D阻/A离/D回断言；修复GREEN后下游原断言继续执行。测试名/数量仍为一个新增项，总29，不新增第30。

扩展冻结测试SHA：`AAA0DFE7DE2773081308F744E90D99EF3EDCCC963D79E87005394C59141FD2EE`。形成此补充时待根统一实际RED；Probe/PS保持前节冻结SHA不变，石蝠仅研究设计未写Source。原Explore v001/v002失败媒体与29原版RED/GREEN日志均保留，不互相覆盖或冒充新扩展已通过。

随后根实际 `FirstRoom-20261015-035613/index.json` 为28 PASS/1 FAIL，扩展第29全部SETUP通过，真实outsideY39.75、S返回Y36、Gap41.999999999999879，新增S业务断言失败；原版RED/夹具/DLL/report已由根另存 `bodycontact-crossaxis-RED-v008`。本代理未执行该UE运行。

保守扫掠候选将允许从fraction计算最邻近可表示的非重叠落点，正确修复后不必继续制造原tiny-inside。根因此明确授权只更新第29SETUP：三组真实冲锋全部尝试，优先真实tiny_inside，若全部无inside才选真实near-outside/exact；保留原1e-9近面读数分类窗并对两侧分类使用，不用于生产移动/伤害容差。每组及最终选择均输出17位rawGap、signedRoundoff与分类，未改差值为0，没有跳过业务。

该SETUP修订SHA为 `A042A1C6EA2703748423BDFC93FA678D9107C1BB0EA5A6911571B2B8607F37DE`，W/S/D/A全部业务原文与条件不动、总29不变。根将先在旧GM `DBB606C932E114D9330A08F136ED750AF2F4F57F0AF3BCBF82F04B3C99F45D70` /Driver `3D5D905EB9A6E466E8512BFC32C6740CE6510774FD911B156956464C699C8CF6` 上再次运行应有RED，以证明SETUP修改未稀释业务，再授权运行几何修复；此处尚未记录该新实跑结论。

后续根已实际完成上述对照：`FirstRoom-20261015-040803/index.json` 单独BodyContact测试0 PASS/1 FAIL，三个自然rawGap/最终tiny_inside输出与全部SETUP通过，S仍返回Y36；更新前置没有稀释业务。test/DLL/report由根另存v009。

保守fraction运行修订后，根 `FirstRoom-20261015-042039/index.json` 实际expanded29/29 GREEN，仍使用A042…测试；本代理没有改W/S/D/A业务或运行源码。根随后冻结314files/DLL/资产v010并启动Explore-v003；该录制状态不自动代表26已通过。普通受阻尾段B3与复杂LOS等公开边界仍未因29 GREEN消失，本审查不把它们关闭，也不把石蝠独立Standalone GREEN混作接触/UE实跑。
