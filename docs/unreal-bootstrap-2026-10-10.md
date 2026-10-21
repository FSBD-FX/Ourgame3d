# Unreal Engine 5.5 初始化与验证

用户于 2026-10-10 明确改用 Unreal Engine 5。当前工程为 `E:/codex_game/UnrealGame/CodexDungeon.uproject`。旧 `Game/` Unity 工程仅保留作历史参考。

## 引擎与工具链事实

- 本机引擎：`G:/UE_5.5`，`Engine/Build/Build.version` 为 **5.5.4 / CL 40574608**。
- 引擎自带 .NET SDK **8.0.300**，Build.bat 实际选用此 SDK。
- VS2022 Community 17.13.3 已安装，但初始检查其目录没有 `VC/Tools/MSVC`；IDE 安装不等于 C++ 编译工具链已安装。
- 初始 Windows SDK 为 **10.0.19041.0**；满足本机 UE `Windows_SDK.json` 的最低要求。UE5.5 首选 MSVC 14.38.33130，最低同为 14.38.33130，VS2019 的 14.29.30133 不满足要求。
- 第一次真实 Editor Target 构建返回 **UBT 退出码 6**，明确缺少有效的 VS2022 x64 C++ 工具链，证据为 `UnrealGame/Saved/Bootstrap/build-editor-20261010-093810.log`。
- 补装后真实构建选用 **MSVC 14.38.33145**（安装目录 `14.38.33130`）和 **Windows SDK 10.0.19041.0**。项目 `DefaultEngine.ini` 显式固定 VS2022 / CompilerVersion 14.38.33130，避免隐式安装的 14.43 被后续构建选用。
- RTX 3060 Laptop GPU 可由系统枚举到；后续真实 Editor 日志进一步确认以该 GPU 初始化 D3D11 / SM5。

## 已准备的工程内容

- 最小 `CodexDungeon` Runtime C++ 模块，独立 Game 与 Editor Target，UE5.5 include order / BuildSettings V5。
- 启用 Enhanced Input、PythonScriptPlugin、EditorScriptingUtilities、UnrealMCP（仅 Editor）。没有编写战斗、角色控制、敌人或关卡玩法。
- `Content/Python/bootstrap_foundation.py` 已通过真实 UE Editor API 创建并保存 Foundation 准备地图：校准地面、1 米方块、光源、天空、相机、PlayerStart，以及一个空基础 Blueprint。`Saved/Bootstrap/foundation-report.json` 确认 `/Game/Maps/Foundation`、`BP_WorkspaceMarker` 存在，地图含 7 个准备 actor。
- 准备地图使用 DX11 / SM5，关闭 Lumen、Nanite、虚拟阴影与硬件光追，使用 TAA；减少首次着色负担，后续实际视觉结果再决定品质参数。没有自动更新显卡驱动。

## Unreal MCP 来源与本地改动

- 源仓库：<https://github.com/chongdashu/unreal-mcp>。
- 固定提交：`4e5f00da50733190481311e254d16d137a84ef33`。
- 项目副本：`UnrealGame/Plugins/UnrealMCP`；上游 checkout 保留不改。
- 上游 README 声明 MIT，但本次固定树没有独立 LICENSE 文件，不能声称已保存完整许可文件。当前用于本地连通性测试。
- 副本的 `MCPServerRunnable.cpp` 修复两个明确缺陷：接收缓冲区为 NUL 终止符额外预留 1 字节；发送 JSON 使用 UTF-8 字节数，而非 FString 的 TCHAR 长度。
- 完整可复核补丁在 `tools/scripts/unreal-plugin-fixes.patch`，说明在插件 `UPSTREAM.md`。
- 插件固定监听 `127.0.0.1:55557`；没有认证，保持 loopback 范围。Python MCP 服务由另一任务接入。

## 启动与状态脚本

在 C++ 工具链可用后按顺序执行：

```powershell
E:\codex_game\tools\scripts\unreal-build.ps1
E:\codex_game\tools\scripts\unreal-bootstrap-map.ps1
E:\codex_game\tools\scripts\unreal-open.ps1
E:\codex_game\tools\scripts\unreal-status.ps1
```

`unreal-build.ps1` 默认最多 2 个并行编译动作，降低本机 16 GB 内存下同时编译大型 PCH 的压力。`-Target Game` 可独立编译 Game Target。启动脚本使用 Hidden 后台窗口并记录该工程 PID；不关闭用户其他 Unreal 进程。

