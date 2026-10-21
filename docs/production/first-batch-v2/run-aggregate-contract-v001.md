# Bound Run 聚合 Capture／暂停安装合同 v001

2026-10-16，只读源码合同。替代旧地图中“owner 尚无接口”的过时描述，保留旧文原件。现有 Equipment／Scene／Exploration／Fighter Schema2／World Schema1 已分别验证；[默认111审计](F:/Ourgame/docs/production/first-batch-v2/evidence/world-owner-snapshot-v001/actual-owner-final-default111-audit-v001.json)记录111 Success、旧103保留、零错误警告，明确 aggregate_Continue=false。本文没有运行UE/UBT，没有修改Source、台账或进度；以下新类型/API是待实现合同，完整内容仍0/15。

## 事实

1. GameMode 还没有完整Run Capture/Validate/Install；当前公开 CaptureEquipmentSnapshot 只是转发单个owner。[GM.h:71](F:/Ourgame/UnrealGame/Source/CodexDungeon/DungeonGameMode.h:71)。Windows A/B Store 接受完整canonical字节并校验发布，但不会捕获Actor或恢复游戏。[Store.h:7](F:/Ourgame/UnrealGame/Source/CodexDungeon/DungeonSaveGenerationStore.h:7)。
2. 当前可恢复的Actor类型只有 BoundPlayer、ENM-STN-001 石像骑士、ENM-STN-002 石像蝙蝠；unbound／QA-PROTOTYPE-ENEMY、其余敌人和Boss没有这套完整owner实现。Fighter Schema2 包含actual native HeightAnchorRelative、custom muzzle和历史冻结emission，不能退回“Jump/Facing重建全部组件”。[Snapshot.h:32](F:/Ourgame/UnrealGame/Source/CodexDungeon/DungeonFighterSnapshot.h:32)、[合同v002](F:/Ourgame/docs/production/first-batch-v2/fighter-owner-snapshot-contract-v002.md)。
3. 存在聚合必经的跨房身份前提冲突：BeginEquipmentRun只在出生房给player一条binding；NextRoom升当前Room但不改该binding。World validator允许出生／历史房binding；Fighter.cpp120、125却要求它属于当前房，因此正常第二房的player和新knight Capture预计被拒。现111中World测试真实换房后只恢复World，没有紧接着Capture全部Actor。[初始化:105](F:/Ourgame/UnrealGame/Source/CodexDungeon/DungeonGameMode.cpp:105)、[换房:1678](F:/Ourgame/UnrealGame/Source/CodexDungeon/DungeonGameMode.cpp:1678)、[Actor门:120](F:/Ourgame/UnrealGame/Source/CodexDungeon/DungeonFighter.cpp:120)、[World门:74](F:/Ourgame/UnrealGame/Source/CodexDungeon/DungeonWorldSnapshot.cpp:74)。这是静态推导，尚不是实际RED；必须先用真实E/Enter换房反证，不改出生binding来掩盖。
4. FDungeonPickup只有Position/Kind/bConsumed，死亡直接append coin，首个死亡加potion，房清加axe，没有ObjectID／来源／领取receipt。bound TryInteract提前路由装备／场景，尚不会执行legacy金币拾取循环。[GM.h:25](F:/Ourgame/UnrealGame/Source/CodexDungeon/DungeonGameMode.h:25)、[死亡:1759](F:/Ourgame/UnrealGame/Source/CodexDungeon/DungeonGameMode.cpp:1759)、[交互:1821](F:/Ourgame/UnrealGame/Source/CodexDungeon/DungeonGameMode.cpp:1821)。不能声称已有正式bound金币领取或D08预算闭环。
5. FExploration已能精确Capture/Restore，但真实记忆仍是HUD私有成员；只在有Canvas的DrawHUD→UpdateRoomView中Reveal。Owner/RoomNumber/RunRestartSerial变化会重新分配空Memory，当前没有跨房记忆库或HUD恢复接口。[HUD.h:103](F:/Ourgame/UnrealGame/Source/CodexDungeon/DungeonHUD.h:103)、[HUD.cpp:230](F:/Ourgame/UnrealGame/Source/CodexDungeon/DungeonHUD.cpp:230)、[Draw:1386](F:/Ourgame/UnrealGame/Source/CodexDungeon/DungeonHUD.cpp:1386)。Exploration的int RoomId是显示房号，不能代替uint64 RoomInstanceId或RunGuid。

