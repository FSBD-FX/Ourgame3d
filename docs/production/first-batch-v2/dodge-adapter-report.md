# Dodge UE 适配记录

日期：2026-10-15，Asia/Shanghai。阶段：可编译RED准备；未实施GREEN、未构建或启动UE、未改纯核/HUD/Probe/原22测试。

## 真实起点与接口桩

已读取根节点 `test-logs/ue-swd-skill-GREEN.json`：22项全部通过；原SWD、甲、石骑反馈、终局代码保留。已读Dodge v2纯核及报告/独立review：164检查与11复审场景覆盖内存合同，不能证明Actor接线。纯核SHA为375ee1aa3d83612a3c686f0b1a6a6d322c97e247ea957c3d7380dcd431fd9ec2，本轮只读。

只新增最小可编译桩：Fighter::TryBeginDodge(MoveIntent,FreshPress)返回false，IsDodgeInvulnerableAt返回false，GetDodgeState只读占位核状态。占位尚不推进任何权威，不重建/干预目前运动或旧无敌。Green之后须按真正新Run创建身份与起点，而不是在移动/换甲/房间时重构。

Driver.h只新增FDungeonDirectInvulnerabilityInterval{Start,EndExclusive}及Body的bUseTimedDamageAdmission（默认false）/区间数组；Driver.cpp未修改，现逻辑尚不使用新字段，保留缺行为取得RED。默认legacy字段不改原Driver5项含义。后续必须按几何相交的entry/exit减去区间，不能只在entry看一次、不能将一整个5ms统一判无敌。

## 我方4项新测试

新增文件 Tests/DungeonDodgeAdapterTests.cpp，均为CodexDungeon.Content.DodgeAdapter前缀：

1. FixedMotionAndIdlePositionHandoff：无甲/四甲固定185/0.4/起招+1.2、斜向归一与空方向facing、真实旧普通走位26.5后位置专域凭据交接、完成后普通移动再下一次dodge且核/ID/CD不洗；真实石骑身体截至58、注册墙截至27，受阻保全时轴。
2. CompositeCancelAndActionExclusion：只有成功dodge才撤未提交甲；CD失败保甲进度并允许正常完成；活动主攻缓冲/技能拒绝dodge且不改原工作；fresh拒绝不清地面链、成功才清；空中非法且不动空攻token。
3. DirectIntervalsAndResolvedInterrupt：新fixture分别实际接触+.059/.061/.199/.201避免旧hurt污染相邻边界；历史精确+.06/.20查询；普通非破韧保dodge、真实早期阈值break保CD/停止运动/不能激活未来保护；死亡关闭并冻结核时钟；旧hurt与dodge区间并集不加时长。
4. StoneTimedWindowResumesAfterProtection：真实UWorld/Driver/Actor、实际核苏醒和自动A2；冻结明确区间覆盖首entry但结束早于有效窗末，期望余窗首次命中恰在保护结束、去重不补第二次；区间覆盖整个窗则零命中。该子场景直接给Driver冻结观察，不能冒充玩家Shift已经成功；Driver查询不扣Actor HP的断言仍保留。

我方计数为原22+4=26。root授权的独立审查者另写DungeonSkillBoundaryReviewTests.cpp两项，合并预计28，实际以根运行报告为准；没有复制或重写旧22。

## 共同前提与停点

已实际读取swd-skill-adapter-review.md。批内早破韧/未来技能消费顺序、最后窗内LOS解除两项目前是待真实UE复现候选，不冒充已修复；独立review负责它们的真实反例。Dodge后续GREEN必须解决实际接触时序与保护区间刷新，不通过扩大无敌、epsilon或忽略旧伤害绕过。运动轨迹的瞬时前踏/受阻尾段也须与Driver观察统一，不能只给真实终点便称全批轨迹正确。

只读短计划见dodge-adapter-plan.md。根线程取得真实可编译RED前保持实现空桩；后续实际Shift边缘输入、联合运动/伤害、受阻录像、D13全代保存均待对应运行证据。API fresh参数断言不作为物理键盘验收。

## EV-042：运行房间空间独立变更

