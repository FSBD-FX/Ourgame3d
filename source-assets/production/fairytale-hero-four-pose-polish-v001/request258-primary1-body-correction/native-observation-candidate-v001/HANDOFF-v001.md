# Request258 native observer 候选

Root 待审 CPP：`projected/DungeonHeroLandingPriorityProbeV001.cpp`。实际基线是 e73 observer，SHA `e73bb9df5e3b95d1dcf16152e945f0efeb90ffc4c522a89b3c6a2d06cc71a422`；本地逐字节副本在 `before/`。本候选只追加 helper + Brown/readback/report 三处，不删除或改写任何 e73 原字节；全部声音 telemetry 因而保留。未改实际 Source/Content/tools/UE/E/状态，未生成或 View 图片。

新行为仅 `-DungeonFairytalePrimary1Bridge258Preview` 与实际 CLI action `J` 同时存在时生效。Brown 保留所有原 common guards；只对 Primary1 Frame0/1 检查新8层完整 DrawStack、Root(256,464)、J0 Grip(211,343)/J1 Grip(159,213)、原军剑 object、scale .5 及对应 axis/facing angle。原旧 J2–5、Ready 和所有非新 flag 路径逐字节保留。旧完整 Body TexturePath 仍是旧 metadata/readiness，不把它冒充新实际 body。

启动 readback 原 J115 全部保留并按原 Capture 严格要求追加14个新 Texture2D，合计129；GPU/editor-source readback、Unique、原生512、资源 ready、CRC、磁盘原件、audio/movie/input前置条件全部复用。没有新 LoadObject、等待 completion 或 Need 放宽。无新 flag 的 J115/Shift105 不变；新 flag+Shift 也不会进入 J-only 补充。此候选不导入资源；需要 Root 先独立 admit 对应14 Texture2D 与 presentation variant。

runtime report 仅增加：`request258_primary1_bridge_optin`、`request258_primary1_bridge_source_contract_sha256`、`request258_primary1_bridge_source_pins`。source contract SHA 为 `f85284dc25d0a5f0be5bf09aa7b9f7dbdf2a62bccbb61e4ca0c5ce0ef1238f6e`，来源 binding freeze `eaa11e20169bb6b53687671800100aa1eea1e703a29ec48ecb36ab55cbb0c6b9`。enabled 时 source_pins 恰好14条，每条有frame/component/object_path/source_png/source_png_bytes（十进制字符串）/source_png_sha256；disabled时数组为空。它们是冻结源 metadata，实际 GPU/editor-source 仍由原 readback 字段提供，不能只凭 metadata 宣称像素通过。

主机 RED/GREEN：34 checks，从缺失分支/追加 readback 的6个预期失败到0 failures。测试编译 projected 的真实 Brown 函数和新增 readback 块，但使用轻量 UE 类型/CLI shim，不能代替 UE 编译或真正 GPU readback。额外检查四处唯一接点、全部 e73 字节 roundtrip、14源 PNG完整 hash/size、objects精确集与同一测试片段；新增加代码没有控制/播放/资源加载/completion/失败调用。

Root admit 前执行 `python check-candidate.py --against-current`，独立审查 `native-observation.patch`、`exact-seams.json` 与 projected CPP；只精确应用这四处，实际 Source 文件数不增加。默认 `python check-candidate.py` 使用本地历史快照验证，Root以后修改actual probe不会破坏候选冻结。随后 fresh build、原203（关闭newflag）、新flag两side正常 Land4→J0/J1→旧J2…5→Ready，沿用原输入/时序/HP/AI/失败闸并使用新的独立 native checker；不得改旧 immutable checker 或历史证据。声音 native Shift_right 仍应优先按 Root 当前队列完成。

这里只提供观察器源码候选。真实导入、编译、资源 readback、动作衔接、抓拍/视频和验收均待 Root 执行，FinalAccepted 不提升。
