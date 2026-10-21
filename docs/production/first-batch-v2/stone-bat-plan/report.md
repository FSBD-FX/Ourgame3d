# ENM-STN-002 纯规则核计划与证据

日期：2026-10-15，Asia/Shanghai。阶段：只读设计计划，等待根结束当前接触回归统一构建并冻结capture后再授权继续TDD。**尚未创建DungeonStoneBat.h、Standalone或Run脚本，尚无RED/GREEN**；不把其他石骑/接触测试、素材或录像记作石蝠运行证据。

## 冻结来源与前提

已读 `F:/Ourgame/docs/design/enemies-v1/stone-forest.json` 的ENM-STN-002全文、common-rules.json、target-profiles.json、`01-石像与森林敌人.md` 的石蝠段，以及D02玩家真实高度规则。根已确认任务原简写“实际Z<=20才可合法近战”不覆盖冻结设计，必须区分：

- incoming近战高度合法性为真实攻击者与石蝠Z差<=65，跳攻可打Z90；不新增Z20以上免疫。
- 真实Z<=20且位置合法才具低位恢复资格；计时不能提前在高处开始。
- 地面身体阻挡实际Z<=40，死亡关闭；高位仍受墙/房界限制。
- A1对地面目标另有实际石蝠Z<=65伤害gate，攻击中心是实际石蝠Z；不是把整段俯冲强行投影到20。

| 项 | 冻结数值/合同 |
| --- | --- |
| 基础 | HP55/甲15/魔抗10/韧性25/移动220；body16×12，hurtbox初值16×12但独立字段 |
| 唤醒 | 近距LOS椭圆180×85或真实正HP损失；完整.80s，不回血/换ID/发奖励；共同12s及其他活敌清除显式兜底，唤醒开始间隔由外层许可 |
| A1低掠啄击 | 前摇.80、锁.40、有效.25、后摇2.10、起招CD3.70；物理12/削韧10；移动椭圆80×30，实际Z容差65；有效期90→20，水平预算260、速度上限1040 |
| A2落翼横拍 | 前摇.80、锁.40、有效.20、后摇2.10、起招CD3.60；物理10/削韧12；椭圆80×35、实际低位Z20/容差65；后半前摇.40s内90→20，水平预算140、上限350 |
| 低位 | 每次接受攻击置pending_low；攻击、落空或破韧后义务不清。合法到20后完整定点至少1.80，再.30升90；死亡可终止；章节/精英不能压缩 |
| 候选顺序 | 锁定玩家点+(70,0)、(-70,0)、(60,18)、(60,-18)、(-60,18)、(-60,-18)、(50,0)、(-50,0)，逐点实际sweep合法/不重叠/在招式水平预算内；锁后不追随玩家 |
| 失落点 | 锁时无合法候选则拒绝有伤下降、保CD/低位义务/扑空提示，连续寻找最近合法低位；不传送/不落在体内 |
| 共同控制 | 真破韧.40s、保护1s、最后削韧后1s再20/s衰减；普通非破韧HP损失不中断；不套Boss抗性/隐含接触伤害 |
| 高位待机 | 仅在CD已好、动作名额可用且存在合法低点时累计上限2.40s；不能把外层slot拒绝算成玩家无限滞空的核证明 |

## 拟议纯接口与边界

新增纯C++17 `DungeonStoneBat.h`：FDefinition、FAction、FState、FMotionSegment、FEvent/FResult与FStoneBatKernel；无UObject/Engine依赖。外层显式请求A1或A2，核不臆造设计未给的距离优先级或攻击随机权重；高待机期限应给明确到期选择/强制下降事件接口，不能以一直不调用TryStart掩盖上限。

FWorldInput仅提供只读真实目标快照、LOS/动作名额/唤醒许可、候选点合法与连续扫掠查询、最近合法低点查询。核拥有实际XYZ、绝对动作/低位/CD/硬直时钟，sweep只能返回最早合法fraction/阻挡类型；无合法查询不能授权穿墙/穿身体。高低身体启用点40、A1地面伤害gate65、实际到20均必须成为运动/事件分段边界，不把夹取终点摊成整段慢速。

攻守同一绝对时间批内按关键时刻细分；真实输入伤害按receipt去重，同点先全量正HP损失/死亡，再决定未发动作和破韧，死亡优先不补发Active或奖励第二次。对外命中准入须读该时刻实际XYZ/原椭圆/LOS/无敌并在成功后才消费{AttackId,TargetId}；不能凭动画或持续遍历每帧重打。

