# 石像骑士行为核：首单元接口与验证

2026-10-14，Asia/Shanghai。交付状态：纯 C++17 行为核已实现并独立测试；未接 UE、未运行物理或游戏，不代表首批敌人完整制作完成。原 D05 与首批合同只读，所有新文件限本任务 ownership，无付费生成、Git 提交或旧 combat 核修改。

## 依据与实现边界

真实来源：

- `docs/design/enemies-v1/enemies.json#/enemies/0`；`/stats`、`/body`、`/activation`、`/attacks/0`（ENM-STN-001-A1）与 `/attacks/1`（ENM-STN-001-A2）。
- `docs/design/enemies-v1/common-rules.json#/behavior`、`/attack`、`/charge`、`/dormancy`、`/control`、`/encounter`、`/reward`。
- `docs/design/enemies-v1/target-profiles.json#/profiles/0`，身体与受击体各自24×20cm半尺寸；近战按目标中心，不把受击体扩进攻击矩形。
- `docs/production/first-batch-v1/content-contract.json#/ordinary_enemies/0` 与 `/completion_contract`；当前生产计划 `docs/superpowers/plans/2026-10-14-first-content-runtime.md` Task2。

事实：原骑士110HP、45甲、20抗、60韧、185cm/s；休眠可伤、计入清房，同实体苏醒不回血。A1为20物理伤/24削韧，A2为13物理伤/18削韧。核仅接收调用者已结算的实际HP损失与合法削韧，不再次套甲抗。

实现取舍：A1的140—500cm采用地面XY距离，另验absY≤55；锁定目标XY并沿固定归一化2D直线冲锋。A2近身条件采用absX≤90、absY≤32，仅锁左右X朝向。普通观察使用共同规则650×250cm半尺寸和LOS，休眠靠近使用精确260×110椭圆。追近先对齐Y，再接近X；不穿过42cm双方身体X半尺寸和，真实墙体/身体截停仍由扫掠确认。攻击接受由调用者显式请求，StepTo不自动连发新攻击，以便遭遇系统先授予行动槽。

风险：此处扫掠均为测试夹具，尚无真实墙体/受击体/LOS/玩家高度/无敌验证，不能把直线算术通过视为完整UE敌人已完成。实体的全局键、D07名额和苏醒间隔、章节/精英派生、属性状态/推拉、导航、正式动作/声音、掉落来源和D13磁盘bundle仍待适配。

## 精确公开接口

头文件：`UnrealGame/Source/CodexDungeon/DungeonStoneKnight.h`，namespace `DungeonStoneKnight`。

~~~cpp
FKnightKernel(uint64_t EntityId, double StartTime=0, FPoint Position={});
static FDefinition Definition();
const FState& State() const;
FResult StepTo(double Now, const FWorldInput&);
EAttack ChooseAttack(const FWorldInput&) const;
FResult TryStartAttack(EAttack, const FWorldInput&);
FResult ApplyResolvedHit(double ActualHPLoss, double LegalStagger, const FWorldInput&);
bool BeginCombat();
bool NotifyOtherAcceptedEnemiesCleared();
bool TryMarkMeleeHit(uint64_t AttackId, uint64_t TargetId);
bool ClaimDeathReward();
FState Capture() const;
bool Restore(const FState&);
~~~

`FPoint={X,Y}`；`EAttack=None/Charge/Shield`对应无招、ENM-STN-001-A1、ENM-STN-001-A2。`EPhase=Dormant/Waking/Idle/Windup/Active/Recovery/Stunned/Dead`。

`FWorldInput`含HasTarget/TargetAlive/LOS、TargetXY/TargetZ、CanStartAttack、CanBeginWake，以及 `std::function<FSweepResult(const FSweepRequest&)> Sweep`。CanStartAttack由遭遇系统授予，CanBeginWake由全房苏醒队列授予（共同规则至少1秒间隔）；核不会自行假定全房许可。

`FResult={Accepted,Events}`。每条事件含EventId、EntityId、TargetId、Kind、AtTime/EndTime/Amount、From/To和Action值快照。命令直接返回同批事件，没有隐式PendingEvents：调用者必须消费结果，再到完整批次提交边界保存；不能重新放回事件伪造再次消费。EventId/AttackId为该Entity内单调ID，全局需结合RunID/RoomInstanceID/稳定EntityID。

典型次序：用同一权威run_sim_time调用StepTo并处理结果，再按ChooseAttack请求TryStartAttack；真正受击调用ApplyResolvedHit并处理结果。需要追近/冲锋位移时，Sweep为必需；缺失或非法返回拒绝整个Step，核状态回到调用前。输入在步进区间视为恒定，目标移动/LOS/权限/外部属性变化必须在真实提交点分割，锁点读取该点合法输入。失败Sweep不得已向外界提交伤害或位移。

## 连续扫掠与两招

`FSweepRequest`携带Charge标记、FromTime/ToTime、From/To、冻结Action、身体/独立受击体半尺寸24×20、A1前伸65、半深24、高度中心0/容差65。Sweep必须是无副作用查询：沿整个时间区间找最早接触，不仅测试末帧位置。

`FSweepResult={Fraction,Stop,TargetId}`，Fraction在[0,1]；无阻挡必须Fraction=1且TargetId=0。Stop为None/Wall/Body/ValidHit；只有ValidHit携带非零目标ID。调用者先按真实攻击形状/高度/LOS/无敌合法性判断，再判身体截停。掠过身体或碰到无敌/不合法伤害目标可返回Body而不造成伤害。核按fraction记录实际接触时间与位置，ValidHit返回一次Hit事件；调用者随后在同批结算玩家实际伤害。State().Position才是核接受的最终位置。

