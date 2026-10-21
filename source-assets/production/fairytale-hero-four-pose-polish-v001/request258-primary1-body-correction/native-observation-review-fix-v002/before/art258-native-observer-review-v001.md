# Request258 native observer fresh review v001

**NeedsFixes：Critical 0 / Important 1。** 四处 additive inserts、两帧精确绘制检查及声音 telemetry 保留符合范围；但新 flag 启动预加载集合与新 observer 的 129 项 readback 前提冲突，需先补齐确定的资源预加载，再准入该组合。

## 🟡 Important — 新进程缺少 readback 仍强制要求的旧 J0/J1 14 层

**事实：** `projected/DungeonHeroLandingPriorityProbeV001.cpp:360` 的原 Primary1 loop 保留全部旧 42 个分层 object path；`:342` 的 Capture 仅 `FindObject<UTexture2D>`，禁止临时加载。新 `:369` 再追加 14 个新层，使 J 的预期从 115→129。与此同时，已审 presentation candidate 的 resolver `UE-import-binding-candidate-v001/source/after-DungeonFairytaleSwordPresentation.cpp:45` 在新 flag + Bound + LeatherPrimary1 下把 frame 0/1 的请求替换为 Bridge258 路径。实际 `DungeonHUD.cpp:121–125` 在 BeginPlay 只通过此 resolver 收集 6×7 个 Primary1 纹理再执行既有 compilation/flush，因此这条路径收集的是旧 J2–5 的 28 个层 + 新 J0/J1 的 14 个层。旧完整 Body 预加载在另一个 namespace，不能补上旧 14 个分层对象。

**推理：** 独立按真实循环/路径构造集合，旧 Primary1 required=42、替换后的 selected preload=42，其中 required 旧路径缺失 **14**。全 Source/Config 检索没有另一条 old J0/J1 分层预加载入口。首个缺失路径为 `/Game/Production/ArtTrials/EV048/v007/HeroSwordArmorPrimary1/T_Fairytale_SwordPrimary1BodyRest_000_v001.T_Fairytale_SwordPrimary1BodyRest_000_v001`。fresh standalone 进程不能依赖此前编辑器进程的对象驻留。

**风险与建议：** 新 observer 会在旧 J115 loop 的 J0 第一层 FindObject/resource gate 先失败，尚未开始音频/输入和新增 14 个 readback。建议制作一个新候选，在实际 startup compilation/flush 之前显式保留、持有并编译这旧 14 个纹理，与新 14 共存；继续保留本 observer 的 FindObject、原115 + 新14=129、实际 GPU/editor-source gate，不要改成临时 LoadObject、跳过缺失层或减少要求。补一个从真实 preload 选择得到 resident set 的 host integration 检查，而不是把 `Readback(115,...)` 的 Base=115 当作已成立事实。无需改时序/声音/输入或扩大观察器框架。

## 此次独立检查通过的部分

- freeze 8072 B / SHA256 `0fcc6eb38e6675c48a6fa66811b371c3443e2570ce19ef6d7ddefaaf5b81c35e`：41 local files 精确成员集合、全部两次 SHA/长度匹配，0 mismatch。
- `check-candidate.py --against-current` 实际 exit 0：current e73 基线匹配；四处 inserts 可精确复现 projected 74754 B / `a4782db14de4f94979681d8f909f26dd46e33ebd94ea86db2beed558ea1a41d7`；移除 inserts 后全部 e73 原字节及声音 telemetry 精确还原；14 PNG 原字节与 objects 集合匹配；无新增播放、输入、load、completion 或失败控制调用。
- 冻结最新 GREEN host exe 实际重跑 exit 0，34 checks / 0 failures。它使用实际抽出的 Brown/readback 块与轻量 UE shim，不能发现上述真实预加载集合冲突，也不代表 UE 编译/GPU 已通过。未运行会向冻结目录写报告的 run-host.ps1。
- 新 Brown 分支先保留原 common guards，J0/1 检查全部 8 项实际 stack、Root/Grip、剑 path、scale=.5、对应 Axis/Facing angle。旧 J2–5/Ready、flag off、Shift 原分支保留。三个新 report 字段只是 source metadata，未代替 GPU/source 原始字节。

仅新增本报告，未修改冻结候选、Source/Content/tools/E/状态，未启动 UE、生成/查看图像或执行导入。声音 Shift native proof 可按原 Root 队列独立继续。最终美术/衔接/音效验收均未提升。

审查完成 UTC：2026-10-18T21:04:45.075939+00:00