## 剩余字段的权威与处理

| 真实字段／owner | 聚合处理 |
| --- | --- |
| SimulationTime，RoomNumber，bRoomCleared，bGameOver，bWaitingForStart | 必存原值。load暂停必须是新的技术gate，不能把bWaitingForStart当暂停后无条件清false。GameOver时Tick仍推进terminal presentation，暂停gate须先于该分支。 |
| LastStoneWakeStartedAt | 必存，包括−1哨兵；MakeKnightFrame/NextSimulationBoundary用它限制全房唤醒。不能从当前活敌最大WakeAt猜历史值。[GM.cpp:821](F:/Ourgame/UnrealGame/Source/CodexDungeon/DungeonGameMode.cpp:821)。 |
| PlayerFighter／Enemies数组 | 保存稳定ID、完整Schema2 owner，以及**敌人数组顺序**。恢复新Actor并重绑，不存指针、不按ID排序改变原遍历/同点顺序。当前死亡敌也保留到真实离房；不因dead而过滤。 |
| WorldEntityIds | 暂态弱指针map，按保存的当前Actor→ID安装，不能调用AdmitWorldFighters/GetUniqueID。World.ActorBindings全部历史保留，旧房binding不表示该Actor仍应spawn。[WorldProjectiles.cpp:217](F:/Ourgame/UnrealGame/Source/CodexDungeon/DungeonWorldProjectiles.cpp:217)。 |
| Equipment／World／Scene | 调用已有完整owner验证器，不重写内核。WA.Issued、资源注册/更新/Operations、CritReceipts、active/inactive projectile/window、HitReceipts、Burns、Events及所有next游标保持全量；不截成最近N条，不按journal.AtTime全局重排。 |
| SceneEncounterEntityId | 必存；是出口核查的真实本房敌实体。Scene active时须在当前Actor中唯一对应knight，保dead/claimed事实；inactive时不得带无来源的encounter。 |
| bSceneCommitRequested | 保存边界应已drain为false；pending已确认Survey/Exit必须按正常同点次序先提交，不能仅清该bit。尚待新确认的exit层保留原owner观察，load确认键不得再确认出口。 |
| bSceneEquipmentTargetLost | 一代输入路由锁存，现Tick结束清false。只允许completed边界false，不从半帧保存；不能恢复为跳过一次真实交互的新规则。 |
| Pickups／死亡与领取事实 | 需要新增稳定地面对象/来源/结果receipt根，见下节；当前array本身先逐值保留，Consumed记录不能因为不绘制而删除。 |
| SceneWorldActors | 仅几何对象缓存。当前Scene墙的BoxExtent/中心/碰撞来自已知Layout；拆出GeometryOnly创建器，不能调用同时清遭遇并新生knight的SpawnSceneExplorationRoom。[GM.cpp:270](F:/Ourgame/UnrealGame/Source/CodexDungeon/DungeonGameMode.cpp:270)。 |
| PendingDamage、bSimulationBatch、bSimulatingMotion、SkillBatchBodies、MotionBatchBodies、SkillOldIframeUntil、SkillBatchFrom/To | 指针/单批query缓存不入payload。证明完整批已结算后重建空缓存；PendingDamage非空时拒绝捕获，不丢弃未提交伤害。 |
| RunRestartSerial | 本进程HUD失效token，不是RunID/存档时间。安装可递增本地presentation epoch并显式装回记忆；不能通过“序号变了让HUD自己初始化”清掉保存Memory。 |
| bManualWeaponPreview／ManualWeaponPreviewRunGuid／Fairytale flag,facing,wall epoch | QA生命周期/试装值，不作正式Run状态。明确development内容scope；恢复入口不能继承新局QA分支，禁止因此重新注册物品/生成敌人。 |
| LastMessage | 可保存原文/消息key用于首帧连续性，非成功凭据。不得解析字符串派生房清/奖励；技术暂停提示与它分域。 |
| HUD纹理、材质、CameraX、ActorQuads、Rendered*、音频request计数／receipt、Controller／物理按键／Probe | 进程/展示缓存重建；Camera允许从当前位置重建，音效请求不当作设备已发声证据。Probe的Fixture/自动输入/录音/截图异步任务都不得入Run或在Continue重跑。 |

