# Death v005：独立正常J死亡／自动金币候选

此目录未运行 UE、UBT、导入、录制、ffmpeg 或 View。静态契约检查通过不等于原生可达或编译成功。旧 partial、AxeCycle 和 StunIR v004 全部保持冻结；本目录独立 actor/入口/schema，不借用原 proof 的成功结果。Hurt4 和 MoveRig 不在范围内。

Root 最小准入是两件 new-source 与一个 HUD startup patch。当前未准入 StunIR 的 HUD 可用 `patches/minimal-HUD-Death-startup-v005.patch`；已合并 StunIR v004 后改用 `patches/minimal-HUD-Death-after-StunIR-v004-startup-v005.patch`。两个是二选一的上下文补丁，不可都应用；有其他 startup 修改时 Root 只合并 include 与独立 Death 分支。没有整文件 HUD/Fighter 覆盖，没有 Content 改动。

入口：`-DungeonGuardArtDeathProofV005 -DungeonGuardArtScenario=Death -DungeonFairytaleGuardFullPreview`。其余皮甲军剑 Ready/P1/P2/P3/Walk/EquipmentBound 与原生 async lossless 参数由本目录 launcher 保留。不能同时打开 StunIR/AxeCycle/partial proof 或 partial preview。native `guard-art-known44-death-observer-v005`，session `guard-art-known44-death-session-v005`，Root prereg `guard-known44-death-Root-prereg-v005`，独立 receipt `independent-Death-v005.json`。正常启动 restart serial 为1。

流程保持正式三槽房间的出生、喘息与预告：真实 Enter，公开 display LGT source +真实 E；Knight/Bat 仅公开 ApplyCombatHit 诊断清除，Guard 由正式 slot2 计划出生。真实 WASD 绕路至140 staging，再真实向内 A/D 至观察到朝 Guard 且110..132/absY≤6才提交J。正常J按真实 melee ActiveEnd/End-.10队列三段，继续到实际唯一Died；Crit、受伤、击退、miss、cancel、poise decay、无敌窗都遵循现有实际生产逻辑。没有 Guard public damage、Spawn、Teleport、HP/poise/facing/time/stat/RNG写入，未手工Tick/StepTo/SetState，未无敌或回血。

死亡事件锁定后停止J和移动。Death6只在真实 `[Died.AtTime,Died.AtTime+1.0)` 计数，原分界0/.1/.2/.35/.55/.75，最初100ms余辉，末帧之后正常保持但不得补首1秒覆盖。独立 checker 核真实 Died、完整玩家 SWD windows/hit receipts、185HP单次Armor60减伤链（Crit用真实锁定Damage）、85破韧历史和每Draw源/pivot/ONErow/单整身斧/实际位置。Death coverage只要求同一个Died事件，不误把Died事件ID当AttackId。

1秒完成后只读实际 deathObserved/settled/RewardClaimed/slot Dead/roomCleared 与既有 Rewards schema2，再正常 WASD 走向原 slot2 coin object。观察器不调用 ClaimDeathReward、ClaimStoneGuardDeathEligibility、OnFighterDied、ResolveDeath、CollectCoin 或 TryCollect。真实 GameMode 的自动拾取单独完成。checker核唯一原死亡AtTime→单源→coin9→单次collection/wallet连续链、原coin偏移[-18,-12]、首次consumed回调实际活玩家≤60×30，以及最后同slot/room/owner保持。金币可在既有其他Coin自动拾取后收，钱包从20按全部真实collections重算；不硬写最终29。death source时间按实际 `DungeonFirstBatchGuardRoomRuntime.inl` 的唯一原 Died.AtTime，RewardClaimed事件允许真实结算帧端时间≥Died，不误要求二者同stamp。

Root 建议先合并源码、编译、严格全套后创建 NEW fresh compiled snapshot/prereg。本目录模板始终 is_template=true、pre_registered=false、所有实际SHA/count null，不冒审批。复用已冻 AxeCycle tooling-v003 source_check 仅作 source/profile 检查：Root另建 NEW Axe-compatible source-profile prereg，绑定同一新快照、实际最新源计数及 unchanged10 row/13allrows/44sources/gaps。Death专用 prereg独立绑定 fresh source-profile pin、whole freeze 与实际两actor/HUD三文件pins。不能沿用旧v132/Source231硬常量，也不能运行旧compiled DLL冒新actor。

Root命令（先 ValidateOnly，不启动UE）：

```powershell
& '<candidate>/tooling/capture-Death-v005.ps1' -Snapshot '<actual fresh snapshot>' -ProfilePrereg '<actual NEW shared source-profile prereg>' -RootPrereg '<actual NEW Death prereg>' -ApproachSide -1 -Version v001 -ValidateOnly
```

删掉 ValidateOnly 才启动一个新进程。默认当前hero存活/原HP保留，phase8 wall34秒／全录48秒，结束即停；原1秒Death窗口丢相立即失败，不等待后续保持帧补相，不重试重放。未能在真正伤害压力下完成击杀、低HP、真实正常J错过、录制丢帧等仍可能让首原生试验RED，必须保留原件再定位；这不是预先声明可玩通过。设备/磁盘失败仍180秒外部保护，旧索引PID发布顺序修复保留。

本次检查：Python AST、PowerShell parser0、源公开接口/无Guard owner写入与括号结构、旧像素CRC/FIFO assert AST相同、11个仅内存oracle边界（包含早结算／重复源／重复collection／远程拾取／1秒后补帧拒绝）。当前base HUD patch `git apply --check`通过；Root未来StunIR后patch是明确上下文合并方案。全44 resident不等于全部44渲染，Death6也不等于全57、正式敌人、美术、音色、足锁或死亡塌落root的视觉验收。Root录制后需独立重核、另准备媒体并E保全后实际View。