用户指出人物/怪物偏大、场景拥挤与探索不足。根线程授权先扩大运行房间中心空间，建议值X[-1350,1350]、Y[-420,440]cm；新公共DungeonRoomLayout.h是该运行边界唯一来源，提供MinX/MaxX/MinY/MaxY与CenterBounds()，供HUD滚动相机读取。角色缩放、相机、场景绘制、探索fog和遮脸骑士形象由根/素材负责人处理，本次仅共享逻辑空间。

普通Fighter移动XY clamp、旧原型受击推位X clamp、SWD实际前踏边界及GameMode传入石骑Driver的运行Frame.CenterBounds均读取同一头文件。出生点、数量、HP、移动/攻击时轴、掉落与原普通出口判据不变；扩大边界本身不增加房间结构或探索奖励。

纯Stone/Dodge核与Driver默认[-700,700]/[-200,220]夹具边界保持原样，原5个Driver显式输入合同不扩。旧22及Dodge4没有断言运行墙边必须700；近处真实墙27/身体58等几何断言不受扩界影响。没有改旧测试来隐藏边界差异。Dodge入口仍为空桩，未提前GREEN，未构建或运行UE；等待根统一新范围/独立review测试及图形实录。

## 2026-10-15 03:15：真实RED后的实现候选 v001

事实：已收到并读取 `test-logs/ue-dodge-skill-boundary-RED.json`，实际28项中原22全部通过、新Dodge4失败、独立SWD review2失败；review两项SETUP均通过。A已证明1.550000000000真实盾击/破韧早于1.551000293158技能前踏，旧实现仍前踏并对石骑损HP22.069；B已证明最后合法窗内实际W移动解除真实墙LOS后仍漏伤。前文“候选/尚未复现”是RED准备时的历史状态，本节显式更新。

当前仅为待根统一构建和28项实跑的实现候选，未宣称GREEN。未自行运行UE/UBT；未改原28项断言、纯Dodge/Combat/Weapon/Stone核、HUD、Probe或独立review文件。共享扩大RoomLayout未变，Driver默认夹具边界未扩。

### 调用与权威

`TryBeginDodge(MoveIntent,FreshPress)` 现接持有的FDodgeKernel。正常左右Shift fresh按OR合并一次，WASD/箭头八向取起招方向；无方向由核取起招facing。严格拒绝空气、伤硬直、主攻/技能与CD不合法请求；成功之后才清未提交甲/主攻链/未执行缓冲，失败不取消原工作。当前SWD之外装填尚未接UE，不能将未来五武器装填/专注迁移称完成。

新Run由ResetFighter按QA实体身份和真实出生点创建核；普通走位、技能前踏、普通跨房只用同一核的CommitResolvedIdlePosition与NextPositionReceiptId专域游标，不重建核、不洗CD。GetDodgeState/IsDodgeInvulnerableAt为既有只读接口。活动表现名称为 `dodge`，AnimationTime由核Time减该Record.Start；HUD素材适配仍由根负责。

GameMode继续以5ms为最大观察跨度，再切到primary/skill/石骑锁点、有效窗/完整恢复、Dodge .06/.20/.4与旧保护/硬直/甲提交边界。只读复制Driver预查询和既有skill窗查询找到更早接触后缩短本批，绝不回滚真实核。`FPendingDamage`新增真实AtTime并稳定排序；同点已接纳伤害仍共用原准入，不让第一击新hurt保护排除其它已接纳同点伤害。

运动先生成冻结Body起终/高度及必要受阻尾段，再实际镜像已解析位置；Actor计时/自然专注/弹道速度仍只推进一次。世界对象box sweep与实体相对身体扫掠共用QueryResolvedMovement，身体为玩家18×16/石骑24×20；公共房间CenterBounds仍为扩大值。它没有制造内墙，真实世界无注册碰撞物时只有中心边界/身体。普通公开MoveOnGround也先解析墙/身体再交接位置凭据。

技能端点事件由纯核排队后，先提交较早/同点真实伤害；实际破韧/死亡取消后不消费前踏或新有效窗。存活合法事件才实际前踏/查询当前位置/提交技能伤害；先前区间不含未来30cm瞬移，下一段从实际落点起。当前仅SWD零成本路径，纯武器核仍不拥有/镜像Fighter的实时Focus；五武器资源、投射物与同点付费发射的完整原子调度必须在后续迁移单独验证。

