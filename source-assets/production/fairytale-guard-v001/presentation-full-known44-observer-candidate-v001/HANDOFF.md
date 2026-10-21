# Known44 单斧周期 native observer 候选 v001

事实：这里新增独立 `ADungeonGuardArtKnown44Probe`、最小 HUD 启动 patch、预注册模板、启动器和独立核验器。旧 partial actor、入口、工具、报告均未改。H/CPP/patch/protocol 四件先冻于 `source-AxeCycle-freeze-v001.json`；整个候选以 `known44-AxeCycle-freeze-v001.json` 为准。没有在本候选工作中启动 UE、UBT、导入或查看新媒体；静态核验成功不等于原生成功。

实际已存在的 Root scoped-trial 记录 `root-full-registration-v001/row-trial-approval.json` 和 native28 import/two-pass receipt 被精确复制为模板中的输入 pins。它批准 10 行（含 Dormant alias）、44 unique / 45 logical，FinalAccepted=false。模板尚未填写未来实际编译快照、Source/DLL/test counts 与候选总冻结 pin，`is_template=true`、`pre_registered_before_capture=false`；Root 必须另写实际 prereg，不能改此模板冒充已完成预注册。

## 准入接口与顺序

只复制 `new-source/DungeonGuardArtKnown44Probe.{h,cpp}` 到实际 Source，同目录使用现有 `DungeonFairytaleGuardFull*V003` 生产接口；最小 patch 只加新 include 与新启动分支。入口同时要求 `-DungeonGuardArtKnown44Proof -DungeonGuardArtScenario=AxeCycle -DungeonFairytaleGuardFullPreview`。旧 partial flag 与新入口同时出现会明确失败。其他 Scenario（包括 StunIR/Death）尚未实现，会明确失败。

Root 合并、编译后，建立新 compiled snapshot，包含实际全部 Source、Production、DLL、成功 build 与 strict full suite。工具按 snapshot 的真实 typed counts 精确核对，不锁死计划中的 Source229/231；目前 full registry 下限184，并要求原 partial3 与新增 full3 同时 Success。Root 正式 Source 资格修复/换行差异用实际快照绑定，不要求 actual header/data 与默认 false 的冻结候选逐字相同。

按 `root-templates/known44-AxeCycle-Root-prereg-TEMPLATE-v001.json` 另写实际 prereg。必填 schema 是 `guard-full-known44-Root-prereg-v1`；`profile_facts` 可为精确10 known gates，或精确13 rows；`all_profile_rows` 必须13行，且两表 known 行全字段一致。Move6、StompActive2、StompRecovery4 必须 SourceId0 / SourcePoseApproved=false / TrialAllowed=false / FinalAccepted=false / Frames空 / 审批空，明确记录 gap。已源审的224/225只可诊断文字，不得填进 runtime source/frames。actual Root审批、native28 receipt及two-SHA receipt必须相互绑定。

## 本次真正要证明的范围

正常三敌房间 URL、实际 Enter 开局、注册公开 display LGT 来源后真实 E 提交、正常 WASD 绕身体外侧通道靠近。Knight/Bat 只用公开 `ApplyCombatHit` 诊断清除，报告明示这不算正常全战。Guard 只能由正式 slot2 计划出生；没有 Guard public damage、spawn、teleport、manual Tick/StepTo、SetState、HP/time override 或无敌。

BeginPlay 在正常 Enter 前要求全44已加载 Texture2D resident、512尺寸与 exact object/source/RGBA metadata；不在观察器中 LoadObject 救首次缺资源。独立 checker 核实际28 import与旧1226的精确并集及当前 Production 集，另16旧已导入纹理从 compiled snapshot/既有资源表绑定。

仅选择 Issued 中**最早真实 Axe AttackStarted**，在其 Windup0 原窗内且实际到达指定侧点时 pin。WU6、Active4、Recovery4 必须相同 Run/Restart/Entity/AttackId；每行 SourceEventId 是对应原始 Issued **EventId**。锁心/facing、唯一 damage window、200ms Active / 1400ms Recovery 及各半开帧时钟均独立核验。WU结束缺63、Active结束缺15、Recovery结束缺15立即保留失败退出，不能以后续攻击补首周期。Ready15独立来自实际 Idle 的 WakeEnd锚定循环，可跨实际后续 Idle 段累积；不把 Ready event0 改成攻击 receipt。

