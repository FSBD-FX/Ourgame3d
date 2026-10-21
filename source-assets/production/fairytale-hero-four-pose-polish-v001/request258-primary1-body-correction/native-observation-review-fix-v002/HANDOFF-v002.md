# Request258 startup residency 修复 v002

完整最终 CPP：`projected/DungeonHeroLandingPriorityProbeV001.cpp`，76025 B，SHA `30b1db6503f8641bcac0165cfc134ae7e841b96f3f23b8d68b912a90696a2205`。`exact-seams.json` 与 `native-observation.patch` 是 **actual e73→最终 v002**，共六处 additive inserts；`v001-to-v002-exact-delta.json` / `v001-to-v002.patch` 单独固定 a478/v001→v002 的两处小增量。actual e73、本地v001、review报告均在 `before/` 逐字节保留，原 v001 41-member freeze 未改。

修复 Important1：新 renderer 的实际 HUD 7×6预加载会选择新J0/J1十四层+旧J2–5二十八层，而 observer 旧115仍强制读回旧J0/J1十四层。仅新flag+ActionJ，在既有 `!Capturing&&!AudioRequested&&GIsDumpingMovie==0` 门之后、严格 FindObject/RHI/readback之前，显式 LoadObject 旧J0/J1全部十四个精确路径，持有 `TArray<TStrongObjectPtr<UTexture2D>>` 至本次整个 capture 函数返回，并 FlushRenderingCommands。新增必要只读 include 为 `UObject/StrongObjectPtr.h`。

没有替换 FindObject、跳过缺失资源、减少旧115或降低129。原 source/editor-source/GPU/pending/RHI/Unique检查逐字节保留，原115仍在前、新14在后；LoadObject 返回null或资源尚未ready时仍由原严格 gate失败。没有改 renderer、纹理、completion策略、MainMix、输入、游戏时钟/HP/AI或声音 telemetry。默认off/Shift路径没有补充加载或Flush。全部e73字节及v001既有字节均能从新增insert移除后精确复原。

新增负例是实际集合检查：编译抽取的实际 HUD Primary1 preload循环、冻结 renderer resolver、实际旧Primary1 required循环，在轻量UE shim中构造驻留集合；不假定Base115。newflag场景真实缺旧14，RED11 checks/4 failures；新增预加载后GREEN11/0，检查explicit14 Load、capture范围14强引用、Flush1和缺集归零。原v001的34项Brown/readback测试代码与helper字节保持原SHA，fresh GREEN34/0。所有主机结果都不能代替UE/UHT/真实资源/GPU验证。

Root scoped freshreview前执行 `python check-candidate.py --against-current`；默认无flag只验证本候选快照，Root准入actual后不会使冻结自毁。依次审两insert delta与full e73 exact seams；Root仅精确应用于actual e73，不覆盖其他工作者改动。实际Source文件数不增加。之后cleanbuild、203关闭newflag、按队列先声音Shift，再新artJ双side；新art129readback/PNG/optical仍须真实通过。最终验收保持OPEN。

freeze schema 为 `request258-native-observation-review-fix-freeze-v002`；`projected_source`/`before_source` 对象指明 relative_path、bytes、sha256；`dependencies`记录旧frozen候选/renderer/binding来源；`files`均为本目录相对路径。Root应按这些字段读取，不猜目录位置。