Stats.CurrentHP是上次Resolve/Update镜像，Pawn.Health才是当前玩家HP事实。现UpdateEquipmentMirrors还调用SyncWeaponMuzzleTransform；**恢复不能把它作为无害“刷新一下”**，否则可能重写已保存actualAnchor。先以原snapshot完成校验/安装，仅在下一个真实正常Tick沿原代码更新。[Equipment.cpp:155](F:/Ourgame/UnrealGame/Source/CodexDungeon/DungeonEquipmentRuntime.cpp:155)、[GM.cpp:627](F:/Ourgame/UnrealGame/Source/CodexDungeon/DungeonGameMode.cpp:627)。

## 推理：直接可实施的值类型与API

下列是下一实施切片建议，非已存在源码；ProfileID/Generation/三版本仍由完整bundle/Store头拥有，不另造第二套代际权威。

```cpp
enum class EDungeonRunScope:uint8 { BoundDevelopmentV1 };
struct FDungeonRunExplorationRoom {
    uint64 RoomInstanceId=0; int32 RoomNumber=0;
    DungeonExploration::FState State; // schema1完整double memory
};
struct FDungeonRunExplorationSnapshot {
    uint32 Schema=1; FGuid RunGuid; uint64 CurrentRoomInstanceId=0;
    TArray<FDungeonRunExplorationRoom> Rooms; // stable room身份，不只HUD int
};
struct FDungeonRunSnapshot {
    uint32 Schema=1; EDungeonRunScope Scope=EDungeonRunScope::BoundDevelopmentV1;
    FGuid RunGuid; uint64 OwnerId=0,RoomInstanceId=0;
    double SimulationTime=0,LastStoneWakeStartedAt=-1;
    int32 RoomNumber=1;
    bool RoomCleared=false,GameOver=false,WaitingForStart=false;
    FString LastMessage;
    uint64 SceneEncounterEntityId=0;
    FDungeonEquipmentRuntimeSnapshot Equipment;
    FDungeonSceneObjectsSnapshot Scene;
    FDungeonWeaponWorldSnapshot WeaponWorld;
    TArray<FDungeonFighterOwnerSnapshot> Fighters; // 全当前Actor含死亡
    TArray<uint64> EnemyOrder;
    FDungeonRunRewardSnapshot Rewards; // 下节定义；不能留不透明unknown blob
    FDungeonRunExplorationSnapshot Exploration;
};
namespace DungeonRunAggregate {
    // 内部先构造完全值候选，无Actor/IO/随机/事件消费。
    bool Validate(const FDungeonRunSnapshot&,FDungeonValidatedRun&,FString&);
}
// GM公开只读值捕获+请求；请求在真正completed point处理。
bool ADungeonGameMode::CaptureRunSnapshot(FDungeonRunSnapshot&,FString&) const;
bool ADungeonGameMode::RequestRunCapture(FString&);
// 两阶段安装；Stage对象只包含进程内暂存资源，不序列化。
bool PreparePausedRun(const FDungeonRunSnapshot&,FDungeonPreparedRun&,FString&);
bool InstallPreparedRun(FDungeonPreparedRun&&,FString&);
bool RequestExplicitContinue(bool FreshUiPress,FString&); // UI键被消费
```

`FDungeonValidatedRun`／`FDungeonPreparedRun`应是实现受控类型，只能由验证器/暂存器产生，不能让调用者伪造bool“已验证”。root重复身份必须与各owner严格相同；Player恰一个、EnemyOrder恰覆盖全部非player且不重复；RoomNumber与uint64 RoomInstanceId分域校验，不用强转相互替代。World恢复先用保存player的真实WA state，不读新Actor默认内核；之后每个Fighter使用保存Equipment+已验证World+GameOver的ExplicitStaging context。出生player binding冲突须先真实反证修正原语，不靠聚合伪造其出生房。

