# 军剑真实前踏脚声回归候选 v001

仅 NEW 本目录。actual Source/Content/tools/E/status/ledger 未修改，UE 未启动，候选测试尚未经 Unreal 编译或运行。FinalAccepted=false；RootApproved=false；等待 Root 独立复核、准入、专项和全 203。

## 真实失败与变化依据

Root 实际音效三文件准入后，`build-editor-20261019-061304.log` 编译成功；保存的实际 D3D11 `FirstRoomNativeRHI-20261019-062104/index.json` 是 202 Success / 1 Fail / 0 warning/notRun/inProcess。原报告 408652 bytes，SHA256 `625037d5cf53cbaa03221c3181d7b9c23e7ad6dfb37cc80a6d358cf274a49bc4`，本目录 evidence/failed-index-062104.json 原字节副本；编译 log 也保留原字节副本。

唯一失败 ID：`CodexDungeon.Content.MeleeAudioJournal.NormalSkillsRealIndependentSubhitsOnce`。两个失败都是原完整 journal 总数期待 1、实际 2。原 kernel/window/逐 whoosh ExpectOne/NoReplay 没有失败。原因是当前完整 ActionAudio journal 合法包含 SWD 的一次 ActiveWindow whoosh 和同一 ActiveAt 的一次真实非零 ForwardStep 脚声，旧 `total == SubhitCount` 的 whoosh-only 前提失效；没有改变游戏动作／伤害／输入规则。

## 最小修改及防止凑数量通过

只投影一个原测试 CPP，`exact-seams-v001.json` 包含 3 个 insert、2 个明确总数断言替换。原测试文件 16662 bytes / SHA256 `1988802f314071e27d5c74c7bd998ffb9661236bfd93c811fa2b7334d63e8e1a`。全部已有 fixture Create/Key/Frame/AdvanceTo、ExpectOne、NoReplay、独立窗口计数／时间／逐 whoosh 检查字节保持原样；inverse seam removal 恢复全原文件。三条既有 MeleeAudioJournal 测试 ID 保持不变；原全 203 ID 清单随原失败报告保存，不删除或替换任何用例。

完整 facts/requests 总数仍直接 `.Num()`，仅 SWD 加 1，GSW/SPR 加 0；不筛掉新 cue、未知 cue 或坏记录。新 helper 严格检查：

- SWD 整个 fact/request journal 各恰有 1 条 `HERO_STEP_LIGHT_01`、各恰有 1 份 Present witness；非 SWD 整个两个 journal 都不得有脚声或 witness。
- 真实 K current ActionId/InstanceId、SWD Skill、Active/Locked/Active phase、NextSubhit1/ForwardStepIssued、同一真实绝对 ActiveAt、实时时钟、地面和实际 Actor/World/Run gate。没有借用 J AttackId 或冻结旧版本号。
- witness.EventId 等于真实前一时点读取的 WA.NextEventId；实际 kernel ActiveWindow 与 WorldWindow 的 EventId 等于其 +1，实际 post-At NextEventId 等于其 +2；Subhit0、源 action/instance、World key 与当前真正父源一致。
- fact 的 Run/Room/Owner/Action/Instance/Revision/Sequence/Operation/AtTime 全与实际 committed View、journal、WorldWindow 和 current skill 相符。
- RequestedSignedDistance 为 authored 30×真实锁向；DTO Before/After 与调用前后实际 Actor 地面位置完全一致，CommittedDelta 与两次实际读数之差完全一致，数值有限、沿锁向为正、Y=0、且不大于请求幅度。没有把请求 30 当成已提交 30，也不把受阻 0 当有效脚声。
- 已有 HUD consumer 的 Source 每个父字段及 ForwardStep 每个 witness 字段均等于真正 journal fact；真实 light-step SoundPath、原 .25 gain／Pitch1、同一 At 的 request 各一次。

任何未知额外 cue 都仍使完整 `.Num()` 总数失败；坏 action/instance/parent、提前脚声、复制错误或非 SWD 脚声也有独立拒绝断言。

## Before/After 取样时序依据

原 `Frame(Dt)` 顺序是 Game.Tick → input ProcessInputStack → HUD.Tick。原 K Pulse 接受真实动作，随后原循环先 AdvanceTo(nextafter(At,-inf))、再 AdvanceTo(At)。新代码只在这两个既有推进之间读取 BeforeGround、BeforeTime、NextEventId 和 grounded；不增加 Frame／输入／位置 setter／事件。到达 At 后用实际 current skill、真实世界窗口、已复制的 HUD receipt 对照，所以 Before/After 不由 test 重算或强置。

Kernel Issue 原规则是**同一 ActiveAt** 先 Emit ForwardStep，随后 Emit 单一 ActiveWindow。`host/verify_real_event_order.cpp` 用实际公开 WA kernel（不是 mock）验证 -20/0/+20% × 左右六条真实 SWD 与 GSW/SPR first-window，50 checks / 0 failures；日志 evidence/real-event-order-host-v001.txt，MSVC x64 C++17 /W4 /WX，exit0。它只证明现有公开动作内核的事件顺序／ID/时间关系，**不冒称这份 UE 集成测试已执行，也不证明听感**。

公开 API 复核已去掉对 private HeroLocomotionAudioActiveV001 的草稿访问；最终候选仅调用原来已有公开 API，未加 friend／生产 getter／额外业务接口。

## Root 下一步

严格核 baseline pin 后在实际测试文件应用 5 个 seam，先复核 projected source hash，再真实 UE 编译并跑该专项和全 203。源人数/资产数不变化，本候选只修改 1 个既有测试文件，不加入新的 Unreal 测试 ID。若新严格 DTO／位置／时序断言失败，应保留实际失败并调查 producer 或 fixture；不能删除它们或进一步放宽总数。