`Saved/Bootstrap/last-build.json` 保存真实 UBT 退出码；`foundation-report.json` 由 UE 内 Python 生成；`last-editor-start.json` 只证明进程被启动，后续需检查日志、进程存活和 55557 listener，不能单凭它宣称 Editor 可用。

## 真实执行结果

- **Editor C++ 构建成功，退出码 0**：`Saved/Bootstrap/build-editor-20261010-094110.log`。22 个动作、111.42 秒；生成 `Binaries/Win64/UnrealEditor-CodexDungeon.dll` 和插件 `UnrealEditor-UnrealMCP.dll`。上游仍有 `ANY_PACKAGE`、`CompressImageArray` 弃用警告及 `BufferSize` 名称遮蔽警告，没有阻止 UE5.5.4 编译。Game Target 已定义，未单独编译或打包 Game Target。
- **建图 commandlet 成功，退出码 0**：`Saved/Bootstrap/map-20261010-094341.log`，报告时间 09:44:02。该次使用 nullRHI 只生成准备资产；有一条 `EditorLevelLibrary.get_editor_world` 弃用警告，0 error。
- **真实图形 Editor 就绪**：`unreal-open.ps1` 启动 PID **65996**，`Saved/Bootstrap/editor-20261010-094422.log` 确认 RTX 3060、D3D11 / SM5，09:45:28 出现 `Engine is initialized. Leaving FEngineLoop::Init()`。该过程不是 nullRHI。
- **插件真实监听**：同一 Editor 日志出现 `UnrealMCPBridge: Server started on 127.0.0.1:55557`；Windows TCP listener 的 OwningProcess 为 **65996**。

MCP 的 initialize / 30 工具枚举、真实 actor 读取、可逆创建 / 变换 / 删除已通过。主任务还以原生 MCP 验证中文 actor 名精确 UTF-8 回环，删除后前后 actor 名称集合一致，证据在 `evidence/preparation/native-unreal-utf8-roundtrip-2026-10-10.json`。

## 引擎内素材与运行验收

- `unreal-verify-editor.ps1` 以单一真实图形 Editor 的 `-ExecutePythonScript` 运行 `unreal-verify-editor.py`。既有同项目 Editor 未退出时拒绝启动，避免并发写包。Python remote execution 仍关闭。
- 最初 14 项导入得到 76 对象：两角色各 30 动作。源审计各有 32 take，真实 FBX 日志证明左右近战动作因 30 fps 半帧边界被拒，不能以网格类导入成功掩盖动作缺失。
- 首次 60 fps mesh 重导走 Interchange 只返回既有网格，仍缺动作，保留失败报告。随后使用 legacy FBX 动画-only、原 Skeleton、60 fps 成功补齐：角色各 32 动作、左右近战均存在且保存成功。近战实际 UE 时长为 0.400000006 秒，不能声称和源约 0.416667 秒逐帧一致。
- 第三轮 `editor-verification-20261010-100334.log`：PIE 实际进入 `/Game/Tests/Preparation/UEDPIE_0_AssetIntake.AssetIntake`，两角色 idle 播放位置从 0 推进到 0.8003 秒，运行 8 秒后正常退出；地图前后 13 个准备 actor。`pie-report-20261010T020355Z.json` 为引擎内报告。
- `AssetIntake` 为独立素材验收地图：原比例人类 / 兽人、剑 / 金币 / 宝箱、地板，两个 colormap 接到简单材质。尚无战斗、控制器或流程。
- Blender 校准 FBX 真实 StaticMesh bounds 为 **100 / 100 / 200 cm**，Z 为最长轴。
- Noto Sans CJK SC Regular FontFace 和引用它的 runtime Composite Font 已由引擎创建；`font-import-report.json` success=true，实际中文 UI 渲染仍未测试。

## 视觉诊断与修正记录

所有截图均先保留原件 / 展示副本 / index 于 `E:/OurGame/Knight/过程图稿与视频` 后审阅。v001 首轮截图为黑图，截图 API 泵 Slate 导致回调重入；已增加重入保护，等待图像保存后才结束 PIE，保留首轮诊断证据。

v002 `2026-10-10_UE55素材验收_v002/展示副本/asset-intake-pie.png` 实审证明道具和材质可见，但角色仰躺，因此不能称角色视觉通过。v003 `2026-10-10_UE55骨骼轴诊断_v003/展示副本/character-axis-comparison.png` 将正式导入和 fresh 整套导入并排，二者均仰躺，排除仅 animation-only 与 mesh 混用造成差异。