Ready及所选WU0..2必须实际 side*dx ∈[120,180]、距离≤180、|dy|≤12；WU3..5/Active/Recovery可按真实锁定同一 AttackId 后纵向避让，仍要求 side*dx ∈[120,180]。路线有三段真实 WASD waypoint/观察见证，HP必须保持100，Guard185、incoming/outgoing hit receipts均0。旧右侧 facing-only 重叠反例会被新硬位置门拒绝。

每个实际 DrawId 的全部 Full DTO字段、source pin、ONE row scale、左右 floor pivot（left=512-right）、单层包含斧头的 DrawStack 均核验。Dormant只aliasWake0，若未观察到则如实记 DormantUnobserved。缺行必须零纹理层+明确 procedural gap，不能 Ready 兜底。本次最低真实覆盖24 unique（Wake6+Ready4+WU6+A4+R4）；全44 resident 是加载事实，**不等于44全部已渲染**。Stun、IR、Death、Stomp 的实际原生场景将在后续独立进程实现，不能从本次成功推导。

## Root 执行命令

在 `F:/Ourgame`，先填写真实路径；以下占位路径不属于证据：

```powershell
$snapshot = 'F:/Ourgame/docs/production/first-batch-v2/evidence/<fresh-compiled-snapshot>'
$prereg = 'F:/Ourgame/source-assets/production/fairytale-guard-v001/<Root-new-actual-prereg>.json'
& .\tools\runtime\asset-gen\Scripts\python.exe -B -X utf8 .\source-assets\production\fairytale-guard-v001\presentation-full-known44-observer-candidate-v001\tooling\verify-known44-axecycle-v001.py --snapshot $snapshot --root-prereg $prereg --source-only
& .\source-assets\production\fairytale-guard-v001\presentation-full-known44-observer-candidate-v001\tooling\capture-known44-axecycle-v001.ps1 -Snapshot $snapshot -RootPrereg $prereg -Version native_left_v001 -ApproachSide -1
& .\source-assets\production\fairytale-guard-v001\presentation-full-known44-observer-candidate-v001\tooling\capture-known44-axecycle-v001.ps1 -Snapshot $snapshot -RootPrereg $prereg -Version native_right_v001 -ApproachSide 1
```

两个方向是顺序 fresh processes，每次结束即停，失败原件不覆盖。先做一次足够定位的问题，不自动重试。启动器保留当前棕皮 Ready/P1/P2/P3、同款 LGT/Walk flags；全新 session/native/pixel helper schema分别固定为 `guard-art-known44-native-session-v001` / `guard-art-known44-native-observer-v001`，scenario=AxeCycle，旧partial schema不能误入。CRC/FIFO/stop-flush算法与旧已冻结v010对应assert AST一致，只另设版本schema门。

## 边界、成本和未完成

原生30fps不能保证50ms Active每相必有无停顿截图；若实际丢相必须 RED，不能延长窗口、慢钟或重复cycle补齐。phase8墙钟22s/全采36s有界，资源/引擎崩溃时启动器另有180s外部终止保护；这个保护不授予90s无用行为重试。依旧部分试样每23s约2.5GB原始PNG粗估，本次双进程约5GB，实际以 receipts/files为准；后续五进程13.8GB只是设计估算。

没有最终美术、join无pop、足锁、音色或全部57帧验收。214后四帧 floor 是 artist standing-root propagation，不能称测得隐藏脚/COM；222是 FAR抬脚/NEAR支撑 variant。WU222→Active224约29.7displaypx源pose突进风险与Move rig pilot均不在本次修复范围。静音视频不是音效验收。Root须先完成E保全再View新样本；原始PNG/时序/CRC与视觉评价分别留证。
