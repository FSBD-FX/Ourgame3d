# Fighter owner 快照合同 v002：实际原生锚点数值

2026-10-16。仅补充已存在的 Actor owner Capture/Restore；v001 原稿保持原样。本版未运行 UE/UBT，等待 root 的实际完整测试。尚未实现 GM 聚合安装或磁盘 Continue。

## 事实

真实 `FirstRoom-20261016-023434` 只运行 Actor5：4 Success / 1 Fail，warning/notRun 为0；Atomic 恰有3个错误，分别是1e-10初始 body 差恢复后不精确、native anchor 相对/世界变换不等、public custom muzzle origin 不等。它不是完整111结果。原 report/log 与修前六文件逐字副本在 `evidence/fighter-owner-snapshot-v001/production-v009/`。

正常 `StartJump` 后两个真实中央 Tick（1e-6f、1e-8f）观察到：JumpHeight=0.00063629908254370093；实际 native anchor relativeZ/worldZ/public muzzleHeight=0.00062999915098771453；simulation=1.009999997414468e-06。没有手工构造 kernel、journal 或 snapshot。原生组件更新可保留先前的数值，故 HeightAnchor 不是能够由当前 JumpHeight/Facing 完整重建的纯派生值。

本机 UE5.5 `SceneComponent.cpp` 的普通位置更新用默认 FVector::Equals；NoPhysics 安装随后仍调用 ComponentToWorld 更新，其中小于 UE_SMALL_NUMBER 的差可能不写世界变换。`UpdateComponentToWorld(SkipPhysicsUpdate, TeleportPhysics)` 的非 None 参数强制写入现已赋值的完整 native world transform。对应本机源码节选与 SHA 记录在本版 evidence；这是原生更新路径依据，未新增容差，也未修改 kernel 原值。

## 合同修正

- `FDungeonFighterOwnerSnapshot::Schema=2`，新增 `FTransform HeightAnchorRelative=FTransform::Identity`。Capture 深值复制真实 `WeaponMuzzleHeightAnchor->GetRelativeTransform()`；完整测试签名包含其 translation、quaternion、scale。
- Schema1 缺少此实际数值事实，Restore 明确拒绝；Schema3 等未知版本同样拒绝。此接口仍在开发，没有已交付磁盘 Continue 或迁移负担；不猜默认值升级旧档。
- 全变换必须有限、quaternion normalized。按当前 native 结构域，relative X/Y=0、Z>=0、旋转为 identity orientation、scaleX 为±1且scaleY/Z=1。保留实际各分量，不把 anchor.Z 与 JumpHeight、scaleX 与 Facing 强行关联；石像的未使用 muzzle 和 terminal 也可保留先前值。
- Capture/Restore 要求实际 native parent 链 Root → HeightAnchor → WeaponMuzzle。Actor、组件对象与内部缓存仍不进入 payload。
- Restore 完整候选验证通过后，先原生 NoPhysics 写 saved body，再 force 更新 Root 的实际世界数值；对 saved anchor 和原有 muzzle 路径共用 native direct setters + 从 saved quaternion 重建 conversion cache + force world update。没有 Initialize/Reset/Step、ID分配、动作重播、HP重算或 Jump 归一化。

## 验证与边界

原有5注册/全部旧语义断言保留。Atomic 已有真实1e-10 staging body 和真实两步起跳/custom24,7控制，保持精确比较；另在同组新增旧Schema1、非有限anchor、水平位移、非法scale、非法rotation拒绝及 owner/资源/audio 不变校验。原有明显 body+1 反例仍拒绝。

本版只修复上述实际 RED 合同遗漏及精确安装，不扩正常运行逻辑：Fighter constructor 起全部旧 suffix 与修前字节相同，Bat driver 与 Fighter.h 未改。Actor owner 恢复到独立 staging 并回捕获的证据不能被描述为真实 Run Continue 已完成；root 后续唯一运行完整111和默认入口并由独立 reviewer 核实。