Capture/Restore保全部动作锁定事实、实际运动/未完成下降、pending_low、真正低位开始/完成时刻、各招CD、削韧与保护、发射/命中/伤害去重和一次死亡/奖励凭据。拒绝NaN/倒时、身份/版本/冻结数值篡改、不一致phase与去重游标；失败原子。仅内存快照，不声称D13磁盘事务/Actor持久身份已接入。

计时解释须在实现前明确写测试：A2在ActiveStart已到20，但冻结正文要求“后摇前1.80秒”都低位，因此正常low恢复开始取max(实际合法到20时刻,ActiveEnd)，不能拿A2有效.20抵掉后摇；正常总周期仍.8+.2+2.1=3.1。破韧期间若已合法定点20，真实低位经过的时间可以继续累计，不能因为每次被打把窗口洗掉；未到20则硬直结束继续原义务下降，延后的真正到达时刻才起完整窗口。后续若根要求不同解释须显式复核源，不能偷偷缩短1.80。

## TDD顺序与交付

1. 写最小完整声明桩与Standalone，真正MSVC /std:c++17 /W4 /WX编译成功后观察行为RED，保完整log/退出码；whole Standalone仅自己的RunStoneBat.ps1显式宏启用，宏外TU预处理为空。
2. 先唤醒/真实高度，再两招锁点与连续下降、失合法落点/受阻/低位义务，再伤害同点优先与去重，再完整Snapshot和分帧/长步一致；每阶段先实际RED再最小GREEN，不用编译失败当RED。
3. 验证最终运行全部Standalone、无宏空TU及UE禁异常模式头编译，记录实际检查数量、hash、日志与未覆盖项，冻结给根后续统一UE构建。不得启动UE/UBT、改其他核/Actor/Probe/原29或生成素材。

计划中的动作/伤害事件只用于未来适配器消费；无论Standalone多少GREEN，都不等于石蝠Actor、AI导航、动态LOS、图声、实际来源/存档或游戏实跑已完成。

## 2026-10-15 04:18 真正可编译RED

根取得第29改前置旧源实跑RED后，明确授权恢复本核TDD。本代理新增完整纯类型/行为声明桩、Standalone和指定tools/tests/RunStoneBat.ps1，先写测试后跑行为桩，没有先实现GREEN。

实际执行 `pwsh -NoProfile -File F:/Ourgame/tools/tests/RunStoneBat.ps1 -Phase RED`：MSVC14.38 /std:c++17 /W4 /WX `COMPILE_EXIT=0`，`CHECKS=79 FAILURES=49`，`EXIT_CODE=1`；这是行为RED，不是拿编译故障代替RED。另实际通过wholeStandalone无宏预处理空TU、/EHs-c-且_HAS_EXCEPTIONS=0的纯头编译，Run脚本PS AST解析通过。

完整实际日志：`C:/Users/22499/AppData/Local/Temp/OurgameStoneBat/20261015-041808-383-RED/standalone.log`。测试含两招原时轴/锁点、真实Z/椭圆/地面gate、完整1.80低位、伤后下降义务、同点死亡先于发射、实际命中去重、失落点/无假低位、内存恢复/篡改与原子拒绝等；目前多数尚未实现，不能声称79都已有规则覆盖成功。

04:18后根即将统一构建有向保守接触修复，要求立即冻结所有本代理Source；本代理已确认冻结，当前仍为此RED声明桩，**尚未写GREEN实现**。期间只登记文档/读日志，待根capture启动后再继续实现；不会让UBT读到半写文件。接触第29仍A042…，Probe/PS未改，新石蝠Standalone默认UE宏外为空，不引main冲突。

## 2026-10-15 04:40 实现与最终冻结

根完成保守接触实际expanded29/29 GREEN并启动已固定Source hash的Explore-v003后，明确授权恢复本核。以上RED声明桩/等待记录保留为历史；本节更新为真正Standalone **134/134 GREEN**。没有启动UE/UBT、改Actor/GameMode/Driver/HUD/Probe/原29或生成素材。

### 测试前提纠正与实际TDD链

没有让错误测试驱动违约实现：目标X100时A2的首候选170超140cm预算，按八候选次序应选30；A1预算260才选170。先仅修此预期再重跑79项/49失败的可编译RED。锁点测试读取实际Action.LockAt，不能把十进制1.2当作`.8+.4`的二进制同一点；保护不重置测试比较保存的原StunUntil，不能把2.8+.4武断替换成字面3.2。生产半开边界和时长没有加epsilon。