真实未破韧HP损失保Dodge；真实区间外破韧/死亡按Dodge当前绝对Time中断，保原ReadyAt并裁短未来保护。终局仍仅推进死亡表现，不推进SimulationTime或任何核时钟。旧hurt保护和Dodge半开区间取并集，不相加。

### Driver观察与剩余有效窗

Body的timed模式现忽略旧整批bool猜测，使用DirectInvulnerabilityIntervals求几何entry/exit内首个实际合法点；保护覆盖首次接触时保留余窗，覆盖完整窗时不命中。默认legacy=false仍沿原bool合同。新增MotionSegments为绝对起终时间/位置/高度和可选端点排除，表达受阻后静止；运动/伤害查询均无Actor HP、资源、奖励或反馈副作用，真实Batch才进入既有提交/日志。

skill和石骑LOS在首次合法几何点受阻后会继续查询剩余合法窗，含半开窗末的最后可表示时间；找到真实阻挡→可见区间后再二分查询首个可见点，不把有效窗延长epsilon。风险：目前对剩余LOS窗使用16个真实查询探针及二分，覆盖本次“解除后持续可见”反例；不能声称对任意复杂/动态场景中小于探针间距的短暂可见岛已给出完备连续几何证明。多移动体互相接触的预测成本/一致性、长局历史大小和正常双Shift输入仍须真实复核/录像；D13磁盘保存尚未实现。

### 冻结与待验证

最后运行源码写入：2026-10-15 03:15:22 Asia/Shanghai。六个变更源码候选SHA256：

| 文件 | SHA256 |
|---|---|
| DungeonFighter.h | 6DBD603E1AA727D864BCF0EC07F23B690454E8FF8B1348B891C56F651F2ED102 |
| DungeonFighter.cpp | 536C76D081C19D218E0872F28EE3B82B2DB6C263BC162BDCD1D4F11E92373F53 |
| DungeonGameMode.h | 53A00EA1919577E7562AB9BA676C317A9599B234CBFC2249B06A3F3AB9EB8A53 |
| DungeonGameMode.cpp | 8C80497A3465BF84CAC6F8A1839565875427B18918622ABF1006A98AAEA930AD |
| DungeonStoneKnightDriver.h | 82CD23473132B2B78337F1FAB151E8DAA88F1394FC133183184EEB9A2BD323A8 |
| DungeonStoneKnightDriver.cpp | F993602D3A99443EAC32A9ED3564BA10B00D08E4CD1177CF354FB51D047D39F0 |

只读核SHA核对一致：Dodge375ee1aa…fd9ec2、Weapon574b8090…b82db、Combat0becdef8…d6a5、Stone1c5a6813…758b。Dodge4测试SHA保持7c7da95854f585d815b3e6451e0ed1ddc41ca678f19bc3633964ef0d12a8bd53；独立review2保持4b9e7845205cb8eed62cf1beda5364cf3063eb33b60754a9cca2a16ebe7f0731（完整实际文件hash由根索引采集，以文件为准）。等待根统一编译、原28项和正常输入录像，编译/实跑结果另追加，不以静态检查替代。

## 2026-10-15 03:28：实际27/28后绝对帧终点修订 v002

根实际构建032251成功（根补Capture lambda的`this`），实际UE032344为27通过/1失败：Dodge4和SWD review2全部通过，唯一原DamageBatch.AllDueHitsResolve触发no-progress ensure。独立审查定位.47f/.46f分段后Remaining累减尾数约2.775e-17，当前clock约.469999998807907，`clock+Remaining==clock`；没有真实接触仍会进入17次零步检查。

最小修订只改GameMode帧终止方式：开始冻结`FrameEnd=SimulationTime+double(DeltaSeconds)`，循环条件`SimulationTime<FrameEnd`，最大候选终点`min(FrameEnd,SimulationTime+.005)`。不再累减Remaining，不加epsilon、不跳过真实接触。更早真实contact将候选压到FromTime时，原零步计数和断言仍保留。根的`[this,&Bodies]`编译修正保留，测试及纯核均未改。