A1起攻即保CD=Start+3.8；LockAt=Start+.45，ActiveAt=Start+.9，最长ActiveEnd=Start+1.7。ChargeStarted标示开始，真正命中只经连续Sweep，不应把其名义未来整个区间当一次已发生的命中。无阻挡速度620，0.8s最多496cm；锁后不能追Y或转弯。墙、身体、合法命中按接触时间停止，ActiveEnd截到该点，RecoveryEnd=接触时间+1.6。到达最长末点才接触也合法。失手走到最长末点，再满1.6s恢复；中途不会改接A2，冷却不退款。

A2起攻即保CD=Start+2.2；LockAt=Start+.35，ActiveAt=Start+.7，ActiveEnd=Start+.82，RecoveryEnd=ActiveEnd+.9。ActiveWindow含完整[AtTime,EndTime)，大步跨过整个窗仍返回一次。调用者用Action.Origin/Direction和0—90cm前矩形、Y半宽32、高度中心0/容差65、LOS精检真实玩家中心，然后TryMarkMeleeHit以AttackId+TargetId去重，再提交伤害；不能由纸面动画补判。

## 苏醒、受击和奖励

靠近椭圆+LOS或正实际HP损失排队苏醒；真正接受时起0.85s警告。BeginCombat显式记录本房战斗起点，12活跃模拟秒到点排队；NotifyOtherAcceptedEnemiesCleared只代表调用者已证明其他已接纳存活敌实际清除的事件，不能在初始化空集合上调用。排队等全房CanBeginWake后仍得完整警告。未觉醒破韧期间的实际伤害/其他敌清除事件保留，眩晕结束后苏醒，不丢事件。

削韧累计到60才中断；未破韧受击保原动作。真破韧眩晕0.4s，保护1s，保护内削韧不再次累计或延长眩晕；原起攻CD保留。削韧最后合法贡献后延迟1s，每模拟秒衰减20。苏醒期间破韧不能跳过剩余警告，也不回血。死亡先终止动作、关闭余窗、禁身体由适配负责；ClaimDeathReward仅同一死亡实体第一次返回true。具体奖励交付及D13原子事务由外层负责，核不发装备或目录奖励。

## 可保存状态与恢复

FState.Version=1，稳定EntityId、NextAttackId/NextEventId、Time、HP/PoiseAccum/LastPoiseAt、ProtectionUntil/StunUntil、CombatStartedAt、WakeStartedAt/WakeEnd/WakeQueued/Awakened、两个ReadyAt、RewardClaimed、Phase、Position、Action、ActiveReceipts和HitReceipts。

Action保ID/招式/InProgress/Locked/ActiveIssued、起攻/锁定/有效开始/名义与实际有效结束/恢复结束、Damage/Stagger、Origin/Target/Direction和Stop原因。每个ActiveReceipt保不可变FrozenAction、实际窗口End与对应EventId，离开当前攻击后仍有独立证据；HitReceipts保AttackId+TargetId。当前实现随本局保留这些凭据，不能盲目截断。

Restore拒绝未知版本、不同Entity、非有限字段、非法HP/韧性、破损警告/phase、伪造招式数值/时间表/锁线、CD重置、事件游标复用、窗口与当前动作矛盾、重复命中。坏候选不修改运行核。继续只复制原绝对时钟与剩余schedule；暂停期间调用者不推进Now，不走离线计时、不重起警告、不回HP/CD。没有磁盘序列化或迁移，文件完整性与同代bundle由D13外层负责；本核不认证所有证据一起被一致篡改的文件。

## TDD与范围证据

- stone-red-01.txt：真实编译成功，68检查/48失败；stone-red-02.txt仍68/48（将追近夹具置于共同规则650视野内）。
- stone-green-01.txt实际仍68检查/2失败，文件名不代表通过：两项是夹具绝对目标位置和double字面量误用。测试改为冲锋后真实相对近身点、数值近似断言，生产边界不加epsilon。
- stone-green-02.txt：68/68通过。
- 自审追加窗口末点接触/未觉醒眩晕受伤/短警告/事件计数器恢复反例：stone-red-03.txt为76检查/4失败；修复后stone-green-03.txt为76/76通过。
- 未觉醒眩晕中其他敌实际清除事件：stone-red-04.txt为77检查/1失败；最小修复后stone-green-final.txt为77/77通过、exit0，MSVC14.38 C++17 /W4 /WX。
- 已有动作核只读回归：stone-regression-combat-01.txt为80检查/0失败/exit0；未改已有动作核或其测试文件。

未运行UE/完整项目套件或真实物理，不声称正式敌人内容验收。根线程负责适配和独立review；本次只冻结行为核与夹具证据。

旧源读取SHA256：enemies.json `d01dd609a95ff9ad182638982a0ac7de864dbbd29f6b03995f9a3625a0c44266`；common-rules.json `0296b0d87fc1d16ef1f90d15b73aa08544b7e1c5ca173db898cf2d20f93976f5`；target-profiles.json `e5649ff4f5c53f0740126923f2a5a99b73d3e523a2d2dd4dc4e75e60ae85c4e5`。

核冻结：2026-10-14 22:58:23.1335431 Asia/Shanghai；DungeonStoneKnight.h SHA256 `1c5a68131a52dc0cfcf02a684d178488cc8f61f54d13d39799e0cb69b634758b`。最终测试后无核修改。