| 实际阶段 | 编译/行为结果 | 完整本地log目录（均含standalone.log） |
| --- | --- | --- |
| 首次声明桩RED | compile0；79项/49失败；exit1 | `C:/Users/22499/AppData/Local/Temp/OurgameStoneBat/20261015-041808-383-RED` |
| A2预算预期修正后RED | compile0；79项/49失败；exit1 | `C:/Users/22499/AppData/Local/Temp/OurgameStoneBat/20261015-042334-984-RED` |
| 首轮实现中间态 | compile0；79项/4失败；发现测试用了锁点前一可表示时间，未改生产门槛 | `C:/Users/22499/AppData/Local/Temp/OurgameStoneBat/20261015-042752-150-GREEN` |
| 首轮GREEN | compile0；79项/0失败；exit0 | `C:/Users/22499/AppData/Local/Temp/OurgameStoneBat/20261015-042817-846-GREEN` |
| 新高度/快照边界RED | compile0；113项/11失败；exit1 | `C:/Users/22499/AppData/Local/Temp/OurgameStoneBat/20261015-043506-528-RED` |
| 新边界GREEN | compile0；113项/0失败；exit0 | `C:/Users/22499/AppData/Local/Temp/OurgameStoneBat/20261015-043746-574-GREEN` |
| 新中断/恢复/选择边界RED | compile0；134项/2失败；其中1项为StunUntil字面前提，另一项为真实提前SeekingLow恢复校验缺口 | `C:/Users/22499/AppData/Local/Temp/OurgameStoneBat/20261015-043939-674-RED` |
| 最终GREEN | **compile0；134项/0失败；exit0**；无宏空TU与禁异常头编译均PASS | `C:/Users/22499/AppData/Local/Temp/OurgameStoneBat/20261015-044007-268-GREEN` |

这些log阶段由运行命令传入命名；中间目录名含GREEN而检查失败时，照实记录失败，不把目录名称当通过证据。输出仅在独立时间戳TEMP子目录，不覆盖此前结果；报告保留路径与实测汇总，尚未宣称TEMP长期归档或D13持久化。

### 已实现接口与权威

- `FBatKernel(EntityId,StartTime,Position)`：同实体非零ID、真实XY，初始高位Z90；纯FState拥有XYZ/时间/HP/削韧/保护/动作/CD/低位义务、事件与凭据。`Definition()`提供冻结55/15/10/25/220、独立16×12 body/hurtbox字段。
- `StepTo(Now,World,IncomingHits)`：输入真实已减甲正HP损失/削韧、单调独立receipt和真实AtTime；先预验全部输入，再按唤醒/锁点/有效窗/高度65与40/落点/低位/升高/硬直/伤害时刻分段。同点先处理全部输入损失，死亡停止未来发射与破韧，活着的普通非破韧损失不取消原动作。非法query/NaN/倒时/重复凭据原子拒绝，包含事件ID与时钟回滚。
- `TryStartAttack(Peck/Wing,World)`：只在已醒高位idle、原招CD已好、动作名额允许且有合法候选时接纳；起招立刻置pending_low和对应CD。50%锁点才冻结最终目标/端点，之后不追随。A2严格140/350，A1严格260/1040，不共用错误预算。
- `World.LegalLowPoint / NearestLegalLowPoint / Sweep`：显式只读世界供方，必须根据实际墙/身体/房界与真实高度返回最早合法结果。核沿实际fraction提交XYZ，高度40才启用地面身体，始终不借高飞穿墙；正常下降被挡不伪到20、不起低位钟。失落点显示MissedDescent、保CD/低位义务，fallback以移动220与本招派生Z速（280或175）上限连续寻找供方认证的最近合法低位。
- `World.SelectDueAttack(PeckLegal,WingLegal)`：冻结源未给AI权重/两招距离优先，核不编造。只有CD/slot/合法落点都许可时累计高位eligible clock；2.4s到期调用外层明确选择并发DescentDue/接纳实际攻击。缺选择或选非法招则原子拒绝此次推进，不能悄悄接受无限高位idle；真实AI供方及其故障处理仍待Actor适配。
- `TryHit(TargetId,ActualPoint,Grounded,LOS,Invulnerable)`：外层先定位真实连续接触并把核推进到该时刻，且目标必须由外层确认存活/敌对。核检查当前严格有效窗、真实XYZ高度差65、原椭圆、A1地面gate<=65与LOS/无敌观察，成功后才消耗{AttackId,TargetId}并返回一次原物理12/10伤害事件；拒绝不消费。它不是场景连续相交/队伍解析器，不能在帧末一次调用就声称已覆盖批内后来进入/复杂LOS。
- `IncomingMeleeHeightLegal`与`GroundBodyEnabled`分开：地面高度0无法打Z90，但实际跳高25或更高可合法命中；目标Z110.25是有效世界观察，不被石蝠自身最高90误限。自己的XYZ仍限真实0..90；低位资格/定点目标20没有变成全近战免疫门。
- `ClaimDeathReward`：只有真实死态接受一次，后续Capture/Restore保已领取事实，不再次生成死亡/奖励事件；仅在核内表达凭据，不创建金币/掉落或正式来源。

