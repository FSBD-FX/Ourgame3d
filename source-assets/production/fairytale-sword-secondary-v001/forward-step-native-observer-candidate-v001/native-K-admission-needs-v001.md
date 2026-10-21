# K 原生观察器当前最小准入缺口 v001

这是 NEW 补充文档，**不属于原 28-member 冻结集合**；未修改 `candidate-freeze-v001.json`（6543B / SHA256 cdc65ddfd5922156517ff681aba6378ac4b3047888cd425054d9e38b41603046）或任何冻结成员。没有新框架、host 测试、源码/资源准入或 UE 操作。

## 已有事实

实际 Source303 / Production uassets1439；K 新图层尚未实际导入，真实 HUD 尚无已准入 K8 getter/分支。音效 producer 和新增 DTO 已实际准入；回归测试命名修正后的实际 CPP 为 25069B / SHA256 36c0288a344920b69ff4ec3ac6e2510e4fde4ac2d60a21a1522d73cff9ed7107，063547 实际 Editor build ExitCode0。本补充不认证随后 full203 结果，编译不是新的完整 GREEN CM。

runtime-plan-candidate-v001 仍是未准入的三个新增 Source 文件和十个 insert seams；其 Profile() 返回 NotAdmitted。当前 observer 是 Draft_NotReady，+2 新 Source 文件、三个插入操作（涉及两个既有文件），未 UHT/Editor 编译或独立 Approved。其 typed serializer 根据候选 API 准备，不表示当前实际 HUD 能输出这条 trace。36 项 host 模型结果是准备性证据，六路线均仍关闭进程启动。

## 最小实际顺序

1. **先锁定真实 K8 资源和 Profile。** 完成 K0..7 每帧七层（共 56 PNG）的实际分层、透明重构和审阅；每帧实测 Root/Grip/Axis，完整 SourceContract/ProfileId；八帧共 56 个实际 object/source pins，加已存在独立军剑组成 57 闭包。不能只把 RuntimeReady 翻 true、复制 J/258 marker 或拿 260 的部分帧当全八帧。实际导入应逐项记录 source PNG、uasset 的真实 bytes/SHA。固定 512 作者画布、72px 显示和 .50 独立剑按原设计保留。
2. **复合 runtime 与 observer，再真实编译/回归。** 在已准入音效的新 HUD 基线上逐条应用 runtime inserts，不能覆写旧完整 projected HUD；冻结最终 Profile/runtime 新版本并 fresh review。observer 两新文件及三个 dispatch inserts 也需 fresh review 和 UHT/Editor 编译。核真实旧203 IDs/全部结果后，保存新的完整 Source/Content/DLL/构建/测试 pins 和 CM。若仅新增已描述的 runtime3 + observer2，则 Source303→308；若 56 新 K 图层各为新 uasset、剑复用，则 Production1439→1495。它们仅是数量推理，实际准入清单和真实计数优先，不能拿预期数量伪造当前状态。
3. **补实际 K 像素 checker。** 现 observer 可记录真实 typed Sample.Action/绝对边界、binding、Geometry、8 Slots.Selected/Drawn、ActualStack、57 Residents、共同 DrawId，以及启动前 K57+Ready24 的原始 GPU/source BGRA8。仍需一个经独立审阅并 pinned 的 `audit(archive, prereg)` 实现，逐实际 native PNG 核 K0..7、左右一次镜像、甲/近手/独立剑遮挡与几何；不能只复算 sampler 或检查 metadata。原 PNG 全帧 CRC/FIFO/异步 flush 和完整 MainMix PCM checker 可直接复用；cue Source/PlaySound2D request 不等于已经听到该脚声或测到设备起点。
4. **先实际勘验正常地图路线，再写 NEW prereg。** readiness 中坐标目前只是 proposed。确认 `/Game/Maps/FirstRoom?DungeonFirstBatchGuardRoom` 的真实 entry/碰撞/敌人和可用阻挡边；不能假定那块矩形屏障一定存在于此 map。以普通 Enter/E/WASD/K 取得左右 full 与 partial 的实际位置/DTO，再给严格证据运行填写已验证路线。无瞬移、清敌、冻结 AI、移墙或改时钟；若正常敌人干扰，应选实际安全路线或让证据失败，不改业务来制造通过。NEW prereg 需精确 pins：fresh review、最终 K Profile/资源、最新完整 CM/当前 DLL/uproject/Editor、81 source/uasset、全部 checker。新声音与测试通过的旧 CM、e08 或保留的 202/1 RED CM 都不能冒充含新 K/observer 的编译清单。
5. **先跑左右 full/partial 四案，单独保留零案缺口。** 原 Start/LockAt/ActiveAt/ActiveEnd/End 不改；Ready→K0..7→原 End 后 Ready join、实际 ActionAudio parent/DTO 和真实 HUD receipt、完整原始 PCM/PNG/source/GPU 一起保存。当前 observer 只允许基线无速度/冷却 affix 的军剑，另存真实 unlocked cooldown0 和首次 locked cooldown4 source，并以真实库存回执接受该一次合法 Version+1，不能把初始 0 捏成 4 或冻结旧版本。需要变速/其他 affix 时应单独修改具体断言和审阅，当前候选不宣称覆盖。

## blocked-zero 的必要独立 seam

正位移会有真实 DTO，可独立核 requested30 与实际提交 partial/full。完全受阻没有 append/DTO；“没有脚声 + callback 总位移为 0”不能证明该 ForwardStep 的实际 Set/Sync 结果。当前 source、driver、checker 都将两个 blocked-zero 案拒为 NotReady，不能仅改 prereg 解除。

最小下一步是在**原** ForwardStep 的原 SetActorLocation/Sync 后，给 opt-in observer 暴露一份只读真实提交快照/getter，包含实际 Run/Room/Owner/Action/Instance/EventId/SubhitId、AtTime、Before、After、RequestedSignedDistance、grounded/commit observed；零位移也必须可读取，并有来源 scope/序号防止复用旧快照。它不是新音频事件，不改 Append 签名、BatchSkillStepDelta、cadence、伤害或动作时间；不重跑 kernel，不伪造零 DTO。该小 seam 需另行具体制作、独立审阅和实际编译，再出 observer 新版本，把真实零 witness 与无音频 fact/request 关联。现有 CompletedGroundMotion 仅表示整个 callback，不能替代事件级快照。

因此，**最早可实际推进的是完成真实 K8 资源/runtime 准入和编译，再勘验/运行四个正提交案例**；零 getter 不是这四案的必要阻碍，但六案“全部完成”的结论必须等零案有独立真实证据。当前更新后的原集成测试已经能先验证 K 内核/DTO/真实 consumer 请求，无需等待美术；它不能冒充新的八帧可见结果。
