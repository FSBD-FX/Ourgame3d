# 稳定试玩启动检查 v002 候选

事实：Root 的 v001 ValidateOnly 已 exit0、全部通过、UE_started=false。约02:24启动到02:26结束，没有准确总耗时计时，不能报告精确秒数。实际v001源10957B / f94a28e6064973781292897089fce7d92b1ab1021f82e400ef0331e3133026f1，仍保持不变。

诊断：AssertStagePin先经StagePath检查完整父链，又再次检查父链及provider Length；目录枚举每项也检查完整父链。三个实际副本路径的少量交错微基准中，每轮同样6次查询，旧实现112.3614/110.2905ms，新实现6.3076/3.4985ms。这只证明路径查询热点改善；没有测完整新入口，也不能据此换算实际启动速度。

最小实现：每次对完整父链重新调用.NET File.GetAttributes检查ReparsePoint；非Directory叶子仍使用原Get-Item -Force .LinkType检查，保留文件hardlink拒绝。没有目录缓存，没有并行或跳过哈希，没有改变Get-FileHash调用位置/1778runtime成员/hidden精确集合/引擎marker/原生证明/Root批准门。provider Length也保持原样。

边界：两版都是分步、时点检查，不是原子文件系统锁。父链每次fresh检查，不缓存目录状态；检查与后续文件打开/UE启动之间仍有与原版相同的竞态窗口。只吞FileNotFound/DirectoryNotFound两种原缺失路径情况，权限及其它I/O异常继续拒绝。Windows目录junction/symlink有ReparsePoint；hardlink仅文件，不能单靠属性bit检测，故保留叶子检查。[微软文件系统说明](https://learn.microsoft.com/en-us/windows/win32/fileio/hard-links-and-junctions)

## Root 准入步骤

1. 只读核对本候选freeze/diff/source。物理复制新的launch-stable-preview-v002.ps1到副本_proof/tools/launch-stable-preview-v002.ps1，逐字节核验；不改v001脚本或父metadata中旧Stage启动CMD。Root确认采用NEW wrapper launch-hero-stable-preview-v002.ps1和NEW alias“钟盔轻甲快捷试玩.cmd”，旧固定试玩alias也保留。
2. 另写_proof/runtime-snapshot-manifest-v002.json：逐字保留父v001全部1778runtime rows、engine rows、CM/count/copy字段与全部旧metadata rows；新增新launcher metadata pin，并新增parent_runtime_manifest_pin，明确指向实际旧_proof/runtime-snapshot-manifest-v001.json的路径/字节/SHA。禁止改旧manifest。
3. 另写_proof/Root-stable-approval-v002.json，schema仍使用既有HeroAir6-Root-stable-manual-approval-v001；runtime_manifest_pin指向新v002。stage_copy_receipt_pin、staged_native_proof_pin、Root_visible_review_receipt_pin继续引用真实旧件，完全不改写旧copyreceipt/native174证明/旧批准。新gate将copyreceipt/native证明严格与parent pin比较，同时逐行验证新旧runtime/engine/CM等价；原实际174证明继续只证明旧父，而不是假称观察过新metadata。
4. Root独占更新当前入口到新脚本并做真正ValidateOnly计时。仍限定LIMITED_WIP；full_realtime_playback_reviewed=false、audio_listened=false、FinalAccepted=false、known_pose_join_refinement_open=true。无需由本候选重跑native；这是相同游戏runtime的启动工具派生。

## 实际验证范围

16项小检查已通过：旧/新函数的ordinary/hidden/目录/hardlink/junction/缺失路径行为，以及实际父JSON数据的相等组件正例、runtimeSHA/order/member/engineSHA/CM/count/旧metadata缺失负例。组件测试不执行Root批准、完整入口、1778全哈希或UE，不构成新native通过。

source-delta-verification-v002.json逐字逆变换能精确还原旧f94源；全部22个普通native flags及其它旧门字节不变，仅函数、批准文件版本、显式parent lineage绑定与ValidateOnly说明发生变化。host link/junction fixtures保留在_host-fixtures，故意链接不进入代码准入闭包。

本候选没有修改actual Stage、actual tools、E、游戏Source或冻结v001，没有创建新Root批准，也不声称实际完整启动已变快。
