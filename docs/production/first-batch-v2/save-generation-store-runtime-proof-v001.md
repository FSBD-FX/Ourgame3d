# D13 完整代文件容器：实际验证记录

本记录只覆盖 Windows A/B 两槽文件容器。当前没有接入 Actor / Run 捕获、继续游戏或完整战斗恢复；完整内容单元仍为 0/15。

## 事实

- Stage0 的六组真实磁盘测试在 `FirstRoom-20261015-223217/index.json` 实际全部失败；不是静态检查或模拟文件系统。精确报告另存 `actual-stage0-red-review-v001/actual-automation-index-exact.json`。
- 第一版生产实现构建 `225358` 失败，原因是 UE5.5 没有该 `FCString::Strtod` 接口，另有直接 Windows Pre/Post include 警告。窄修接口/includes 后，`225657` 构建成功；`FirstRoom-20261015-225719/index.json` 实际 96/96、零失败/未运行/警告，旧90项名称完整保留，新增六组容器测试。
- 上述通过版冻结为 `source-assets/production/backups/2026-10-15_save-generation-store-actual96GREEN-v055`。它是历史通过版，随后独立复核发现两处测试遗漏，不能因此当作最终正确实现。
- 新增真实反证后，`231930` 构建成功；`FirstRoom-20261015-231941/index.json` 实际 **4组通过、2组失败**。测试文件 SHA256 `3fc95c05bad9e29a9ac45105e0519d66f9ae026f5ffa9b0938c1943331959ba2`；生产 h/cpp 仍与 v055 完全相同。
- 精确报告、当时三份源码、构建/测试日志及25个独立真实 IO 目录已保全到 `evidence/save-generation-store-v001/actual-counterexamples-RED-v002`，共159文件、276702字节。报告名固定为 `actual-automation-index-exact.json`，不与证据清单混用。

## 反证与推理

1. 正常发布到 B4，再放回真实 A1 原件；两槽各自校验正确，但 B4 的 parent=3 与 A1 不连接。Load 拒绝，而同代 B4 重试和普通 G5 提交原实现均接受；G5 会覆盖 A1，掩盖断代。实际三条断言失败。修复应共用已有读取代际关系，覆盖正常写入与同代重试，保留显式恢复独立路径。
2. 实际 Recover 已归档四份原件后，只删除测试自己 GUID 目录中的根四槽文件。原实现把剩下的恢复历史判为 Empty，允许新 G1。另一个真实非空 migration 目录也误判 Empty。实际四条断言失败。无根 marker 且留有正式历史证据，必须要求恢复，不能自动覆盖或猜测归档版本。

## 证据保全工具的失败记录

首次复制到长名称目录 `actual-parent-gap-archive-bootstrap-RED-v001`，Windows 经典 MAX_PATH 限制导致深层 GUID/temporary 路径创建失败；已复制部分保留。工具随后仅为文件 IO 使用 Windows 扩展绝对路径，在新的 `actual-counterexamples-RED-v002` 完整复制并逐字复核。未重跑测试、改原报告或删除失败目录。

## 边界

容器目前证明真实文件写入、FlushFileBuffers、同卷发布、摘要/长度验证、排他句柄和所列故障注入边界。它们不等同断电/杀进程实验，也不证明 Run 语义、敌人/弹道/状态/RNG 恢复。

## 修复后实际结果

生产 v003 只将原 Load 的 parent 关系提成共同判定，供 Load/普通 Commit/同代 replay 使用；无 head 时正式 history 非空/名称文件冲突/枚举失败设为 RecoveryRequired 与 UnknownHead，防首代同字节重试绕门。没有放宽读取条件或将档案自动混入新代。

`build-editor-20261015-233431.log` 实际 exit0；`FirstRoom-20261015-233446/index.json` 实际 **96/96**，失败/未运行/Warning/Error 事件均0，原90个注册名称完整保留。原失败断言未删除/弱化；另在现有六组内验证真正空 history、有效恢复 head 带 archive 后正常继续、历史证据不能被首代相同重试绕过及两个目录名称文件冲突。

精确源码/报告/日志与28个实际IO目录保全为 `actual-two-fixes-full96-GREEN-v003`：165文件510231字节。v056冻结1078文件72626383字节，路径 `source-assets/production/backups/2026-10-15_save-store-two-boundaries-actual96GREEN-v056`。独立复核逐字核对 RED/GREEN 全部保全记录和 live/v056三源码、DLL、构建日志、报告，并抽查 A1/B4 与四份历史原件，针对性关闭原两缺口；见 `evidence/save-generation-store-v001/independent-final-two-fixes-review-v001.md`。

下一实际续玩接线依据是 `evidence/save-generation-store-v001/next-run-snapshot-code-map-v001.md`，不是新游戏重置后装回少数字段。当前容器不接 Actor/Run，完整首批目标继续 active、0/15。