## 稳定拾取／奖励／retired历史最小合同

建议新`FDungeonRunRewardSnapshot`有Schema、RunGuid、NextObjectId、NextOperationId、DeathSources、Objects、PickupReceipts；ID是独立域，不能复用Equipment.SourceId/OperationId而没有domain。

- DeathSources：稳定来源key至少含Run/Room/Entity及来源种类；记录真实死亡/已Claim、原解析结果和关联ObjectIDs。当前coin源是该敌首次死亡；首死potion与房清axe另有room级唯一来源key，避免换新operation重复生成。只标记现规则为development奖励，不捏造D08 SlotID／有限预算已完成。
- Objects：ObjectId、原SourceKey/resultIndex、RoomInstanceId、Position、Kind/同规则版本的已解析数量或效果、Ground/Consumed/Retired状态。对应FDungeonPickup的绘制投影可重建；已经Consumed/离房丢弃仍保消费事实，不能再生成。稳定ID在**正常出生/解析**处赋予并同根保存，Capture不得临时根据array下标补发ID。
- PickupReceipts：OperationId+规范请求/原精确结果，ObjectId、原/新账或库存version、仿真AtTime、实际变化。生成和真实领取分开；OnFighterDied重入返回旧事实，不能load时重跑。绑定模式领取尚未接线，第一聚合只证明已有真实掉落生成/恢复/不重复；不能手改bConsumed或借legacy unbound拾取声称bound领取通过。
- 旧房Actor退场保最小tombstone（Run/Room/Entity/content/team、真实死亡/已报告/来源消耗事实）服务历史引用；World.ActorBindings目前只有ID/room/content，**不等于完整死亡奖励tombstone**。当前已死亡而仍在Enemies中的Actor保完整owner；实际离房后可转retired事实。未死亡普通离房废弃需明确Despawned，不能伪记死亡/奖励。
- 保存完整WA.Issued、发射socket、旧instance/来源、World hit/burn/event及retired目标，不把“当前不在Actor map”当非法历史。不得为了让validator通过将历史全部spawn成活敌或复活owner。

## 真实捕获边界与探索交接

新的GM请求gate须覆盖整个Tick，而非只测bSimulationBatch=false：Tick先处理Enter/R和新鲜input，随后每个中央子批依次motion→旧窗口/弹道→enemy→同点damage/burn→bat→damage→player新事件→damage→equipment→scene。捕获请求只在完整边界后处理，且PendingDamage空、非motion/batch/resolving、scene commit已drain、input代路由锁存已结束；不能在一次Tick内部getter各读一份。[GM.cpp:1378](F:/Ourgame/UnrealGame/Source/CodexDungeon/DungeonGameMode.cpp:1378)、[提交尾:1543](F:/Ourgame/UnrealGame/Source/CodexDungeon/DungeonGameMode.cpp:1543)。不限制必须idle：accepted combo、reload、pickup/switch、enemy locked动作、旧弹/burn都应原样捕获。合法terminal内核时间可小于master，display高度可变化，不能Step补齐。

HUD没有Canvas时DrawHUD不做Reveal，故不能从纯FExploration测试推断真实HUD已捕获。最小交接方案：加只读HUD当前探索Capture和明确的Install/Attach接口；首次接线从真实已观测Memory深值捕获，校验owner/Run/Room/同一冻结边界，未attached或身份不符明确失败，**不初始化空Memory冒成功**。捕获期间暂停观测写入，恢复先安装，再绑定新Actor+本地epoch，随后第一Draw不能因owner/serial变了清空它，也不能先Reveal再声称exact。

