# Root 集成交接

## 事实

基线 manifest：`F:/Ourgame/source-assets/production/backups/v144-HeroAirDiskRestore300-203GREEN-v001/compiled-source-manifest.json`，581493 bytes，SHA256 `fb225bef1e9b2e3584a16d3eff192bd39587867b68c0fcdb525a4d876324e59a`。本候选三份实际文件的字节/SHA、每处唯一 before/after 和集成结果 SHA 在 `exact-seams.json`，可读补丁在 `exact-seams.patch`。只读生成时实际整个 Source 为 300 文件，CodexDungeon 模块为 298，Production 为 1419；候选增加 3 源文件、修改 3 现有文件，6 SoundWave 导入后预计 Source303 / Production1425。需要在 Root 集成后重新计数，不应把预计数当实际结果。

六 WAV 的来源冻结 SHA256 为 `cf63ec47a15855f17703f72540471d8cba2a7a952a26bfc7bc03acd0b2f216ac`。每条原 WAV 的当前完整 SHA/size 与该冻结一致。导入目的地当前不存在。没有复制/处理 WAV、支付、联网或调用 UE/MCP/API。

## 集成顺序

1. 等当前真实磁盘 native pair 完成。先执行候选目录的 `python verify-handoff.py`；失败说明实际源码/源 WAV/接点漂移，应重新审查，不可强行覆盖。
2. Root 将 `Source/` 下三个新文件逐一放入实际 `UnrealGame/Source/CodexDungeon/`；实际目的文件必须不存在。按 `exact-seams.json` 应用三份现有文件的唯一接点，保留原行结束符；核对每份集成结果 SHA。`prepare-handoff.py` 只生成候选文件，故意没有实际 apply 功能。
3. Root 用原工程方式做 UE5.5 编译和原有全套检查；主机 GREEN 不替代 UE/UHT/link 或原 203 项检查。编译失败时只修新增绑定范围，不修改运动/时间/HP/输入/既有 cue 增益。
4. Root 在独占的 UE 导入窗口执行 `import/ue-import-hero-locomotion-v001.py`。普通 Python 只能 `--validate-only`。脚本先全量验证六文件，再使用 SoundFactory/AssetImportTask、replace_existing=false、save=false；校验导入类型/声道/48k源速率/时长/ADPCM/ForceInline/priority 后保存，验证 registry 与磁盘都恰好六对象。执行收据写本候选 `reports/ue-import-<UTC>.json`。失败可能留下未保存 UObject 或部分新资产，不删除、不重试覆盖、不改冻结；Root 应明确处理或换新的唯一版本路径。
5. Root 新运行默认真实游戏：静止/纯相机变化/暂停无新增脚步；实际地面碰撞后累计 40cm 每次一足，01/02 交替；离地/闪避/攻击专属移动不累计普通脚步。真实 Space 成功一次起跳；拒绝请求无 cue。实际落地一次，Land4/5/Ready 不重发。真实 Dodge 成功一次 Started，其真实 EventId/ActionId 保留在新请求中。
6. Root 做 Apex 保存→新进程 restore→显式继续的真实检查：准备、等待、接入都无 takeoff/Dodge 历史补播；接地才产生一个新的 landing。新音频 receipt getter 为 `GetHeroLocomotionAudioPlayRequestsV001()`；字段有真实 cue/源事件/时间/对象路径/增益，但它仅证明请求，必须关联实际主混音或设备听感，不能当已听见。按项目要求先保留 F/E 原件与展示副本，再展示/试听。

## 推理与政策

- 接点只在真实成功 StartJump、TryBeginDodge 返回的新 Events、RecordCompletedGroundMotion 和统一 CommitMotion 之后；不在 PredictMotionBodies、副本 StepTo、HUD/OnDrawHUD 或 pose frame 上发声。
- 统一模拟会先调用旧 SimulateMotion。旧逻辑可能已将 V 归零，故唯一音频接点用 canonical P.StartHeight/P.EndHeight；音频用归零前原 V 加现有重力步长得真实下降速度，传显式 ToTime。旧 SimulateMotion 不增加任何音频 hook，同一接地事实不会两路声音。GameMode 统一模拟同时覆盖旧武器路径；独立 Fighter::Tick/直接 SimulateMotion 不属此候选支持范围。
- 成功起跳分支在实际 V=630 赋值前静默 seed，Dodge 在真实 TryStart 前静默 seed，然后只观察真实成功事件；首个公开真实动作不会因首次接入时读取了新状态而被误判为历史。关闭门/等待/终点状态在 Tick 早退前消费丢弃待播队列。
- producer 队列和 consumer cursor 都是 transient，接入按实际对象/RunGuid/Owner/Room/Restart/Epoch 换代；新 epoch 静默 seed 当前 H/V 与 Dodge.NextEventId−1。相同 scope 再次 seed 是 no-op，不重置脚步余量。
- 每个有效实际 interval 先推进 through cursor；consume 先推进 sequence 再按 .25s 年龄/暂停/终点死亡/缺资源丢弃。不会下帧重试旧声音。全部声音在完整真实 Tick 之后请求，终点已死亡则本 Tick 新请求丢弃。
- 当前实际 gait=80cm/周期，候选40cm/足；这是独立音频距离累计，不改变既有动画相位。Light/Firm 初始阈值为真实落速 >=540cm/s 或本 epoch 实测下落距离 >=110cm。这两个值是候选听感选择，未获混音/材质认可。

## 风险及未完成边界

1. 未执行 UE 编译、导入、运行、PCM采集或试听。native API 参数已对照本机 UE5.5 头文件，但不能据此宣称 UE 编译成功。
2. 与当前武器/Guard 架构一致的 native 2D prototype sink；bIsUISound=false 尊重引擎暂停。middleware、真实3D空间化/遮挡/混响仍未完成，不能按正式平台音频交付认证。本候选不扩展这些系统。
3. 不改存档 Schema1，恢复后脚步余量/交替奇偶重新开始，保存前已下落距离不重建；Firm 仍可依当前真实落速选择。若要求音频节拍也精确续接，需单独版本化 continuation/codec/aggregate/installer，不能静默塞字段。
4. 256 pending/receipt 上限和六声音共享 6 voice 并非全项目音频预算验证；高密度战斗、CPU/内存与平台听感尚未测。超过单次10240cm不连续距离会静默丢弃该次音频距离，避免巨大输入产生音频风暴，不改运动结果。
5. 标称 CC0 来自已保留的许可链；本次未新做网络法律审计。声音没有证明石地/皮靴材料、没有最终听感认可。受伤/死亡与已知 Guard 双接触混音风险完全保留原状，不计入本次完成。