低位：正常A1在ActiveEnd真实到20开始完整1.8；正常A2虽ActiveStart到20，仍在ActiveEnd才开始后摇1.8，随后.3真实升90。未到低位的真破韧先保.4硬直，结束后继续连续下降，真正合法到20才起完整1.8；已在20的低位受破韧保原低位deadline，不借动画清标签或洗钟。只有完整低位履约才清pending并允许升高/下一招，死亡例外。

### 内存快照与实际覆盖

Capture包括初始身份/位置/时间、当前绝对状态、当前及历史完整动作/冻结点/独立CD、未完成低位与升高时钟、实际收到伤害receipt、削韧衰减原点、发射/命中/死亡/奖励事件和游标。Restore交叉核对HP与实际损失、削韧/保护/硬直与收到receipt、位置与已发移动记录、动作与历史/事件时点、pending与LowStarted/LowCompleted、命中去重与Hit事件，以及死亡/单奖励。明确拒绝删掉low义务、伪提前active/seek、在高处伪低位时钟、抹掉命中或伤害历史导致重打/回血等反例。

134项实际检查还包括：完整.80唤醒与伤硬直钟独立、显式12秒/清除兜底与外层wake许可、八点真实顺序、锁后不追随、地面gate65/身体40/有效窗半开、受阻40后不计20、延后真实到20后的完整低位、低位受击/中断不清标签、同点死亡不发active、每target一次与LOS/无敌拒绝后合法再尝试、原CD不退且完整恢复后仍受CD约束、eligible高idle2.4与无slot不假计时、长步/分帧玩法状态一致、正常/硬直/低位/死亡奖励等阶段内存恢复与篡改拒绝、无宏空TU和禁异常模式。

剩余边界：World目标样本和许可在一次StepTo内视作外层提供的有效观察，真实移动/LOS/slot变化必须由未来适配器按实际时点切段；动态导航、碰撞供方真实性、敌对身份、每帧表现和HP消费不由此核凭空完成。移动事件分段数量/事件ID可随caller查询粒度变化，已验证的是相同观察下的动作/位置/低位时钟/攻击ID语义，以及相同分段下快照续行事件一致，不能误称不同物理采样粒度逐事件完全相同。完整历史目前保留在内存，长局压缩/有界日志与D13 IO尚待后续；单次内部转换上限65536，超限整次原子拒绝，调用方需分合理批次，不改玩法时轴。

### 冻结哈希与范围

| 文件 | SHA-256 |
| --- | --- |
| DungeonStoneBat.h | `3B6E39C07D2EC44974652137698957EF13AAD7A238008928D9AC81CD3DDCC300` |
| Tests/DungeonStoneBatStandalone.cpp | `4058201ECCE45AF09C73B57ADFDDB72844DBFEA8CD99BB2B3A556BD944737534` |
| tools/tests/RunStoneBat.ps1 | `B65D4699A2B6E15EDAB59A5C9176C3D2924659D8533DF63D6070AD91FD446B56` |
| 冻结stone-forest.json来源 | `5757EF0E4DA5830546DFF944D1E717C22FBF92E7692229BBADD5B9397AEEA0C5` |
| 冻结common-rules.json来源 | `0296B0D87FC1D16EF1F90D15B73AA08544B7E1C5CA173DB898CF2D20F93976F5` |
| 冻结target-profiles.json来源 | `E5649FF4F5C53F0740126923F2A5A99B73D3E523A2D2DD4DC4E75E60AE85C4E5` |

本交付仅纯规则核与内存测试；无石蝠Actor/UE Driver/AI/素材/音效/特效/实际来源/磁盘保存或游戏录像。此前接触29/29与Explore录像不属于石蝠运行证据。Source已通知根冻结，后续根统一构建不等于石蝠实机验收。