跨房Rooms记忆库是当前新缺口：离房前将真实HUD原Memory移交Run root，新房以正常新房规则开始；旧房记录保原RoomInstanceId/RoomNumber。若某历史房在这项功能启用前已被HUD丢弃，不能倒猜已探索范围；这类旧开发Run明确不支持完整聚合capture。正式D13要保全部已建房事实，但本切片不创建尚无实现的D07路线图/未来槽。建议最终把可持久化探索owner归Run，HUD只观察，以免专用server/headless依赖Canvas；迁移须保已有真实Memory并用同一Reveal算法验证，不顺便改变视野半径。

## 暂停暂存与原子安装顺序

1. 收到Load/Continue请求后冻结技术gate，位置必须在Tick处理R/Enter及gameover terminal显示之前；其它公开Register/Interact/攻击/重开入口也须拒绝安装期副作用。不是调用BeginEquipmentRun、RestartRun、ResetFighter、SpawnRoom、InitializeStone*。UI墙钟可继续，run钟/DoT/CD/预告/音频不前进。
2. 从同一代decode值→全版本/域/引用校验：Equipment候选；保存player WA纯验证；World候选；Scene候选和房间registry；Exploration候选；reward/tombstone；全部Fighter纯+native候选及root约束。检查活动动作互斥、SceneEncounter、房清/存活状态；未曾清房的空房不能由load推成清房。
3. 在受控staging中创建独立Actor，disabled tick/hidden、无碰撞影响；GeometryOnly创建已知Layout的墙，先关闭碰撞，不清旧几何/旧敌。按保存ID构造Actor context并Restore，各值和actual native anchor/muzzle回读。保原enemy顺序；不Admit、不新FGuid、不随机抽、不重播pending事件。未知Actor/几何/布局/规则版本整体拒绝，不能将外来障碍悄悄忽略。初版只允许已知平面bounds和Scene探索布局；实际Map静态碰撞注册/版本须在新进程接线时实查，本文未从Python源臆称实际.umap已核。
4. 所有fallible创建/注册/回读在切换前完成；RAII失败销毁**只属于此次staging**的Actor/组件，真实world context必须合法，旧Run/ID/RNG/物品/记忆/碰撞不变。不能先Destroy旧Enemies再尝试后半恢复。
5. 单游戏线程、gate仍关闭，成组swap Equipment/Scene/World/Root scalars/Actors/maps/reward/fog；激活新几何、停用旧几何，最后Possess/绑定HUD。native组件值已由owner精确安装，不额外Sync归一化。回调也受安装gate保护，不能看到半根状态。成功后才释放旧资源；没有必要称跨线程/OS原子。
6. Seed展示历史消费位置，再允许静态首帧；仍保持AwaitExplicitContinue。新的UI确认只解技术gate，所有游戏按钮松开/轴回中后才认下一fresh edge。原WaitingForStart/GameOver含义保留；dead不能被Continue复活。第一次正常Tick沿原absolute时序走，不补离线delta，不赠血/弹/无敌，不清accepted连段/terminal queue。

D13完整磁盘步骤随后把**整个同代bundle** canonical化给Store语义validator，不能只写Run段冒充account/settings/journal已完成。经济/奖励/过门的原新结果须先发布再曝光成功；写失败保同candidate/ID/RNG，marker后失ack通过原代际检查恢复，不能newID重试。这是未来接线要求，本合同不实现未有的D09账号系统。

## Audio／HUD历史消费边界

ActionAudioState与ActionAudioWeaponCursors在源码明确是transient展示，不是D13经济事实。可从保存WA当前/历史tail调用只读SeedActionAudioWeapon：已elapsed draw/insert被标记，未来phase才发新声；不得因此Step内核。新session journal可空，NextSequence为会话域，运行中更换/加载**同Run**也必须显式重绑HUD展示epoch，不能只靠RunGuid变化。[GM.cpp:149](F:/Ourgame/UnrealGame/Source/CodexDungeon/DungeonGameMode.cpp:149)、[HUD.cpp:167](F:/Ourgame/UnrealGame/Source/CodexDungeon/DungeonHUD.cpp:167)。

