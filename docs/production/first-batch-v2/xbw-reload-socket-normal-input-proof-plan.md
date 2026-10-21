# 猎弩装填与 socket 正常输入录制器

日期：2026-10-15。本文属于新录制器的实现说明，不是独立 Actor 审查结论。独立 `DungeonWeaponPoseSocketReviewTests.cpp` 仍保持 `177220ff…` 冻结；本录制器不改旧80组、生产/HUD/Probe hook/PS 或已有 Proof。UE/UBT、录制、F/E 保全和实际验收由 root 执行。

## 入口与权限

新增两文件：`DungeonXBWReloadSocketProofState.h`、`DungeonXBWReloadSocketProof.inl`。Root hook 使用 `FXBWReloadSocketProofState XBWReloadSocketProof` 和 `TickXBWReloadSocketProof()`，并从 `FXBWReloadSocketProofState::RequiredChecks()` 取得20个静态唯一名称。总 wall deadline55s；有模拟进展的单阶段期限12s。实际60fps仅设上限，不固定步长、不慢放、不改动作/装填速度。20ms 的 primary pose3若三次正常尝试仍未捕获就失败留证，不能合成 mask。

Phase0 仅 genuine `BeginEquipmentRun(IntegrationPreview,1)`、注册唯一 Ammo1 XBW 来源于玩家前32cm、创建左右各220cm/400HP 的静态普通 QA Actor。仅创建时设置 bEnemy/bAIEnabled/MaxHealth/ResetFighter。它们是明确的 QA 靶，不冒称正式敌人。BeginEquipmentRun 本身把启动门打开；root明确允许本录制器在 phase0 初始化时将 `bWaitingForStart=true` 一次，以便后续真正 fresh Enter 开门。本文不声称原 Begin 函数原生保留菜单。

Phase0 后不写 HP、位置、Facing、装备、弹药、动作、来源消费或 socket；只使用现有 Controller Key/UnitMove/UnitPulse。所有实时状态、世界事件和资源回执均只读。测试与录制结果分域：录制器新增源不计 Automation 组数。

## 正常流程与门

1. fresh Enter 打开 QA 初始门，fresh E 取得真实来源；观察完整.35提交、旧持握到提交、真实 instance/slot/sourceConsumed。
2. 正常 D/A 设左右朝向；每侧真实 ready6帧 mask63、primary6帧 mask63、reload4帧 mask15，检查实际4层 stack、武器状态、Actor action/instance 与 HUD自己的 SampleTime。每侧至少1、最多3次正常 J及完整自动装填，用于尽力捕获短pose3。
3. 每发检查真实 World bolt、同一目标一次 HP loss、pre-spend immutable hand socket、combat Height0、独立 presentation高度、角色 RangeAnchor 与真实扣减量。口坐标由该发 native Emit/Root/BodySize推导，不能把初始neutral口常数错误套在后来loaded3的新组件上。
4. 每侧自动装填必须在完整主攻后摇后才开始，真实1.10s内 Ammo0，真实完成后 Ammo1/持握图loaded3。正常 Q到军剑再Q回弩，保留同一 instance与loaded状态。
5. 再真实 J，观察实际ammo与图empty0；自动装填插箭frame2仍 Ammo0。在真实deadline前 fresh T取消，等超过原deadline仍empty0、Ammo0且无 ReloadCompleted回执。再fresh T重启完整1.10s，只有真实完成后Ammo1。
6. 最后核所有发射/命中/停止各一次、真实crit draw次数、无Focus回执、完成装填回执总数、两靶实际HP损失/原位置以及历史 socket/RangeAnchor不随当前状态漂移。

装填动画 frame3(.85..1.10)可以已经画出“装好”的图，资源仍须为0。`GetRenderedWeaponStateIndex` 在 reload 内只是视觉pose；“完成后loaded3”门只用于非reload持握。图像与 HUD均无资源提交权限。

## 渲染滞后和 trace

HUD SampleTime/ActionId/InstanceId是实际上一帧渲染观察，不能强行等于当前 post-batch WA.Time。录制器保存已真实接受的 primary/reload actions，以 HUD自身时刻检半开区间；用真实 WeaponRuntimeHistory 还原该绘制时刻的 ammo与已完成装填次数。未匹配动作不会凭空补帧。左右 mask按对应实际 shotFacing归属，不能把右reload归成左reload。

每个 post-batch trace记录 wall/sim/WA/HUD四种时刻，输入键、来源/slot/instance/ammo/reservation、真实action及history、当前Actor socket与世界每次实际 emission/hit/stop冻结socket、RangeAnchor、native/component emit、武器视觉state、actual draw stack/paths、左右mask/尝试次数、QA靶的真实ID/XY/HP。源码调用 Check只在阶段完成一次；重复check尝试主动失败，不重复追加PASS。失败仍FinishAudioCapture保存已有证据。

## Root 接线契约

- HUD只读getter：`GetRenderedWeaponBodyInstanceId()`、`GetRenderedWeaponStateIndex()`，现有 Clip/Frame/Facing/ActionId/SampleTime/DrawStack/EmitScreen/Trail getters保留。
- Clip exact：`xbw_ready_idle`、`xbw_primary`、`xbw_reload_four_keyposes`。
- 无甲4层次序：body_far → weapon → body_support → body_near。Ready body为v016 `T_XBWReadyIdle_{track}_{frame:03d}_v001`；primary body为v017 `T_XBWPrimary_…`；reload四层为v018 `T_XBWReload_{track}_{frame:03d}_v001`。
- 初始loaded neutral武器为v015 `T_WPN_XBW_001_neutral_v001`、state−1；真实空态0与完成装填后持握3使用v018对应weapon图；reload内state取0..3的实际pose，不据此提交弹药。
- World 使用新增 HasPoseSocket/PoseSocket/RangeAnchor及 FResolved.ActorOrigin/WeaponStateIndex/Emit/Root/BodySize 等冻结字段。Source为pre-spend实际发射口；Actor当前empty0口可以不同，不能用历史getter假装当前组件。

## 已发现边界与证据状态

静态发现 left J自动reload转右风险：WA StartReload的FAction.Facing默认+1，Fighter SyncWeaponSkillAction无条件复制。已交 producer/root；本录制器不写Facing或伪造左mask。是否修复以实际候选及独立证据记录为准。

本版截至冻结前只做静态自审，没有编译、运行、音画或像素验收。Root负责独立审源、实际录制和F/E保留后再审原帧；本实现者在F/E保全前不view新媒体。尚不声明四甲动作、完整美术、听感、正式敌人/来源、D13存档或正式15项完成。

Root审源发现原稿ready Prefix漏Idle。原 `56794430…` 已保原稿证据；root接管inl仅修正Prefix，后续SHA为 `8617ff738b758c60474c34025dcc7f9248b4a0f5d955b0b1cc125defba905592`。原State `d6dd0771…` 未据此改变。当前root已接管录制器/hook/PS；本实现者停止该Source写入，不将静态路径修正称为录制通过。