独立Python IEEE算术复算仅证明该尾数原因及绝对终点控制：保.46f边界/5ms上限，95个正步后精确停在float32(.47)转double值0.4699999988079071，零尾数步0。该算术没有运行UE或替代DamageBatch测试。最后运行源写入2026-10-15 03:28:54，DungeonGameMode.cpp新SHA256为2DB1E6178597E846766CB1960B25684F6492EBD7A7C73FB69A699E00FBA7E050，其余五运行源沿v001冻结。

根另报告Explore26 v001实际失败（normal_y_input_did_not_avoid_first_shield、charge_jump），该媒体与音频同步结果分别留档。等待独立审查真实trace；不把当前候选、27/28或早段画面表述为完整GREEN/可玩验收。

## 2026-10-15 03:38：同房重开探索失效序号

根静态确认RestartRun复用同一个Player且房号1→1时，HUD原有Owner/Room变化检测无法识别新一局。按根授权仅新增GM只读 `uint64 GetRunRestartSerial() const`，私有成员从0开始；RestartRun确认Player有效、无失败return之后递增一次，NextRoom不递增。它仅为内存表现失效序号，不是D13 RunID，不改变角色资源或玩法规则；HUD记录和比较由根接入。

接口冻结03:38:03：GM.h SHA9B86FC16C8368AD3F4D51C2761607AC70F978DA9C5625FB8D4853926CEBDCD79；GM.cpp SHAE77D1005AEA1876FC04FEBF58E63766A1379DFE8A2F13AFFA38827A8E367C2C8。前述FrameEnd修订保留，BodyOverlap尚未修；独立第29测试SHA保持737DEBAE2816904A1086B2A20B31A1359FAB6D01C22B99B5411A66C755F220FF，待根真实RED。未构建/启动UE，正常R重开显示另待实录。

## 2026-10-15 03:42：自然冲锋接触面锁死修订 v003

真实证据由根运行：build033839成功，FirstRoom-20261015-033944实际29项为28通过/1失败，原28（包括DamageBatch尾数修订）全通过。新BodyContactReview全部SETUP通过：自然苏醒/冲锋/起跳/身体截停/落地得到KnightX84.182999999999879与Gap41.999999999999879，向内误差1.2079e-13；W切向、位置凭据增长、A脱离三条业务断言失败。没有接触后传送制造偏差。

本次只修身体扫掠起点重叠：entry=0且起点严格在合并身体内时，以最浅重叠轴作为最近接触面；该轴的有符号相对运动切向或朝外时允许恢复，朝内仍在0截停。用起点方向与相对增量的乘积判方向，不用终点绝对距离，因而不会把穿到对面误认作脱离。不加人为接触/伤害距离epsilon，不改盾深度、冲锋深度、无敌、HP、动作时轴或位置。

相同方向判据用于GameMode.QueryResolvedMovement（普通/Dodge）、GameMode.SweepWeaponStep以及Driver.BodyContact，避免三条身体路径对既存重叠有不同恢复含义。原外部起点的slab首次接触，以及精确贴面时的既有“离开/切向不穿入”判断保留。没有修改纯核、29项测试、HUD或Probe。FrameEnd与RunRestartSerial修订保持。

最后运行源写入03:42:35：GM.cpp SHA256 DBB606C932E114D9330A08F136ED750AF2F4F57F0AF3BCBF82F04B3C99F45D70；Driver.cpp SHA256 3D5D905EB9A6E466E8512BFC32C6740CE6510774FD911B156956464C699C8CF6。独立第29文件仍737DEBAE2816904A1086B2A20B31A1359FAB6D01C22B99B5411A66C755F220FF。未构建/启动UE，等待根29项和Explore26实际复验，不宣称已GREEN。

范围限制：已读取独立dodge-adapter-candidate-review-v001.md。普通受阻路径缺静止tail为已确认结构缺口，根决定另加真实反例验证后处理，本轮没有悄悄改它；LOS短可见岛、恰同点技能政策与多移动体仍沿该独立审查的证据边界。该几何修订和后续29通过也不能表述成“全连续模型已接受”。

## 2026-10-15 04:14：跨轴返回边界与有向保守fraction v004

事实更新：上一轮根实际29项全通过，但Explore-v002仍真实失败：W避盾/跳避冲锋已经通过，W离开身体纵深后S回到Y36再次粘住。实录GapX41.99999999999985；原修订只处理“起点严格在体内”的切向恢复，没有处理从纵深外重新进入时仍有X微内陷的路径。独立作者扩展第29业务为真实W-out/S-back，根实际RED为原28通过、新29失败；新增返回断言失败，旧先段及全部SETUP通过。

