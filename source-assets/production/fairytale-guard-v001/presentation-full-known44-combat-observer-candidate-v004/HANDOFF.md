# 正常 J StunIR 可执行候选 v004

首个里程碑只有StunIR，Death尚未实现，入口会明确拒绝Death/AxeCycle；旧AxeCycle继续使用原actor，完全未倒改。新增类/文件名是 `ADungeonGuardArtCombatProbeV003` / `DungeonGuardArtCombatProbeV003.{h,cpp}`，版本v004表示本候选的正常输入朝向修复。Root只复制NEW H/CPP并合并最小HUD启动patch；不修改kernel、Guard gameplay、全44资源/注册、Source tests或Content。

v003已冻保留的静态阻断：右侧路线末段仅Y，hero可能向外，且dx134/dy6可超出135×46军剑椭圆。v004先正常走到±140 staging，再真实A/D向Guard走；只观察Facing==-side且实际signedDX110..132、|dy|≤6后请求J。这在135×46椭圆内有余量，保留6单位到点容差，避免3单位容差小于30fps单步一半造成往复。不写Facing/ActorXY。独立peer已读最小diff，未见新API/clock/mask阻断；这只是静态限定，不是原生可达或GREEN。

正常Enter→公开display LGT来源→实际E→Knight/Bat公开诊断清除→正式slot2 Guard出生→WASD+J。前三敌不是正常全战，报告明确。军剑真实尾窗按J：actualStage<2、ActiveEnd后、End-.10后、同AttackId只queue一次；不调用PressPrimary。实际Poise预测只安排普通输入，不改变真实decay/crit/hit。接近85时要求现有原攻击剩余时间可容下一刀+.4Stun+.4可观察IR；若未来decay使该刀未break，真实receipt继续决定结果，不能按键数宣称85。

第一次真实非致死PoiseBroken必须同时有该原AttackId的AttackInterrupted、AttackStarted；StunUntil=BrokenAt+.4，OccupiedUntil保持原RecoveryEnd且正IR至少.4。不满足就保留失败，不重置Guard/血量/poise/时间。英雄可以真实掉HP、断链与推移，禁止回血/无敌。Stun4按原400ms四相；IR4按实际正剩余 `[StunUntil,original OccupiedUntil)`归一，原端点缺mask15立即失败，不拼第二次break。IR.SourceEventId合法0，独立核真实RecoveryStarted与原AttackCompleted；原窗曾issued才需closure，未issued不能强要closure或新Active。

每帧记录actual guard/native/action、player melee action/facing/HP、Full DTO全部字段；最终附玩家原IssuedWindows+HitReceipts、Guard原ReceivedHits/Issued/Windows/Closures。checker按真实军剑锁定Damage/Stagger/时间、单次Armor60缓解与实际收讫序列重算HP和85poise（含1s延迟后20/s衰减），不按J次数。Stun/IR必须同原AttackId与唯一break；纹理/sourceRGBA/ONErow scale/镜像floor/单斧单层、真实伤害MaterialHit、closed gaps及native CRC/FIFO都核。

运行时schema固定`guard-art-known44-combat-observer-v003`，session=`guard-art-known44-combat-session-v003`，Root prereg=`guard-known44-combat-Root-prereg-v003`。全44 resident前置沿现有Full预加载/Flush，缺素材或审批就fail。覆盖仅Stun4/IR4，不把44 resident说成44渲染，不把缺Move/StompA/R伪成Ready。

Root完成编译/全184后建fresh Source/DLL/Content快照。为复用已核严格44 profile/source preflight，另写一个NEW **source-only** Axe-compatible profile prereg（原tooling-v003格式，更新本次compiled_manifest/counts/admitted Source pins、保持10known/13rows/import/gap与tooling-v003 freeze）。它只核来源，不宣称Axe native执行。再按本目录Root模板另写combat prereg，pin同一个snapshot、该profile prereg、新actor/HUD实际pins与本候选总freeze。避免重写另一套44资源验证器。profile/read-only helper与原compiled Source都精确SHA绑定；无伪造审批。

在F:/Ourgame先执行：

```powershell
& .\tools\runtime\asset-gen\Scripts\python.exe -B -X utf8 .\source-assets\production\fairytale-guard-v001\presentation-full-known44-combat-observer-candidate-v004\tooling\verify-StunIR-v003.py --snapshot '<actual-fresh-snapshot>' --profile-prereg '<absolute-new-profile-prereg>' --combat-prereg '<absolute-new-combat-prereg>' --source-only
& .\source-assets\production\fairytale-guard-v001\presentation-full-known44-combat-observer-candidate-v004\tooling\capture-StunIR-v004.ps1 -Snapshot '<actual-fresh-snapshot>' -ProfilePrereg '<absolute-new-profile-prereg>' -RootPrereg '<absolute-new-combat-prereg>' -Version native_left_v001 -ApproachSide -1
```

先一次左侧诊断，结束即停；不自动重试或重新生成Guard。可随后以同build独立右进程核正常面对问题。启动器保留棕皮Ready/P1/P2/P3+LGT/Walk/Full flags，并继承已修的PID/exit/native状态及时落盘顺序。phase8墙钟28s/总采42s，任一原阶段缺帧提前失败；外部180s仅防崩溃。原始PNG成本可能高于被动单斧，按实际帧数核，失败也原样留存。

本候选未UE/UBT/录制/View，不声称native通过。Root须E双SHA保全后View。下一Death版本才会实际J杀到Died→自动Schema2唯一结算→正常WASD进coin60/30范围自动收集；本版不调用Claim/OnFighterDied/TryCollect制造结果，也未完成该路径。
