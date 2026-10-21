# v010 工具接口修复；Source 仍为 v009

事实：已冻 v009 复用了旧像素 helper，该 helper 仍断言 native schema v002；新实际 C++ 的 schema 为 v009。此缺陷会让合法 v009 捕获在像素辅助核验阶段失败。v009 原候选与全部16 pins原样保留，actual Source不再修改。

本目录仅工具。native C++/report schema 继续严格等于 guard-art-partial-native-observer-v009；新 capture index/session schema 为 guard-art-partial-native-session-v010；新 receipt 为 independent-guard-art-partial-v010.json。三个脚本命名与相互调用统一 v010，物理源码依赖仍是同级 presentation-observer-route-candidate-v009/source-route-freeze-v009.json，由 v009-source-interface-pin-v010.json 精确绑定。

新 pixel helper 将 schema gate 改为仅允许明确 v009，并提前到像素解码前无条件检查；v002/v010/空/未知全部拒绝。原 CRC、BGRA转换、PNG尺寸与alpha、每帧FIFO、reservations、copyCRC、回调wall offsets、stop/flush全部断言保持。除 report读入/schema断言位置与schema常量外，其余源代码行逐行相等；全部断言AST多重集合只差该schema常量。未删 gate，未添加宽泛schema兼容。

主checker保持全部 v009空间门与旧事件/时钟/16纹理/floor/单层/CRC约束，只改新工具freeze/session/receipt/helper文件名与补充源freeze依赖pin。Root v131真实 compiled snapshot、typed prereg和其全部Source/Content/DLL/构建/full suite精确pin仍必需；不得拿v130或未完成full结果启动。目录层级与v009同层，Python WORKSPACE与PowerShell五级parent均为F:/Ourgame。

Root 实际 v131 snapshot/prereg 已生成之后（填其真实路径；Version必须未用）：

```powershell
$tool='F:/Ourgame/source-assets/production/fairytale-guard-v001/presentation-observer-route-tooling-candidate-v010/tooling/capture-guard-art-partial-v010.ps1'
& $tool -Version sideL_route_v010 -Snapshot $Snapshot -RootPrereg $RootPrereg -ApproachSide -1 -ValidateOnly
& $tool -Version sideL_route_v010 -Snapshot $Snapshot -RootPrereg $RootPrereg -ApproachSide -1
& $tool -Version sideR_route_v010 -Snapshot $Snapshot -RootPrereg $RootPrereg -ApproachSide 1
```

Root可先直接核验既有同schema v009的新捕获，但该捕获index必须由本v010 launcher在运行前绑定新freeze/session，不回写旧v009 index来冒新工具prereg。此前v002/v003旧实录继续保留facing-only原结论与v009新增空间纠正，不为其改schema或媒体。

静态验证：Python AST、PowerShell AST零错误；schema正例v009通过/反例v002、v010、空、未知均拒绝；原CRC/FIFO其余源行与断言AST保持；v009全部16冻结pins再次核实不变。无UE/UBT/新捕获/像素解码/View；新路线通过与实际最终空间证据由Root真实运行给出。