根随后明确授权独立作者修订SETUP分类，避免将“必须保留tinyinside”变成修复限制：三样本真实自然BodyStop优先tiny_inside，无inside才可选真实近面outside/exact，输出原始Gap及有符号误差；原W/S/D/A业务不减。该前置修订SHA A042A1C6EA2703748423BDFC93FA678D9107C1BB0EA5A6911571B2B8607F37DE，先在旧生产源真实重跑：build040506成功，FirstRoom-20261015-040803 **BodyContact过滤单测试0通过/1失败**，SETUP全通过、仍选tiny_inside_preferred，W-out39.75/S-back36业务失败。原RED/旧测试与前置修订已由根保留，当前实现没有改测试。

本次从新接触的返回fraction解决舍入，不靠历史接触记忆、任意距离epsilon或Actor额外推位。原slab仍给原始首次接触；从原接触比例向起点一侧，用接收者真正的端点算式验证进入面，求最近可表示的严格外侧fraction。只有最终选中的身体停止结果采用保守值，同一个fraction交核计算停止时间/位置；其余动作End、CD、伤害/无敌/纵深不变。已有起点重叠的方向恢复规则保留，但不再用它猜新接触应容许多少内陷。

共享纯算术位于既有Driver.h的DungeonContactGeometry::ConservativeBodyFraction，无新权威状态/保存布局。55次以内只读二分直至相邻可表示值；外侧判据严格比较实际重建的相对坐标和原身体半尺寸，没有world-distance常量。现有Driver Body路径把局部Entry转绝对时间再转回fraction，会引入实际舍入；端点验证包含该结果，不能只信几何比例的纸面精度。

各接收公式逐一对应：

- 石骑核：`From+(To-From)*fraction`，接触时间为`FromTime+dt*fraction`。Driver先按原始几何比例比较、保持同点valid hit > wall > body，再只对选中的Body停止采用保守fraction，不让舍入返退抢走合法命中优先级。
- 普通移动：与实际镜像/MoveOnGround相同的FMath::Lerp；合法位置仍进入同一Dodge位置凭据域。墙优先/同点wall-before-body仍按未舍入比例选择。
- Dodge：核分别记录BlockedAt与Travelled；fraction==1用TargetTravel，否则`oldTravel+(TargetTravel-oldTravel)*fraction`，位置为`Origin+Direction*Travelled`。适配验证直接用此公式，不能用Q.Lerp近似或从BlockedAt反算。实际返回同一个fraction，保Time/Position/Travelled联验，不重建核/CD。
- 技能前踏：实际ActorPosition+SignedStep*fraction；返回的真实delta直接提交，不额外改Actor落点。

临时IEEE算术复核不等UE测试：20,000个按当前Driver时间往返/位置公式的坐标和1..1000s时刻样本，旧9,859端点内陷，保守验点20,000均外侧，最大数值返退3.54e-11cm，由坐标/时间ULP决定；另20,000含斜向Dodge累计路程样本，时间/距离联验最大差2.84e-14cm，小于现核原1e-7验证界。没有修改该核验证界，也没有以算术结果宣称实跑GREEN。

最后运行源写入04:14:38，候选冻结：Driver.h SHA77102F14544DE4D12D77E47744DA18C629243762F8010B79C703BB761C2BDC78；Driver.cpp SHA5EDB5604B7BC68EAD825CD8BB6FC34F8ACDD522FAE6AFF9F0BC628D0EEB108F2；GM.cpp SHA5141AD44C8CB4037A34D1E2A70BC9C643B3542BDB4AC42FADD3A5D3515A3560C。四纯核SHA原样，独立第29仍A042A1C6…607F37DE；Fighter/GM.h、FrameEnd、RestartSerial、RoomLayout、HUD/Probe均未动。未UE/UBT，等根全29和Explore26-v003实跑。

范围仍有限：本修订验证新身体停止的可表示端点；没有修普通受阻静止tail或宣称完整多运动体/非单调LOS模型，未增加磁盘档迁移或自动修补历史存档位置。