`character-axis-diagnostic-report.json` 显示 reference root Quat 为约 (-0.7071,0,0,0.7071)，动画 root 却 identity；源 Blender 实际求值为站立，包含 90°X 父包装节点。修正前 Human / Orc 二进制和哈希已备份于 `Saved/Bootstrap/asset-backups/20261010-before-animation-axis-normalization/`。

先以动画 import_rotation.roll=-90 做隔离对照，真实 root 相差 180°，严格门槛拒绝且未修改 canonical。随后以 **UE 动画导入 roll=+90°** 规范化，AlignedV2 隔离对照及正式两角色的 idle / 左右近战在 0 与中点共 6 样本均通过：root-reference 角差 **0°**、head component Z 为约 **34.325 cm**（近战中点约 34.532 cm）、32 名称全部齐全、同原 Skeleton、保存成功。没有倾斜 mesh 或 actor 来掩盖问题。

最终 `character-axis-repair-report.json` 状态为 `canonical_root_alignment_passed_pose_samples`，两角色姿态已由真实 PIE 图像确认站立。该验证覆盖本工程已存在网格的 animation-only 规范化；全新工程 mesh+anim 整次导入的默认参数仍需遵守同一数值门槛，不能仅按数量宣称轴正确。

## 最终运行证据与当前状态

- 当前保留图形 Editor **PID 69328**，`editor-verification-20261010-101801.log`；同 PID 在 **127.0.0.1:55557** 监听，未关闭 Blender。
- 最终全 14 项检查为 **80 对象**，Human / Orc 各 **32 AnimSequence**，两个近战动作补齐。隔离 Fresh / Aligned / AlignedV2 诊断资产另保留在 `/Game/Tests/Preparation/AxisDiagnostic/`，不计作正式 14 项的 80 对象。
- `pie-report-20261010T021821Z.json`：实际 PIE **8.016 秒**，`capture_complete=true`，正常停止，地图前后 13 个准备 actor；两角色根轴与 head/foot 骨位置、idle 播放进度均由引擎记录。Component bounds 可能回退 reference bounds，不将其等同逐顶点 posed bounds。
- 六张真实图像请求位于 PIE 2、3、4、5.016、6.032、7.032 秒，保存观察时间和原始 UTC 亦保留。不是实时帧率录像。
- 最终归档：`E:/OurGame/Knight/过程图稿与视频/2026-10-10_UE55角色轴修复与运行采样_v004/`，含原 6 帧、展示帧、源运行 / 轴修复 / 资产 / 字体报告、index 和 SHA256 清单。
- `展示副本/asset-intake-low-fps-pie-samples.mp4` 为 **6 秒、1280×720、H.264**，由六个约 1 fps 的实际 PIE 样本各持有 1 秒编码；容器 30 fps 通过重复帧输出，没有插值或实时玩法主张。完整 FFmpeg 解码 **180 帧、退出码 0**；已审阅首 / 中 / 尾解码图，两角色站立、道具与材质可见。首样本在高分辨率 viewport 初始化时取较广构图，后续较近，index 明确记录此捕获变化。

可复用 `unreal-verify-editor.ps1` 重新串行检查 / PIE 采样；`-RepairCharacterAnimations` 用于先前缺动作修复，`-RepairCharacterAxis` 要求备份并严格 gated 轴规范化。`unreal-export-proof.ps1 -ArchiveDirectory <新版本绝对路径>` 只接收 6 帧完成报告，拒绝覆盖既有归档。复测前应正常退出本工程既有 Editor；当前已开放给主任务只读核验，不再启动第二实例。

另修复 UE Python `Rotator` 位置参数顺序：源脚本统一显式 pitch / yaw / roll。原 Foundation 09:44 地图快照 SHA256 为 `949D3666427C138802D36B5C27314225938B3ECD75812754CC75F51954CC09AB`，保存在 `Saved/Bootstrap/snapshots/`；修正相机 / 灯光后地图 SHA256 为 `35EA8117F814C8A077A6EB9FB58357DD0A5A46FDEFD590DE16FD6C282ECBE14A`。不再声称当前 Foundation 仍是最初文件。

本记录区分 C++ 构建、导入、PIE API、截图视觉与玩法完成；资源准备工程不等于游戏完成。