当前WorldWeapon HUD对新Run将cursor置0后读全部Events；age<=.25的历史会请求PlaySound2D，故单纯重建HUD也不等于“已防重播”。新Continue Attach须seed为保存NextEventSequence−1并清瞬态effects/计数；不能删权威World.Events来解决。[presentation.inl:4](F:/Ourgame/UnrealGame/Source/CodexDungeon/DungeonWeaponPresentation.inl:4)。Stone恢复已Begin(savedNextEvent)建空feedback tail，但HUD也需统一Attach，保未来新event正常消费。不得load补播成功音效；声音实际试听与请求计数分开。

Equipment的slot-selection、Scene未确认exit是已有owner保存的观察/展示状态，不能当已接受经济动作自动提交。正式canonical codec需依D13把纯未确认整理意图与真实Action分域，并显式声明允许清除的UI/input字段；不能在聚合实现中暗改原owner快照来凑exact。已接受的装备Action、pending reload和待履行子段必须保留。

## 3–5组真实fixture验收建议

1. **CrossRoomOwners（优先test-only）**：沿现World实际Scene fixture，Room1 default player/knight Capture正对照；正常Enter/移动/J击杀、E/Enter进Room2，保出生房player binding和全部旧World历史。Room2 default player+新knight Capture及独立staging Restore/回捕获都须成功。禁止QA map/房清/HP赋值，不改旧111；先实际RED再修门。
2. **AcceptedStateAggregateContinuation（table）**：真实Register/E/确认获得武器，分别在pickup、switch、reload插箭后、三连击/闪避中捕获；恢复到独立GM+Controller+physics world，先暂停观察全根相等（仅明确unaccepted input例外），再相同正常键和绝对deadline推进。真实ammo/inventoryreceipt/next IDs/crit draw与源对照，pending plan无关注册rebase历史不丢；不同时强造互斥动作。
3. **EnemyWorldRewardHistory**：实际knight wake/charge、moved bat低位/升高、真实staff弹/burn与正常击杀生成coin/potion/axe；包含同Run真实换房old inactive attacks/tombstones。暂停恢复不多spawn活敌/发奖，重新OnFighterDied不增对象，未来真实hit/burn phase一致。bound领取未接线则明确只验生成/未拾；消费闭环留到真实入口实现，不能手置Consumed。
4. **ExplorationAndFreshResume**：真实HUD观察路线/折返后冻结，装回新owner时首Draw之前Memory原值/插值完全相等，首Draw后只允许正常reveal单调增加；跨房保旧记忆。分别sameRun重建HUD和新进程，近历史age<.25排除age跳过捷径；恢复前持J/T/E/Enter，明确Continue+全松后不得产生旧边沿，未来音效仅新phase。需要新HUD read-only Capture/Attach接口，纯FExploration构造测试不能替代。
5. **WholeCandidateRejectionAndStagingFailure**：真实非空源/目标两根，分别坏Run/room/重复IDs、漏retired source/issued、变currentActor/EnemyOrder/Encounter、unknownschema1/非finiteanchor、fog域、reward重复/无receipt；在Actor/geometry第N次创建、注册回读或最终切换前注入失败。整旧根签名、Actor/碰撞、对象/钱包/ID/RNG/音频/Memory不变，仅保诊断；新112等测试数由真正注册统计。以后接Store时另验每发布边界和新进程Continue，不用同进程staging代替磁盘证明。

## 风险与范围

剩余实际缺口包括上述跨房门、HUD记忆交接/历史库、稳定掉落/消费事实、完整aggregate validator与安装gate、canonical codec/同代bundle/语义发布以及真实新进程运行。有限未来槽、正式路线/房间budget、其它敌人与Boss、D03全状态/道具、D08/D09经济/成长尚未有本接口实现：未来为各自已实现owner加有版本的具体字段，unknown scope直接拒绝；不在本切片用空数组宣称D13全覆盖。

本轮接线路线不缩减既定15内容单元（5武器、4甲、5普通敌、1Boss）及20搭配/全动作特效音效验收。当前可实现primitive只覆盖已有真实owner；其余单元完成后沿同root扩展。完整goal仍0/15，Continue也须最后由真实新进程、正常输入、录像审阅和发布故障证据验收。
